"""General-purpose Playwright wait primitives."""

from __future__ import annotations

import time
from typing import Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

import fnmatch

_VALID_LOAD_STATES = {"load", "domcontentloaded", "networkidle", "commit"}


def wait_for(
    page,
    *,
    selector: Optional[str] = None,
    url: Optional[str] = None,
    load: Optional[str] = None,
    fn: Optional[str] = None,
    timeout_ms: int = 10000,
) -> None:
    """Wait for one or more Playwright conditions with a shared timeout budget.

    This wrapper normalizes Playwright timeouts into Python's built-in
    ``TimeoutError`` so callers can treat all waits consistently.
    """
    if not any([selector, url, load, fn]):
        raise ValueError("At least one wait condition must be provided.")
    if load is not None and load not in _VALID_LOAD_STATES:
        raise ValueError(
            "Invalid load state. Expected one of: "
            + ", ".join(sorted(_VALID_LOAD_STATES))
            + "."
        )

    start = time.monotonic()

    def remaining_timeout() -> float:
        elapsed_ms = (time.monotonic() - start) * 1000
        remaining = timeout_ms - elapsed_ms
        if remaining <= 0:
            raise TimeoutError("Timed out waiting for conditions.")
        return remaining

    try:
        if selector is not None:
            page.wait_for_selector(selector, state="visible", timeout=remaining_timeout())
        if url is not None:
            # Playwright's wait_for_url doesn't consistently treat history.pushState()
            # as a navigation. We implement a small polling loop against page.url
            # so URL waits work for both real navigations and SPA history changes.
            while True:
                if fnmatch.fnmatch(page.url, url):
                    break
                remaining = remaining_timeout()
                page.wait_for_timeout(min(50, remaining))
        if load is not None:
            page.wait_for_load_state(load, timeout=remaining_timeout())
        if fn is not None:
            page.wait_for_function(fn, timeout=remaining_timeout())
    except PlaywrightTimeoutError as exc:
        raise TimeoutError("Timed out waiting for conditions.") from exc
