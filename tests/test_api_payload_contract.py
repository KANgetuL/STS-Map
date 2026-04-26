from __future__ import annotations

import json

from sts_map.api import PUBLIC_API_VERSION, generate_map_json, generate_map_payload
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput
from sts_map.io import EXPORT_SCHEMA_VERSION


def test_generate_map_payload_contract_keys() -> None:
    input_data = GenerationInput(act_id=ActId.ACT1, ascension=10, seed=42, rule_version="0.6.0")
    payload = generate_map_payload(input_data)

    assert payload["schema_version"] == EXPORT_SCHEMA_VERSION
    assert payload["api_version"] == PUBLIC_API_VERSION
    assert payload["rule_version"] == "0.6.0"

    map_obj = payload["map"]
    assert isinstance(map_obj, dict)
    assert "act_id" in map_obj
    assert "nodes_by_floor" in map_obj
    assert "edges" in map_obj


def test_generate_map_json_is_valid_payload_json() -> None:
    input_data = GenerationInput(act_id=ActId.ACT2, ascension=12, seed=1234, rule_version="0.6.0")
    payload_json = generate_map_json(input_data)

    parsed = json.loads(payload_json)
    assert parsed["schema_version"] == EXPORT_SCHEMA_VERSION
    assert parsed["api_version"] == PUBLIC_API_VERSION
    assert parsed["rule_version"] == "0.6.0"
    assert parsed["map"]["act_id"] == "act2"
