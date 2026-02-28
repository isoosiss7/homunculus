from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from homunculus.models import Done
from homunculus.state import save_state

ARTIFACTS_ROOT = Path(".homunculus/runs")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
