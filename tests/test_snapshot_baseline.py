from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from sts_map.api.generate_map import generate_map
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput


def _build_metrics() -> dict[str, object]:
    seeds = list(range(50))
    room_counter: Counter[str] = Counter()
    edge_counts: list[int] = []
    floor_counts: list[int] = []
    special_counts: list[int] = []

    for seed in seeds:
        graph = generate_map(
            GenerationInput(act_id=ActId.ACT1, ascension=10, seed=seed, rule_version="0.5.1")
        )
        edge_counts.append(len(graph.edges))
        floor_counts.append(len(graph.nodes_by_floor))
        special_counts.append(
            sum(
                1
                for nodes in graph.nodes_by_floor.values()
                for node in nodes
                if node.room_type is not None and node.room_type.value == "special_elite"
            )
        )

        for nodes in graph.nodes_by_floor.values():
            for node in nodes:
                if node.room_type is not None:
                    room_counter[node.room_type.value] += 1

    return {
        "version": "0.5.1",
        "act": "act1",
        "ascension": 10,
        "seed_start": 0,
        "seed_end": 49,
        "sample_count": len(seeds),
        "room_counter": dict(sorted(room_counter.items())),
        "edge_total": sum(edge_counts),
        "edge_mean": sum(edge_counts) / len(edge_counts),
        "floor_mean": sum(floor_counts) / len(floor_counts),
        "special_elite_total": sum(special_counts),
    }


def test_distribution_snapshot_baseline() -> None:
    baseline_path = Path(__file__).parent / "snapshots" / "act1_distribution_baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = _build_metrics()

    assert current == baseline
