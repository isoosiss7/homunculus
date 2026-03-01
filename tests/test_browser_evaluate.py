from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.browser_evaluate import evaluate_by_role_ref, evaluate_page
from homunculus.role_ref import RoleRef


def test_evaluate_by_role_ref_text_content() -> None:
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
            result = evaluate_by_role_ref(page, role_ref_str, "(el) => el.textContent")

            assert result == "Submit"
        finally:
            context.close()
            browser.close()


def test_evaluate_page_reads_title() -> None:
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

            result = evaluate_page(page, "() => document.title")

            assert result == "RoleRef Fixture"
        finally:
            context.close()
            browser.close()
