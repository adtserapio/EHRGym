"""
TRL-compatible reward functions for EHRGym GRPO training.

These reward functions are designed to be passed to TRL's ``GRPOTrainer``
via the ``reward_funcs`` parameter.  They follow the TRL reward-function
contract: each receives keyword arguments (including ``completions``,
``prompts``, ``environments``, etc.) and returns a list of float scores.

Three reward signals are provided:

* **task_reward** — The primary clinical task reward derived from the
  environment's rubric progress and cumulative reward.
* **format_reward** — Penalises malformed tool calls and rewards well-
  structured agent responses.
* **efficiency_reward** — Encourages completing tasks in fewer steps.

Usage::

    from ehrgym.rewards import task_reward, format_reward, efficiency_reward

    trainer = GRPOTrainer(
        reward_funcs=[task_reward, format_reward, efficiency_reward],
        reward_weights=[1.0, 0.2, 0.1],
        ...
    )
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Primary task reward  (uses environment_factory instances)
# ---------------------------------------------------------------------------

def task_reward(environments: list | None = None, **kwargs) -> list[float]:
    """Return the cumulative rubric reward from each environment instance.

    This is the **primary** reward signal.  It reflects how many clinical
    rubric items (orders placed, note elements written, encounter signed)
    the agent has completed.

    When used with ``environment_factory``, TRL passes the list of
    ``EHRGymEnv`` instances after the tool-calling loop finishes.

    Falls back to 0.0 when environments are not available (e.g. when
    using the standalone ``tools`` approach).
    """
    if environments is None:
        # Fallback: no environment_factory — return neutral reward.
        completions = kwargs.get("completions", [])
        return [0.0] * len(completions)

    rewards: list[float] = []
    for env in environments:
        # cumulative_reward includes action rewards, rubric progress, and
        # the completion bonus (see env_server/app/main.py for details).
        rewards.append(float(getattr(env, "cumulative_reward", 0.0)))
    return rewards


# ---------------------------------------------------------------------------
# Format / structure reward
# ---------------------------------------------------------------------------

def format_reward(completions: list | None = None, **kwargs) -> list[float]:
    """Reward well-structured agent responses; penalise empty / broken ones.

    Checks whether the agent produced at least one tool call and received
    at least one tool response, indicating a coherent interaction loop.
    """
    if completions is None:
        return []

    rewards: list[float] = []
    for completion in completions:
        has_tool_call = False
        has_tool_response = False
        has_content = False

        if isinstance(completion, list):
            for turn in completion:
                role = turn.get("role", "") if isinstance(turn, dict) else ""
                if role == "assistant" and (turn.get("tool_calls") or turn.get("function_call")):
                    has_tool_call = True
                elif role == "tool":
                    has_tool_response = True
                elif role == "assistant":
                    content = turn.get("content", "") if isinstance(turn, dict) else ""
                    if content and content.strip():
                        has_content = True
        else:
            # String completion (standard format) — just check non-empty
            has_content = bool(completion and str(completion).strip())

        if has_tool_call and has_tool_response:
            score = 0.3  # good structure
            if has_content:
                score += 0.2  # also produced a final answer
        elif has_content:
            score = 0.0  # content but no tool use
        else:
            score = -0.5  # empty or broken

        rewards.append(score)

    return rewards


# ---------------------------------------------------------------------------
# Efficiency reward
# ---------------------------------------------------------------------------

def efficiency_reward(environments: list | None = None, **kwargs) -> list[float]:
    """Reward completing the task in fewer steps.

    A perfect completion in ≤10 steps gets a bonus of +1.0.
    For each additional step beyond 10 the bonus linearly decays toward 0.
    Non-completed episodes receive 0.0.
    """
    if environments is None:
        completions = kwargs.get("completions", [])
        return [0.0] * len(completions)

    rewards: list[float] = []
    for env in environments:
        done = getattr(env, "done", False)
        steps = getattr(env, "step_count", 0)
        if done and steps > 0:
            # Linear decay: full bonus at ≤10 steps, zero at ≥30 steps
            bonus = max(0.0, 1.0 - max(0, steps - 10) / 20.0)
            rewards.append(bonus)
        else:
            rewards.append(0.0)
    return rewards
