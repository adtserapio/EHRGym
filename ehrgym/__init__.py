"""
EHRGym — OpenEnv environment for clinical EHR chart-review tasks.

Compatible with TRL's GRPOTrainer for GRPO fine-tuning of language models
that learn to navigate an Epic-like EHR, place orders, write clinical notes,
and sign encounters.

Usage with TRL ``environment_factory``::

    from ehrgym import EHRGymEnv, task_reward
    from trl import GRPOTrainer, GRPOConfig

    trainer = GRPOTrainer(
        model="Qwen/Qwen3-0.6B",
        reward_funcs=task_reward,
        environment_factory=EHRGymEnv,
        train_dataset=dataset,
        args=GRPOConfig(...),
    )
    trainer.train()
"""

__version__ = "0.1.0"

from .env import EHRGymEnv
from .rewards import task_reward, format_reward, efficiency_reward

__all__ = [
    "EHRGymEnv",
    "task_reward",
    "format_reward",
    "efficiency_reward",
]
