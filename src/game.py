from colorama import Fore, Style
from utils.states import GameState, ScreenState, PlayerState
from utils.chatbot.ai import AIPlayer


def play_game(ss: ScreenState, ps: PlayerState, gs: GameState) -> tuple[ScreenState, PlayerState, GameState]:
    """
    Handles a single step of gameplay — input + potential AI response.
    """

    if not gs.all_chat:
        intro_msg = "GAME MASTER: Welcome to Dopplebot! Let's get started.\
            Everyone, please introduce yourselves!"
        gs.all_chat.append(intro_msg)
        print(Fore.YELLOW + intro_msg + Style.RESET_ALL)

    # Get player input
    user_input = input(ps.color + f"{ps.code_name}: " + Style.RESET_ALL)

    # Exit early
    if user_input.strip().lower() == "exit":
        print(Fore.YELLOW + "GAME MASTER: Game exited early." + Style.RESET_ALL)
        return ScreenState.SCORE, ps, gs

    # Add player message
    player_msg = f"{ps.code_name}: {user_input}"
    gs.chat_this_round.append(player_msg)
    gs.all_chat.append(player_msg)

    # Let AI decide to respond
    ai_response = ps.ai_doppleganger.decide_to_respond(gs.all_chat)
    if ai_response:
        ai_msg = f"{ps.ai_doppleganger.player_state.code_name}: {ai_response}"
        print(Fore.RED + ai_msg + Style.RESET_ALL)
        gs.chat_this_round.append(ai_msg)
        gs.all_chat.append(ai_msg)

    # Add game state logic (vote, icebreaker, etc.) here later

    return ScreenState.PLAY, ps, gs
