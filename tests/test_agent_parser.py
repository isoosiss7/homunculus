from types import SimpleNamespace

from homunculus import agent


def test_run_keeps_result_generic(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(agent, "ARTIFACTS_ROOT", tmp_path)
    monkeypatch.setattr(agent, "uuid4", lambda: SimpleNamespace(hex="run-789"))
    monkeypatch.setattr(agent, "save_state", lambda _state: None)

    done = agent.run("Find Thai restaurants near me.")

    assert done.result_json["purpose"] == "Find Thai restaurants near me."
    assert done.result_json["run_id"] == "run-789"
    assert "origin" not in done.result_json
    assert "places" not in done.result_json
