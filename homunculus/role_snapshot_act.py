from __future__ import annotations

from homunculus.browser_wait import wait_for
from homunculus.role_snapshot import (
    RoleSnapshot,
    act_by_ref,
    drag_by_ref,
    evaluate_by_ref,
    extract_text_by_ref,
    snapshot_role_snapshot,
)


def snapshot_then_act_by_ref(
    page,
    ref: str,
    action: str,
    value: str | None = None,
    key: str | None = None,
    timeout_ms: int | None = None,
    state: str | None = None,
    slowly: bool | None = None,
    modifiers: list[str] | None = None,
    button: str | None = None,
    double_click: bool | None = None,
    include_roles: set[str] | None = None,
    visible_only: bool = True,
) -> RoleSnapshot:
    """Snapshot role refs, validate presence, then perform an action."""
    snapshot = snapshot_role_snapshot(
        page,
        include_roles=include_roles,
        visible_only=visible_only,
    )

    if ref not in snapshot.ref_to_role_ref:
        if action == "wait":
            return snapshot
        raise ValueError(f"Ref not found in snapshot: {ref}")

    act_by_ref(
        page,
        snapshot,
        ref,
        action,
        value,
        key,
        timeout_ms,
        state,
        slowly,
        modifiers,
        button,
        double_click,
    )
    return snapshot


def snapshot_then_extract_text_by_ref(
    page,
    ref: str,
    include_roles: set[str] | None = None,
    visible_only: bool = True,
    timeout_ms: int | None = None,
    state: str | None = None,
) -> tuple[RoleSnapshot, str]:
    """Snapshot role refs, then extract visible text."""
    snapshot = snapshot_role_snapshot(
        page,
        include_roles=include_roles,
        visible_only=visible_only,
    )
    if ref not in snapshot.ref_to_role_ref:
        if timeout_ms is None:
            raise ValueError(f"Ref not found in snapshot: {ref}")
        return snapshot, ""

    text = extract_text_by_ref(page, snapshot, ref, timeout_ms, state)
    return snapshot, text


def snapshot_then_drag_by_ref(
    page,
    start_ref: str,
    end_ref: str,
    timeout_ms: int | None = None,
    include_roles: set[str] | None = None,
    visible_only: bool = True,
) -> RoleSnapshot:
    """Snapshot role refs, validate presence, then drag between refs."""
    snapshot = snapshot_role_snapshot(
        page,
        include_roles=include_roles,
        visible_only=visible_only,
    )
    if start_ref not in snapshot.ref_to_role_ref:
        raise ValueError(f"Ref not found in snapshot: {start_ref}")
    if end_ref not in snapshot.ref_to_role_ref:
        raise ValueError(f"Ref not found in snapshot: {end_ref}")

    drag_by_ref(page, snapshot, start_ref, end_ref, timeout_ms)
    return snapshot


def snapshot_then_evaluate_by_ref(
    page,
    ref: str,
    fn: str,
    include_roles: set[str] | None = None,
    visible_only: bool = True,
    timeout_ms: int | None = None,
    state: str | None = None,
) -> tuple[RoleSnapshot, object]:
    """Snapshot role refs, then evaluate against the referenced element."""
    snapshot = snapshot_role_snapshot(
        page,
        include_roles=include_roles,
        visible_only=visible_only,
    )
    if ref not in snapshot.ref_to_role_ref:
        if timeout_ms is None:
            raise ValueError(f"Ref not found in snapshot: {ref}")
        return snapshot, None

    result = evaluate_by_ref(page, snapshot, ref, fn, timeout_ms, state)
    return snapshot, result


def snapshot_then_wait(
    page,
    *,
    selector: str | None = None,
    url: str | None = None,
    load: str | None = None,
    fn: str | None = None,
    text: str | None = None,
    text_gone: str | None = None,
    timeout_ms: int = 10000,
    include_roles: set[str] | None = None,
    visible_only: bool = True,
) -> RoleSnapshot:
    """Snapshot role refs, then wait for general page conditions."""
    snapshot = snapshot_role_snapshot(
        page,
        include_roles=include_roles,
        visible_only=visible_only,
    )
    wait_for(
        page,
        selector=selector,
        url=url,
        load=load,
        fn=fn,
        text=text,
        text_gone=text_gone,
        timeout_ms=timeout_ms,
    )
    return snapshot


__all__ = [
    "snapshot_then_act_by_ref",
    "snapshot_then_drag_by_ref",
    "snapshot_then_extract_text_by_ref",
    "snapshot_then_evaluate_by_ref",
    "snapshot_then_wait",
]
