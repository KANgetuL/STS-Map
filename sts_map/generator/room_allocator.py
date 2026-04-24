from __future__ import annotations

import random

from sts_map.config.schema import ActRuleConfig, RoomWeightConfig
from sts_map.domain.enums import RoomType
from sts_map.domain.models import MapGraph, NodeId, RoomNode
from sts_map.domain.state import GenerationContext


class RoomAllocator:
    def allocate(
        self,
        graph: MapGraph,
        ctx: GenerationContext,
        cfg: ActRuleConfig,
        weights: RoomWeightConfig,
    ) -> None:
        rng = random.Random(ctx.rng_seed + 97)
        self.assign_by_weight(graph, weights, ctx.input.ascension, rng)
        self.apply_floor_blacklist(graph, rng)
        self.apply_consecutive_constraints(graph, rng)
        self.force_key_floors(graph)
        self.repair_minimum_requirements(graph, cfg.min_shop_count, cfg.min_elite_count, rng)

    def assign_by_weight(
        self,
        graph: MapGraph,
        weights: RoomWeightConfig,
        ascension: int,
        rng: random.Random | None = None,
    ) -> None:
        rng = rng or random.Random(0)
        monster_weight = max(1.0, weights.monster - 0.5 * ascension)
        elite_weight = max(1.0, weights.elite + 0.5 * ascension)
        pool = [RoomType.MONSTER, RoomType.ELITE, RoomType.QUESTION, RoomType.SHOP, RoomType.TREASURE]
        value_weights = [monster_weight, elite_weight, weights.question, weights.shop, weights.treasure]

        for floor, nodes in graph.nodes_by_floor.items():
            for node in nodes:
                # Floor 0 is the opening floor and is stabilized as monster in this phase.
                if floor == 0:
                    node.room_type = RoomType.MONSTER
                    node.display_type = RoomType.MONSTER
                    continue
                picked = rng.choices(pool, weights=value_weights, k=1)[0]
                node.room_type = picked
                node.display_type = picked

    def apply_floor_blacklist(self, graph: MapGraph, rng: random.Random | None = None) -> None:
        rng = rng or random.Random(0)
        for floor, nodes in graph.nodes_by_floor.items():
            for node in nodes:
                if node.room_type is None:
                    continue
                if floor in (1, 2, 3) and node.room_type == RoomType.ELITE:
                    self._replace_room_type(node, [RoomType.MONSTER, RoomType.QUESTION, RoomType.SHOP, RoomType.TREASURE], rng)
                if floor in (1, 2, 3, 4, 5, 13) and node.room_type == RoomType.REST:
                    self._replace_room_type(node, [RoomType.MONSTER, RoomType.QUESTION, RoomType.SHOP, RoomType.TREASURE], rng)

    def apply_consecutive_constraints(self, graph: MapGraph, rng: random.Random | None = None) -> None:
        rng = rng or random.Random(0)
        special = {RoomType.REST, RoomType.ELITE, RoomType.SHOP}
        node_index = self._node_lookup(graph)

        for edge in graph.edges:
            src = node_index.get(edge.src)
            dst = node_index.get(edge.dst)
            if src is None or dst is None or src.room_type is None or dst.room_type is None:
                continue
            if src.room_type in special and dst.room_type == src.room_type and dst.id.floor not in (14, 15):
                choices = [RoomType.MONSTER, RoomType.QUESTION, RoomType.TREASURE]
                self._replace_room_type(dst, choices, rng)

    def force_key_floors(self, graph: MapGraph) -> None:
        if 14 in graph.nodes_by_floor:
            for node in graph.nodes_by_floor[14]:
                node.room_type = RoomType.REST
                node.display_type = RoomType.REST

        max_floor = max(graph.nodes_by_floor) if graph.nodes_by_floor else -1
        boss_floor = 15 if 15 in graph.nodes_by_floor else max_floor
        if boss_floor in graph.nodes_by_floor:
            for node in graph.nodes_by_floor[boss_floor]:
                node.room_type = RoomType.BOSS
                node.display_type = RoomType.BOSS

    def repair_minimum_requirements(
        self,
        graph: MapGraph,
        min_shop: int,
        min_elite: int,
        rng: random.Random | None = None,
    ) -> None:
        rng = rng or random.Random(0)
        pool = self._repair_candidates(graph)

        current_shop = self._count_room_type(graph, RoomType.SHOP)
        while current_shop < min_shop and pool:
            node = pool.pop(0)
            node.room_type = RoomType.SHOP
            node.display_type = RoomType.SHOP
            current_shop += 1

        current_elite = self._count_room_type(graph, RoomType.ELITE)
        while current_elite < min_elite and pool:
            node = pool.pop(0)
            node.room_type = RoomType.ELITE
            node.display_type = RoomType.ELITE
            current_elite += 1

        # Re-run consecutive constraints after repair to avoid introducing illegal chains.
        self.apply_consecutive_constraints(graph, rng)

    def _replace_room_type(self, node: RoomNode, choices: list[RoomType], rng: random.Random) -> None:
        chosen = rng.choice(choices)
        node.room_type = chosen
        node.display_type = chosen

    def _count_room_type(self, graph: MapGraph, room_type: RoomType) -> int:
        count = 0
        for nodes in graph.nodes_by_floor.values():
            count += sum(1 for node in nodes if node.room_type == room_type)
        return count

    def _repair_candidates(self, graph: MapGraph) -> list[RoomNode]:
        candidates: list[RoomNode] = []
        for floor in sorted(graph.nodes_by_floor.keys()):
            if floor in (0, 14, 15):
                continue
            for node in graph.nodes_by_floor[floor]:
                if node.room_type in {RoomType.MONSTER, RoomType.QUESTION, RoomType.TREASURE}:
                    candidates.append(node)
        return candidates

    def _node_lookup(self, graph: MapGraph) -> dict[NodeId, RoomNode]:
        lookup: dict[NodeId, RoomNode] = {}
        for nodes in graph.nodes_by_floor.values():
            for node in nodes:
                lookup[node.id] = node
        return lookup
