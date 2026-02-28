"""Helpers for automating Google Maps with Playwright."""

from __future__ import annotations

import re
import time
from typing import Iterable


def open_google_maps(page) -> None:
    """Open Google Maps with consistent load behavior."""
    page.goto("https://www.google.com/maps", wait_until="domcontentloaded")


def search_location(page, query: str) -> None:
    """Search for a location and wait for the results panel to reflect it."""
    _handle_consent_dialog(page)

    search_box = _find_search_box(page)
    search_box.click()
    search_box.fill(query)
    search_box.press("Enter")

    _wait_for_results_panel(page, query)


def _find_search_box(page):
    for role in ("combobox", "textbox"):
        locator = page.get_by_role(role, name=re.compile(r"search", re.I))
        try:
            locator.first.wait_for(state="visible", timeout=5000)
            return locator.first
        except Exception:
            continue
    return page.locator("input#searchboxinput")


def _handle_consent_dialog(page) -> None:
    """Best-effort dismissal of consent dialogs if they appear."""
    for frame in [page, *page.frames]:
        if _try_dismiss_in_frame(frame):
            return


def _try_dismiss_in_frame(frame) -> bool:
    buttons = (
        re.compile(r"accept all", re.I),
        re.compile(r"i agree", re.I),
        re.compile(r"agree", re.I),
        re.compile(r"accept", re.I),
        re.compile(r"reject all", re.I),
        re.compile(r"decline", re.I),
        re.compile(r"no thanks", re.I),
    )
    for name in buttons:
        button = frame.get_by_role("button", name=name).first
        try:
            button.wait_for(state="visible", timeout=1200)
            button.click()
            return True
        except Exception:
            continue
    return False


def _wait_for_results_panel(page, query: str) -> None:
    panel = page.get_by_role("region", name=re.compile(r"results for", re.I))
    try:
        panel.wait_for(state="visible", timeout=15000)
    except Exception:
        return

    tokens = _query_tokens(query)
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            text = panel.inner_text().lower()
        except Exception:
            time.sleep(0.25)
            continue
        if any(token in text for token in tokens):
            return
        time.sleep(0.25)


def _query_tokens(query: str) -> Iterable[str]:
    tokens = [part.strip().lower() for part in re.split(r"[,\s]+", query)]
    return [token for token in tokens if len(token) > 3]
