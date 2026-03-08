from __future__ import annotations

import asyncio
import base64
from typing import Any, Optional
from urllib.parse import urljoin

from playwright.async_api import Browser, Page, Playwright, async_playwright

from .models import Action, Observation


class BrowserSession:
    def __init__(self) -> None:
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def ensure_started(self, *, headless: bool) -> None:
        if self._browser and self.page:
            return

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=headless)
        context = await self._browser.new_context(viewport={"width": 1440, "height": 1024})
        self.page = await context.new_page()

    async def close(self) -> None:
        if self.page:
            await self.page.context.close()
            self.page = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def reset(self, base_url: str) -> None:
        if not self.page:
            raise RuntimeError("Browser session has not been started.")

        await self.page.goto(base_url, wait_until="networkidle")

    async def perform(self, action: Action, *, default_wait_ms: int) -> dict[str, Any]:
        if not self.page:
            raise RuntimeError("Browser session has not been started.")

        metadata: dict[str, Any] = {"action_type": action.type, "success": True}

        if action.type == "goto":
            target_url = action.url or "/"
            if not target_url.startswith("http"):
                current_origin = self.page.url.split("/", 3)
                base_origin = "/".join(current_origin[:3]) if len(current_origin) >= 3 else "http://127.0.0.1:3000"
                target_url = urljoin(f"{base_origin}/", target_url.lstrip("/"))
            await self.page.goto(target_url, wait_until="networkidle")
        elif action.type == "click":
            if not action.selector:
                raise ValueError("click action requires selector")
            url_before = self.page.url
            await self.page.locator(action.selector).click()
            # If the click triggered a navigation, wait for it to settle.
            await asyncio.sleep(0.15)
            if self.page.url != url_before:
                try:
                    await self.page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:  # noqa: BLE001
                    pass
        elif action.type == "fill":
            if not action.selector:
                raise ValueError("fill action requires selector")
            await self.page.locator(action.selector).fill(action.text or "")
        elif action.type == "keypress":
            if not action.key:
                raise ValueError("keypress action requires key")
            await self.page.keyboard.press(action.key)
        elif action.type == "wait":
            await asyncio.sleep((action.milliseconds or default_wait_ms) / 1000)
        else:
            metadata["success"] = False
            metadata["error"] = f"Unsupported action: {action.type}"

        return metadata

    async def observe(self, *, goal: str, metadata: dict[str, Any]) -> Observation:
        if not self.page:
            raise RuntimeError("Browser session has not been started.")

        screenshot = await self.page.screenshot(type="png")
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        current_url = self.page.url
        active_activity = "/" if current_url.endswith(":3000/") else current_url.rsplit("/", 1)[-1]

        return Observation(
            goal=goal,
            screenshot_b64=screenshot_b64,
            current_url=current_url,
            active_activity=active_activity,
            metadata=metadata,
        )
