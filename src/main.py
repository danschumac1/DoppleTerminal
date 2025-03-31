import asyncio
from utils.states import ScreenState
from setup import collect_player_data
from intro_screen import play_intro
from game import play_game
from score import score_screen
import inspect
# import signal

# our functions
from utils.constants import BLANK_GS, BLANK_PS
from utils.logging_utils import MasterLogger

# async def shutdown(signal, loop):
#     print(f"\nReceived exit signal {signal.name}...")
#     tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

#     print(f"Cancelling {len(tasks)} outstanding tasks...")
#     for task in tasks:
#         task.cancel()

#     try:
#         await asyncio.gather(*tasks, return_exceptions=True)
#     except asyncio.CancelledError:
#         print("Tasks cancelled.")
#     finally:
#         print("Closing OpenAI client...")
#         try:
#             from utils.file_io import OpenAIClientManager
#             OpenAIClientManager().close_client()
#             print("OpenAI client closed successfully.")
#         except Exception as e:
#             print(f"Error closing OpenAI client: {e}")

#         print("Shutting down gracefully.")
#         loop.stop()
#         print("Game Exited. Have a great day!")


# def setup_signal_handlers(loop):
#     # Use signal.signal for Windows compatibility
#     signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(shutdown(s, loop)))
#     signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown(s, loop)))


async def main():
    # loop = asyncio.get_running_loop()
    # setup_signal_handlers(loop)

    master_logger = MasterLogger(
        init=True,
        clear=False,
        log_path="./logs/_master.log"
    )

    state_handler = {
        ScreenState.INTRO: play_intro,
        ScreenState.SETUP: collect_player_data,
        ScreenState.CHAT: play_game,
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