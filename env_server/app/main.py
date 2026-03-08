from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException

from .browser import BrowserSession
from .models import Action, EnvironmentState, ResetRequest, ResetResponse, StepResponse

EHR_BASE_URL = os.getenv("EHR_BASE_URL", "http://127.0.0.1:3000")
HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() != "false"
DEFAULT_WAIT_MS = int(os.getenv("OPENENV_DEFAULT_WAIT_MS", "350"))
TASKS_DIR = Path(__file__).resolve().parent.parent.parent / "tasks" / "examples"

browser = BrowserSession()
state = EnvironmentState(episode_id="bootstrap")
goal_text = "Open the chart and complete the assigned workflow."

# ── Reward constants (overridden by task scoring config when available) ──
REWARD_ACTION_SUCCESS = 0.05      # small positive for a successful browser action
REWARD_ACTION_FAILURE = -0.10     # penalty for a failed/invalid action
REWARD_STEP_PENALTY   = -0.01    # per-step cost to discourage aimless wandering
REWARD_COMPLETION_BONUS = 1.0     # bonus when all rubric items are satisfied

# ── Task scoring config cache ──
_task_scoring: dict[str, Any] = {}


def _load_task_scoring(task_id: str | None) -> dict[str, Any]:
    """Load scoring weights from the task JSON file, if available."""
    if not task_id:
        return {}
    if task_id in _task_scoring:
        return _task_scoring[task_id]

    task_file = TASKS_DIR / f"{task_id}.json"
    if task_file.exists():
        try:
            data = json.loads(task_file.read_text())
            scoring = data.get("scoring", {})
            _task_scoring[task_id] = scoring
            return scoring
        except Exception:
            pass
    _task_scoring[task_id] = {}
    return {}


# Progress keys are now granular: "order:<name>", "note_element:<element>",
# "encounter_signed".  They map directly to substep keys in the task JSON.


async def _post_reset() -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{EHR_BASE_URL}/api/dev/reset")
        response.raise_for_status()


async def _fetch_patients() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{EHR_BASE_URL}/api/patients")
        response.raise_for_status()
        return response.json()["patients"]


async def _fetch_patient(patient_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{EHR_BASE_URL}/api/patients/{patient_id}")
        response.raise_for_status()
        return response.json()["patient"]


async def _refresh_progress() -> tuple[list[str], bool]:
    if not state.patient_id:
        return [], False

    patient = await _fetch_patient(state.patient_id)
    scenario = next((item for item in patient["scenarios"] if item["id"] == state.scenario_id), None)
    encounter = next((item for item in patient["encounters"] if item["id"] == state.encounter_id), None)

    if not scenario or not encounter:
        return [], False

    completed: list[str] = []

    # Track each required order individually
    order_names = {order["name"] for order in encounter["orders"] if order["status"] == "SIGNED"}
    required_orders = scenario["requiredOrders"]
    for order_name in required_orders:
        if order_name in order_names:
            completed.append(f"order:{order_name}")

    # Track each required note element individually
    note_text = "\n".join(note["content"] for note in encounter["notes"])
    required_elements = scenario["requiredNoteElements"]
    for element in required_elements:
        if element.lower() in note_text.lower():
            completed.append(f"note_element:{element}")

    if encounter["status"] == "SIGNED":
        completed.append("encounter_signed")

    total_expected = len(required_orders) + len(required_elements) + 1
    return completed, len(completed) == total_expected


@asynccontextmanager
async def lifespan(_: FastAPI):
    await browser.ensure_started(headless=HEADLESS)
    yield
    await browser.close()


app = FastAPI(title="EHRGym Environment Server", version="0.1.0", lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/reset", response_model=ResetResponse)
async def reset(request: Optional[ResetRequest] = None) -> ResetResponse:
    global state, goal_text

    try:
        await _post_reset()
        patients = await _fetch_patients()
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail=f"Failed to reset EHR app: {error}") from error

    patient = next((item for item in patients if item["id"] == request.patient_id), None) if request else None
    patient = patient or patients[0]
    if not patient:
        raise HTTPException(status_code=500, detail="No synthetic patients available after reset")

    scenario = patient.get("scenario")
    encounter = patient.get("encounter")

    # Resolve task_id: explicit request > inferred from scenario
    task_id = (request.task_id if request and request.task_id else None) or (
        scenario.get("task_id") if scenario else None
    )

    # Pre-load task scoring so it's cached for step()
    if task_id:
        _load_task_scoring(task_id)

    state = EnvironmentState(
        episode_id=str(uuid4()),
        patient_id=patient["id"],
        encounter_id=encounter["id"] if encounter else None,
        scenario_id=scenario["id"] if scenario else None,
        task_id=task_id,
        rubric_progress=[],
        cumulative_reward=0.0,
        step_count=0,
    )
    goal_text = scenario["objective"] if scenario else "Open the chart and complete the assigned workflow."

    await browser.reset(EHR_BASE_URL)
    observation = await browser.observe(goal=goal_text, metadata={"reset": True})
    return ResetResponse(observation=observation, state=state)


@app.post("/step", response_model=StepResponse)
async def step(action: Action) -> StepResponse:
    global state

    try:
        metadata = await browser.perform(action, default_wait_ms=DEFAULT_WAIT_MS)
    except Exception as error:  # noqa: BLE001
        metadata = {"success": False, "error": str(error), "action_type": action.type}

    state.step_count += 1

    # ── Reward breakdown ──
    reward_breakdown: dict[str, float] = {}

    # 1. Action success / failure
    action_reward = REWARD_ACTION_SUCCESS if metadata.get("success") else REWARD_ACTION_FAILURE
    reward_breakdown["action"] = action_reward

    # 2. Per-step penalty (encourages efficiency)
    reward_breakdown["step_penalty"] = REWARD_STEP_PENALTY

    # 3. Incremental rubric progress — only reward NEWLY completed items
    previous_progress = set(state.rubric_progress)
    try:
        rubric_progress, done = await _refresh_progress()
    except httpx.HTTPError as error:
        rubric_progress, done = state.rubric_progress, False
        metadata["progress_error"] = str(error)

    new_items = set(rubric_progress) - previous_progress
    scoring = _load_task_scoring(state.task_id) if state.task_id else {}
    substep_weights = scoring.get("substeps", {})
    base_reward = scoring.get("base_reward", 1.0)

    rubric_reward = 0.0
    for item in new_items:
        weight = substep_weights.get(item, 0.1)  # default 0.1 if no task config
        rubric_reward += base_reward * weight
    reward_breakdown["rubric_progress"] = rubric_reward

    # 4. Completion bonus — only on the step that finishes everything
    completion_bonus = 0.0
    if done and not all(item in previous_progress for item in rubric_progress):
        completion_bonus = REWARD_COMPLETION_BONUS
    reward_breakdown["completion"] = completion_bonus

    # Total reward for this step
    reward = sum(reward_breakdown.values())

    state.rubric_progress = rubric_progress
    state.cumulative_reward += reward

    observation = await browser.observe(goal=goal_text, metadata=metadata)
    return StepResponse(
        observation=observation,
        state=state,
        reward=reward,
        done=done,
        info={
            "rubric_progress": rubric_progress,
            "new_rubric_items": sorted(new_items),
            "reward_breakdown": reward_breakdown,
        },
    )


@app.get("/state", response_model=EnvironmentState)
async def get_state() -> EnvironmentState:
    return state
