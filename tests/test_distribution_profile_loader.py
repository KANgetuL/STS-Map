from __future__ import annotations

import json
from pathlib import Path

import pytest

from sts_map.config.distribution_loader import DistributionProfileError
from sts_map.config.distribution_loader import load_distribution_validation_config
from sts_map.domain.enums import ActId


def test_load_distribution_profile_default_for_act3() -> None:
    cfg = load_distribution_validation_config(ActId.ACT3, ascension=10)

    assert cfg.min_samples == 30
    assert cfg.monster_ratio.min_value == 0.20
    assert cfg.monster_ratio.max_value == 0.80


def test_load_distribution_profile_act1_high_ascension_override() -> None:
    cfg = load_distribution_validation_config(ActId.ACT1, ascension=17)

    assert cfg.min_samples == 40
    assert cfg.monster_ratio.min_value == 0.18
    assert cfg.monster_ratio.max_value == 0.78
    assert cfg.elite_like_ratio.max_value == 0.45


def test_invalid_json_raises_profile_error(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not-valid-json}", encoding="utf-8")

    with pytest.raises(DistributionProfileError, match="invalid JSON"):
        load_distribution_validation_config(ActId.ACT1, ascension=0, profile_path=bad_file)


def test_missing_required_default_field_raises_profile_error(tmp_path: Path) -> None:
    payload = {"profiles": []}
    profile_file = tmp_path / "missing_default.json"
    profile_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DistributionProfileError, match="missing required field: default"):
        load_distribution_validation_config(ActId.ACT1, ascension=0, profile_path=profile_file)


def test_invalid_ratio_range_raises_profile_error(tmp_path: Path) -> None:
    payload = {
        "default": {
            "min_samples": 30,
            "monster_ratio": {"min": 0.9, "max": 0.2},
            "elite_like_ratio": {"min": 0.02, "max": 0.4},
            "shop_ratio": {"min": 0.01, "max": 0.25},
            "question_ratio": {"min": 0.05, "max": 0.6},
        },
        "profiles": [],
    }
    profile_file = tmp_path / "bad_range.json"
    profile_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DistributionProfileError, match="invalid range"):
        load_distribution_validation_config(ActId.ACT1, ascension=0, profile_path=profile_file)
