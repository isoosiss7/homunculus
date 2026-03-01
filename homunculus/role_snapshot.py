from __future__ import annotations

from dataclasses import asdict, dataclass

from homunculus.browser_act import act_by_role_ref, extract_text_by_role_ref
from homunculus.browser_evaluate import evaluate_by_role_ref
from homunculus.browser_snapshot import snapshot_role_refs
from homunculus.role_ref import RoleRef


@dataclass(frozen=True)
class RoleSnapshotItem:
    ref: str
    role_ref: str
    role: str
    name: str
    nth: int


@dataclass(frozen=True)
class RoleSnapshot:
    url: str
    title: str
    items: list[RoleSnapshotItem]
    ref_to_role_ref: dict[str, str]
    stats: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def snapshot_role_snapshot(
    page,
    include_roles: set[str] | None = None,
    visible_only: bool = True,
) -> RoleSnapshot:
    role_refs = snapshot_role_refs(
        page,
        include_roles=include_roles,
        visible_only=visible_only,
    )
    parsed: list[tuple[str, str, int, str]] = []
    for role_ref_str in role_refs:
        role_ref = RoleRef.from_str(role_ref_str)
        parsed.append((role_ref.role, role_ref.name, role_ref.nth, role_ref_str))

    parsed.sort(key=lambda entry: (entry[0], entry[1], entry[2]))
    items: list[RoleSnapshotItem] = []
    ref_to_role_ref: dict[str, str] = {}
    for index, (role, name, nth, role_ref_str) in enumerate(parsed, start=1):
        ref = f"e{index}"
        items.append(
            RoleSnapshotItem(
                ref=ref,
                role_ref=role_ref_str,
                role=role,
                name=name,
                nth=nth,
            )
        )
        ref_to_role_ref[ref] = role_ref_str

    return RoleSnapshot(
        url=page.url,
        title=page.title(),
        items=items,
        ref_to_role_ref=ref_to_role_ref,
        stats={"count": len(items)},
    )


def act_by_ref(
    page,
    snapshot: RoleSnapshot,
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
) -> None:
    if ref not in snapshot.ref_to_role_ref:
        raise ValueError(f"Ref not found in snapshot: {ref}")
    role_ref = snapshot.ref_to_role_ref[ref]
    act_by_role_ref(
        page,
        role_ref,
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


def extract_text_by_ref(
    page,
    snapshot: RoleSnapshot,
    ref: str,
    timeout_ms: int | None = None,
    state: str | None = None,
) -> str:
    if ref not in snapshot.ref_to_role_ref:
        raise ValueError(f"Ref not found in snapshot: {ref}")
    role_ref = snapshot.ref_to_role_ref[ref]
    return extract_text_by_role_ref(page, role_ref, timeout_ms, state)


def evaluate_by_ref(
    page,
    snapshot: RoleSnapshot,
    ref: str,
    fn: str,
    timeout_ms: int | None = None,
    state: str | None = None,
) -> object:
    if ref not in snapshot.ref_to_role_ref:
        raise ValueError(f"Ref not found in snapshot: {ref}")
    role_ref = snapshot.ref_to_role_ref[ref]
    return evaluate_by_role_ref(page, role_ref, fn, timeout_ms, state)


__all__ = [
    "RoleSnapshot",
    "RoleSnapshotItem",
    "act_by_ref",
    "extract_text_by_ref",
    "evaluate_by_ref",
    "snapshot_role_snapshot",
]
