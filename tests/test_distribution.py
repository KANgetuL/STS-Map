from __future__ import annotations

from sts_map.api.generate_map import generate_map
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput
from sts_map.validators.map_validator import MapValidator


def test_distribution_validation_over_sample_set() -> None:
    validator = MapValidator()
    samples = [
        generate_map(GenerationInput(act_id=ActId.ACT1, ascension=10, seed=seed, rule_version="0.5.0"))
        for seed in range(120)
    ]

    issues = validator.validate_distribution(samples)
    assert not issues, issues
