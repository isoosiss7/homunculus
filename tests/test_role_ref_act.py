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
                match="Unsupported action 'focus'. Supported actions: click, fill, press, hover.",
            ):
                act_by_role_ref(page, role_ref_str, action="focus")
        finally:
            context.close()
            browser.close()
