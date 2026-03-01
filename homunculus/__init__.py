"""Homunculus CLI package."""

from homunculus.snapshot_act import (
    snapshot_then_act_by_role_ref,
    snapshot_then_extract_text_by_role_ref,
    snapshot_then_evaluate_by_role_ref,
)
from homunculus.role_snapshot_act import (
    snapshot_then_act_by_ref,
    snapshot_then_drag_by_ref,
    snapshot_then_extract_text_by_ref,
    snapshot_then_evaluate_by_ref,
)

__all__ = [
    "snapshot_then_act_by_ref",
    "snapshot_then_act_by_role_ref",
    "snapshot_then_drag_by_ref",
    "snapshot_then_extract_text_by_ref",
    "snapshot_then_extract_text_by_role_ref",
    "snapshot_then_evaluate_by_ref",
    "snapshot_then_evaluate_by_role_ref",
]
