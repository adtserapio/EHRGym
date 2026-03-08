from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import httpx

from trajectory_lib import (
    DEFAULT_ENV_SERVER_URL,
    TRAJECTORY_FORMAT,
    append_jsonl,
    create_trajectory_directory,
    decode_screenshot,
    load_action_bundle,
    post_json,
    strip_screenshot,
    summarize_step,
    utc_now_iso,
    write_json,
)

JsonDict = dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixed action sequence and persist a trajectory for demo replay.")
    parser.add_argument("action_file", help="Path to a JSON file containing an action bundle or array of actions.")
    parser.add_argument("--env-url", default=DEFAULT_ENV_SERVER_URL, help="Base URL of the environment server.")
    parser.add_argument("--output-root", default="runs/trajectories", help="Directory where trajectory folders are created.")
    parser.add_argument("--patient-id", help="Optional patient override for reset().")
    parser.add_argument("--scenario-id", help="Optional scenario override for reset().")
    parser.add_argument("--stop-on-done", action="store_true", help="Stop replaying actions once the environment reports done=true.")
    return parser.parse_args()


def save_step(steps_path: Path, screenshots_dir: Path, *, index: int, kind: str, action: JsonDict | None, response: JsonDict) -> None:
    observation = response["observation"]
    screenshot_name = f"{index:04d}-{kind}.png"
    decode_screenshot(observation, screenshots_dir / screenshot_name)
    append_jsonl(
        steps_path,
        {
            "index": index,
            "kind": kind,
            "timestamp": utc_now_iso(),
            "action": action,
            "reward": response.get("reward"),
            "done": response.get("done"),
            "info": response.get("info", {}),
            "state": response["state"],
            "observation": strip_screenshot(observation, screenshot_file=screenshot_name),
        },
    )


def main() -> None:
    args = parse_args()
    bundle = load_action_bundle(args.action_file)

    reset_request = dict(bundle.get("reset_request", {}))
    if args.patient_id:
        reset_request["patient_id"] = args.patient_id
    if args.scenario_id:
        reset_request["scenario_id"] = args.scenario_id

    trajectory_dir = create_trajectory_directory(args.output_root, task_id=bundle.get("task_id"))
    screenshots_dir = trajectory_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    steps_path = trajectory_dir / "steps.jsonl"

    with httpx.Client(base_url=args.env_url, timeout=60.0) as client:
        reset_response = post_json(client, "/reset", reset_request or None)
        save_step(steps_path, screenshots_dir, index=0, kind="reset", action=None, response=reset_response)
        print(f"reset | {summarize_step(reset_response)}")

        final_response = reset_response
        for index, action in enumerate(bundle["actions"], start=1):
            step_response = post_json(client, "/step", action)
            save_step(steps_path, screenshots_dir, index=index, kind="step", action=action, response=step_response)
            print(f"action[{index}]={action['type']} | {summarize_step(step_response)}")
            final_response = step_response
            if args.stop_on_done and step_response.get("done"):
                break

    manifest = {
        "format": TRAJECTORY_FORMAT,
        "created_at": utc_now_iso(),
        "env_url": args.env_url,
        "task_id": bundle.get("task_id"),
        "description": bundle.get("description"),
        "reset_request": reset_request,
        "source_action_file": str(Path(args.action_file).resolve()),
        "steps_file": "steps.jsonl",
        "screenshots_dir": "screenshots",
        "final_state": final_response["state"],
        "final_info": final_response.get("info", {}),
    }
    write_json(trajectory_dir / "manifest.json", manifest)
    print(f"saved trajectory to {trajectory_dir}")


if __name__ == "__main__":
    main()
