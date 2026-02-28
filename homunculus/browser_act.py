from __future__ import annotations

from homunculus.role_ref import RoleRef


def act_by_role_ref(
    page,
    role_ref_str: str,
    action: str,
    value: str | None = None,
) -> None:
    """Perform an action on an element addressed by a role ref string."""
    role_ref = RoleRef.from_str(role_ref_str)
    locator = page.get_by_role(role_ref.role, name=role_ref.name).nth(role_ref.nth)

    if action == "click":
        locator.click()
        return

    if action == "fill":
        if value is None:
            raise ValueError("action 'fill' requires a value to be provided")
        locator.fill(value)
        return

    raise ValueError(f"Unsupported action '{action}'. Supported actions: click, fill.")


def act_click_by_role_ref(page, role_ref_str: str) -> None:
    """Click the element referenced by a role ref string."""
    act_by_role_ref(page, role_ref_str, "click")


def act_fill_by_role_ref(page, role_ref_str: str, value: str) -> None:
    """Fill the element referenced by a role ref string."""
    act_by_role_ref(page, role_ref_str, "fill", value)
