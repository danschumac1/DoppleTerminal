import asyncio
import inspect
from utils.states import ScreenState
from setup import collect_player_data
from intro_screen import play_intro
from game import play_game
from score import score_screen

# Importing constants and logging
from utils.constants import BLANK_GS, BLANK_PS
from utils.logging_utils import MasterLogger

async def main() -> None:
    """
    Main entry point for the social deduction game.

    Initializes the logging system, sets up state handlers, and manages the game loop.

    Uses asyncio to handle asynchronous game states and allows switching between:
        - Intro screen
        - Player setup
        - Main game loop
        - Scoring screen

    Returns:
        None
    """
    # Initialize the master logger to keep track of game events.
    master_logger = MasterLogger(
        init=True,
        clear=False,
        log_path="./logs/_master.log"
    )
    master_logger.log("Game started - Initializing master logger")

    # Dictionary mapping game states to their corresponding handler functions.
    state_handler = {
        ScreenState.INTRO: play_intro,
        ScreenState.SETUP: collect_player_data,
        ScreenState.PLAY: play_game,
        ScreenState.SCORE: score_screen
    }

    # Initialize the starting screen state and blank game/player states.
    ss = ScreenState.SETUP  # Can also start with ScreenState.INTRO
    gs = BLANK_GS
    ps = BLANK_PS

    # Main game loop
    while True:
        # Check if the current screen state has a handler function.
        if ss in state_handler:
            handler = state_handler[ss]
            
            # Determine if the handler is an asynchronous coroutine.
            if inspect.iscoroutinefunction(handler):
                next_state, next_gs, next_ps = await handler(ss, gs, ps)
            else:
                next_state, next_gs, next_ps = handler(ss, gs, ps)
            
            # Update state variables with the results from the handler.
            ss = next_state
            gs = next_gs
            ps = next_ps
            
            # Log the state transition for debugging and tracking.
            master_logger.log(f"Transitioned to state: {ss}")
        else:
            # Handle unexpected or invalid states.
            master_logger.error(f"Invalid game state encountered: {ss}")
            print("Invalid game state")
            break

if __name__ == "__main__":
    # Run the main game loop using asyncio for asynchronous operations.
    asyncio.run(main())
