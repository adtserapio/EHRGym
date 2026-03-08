#!/usr/bin/env python3
"""
Sync the scenario blocks in shared/seed-data.ts with the task JSON files.

For each patient (pat-100X), reads the corresponding task JSON and updates:
  - title
  - objective
  - rubric (generated from orders + note elements)
  - requiredOrders
  - requiredNoteElements
"""

import json
import glob
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_FILE = os.path.join(ROOT, "shared", "seed-data.ts")
TASK_DIR = os.path.join(ROOT, "tasks", "examples")


def load_tasks():
    """Load all task JSONs keyed by patient_id."""
    tasks = {}
    for f in sorted(glob.glob(os.path.join(TASK_DIR, "*.json"))):
        with open(f) as fh:
            t = json.load(fh)
        pid = t.get("patient_id")
        if not pid:
            continue
        tasks[pid] = t
    return tasks


def build_rubric(task):
    """Generate a rubric list from task data."""
    rubric = []
    # Step 1: Review
    rubric.append("Review relevant labs, vitals, and clinical notes")
    # Steps for orders
    for order in task["required_orders"]:
        rubric.append(f"Place order: {order}")
    # Steps for note elements
    note_count = len(task["required_note_elements"])
    if note_count <= 3:
        rubric.append("Document clinical assessment and plan")
    else:
        rubric.append("Document comprehensive clinical assessment and plan")
    rubric.append("Sign the encounter")
    return rubric


def ts_string_array(items, indent=8):
    """Format a Python list as a TypeScript string array."""
    prefix = " " * indent
    if len(items) <= 3 and all(len(s) < 40 for s in items):
        inner = ", ".join(f'"{s}"' for s in items)
        return f"[{inner}]"
    lines = [f"{prefix}  \"{item}\"" for item in items]
    return "[\n" + ",\n".join(lines) + f"\n{prefix}]"


def build_scenario_block(scn_id, task):
    """Build the full scenario TypeScript object literal."""
    title = task["title"]
    objective = task["objective"]
    rubric = build_rubric(task)
    orders = task["required_orders"]
    notes = task["required_note_elements"]

    lines = []
    lines.append(f'      {{')
    lines.append(f'        id: "{scn_id}",')
    lines.append(f'        title: "{title}",')
    # Objective might be long, keep on one line
    lines.append(f'        objective: "{objective}",')
    lines.append(f'        rubric: {ts_string_array(rubric, 8)},')
    lines.append(f'        requiredOrders: {ts_string_array(orders, 8)},')
    lines.append(f'        requiredNoteElements: {ts_string_array(notes, 8)}')
    lines.append(f'      }}')
    return "\n".join(lines)


def main():
    tasks = load_tasks()
    print(f"Loaded {len(tasks)} task definitions")

    with open(SEED_FILE, "r") as f:
        content = f.read()

    # Match each scenario block: from { id: "scn-XXXX" to the closing }
    # Pattern: scenarios: [\n      {\n        id: "scn-XXXX", ... \n      }\n    ]
    pattern = re.compile(
        r'(scenarios:\s*\[\s*\n)'           # "scenarios: [\n"
        r'(\s*\{[^}]*?id:\s*"(scn-\d+)"'   # opening { with id
        r'[^}]*?\})'                         # rest of the object up to }
        r'(\s*\n\s*\])',                     # closing "]"
        re.DOTALL
    )

    replacements = 0
    skipped = 0

    def replace_scenario(match):
        nonlocal replacements, skipped
        prefix = match.group(1)
        scn_id = match.group(3)
        suffix = match.group(4)

        # scn-100X maps to pat-100X
        pat_id = scn_id.replace("scn-", "pat-")
        task = tasks.get(pat_id)

        if not task:
            print(f"  WARNING: No task found for {pat_id} (scenario {scn_id})")
            skipped += 1
            return match.group(0)

        new_block = build_scenario_block(scn_id, task)
        replacements += 1
        print(f"  Updated {scn_id} ({pat_id}): {task['title']}")
        return prefix + new_block + suffix

    new_content = pattern.sub(replace_scenario, content)

    if replacements > 0:
        with open(SEED_FILE, "w") as f:
            f.write(new_content)
        print(f"\nDone: {replacements} scenarios updated, {skipped} skipped")
    else:
        print("\nNo scenarios matched. Check the regex pattern.")
        # Debug: find scenario blocks
        simple = re.findall(r'scenarios:\s*\[', content)
        print(f"  Found {len(simple)} 'scenarios: [' occurrences")


if __name__ == "__main__":
    main()
