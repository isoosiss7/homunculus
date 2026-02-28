"""Helpers for automating Google Maps with Playwright."""

from __future__ import annotations

import re
import time
from typing import Iterable, Sequence


_SEARCH_BOX_TIMEOUT_MS = 8000


def open_google_maps(page) -> None:
    """Open Google Maps with consistent load behavior."""
    page.goto("https://www.google.com/maps", wait_until="domcontentloaded")
    _handle_consent_dialog(page)

    if not _wait_for_search_box(page, timeout_ms=_SEARCH_BOX_TIMEOUT_MS):
        page.reload(wait_until="domcontentloaded")
        _handle_consent_dialog(page)
        _wait_for_search_box(page, timeout_ms=_SEARCH_BOX_TIMEOUT_MS)


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


def locate_results_panel(page):
    """Return the best locator for the results panel in Google Maps."""
    candidates = [
        page.get_by_role("region", name=re.compile(r"results for", re.I)),
        page.get_by_role("region", name=re.compile(r"explore this area", re.I)),
        page.get_by_role("region", name=re.compile(r"available filters", re.I)),
    ]
    for locator in candidates:
        target = locator.first
        try:
            target.wait_for(state="visible", timeout=15000)
            return target
        except Exception:
            continue

    fallback = page.locator("[role=main]").first
    try:
        fallback.wait_for(state="visible", timeout=5000)
    except Exception:
        pass
    return fallback


def get_top_place_results(page, limit: int = 2) -> list[str]:
    """Return the visible names of the top N place results from the results panel."""
    if limit <= 0:
        return []

    panel = locate_results_panel(page)
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


def _wait_for_search_box(page, timeout_ms: int) -> bool:
    deadline = time.time() + (timeout_ms / 1000)
    locators = [
        page.get_by_role("combobox", name=re.compile(r"search", re.I)),
        page.get_by_role("textbox", name=re.compile(r"search", re.I)),
        page.locator("input#searchboxinput"),
    ]

    while True:
        remaining_ms = int((deadline - time.time()) * 1000)
        if remaining_ms <= 0:
            return False
        for locator in locators:
            target = locator.first
            try:
                target.wait_for(state="visible", timeout=min(1000, remaining_ms))
                if target.is_enabled():
                    return True
            except Exception:
                continue
        if remaining_ms > 200:
            time.sleep(0.05)


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
    panel = locate_results_panel(page)
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


def parse_eta(text: str) -> str | None:
    """Parse a driving ETA string from Google Maps directions UI text."""
    if not text:
        return None

    hour_min_re, mins_only_re = _eta_regexes()

    match = hour_min_re.search(text)
    if match:
        return _format_eta(match.group("hours"), match.group("mins"))

    match = mins_only_re.search(text)
    if match:
        return _format_eta(None, match.group("mins"))

    return None


def find_etas(text: str) -> list[str]:
    """Return all normalized ETA strings found in text."""
    if not text:
        return []

    hour_min_re, mins_only_re = _eta_regexes()
    spans: list[tuple[int, int]] = []
    results: list[str] = []

    for match in hour_min_re.finditer(text):
        results.append(_format_eta(match.group("hours"), match.group("mins")))
        spans.append(match.span())

    for match in mins_only_re.finditer(text):
        if _span_overlaps(match.span(), spans):
            continue
        results.append(_format_eta(None, match.group("mins")))

    seen: set[str] = set()
    deduped = []
    for eta in results:
        if eta not in seen:
            seen.add(eta)
            deduped.append(eta)
    return deduped


def eta_to_minutes(eta: str) -> int | None:
    """Convert a normalized ETA string like '1 hr 5 min' to total minutes."""
    if not eta:
        return None

    hour_min_re, mins_only_re = _eta_regexes()
    match = hour_min_re.search(eta)
    if match:
        hours = int(match.group("hours"))
        mins_group = match.group("mins")
        mins = int(mins_group) if mins_group else 0
        return hours * 60 + mins

    match = mins_only_re.search(eta)
    if match:
        return int(match.group("mins"))

    return None


def select_shortest_eta(texts: Iterable[str]) -> str | None:
    """Pick the shortest ETA from a collection of direction route texts."""
    best_eta: str | None = None
    best_minutes: int | None = None
    for text in texts:
        for eta in find_etas(text):
            minutes = eta_to_minutes(eta)
            if minutes is None:
                continue
            if best_minutes is None or minutes < best_minutes:
                best_minutes = minutes
                best_eta = eta
    return best_eta


def open_directions_for_current_place(page) -> None:
    """Click the Directions button for the current place and wait briefly."""
    directions_button = page.get_by_role("button", name=re.compile(r"directions", re.I)).first
    try:
        directions_button.wait_for(state="visible", timeout=5000)
        directions_button.click()
    except Exception:
        return

    route_panel = page.get_by_role("region", name=re.compile(r"directions", re.I))
    try:
        route_panel.first.wait_for(state="visible", timeout=5000)
    except Exception:
        return


def get_driving_eta(page, origin: str, destination_place_name: str) -> str:
    """Return the shortest driving ETA between origin and destination on Google Maps."""
    if not origin or not destination_place_name:
        raise ValueError("Origin and destination are required to fetch driving ETA.")

    _handle_consent_dialog(page)

    if not _is_directions_button_visible(page):
        search_location(page, destination_place_name)

    if not _is_directions_button_visible(page):
        _open_first_place_result(page)

    open_directions_for_current_place(page)
    _ensure_origin_filled(page, origin)
    _select_driving_mode(page)

    eta = _wait_for_shortest_eta(page, timeout=25000)
    if not eta:
        raise ValueError("Unable to find a driving ETA on Google Maps.")
    return eta


def _eta_regexes() -> tuple[re.Pattern, re.Pattern]:
    hours_pattern = r"(?:hr|hrs|hour|hours|h)"
    mins_pattern = r"(?:min|mins|minute|minutes)"
    hour_min_re = re.compile(
        rf"(?P<hours>\d+)\s*{hours_pattern}\b(?:\s*(?P<mins>\d+)\s*{mins_pattern}\b)?",
        re.IGNORECASE,
    )
    mins_only_re = re.compile(
        rf"(?P<mins>\d+)\s*{mins_pattern}\b",
        re.IGNORECASE,
    )
    return hour_min_re, mins_only_re


def _format_eta(hours: str | None, mins: str | None) -> str:
    if hours:
        hours_value = int(hours)
        mins_value = int(mins) if mins else 0
        if mins_value:
            return f"{hours_value} hr {mins_value} min"
        return f"{hours_value} hr"
    mins_value = int(mins) if mins else 0
    return f"{mins_value} min"


def _span_overlaps(span: tuple[int, int], spans: Sequence[tuple[int, int]]) -> bool:
    start, end = span
    for existing_start, existing_end in spans:
        if start < existing_end and end > existing_start:
            return True
    return False


def _is_directions_button_visible(page) -> bool:
    button = page.get_by_role("button", name=re.compile(r"directions", re.I)).first
    try:
        return button.is_visible()
    except Exception:
        return False


def _open_first_place_result(page) -> None:
    panel = locate_results_panel(page)
    try:
        panel.wait_for(state="visible", timeout=10000)
    except Exception:
        return

    items = _locate_results_items(panel)
    try:
        count = items.count()
    except Exception:
        return

    for index in range(count):
        item = items.nth(index)
        try:
            if not item.is_visible():
                continue
        except Exception:
            continue
        try:
            link = item.get_by_role("link").first
            if link.is_visible():
                link.click()
                return
        except Exception:
            pass
        try:
            item.click()
            return
        except Exception:
            continue


def _ensure_origin_filled(page, origin: str) -> None:
    scope = _directions_scope(page)
    patterns = [
        re.compile(r"starting point", re.I),
        re.compile(r"choose starting point", re.I),
        re.compile(r"from", re.I),
        re.compile(r"your location", re.I),
    ]
    locator = None
    for role in ("combobox", "textbox"):
        for pattern in patterns:
            candidate = scope.get_by_role(role, name=pattern).first
            try:
                candidate.wait_for(state="visible", timeout=5000)
                locator = candidate
                break
            except Exception:
                continue
        if locator:
            break

    if locator is None:
        locator = _find_search_box(page)

    _focus_and_clear(locator)
    locator.fill(origin)
    time.sleep(0.2)

    if not _try_click_autocomplete_option(scope) and not _try_click_autocomplete_option(page):
        _best_effort_press(locator, "ArrowDown")
        _best_effort_press(locator, "Enter")
    time.sleep(0.4)


def _focus_and_clear(locator) -> None:
    try:
        locator.click()
    except Exception:
        return

    _best_effort_press(locator, "Control+A")
    _best_effort_press(locator, "Meta+A")
    _best_effort_press(locator, "Backspace")
    _best_effort_press(locator, "Delete")
    try:
        locator.fill("")
    except Exception:
        pass


def _best_effort_press(locator, key: str) -> None:
    try:
        locator.press(key)
    except Exception:
        return


def _try_click_autocomplete_option(scope) -> bool:
    listbox = scope.get_by_role("listbox").first
    try:
        listbox.wait_for(state="visible", timeout=600)
    except Exception:
        return False

    option = listbox.get_by_role("option").first
    try:
        option.wait_for(state="visible", timeout=600)
        option.click()
        return True
    except Exception:
        return False


def _select_driving_mode(page) -> None:
    scope = _directions_scope(page)
    patterns = [
        re.compile(r"driving", re.I),
        re.compile(r"car", re.I),
    ]
    for role in ("button", "tab"):
        for pattern in patterns:
            button = scope.get_by_role(role, name=pattern).first
            try:
                button.wait_for(state="visible", timeout=3000)
                button.click()
                return
            except Exception:
                continue


def _wait_for_shortest_eta(page, timeout: int = 20000) -> str | None:
    deadline = time.time() + (timeout / 1000)
    scope = _directions_scope(page)
    while time.time() < deadline:
        texts = _collect_route_texts(scope)
        eta = select_shortest_eta(texts)
        if eta:
            return eta
        time.sleep(0.25)
    return None


def _directions_scope(page):
    panel = page.get_by_role("region", name=re.compile(r"directions", re.I)).first
    try:
        panel.wait_for(state="visible", timeout=2000)
        return panel
    except Exception:
        return page


def _collect_route_texts(scope) -> list[str]:
    locators = [
        scope.get_by_role("listitem"),
        scope.get_by_role("article"),
        scope.locator("[role='listitem']"),
        scope.locator("[role='article']"),
    ]
    texts: list[str] = []
    for locator in locators:
        try:
            count = locator.count()
        except Exception:
            continue
        for index in range(count):
            item = locator.nth(index)
            try:
                if not item.is_visible():
                    continue
                text = item.inner_text().strip()
            except Exception:
                continue
            if text:
                texts.append(text)
        if texts:
            return texts
    try:
        text = scope.inner_text().strip()
    except Exception:
        return []
    return [text] if text else []
