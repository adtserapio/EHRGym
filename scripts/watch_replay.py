"""
Smooth headed Playwright replay — drives the browser directly without the
env server, so there are no screenshots, no progress-check HTTP calls,
and no per-step overhead.  The result is a visually seamless demo.

Usage (from repo root):

  1. Make sure the Next.js EHR app is running on port 3000:
       npm run dev:ehr          # or: npm run watch:ehr

  2. Replay:
       python scripts/watch_replay.py tasks/examples/aki-demo-actions.json

  Options:
    --pause-ms 1200        delay between actions (default 800)
    --ehr-url …            base URL of the EHR app (default http://127.0.0.1:3000)
    --reset                POST /api/dev/reset before starting (default: on)
    --no-reset             skip the DB reset
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from playwright.async_api import async_playwright

JsonDict = dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smooth headed replay — Playwright only, no env server.",
    )
    parser.add_argument(
        "action_file",
        help="Path to a JSON action bundle or array of actions.",
    )
    parser.add_argument(
        "--ehr-url",
        default="http://127.0.0.1:3000",
        help="Base URL of the running EHR app (default: http://127.0.0.1:3000).",
    )
    parser.add_argument(
        "--pause-ms",
        type=int,
        default=800,
        help="Milliseconds to wait between actions (default: 800).",
    )
    parser.add_argument(
        "--reset",
        dest="do_reset",
        action="store_true",
        default=True,
        help="POST /api/dev/reset before the replay (default).",
    )
    parser.add_argument(
        "--no-reset",
        dest="do_reset",
        action="store_false",
        help="Skip the database reset.",
    )
    return parser.parse_args()


def load_bundle(path: str | Path) -> tuple[list[JsonDict], JsonDict | None]:
    raw = json.loads(Path(path).read_text())
    if isinstance(raw, list):
        return raw, None
    if isinstance(raw, dict) and "actions" in raw:
        return raw["actions"], raw.get("reset_request")
    raise ValueError("Action file must be a JSON array or an object with an 'actions' key.")


async def _reset_db(ehr_url: str) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{ehr_url}/api/dev/reset")
        response.raise_for_status()
    print("database reset ✓")


async def run(args: argparse.Namespace) -> None:
    actions, _ = load_bundle(args.action_file)
    pause_seconds = max(args.pause_ms, 0) / 1000

    if args.do_reset:
        await _reset_db(args.ehr_url)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 1024})
        page = await context.new_page()

        print("navigating to EHR …")
        await page.goto(args.ehr_url, wait_until="networkidle")
        print(f"loaded  {page.url}")
        await asyncio.sleep(pause_seconds)

        for index, action in enumerate(actions, start=1):
            action_type = action["type"]
            label = action.get("selector") or action.get("url") or action.get("key") or ""

            if action_type == "goto":
                target = action.get("url", "/")
                if not target.startswith("http"):
                    target = urljoin(f"{args.ehr_url}/", target.lstrip("/"))
                await page.goto(target, wait_until="networkidle")
            elif action_type == "click":
                selector = action["selector"]
                # Wait until the target is visible to avoid acting on a loading page.
                await page.locator(selector).wait_for(state="visible", timeout=5000)
                await page.locator(selector).click()
                # If it triggered a real navigation (not just a hash change), wait.
                await page.wait_for_load_state("domcontentloaded", timeout=5000)
            elif action_type == "fill":
                selector = action["selector"]
                await page.locator(selector).wait_for(state="visible", timeout=5000)
                await page.locator(selector).fill(action.get("text", ""))
            elif action_type == "keypress":
                await page.keyboard.press(action["key"])
            elif action_type == "wait":
                await asyncio.sleep((action.get("milliseconds", 500)) / 1000)
                # Don't add the normal inter-step pause on top of explicit waits.
                print(f"  [{index}/{len(actions)}] wait {action.get('milliseconds', 500)}ms")
                continue
            else:
                print(f"  [{index}/{len(actions)}] ⚠ unknown action type: {action_type}")
                continue

            print(f"  [{index}/{len(actions)}] {action_type:6s} {label}")
            await asyncio.sleep(pause_seconds)

        print("replay finished — press Ctrl-C to close the browser")
        try:
            # Keep browser open so the user can inspect the result.
            await asyncio.Event().wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await context.close()
            await browser.close()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
