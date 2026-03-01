from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.role_ref import RoleRef
from homunculus.role_snapshot import snapshot_role_snapshot
from homunculus.role_snapshot_act import (
    snapshot_then_act_by_ref,
    snapshot_then_evaluate_by_ref,
    snapshot_then_extract_text_by_ref,
)


def _load_fixture_page(playwright, html: str):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.set_content(html, wait_until="domcontentloaded")
    return browser, context, page


def test_snapshot_then_act_by_ref_click() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser, context, page = _load_fixture_page(playwright, html)
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        try:
            snapshot = snapshot_role_snapshot(page)
            target_role_ref = RoleRef(
                role="button",
                name="Submit",
                nth=1,
            ).to_str()
            ref = next(item.ref for item in snapshot.items if item.role_ref == target_role_ref)

            snapshot_then_act_by_ref(page, ref, action="click")

            assert page.text_content("#result") == "clicked-1"
        finally:
            context.close()
            browser.close()


def test_snapshot_then_act_by_ref_missing_ref_click() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser, context, page = _load_fixture_page(playwright, html)
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        try:
            with pytest.raises(ValueError, match="e999"):
                snapshot_then_act_by_ref(page, "e999", action="click")
        finally:
            context.close()
            browser.close()


def test_snapshot_then_act_by_ref_missing_ref_wait_noop() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser, context, page = _load_fixture_page(playwright, html)
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        try:
            snapshot_then_act_by_ref(page, "e999", action="wait")

            assert page.text_content("#result") == "idle"
        finally:
            context.close()
            browser.close()


def test_snapshot_then_extract_text_by_ref_missing_ref_timeout() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser, context, page = _load_fixture_page(playwright, html)
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        try:
            snapshot, text = snapshot_then_extract_text_by_ref(page, "e999", timeout_ms=100)

            assert snapshot.stats["count"] > 0
            assert text == ""
        finally:
            context.close()
            browser.close()


def test_snapshot_then_evaluate_by_ref_text_content() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser, context, page = _load_fixture_page(playwright, html)
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        try:
            snapshot = snapshot_role_snapshot(page)
            target_role_ref = RoleRef(role="button", name="Submit", nth=0).to_str()
            ref = next(item.ref for item in snapshot.items if item.role_ref == target_role_ref)

            snapshot, result = snapshot_then_evaluate_by_ref(page, ref, "(el) => el.textContent")

            assert snapshot.stats["count"] > 0
            assert result == "Submit"
        finally:
            context.close()
            browser.close()


def test_snapshot_then_evaluate_by_ref_missing_ref_timeout() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    html = fixture_path.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        try:
            browser, context, page = _load_fixture_page(playwright, html)
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")

        try:
            snapshot, result = snapshot_then_evaluate_by_ref(
                page, "e999", "(el) => el.textContent", timeout_ms=100
            )

            assert snapshot.stats["count"] > 0
            assert result is None
        finally:
            context.close()
            browser.close()
