from __future__ import annotations

import subprocess
import sys


def test_cli_run_outputs_done() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "homunculus", "run", "say hello"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "DONE" in result.stdout.upper()
