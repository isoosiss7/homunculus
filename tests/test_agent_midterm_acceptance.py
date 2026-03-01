import os
import re

import pytest
from playwright.sync_api import sync_playwright

from homunculus.playwright_utils import launch_chromium, new_anonymous_context
from tests.gmaps_helpers import (
    get_driving_eta,
    get_top_place_results,
    open_google_maps,
    search_location,
    search_places_nearby,
)

pytestmark = pytest.mark.skipif(
    os.getenv("HOMUNCULUS_RUN_ACCEPTANCE") != "1",
    reason="Acceptance tests require HOMUNCULUS_RUN_ACCEPTANCE=1",
)


def test_agent_run_google_maps_midterm():
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright, headless=True)
        context = new_anonymous_context(browser)
        page = context.new_page()
        try:
            origin = "Cross Creek Ranch community center, Fulshear TX"
            open_google_maps(page)
            search_location(page, origin)
            search_places_nearby(page, origin, "Thai restaurants")
            places = get_top_place_results(page, limit=2)
            assert len(places) == 2
            for place in places:
                eta_page = context.new_page()
                try:
                    open_google_maps(eta_page)
                    eta = get_driving_eta(eta_page, origin, place)
                finally:
                    eta_page.close()
                assert eta
                assert re.match(r"^\d+\s+min$|^\d+\s+hr(?:\s+\d+\s+min)?$", eta)
        finally:
            context.close()
            browser.close()
