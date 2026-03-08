"""
EHRGym SFT Training Script  (Unsloth)
=======================================
Fine-tunes any HF chat model on the exported EHRGym trajectory dataset
using Unsloth + QLoRA for 2x faster training and 70% less VRAM.

Usage (on H100):
  python scripts/train_sft.py \
      --dataset runs/datasets/ehrgym_sft.jsonl \
      --model unsloth/Qwen2.5-7B-Instruct \
      --output runs/checkpoints/ehrgym-sft \
      --epochs 3 --lr 2e-4 --batch-size 4 --grad-accum 4

Quick smoke test (tiny model):
  python scripts/train_sft.py \
      --dataset runs/datasets/ehrgym_sft.jsonl \
      --model unsloth/Qwen2.5-0.5B-Instruct \
      --output runs/checkpoints/ehrgym-sft-tiny \
      --epochs 1 --batch-size 2 --lora-r 16

Full 16-bit LoRA (no 4-bit quant):
  python scripts/train_sft.py ... --no-4bit

Save merged model for vLLM:
  python scripts/train_sft.py ... --save-method merged_16bit
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EHRGym SFT fine-tuning (Unsloth)")
    p.add_argument("--dataset", required=True, help="Path to ehrgym_sft.jsonl")
    p.add_argument("--model", default="unsloth/Qwen2.5-7B-Instruct",
                   help="HuggingFace model ID (use unsloth/ prefix for optimised 4-bit quants)")
    p.add_argument("--output", default="runs/checkpoints/ehrgym-sft",
                   help="Output directory for checkpoints")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--batch-size", type=int, default=4, help="Per-device train batch size")
    p.add_argument("--grad-accum", type=int, default=4, help="Gradient accumulation steps")
    p.add_argument("--max-seq-len", type=int, default=2048, help="Max sequence length")
    p.add_argument("--lora-r", type=int, default=64, help="LoRA rank")
    p.add_argument("--lora-alpha", type=int, default=128, help="LoRA alpha (default: 2 * lora_r)")
    p.add_argument("--lora-dropout", type=float, default=0.0,
                   help="LoRA dropout (Unsloth optimised kernels work best with 0)")
    p.add_argument("--no-4bit", action="store_true",
                   help="Disable 4-bit quantisation; use 16-bit LoRA instead")
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--logging-steps", type=int, default=1)
    p.add_argument("--save-steps", type=int, default=50)
    p.add_argument("--max-steps", type=int, default=-1,
                   help="Override epoch count with max_steps (useful for smoke tests)")
    p.add_argument("--save-method", default="lora",
                   choices=["lora", "merged_16bit", "merged_4bit", "mxfp4"],
                   help="How to save the final model")
    p.add_argument("--wandb-project", default=None,
                   help="Weights & Biases project name (optional)")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_sft_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL and return list of dicts with a 'messages' column."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            # Keep only the chat messages
            rows.append({"messages": row["messages"]})
    log.info("Loaded %d examples from %s", len(rows), path)
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # ---- Imports (Unsloth patches HF on import) ----
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import get_chat_template
    import torch
    from datasets import Dataset
    from trl import SFTTrainer, SFTConfig

    # ---- W&B ----
    if args.wandb_project:
        os.environ["WANDB_PROJECT"] = args.wandb_project
        report_to = "wandb"
    else:
        report_to = "none"

    # ---- Load model + tokenizer via Unsloth ----
    load_in_4bit = not args.no_4bit
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_len,
        load_in_4bit=load_in_4bit,
        dtype=None,  # auto-detect (bf16 on H100)
    )
    log.info("Loaded %s  (4-bit=%s)", args.model, load_in_4bit)

    # ---- Apply LoRA adapter via Unsloth ----
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        use_gradient_checkpointing="unsloth",  # Unsloth's optimised checkpointing
        random_state=args.seed,
    )
    model.print_trainable_parameters()

    # ---- Chat template ----
    # Our JSONL uses {"role": "system/user/assistant", "content": "..."} (ChatML-compatible)
    # Detect the right template from the model name
    model_lower = args.model.lower()
    if "qwen" in model_lower:
        chat_template = "qwen-2.5"
    elif "llama-3" in model_lower or "llama3" in model_lower:
        chat_template = "llama-3.1"
    elif "phi" in model_lower:
        chat_template = "phi-4"
    elif "gemma" in model_lower:
        chat_template = "gemma-3"
    elif "mistral" in model_lower:
        chat_template = "mistral"
    else:
        chat_template = "chatml"

    tokenizer = get_chat_template(tokenizer, chat_template=chat_template)
    log.info("Using chat template: %s", chat_template)

    # ---- Dataset ----
    raw = load_sft_jsonl(args.dataset)
    dataset = Dataset.from_list(raw)

    def formatting_func(examples):
        convos = examples["messages"]
        texts = [
            tokenizer.apply_chat_template(
                convo, tokenize=False, add_generation_prompt=False
            )
            for convo in convos
        ]
        return {"text": texts}

    dataset = dataset.map(formatting_func, batched=True)
    log.info("Dataset ready: %d examples", len(dataset))

    # ---- Training config ----
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = SFTConfig(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        bf16=True,
        fp16=False,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=3,
        seed=args.seed,
        report_to=report_to,
        max_seq_length=args.max_seq_len,
        dataset_text_field="text",
        optim="adamw_8bit",
        weight_decay=0.01,
        packing=False,  # disable packing—our examples are short enough
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=dataset,
    )

    # ---- Train ----
    log.info("Starting training …")
    trainer_stats = trainer.train()
    log.info("Training complete. Loss: %.4f", trainer_stats.training_loss)

    # ---- Save ----
    if args.save_method == "lora":
        save_dir = str(output_dir / "lora_adapter")
        model.save_pretrained(save_dir)
        tokenizer.save_pretrained(save_dir)
        log.info("Saved LoRA adapter → %s", save_dir)
    else:
        save_dir = str(output_dir / "merged")
        model.save_pretrained_merged(save_dir, tokenizer, save_method=args.save_method)
        log.info("Saved merged model (%s) → %s", args.save_method, save_dir)

    log.info("Done ✓")


if __name__ == "__main__":
    main()
