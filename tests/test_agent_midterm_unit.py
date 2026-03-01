import json
from types import SimpleNamespace

from homunculus import agent


def test_run_writes_done_and_result(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(agent, "ARTIFACTS_ROOT", tmp_path)
    monkeypatch.setattr(agent, "uuid4", lambda: SimpleNamespace(hex="run-456"))
    monkeypatch.setattr(agent, "_utc_now", lambda: "2024-01-01T00:00:00+00:00")

    captured_state = {}

    def _save_state(state):
        captured_state.update(state)

    monkeypatch.setattr(agent, "save_state", _save_state)

    done = agent.run("Test purpose")

    assert done.summary == "DONE: Test purpose"
    assert done.result_json == {"purpose": "Test purpose", "run_id": "run-456"}

    artifacts_dir = tmp_path / "run-456"
    done_payload = json.loads((artifacts_dir / "done.json").read_text())
    assert done_payload["summary"] == "DONE: Test purpose"

    result_payload = json.loads((artifacts_dir / "result.json").read_text())
    assert result_payload["run_id"] == "run-456"

    assert captured_state["run_id"] == "run-456"
