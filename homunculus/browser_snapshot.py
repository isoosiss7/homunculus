from __future__ import annotations

from homunculus.role_ref import RoleRef

DEFAULT_INCLUDE_ROLES = {"button", "textbox", "link", "checkbox", "radio", "combobox"}


def snapshot_role_refs(page, include_roles: set[str] | None = None) -> list[str]:
    roles = include_roles or DEFAULT_INCLUDE_ROLES
    snapshot = page.accessibility.snapshot()
    if not snapshot:
        return []

    role_refs: list[str] = []
    counters: dict[tuple[str, str], int] = {}

    def walk(node: dict) -> None:
        role = node.get("role")
        name = node.get("name")
        if role is not None and name is not None and role in roles:
            key = (role, name)
            nth = counters.get(key, 0)
            counters[key] = nth + 1
            role_refs.append(RoleRef(role=role, name=name, nth=nth).to_str())

        for child in node.get("children", []) or []:
            walk(child)

    walk(snapshot)
    return role_refs
