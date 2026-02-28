from __future__ import annotations

from homunculus.role_ref import RoleRef


def act_click_by_role_ref(page, role_ref_str: str) -> None:
    role_ref = RoleRef.from_str(role_ref_str)
    page.get_by_role(role_ref.role, name=role_ref.name).nth(role_ref.nth).click()


def act_fill_by_role_ref(page, role_ref_str: str, value: str) -> None:
    role_ref = RoleRef.from_str(role_ref_str)
    page.get_by_role(role_ref.role, name=role_ref.name).nth(role_ref.nth).fill(value)
