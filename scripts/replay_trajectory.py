from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import httpx

from trajectory_lib import DEFAULT_ENV_SERVER_URL, load_json, post_json, summarize_step

JsonDict = dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay a saved trajectory against a fresh environment reset.")
    parser.add_argument("trajectory", help="Path to a trajectory directory or its manifest.json file.")
    parser.add_argument("--env-url", default=DEFAULT_ENV_SERVER_URL, help="Base URL of the environment server.")
    parser.add_argument("--pause-ms", type=int, default=400, help="Delay between replayed actions.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Wait for Enter before each action so the browser can be stepped through manually.",
    )
    parser.add_argument("--stop-on-done", action="store_true", help="Stop when the replayed environment reports done=true.")
    return parser.parse_args()


def resolve_manifest(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_dir():
        path = path / "manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    return path


def load_steps(steps_path: Path) -> list[JsonDict]:
    rows: list[JsonDict] = []
    with steps_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    args = parse_args()
    manifest_path = resolve_manifest(args.trajectory)
    manifest = load_json(manifest_path)
    trajectory_dir = manifest_path.parent
    steps = load_steps(trajectory_dir / manifest["steps_file"])

    reset_request = manifest.get("reset_request") or None
    action_steps = [step for step in steps if step["kind"] == "step"]

    with httpx.Client(base_url=args.env_url, timeout=60.0) as client:
        reset_response = post_json(client, "/reset", reset_request)
        print(f"reset | {summarize_step(reset_response)}")

        for step in action_steps:
            action = step["action"]
            if args.interactive:
                print(f"next[{step['index']}]={action['type']} | action={json.dumps(action)}")
                input("Press Enter to replay this action...")
            response = post_json(client, "/step", action)
            print(f"replay[{step['index']}]={action['type']} | {summarize_step(response)}")
            if args.stop_on_done and response.get("done"):
                break
            if not args.interactive:
                time.sleep(max(args.pause_ms, 0) / 1000)

    print(f"replayed {len(action_steps)} actions from {trajectory_dir}")


if __name__ == "__main__":
    main()
