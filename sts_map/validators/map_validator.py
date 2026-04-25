from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Sequence

from sts_map.config.schema import ActRuleConfig
from sts_map.domain.enums import ActId, RoomType
from sts_map.domain.models import Edge, GenerationInput, MapGraph, NodeId
from sts_map.domain.state import GenerationContext, ValidationIssue, ValidationReport


class MapValidator:
    _DIST_MIN_SAMPLES = 30

    def validate_all(
        self,
        graph: MapGraph,
        ctx: GenerationContext,
        cfg: ActRuleConfig,
    ) -> ValidationReport:
        issues = []
        issues.extend(self.validate_structure(graph))
        issues.extend(self.validate_room_rules(graph, cfg, ctx))
        return ValidationReport(ok=not issues, issues=tuple(issues))

    def validate_structure(self, graph: MapGraph) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not graph.nodes_by_floor:
            return [ValidationIssue(code="STRUCT_EMPTY_GRAPH", message="nodes_by_floor is empty")]

        floor_ids = sorted(graph.nodes_by_floor.keys())
        max_floor = floor_ids[-1]
        for floor in floor_ids:
            if not graph.nodes_by_floor[floor]:
                issues.append(
                    ValidationIssue(
                        code="STRUCT_EMPTY_FLOOR",
                        message=f"floor {floor} has no nodes",
                    )
                )

        for edge in graph.edges:
            if not self._can_connect(edge.src, edge.dst):
                issues.append(
                    ValidationIssue(
                        code="STRUCT_ILLEGAL_EDGE",
                        message=f"illegal edge ({edge.src.floor},{edge.src.x})->({edge.dst.floor},{edge.dst.x})",
                    )
                )

        by_floor: defaultdict[int, list[Edge]] = defaultdict(list)
        for edge in graph.edges:
            by_floor[edge.src.floor].append(edge)

        for floor, edges in by_floor.items():
            for i, e1 in enumerate(edges):
                for e2 in edges[i + 1 :]:
                    if self._intersects(e1, e2):
                        issues.append(
                            ValidationIssue(
                                code="STRUCT_EDGE_INTERSECTION",
                                message=f"intersecting edges on floor {floor}",
                            )
                        )

        if not self._has_path_to_boss(graph, max_floor):
            issues.append(
                ValidationIssue(
                    code="STRUCT_NO_BOSS_PATH",
                    message="no valid path from floor 0 to boss floor",
                )
            )

        return issues

    def validate_room_rules(
        self,
        graph: MapGraph,
        cfg: ActRuleConfig,
        ctx: GenerationContext | None = None,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        if graph.act_id == ActId.ACT4:
            # Act4 has its own fixed template and skips standard room constraints.
            return issues

        if 14 in graph.nodes_by_floor:
            for node in graph.nodes_by_floor[14]:
                if node.room_type != RoomType.REST:
                    issues.append(
                        ValidationIssue(
                            code="ROOM_FORCE_FLOOR14",
                            message="floor 14 must be rest",
                        )
                    )

        if 15 in graph.nodes_by_floor:
            for node in graph.nodes_by_floor[15]:
                if node.room_type != RoomType.BOSS:
                    issues.append(
                        ValidationIssue(
                            code="ROOM_FORCE_FLOOR15",
                            message="floor 15 must be boss",
                        )
                    )

        if self._count_room_type(graph, RoomType.SHOP) < cfg.min_shop_count:
            issues.append(
                ValidationIssue(
                    code="ROOM_MIN_SHOP",
                    message=f"shop count below minimum {cfg.min_shop_count}",
                )
            )

        elite_like = self._count_room_type(graph, RoomType.ELITE) + self._count_room_type(
            graph, RoomType.SPECIAL_ELITE
        )
        if elite_like < cfg.min_elite_count:
            issues.append(
                ValidationIssue(
                    code="ROOM_MIN_ELITE",
                    message=f"elite count below minimum {cfg.min_elite_count}",
                )
            )

        for floor in (1, 2, 3):
            for node in graph.nodes_by_floor.get(floor, []):
                if node.room_type == RoomType.ELITE:
                    issues.append(
                        ValidationIssue(
                            code="ROOM_BLACKLIST_ELITE",
                            message=f"elite not allowed on floor {floor}",
                        )
                    )

        for floor in (1, 2, 3, 4, 5, 13):
            for node in graph.nodes_by_floor.get(floor, []):
                if node.room_type == RoomType.REST:
                    issues.append(
                        ValidationIssue(
                            code="ROOM_BLACKLIST_REST",
                            message=f"rest not allowed on floor {floor}",
                        )
                    )

        node_index = {node.id: node for nodes in graph.nodes_by_floor.values() for node in nodes}
        special = {RoomType.REST, RoomType.ELITE, RoomType.SHOP}
        for edge in graph.edges:
            src = node_index.get(edge.src)
            dst = node_index.get(edge.dst)
            if src is None or dst is None or src.room_type is None or dst.room_type is None:
                continue
            if dst.id.floor in (14, 15):
                continue
            if src.room_type in special and dst.room_type == src.room_type:
                issues.append(
                    ValidationIssue(
                        code="ROOM_CONSECUTIVE_SPECIAL",
                        message=f"consecutive special room type {src.room_type.value} on edge {src.id.floor}->{dst.id.floor}",
                    )
                )

        _ = ctx
        return issues

    def validate_distribution(self, samples: Sequence[MapGraph]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not samples:
            return [ValidationIssue(code="DIST_EMPTY_SAMPLES", message="distribution samples are empty")]

        if len(samples) < self._DIST_MIN_SAMPLES:
            issues.append(
                ValidationIssue(
                    code="DIST_LOW_SAMPLE_COUNT",
                    message=f"sample count {len(samples)} is below recommended minimum {self._DIST_MIN_SAMPLES}",
                )
            )

        invalid_structure = 0
        room_counter: defaultdict[RoomType, int] = defaultdict(int)
        total_rooms = 0

        for sample in samples:
            if self.validate_structure(sample):
                invalid_structure += 1

            for nodes in sample.nodes_by_floor.values():
                for node in nodes:
                    if node.room_type is None:
                        continue
                    room_counter[node.room_type] += 1
                    total_rooms += 1

        if invalid_structure > 0:
            issues.append(
                ValidationIssue(
                    code="DIST_INVALID_STRUCTURE_FOUND",
                    message=f"{invalid_structure} samples failed structural validation",
                )
            )

        if total_rooms == 0:
            issues.append(
                ValidationIssue(
                    code="DIST_NO_ROOM_DATA",
                    message="no room data found in samples",
                )
            )
            return issues

        monster_ratio = room_counter[RoomType.MONSTER] / total_rooms
        elite_like_ratio = (
            room_counter[RoomType.ELITE] + room_counter[RoomType.SPECIAL_ELITE]
        ) / total_rooms
        shop_ratio = room_counter[RoomType.SHOP] / total_rooms
        question_ratio = room_counter[RoomType.QUESTION] / total_rooms

        if not (0.20 <= monster_ratio <= 0.80):
            issues.append(
                ValidationIssue(
                    code="DIST_MONSTER_RATIO",
                    message=f"monster ratio out of range: {monster_ratio:.3f}",
                )
            )

        if not (0.02 <= elite_like_ratio <= 0.40):
            issues.append(
                ValidationIssue(
                    code="DIST_ELITE_RATIO",
                    message=f"elite-like ratio out of range: {elite_like_ratio:.3f}",
                )
            )

        if not (0.01 <= shop_ratio <= 0.25):
            issues.append(
                ValidationIssue(
                    code="DIST_SHOP_RATIO",
                    message=f"shop ratio out of range: {shop_ratio:.3f}",
                )
            )

        if not (0.05 <= question_ratio <= 0.60):
            issues.append(
                ValidationIssue(
                    code="DIST_QUESTION_RATIO",
                    message=f"question ratio out of range: {question_ratio:.3f}",
                )
            )

        return issues

    def validate_reproducibility(self, input_data: GenerationInput) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if input_data.rule_version.strip() == "":
            issues.append(
                ValidationIssue(
                    code="REPRO_RULE_VERSION_EMPTY",
                    message="rule_version must be non-empty for reproducibility tracking",
                )
            )

        if input_data.ascension < 0 or input_data.ascension > 20:
            issues.append(
                ValidationIssue(
                    code="REPRO_ASCENSION_RANGE",
                    message="ascension must be between 0 and 20",
                )
            )

        return issues

    def _can_connect(self, src: NodeId, dst: NodeId) -> bool:
        return dst.floor == src.floor + 1 and abs(dst.x - src.x) <= 1

    def _intersects(self, a: Edge, b: Edge) -> bool:
        if a.src.floor != b.src.floor or a.dst.floor != b.dst.floor:
            return False
        if a.src == b.src or a.src == b.dst or a.dst == b.src or a.dst == b.dst:
            return False
        return (a.src.x - b.src.x) * (a.dst.x - b.dst.x) < 0

    def _has_path_to_boss(self, graph: MapGraph, max_floor: int) -> bool:
        adjacency: defaultdict[NodeId, list[NodeId]] = defaultdict(list)
        starts = [node.id for node in graph.nodes_by_floor.get(0, [])]
        targets = {node.id for node in graph.nodes_by_floor.get(max_floor, [])}
        for edge in graph.edges:
            adjacency[edge.src].append(edge.dst)

        queue: deque[NodeId] = deque(starts)
        seen: set[NodeId] = set(starts)

        while queue:
            node = queue.popleft()
            if node in targets:
                return True
            for nxt in adjacency.get(node, []):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)

        return False

    def _count_room_type(self, graph: MapGraph, room_type: RoomType) -> int:
        count = 0
        for nodes in graph.nodes_by_floor.values():
            count += sum(1 for node in nodes if node.room_type == room_type)
        return count
