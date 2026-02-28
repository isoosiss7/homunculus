import os
import re

import pytest

from homunculus.agent import run

pytestmark = pytest.mark.skipif(
    os.getenv("HOMUNCULUS_RUN_ACCEPTANCE") != "1",
    reason="Acceptance tests require HOMUNCULUS_RUN_ACCEPTANCE=1",
)


def test_agent_run_google_maps_midterm():
    purpose = (
        'I"m currently at the community center of Cross Creek Ranch, Fulshear TX, '
        "United States. Can you help me to find a couple of Thai restaurants near "
        "me and tell me the driving time under current traffic?"
    )
    done = run(purpose)
    assert done.result_json
    assert done.result_json.get("origin")
    assert done.result_json.get("query")
    places = done.result_json.get("places")
    assert isinstance(places, list)
    assert len(places) == 2
    for place in places:
        assert place.get("name")
        eta = place.get("eta")
        assert eta
        assert re.match(r"^\d+\s+min$|^\d+\s+hr(?:\s+\d+\s+min)?$", eta)
