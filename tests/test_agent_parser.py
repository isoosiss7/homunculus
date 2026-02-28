from homunculus.agent import parse_maps_midterm_intent


def test_parse_maps_midterm_intent_exact():
    purpose = (
        'I"m currently at the community center of Cross Creek Ranch, Fulshear TX, '
        "United States. Can you help me to find a couple of Thai restaurants near "
        "me and tell me the driving time under current traffic?"
    )
    intent = parse_maps_midterm_intent(purpose)
    assert intent is not None
    assert (
        intent.origin
        == "the community center of Cross Creek Ranch, Fulshear TX, United States"
    )
    assert intent.query == "Thai restaurants"
    assert intent.count == 2


def test_parse_maps_midterm_intent_non_matching():
    intent = parse_maps_midterm_intent("Find Thai restaurants near me.")
    assert intent is None
