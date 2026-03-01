from __future__ import annotations

from homunculus.role_snapshot import RoleSnapshot, snapshot_role_snapshot
from homunculus.role_snapshot_act import (
    snapshot_then_act_by_ref,
    snapshot_then_drag_by_ref,
    snapshot_then_evaluate_by_ref,
    snapshot_then_extract_text_by_ref,
    snapshot_then_wait,
)


class BrowserPrimitives:
    def __init__(self, page) -> None:
        self._page = page

    def snapshot(
        self,
        include_roles: set[str] | None = None,
        visible_only: bool = True,
        selector: str | None = None,
    ) -> RoleSnapshot:
        return snapshot_role_snapshot(
            self._page,
            include_roles=include_roles,
            visible_only=visible_only,
            selector=selector,
        )

    def act(
        self,
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
        include_roles: set[str] | None = None,
        visible_only: bool = True,
        selector: str | None = None,
    ) -> RoleSnapshot:
        return snapshot_then_act_by_ref(
            self._page,
            ref,
            action,
            value=value,
            key=key,
            timeout_ms=timeout_ms,
            state=state,
            slowly=slowly,
            modifiers=modifiers,
            button=button,
            double_click=double_click,
            include_roles=include_roles,
            visible_only=visible_only,
            selector=selector,
        )

    def drag(
        self,
        start_ref: str,
        end_ref: str,
        timeout_ms: int | None = None,
        include_roles: set[str] | None = None,
        visible_only: bool = True,
        selector: str | None = None,
    ) -> RoleSnapshot:
        return snapshot_then_drag_by_ref(
            self._page,
            start_ref,
            end_ref,
            timeout_ms=timeout_ms,
            include_roles=include_roles,
            visible_only=visible_only,
            selector=selector,
        )

    def extract_text(
        self,
        ref: str,
        include_roles: set[str] | None = None,
        visible_only: bool = True,
        timeout_ms: int | None = None,
        state: str | None = None,
        selector: str | None = None,
    ) -> tuple[RoleSnapshot, str]:
        return snapshot_then_extract_text_by_ref(
            self._page,
            ref,
            include_roles=include_roles,
            visible_only=visible_only,
            timeout_ms=timeout_ms,
            state=state,
            selector=selector,
        )

    def evaluate(
        self,
        ref: str,
        fn: str,
        include_roles: set[str] | None = None,
        visible_only: bool = True,
        timeout_ms: int | None = None,
        state: str | None = None,
        selector: str | None = None,
    ) -> tuple[RoleSnapshot, object]:
        return snapshot_then_evaluate_by_ref(
            self._page,
            ref,
            fn,
            include_roles=include_roles,
            visible_only=visible_only,
            timeout_ms=timeout_ms,
            state=state,
            selector=selector,
        )

    def wait(
        self,
        snapshot_selector: str | None = None,
        selector: str | None = None,
        url: str | None = None,
        load: str | None = None,
        fn: str | None = None,
        text: str | None = None,
        text_gone: str | None = None,
        timeout_ms: int = 10000,
        include_roles: set[str] | None = None,
        visible_only: bool = True,
    ) -> RoleSnapshot:
        return snapshot_then_wait(
            self._page,
            snapshot_selector=snapshot_selector,
            selector=selector,
            url=url,
            load=load,
            fn=fn,
            text=text,
            text_gone=text_gone,
            timeout_ms=timeout_ms,
            include_roles=include_roles,
            visible_only=visible_only,
        )


__all__ = ["BrowserPrimitives"]
