from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from tests.gmaps_helpers import (
    eta_to_minutes,
    find_etas,
    parse_eta,
    select_shortest_eta,
)


class _DirectionsCaseParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cases: list[tuple[str, str]] = []
        self._current_expected: str | None = None
        self._capture = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "div":
            return
        attributes = {key: value for key, value in attrs}
        if attributes.get("class") == "case":
            self._capture = True
            self._current_expected = attributes.get("data-expected") or ""
            self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._capture or tag != "div":
            return
        text = " ".join("".join(self._chunks).split())
        self.cases.append((self._current_expected or "", text))
        self._capture = False
        self._current_expected = None
        self._chunks = []


def _load_fixture_cases() -> list[tuple[str, str]]:
    fixture_path = Path(__file__).parent / "fixtures" / "google_maps_directions.html"
    html = fixture_path.read_text(encoding="utf-8")
    parser = _DirectionsCaseParser()
    parser.feed(html)
    return parser.cases


def test_parse_eta_from_fixture_cases() -> None:
    cases = _load_fixture_cases()
    assert cases
    for expected, text in cases:
        assert parse_eta(text) == expected


def test_parse_eta_none_when_missing() -> None:
    text = "No routes available. Try again later."
    assert parse_eta(text) is None


def test_find_etas_from_fixture_cases() -> None:
    cases = _load_fixture_cases()
    assert cases
    for expected, text in cases:
        assert expected in find_etas(text)


def test_eta_to_minutes() -> None:
    assert eta_to_minutes("12 min") == 12
    assert eta_to_minutes("1 hr") == 60
    assert eta_to_minutes("1 hr 5 min") == 65


def test_select_shortest_eta() -> None:
    texts = [
        "Fastest route 20 min",
        "Alternate route 1 hr 5 min",
        "Scenic route 15 min",
    ]
    assert select_shortest_eta(texts) == "15 min"
