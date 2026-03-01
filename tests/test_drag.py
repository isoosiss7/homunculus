from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.browser_act import drag_by_role_ref
from homunculus.role_ref import RoleRef
from homunculus.role_snapshot import snapshot_role_snapshot
from homunculus.role_snapshot_act import snapshot_then_drag_by_ref


def test_drag_by_role_ref() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "drag_drop.html"
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

            start_role_ref = RoleRef(role="button", name="Drag source", nth=0).to_str()
            end_role_ref = RoleRef(role="button", name="Drop target", nth=0).to_str()

            drag_by_role_ref(page, start_role_ref, end_role_ref)

            assert page.text_content("#result") == "dropped:payload"
        finally:
            context.close()
            browser.close()


def test_snapshot_then_drag_by_ref() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "drag_drop.html"
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

            snapshot = snapshot_role_snapshot(page)
            start_role_ref = RoleRef(role="button", name="Drag source", nth=0).to_str()
            end_role_ref = RoleRef(role="button", name="Drop target", nth=0).to_str()
            start_ref = next(item.ref for item in snapshot.items if item.role_ref == start_role_ref)
            end_ref = next(item.ref for item in snapshot.items if item.role_ref == end_role_ref)

            snapshot_then_drag_by_ref(page, start_ref, end_ref)

            assert page.text_content("#result") == "dropped:payload"
        finally:
            context.close()
            browser.close()
