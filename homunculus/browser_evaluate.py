from __future__ import annotations

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from homunculus.role_ref import RoleRef
from homunculus.role_ref_locator import locator_for_role_ref


def evaluate_page(page, fn: str, timeout_ms: int | None = None) -> object:
    """Evaluate a function in the page context."""
    try:
        if timeout_ms is None:
            return page.evaluate(fn)
        return page.evaluate(fn, timeout=timeout_ms)
    except PlaywrightTimeoutError as exc:
        raise TimeoutError("Timed out evaluating page function.") from exc


def evaluate_by_role_ref(
    page,
    role_ref_str: str,
    fn: str,
    timeout_ms: int | None = None,
    state: str | None = None,
) -> object:
    """Wait for an element addressed by a role ref string, then evaluate."""
    role_ref = RoleRef.from_str(role_ref_str)
    locator = locator_for_role_ref(page, role_ref)
    wait_state = state if state is not None else "visible"
    wait_options: dict[str, str | int] = {"state": wait_state}
    if timeout_ms is not None:
        wait_options["timeout"] = timeout_ms
    evaluate_options: dict[str, int] = {}
    if timeout_ms is not None:
        evaluate_options["timeout"] = timeout_ms
    try:
        locator.wait_for(**wait_options)
        if evaluate_options:
            return locator.evaluate(fn, **evaluate_options)
        return locator.evaluate(fn)
    except PlaywrightTimeoutError as exc:
        raise TimeoutError("Timed out evaluating locator function.") from exc


__all__ = ["evaluate_by_role_ref", "evaluate_page"]
