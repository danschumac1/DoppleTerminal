from colorama import Fore
from utils.states import GameState, PlayerState

COLOR_DICT = {
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "BLUE": Fore.BLUE,
    "MAGENTA": Fore.MAGENTA,
    "CYAN": Fore.CYAN,
}
NAMES_PATH="./data/runtime/possible_code_names.txt"
NAMES_INDEX_PATH="./runtime/data/code_names_index.txt"
COLORS_PATH="./data/runtime/possible_colors.txt"
COLORS_INDEX_PATH="./data/runtime/colors_index.txt"

BLANK_PS = PlayerState(
    first_name="",
    last_initial="",
    code_name="",
    grade="",
    lobby_id="",
    game_id="",
    favorite_food="",
    favorite_animal="",
    hobby="",
    extra_info="",
    color_name="",
    color=""
)

BLANK_GS = GameState(
    round_number=0,
    players=[],
    players_voted_off=[],
    last_vote_outcome="",
    textual_summary="",
    chat_this_round=[],
    all_chat=[]
)