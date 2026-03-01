from dataclasses import dataclass

from homunculus import agent


class _FakePage:
    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _FakeContext:
    def __init__(self) -> None:
        self.pages = []
        self.closed = False

    def new_page(self):
        page = _FakePage(f"page-{len(self.pages)}")
        self.pages.append(page)
        return page

    def close(self) -> None:
        self.closed = True


class _FakeBrowser:
    def __init__(self, context: _FakeContext) -> None:
        self._context = context
        self.closed = False

    def new_context(self, **_kwargs):
        return self._context

    def close(self) -> None:
        self.closed = True


class _FakeChromium:
    def __init__(self, browser: _FakeBrowser) -> None:
        self._browser = browser

    def launch(self, **_kwargs):
        return self._browser


class _FakePlaywright:
    def __init__(self, browser: _FakeBrowser) -> None:
        self.chromium = _FakeChromium(browser)


class _FakeSyncPlaywright:
    def __init__(self, playwright: _FakePlaywright) -> None:
        self._playwright = playwright

    def __enter__(self):
        return self._playwright

    def __exit__(self, exc_type, exc, tb):
        return False


@dataclass(frozen=True)
class _Intent:
    origin: str
    query: str
    count: int


def test_run_maps_midterm_uses_fresh_pages(monkeypatch) -> None:
    context = _FakeContext()
    browser = _FakeBrowser(context)
    fake_playwright = _FakePlaywright(browser)

    def _fake_sync_playwright():
        return _FakeSyncPlaywright(fake_playwright)

    opened_pages = []
    eta_pages = []
    search_pages = []

    def _open_google_maps(page):
        opened_pages.append(page)

    def _search_location(page, _origin):
        search_pages.append(page)

    def _search_places_nearby(page, _origin, _query):
        search_pages.append(page)

    def _get_top_place_results(_page, limit):
        return [f"Place {idx}" for idx in range(1, limit + 1)]

    def _get_driving_eta(page, _origin, destination_place_name):
        eta_pages.append(page)
        return f"{destination_place_name} ETA"

    monkeypatch.setattr(agent, "sync_playwright", _fake_sync_playwright)
    monkeypatch.setattr(agent, "launch_chromium", lambda _pw, headless: browser)
    monkeypatch.setattr(agent, "new_anonymous_context", lambda _browser: context)
    monkeypatch.setattr(agent, "open_google_maps", _open_google_maps)
    monkeypatch.setattr(agent, "search_location", _search_location)
    monkeypatch.setattr(agent, "search_places_nearby", _search_places_nearby)
    monkeypatch.setattr(agent, "get_top_place_results", _get_top_place_results)
    monkeypatch.setattr(agent, "get_driving_eta", _get_driving_eta)

    intent = _Intent(origin="Austin, TX", query="tacos", count=2)
    done = agent._run_maps_midterm(intent, run_id="run-456")

    assert done.result_json["places"]
    assert len(context.pages) == 1 + intent.count
    assert len(opened_pages) == 1 + intent.count
    assert opened_pages[0] is context.pages[0]
    assert eta_pages == context.pages[1:]
    assert all(page.closed for page in context.pages[1:])
    assert context.pages[0] in search_pages
