from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from homunculus.browser_snapshot import snapshot_role_refs
from homunculus.models import Done
from homunculus.state import save_state

ARTIFACTS_ROOT = Path(".homunculus/runs")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _capture_failure(page, run_id: str, error: Exception) -> None:
    artifacts_dir = ARTIFACTS_ROOT / run_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": run_id,
        "captured_at": _utc_now(),
        "url": None,
        "error": {"type": type(error).__name__, "message": str(error)},
    }

    try:
        metadata["url"] = page.url
    except Exception:
        metadata["url"] = None

    try:
        page.screenshot(path=str(artifacts_dir / "failure.png"), full_page=True)
    except Exception:
        pass

    try:
        role_refs = snapshot_role_refs(page)
    except Exception:
        role_refs = []
    (artifacts_dir / "failure_role_refs.json").write_text(
        json.dumps(role_refs, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (artifacts_dir / "failure_metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(purpose: str) -> Done:
    run_id = uuid4().hex
    started_at = _utc_now()

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
        (artifacts_dir / "result.json").write_text(
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
