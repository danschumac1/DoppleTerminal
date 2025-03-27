from utils.states import ScreenState
from setup import collect_player_data
from intro_screen import play_intro
from game import play_game
from score import score_screen
from utils.constants import BLANK_GS, BLANK_PS

def main():
    """
    The main function initializes the game window and runs the game loop.
    """
    state_handler = {
        ScreenState.INTRO: play_intro,
        ScreenState.SETUP: collect_player_data,
        ScreenState.PLAY: play_game,
        ScreenState.SCORE: score_screen
    }

    ss = ScreenState.SETUP # TODO Change to ScreenState.INTRO
    ps = BLANK_PS
    gs = BLANK_GS

    while True:
        if ss in state_handler:
            next_state, next_ps, next_gs = state_handler[ss](ss, ps, gs)
            if next_ps != ps:
                ps = next_ps  # Keep the most recent persona
            if next_gs != gs:
                gs = next_gs
            if next_state != ss:
                ss = next_state
        else:
            print("Invalid game state")
            break

if __name__ == "__main__":
    main()