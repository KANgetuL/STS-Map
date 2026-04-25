from __future__ import annotations

from sts_map.api.generate_map import default_act_rule_config, generate_map
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput
from sts_map.domain.state import GenerationContext
from sts_map.validators.map_validator import MapValidator


def test_multi_seed_validation_has_no_issues() -> None:
    validator = MapValidator()
    cfg = default_act_rule_config()

    for seed in range(80):
        input_data = GenerationInput(act_id=ActId.ACT1, ascension=10, seed=seed, rule_version="0.5.0")
        graph = generate_map(input_data)
        ctx = GenerationContext(rng_seed=input_data.seed, input=input_data)

        report = validator.validate_all(graph, ctx, cfg)
        assert report.ok, report.issues
