from utils.states import GameState, PlayerState

COLOR_DICT = {
    "RED": "\x1b[31m",
    "GREEN": "\x1b[32m",
    "YELLOW": "\x1b[33m",
    "BLUE": "\x1b[34m",
    "MAGENTA": "\x1b[35m",
    "CYAN": "\x1b[36m"
}

NAMES_PATH="./data/runtime/possible_code_names.txt"
NAMES_INDEX_PATH="./data/runtime/code_names_index.txt"
COLORS_PATH="./data/runtime/possible_colors.txt"
COLORS_INDEX_PATH="./data/runtime/colors_index.txt"

BLANK_PS = PlayerState(
    lobby_id="",
    first_name="",
    last_initial="",
    code_name="",
    grade="",
    favorite_food="",
    favorite_animal="",
    hobby="",
    extra_info="",
    color_name="",
    color=""
)

DEBUG_PS = PlayerState(
    lobby_id="1",
    first_name="Dan",
    last_initial="S",
    code_name="DebugBot",
    grade="8",
    favorite_food="Pizza",
    favorite_animal="Dog",
    hobby="Coding",
    extra_info="Just a debug bot.",
    color_name="CYAN",
    color="\x1b[36m",
    ai_doppleganger=None 
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