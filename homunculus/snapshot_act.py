from __future__ import annotations

from homunculus.browser_act import act_by_role_ref, extract_text_by_role_ref
from homunculus.browser_snapshot import snapshot_role_refs


def snapshot_then_act_by_role_ref(
    page,
    role_ref_str: str,
    action: str,
    value: str | None = None,
    key: str | None = None,
    timeout_ms: int | None = None,
    state: str | None = None,
    slowly: bool | None = None,
    include_roles: set[str] | None = None,
) -> None:
    """Snapshot role refs, validate presence, then perform an action."""
    # For most actions, we validate the target exists in the current snapshot.
    # For action=wait, the element may legitimately be missing (e.g. waiting for
    # a delayed element to appear), so we skip strict snapshot validation.
    if action != "wait":
        role_refs = snapshot_role_refs(page, include_roles=include_roles)
        if role_ref_str not in role_refs:
            raise ValueError(f"Role ref not found in snapshot: {role_ref_str}")

    act_by_role_ref(
        page,
        role_ref_str,
        action,
        value,
        key,
        timeout_ms,
        state,
        slowly,
    )


def snapshot_then_extract_text_by_role_ref(
    page,
    role_ref_str: str,
    include_roles: set[str] | None = None,
    timeout_ms: int | None = None,
    state: str | None = None,
) -> str:
    """Snapshot role refs, then extract visible text.

    We prefer to validate that the role ref exists in the current snapshot, but
    for delayed elements it's reasonable to allow waiting when a timeout was
    provided.
    """
    role_refs = snapshot_role_refs(page, include_roles=include_roles)
    if role_ref_str not in role_refs:
        if timeout_ms is None:
            raise ValueError(f"Role ref not found in snapshot: {role_ref_str}")
        # Allow waiting for elements that appear later.

    return extract_text_by_role_ref(page, role_ref_str, timeout_ms, state)


__all__ = ["snapshot_then_act_by_role_ref", "snapshot_then_extract_text_by_role_ref"]
