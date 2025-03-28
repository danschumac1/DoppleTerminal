import os
import asyncio
from prompt_toolkit.shortcuts import PromptSession, print_formatted_text
from prompt_toolkit.formatted_text import ANSI

from utils.asthetics import (
    format_gm_message, get_color_for_code_name, print_color, clear_screen)
from utils.logging_utils import MasterLogger, StandAloneLogger
from utils.states import GameState, ScreenState, PlayerState
from utils.constants import DEBUG_PS
from utils.chatbot.ai import AIPlayer

from utils.file_io import (
    append_message, read_new_messages, init_chat_log, 
    save_player_to_lobby_file, load_players_from_lobby
)

async def refresh_messages_loop(
    chat_log_path: str, gs: GameState, ps: 
    PlayerState, delay: float = 0.5) -> None:
    """
    Continuously refreshes messages by reading the chat log file and printing new messages.

    Args:
        chat_log_path (str): Path to the chat log file.
        gs (GameState): Current game state object.
        ps (PlayerState): Player state object.
        delay (float): Delay between refreshes.
    """
    last_line = 0  # Tracks the last read line number
    while True:
        await asyncio.sleep(delay)  # Pause to prevent busy looping
        new_msgs, last_line = read_new_messages(chat_log_path, last_line)

        # If there are new messages, update the game state and print them
        if new_msgs:
            gs.players = load_players_from_lobby(ps.lobby_id)
            formatted_msgs = []

            for msg in new_msgs:
                if "GAME MASTER" in msg or "*****" in msg:
                    formatted_msgs.append(print_color(msg, "YELLOW", print_or_return="return"))
                else:
                    # Extract the code name and print the message with the corresponding color
                    code_name = msg.split(":", 1)[0]
                    try:
                        color = get_color_for_code_name(code_name, gs)
                        formatted_msgs.append(print_color(msg, color, print_or_return="return"))
                    except:
                        continue  # Ignore messages with unknown code names
            print_formatted_text(ANSI("\n".join(formatted_msgs)))

async def ai_loop(
    chat_log_path: str, ps: PlayerState, master_logger: 
    MasterLogger, sa_logger: StandAloneLogger, delay: float = 0.25) -> None:
    """
    Manages the AI response loop, ensuring the AI does not respond to its own message repeatedly.

    Args:
        chat_log_path (str): Path to the chat log file.
        ps (PlayerState): Player state object (including AI data).
        master_logger (MasterLogger): Central logging instance.
        sa_logger (StandAloneLogger): Player-specific logging instance.
        delay (float): Delay between AI response checks.
    """
    last_message_count = 0  # Tracks the number of messages seen by the AI
    ai_code_name = ps.ai_doppleganger.player_state.code_name

    while True:
        new_messages, new_message_count = read_new_messages(chat_log_path, last_message_count)

        if new_messages:
            full_log, _ = read_new_messages(chat_log_path, 0)

            # Prevent AI from responding to its own latest message
            last_line = full_log[-1] if full_log else ""
            if last_line.startswith(f"{ai_code_name}:"):
                await asyncio.sleep(delay)
                last_message_count = new_message_count
                continue

            # Generate a response from the AI if the message is not self-generated
            ai_response = ps.ai_doppleganger.decide_to_respond(full_log)

            if ai_response and not ai_response.startswith("Wait for"):
                ai_msg = f"{ai_code_name}: {ai_response}"
                append_message(chat_log_path, ai_msg)
                master_logger.log(f"[AI] {ai_code_name} responded: {ai_response}")
                sa_logger.info(f"[AI] {ai_code_name} responded: {ai_response}")

            last_message_count = new_message_count

        await asyncio.sleep(delay)

async def user_input_loop(
        session: PromptSession, chat_log_path: str, ps: PlayerState, 
        master_logger: MasterLogger, sa_logger: StandAloneLogger) -> None:
    """
    Continuously prompts the user for input and logs the messages.

    Args:
        session (PromptSession): The interactive session for user input.
        chat_log_path (str): Path to the chat log file.
        ps (PlayerState): Player state object.
        master_logger (MasterLogger): Central logging instance.
        sa_logger (StandAloneLogger): Player-specific logging instance.
    """
    while True:
        user_input = await session.prompt_async(ANSI(f"{ps.color}{ps.code_name}\x1b[0m: "))

        if user_input.strip().lower() == "exit":
            print_formatted_text(ANSI(format_gm_message("Game exited early.")))
            raise asyncio.CancelledError

        player_msg = f"{ps.code_name}: {user_input}"
        append_message(chat_log_path, player_msg)
        master_logger.log(f"[User] {ps.code_name} sent: {user_input}")
        sa_logger.info(f"[User] {ps.code_name} sent: {user_input}")

async def play_game(
        ss: ScreenState, gs: GameState, ps: PlayerState = None) \
            -> tuple[ScreenState, GameState, PlayerState]:
    """
    Main game loop that handles AI, user input, and message management.

    Args:
        ss (ScreenState): Current screen state.
        gs (GameState): Current game state.
        ps (PlayerState): Player state object.

    Returns:
        tuple: Updated screen state, game state, and player state.
    """
    # Fallback for missing player state
    if ps is None or ps.code_name == "":
        print_color("AUTO DEBUG MODE ENABLED — using fallback player.", "RED")
        ps = DEBUG_PS

    session = PromptSession()
    master_logger = MasterLogger.get_instance()
    clear_logger = not ps.written_to_file
    init_logger = clear_logger

    # Set up player-specific logger
    sa_logger = StandAloneLogger(
        log_path=f"./data/runtime/lobbies/lobby_{ps.lobby_id}/{ps.code_name}_game_log.log",
        clear=clear_logger,
        init=init_logger
    )

    # Save player state if new
    if not ps.written_to_file:
        clear_screen()
        ps.written_to_file = True
        save_player_to_lobby_file(ps)
        master_logger.log(f"Player {ps.code_name} saved to lobby file.")

    # Initialize chat log and game setup
    chat_log_path = f"./data/runtime/lobbies/lobby_{ps.lobby_id}/chat_log.txt"
    if not os.path.exists(chat_log_path):
        init_chat_log(chat_log_path)
        append_message(
            chat_log_path, 
            format_gm_message("Welcome to Dopplebot! Everyone, please introduce yourselves."))
        master_logger.log("Initialized chat log and added intro message.")

    # Start background message refresher
    refresh_task = asyncio.create_task(refresh_messages_loop(chat_log_path, gs, ps))

    try:
        await asyncio.gather(
            ai_loop(chat_log_path, ps, master_logger, sa_logger),
            user_input_loop(session, chat_log_path, ps, master_logger, sa_logger)
        )
    except asyncio.CancelledError:
        pass
    finally:
        refresh_task.cancel()
        await asyncio.sleep(0.1)

    return ScreenState.SCORE, gs, ps