from __future__ import annotations

from tests import gmaps_helpers as google_maps


class _FakeInput:
    def __init__(self) -> None:
        self.click_calls = 0
        self.fill_calls: list[str] = []
        self.press_calls: list[str] = []
        self.wait_for_calls: list[tuple[str | None, int | None]] = []

    def wait_for(self, state: str | None = None, timeout: int | None = None) -> None:
        self.wait_for_calls.append((state, timeout))

    def click(self) -> None:
        self.click_calls += 1

    def fill(self, value: str) -> None:
        self.fill_calls.append(value)

    def press(self, key: str) -> None:
        self.press_calls.append(key)


class _FakeOption:
    def __init__(self, visible: bool) -> None:
        self.visible = visible
        self.click_calls = 0

    def wait_for(self, state: str | None = None, timeout: int | None = None) -> None:
        if not self.visible:
            raise RuntimeError("not visible")

    def click(self) -> None:
        self.click_calls += 1


class _FakeListbox:
    def __init__(self, visible: bool) -> None:
        self.visible = visible
        self.option = _FakeOption(visible=False)

    def wait_for(self, state: str | None = None, timeout: int | None = None) -> None:
        if not self.visible:
            raise RuntimeError("not visible")

    def get_by_role(self, role: str, name=None):
        return _FakeLocator(self.option)


class _FakeLocator:
    def __init__(self, target) -> None:
        self.first = target


class _FakeScope:
    def __init__(self, input_locator: _FakeInput, listbox: _FakeListbox) -> None:
        self._input = input_locator
        self._listbox = listbox

    def get_by_role(self, role: str, name=None):
        if role == "listbox":
            return _FakeLocator(self._listbox)
        return _FakeLocator(self._input)


class _FakePage:
    def __init__(self, scope: _FakeScope) -> None:
        self._scope = scope

    def get_by_role(self, role: str, name=None):
        return self._scope.get_by_role(role, name)


def test_ensure_origin_filled_clears_and_falls_back_to_keys(monkeypatch) -> None:
    origin = "Chicago, IL"
    fake_input = _FakeInput()
    scope = _FakeScope(fake_input, _FakeListbox(visible=False))
    page = _FakePage(scope)

    monkeypatch.setattr(google_maps, "_directions_scope", lambda page: scope)

    google_maps._ensure_origin_filled(page, origin)

    assert fake_input.click_calls == 1
    assert "" in fake_input.fill_calls
    assert origin in fake_input.fill_calls
    assert "ArrowDown" in fake_input.press_calls
    assert "Enter" in fake_input.press_calls
    assert ("Control+A" in fake_input.press_calls) or ("Meta+A" in fake_input.press_calls)
    assert ("Backspace" in fake_input.press_calls) or ("Delete" in fake_input.press_calls)
