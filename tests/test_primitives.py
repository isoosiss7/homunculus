from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.primitives import BrowserPrimitives
from homunculus.role_ref import RoleRef


def _load_fixture_page(playwright, html: str):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.set_content(html, wait_until="domcontentloaded")
    return browser, context, page


def test_primitives_act_click_updates_result() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser, context, page = _load_fixture_page(playwright, html)
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        try:
            primitives = BrowserPrimitives(page)
            snapshot = primitives.snapshot()
            target_role_ref = RoleRef(role="button", name="Submit", nth=1).to_str()
            ref = next(item.ref for item in snapshot.items if item.role_ref == target_role_ref)

            primitives.act(ref, action="click")

            assert page.text_content("#result") == "clicked-1"
        finally:
            context.close()
            browser.close()
