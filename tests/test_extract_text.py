from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.browser_act import extract_text_by_role_ref
from homunculus.role_ref import RoleRef
from homunculus.snapshot_act import snapshot_then_extract_text_by_role_ref


def test_extract_text_by_role_ref_visible() -> None:
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
            text = extract_text_by_role_ref(page, role_ref_str)

            assert text == "Submit"
        finally:
            context.close()
            browser.close()


def test_extract_text_by_role_ref_waits_for_visibility() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref_wait.html"
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

            role_ref_str = RoleRef(
                role="button",
                name="Delayed button",
                nth=0,
            ).to_str()
            text = extract_text_by_role_ref(page, role_ref_str, timeout_ms=2000)

            assert text == "Delayed button"
        finally:
            context.close()
            browser.close()


def test_snapshot_then_extract_text_by_role_ref_missing_role() -> None:
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
                snapshot_then_extract_text_by_role_ref(page, role_ref_str)
        finally:
            context.close()
            browser.close()


def test_snapshot_then_extract_text_by_role_ref_success() -> None:
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

            role_ref_str = RoleRef(role="button", name="Submit", nth=0).to_str()
            text = snapshot_then_extract_text_by_role_ref(page, role_ref_str)

            assert text == "Submit"
        finally:
            context.close()
            browser.close()
