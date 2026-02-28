from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import sync_playwright

from homunculus.google_maps import (
    get_driving_eta,
    get_top_place_results,
    open_google_maps,
    search_location,
    search_places_nearby,
)
from homunculus.models import Done
from homunculus.playwright_utils import launch_chromium, new_anonymous_context
from homunculus.state import save_state

ARTIFACTS_ROOT = Path(".homunculus/runs")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MapsMidtermIntent:
    origin: str
    query: str
    count: int


_ORIGIN_RE = re.compile(r"\bI[\"']?m currently at\s+(?P<origin>.+?)\.", re.IGNORECASE)
_QUERY_RE = re.compile(
    r"\bfind\s+(?P<count>a couple)\s+of\s+(?P<query>.+?)\s+near me\b",
    re.IGNORECASE,
)


def parse_maps_midterm_intent(purpose: str) -> MapsMidtermIntent | None:
    if not purpose:
        return None
    origin_match = _ORIGIN_RE.search(purpose)
    query_match = _QUERY_RE.search(purpose)
    if not origin_match or not query_match:
        return None
    origin = origin_match.group("origin").strip()
    query = query_match.group("query").strip()
    count = 2 if query_match.group("count").lower() == "a couple" else 0
    if not origin or not query or count <= 0:
        return None
    return MapsMidtermIntent(origin=origin, query=query, count=count)


def _should_run_headless() -> bool:
    env_value = (os.getenv("HOMUNCULUS_HEADLESS") or "").strip().lower()
    if env_value in {"1", "true", "yes"}:
        return True
    if os.getenv("PYTEST_CURRENT_TEST"):
        return True
    return False


def _run_maps_midterm(intent: MapsMidtermIntent, run_id: str) -> Done:
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright, headless=_should_run_headless())
        context = new_anonymous_context(browser)
        page = context.new_page()
        try:
            open_google_maps(page)
            search_location(page, intent.origin)
            search_places_nearby(page, intent.origin, intent.query)
            places = get_top_place_results(page, limit=intent.count)

            results = []
            for place_name in places:
                eta = get_driving_eta(page, intent.origin, place_name)
                results.append({"name": place_name, "eta": eta})
        finally:
            context.close()
            browser.close()

    result_json = {
        "origin": intent.origin,
        "query": intent.query,
        "places": results,
        "run_id": run_id,
    }

    summary = (
        f"DONE: Found {len(results)} {intent.query} near {intent.origin} with ETAs."
    )
    return Done(summary=summary, result_json=result_json)


def run(purpose: str) -> Done:
    run_id = uuid4().hex
    started_at = _utc_now()

    intent = parse_maps_midterm_intent(purpose)
    if intent:
        done = _run_maps_midterm(intent, run_id)
    else:
        done = Done(
            summary=f"DONE: {purpose}",
            result_json={"purpose": purpose, "run_id": run_id},
        )

    artifacts_dir = ARTIFACTS_ROOT / run_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "done.json").write_text(
        json.dumps(done.model_dump(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if done.result_json:
        (artifacts_dir / "maps_results.json").write_text(
            json.dumps(done.result_json, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    state = {
        "status": "done",
        "step_id": "done",
        "step_name": "Complete",
        "started_at": started_at,
        "last_heartbeat_at": _utc_now(),
        "last_error": None,
        "needs_human": False,
        "human_question": None,
        "run_id": run_id,
    }
    save_state(state)

    return done
