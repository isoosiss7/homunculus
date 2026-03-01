from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


def _ensure_playwright_available() -> None:
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")
        else:
            browser.close()


def test_cli_wait_for_selector_delayed_element() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "browser_wait.html"

    start = time.monotonic()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "wait",
            fixture_path.resolve().as_uri(),
            "--selector",
            "#late",
            "--timeout-ms",
            "1000",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed_ms = (time.monotonic() - start) * 1000

    assert result.returncode == 0
    assert elapsed_ms >= 40


def test_cli_wait_for_text_delayed() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "browser_wait.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "wait",
            fixture_path.resolve().as_uri(),
            "--text",
            "Hello from later text",
            "--timeout-ms",
            "1000",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0


def test_cli_wait_requires_condition() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "browser_wait.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "wait",
            fixture_path.resolve().as_uri(),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode in {1, 2}
    assert "at least one wait condition must be provided" in result.stderr.lower()
