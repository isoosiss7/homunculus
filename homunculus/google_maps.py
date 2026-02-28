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


def search_places_nearby(page, base_location: str, place_query: str) -> None:
    """Search for places near a base location and wait for the results panel."""
    search_location(page, f"{place_query} near {base_location}")


def get_top_place_results(page, limit: int = 2) -> list[str]:
    """Return the visible names of the top N place results from the results panel."""
    if limit <= 0:
        return []

    panel = page.get_by_role("region", name=re.compile(r"results for", re.I))
    try:
        panel.wait_for(state="visible", timeout=15000)
    except Exception as exc:
        raise ValueError("Results panel not found or not visible on Google Maps.") from exc

    items = _locate_results_items(panel)
    names: list[str] = []
    seen = set()
    try:
        count = items.count()
    except Exception as exc:
        raise ValueError("Unable to read place results from Google Maps.") from exc

    for index in range(count):
        item = items.nth(index)
        try:
            if not item.is_visible():
                continue
        except Exception:
            continue
        name = _extract_place_name(item)
        if not name:
            continue
        if _is_sponsored_name(name) or _is_sponsored_text(item):
            continue
        normalized = name.strip()
        if not normalized or normalized in seen:
            continue
        names.append(normalized)
        seen.add(normalized)
        if len(names) >= limit:
            break

    if len(names) < limit:
        raise ValueError(
            f"Only found {len(names)} visible place results; expected at least {limit}."
        )
    return names


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


def _locate_results_items(panel):
    selectors = [
        panel.get_by_role("article"),
        panel.locator("div[role='article']"),
        panel.locator("[role='feed'] [role='article']"),
    ]
    for locator in selectors:
        try:
            if locator.first.is_visible():
                return locator
        except Exception:
            continue
    return panel.locator("div[role='article']")


def _extract_place_name(item) -> str:
    candidates: list[str] = []
    try:
        aria = item.get_attribute("aria-label")
        if aria:
            candidates.append(aria)
    except Exception:
        pass

    locator_candidates = [
        item.get_by_role("heading"),
        item.locator("div[role='heading']"),
        item.locator("span[role='heading']"),
        item.locator("a[href*='/maps/place']"),
        item.locator("a[aria-label]"),
    ]
    for locator in locator_candidates:
        try:
            target = locator.first
            if target.is_visible():
                text = target.inner_text().strip()
                if text:
                    candidates.append(text)
        except Exception:
            continue

    if not candidates:
        try:
            text = item.inner_text().strip()
        except Exception:
            text = ""
        if text:
            candidates.append(text.splitlines()[0].strip())

    for candidate in candidates:
        cleaned = candidate.strip()
        if cleaned and len(cleaned) <= 120:
            return cleaned
    return ""


def _is_sponsored_name(name: str) -> bool:
    lowered = name.lower()
    return "sponsored" in lowered or lowered.startswith("ad ")


def _is_sponsored_text(item) -> bool:
    try:
        text = item.inner_text().lower()
    except Exception:
        return False
    return bool(re.search(r"\bsponsored\b|\bad\b", text))
