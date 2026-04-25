from __future__ import annotations

from sts_map.api.generate_map import generate_map
from sts_map.domain.enums import ActId, RoomType
from sts_map.domain.models import GenerationInput


def test_act4_is_fixed_linear_template() -> None:
    graph = generate_map(GenerationInput(act_id=ActId.ACT4, ascension=0, seed=42, rule_version="0.5.0"))

    assert len(graph.nodes_by_floor) == 4
    assert len(graph.edges) == 3

    assert graph.nodes_by_floor[0][0].room_type == RoomType.REST
    assert graph.nodes_by_floor[1][0].room_type == RoomType.SHOP
    assert graph.nodes_by_floor[2][0].room_type == RoomType.ELITE
    assert graph.nodes_by_floor[3][0].room_type == RoomType.BOSS
