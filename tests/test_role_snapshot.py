from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.role_ref import RoleRef
from homunculus.role_snapshot import act_by_ref, snapshot_role_snapshot


def test_snapshot_role_snapshot_deterministic_dense_refs() -> None:
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

            snapshot = snapshot_role_snapshot(page)

            refs = [item.ref for item in snapshot.items]
            assert refs == [f"e{index}" for index in range(1, len(refs) + 1)]

            expected_role_refs = [
                RoleRef(role="button", name="Double target", nth=0).to_str(),
                RoleRef(role="button", name="Hover target", nth=0).to_str(),
                RoleRef(role="button", name="Modifier target", nth=0).to_str(),
                RoleRef(role="button", name="Submit", nth=0).to_str(),
                RoleRef(role="button", name="Submit", nth=1).to_str(),
                RoleRef(role="combobox", name="Assistant", nth=0).to_str(),
                RoleRef(role="textbox", name="Typing target", nth=0).to_str(),
                RoleRef(role="textbox", name="User name", nth=0).to_str(),
            ]
            assert [item.role_ref for item in snapshot.items] == expected_role_refs
            assert snapshot.stats["count"] == len(expected_role_refs)
        finally:
            context.close()
            browser.close()


def test_act_by_ref_rejects_unknown_ref() -> None:
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

            snapshot = snapshot_role_snapshot(page)
            with pytest.raises(ValueError, match="e999"):
                act_by_ref(page, snapshot, "e999", action="click")
        finally:
            context.close()
            browser.close()


def test_snapshot_role_snapshot_scoped_by_selector() -> None:
    html = """
    <div id="left">
      <button>Save</button>
      <input aria-label="Name" />
    </div>
    <div id="right">
      <button>Save</button>
      <input aria-label="Name" />
    </div>
    """

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        context = browser.new_context()
        try:
            page = context.new_page()
            page.set_content(html, wait_until="domcontentloaded")

            snapshot = snapshot_role_snapshot(page, selector="#left")

            expected_role_refs = [
                RoleRef(role="button", name="Save", nth=0).to_str(),
                RoleRef(role="textbox", name="Name", nth=0).to_str(),
            ]
            assert [item.role_ref for item in snapshot.items] == expected_role_refs
            assert snapshot.stats["count"] == len(expected_role_refs)
        finally:
            context.close()
            browser.close()
