"""Website-agnostic Playwright helpers."""

from __future__ import annotations

import re
import time
from typing import Iterable, Sequence

_DEFAULT_CONSENT_BUTTONS: Sequence[re.Pattern[str]] = (
    re.compile(r"accept all", re.I),
    re.compile(r"i agree", re.I),
    re.compile(r"agree", re.I),
    re.compile(r"accept", re.I),
    re.compile(r"reject all", re.I),
    re.compile(r"decline", re.I),
    re.compile(r"no thanks", re.I),
)


def open_url(page, url: str, *, wait_until: str = "domcontentloaded") -> None:
    """Navigate to a URL and best-effort dismiss common consent dialogs."""
    page.goto(url, wait_until=wait_until)
    dismiss_consent_dialogs(page)


def dismiss_consent_dialogs(
    page,
    *,
    button_patterns: Sequence[re.Pattern[str]] | None = None,
    timeout_ms: int = 1200,
) -> bool:
    """Best-effort dismissal of consent dialogs if they appear."""
    patterns = button_patterns or _DEFAULT_CONSENT_BUTTONS
    frames = [page]
    try:
        frames.extend(page.frames)
    except Exception:
        pass
    for frame in frames:
        if _try_dismiss_in_frame(frame, patterns, timeout_ms):
            return True
    return False


def _try_dismiss_in_frame(
    frame,
    patterns: Iterable[re.Pattern[str]],
    timeout_ms: int,
) -> bool:
    for name in patterns:
        try:
            button = frame.get_by_role("button", name=name).first
        except Exception:
            continue
        try:
            button.wait_for(state="visible", timeout=timeout_ms)
            button.click()
            return True
        except Exception:
            continue
    return False


def find_search_box(page):
    """Return the best-effort locator for a generic search box."""
    for role in ("combobox", "textbox"):
        locator = page.get_by_role(role, name=re.compile(r"search", re.I))
        try:
            locator.first.wait_for(state="visible", timeout=5000)
            return locator.first
        except Exception:
            continue

    selectors = [
        "input[type='search']",
        "input[aria-label*='search' i]",
        "input[placeholder*='search' i]",
        "input[name*='search' i]",
        "input[title*='search' i]",
    ]
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=2000)
            return locator
        except Exception:
            continue
    return page.locator(selectors[0]).first


def wait_for_search_box(page, timeout_ms: int = 8000) -> bool:
    """Wait until a search box is visible and enabled."""
    deadline = time.time() + (timeout_ms / 1000)
    locators = _search_box_locators(page)

    while True:
        remaining_ms = int((deadline - time.time()) * 1000)
        if remaining_ms <= 0:
            return False
        for locator in locators:
            target = locator.first
            try:
                target.wait_for(state="visible", timeout=min(1000, remaining_ms))
                try:
                    if target.is_enabled():
                        return True
                except Exception:
                    return True
            except Exception:
                continue
        if remaining_ms > 200:
            time.sleep(0.05)


def _search_box_locators(page):
    return [
        page.get_by_role("combobox", name=re.compile(r"search", re.I)),
        page.get_by_role("textbox", name=re.compile(r"search", re.I)),
        page.locator("input[type='search']"),
        page.locator("input[aria-label*='search' i]"),
        page.locator("input[placeholder*='search' i]"),
        page.locator("input[name*='search' i]"),
        page.locator("input[title*='search' i]"),
    ]


def extract_text(locator) -> str:
    """Return best-effort visible text from a locator."""
    try:
        return locator.inner_text().strip()
    except Exception:
        pass
    try:
        return (locator.text_content() or "").strip()
    except Exception:
        return ""
