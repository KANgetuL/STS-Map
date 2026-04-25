from __future__ import annotations

from sts_map.api.generate_map import generate_map
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput
from sts_map.io.serializer import map_to_dict


def test_same_seed_same_output() -> None:
    input_data = GenerationInput(act_id=ActId.ACT1, ascension=7, seed=20260425, rule_version="0.5.0")

    first = generate_map(input_data)
    second = generate_map(input_data)

    assert map_to_dict(first) == map_to_dict(second)


def test_different_seed_likely_different_output() -> None:
    first_input = GenerationInput(act_id=ActId.ACT1, ascension=7, seed=1001, rule_version="0.5.0")
    second_input = GenerationInput(act_id=ActId.ACT1, ascension=7, seed=1002, rule_version="0.5.0")

    first = generate_map(first_input)
    second = generate_map(second_input)

    assert map_to_dict(first) != map_to_dict(second)
