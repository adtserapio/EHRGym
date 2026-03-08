# Offline training workflow

This workflow avoids live SSH-dependent demos while still producing real supervised training data for a remote GPU run.

## What you will produce

1. A recorded trajectory directory under `runs/trajectories/`
2. A replayable live demo using the same actions
3. An SFT-ready dataset in JSONL format under `runs/datasets/`

## Scripts

- [scripts/record_trajectory.py](../scripts/record_trajectory.py)
- [scripts/replay_trajectory.py](../scripts/replay_trajectory.py)
- [scripts/export_sft_dataset.py](../scripts/export_sft_dataset.py)
- [tasks/examples/aki-demo-actions.json](../tasks/examples/aki-demo-actions.json)

## Step-by-step

### 1. Start the app and env locally

```bash
npm run dev
```

This gives:
- EHR UI on `http://127.0.0.1:3000`
- Env server on `http://127.0.0.1:8000`

### 2. Record a deterministic trajectory

```bash
python scripts/record_trajectory.py tasks/examples/aki-demo-actions.json --stop-on-done
```

This creates a directory like:
- `runs/trajectories/20260307-120000-aki-chart-review-demo/`

with:
- `manifest.json`
- `steps.jsonl`
- `screenshots/`

### 3. Replay the trajectory for a reliable demo

```bash
python scripts/replay_trajectory.py runs/trajectories/<YOUR_TRAJECTORY_DIR>
```

### 4. Export SFT training data

```bash
python scripts/export_sft_dataset.py runs/trajectories --output runs/datasets/ehrgym_sft.jsonl
```

The output is JSONL with one next-action training example per step.

### 5. Copy the dataset to the remote GPU box

Example with `scp`:

```bash
scp runs/datasets/ehrgym_sft.jsonl <user>@<gpu-host>:/workspace/data/
```

Or upload the whole directory:

```bash
scp -r runs/datasets <user>@<gpu-host>:/workspace/
```

## Record more than one demo

After you create more action bundles, rerun the recorder and then rerun the exporter over the whole `runs/trajectories/` directory.

## Notes

- The exporter uses the observation from step `t` as the input and the action at step `t+1` as the supervised target.
- Screenshot paths are stored as absolute paths by default.
- For text-only experiments, export without image paths:

```bash
python scripts/export_sft_dataset.py runs/trajectories --image-mode none --output runs/datasets/ehrgym_sft_textonly.jsonl
```
