import json
from pathlib import Path

from homunculus import agent


class _FakePage:
    url = "https://example.com/maps"

    def screenshot(self, *, path: str, full_page: bool) -> None:
        Path(path).write_bytes(b"png")


def test_capture_maps_failure_writes_artifacts(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(agent, "ARTIFACTS_ROOT", tmp_path)
    monkeypatch.setattr(agent, "snapshot_role_refs", lambda page: ["button:Save"])

    agent._capture_maps_failure(_FakePage(), "run-123", RuntimeError("boom"))

    artifacts_dir = tmp_path / "run-123"
    assert (artifacts_dir / "failure.png").read_bytes() == b"png"
    assert json.loads((artifacts_dir / "failure_role_refs.json").read_text()) == [
        "button:Save",
    ]
    metadata = json.loads((artifacts_dir / "failure_metadata.json").read_text())
    assert metadata["url"] == "https://example.com/maps"
    assert metadata["error"]["type"] == "RuntimeError"
