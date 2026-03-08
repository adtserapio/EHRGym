# Remote VLM demo flow

This repository now includes a simple path to demo computer-use behavior without depending on a fully live end-to-end remote inference loop.

## Recommended demo modes

### 1. Offline trajectory replay

Use a deterministic action bundle to create a trajectory once, then replay it live against a fresh reset during a demo.

Files:
- [tasks/examples/aki-demo-actions.json](../tasks/examples/aki-demo-actions.json)
- [scripts/record_trajectory.py](../scripts/record_trajectory.py)
- [scripts/replay_trajectory.py](../scripts/replay_trajectory.py)

Typical flow:
1. Start the EHR app and env server.
2. Record a trajectory from a fixed action bundle.
3. Save screenshots and step-by-step JSONL.
4. Replay the saved actions in front of an audience.

Trajectory layout:
- `manifest.json`: metadata, reset request, final state
- `steps.jsonl`: one row per reset/step event
- `screenshots/`: screenshot per step

## 2. Remote VLM rollout through SSH tunnel

Use a small remote policy server on the GPU machine and call it over HTTP through SSH port forwarding.

File:
- [scripts/remote_vlm_agent.py](../scripts/remote_vlm_agent.py)

Recommended topology:
- local machine or Hugging Face Space: runs the environment and browser
- remote GPU server: runs the VLM inference service
- SSH tunnel: forwards the remote policy port to localhost

Example tunnel shape:
- local `localhost:9000` -> remote `localhost:9000`

The local rollout script then calls the policy endpoint on `http://127.0.0.1:9000/act`.

## Remote policy contract

Expected request payload:

```json
{
  "timestamp": "2026-03-07T00:00:00Z",
  "goal": "Review the patient chart and complete the workflow.",
  "observation": {
    "goal": "Review the patient chart and complete the workflow.",
    "screenshot_b64": "<base64 PNG>",
    "current_url": "http://127.0.0.1:3000/patient/pat-1001",
    "active_activity": "pat-1001",
    "metadata": {}
  },
  "state": {
    "episode_id": "...",
    "step_count": 3,
    "patient_id": "pat-1001",
    "encounter_id": "enc-1001",
    "scenario_id": "scn-1001",
    "rubric_progress": [],
    "cumulative_reward": 0.06
  },
  "allowed_actions": [
    {"type": "goto", "fields": ["url"]},
    {"type": "click", "fields": ["selector"]},
    {"type": "fill", "fields": ["selector", "text"]},
    {"type": "keypress", "fields": ["key"]},
    {"type": "wait", "fields": ["milliseconds"]}
  ]
}
```

Accepted response payloads:

```json
{"action": {"type": "click", "selector": "[data-testid='activity-orders']"}}
```

or:

```json
{"type": "click", "selector": "[data-testid='activity-orders']"}
```

## Practical recommendation

For the first H100-backed demo:
1. Generate one stable offline trajectory.
2. Replay it live.
3. If desired, switch to the remote VLM for the final few steps.

This is more reliable than a fully live remote rollout while still exercising the real environment.
