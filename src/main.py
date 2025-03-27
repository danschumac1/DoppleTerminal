import asyncio
from utils.states import ScreenState
from setup import collect_player_data
from intro_screen import play_intro
from game import play_game
from score import score_screen
from utils.constants import BLANK_GS, BLANK_PS
import inspect

async def main():


    state_handler = {
        ScreenState.INTRO: play_intro,
        ScreenState.SETUP: collect_player_data,
        ScreenState.PLAY: play_game,
        ScreenState.SCORE: score_screen
    }

    ss = ScreenState.SETUP  # or INTRO
    gs = BLANK_GS
    ps = BLANK_PS

    while True:
        if ss in state_handler:
            handler = state_handler[ss]
            if inspect.iscoroutinefunction(handler):
                next_state, next_gs, next_ps = await handler(ss, gs, ps)
            else:
                next_state, next_gs, next_ps = handler(ss, gs, ps)

            ss = next_state
            gs = next_gs
            ps = next_ps
        else:
            print("Invalid game state")
            break

if __name__ == "__main__":
    asyncio.run(main())