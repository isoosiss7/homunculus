from __future__ import annotations

import pytest
from pydantic import ValidationError

from homunculus.role_ref import RoleRef


def test_role_ref_normalizes_role_lowercase() -> None:
    role_ref = RoleRef(role="BuTtOn", name="Submit", nth=0)
    assert role_ref.role == "button"
    assert role_ref.to_str().startswith("role:button;")

    parsed = RoleRef.from_str("role:BuTtOn;name:Submit;nth:0")
    assert parsed.role == "button"


def test_role_ref_empty_role_raises() -> None:
    with pytest.raises(ValidationError):
        RoleRef(role="   ", name="Submit", nth=0)


def test_role_ref_empty_name_raises() -> None:
    with pytest.raises(ValidationError):
        RoleRef(role="button", name="   ", nth=0)


def test_role_ref_negative_nth_raises() -> None:
    with pytest.raises(ValidationError):
        RoleRef(role="button", name="Submit", nth=-1)


def test_role_ref_from_str_invalid_nth() -> None:
    with pytest.raises(ValueError, match="Invalid role ref nth"):
        RoleRef.from_str("role:button;name:Submit;nth:abc")


def test_role_ref_from_str_negative_nth() -> None:
    with pytest.raises(ValueError, match="Invalid role ref nth"):
        RoleRef.from_str("role:button;name:Submit;nth:-1")
