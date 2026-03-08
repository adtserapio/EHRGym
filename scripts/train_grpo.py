"""
EHRGym GRPO Reinforcement Learning Script  (Unsloth)
=====================================================
Trains a model with GRPO to interact with the live EHRGym environment.
The model learns to navigate the EHR, place orders, and write notes
by receiving reward signals from the rubric evaluator.

Prerequisites:
  1. EHRGym running:  npm run dev          (Next.js + env server)
  2. Dependencies:    pip install -r requirements-train.txt

Usage (on H100):
  python scripts/train_grpo.py \
      --model unsloth/Qwen2.5-7B-Instruct \
      --output runs/checkpoints/ehrgym-grpo \
      --max-steps 500 --num-generations 4

Quick smoke test:
  python scripts/train_grpo.py \
      --model unsloth/Qwen2.5-0.5B-Instruct \
      --output runs/checkpoints/ehrgym-grpo-tiny \
      --max-steps 20 --num-generations 2 --lora-r 16
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a clinical computer-use agent operating an Epic-like EHR. "
    "Given the current screenshot description, URL, activity, task goal, and state metadata, "
    "return exactly one valid next action as strict JSON.\n\n"
    "Valid action types: click, fill, keypress, goto, wait.\n"
    "Examples:\n"
    '  {"type": "click", "selector": "[data-testid=\'order-btn\']"}\n'
    '  {"type": "fill", "selector": "#note-body", "value": "Patient improving..."}\n'
    '  {"type": "goto", "url": "http://127.0.0.1:3000/patient/pat-1001"}\n'
)

ENV_SERVER = "http://127.0.0.1:8000"
TASK_ID = "aki-chart-review"  # default task

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EHRGym GRPO RL training (Unsloth)")
    p.add_argument("--model", default="unsloth/Qwen2.5-7B-Instruct")
    p.add_argument("--output", default="runs/checkpoints/ehrgym-grpo")
    p.add_argument("--max-steps", type=int, default=500)
    p.add_argument("--num-generations", type=int, default=4,
                   help="Number of completions to sample per prompt (GRPO group size)")
    p.add_argument("--max-seq-len", type=int, default=2048)
    p.add_argument("--lora-r", type=int, default=64)
    p.add_argument("--lora-alpha", type=int, default=128)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=4)
    p.add_argument("--no-4bit", action="store_true")
    p.add_argument("--env-server", default=ENV_SERVER)
    p.add_argument("--task-id", default=TASK_ID)
    p.add_argument("--max-episode-steps", type=int, default=25,
                   help="Max env steps per episode before termination")
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--wandb-project", default=None)
    p.add_argument("--save-method", default="lora",
                   choices=["lora", "merged_16bit", "merged_4bit"])
    return p.parse_args()


# ---------------------------------------------------------------------------
# Environment interaction helpers
# ---------------------------------------------------------------------------

def env_reset(base_url: str, task_id: str) -> dict:
    """Reset the EHRGym environment and return the initial observation."""
    import httpx
    resp = httpx.post(f"{base_url}/reset", json={"task_id": task_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def env_step(base_url: str, action: dict) -> dict:
    """Take an action in the EHRGym environment."""
    import httpx
    resp = httpx.post(f"{base_url}/step", json=action, timeout=30)
    resp.raise_for_status()
    return resp.json()


def obs_to_text(obs: dict) -> str:
    """Convert an EHRGym observation to a text prompt (no screenshot b64)."""
    payload = {
        "goal": obs.get("goal", ""),
        "current_url": obs.get("current_url", ""),
        "active_activity": obs.get("active_activity", ""),
        "state": obs.get("state", {}),
    }
    return json.dumps(payload, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Reward functions
# ---------------------------------------------------------------------------

def valid_json_reward(completions: list, **kwargs) -> list[float]:
    """Reward: is the model output valid JSON with a 'type' field?"""
    scores = []
    for completion in completions:
        text = completion[0]["content"] if isinstance(completion, list) else completion
        try:
            parsed = json.loads(text)
            if "type" in parsed:
                scores.append(1.0)
            else:
                scores.append(-0.5)
        except (json.JSONDecodeError, TypeError):
            scores.append(-1.0)
    return scores


def action_type_reward(completions: list, **kwargs) -> list[float]:
    """Reward: does the action use a valid EHRGym action type?"""
    valid_types = {"click", "fill", "keypress", "goto", "wait"}
    scores = []
    for completion in completions:
        text = completion[0]["content"] if isinstance(completion, list) else completion
        try:
            parsed = json.loads(text)
            if parsed.get("type") in valid_types:
                scores.append(1.0)
            else:
                scores.append(-1.0)
        except Exception:
            scores.append(-1.0)
    return scores


def rubric_progress_reward(completions: list, **kwargs) -> list[float]:
    """
    Reward: execute the action against the live env and return rubric reward.
    This is the main task reward — it actually steps the environment.
    
    NOTE: For GRPO with num_generations > 1, each completion gets the same
    starting state (we reset before each prompt). This function is called
    once per batch, so we run one episode per completion.
    """
    env_url = kwargs.get("env_url", ENV_SERVER)
    task_id = kwargs.get("task_id", TASK_ID)
    max_steps = kwargs.get("max_episode_steps", 25)
    
    scores = []
    for completion in completions:
        text = completion[0]["content"] if isinstance(completion, list) else completion
        try:
            action = json.loads(text)
        except Exception:
            scores.append(-2.0)
            continue
        
        try:
            # Step the environment with this single action
            result = env_step(env_url, action)
            reward = result.get("reward", 0.0)
            # Scale reward: rubric items are worth a lot
            scores.append(reward * 10.0)
        except Exception as e:
            log.warning("Env step failed: %s", e)
            scores.append(-1.0)
    
    return scores


# ---------------------------------------------------------------------------
# Dataset: generate prompts by resetting env
# ---------------------------------------------------------------------------

def build_prompt_dataset(env_url: str, task_id: str, n_prompts: int = 100):
    """Create a dataset of prompts by resetting the env multiple times."""
    from datasets import Dataset
    
    rows = []
    for i in range(n_prompts):
        try:
            obs = env_reset(env_url, task_id)
            observation = obs.get("observation", obs)
            user_content = obs_to_text(observation)
            rows.append({
                "prompt": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
            })
        except Exception as e:
            log.warning("Failed to reset env (prompt %d): %s", i, e)
            continue
    
    if not rows:
        raise RuntimeError(f"Could not get any prompts from {env_url}")
    
    log.info("Built %d prompts from env resets", len(rows))
    return Dataset.from_list(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    from unsloth import FastLanguageModel
    from unsloth.chat_templates import get_chat_template
    from trl import GRPOConfig, GRPOTrainer

    # ---- W&B ----
    if args.wandb_project:
        os.environ["WANDB_PROJECT"] = args.wandb_project
        report_to = "wandb"
    else:
        report_to = "none"

    # ---- Load model ----
    load_in_4bit = not args.no_4bit
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_len,
        load_in_4bit=load_in_4bit,
        dtype=None,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.0,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        use_gradient_checkpointing="unsloth",
        random_state=args.seed,
    )
    model.print_trainable_parameters()

    # Chat template
    model_lower = args.model.lower()
    if "qwen" in model_lower:
        chat_template = "qwen-2.5"
    elif "llama" in model_lower:
        chat_template = "llama-3.1"
    else:
        chat_template = "chatml"
    tokenizer = get_chat_template(tokenizer, chat_template=chat_template)

    # ---- Dataset (prompts from env) ----
    dataset = build_prompt_dataset(args.env_server, args.task_id, n_prompts=200)

    # ---- GRPO config ----
    max_prompt_length = args.max_seq_len // 2
    max_completion_length = args.max_seq_len - max_prompt_length

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = GRPOConfig(
        output_dir=str(output_dir),
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        num_generations=args.num_generations,
        max_prompt_length=max_prompt_length,
        max_completion_length=max_completion_length,
        learning_rate=args.lr,
        lr_scheduler_type="linear",
        warmup_ratio=0.1,
        weight_decay=0.01,
        optim="adamw_8bit",
        bf16=True,
        logging_steps=1,
        save_steps=100,
        save_total_limit=3,
        seed=args.seed,
        report_to=report_to,
        temperature=1.0,
    )

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        args=training_args,
        train_dataset=dataset,
        reward_funcs=[
            valid_json_reward,       # +1 for valid JSON with "type"
            action_type_reward,      # +1 for valid action type
            rubric_progress_reward,  # +N for actual rubric progress
        ],
    )

    # ---- Train ----
    log.info("Starting GRPO training (max_steps=%d, num_generations=%d) …",
             args.max_steps, args.num_generations)
    trainer.train()

    # ---- Save ----
    if args.save_method == "lora":
        save_dir = str(output_dir / "lora_adapter")
        model.save_pretrained(save_dir)
        tokenizer.save_pretrained(save_dir)
        log.info("Saved LoRA adapter → %s", save_dir)
    else:
        save_dir = str(output_dir / "merged")
        model.save_pretrained_merged(save_dir, tokenizer, save_method=args.save_method)
        log.info("Saved merged model → %s", save_dir)

    log.info("Done ✓")


if __name__ == "__main__":
    main()
