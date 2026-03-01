from __future__ import annotations

from homunculus.role_ref import RoleRef
from homunculus.web import extract_text


def act_by_role_ref(
    page,
    role_ref_str: str,
    action: str,
    value: str | None = None,
    key: str | None = None,
    timeout_ms: int | None = None,
    state: str | None = None,
    slowly: bool | None = None,
    modifiers: list[str] | None = None,
    button: str | None = None,
    double_click: bool | None = None,
) -> None:
    """Perform an action on an element addressed by a role ref string."""
    role_ref = RoleRef.from_str(role_ref_str)
    locator = page.get_by_role(role_ref.role, name=role_ref.name).nth(role_ref.nth)
    action_options: dict[str, object] = {}
    if timeout_ms is not None:
        action_options["timeout"] = timeout_ms

    if action == "click":
        click_options = dict(action_options)
        if modifiers:
            click_options["modifiers"] = modifiers
        if button:
            click_options["button"] = button
        if double_click:
            locator.dblclick(**click_options)
        else:
            locator.click(**click_options)
        return

    if action == "fill":
        if value is None:
            raise ValueError("action 'fill' requires a value to be provided")
        locator.fill(value, **action_options)
        return

    if action == "select":
        if value is None:
            raise ValueError("action 'select' requires a value to be provided")
        try:
            locator.select_option(label=value, **action_options)
        except Exception:
            locator.select_option(value=value, **action_options)
        return

    if action == "type":
        if value is None:
            raise ValueError("action 'type' requires a value to be provided")
        type_options = dict(action_options)
        if slowly:
            type_options["delay"] = 50
        locator.type(value, **type_options)
        return

    if action == "press":
        if key is None:
            raise ValueError("action 'press' requires a key to be provided")
        locator.press(key, **action_options)
        return

    if action == "hover":
        locator.hover(**action_options)
        return

    if action == "wait":
        wait_state = state if state is not None else "visible"
        wait_options: dict[str, str | int] = {"state": wait_state}
        if timeout_ms is not None:
            wait_options["timeout"] = timeout_ms
        locator.wait_for(**wait_options)
        return

    raise ValueError(
        "Unsupported action"
        f" '{action}'. Supported actions: click, fill, select, type, press, hover, wait."
    )


def extract_text_by_role_ref(
    page,
    role_ref_str: str,
    timeout_ms: int | None = None,
    state: str | None = None,
) -> str:
    """Wait for an element addressed by a role ref string, then extract text."""
    role_ref = RoleRef.from_str(role_ref_str)
    locator = page.get_by_role(role_ref.role, name=role_ref.name).nth(role_ref.nth)
    wait_state = state if state is not None else "visible"
    wait_options: dict[str, str | int] = {"state": wait_state}
    if timeout_ms is not None:
        wait_options["timeout"] = timeout_ms
    locator.wait_for(**wait_options)
    return extract_text(locator)


def act_click_by_role_ref(page, role_ref_str: str) -> None:
    """Click the element referenced by a role ref string."""
    act_by_role_ref(page, role_ref_str, "click")


def act_fill_by_role_ref(page, role_ref_str: str, value: str) -> None:
    """Fill the element referenced by a role ref string."""
    act_by_role_ref(page, role_ref_str, "fill", value)
