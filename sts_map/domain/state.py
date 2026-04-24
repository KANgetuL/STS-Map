from __future__ import annotations

from dataclasses import dataclass, field

from .enums import RoomType
from .models import GenerationInput


@dataclass(slots=True)
class GenerationContext:
    rng_seed: int
    input: GenerationInput
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RandomRoomState:
    pity_fight: float = 0.0
    pity_treasure: float = 0.0
    pity_shop: float = 0.0
    pity_event: float = 0.0


@dataclass(frozen=True, slots=True)
class RandomResolveResult:
    resolved_type: RoomType
    next_state: RandomRoomState


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    ok: bool
    issues: tuple[ValidationIssue, ...]
