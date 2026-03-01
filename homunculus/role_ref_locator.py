from __future__ import annotations

from homunculus.role_ref import RoleRef


def locator_for_role_ref(scope, role_ref: RoleRef):
    """Return a locator for a role ref, preferring exact matches."""
    locator = scope.get_by_role(role_ref.role, name=role_ref.name, exact=True)
    if locator.count() == 0:
        locator = scope.get_by_role(role_ref.role, name=role_ref.name, exact=False)
    return locator.nth(role_ref.nth)


__all__ = ["locator_for_role_ref"]
