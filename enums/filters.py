from enum import Enum

class PlayerFilters(Enum):
    NAME = "name"
    QUALITY = "quality"
    POSITON = "position"
    CHEM = "chem"
    NATION = "nation"
    LEAGUE = "league"
    CLUB = "club"
    MAX_BIN = "maxBIN"


class ConsumablesFilters(Enum):
    QUALITY = "quality"
    CONSUMABLE_NAME = "name"
    MAX_BIN = "maxBIN"
