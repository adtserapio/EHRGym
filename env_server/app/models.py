from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


ActionType = Literal["goto", "click", "fill", "keypress", "wait"]


class Action(BaseModel):
    type: ActionType
    selector: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    key: Optional[str] = None
    milliseconds: Optional[int] = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Observation(BaseModel):
    goal: str
    screenshot_b64: str
    current_url: str
    active_activity: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnvironmentState(BaseModel):
    episode_id: str
    step_count: int = 0
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None
    scenario_id: Optional[str] = None
    task_id: Optional[str] = None
    rubric_progress: list[str] = Field(default_factory=list)
    cumulative_reward: float = 0.0


class ResetRequest(BaseModel):
    patient_id: Optional[str] = None
    scenario_id: Optional[str] = None
    task_id: Optional[str] = None


class ResetResponse(BaseModel):
    observation: Observation
    state: EnvironmentState


class StepResponse(BaseModel):
    observation: Observation
    state: EnvironmentState
    reward: float
    done: bool
    info: dict[str, Any] = Field(default_factory=dict)
