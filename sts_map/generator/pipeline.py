from __future__ import annotations

from sts_map.config.schema import ActRuleConfig, RoomWeightConfig
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput, MapGraph
from sts_map.domain.state import GenerationContext
from sts_map.generator.room_allocator import RoomAllocator
from sts_map.generator.topology_builder import TopologyBuilder
from sts_map.rules.rule_engine import RuleEngine
from sts_map.validators.map_validator import MapValidator


class MapGenerationService:
    def __init__(
        self,
        topology_builder: TopologyBuilder,
        room_allocator: RoomAllocator,
        rule_engine: RuleEngine,
        validator: MapValidator,
        act_cfg: ActRuleConfig,
        room_weights: RoomWeightConfig,
    ) -> None:
        self._topology_builder = topology_builder
        self._room_allocator = room_allocator
        self._rule_engine = rule_engine
        self._validator = validator
        self._act_cfg = act_cfg
        self._room_weights = room_weights

    def generate(self, input_data: GenerationInput) -> MapGraph:
        ctx = GenerationContext(rng_seed=input_data.seed, input=input_data)

        if input_data.act_id == ActId.ACT4:
            graph = self._rule_engine.build_fixed_act4_map(ctx)
        else:
            graph = self._topology_builder.build(ctx, self._act_cfg)
            self._room_allocator.allocate(graph, ctx, self._act_cfg, self._room_weights)
            self._rule_engine.apply_act_specific_rules(graph, ctx)

        report = self._validator.validate_all(graph, ctx, self._act_cfg)
        if not report.ok:
            issue_text = "; ".join(f"{issue.code}:{issue.message}" for issue in report.issues)
            raise ValueError(f"Map validation failed: {issue_text}")

        return graph

    def generate_many(self, input_list: list[GenerationInput]) -> list[MapGraph]:
        return [self.generate(item) for item in input_list]
