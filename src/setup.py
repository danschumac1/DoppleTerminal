import os
from typing import Tuple
from colorama import Fore, Style
from utils.chatbot.ai import AIPlayer
from utils.states import GameState, ScreenState, PlayerState
from utils.sequential_assigner import SequentialAssigner
from utils.constants import NAMES_PATH, NAMES_INDEX_PATH, COLORS_PATH, COLORS_INDEX_PATH, COLOR_DICT


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
            print(Fore.RED + f"{field_name} cannot be empty.")

    def prompt_grade(self, lower=6, upper=8):
        while True:
            try:
                value = int(input(f"What grade are you in? ({lower} - {upper}): "))
                if lower <= value <= upper:
                    self.data["grade"] = str(value)
                    return
                print(f"Grade must be between {lower} and {upper}.")
            except ValueError:
                print("Please enter a valid number.")


    def run(self) -> Tuple[PlayerState, ScreenState]:
        print(Fore.CYAN + Style.BRIGHT + "\n=== Player Setup ===\n")

        self.prompt_not_empty("first_name", "Enter your first name: ")
        self.prompt_not_empty("last_initial", "Enter your last initial: ")
        self.prompt_grade()
        self.prompt_not_empty("favorite_food", "Favorite food: ")
        self.prompt_not_empty("favorite_animal", "Favorite animal: ")
        self.prompt_not_empty("hobby", "What's your hobby? ")
        self.prompt_not_empty("extra_info", "Tell us one more thing about you: ")

        # Add default lobby/game IDs for now
        self.data["lobby_id"] = "default_lobby"
        self.data["game_id"] = "default_game"
        picked_color = self.assign_color()
        ps = PlayerState(
            first_name=self.data["first_name"],
            last_initial=self.data["last_initial"],
            grade=self.data["grade"],
            code_name=self.assign_code_name(),
            lobby_id=self.data["lobby_id"],
            game_id=self.data["game_id"],
            favorite_food=self.data["favorite_food"],
            favorite_animal=self.data["favorite_animal"],
            hobby=self.data["hobby"],
            extra_info=self.data["extra_info"],
            color_name=picked_color,
            color=COLOR_DICT[picked_color]
        )

        return ScreenState.PLAY, ps

def collect_player_data(
        ss: ScreenState, 
        ps: PlayerState, 
        gs: GameState) -> Tuple[ScreenState, PlayerState, GameState]:
    
    setup = PlayerSetup()
    next_state, ps = setup.run()
    gs.players.append(ps)

    # Avoid circular import at module level
    from utils.chatbot.ai import AIPlayer

    ps.ai_doppleganger = AIPlayer(
        player_to_steal=ps,
        players_code_names=[p.code_name for p in gs.players]
    )

    input("Press Enter to continue...")
    return next_state, ps, gs


