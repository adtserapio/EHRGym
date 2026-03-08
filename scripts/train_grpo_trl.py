"""
EHRGym GRPO Training Script — TRL + OpenEnv Edition
====================================================
Fine-tune a language model with GRPO to interact with the EHRGym
environment using TRL's native agent-training pipeline.

The model learns to:
  • Navigate an Epic-style EHR interface
  • Place clinical orders  (e.g. IV fluids, labs)
  • Write SOAP-style clinical notes
  • Sign encounters
  • Earn reward from a rubric evaluator

Prerequisites
-------------
1. EHRGym running:
     npm run dev            # Next.js on :3000
     uvicorn env_server.app.main:app --port 8000

2. Dependencies:
     pip install "trl[vllm]>=0.29" transformers>=5.2 datasets accelerate peft

Usage
-----
# Quick smoke test  (single GPU, no vLLM)
python scripts/train_grpo_trl.py \
    --model_name_or_path Qwen/Qwen3-0.6B \
    --output_dir runs/checkpoints/ehrgym-grpo-trl \
    --max_steps 50 \
    --num_generations 2 \
    --max_completion_length 512

# Full training  (multi-GPU with vLLM)
accelerate launch \
    --config_file configs/deepspeed_zero2.yaml \
    scripts/train_grpo_trl.py \
    --model_name_or_path Qwen/Qwen3-1.7B \
    --output_dir runs/checkpoints/ehrgym-grpo-trl \
    --max_steps 500 \
    --num_generations 4 \
    --max_completion_length 1024 \
    --use_vllm True \
    --vllm_mode colocate \
    --report_to wandb
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from datasets import Dataset

from trl import GRPOConfig, GRPOTrainer, ModelConfig, ScriptArguments, TrlParser

from ehrgym import EHRGymEnv
from ehrgym.env import TASK_IDS
from ehrgym.rewards import task_reward, format_reward, efficiency_reward


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EHRGYM_SERVER_URL = os.getenv("EHRGYM_SERVER_URL", "http://127.0.0.1:8000")
TASKS_DIR = Path(__file__).resolve().parent.parent / "tasks" / "examples"


# ---------------------------------------------------------------------------
# Dataset construction
# ---------------------------------------------------------------------------

def build_dataset(tasks_dir: Path = TASKS_DIR, task_ids: list[str] | None = None) -> Dataset:
    """Build a conversational prompt dataset from task JSON files.

    Each row contains a ``prompt`` (list of chat messages) and a ``task_id``
    that is forwarded to ``EHRGymEnv.reset()`` via TRL's dataset passthrough.
    """
    task_ids = task_ids or TASK_IDS
    rows: list[dict] = []

    for tid in task_ids:
        task_file = tasks_dir / f"{tid}.json"
        if not task_file.exists():
            continue

        task = json.loads(task_file.read_text())
        objective = task.get("objective", "Complete the clinical chart review.")

        system_msg = (
            "You are a clinical AI agent operating an Epic-style Electronic Health "
            "Records (EHR) system. You are logged in as Patrick Sullivan, MD — the "
            "attending physician.\n\n"
            "You can interact with the EHR using the provided tools:\n"
            "  • navigate(url)          — go to a URL in the EHR\n"
            "  • click(selector)        — click a page element by CSS selector\n"
            "  • type_text(selector, text) — type into an input / select an option\n"
            "  • press_key(key)         — press a keyboard key\n\n"
            "Complete the clinical workflow efficiently. After finishing all rubric "
            "items the episode ends automatically."
        )

        user_msg = f"Clinical task: {objective}"

        rows.append({
            "prompt": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            "task_id": tid,
        })

    if not rows:
        raise RuntimeError(f"No task files found in {tasks_dir}")

    return Dataset.from_list(rows)


# ---------------------------------------------------------------------------
# Env factory
# ---------------------------------------------------------------------------

def make_env() -> EHRGymEnv:
    """Factory callable passed to ``GRPOTrainer(environment_factory=...)``."""
    return EHRGymEnv(base_url=EHRGYM_SERVER_URL)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = TrlParser((ScriptArguments, GRPOConfig, ModelConfig))
    script_args, training_args, model_args = parser.parse_args_and_config()

    # ---- Dataset ----
    dataset = build_dataset()
    print(f"Built dataset with {len(dataset)} tasks")

    # ---- Ensure remove_unused_columns is False (we forward task_id) ----
    training_args.remove_unused_columns = False

    # ---- Disable thinking wrapper for tool-calling models ----
    if training_args.chat_template_kwargs is None:
        training_args.chat_template_kwargs = {}
    training_args.chat_template_kwargs.setdefault("enable_thinking", False)

    # ---- Set sensible defaults for agent training ----
    if training_args.max_tool_calling_iterations is None:
        training_args.max_tool_calling_iterations = 25  # max actions per episode

    # ---- Trainer ----
    trainer = GRPOTrainer(
        model=model_args.model_name_or_path,
        args=training_args,
        train_dataset=dataset,
        reward_funcs=[task_reward, format_reward, efficiency_reward],
        reward_weights=[1.0, 0.2, 0.1],
        environment_factory=make_env,
    )

    # ---- Train ----
    trainer.train()

    # ---- Save ----
    trainer.save_model(training_args.output_dir)
    if training_args.push_to_hub:
        trainer.push_to_hub(dataset_name=script_args.dataset_name)

    print("Training complete ✓")


if __name__ == "__main__":
    main()
