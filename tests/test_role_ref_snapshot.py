from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.browser_snapshot import snapshot_role_refs
from homunculus.role_ref import RoleRef


def test_snapshot_role_refs() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        context = browser.new_context()
        try:
            page = context.new_page()
            page.set_content(html, wait_until="domcontentloaded")

            role_refs = snapshot_role_refs(page)

            assert RoleRef(role="button", name="Submit", nth=0).to_str() in role_refs
            assert RoleRef(role="button", name="Submit", nth=1).to_str() in role_refs
            assert RoleRef(role="textbox", name="User name", nth=0).to_str() in role_refs
        finally:
            context.close()
            browser.close()
