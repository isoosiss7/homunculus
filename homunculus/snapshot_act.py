from __future__ import annotations

from homunculus.browser_act import act_by_role_ref
from homunculus.browser_snapshot import snapshot_role_refs


def snapshot_then_act_by_role_ref(
    page,
    role_ref_str: str,
    action: str,
    value: str | None = None,
    key: str | None = None,
    timeout_ms: int | None = None,
    state: str | None = None,
    include_roles: set[str] | None = None,
) -> None:
    """Snapshot role refs, validate presence, then perform an action."""
    role_refs = snapshot_role_refs(page, include_roles=include_roles)
    if role_ref_str not in role_refs:
        raise ValueError(f"Role ref not found in snapshot: {role_ref_str}")

    act_by_role_ref(page, role_ref_str, action, value, key, timeout_ms, state)


__all__ = ["snapshot_then_act_by_role_ref"]
