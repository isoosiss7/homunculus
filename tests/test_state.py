from __future__ import annotations

from pathlib import Path

from homunculus.state import load_state, save_state


def test_state_roundtrip(tmp_path: Path) -> None:
    state = {
        "status": "idle",
        "step_id": "s1",
        "step_name": "Start",
        "started_at": "2026-02-28T00:00:00Z",
        "last_heartbeat_at": "2026-02-28T00:00:01Z",
        "last_error": None,
        "needs_human": False,
        "human_question": None,
        "run_id": "run-123",
    }
    path = tmp_path / "state.json"

    save_state(state, path)
    loaded = load_state(path)

    assert loaded == state
