import os
from typing import Tuple
from utils.states import GameState, ScreenState, PlayerState
from utils.file_io import SequentialAssigner
from utils.constants import (
    NAMES_PATH, NAMES_INDEX_PATH, COLORS_PATH, COLORS_INDEX_PATH, COLOR_DICT
)
from utils.asthetics import print_color


class PlayerSetup:
    def __init__(
        self,
        names_path=NAMES_PATH,
        names_index_path=NAMES_INDEX_PATH,
        colors_path=COLORS_PATH,
        colors_index_path=COLORS_INDEX_PATH
    ):
        self.data = {}
        self.code_name_assigner = SequentialAssigner(names_path, names_index_path)
        self.color_assigner = SequentialAssigner(colors_path, colors_index_path)

    def assign_code_name(self) -> str:
        return self.code_name_assigner.assign()

    def assign_color(self) -> str:
        return self.color_assigner.assign()

    def prompt_not_empty(self, field_name, prompt):
        while True:
            value = input(prompt).strip()
            if value:
                self.data[field_name] = value
                return
            print_color(f"{field_name} cannot be empty.", "RED")

    def prompt_initial(self):
        while True:
            value = input("Enter your last initial (A–Z): ").strip()
            if len(value) == 1 and value.isalpha():
                self.data["last_initial"] = value.upper()
                return
            print_color("Last initial must be a single letter (A–Z).", "RED")

    def prompt_number(self, lower, upper, field_name):
        while True:
            try:
                value = int(input(f"What {field_name} are you in? ({lower} - {upper}): "))
                if lower <= value <= upper:
                    self.data[field_name] = str(value)
                    return
                print_color(f"{field_name} must be between {lower} and {upper}.", "RED")
            except ValueError:
                print_color("Please enter a valid number.", "RED")

    def run(self) -> Tuple[PlayerState, ScreenState]:
        print_color("=== Player Setup ===", "CYAN")
        self.prompt_number(lower=1, upper=10000, field_name="lobby")
        self.prompt_not_empty("first_name", "Enter your first name: ")
        self.prompt_initial()
        self.prompt_number(lower=6, upper=8, field_name="grade")
        self.prompt_not_empty("favorite_food", "Favorite food: ")
        self.prompt_not_empty("favorite_animal", "Favorite animal: ")
        self.prompt_not_empty("hobby", "What's your hobby? ")
        self.prompt_not_empty("extra_info", "Tell us one more thing about you: ")

        self.data["lobby_id"] = "default_lobby"
        self.data["game_id"] = "default_game"
        picked_color = self.assign_color()

        ps = PlayerState(
            lobby_id=self.data["lobby"],
            first_name=self.data["first_name"],
            last_initial=self.data["last_initial"],
            grade=self.data["grade"],
            code_name=self.assign_code_name(),
            favorite_food=self.data["favorite_food"],
            favorite_animal=self.data["favorite_animal"],
            hobby=self.data["hobby"],
            extra_info=self.data["extra_info"],
            color_name=picked_color,
            color=COLOR_DICT[picked_color],
        )

        return ps, ScreenState.PLAY


def collect_player_data(
        ss: ScreenState,
        gs: GameState,
        ps: PlayerState,
        ) -> Tuple[ScreenState, GameState, PlayerState]:

    setup = PlayerSetup()
    ps, next_state = setup.run()
    gs.players.append(ps)

    input("Press Enter to continue...")
    return next_state, gs, ps
