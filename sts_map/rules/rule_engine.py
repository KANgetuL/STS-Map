from __future__ import annotations

from sts_map.domain.enums import ActId, RoomType
from sts_map.domain.models import Edge, MapGraph, NodeId, RoomNode
from sts_map.domain.state import GenerationContext


class RuleEngine:
    def apply_act_specific_rules(self, graph: MapGraph, ctx: GenerationContext) -> None:
        visited_special_elite = ctx.metadata.get("visited_special_elite", "false") == "true"
        pending_flag = ctx.metadata.get("pending_special_elite")

        if graph.act_id == ActId.ACT1:
            self.apply_act1_special_elite(graph, visited_special_elite)
            # Campaign-level manager can carry this flag into Act2 generation.
            ctx.metadata["pending_special_elite"] = "false" if visited_special_elite else "true"
            return None

        should_apply_in_act2 = pending_flag != "false"
        if graph.act_id == ActId.ACT2 and should_apply_in_act2 and not visited_special_elite:
            self.apply_act1_special_elite(graph, visited_special_elite)

        return None

    def apply_act1_special_elite(self, graph: MapGraph, visited_special_elite: bool) -> None:
        if visited_special_elite:
            return None

        elite_nodes: list[RoomNode] = []
        for floor in sorted(graph.nodes_by_floor.keys()):
            for node in graph.nodes_by_floor[floor]:
                if node.room_type == RoomType.ELITE:
                    elite_nodes.append(node)

        if not elite_nodes:
            return None

        # Deterministic selection to keep reproducibility stable.
        elite_nodes.sort(key=lambda n: (n.id.floor, n.id.x))
        picked = elite_nodes[0]
        picked.room_type = RoomType.SPECIAL_ELITE
        picked.display_type = RoomType.SPECIAL_ELITE
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
