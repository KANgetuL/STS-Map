from __future__ import annotations

from sts_map.domain.enums import ActId, RoomType
from sts_map.domain.models import Edge, MapGraph, NodeId, RoomNode
from sts_map.domain.state import GenerationContext


class RuleEngine:
    def apply_act_specific_rules(self, graph: MapGraph, ctx: GenerationContext) -> None:
        _ = (graph, ctx)
        return None

    def apply_act1_special_elite(self, graph: MapGraph, visited_special_elite: bool) -> None:
        _ = (graph, visited_special_elite)
        return None

    def build_fixed_act4_map(self, ctx: GenerationContext) -> MapGraph:
        _ = ctx
        nodes_by_floor: dict[int, list[RoomNode]] = {
            0: [RoomNode(id=NodeId(0, 0), room_type=RoomType.REST, display_type=RoomType.REST)],
            1: [RoomNode(id=NodeId(1, 0), room_type=RoomType.SHOP, display_type=RoomType.SHOP)],
            2: [RoomNode(id=NodeId(2, 0), room_type=RoomType.ELITE, display_type=RoomType.ELITE)],
            3: [RoomNode(id=NodeId(3, 0), room_type=RoomType.BOSS, display_type=RoomType.BOSS)],
        }
        edges = [
            Edge(src=NodeId(0, 0), dst=NodeId(1, 0)),
            Edge(src=NodeId(1, 0), dst=NodeId(2, 0)),
            Edge(src=NodeId(2, 0), dst=NodeId(3, 0)),
        ]
        return MapGraph(act_id=ActId.ACT4, nodes_by_floor=nodes_by_floor, edges=edges)
