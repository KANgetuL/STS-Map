from __future__ import annotations

import random
from collections.abc import Mapping

from sts_map.config.schema import RandomRoomDynamicWeight
from sts_map.domain.enums import RoomType
from sts_map.domain.state import RandomResolveResult, RandomRoomState


class RandomRoomResolver:
    def resolve(
        self,
        state: RandomRoomState,
        dyn: RandomRoomDynamicWeight,
        rng_seed: int,
    ) -> RandomResolveResult:
        rng = random.Random(rng_seed)
        weights = self.compute_current_weights(state, dyn)

        population: list[RoomType] = []
        values: list[float] = []
        for room_type, weight in weights.items():
            if weight > 0:
                population.append(room_type)
                values.append(weight)

        if not population:
            resolved = RoomType.EVENT
        else:
            resolved = rng.choices(population, weights=values, k=1)[0]

        if resolved == RoomType.EVENT:
            next_state = self.on_event_hit(state, dyn)
        else:
            next_state = self.on_special_hit(state)

        return RandomResolveResult(resolved_type=resolved, next_state=next_state)

    def compute_current_weights(
        self,
        state: RandomRoomState,
        dyn: RandomRoomDynamicWeight,
    ) -> Mapping[RoomType, float]:
        event_weight = max(0.0, dyn.event_base + state.pity_event)
        fight_weight = max(0.0, dyn.fight_base + state.pity_fight)
        treasure_weight = max(0.0, dyn.treasure_base + state.pity_treasure)
        shop_weight = max(0.0, dyn.shop_base + state.pity_shop)

        # Elite can be introduced by future act-specific tuning; default weight is zero.
        return {
            RoomType.EVENT: event_weight,
            RoomType.MONSTER: fight_weight,
            RoomType.TREASURE: treasure_weight,
            RoomType.SHOP: shop_weight,
            RoomType.ELITE: 0.0,
        }

    def on_event_hit(self, state: RandomRoomState, dyn: RandomRoomDynamicWeight) -> RandomRoomState:
        special_sum = dyn.fight_base + dyn.treasure_base + dyn.shop_base
        return RandomRoomState(
            pity_fight=state.pity_fight + dyn.fight_base,
            pity_treasure=state.pity_treasure + dyn.treasure_base,
            pity_shop=state.pity_shop + dyn.shop_base,
            pity_event=state.pity_event - special_sum,
        )

    def on_special_hit(self, state: RandomRoomState) -> RandomRoomState:
        _ = state
        return RandomRoomState()
