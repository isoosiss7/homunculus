from __future__ import annotations

import json
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


def test_cli_snapshot_role_refs_roles_filter() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "snapshot-role-refs",
            str(fixture_path),
            "--roles",
            "button",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    role_refs = result.stdout.splitlines()
    assert RoleRef(role="button", name="Submit", nth=0).to_str() in role_refs
    assert RoleRef(role="textbox", name="User name", nth=0).to_str() not in role_refs


def test_cli_snapshot_role_refs_json() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "snapshot-role-refs",
            str(fixture_path),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    role_refs = json.loads(result.stdout)
    assert role_refs == sorted(role_refs)
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
            "--timeout-ms",
            "1000",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "clicked-1" in result.stdout


def test_cli_act_by_role_ref_fill_print_title() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    role_ref = RoleRef(role="textbox", name="User name", nth=0).to_str()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "act-by-role-ref",
            str(fixture_path),
            role_ref,
            "--action",
            "fill",
            "--value",
            "Ada",
            "--print-title",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Ada" in result.stdout


def test_cli_act_by_role_ref_press_print_title() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    role_ref = RoleRef(role="textbox", name="User name", nth=0).to_str()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "act-by-role-ref",
            str(fixture_path),
            role_ref,
            "--action",
            "press",
            "--key",
            "Enter",
            "--print-title",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "pressed-enter" in result.stdout


def test_cli_snapshot_act_click_print_title() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    role_ref = RoleRef(role="button", name="Submit", nth=1).to_str()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "snapshot-act",
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


def test_cli_snapshot_act_missing_role_ref() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"
    role_ref = RoleRef(role="button", name="Missing", nth=0).to_str()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "snapshot-act",
            str(fixture_path),
            role_ref,
            "--action",
            "click",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "not found" in result.stderr.lower()


def test_cli_act_click_print_title() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "act",
            str(fixture_path),
            "--role",
            "button",
            "--name",
            "Submit",
            "--nth",
            "1",
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


def test_cli_act_fill_print_title() -> None:
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "role_ref.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "homunculus",
            "act",
            str(fixture_path),
            "--role",
            "textbox",
            "--name",
            "User name",
            "--action",
            "fill",
            "--value",
            "Ada",
            "--print-title",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Ada" in result.stdout
