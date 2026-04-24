from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RoomWeightConfig:
    monster: float
    elite: float
    question: float
    shop: float
    treasure: float


@dataclass(frozen=True, slots=True)
class RandomRoomDynamicWeight:
    fight_base: float = 10.0
    treasure_base: float = 2.0
    shop_base: float = 3.0
    event_base: float = 85.0


@dataclass(frozen=True, slots=True)
class ActRuleConfig:
    floor_count: int
    min_paths: int
    max_paths: int
    min_nodes_per_floor: int
    max_nodes_per_floor: int
    force_floor14_rest: bool
    force_floor15_boss: bool
    min_shop_count: int
    min_elite_count: int
