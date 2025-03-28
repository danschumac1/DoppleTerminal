import os
from typing import Tuple
from utils.logging_utils import MasterLogger
from utils.states import GameState, ScreenState, PlayerState
from utils.file_io import SequentialAssigner
from utils.constants import (
    NAMES_PATH, NAMES_INDEX_PATH, COLORS_PATH, COLORS_INDEX_PATH, COLOR_DICT
)
from utils.asthetics import print_color

class PlayerSetup:
    """
    Handles the player setup process, including collecting player information,
    assigning a code name and color, and creating a PlayerState object.
    """

    def __init__(
        self,
        names_path: str = NAMES_PATH,
        names_index_path: str = NAMES_INDEX_PATH,
        colors_path: str = COLORS_PATH,
        colors_index_path: str = COLORS_INDEX_PATH
    ):
        """
        Initializes the PlayerSetup object with necessary paths for name and color assignment.

        Args:
            names_path (str): Path to the file containing player names.
            names_index_path (str): Path to the file tracking the current name index.
            colors_path (str): Path to the file containing color names.
            colors_index_path (str): Path to the file tracking the current color index.
        """
        self.data = {}
        self.code_name_assigner = SequentialAssigner(names_path, names_index_path)
        self.color_assigner = SequentialAssigner(colors_path, colors_index_path)

    def assign_code_name(self) -> str:
        """
        Assigns a unique code name to the player.

        Returns:
            str: A unique code name.
        """
        return self.code_name_assigner.assign()

    def assign_color(self) -> str:
        """
        Assigns a unique color to the player.

        Returns:
            str: A color name.
        """
        return self.color_assigner.assign()

    def prompt_not_empty(self, field_name: str, prompt: str) -> None:
        """
        Prompts the player for input, ensuring the field is not empty.

        Args:
            field_name (str): The field to be filled.
            prompt (str): The prompt message for the player.
        """
        while True:
            value = input(prompt).strip()
            if value:
                self.data[field_name] = value
                return
            print_color(f"{field_name} cannot be empty.", "RED")

    def prompt_initial(self) -> None:
        """
        Prompts the player for their last initial, ensuring it is a single letter (A-Z).
        """
        while True:
            value = input("Enter your last initial (A–Z): ").strip()
            if len(value) == 1 and value.isalpha():
                self.data["last_initial"] = value.upper()
                return
            print_color("Last initial must be a single letter (A–Z).", "RED")

    def prompt_number(self, lower: int, upper: int, field_name: str) -> None:
        """
        Prompts the player for a number within a specified range.

        Args:
            lower (int): The minimum allowed value.
            upper (int): The maximum allowed value.
            field_name (str): The name of the field being collected.
        """
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
        """
        Runs the player setup process, collecting all necessary player information.

        Returns:
            Tuple[PlayerState, ScreenState]: The initialized player state and the next screen state.
        """
        print_color("=== Player Setup ===", "CYAN")
        # Collect necessary player information
        self.prompt_number(lower=1, upper=10000, field_name="lobby")
        self.prompt_not_empty("first_name", "Enter your first name: ")
        self.prompt_initial()
        self.prompt_number(lower=6, upper=8, field_name="grade")
        self.prompt_not_empty("favorite_food", "Favorite food: ")
        self.prompt_not_empty("favorite_animal", "Favorite animal: ")
        self.prompt_not_empty("hobby", "What's your hobby? ")
        self.prompt_not_empty("extra_info", "Tell us one more thing about you: ")

        # Assign default lobby and game ID, and generate code name and color
        self.data["lobby_id"] = "default_lobby"
        self.data["game_id"] = "default_game"
        picked_color = self.assign_color()

        # Create the PlayerState object
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
        ps: PlayerState
) -> Tuple[ScreenState, GameState, PlayerState]:
    """
    Collects player data and initializes the PlayerState.

    Args:
        ss (ScreenState): The current screen state.
        gs (GameState): The current game state.
        ps (PlayerState): The existing player state.

    Returns:
        Tuple[ScreenState, GameState, PlayerState]: The updated screen state, game state, and player state.
    """
    master_logger = MasterLogger.get_instance()
    master_logger.log("Starting Setup screen...")

    # Initialize player setup and collect data
    setup = PlayerSetup()
    ps, next_state = setup.run()
    gs.players.append(ps)

    input("Press Enter to continue...")
    return next_state, gs, ps
