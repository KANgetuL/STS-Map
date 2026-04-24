from __future__ import annotations

from dataclasses import dataclass

from .enums import ActId, RoomType


@dataclass(frozen=True, slots=True)
class NodeId:
    floor: int
    x: int


@dataclass(frozen=True, slots=True)
class Edge:
    src: NodeId
    dst: NodeId


@dataclass(slots=True)
class RoomNode:
    id: NodeId
    room_type: RoomType | None = None
    display_type: RoomType = RoomType.QUESTION


@dataclass(slots=True)
class MapGraph:
    act_id: ActId
    nodes_by_floor: dict[int, list[RoomNode]]
    edges: list[Edge]


@dataclass(frozen=True, slots=True)
class GenerationInput:
    act_id: ActId
    ascension: int
    seed: int
    rule_version: str
