from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from trajectory_lib import load_json, utc_now_iso, write_json

JsonDict = dict[str, Any]

SYSTEM_PROMPT = (
    "You are a clinical computer-use agent operating an Epic-like EHR. "
    "Given the current screenshot, URL, activity, task goal, and state metadata, "
    "return exactly one valid next action as strict JSON."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert recorded trajectories into SFT-ready JSONL examples.")
    parser.add_argument(
        "trajectory_root",
        help="Directory containing one or more trajectory folders, each with manifest.json and steps.jsonl.",
    )
    parser.add_argument(
        "--output",
        default="runs/datasets/ehrgym_sft.jsonl",
        help="Path to the output JSONL dataset file.",
    )
    parser.add_argument(
        "--image-mode",
        choices=["path", "none"],
        default="path",
        help="Whether to include screenshot file paths in each example.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional maximum number of examples to export. 0 means no limit.",
    )
    return parser.parse_args()


def find_trajectory_dirs(root: Path) -> list[Path]:
    manifests = sorted(root.glob("**/manifest.json"))
    return [manifest.parent for manifest in manifests]


def load_steps(trajectory_dir: Path, steps_file: str) -> list[JsonDict]:
    rows: list[JsonDict] = []
    with (trajectory_dir / steps_file).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_user_payload(trajectory_dir: Path, manifest: JsonDict, current_step: JsonDict) -> JsonDict:
    observation = current_step["observation"]
    payload: JsonDict = {
        "goal": observation["goal"],
        "current_url": observation["current_url"],
        "active_activity": observation["active_activity"],
        "state": current_step["state"],
        "metadata": observation.get("metadata", {}),
        "task_id": manifest.get("task_id"),
        "trajectory_format": manifest.get("format"),
    }

    screenshot_file = observation.get("screenshot_file")
    if screenshot_file:
        payload["screenshot_path"] = str((trajectory_dir / manifest["screenshots_dir"] / screenshot_file).resolve())

    return payload


def build_example(trajectory_dir: Path, manifest: JsonDict, previous_step: JsonDict, target_step: JsonDict, *, image_mode: str) -> JsonDict:
    user_payload = build_user_payload(trajectory_dir, manifest, previous_step)
    if image_mode == "none":
        user_payload.pop("screenshot_path", None)

    target_action = target_step["action"]
    example_id = f"{manifest.get('task_id', 'task')}-{target_step['index']:04d}"
    return {
        "id": example_id,
        "created_at": utc_now_iso(),
        "source_manifest": str((trajectory_dir / "manifest.json").resolve()),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            {"role": "assistant", "content": json.dumps(target_action, ensure_ascii=False)},
        ],
        "target_action": target_action,
        "reward": target_step.get("reward"),
        "done": target_step.get("done"),
        "info": target_step.get("info", {}),
        "state_before": previous_step["state"],
        "state_after": target_step["state"],
    }


def main() -> None:
    args = parse_args()
    root = Path(args.trajectory_root)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    trajectory_dirs = find_trajectory_dirs(root)
    if not trajectory_dirs:
        raise FileNotFoundError(f"No manifest.json files found under {root}")

    count = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for trajectory_dir in trajectory_dirs:
            manifest = load_json(trajectory_dir / "manifest.json")
            steps = load_steps(trajectory_dir, manifest["steps_file"])
            for previous_step, target_step in zip(steps, steps[1:]):
                if target_step.get("kind") != "step" or not target_step.get("action"):
                    continue
                example = build_example(
                    trajectory_dir,
                    manifest,
                    previous_step,
                    target_step,
                    image_mode=args.image_mode,
                )
                handle.write(json.dumps(example, ensure_ascii=False) + "\n")
                count += 1
                if args.limit and count >= args.limit:
                    break
            if args.limit and count >= args.limit:
                break

    summary = {
        "trajectory_root": str(root.resolve()),
        "output": str(output_path.resolve()),
        "examples": count,
        "image_mode": args.image_mode,
    }
    write_json(output_path.with_suffix(output_path.suffix + ".summary.json"), summary)
    print(f"wrote {count} examples to {output_path}")


if __name__ == "__main__":
    main()
