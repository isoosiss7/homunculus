from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.role_ref import RoleRef
from homunculus.snapshot_act import snapshot_then_act_by_role_ref


def test_snapshot_then_act_by_role_ref_click() -> None:
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

            role_ref_str = RoleRef(role="button", name="Submit", nth=1).to_str()
            snapshot_then_act_by_role_ref(page, role_ref_str, action="click")

            assert page.text_content("#result") == "clicked-1"
        finally:
            context.close()
            browser.close()


def test_snapshot_then_act_by_role_ref_missing_role() -> None:
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

            role_ref_str = RoleRef(role="button", name="Missing", nth=0).to_str()
            with pytest.raises(ValueError, match=role_ref_str):
                snapshot_then_act_by_role_ref(page, role_ref_str, action="click")
        finally:
            context.close()
            browser.close()
