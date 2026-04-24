from __future__ import annotations

import json

from sts_map.domain.models import MapGraph


def map_to_dict(graph: MapGraph) -> dict[str, object]:
    """Convert map graph into a JSON-serializable dictionary."""
    return {
        "act_id": graph.act_id.value,
        "nodes_by_floor": {
            str(floor): [
                {
                    "floor": node.id.floor,
                    "x": node.id.x,
                    "room_type": node.room_type.value if node.room_type else None,
                    "display_type": node.display_type.value,
                }
                for node in nodes
            ]
            for floor, nodes in graph.nodes_by_floor.items()
        },
        "edges": [
            {
                "src": {"floor": edge.src.floor, "x": edge.src.x},
                "dst": {"floor": edge.dst.floor, "x": edge.dst.x},
            }
            for edge in graph.edges
        ],
    }


def map_to_json(graph: MapGraph, *, indent: int = 2) -> str:
    """Serialize map graph to JSON string."""
    return json.dumps(map_to_dict(graph), ensure_ascii=False, indent=indent)
