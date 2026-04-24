from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Sequence

from sts_map.config.schema import ActRuleConfig
from sts_map.domain.models import Edge, MapGraph, NodeId, RoomNode
from sts_map.domain.state import GenerationContext


class TopologyBuilder:
    def build(self, ctx: GenerationContext, cfg: ActRuleConfig) -> MapGraph:
        rng = random.Random(ctx.rng_seed)
        nodes_by_floor: dict[int, list[RoomNode]] = {}

        for floor in range(cfg.floor_count):
            count = self.sample_floor_node_count(floor, cfg, rng)
            positions = self._compute_x_positions(count, cfg.max_nodes_per_floor)
            nodes_by_floor[floor] = [RoomNode(id=NodeId(floor=floor, x=x)) for x in positions]

        graph = MapGraph(act_id=ctx.input.act_id, nodes_by_floor=nodes_by_floor, edges=[])
        self.generate_main_paths(graph, cfg.min_paths, cfg.max_paths, rng)
        self._saturate_connectivity(graph, rng)
        self.enforce_node_load_limits(graph)
        self.prune_isolated_nodes(graph)
        return graph

    def sample_floor_node_count(self, floor: int, cfg: ActRuleConfig, rng: random.Random | None = None) -> int:
        rng = rng or random.Random(floor)
        if cfg.floor_count <= 1:
            return cfg.max_nodes_per_floor

        # Floors closer to boss have stronger pull towards smaller width.
        progress = floor / (cfg.floor_count - 1)
        low_pick_weight = progress
        pivot = (cfg.min_nodes_per_floor + cfg.max_nodes_per_floor) // 2

        if rng.random() < low_pick_weight:
            upper = max(cfg.min_nodes_per_floor, pivot)
            return rng.randint(cfg.min_nodes_per_floor, upper)

        lower = min(cfg.max_nodes_per_floor, pivot)
        return rng.randint(lower, cfg.max_nodes_per_floor)

    def generate_main_paths(
        self,
        graph: MapGraph,
        min_paths: int,
        max_paths: int,
        rng: random.Random | None = None,
    ) -> list[list[NodeId]]:
        rng = rng or random.Random(0)
        path_count = rng.randint(min_paths, max_paths)

        starts = list(graph.nodes_by_floor[0])
        rng.shuffle(starts)
        chosen_starts: list[NodeId] = []
        for node in starts:
            chosen_starts.append(node.id)
            if len(chosen_starts) >= min(path_count, len(starts)):
                break

        if len(chosen_starts) == 1 and len(starts) > 1:
            chosen_starts.append(starts[1].id)

        paths: list[list[NodeId]] = []
        out_degree: defaultdict[NodeId, int] = defaultdict(int)
        in_degree: defaultdict[NodeId, int] = defaultdict(int)
        edge_set: set[tuple[NodeId, NodeId]] = set()

        for i in range(path_count):
            current = chosen_starts[i % len(chosen_starts)]
            path = [current]
            for floor in range(1, len(graph.nodes_by_floor)):
                candidates = [node.id for node in graph.nodes_by_floor[floor] if self.can_connect(current, node.id)]
                rng.shuffle(candidates)

                if not candidates:
                    raise ValueError(
                        f"No legal candidate from floor {current.floor} x={current.x} to floor {floor}"
                    )

                selected: NodeId | None = None
                for candidate in candidates:
                    edge = Edge(src=current, dst=candidate)
                    if self.would_intersect(graph.edges, edge):
                        continue
                    if out_degree[current] >= 2 or in_degree[candidate] >= 2:
                        continue
                    selected = candidate
                    break

                if selected is None:
                    selected = min(candidates, key=lambda nid: abs(nid.x - current.x))

                edge_key = (current, selected)
                if edge_key not in edge_set:
                    graph.edges.append(Edge(src=current, dst=selected))
                    edge_set.add(edge_key)
                    out_degree[current] += 1
                    in_degree[selected] += 1

                current = selected
                path.append(current)

            paths.append(path)

        return paths

    def can_connect(self, src: NodeId, dst: NodeId) -> bool:
        return dst.floor == src.floor + 1 and abs(dst.x - src.x) <= 1

    def would_intersect(self, existing_edges: Sequence[Edge], candidate: Edge) -> bool:
        for edge in existing_edges:
            if edge.src.floor != candidate.src.floor:
                continue
            if edge.dst.floor != candidate.dst.floor:
                continue

            # Shared endpoints represent branch/merge and are allowed.
            if (
                edge.src == candidate.src
                or edge.src == candidate.dst
                or edge.dst == candidate.src
                or edge.dst == candidate.dst
            ):
                continue

            if (edge.src.x - candidate.src.x) * (edge.dst.x - candidate.dst.x) < 0:
                return True

        return False

    def enforce_node_load_limits(self, graph: MapGraph, max_in: int = 2, max_out: int = 2) -> None:
        in_degree: defaultdict[NodeId, int] = defaultdict(int)
        out_degree: defaultdict[NodeId, int] = defaultdict(int)
        kept: list[Edge] = []

        for edge in sorted(graph.edges, key=lambda e: (e.src.floor, e.src.x, e.dst.x)):
            if out_degree[edge.src] >= max_out or in_degree[edge.dst] >= max_in:
                continue
            kept.append(edge)
            out_degree[edge.src] += 1
            in_degree[edge.dst] += 1

        graph.edges = kept

    def prune_isolated_nodes(self, graph: MapGraph) -> None:
        has_in: set[NodeId] = {edge.dst for edge in graph.edges}
        has_out: set[NodeId] = {edge.src for edge in graph.edges}

        for floor, nodes in graph.nodes_by_floor.items():
            if floor == 0 or floor == max(graph.nodes_by_floor):
                continue
            graph.nodes_by_floor[floor] = [
                node for node in nodes if node.id in has_in or node.id in has_out
            ]

    def _saturate_connectivity(self, graph: MapGraph, rng: random.Random) -> None:
        out_degree: defaultdict[NodeId, int] = defaultdict(int)
        in_degree: defaultdict[NodeId, int] = defaultdict(int)
        edge_set = {(edge.src, edge.dst) for edge in graph.edges}
        for edge in graph.edges:
            out_degree[edge.src] += 1
            in_degree[edge.dst] += 1

        max_floor = max(graph.nodes_by_floor)
        for floor in range(max_floor):
            current_nodes = list(graph.nodes_by_floor[floor])
            next_nodes = list(graph.nodes_by_floor[floor + 1])
            rng.shuffle(current_nodes)
            rng.shuffle(next_nodes)

            for node in current_nodes:
                if out_degree[node.id] > 0:
                    continue
                candidates = [n.id for n in next_nodes if self.can_connect(node.id, n.id)]
                candidates.sort(key=lambda nid: (in_degree[nid], abs(nid.x - node.id.x)))
                for candidate in candidates:
                    edge = Edge(src=node.id, dst=candidate)
                    if (edge.src, edge.dst) in edge_set:
                        continue
                    if out_degree[edge.src] >= 2 or in_degree[edge.dst] >= 2:
                        continue
                    if self.would_intersect(graph.edges, edge):
                        continue
                    graph.edges.append(edge)
                    edge_set.add((edge.src, edge.dst))
                    out_degree[edge.src] += 1
                    in_degree[edge.dst] += 1
                    break

    def _compute_x_positions(self, count: int, max_nodes_per_floor: int) -> list[int]:
        if count <= 1:
            return [0]

        span = max(1, max_nodes_per_floor - 1)
        values = [round(i * span / (count - 1)) for i in range(count)]

        # Ensure uniqueness and stable ordering if rounding collides.
        deduped: list[int] = []
        seen: set[int] = set()
        for value in values:
            if value not in seen:
                seen.add(value)
                deduped.append(value)

        candidate = 0
        while len(deduped) < count:
            if candidate not in seen:
                deduped.append(candidate)
                seen.add(candidate)
            candidate += 1

        return sorted(deduped)
