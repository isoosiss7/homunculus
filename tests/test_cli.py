from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.role_ref import RoleRef


def _ensure_playwright_available() -> None:
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")
        else:
            browser.close()


def test_cli_run_outputs_done() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "homunculus", "run", "say hello"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "DONE" in result.stdout.upper()


def test_cli_snapshot_role_refs() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "snapshot-role-refs",
            str(fixture_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    role_refs = result.stdout.splitlines()
    assert RoleRef(role="button", name="Submit", nth=0).to_str() in role_refs
    assert RoleRef(role="textbox", name="User name", nth=0).to_str() in role_refs


def test_cli_act_by_role_ref_fill() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    role_ref = RoleRef(role="textbox", name="User name", nth=0).to_str()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "act-by-role-ref",
            fixture_path.resolve().as_uri(),
            role_ref,
            "--action",
            "fill",
            "--value",
            "Ada",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0


def test_cli_act_by_role_ref_click_print_title() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    role_ref = RoleRef(role="button", name="Submit", nth=1).to_str()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "act-by-role-ref",
            str(fixture_path),
            role_ref,
            "--action",
            "click",
            "--print-title",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "clicked-1" in result.stdout
