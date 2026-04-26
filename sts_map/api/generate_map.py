from __future__ import annotations

from sts_map.config import load_distribution_validation_config
from sts_map.config.schema import ActRuleConfig, RoomWeightConfig
from sts_map.domain.models import GenerationInput, MapGraph
from sts_map.generator.pipeline import MapGenerationService
from sts_map.generator.room_allocator import RoomAllocator
from sts_map.generator.topology_builder import TopologyBuilder
from sts_map.io.serializer import map_to_payload, payload_to_json
from sts_map.rules.rule_engine import RuleEngine
from sts_map.validators.map_validator import MapValidator

PUBLIC_API_VERSION = "1.0.0"


def default_act_rule_config() -> ActRuleConfig:
    return ActRuleConfig(
        floor_count=16,
        min_paths=4,
        max_paths=6,
        min_nodes_per_floor=3,
        max_nodes_per_floor=5,
        force_floor14_rest=True,
        force_floor15_boss=True,
        min_shop_count=1,
        min_elite_count=2,
    )


def default_room_weight_config() -> RoomWeightConfig:
    return RoomWeightConfig(monster=55.0, elite=8.0, question=22.0, shop=10.0, treasure=7.0)


def generate_map(input_data: GenerationInput) -> MapGraph:
    """Public single-function entrypoint for map generation."""
    dist_cfg = load_distribution_validation_config(input_data.act_id, input_data.ascension)
    service = MapGenerationService(
        topology_builder=TopologyBuilder(),
        room_allocator=RoomAllocator(),
        rule_engine=RuleEngine(),
        validator=MapValidator(dist_cfg=dist_cfg),
        act_cfg=default_act_rule_config(),
        room_weights=default_room_weight_config(),
    )
    return service.generate(input_data)


def generate_map_payload(input_data: GenerationInput) -> dict[str, object]:
    """Generate stable export payload containing schema and version metadata."""
    graph = generate_map(input_data)
    return map_to_payload(
        graph,
        rule_version=input_data.rule_version,
        api_version=PUBLIC_API_VERSION,
    )


def generate_map_json(input_data: GenerationInput, *, indent: int = 2) -> str:
    """Generate stable export payload in JSON format."""
    payload = generate_map_payload(input_data)
    return payload_to_json(payload, indent=indent)
