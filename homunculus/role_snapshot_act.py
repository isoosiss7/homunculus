from __future__ import annotations

from homunculus.role_snapshot import (
    RoleSnapshot,
    act_by_ref,
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


__all__ = ["snapshot_then_act_by_ref", "snapshot_then_extract_text_by_ref"]
