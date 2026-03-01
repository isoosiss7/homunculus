from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.browser_act import (
    act_by_role_ref,
    act_click_by_role_ref,
    act_fill_by_role_ref,
)
from homunculus.role_ref import RoleRef


def test_act_click_by_role_ref_nth() -> None:
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
            act_click_by_role_ref(page, role_ref_str)

            assert page.text_content("#result") == "clicked-1"
        finally:
            context.close()
            browser.close()


def test_act_fill_by_role_ref_textbox() -> None:
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

            role_ref_str = RoleRef(role="textbox", name="User name", nth=0).to_str()
            act_fill_by_role_ref(page, role_ref_str, "Ada")

            assert page.text_content("#result") == "Ada"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_click() -> None:
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
            act_by_role_ref(page, role_ref_str, action="click")

            assert page.text_content("#result") == "clicked-1"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_click_with_modifiers() -> None:
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

            role_ref_str = RoleRef(role="button", name="Modifier target", nth=0).to_str()
            act_by_role_ref(
                page,
                role_ref_str,
                action="click",
                modifiers=["Shift", "Alt"],
            )

            assert page.text_content("#result") == "modifiers:shift+alt"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_double_click() -> None:
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

            role_ref_str = RoleRef(role="button", name="Double target", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="click", double_click=True)

            assert page.text_content("#result") == "double-clicked"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_fill() -> None:
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

            role_ref_str = RoleRef(role="textbox", name="User name", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="fill", value="Ada")

            assert page.text_content("#result") == "Ada"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_select_by_label() -> None:
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

            role_ref_str = RoleRef(role="combobox", name="Assistant", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="select", value="Ada Lovelace")

            assert page.text_content("#result") == "ada"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_select_by_value() -> None:
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

            role_ref_str = RoleRef(role="combobox", name="Assistant", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="select", value="grace")

            assert page.text_content("#result") == "grace"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_type() -> None:
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

            role_ref_str = RoleRef(role="textbox", name="Typing target", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="type", value="Grace")

            assert page.text_content("#result") == "Grace"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_press() -> None:
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

            role_ref_str = RoleRef(role="textbox", name="User name", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="press", key="Enter")

            assert page.text_content("#result") == "pressed-enter"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_hover() -> None:
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

            role_ref_str = RoleRef(role="button", name="Hover target", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="hover")

            assert page.text_content("#result") == "hovered"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_check_uncheck() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "checkbox.html"
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

            role_ref_str = RoleRef(role="checkbox", name="Enable alerts", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="check")

            assert page.text_content("#result") == "checked"

            act_by_role_ref(page, role_ref_str, action="uncheck")

            assert page.text_content("#result") == "unchecked"
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_wait_visible() -> None:
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

            role_ref_str = RoleRef(role="button", name="Delayed button", nth=0).to_str()
            act_by_role_ref(page, role_ref_str, action="wait", timeout_ms=2000)

            assert page.is_visible("#delayed")
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_scroll_into_view() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "scroll_into_view.html"
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

            role_ref_str = RoleRef(role="button", name="Scroll target", nth=0).to_str()
            before = page.evaluate(
                "() => {"
                "  const el = document.getElementById('target');"
                "  const rect = el.getBoundingClientRect();"
                "  return { top: rect.top, bottom: rect.bottom, innerHeight: window.innerHeight };"
                "}"
            )

            assert before["top"] > before["innerHeight"]

            act_by_role_ref(page, role_ref_str, action="scrollintoview")

            after = page.evaluate(
                "() => {"
                "  const el = document.getElementById('target');"
                "  const rect = el.getBoundingClientRect();"
                "  return { top: rect.top, bottom: rect.bottom, innerHeight: window.innerHeight };"
                "}"
            )

            assert after["top"] <= after["innerHeight"]
            assert after["bottom"] >= 0
        finally:
            context.close()
            browser.close()


def test_act_by_role_ref_unsupported_action() -> None:
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
            with pytest.raises(
                ValueError,
                match=(
                    "Unsupported action 'focus'. Supported actions: click, fill, "
                    "select, type, press, hover, scrollintoview, check, uncheck, wait."
                ),
            ):
                act_by_role_ref(page, role_ref_str, action="focus")
        finally:
            context.close()
            browser.close()
