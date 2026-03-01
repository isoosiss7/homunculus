from __future__ import annotations

from tests import gmaps_helpers as google_maps


class _FakeTarget:
    def __init__(self, visible: bool, enabled: bool) -> None:
        self.visible = visible
        self.enabled = enabled
        self.wait_for_calls: list[tuple[str | None, int | None]] = []

    def wait_for(self, state: str | None = None, timeout: int | None = None) -> None:
        self.wait_for_calls.append((state, timeout))
        if not self.visible:
            raise RuntimeError("not visible")

    def is_enabled(self) -> bool:
        return self.enabled

    def is_visible(self) -> bool:
        return self.visible


class _FakeLocator:
    def __init__(self, target: _FakeTarget) -> None:
        self.first = target


class _FakePage:
    def __init__(
        self,
        role_targets: dict[str, _FakeTarget],
        css_target: _FakeTarget,
        reload_hook=None,
    ) -> None:
        self._role_targets = role_targets
        self._css_target = css_target
        self._reload_hook = reload_hook
        self.goto_calls: list[tuple[str, str | None]] = []
        self.reload_calls: list[str | None] = []
        self.role_calls: list[tuple[str, object | None]] = []
        self.locator_calls: list[str] = []

    def goto(self, url: str, wait_until: str | None = None) -> None:
        self.goto_calls.append((url, wait_until))

    def reload(self, wait_until: str | None = None) -> None:
        self.reload_calls.append(wait_until)
        if self._reload_hook:
            self._reload_hook()

    def get_by_role(self, role: str, name=None):
        self.role_calls.append((role, name))
        return _FakeLocator(self._role_targets[role])

    def locator(self, selector: str):
        self.locator_calls.append(selector)
        return _FakeLocator(self._css_target)


def test_open_google_maps_waits_for_role_search_box(monkeypatch) -> None:
    monkeypatch.setattr(google_maps, "_handle_consent_dialog", lambda page: None)
    combobox = _FakeTarget(visible=True, enabled=True)
    textbox = _FakeTarget(visible=False, enabled=False)
    css = _FakeTarget(visible=False, enabled=False)
    page = _FakePage({"combobox": combobox, "textbox": textbox}, css)

    google_maps.open_google_maps(page)

    assert page.goto_calls == [("https://www.google.com/maps", "domcontentloaded")]
    assert page.reload_calls == []
    assert any(
        role == "combobox"
        and hasattr(name, "pattern")
        and name.pattern == r"search"
        for role, name in page.role_calls
    )
    assert any(
        role == "textbox"
        and hasattr(name, "pattern")
        and name.pattern == r"search"
        for role, name in page.role_calls
    )
    assert combobox.wait_for_calls


def test_open_google_maps_falls_back_to_css_locator(monkeypatch) -> None:
    monkeypatch.setattr(google_maps, "_handle_consent_dialog", lambda page: None)
    combobox = _FakeTarget(visible=False, enabled=False)
    textbox = _FakeTarget(visible=False, enabled=False)
    css = _FakeTarget(visible=True, enabled=True)
    page = _FakePage({"combobox": combobox, "textbox": textbox}, css)

    google_maps.open_google_maps(page)

    assert "input#searchboxinput" in page.locator_calls
    assert css.wait_for_calls


def test_open_google_maps_retries_after_reload(monkeypatch) -> None:
    monkeypatch.setattr(google_maps, "_handle_consent_dialog", lambda page: None)
    monkeypatch.setattr(google_maps, "_SEARCH_BOX_TIMEOUT_MS", 5)
    combobox = _FakeTarget(visible=False, enabled=False)
    textbox = _FakeTarget(visible=False, enabled=False)
    css = _FakeTarget(visible=False, enabled=False)

    def _on_reload() -> None:
        css.visible = True
        css.enabled = True

    page = _FakePage({"combobox": combobox, "textbox": textbox}, css, _on_reload)

    google_maps.open_google_maps(page)

    assert page.reload_calls == ["domcontentloaded"]
    assert css.wait_for_calls
