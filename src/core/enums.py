"""Enumerations for decisions, stances, terrain, origins."""
from enum import Enum, auto

class DecisionType(Enum):
    COMMAND = auto()
    SOVIET_VOTE = auto()
    HIGHER_ORDER = auto()

class UnitStance(Enum):
    ASSAULT = auto()
    DEFEND = auto()
    FLANK_LEFT = auto()
    FLANK_RIGHT = auto()
    AMBUSH = auto()
    RETREAT = auto()
    LEAD_FROM_FRONT = auto()

class TerrainType(Enum):
    PLAINS = auto()
    FOREST = auto()
    HILLS = auto()
    MOUNTAINS = auto()
    RIVER = auto()
    VILLAGE = auto()

class Origin(Enum):
    PEASANT = "peasant"
    INTELLECTUAL = "intellectual"
    WORKER = "worker"
    FOREIGN_EDUCATED = "foreign_educated"

class PrologueChoice(Enum):
    WRITING_POETRY = "writing_poetry"
    PHYSICAL_TRAINING = "physical_training"
    STUDYING_MAPS = "studying_maps"
    OPIUM = "opium"

