from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.browser_act import act_by_role_ref
from homunculus.browser_snapshot import snapshot_role_refs
from homunculus.role_ref import RoleRef


def test_role_ref_snapshot_act_roundtrip() -> None:
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
            expected_role_ref = RoleRef(role="button", name="Submit", nth=1).to_str()
            role_ref_str = next(ref for ref in role_refs if ref == expected_role_ref)

            act_by_role_ref(page, role_ref_str, action="click")

            assert page.text_content("#result") == "clicked-1"
        finally:
            context.close()
            browser.close()


def test_role_ref_snapshot_act_roundtrip_fill() -> None:
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
            expected_role_ref = RoleRef(role="textbox", name="User name", nth=0).to_str()
            role_ref_str = next(ref for ref in role_refs if ref == expected_role_ref)

            act_by_role_ref(page, role_ref_str, action="fill", value="Ada")

            assert page.text_content("#result") == "Ada"
        finally:
            context.close()
            browser.close()
