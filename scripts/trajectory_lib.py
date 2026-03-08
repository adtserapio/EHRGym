from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

DEFAULT_ENV_SERVER_URL = "http://127.0.0.1:8000"
TRAJECTORY_FORMAT = "ehrgym-trajectory.v1"


JsonDict = dict[str, Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip("-") or "trajectory"


def load_json(file_path: str | Path) -> Any:
    return json.loads(Path(file_path).read_text())


def write_json(file_path: str | Path, payload: Any) -> None:
    Path(file_path).write_text(json.dumps(payload, indent=2) + "\n")


def append_jsonl(file_path: str | Path, payload: JsonDict) -> None:
    with Path(file_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def create_trajectory_directory(output_root: str | Path, *, task_id: str | None = None) -> Path:
    base_name = slugify(task_id or "trajectory")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return ensure_directory(Path(output_root) / f"{timestamp}-{base_name}")


def load_action_bundle(file_path: str | Path) -> JsonDict:
    raw = load_json(file_path)
    if isinstance(raw, list):
        return {"actions": raw, "reset_request": {}, "task_id": Path(file_path).stem}
    if not isinstance(raw, dict):
        raise ValueError("Action file must contain either a JSON array or object.")
    if "actions" not in raw or not isinstance(raw["actions"], list):
        raise ValueError("Action bundle object must contain an 'actions' array.")
    return raw


def decode_screenshot(observation: JsonDict, file_path: str | Path) -> str | None:
    screenshot_b64 = observation.get("screenshot_b64")
    if not screenshot_b64:
        return None
    destination = Path(file_path)
    destination.write_bytes(base64.b64decode(screenshot_b64))
    return destination.name


def strip_screenshot(observation: JsonDict, *, screenshot_file: str | None) -> JsonDict:
    return {
        "goal": observation.get("goal"),
        "current_url": observation.get("current_url"),
        "active_activity": observation.get("active_activity"),
        "metadata": observation.get("metadata", {}),
        "screenshot_file": screenshot_file,
    }


def post_json(client: httpx.Client, path: str, payload: JsonDict | None = None) -> JsonDict:
    response = client.post(path, json=payload)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object from {path}, got {type(data).__name__}.")
    return data


def summarize_step(step: JsonDict) -> str:
    state = step.get("state", {})
    observation = step.get("observation", {})
    reward = step.get("reward")
    done = step.get("done")
    parts = [
        f"step={state.get('step_count', '?')}",
        f"activity={observation.get('active_activity', '?')}",
        f"url={observation.get('current_url', '?')}",
    ]
    if reward is not None:
        parts.append(f"reward={reward:.3f}")
    if done is not None:
        parts.append(f"done={done}")
    return " | ".join(parts)


def build_allowed_actions() -> list[JsonDict]:
    return [
        {"type": "goto", "fields": ["url"]},
        {"type": "click", "fields": ["selector"]},
        {"type": "fill", "fields": ["selector", "text"]},
        {"type": "keypress", "fields": ["key"]},
        {"type": "wait", "fields": ["milliseconds"]},
    ]
