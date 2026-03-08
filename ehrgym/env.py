"""
EHRGymEnv — OpenEnv-compatible environment for TRL GRPO agent training.

This class wraps a remote EHRGym server (FastAPI + Playwright) and exposes
browser-level actions as tool functions that TRL's GRPOTrainer can call
during multi-turn agent training.

Two integration modes are supported:

1. **``environment_factory``** (recommended, requires ``transformers>=5.2``)::

       trainer = GRPOTrainer(
           environment_factory=lambda: EHRGymEnv(base_url="http://localhost:8000"),
           reward_funcs=task_reward,
           ...
       )

   Each generation gets its own ``EHRGymEnv`` instance; ``reset()`` is called
   automatically and its return value is appended to the user message.

2. **Standalone ``tools`` list** (broader TRL compatibility)::

       env = EHRGymEnv()
       trainer = GRPOTrainer(
           tools=[env.navigate, env.click, env.type_text, env.press_key],
           reward_funcs=task_reward,
           ...
       )
"""
from __future__ import annotations

import os
from typing import Any

import httpx

# ---------------------------------------------------------------------------
# Default server URL (overridable via env-var or constructor arg)
# ---------------------------------------------------------------------------

_DEFAULT_SERVER_URL = os.getenv("EHRGYM_SERVER_URL", "http://127.0.0.1:8000")

# ---------------------------------------------------------------------------
# All 25 clinical tasks shipped with EHRGym
# ---------------------------------------------------------------------------

TASK_IDS: list[str] = [
    "acute-coronary-syndrome",
    "acute-ischemic-stroke",
    "acute-pancreatitis",
    "aki-chart-review",
    "alcohol-withdrawal",
    "anaphylaxis",
    "asthma-exacerbation",
    "bacterial-meningitis",
    "cap-pneumonia-followup",
    "cdiff-colitis",
    "chf-exacerbation",
    "copd-exacerbation",
    "dka-management",
    "hepatic-encephalopathy",
    "hip-fracture",
    "hyperkalemia",
    "hyponatremia-workup",
    "mrsa-cellulitis",
    "new-onset-afib",
    "pe-workup",
    "postop-ileus",
    "sickle-cell-crisis",
    "thyroid-storm",
    "upper-gi-bleed",
    "urosepsis",
]


class EHRGymEnv:
    """OpenEnv-compatible environment for clinical EHR chart-review tasks.

    The environment connects to a running EHRGym server and exposes four
    browser-level tool functions (``navigate``, ``click``, ``type_text``,
    ``press_key``) that a language model can invoke during training.

    Attributes:
        cumulative_reward: Total reward accumulated during the current episode.
        done: Whether the episode has ended (all rubric items complete).
        step_count: Number of actions taken in the current episode.
        rubric_progress: List of completed rubric item keys.
    """

    def __init__(self, base_url: str | None = None, task_id: str | None = None) -> None:
        self.base_url = (base_url or _DEFAULT_SERVER_URL).rstrip("/")
        self._default_task_id = task_id

        # When pointing at a HuggingFace Space URL, the env server is behind
        # the nginx proxy at /env/*  (e.g. https://…hf.space/env/reset).
        # For a direct env server URL (http://localhost:8000) no prefix needed.
        if "hf.space" in self.base_url or "huggingface.co" in self.base_url:
            api_base = f"{self.base_url}/env"
        else:
            api_base = self.base_url

        self._client = httpx.Client(base_url=api_base, timeout=30.0)

        # Episode state (populated after reset)
        self.cumulative_reward: float = 0.0
        self.done: bool = False
        self.step_count: int = 0
        self.rubric_progress: list[str] = []
        self._goal: str = ""
        self._current_url: str = ""
        self._last_reward: float = 0.0

    # ------------------------------------------------------------------
    # reset() — required by TRL environment_factory
    # ------------------------------------------------------------------

    def reset(self, *, task_id: str | None = None, **kwargs: Any) -> str:
        """Reset the environment for a new episode.

        Called automatically by TRL's ``GRPOTrainer`` before each generation
        when using ``environment_factory``.  Returns a context string that is
        appended to the last user message.

        Args:
            task_id: Clinical task identifier (e.g. ``"aki-chart-review"``).
                     Falls back to the constructor default or the first task.

        Returns:
            A human-readable description of the loaded patient and goal.
        """
        tid = task_id or self._default_task_id
        payload: dict[str, Any] = {}
        if tid:
            payload["task_id"] = tid

        resp = self._client.post("/reset", json=payload)
        resp.raise_for_status()
        data = resp.json()

        obs = data["observation"]
        self._goal = obs.get("goal", "Complete the clinical chart review.")
        self._current_url = obs.get("current_url", "")

        # Reset episode accumulators
        self.cumulative_reward = 0.0
        self.done = False
        self.step_count = 0
        self.rubric_progress = []
        self._last_reward = 0.0

        return (
            f"EHR system loaded.\n"
            f"Goal: {self._goal}\n"
            f"Current URL: {self._current_url}\n"
            f"Use the available tools to navigate the EHR, review the chart, "
            f"place clinical orders, write your assessment note, and sign the encounter."
        )

    # ------------------------------------------------------------------
    # Tool functions — public methods exposed to the LLM
    # ------------------------------------------------------------------

    def navigate(self, url: str) -> str:
        """Navigate to a URL in the EHR system.

        Args:
            url: Target URL or path (e.g. ``/patient/pat-1001`` or full URL).

        Returns:
            Navigation result including the current page URL.
        """
        return self._step({"type": "goto", "url": url})

    def click(self, selector: str) -> str:
        """Click an interactive element on the current page.

        Args:
            selector: CSS selector for the element to click
                      (e.g. ``button[data-testid='sign-encounter']``).

        Returns:
            Click result including current page URL and any new progress.
        """
        return self._step({"type": "click", "selector": selector})

    def type_text(self, selector: str, text: str) -> str:
        """Type text into an input field or text area.

        For ``<select>`` elements this automatically selects the matching option.

        Args:
            selector: CSS selector for the input element.
            text: Text content to enter.

        Returns:
            Result including current page URL and any new progress.
        """
        return self._step({"type": "fill", "selector": selector, "text": text})

    def press_key(self, key: str) -> str:
        """Press a keyboard key or key combination.

        Args:
            key: Key name (e.g. ``Enter``, ``Tab``, ``Escape``, ``Control+a``).

        Returns:
            Result including current page URL.
        """
        return self._step({"type": "keypress", "key": key})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _step(self, action: dict[str, Any]) -> str:
        """Execute a single browser action via the remote env server."""
        if self.done:
            return "Episode already complete — all rubric items satisfied."

        resp = self._client.post("/step", json=action)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()

        # Update episode state
        obs = data.get("observation", {})
        self._current_url = obs.get("current_url", self._current_url)

        reward: float = data.get("reward", 0.0)
        self._last_reward = reward
        self.cumulative_reward += reward
        self.done = data.get("done", False)
        self.step_count += 1

        info: dict[str, Any] = data.get("info", {})
        self.rubric_progress = info.get("rubric_progress", self.rubric_progress)
        new_items: list[str] = info.get("new_rubric_items", [])

        # Build text observation for the LLM
        parts: list[str] = [f"Step {self.step_count} | URL: {self._current_url}"]

        breakdown = info.get("reward_breakdown", {})
        if breakdown.get("action", 0) < 0:
            parts.append("Warning: action may have failed.")

        if new_items:
            parts.append(f"New progress: {', '.join(new_items)}")

        n_done = len(self.rubric_progress)
        parts.append(f"Rubric progress: {n_done} item(s) completed")

        if self.done:
            parts.append("All tasks complete! Encounter signed and verified.")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_state(self) -> dict[str, Any]:
        """Return the current environment state (for debugging / reward)."""
        resp = self._client.get("/state")
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __repr__(self) -> str:
        return (
            f"EHRGymEnv(base_url={self.base_url!r}, "
            f"step={self.step_count}, reward={self.cumulative_reward:.3f}, "
            f"done={self.done})"
        )
