from __future__ import annotations

from enum import Enum


class ActId(str, Enum):
    ACT1 = "act1"
    ACT2 = "act2"
    ACT3 = "act3"
    ACT4 = "act4"


class RoomType(str, Enum):
    MONSTER = "monster"
    ELITE = "elite"
    EVENT = "event"
    QUESTION = "question"
    SHOP = "shop"
    REST = "rest"
    TREASURE = "treasure"
    BOSS = "boss"
    SPECIAL_ELITE = "special_elite"
