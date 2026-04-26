from __future__ import annotations

import json

from sts_map.domain.models import MapGraph

EXPORT_SCHEMA_VERSION = "1.0.0"


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
            for floor, nodes in sorted(graph.nodes_by_floor.items())
        },
        "edges": [
            {
                "src": {"floor": edge.src.floor, "x": edge.src.x},
                "dst": {"floor": edge.dst.floor, "x": edge.dst.x},
            }
            for edge in graph.edges
        ],
    }


def map_to_payload(
    graph: MapGraph,
    *,
    rule_version: str,
    api_version: str = "1.0.0",
) -> dict[str, object]:
    """Wrap map graph into stable export payload with metadata."""
    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "api_version": api_version,
        "rule_version": rule_version,
        "map": map_to_dict(graph),
    }


def map_to_json(graph: MapGraph, *, indent: int = 2) -> str:
    """Serialize map graph to JSON string."""
    return json.dumps(map_to_dict(graph), ensure_ascii=False, indent=indent)


def payload_to_json(payload: dict[str, object], *, indent: int = 2) -> str:
    """Serialize export payload to JSON string."""
    return json.dumps(payload, ensure_ascii=False, indent=indent)
