from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import httpx

from trajectory_lib import (
    DEFAULT_ENV_SERVER_URL,
    TRAJECTORY_FORMAT,
    append_jsonl,
    build_allowed_actions,
    create_trajectory_directory,
    decode_screenshot,
    post_json,
    strip_screenshot,
    summarize_step,
    utc_now_iso,
    write_json,
)

JsonDict = dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a remote VLM policy against the environment server and optionally save the rollout.")
    parser.add_argument("--policy-url", required=True, help="HTTP endpoint that returns the next action. Best used through an SSH tunnel.")
    parser.add_argument("--env-url", default=DEFAULT_ENV_SERVER_URL, help="Base URL of the environment server.")
    parser.add_argument("--max-steps", type=int, default=20, help="Maximum number of policy decisions to request.")
    parser.add_argument("--patient-id", help="Optional patient override for reset().")
    parser.add_argument("--scenario-id", help="Optional scenario override for reset().")
    parser.add_argument("--output-root", help="Optional rollout directory root. When set, a trajectory is saved.")
    return parser.parse_args()


def save_step(steps_path: Path, screenshots_dir: Path, *, index: int, kind: str, action: JsonDict | None, response: JsonDict, policy_payload: JsonDict | None = None, policy_response: JsonDict | None = None) -> None:
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
            "policy_request": policy_payload,
            "policy_response": policy_response,
        },
    )


def request_action(client: httpx.Client, policy_url: str, response: JsonDict) -> tuple[JsonDict, JsonDict]:
    payload = {
        "timestamp": utc_now_iso(),
        "goal": response["observation"]["goal"],
        "observation": response["observation"],
        "state": response["state"],
        "allowed_actions": build_allowed_actions(),
    }
    policy_response = client.post(policy_url, json=payload)
    policy_response.raise_for_status()
    data = policy_response.json()
    if isinstance(data, dict) and "action" in data:
        action = data["action"]
    elif isinstance(data, dict):
        action = data
    else:
        raise ValueError("Policy endpoint must return a JSON object or an object with an 'action' field.")
    if not isinstance(action, dict) or "type" not in action:
        raise ValueError("Policy action must be a JSON object containing a 'type' field.")
    return payload, data


def main() -> None:
    args = parse_args()
    reset_request = {key: value for key, value in {"patient_id": args.patient_id, "scenario_id": args.scenario_id}.items() if value}

    trajectory_dir: Path | None = None
    steps_path: Path | None = None
    screenshots_dir: Path | None = None
    if args.output_root:
        trajectory_dir = create_trajectory_directory(args.output_root, task_id="remote-vlm-rollout")
        steps_path = trajectory_dir / "steps.jsonl"
        screenshots_dir = trajectory_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(base_url=args.env_url, timeout=90.0) as env_client, httpx.Client(timeout=90.0) as policy_client:
        reset_response = post_json(env_client, "/reset", reset_request or None)
        current_response = reset_response
        print(f"reset | {summarize_step(current_response)}")

        if steps_path and screenshots_dir:
            save_step(steps_path, screenshots_dir, index=0, kind="reset", action=None, response=current_response)

        for index in range(1, args.max_steps + 1):
            policy_payload, policy_response = request_action(policy_client, args.policy_url, current_response)
            action = policy_response.get("action", policy_response)
            current_response = post_json(env_client, "/step", action)
            print(f"policy[{index}]={action['type']} | {summarize_step(current_response)}")
            if steps_path and screenshots_dir:
                save_step(
                    steps_path,
                    screenshots_dir,
                    index=index,
                    kind="step",
                    action=action,
                    response=current_response,
                    policy_payload=policy_payload,
                    policy_response=policy_response,
                )
            if current_response.get("done"):
                break

    if trajectory_dir:
        write_json(
            trajectory_dir / "manifest.json",
            {
                "format": TRAJECTORY_FORMAT,
                "created_at": utc_now_iso(),
                "env_url": args.env_url,
                "policy_url": args.policy_url,
                "reset_request": reset_request,
                "steps_file": "steps.jsonl",
                "screenshots_dir": "screenshots",
                "final_state": current_response["state"],
                "final_info": current_response.get("info", {}),
            },
        )
        print(f"saved rollout to {trajectory_dir}")


if __name__ == "__main__":
    main()
