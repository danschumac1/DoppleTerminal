from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
import json
import os
from typing import List, Optional

class ScreenState(Enum):
    INTRO = 0
    SETUP = 1
    PLAY = 2
    SCORE = 3

@dataclass
class PlayerState:
    lobby_id: str
    first_name: str
    last_initial: str
    code_name: str
    grade: str
    favorite_food: str
    favorite_animal: str
    hobby: str
    extra_info: str
    color_name: str     
    color: str          
    ai_doppleganger: Optional[AIPlayer] = None # type: ignore
    written_to_file: bool = False # Flag to indicate if the player has been written to a file

    def to_json_file(self):
        # Extract first name and last initial safely
        try:
            first_name = self.first_name.capitalize()
            last_initial = self.last_initial.capitalize()
        except ValueError:
            raise ValueError("Error in name parsing enums_dcs.py @ to_json_file")
        
        path = os.path.join("data", f"{first_name}{last_initial}_{self.grade}_player_info.json")
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

@dataclass
class GameState:
    round_number: int
    players: list                   #TODO determine typing of list
    players_voted_off: List[str]    # List of players voted off
    last_vote_outcome: str          # The outcome of the last vote