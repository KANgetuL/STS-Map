from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sts_map.domain.enums import ActId

from .schema import DistributionValidationConfig, RatioRange


class DistributionProfileError(ValueError):
    """Raised when distribution profile file is malformed."""


def load_distribution_validation_config(
    act_id: ActId,
    ascension: int,
    profile_path: Path | None = None,
) -> DistributionValidationConfig:
    """Load distribution validation thresholds from external profile JSON.

    Resolution order:
    1) First matching profile by act and ascension range.
    2) Global default config.
    """
    path = profile_path or Path(__file__).with_name("distribution_profiles.json")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DistributionProfileError(f"distribution profile file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DistributionProfileError(
            f"invalid JSON in distribution profile file {path}: {exc.msg}"
        ) from exc

    if not isinstance(payload, dict):
        raise DistributionProfileError("root payload must be an object")

    if "default" not in payload:
        raise DistributionProfileError("missing required field: default")

    default_cfg = _parse_config(payload["default"])
    profiles_raw = payload.get("profiles", [])
    if not isinstance(profiles_raw, list):
        raise DistributionProfileError("profiles must be a list")

    valid_acts = {item.value for item in ActId}

    for idx, item in enumerate(profiles_raw):
        if not isinstance(item, dict):
            raise DistributionProfileError(f"profiles[{idx}] must be an object")
        if "act" not in item:
            raise DistributionProfileError(f"profiles[{idx}] missing required field: act")
        if "config" not in item:
            raise DistributionProfileError(f"profiles[{idx}] missing required field: config")

        act_name = item["act"]
        if act_name not in valid_acts:
            raise DistributionProfileError(
                f"profiles[{idx}].act invalid value: {act_name}; expected one of {sorted(valid_acts)}"
            )

        if act_name != act_id.value:
            continue

        min_a = _parse_int(item.get("ascension_min", 0), f"profiles[{idx}].ascension_min")
        max_a = _parse_int(item.get("ascension_max", 20), f"profiles[{idx}].ascension_max")
        if min_a < 0 or max_a > 20 or min_a > max_a:
            raise DistributionProfileError(
                f"profiles[{idx}] invalid ascension range: [{min_a}, {max_a}], expected 0 <= min <= max <= 20"
            )

        if min_a <= ascension <= max_a:
            return _parse_config(item["config"], location=f"profiles[{idx}].config")

    return default_cfg


def _parse_config(data: Any, location: str = "default") -> DistributionValidationConfig:
    if not isinstance(data, dict):
        raise DistributionProfileError(f"{location} must be an object")

    required_fields = [
        "min_samples",
        "monster_ratio",
        "elite_like_ratio",
        "shop_ratio",
        "question_ratio",
    ]
    for field in required_fields:
        if field not in data:
            raise DistributionProfileError(f"{location} missing required field: {field}")

    min_samples = _parse_int(data["min_samples"], f"{location}.min_samples")
    if min_samples <= 0:
        raise DistributionProfileError(f"{location}.min_samples must be > 0")

    return DistributionValidationConfig(
        min_samples=min_samples,
        monster_ratio=_parse_ratio(data["monster_ratio"], f"{location}.monster_ratio"),
        elite_like_ratio=_parse_ratio(data["elite_like_ratio"], f"{location}.elite_like_ratio"),
        shop_ratio=_parse_ratio(data["shop_ratio"], f"{location}.shop_ratio"),
        question_ratio=_parse_ratio(data["question_ratio"], f"{location}.question_ratio"),
    )


def _parse_ratio(data: Any, location: str) -> RatioRange:
    if not isinstance(data, dict):
        raise DistributionProfileError(f"{location} must be an object")
    if "min" not in data or "max" not in data:
        raise DistributionProfileError(f"{location} must contain min and max")

    min_value = _parse_float(data["min"], f"{location}.min")
    max_value = _parse_float(data["max"], f"{location}.max")

    if min_value < 0.0 or max_value > 1.0 or min_value > max_value:
        raise DistributionProfileError(
            f"{location} invalid range [{min_value}, {max_value}], expected 0.0 <= min <= max <= 1.0"
        )

    return RatioRange(min_value=min_value, max_value=max_value)


def _parse_int(value: Any, location: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise DistributionProfileError(f"{location} must be an integer") from exc


def _parse_float(value: Any, location: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise DistributionProfileError(f"{location} must be a number") from exc
