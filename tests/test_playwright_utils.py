from homunculus.playwright_utils import launch_chromium, new_anonymous_context


class FakeChromium:
    def __init__(self):
        self.launch_calls = []

    def launch(self, **kwargs):
        self.launch_calls.append(kwargs)
        return {"launched": True, "kwargs": kwargs}


class FakePlaywright:
    def __init__(self):
        self.chromium = FakeChromium()


class FakeBrowser:
    def __init__(self):
        self.context_calls = []

    def new_context(self, **kwargs):
        self.context_calls.append(kwargs)
        return {"context": True, "kwargs": kwargs}


def test_launch_chromium_passes_expected_options():
    playwright = FakePlaywright()

    result = launch_chromium(playwright, headless=False)

    assert result["launched"] is True
    assert len(playwright.chromium.launch_calls) == 1
    kwargs = playwright.chromium.launch_calls[0]
    assert kwargs["headless"] is False
    assert kwargs["args"] == [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
    ]


def test_new_anonymous_context_passes_expected_options():
    browser = FakeBrowser()

    result = new_anonymous_context(browser)

    assert result["context"] is True
    assert len(browser.context_calls) == 1
    kwargs = browser.context_calls[0]
    assert kwargs["storage_state"] is None
    assert kwargs["java_script_enabled"] is True
    assert kwargs["locale"] == "en-US"
    assert kwargs["timezone_id"] == "America/Chicago"
    assert kwargs["viewport"] == {"width": 1366, "height": 768}
    assert kwargs["user_agent"].startswith("Mozilla/5.0")
    assert "Chrome/" in kwargs["user_agent"]
