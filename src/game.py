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

async def refresh_messages_loop(chat_log_path: str, gs: GameState, ps: PlayerState, delay: float = 0.5):
    last_line = 0
    while True:
        await asyncio.sleep(delay)
        new_msgs, last_line = read_new_messages(chat_log_path, last_line)
        if new_msgs:
            gs.players = load_players_from_lobby(ps.lobby_id)
            formatted_msgs = []
            for msg in new_msgs:
                if "GAME MASTER" in msg or "*****" in msg:
                    formatted_msgs.append(print_color(msg, "YELLOW", print_or_return="return"))
                else:
                    code_name = msg.split(":", 1)[0]
                    try:
                        color = get_color_for_code_name(code_name, gs)
                        formatted_msgs.append(print_color(msg, color, print_or_return="return"))
                    except:
                        continue  # Ignore unknown code names for now
            print_formatted_text(ANSI("\n".join(formatted_msgs)))

async def ai_loop(chat_log_path, ps, master_logger, sa_logger, delay=0.25):
    last_message_count = 0
    ai_code_name = ps.ai_doppleganger.player_state.code_name

    while True:
        new_messages, new_message_count = read_new_messages(chat_log_path, last_message_count)

        if new_messages:
            full_log, _ = read_new_messages(chat_log_path, 0)

            last_line = full_log[-1] if full_log else ""
            if last_line.startswith(f"{ai_code_name}:"):
                # 🚫 Skip if the AI just spoke
                await asyncio.sleep(delay)
                last_message_count = new_message_count
                continue

            # ✅ AI may respond
            ai_response = ps.ai_doppleganger.decide_to_respond(full_log)

            if ai_response and not ai_response.startswith("Wait for"):
                ai_msg = f"{ai_code_name}: {ai_response}"
                append_message(chat_log_path, ai_msg)
                master_logger.log(f"[AI] {ai_code_name} responded: {ai_response}")
                sa_logger.info(f"[AI] {ai_code_name} responded: {ai_response}")

            last_message_count = new_message_count

        await asyncio.sleep(delay)



async def user_input_loop(session, chat_log_path, ps, master_logger, sa_logger):
    while True:
        user_input = await session.prompt_async(
            ANSI(f"{ps.color}{ps.code_name}\x1b[0m: ")
        )

        if user_input.strip().lower() == "exit":
            print_formatted_text(ANSI(format_gm_message("Game exited early.")))
            raise asyncio.CancelledError  # Exit all loops

        player_msg = f"{ps.code_name}: {user_input}"
        append_message(chat_log_path, player_msg)
        master_logger.log(f"[User] {ps.code_name} sent: {user_input}")
        sa_logger.info(f"[User] {ps.code_name} sent: {user_input}")


async def play_game(
        ss: ScreenState, gs: GameState, ps: PlayerState = None) \
        -> tuple[ScreenState, GameState, PlayerState]:
    
    # --- Debug fallback ---
    if ps is None or ps.code_name == "":
        print_color("AUTO DEBUG MODE ENABLED — using fallback player.", "RED")
        ps = DEBUG_PS

    session = PromptSession()
    master_logger = MasterLogger.get_instance()
    if not ps.written_to_file:
        clear_logger = True
        init_logger = True
        clear_screen()
        ps.written_to_file = True
        save_player_to_lobby_file(ps)
        master_logger.log(f"Player {ps.code_name} saved to lobby file.")
    else:
        clear_logger = False
        init_logger = False

    sa_logger = StandAloneLogger(
        log_path=f"./data/runtime/lobbies/lobby_{ps.lobby_id}/{ps.code_name}_game_log.log",
        clear=clear_logger,
        init=init_logger
)



    # --- Load all players so far ---
    active_players = load_players_from_lobby(ps.lobby_id)

    # --- Make sure local player is in memory ---
    if ps.code_name not in [p.code_name for p in gs.players]:
        gs.players.append(ps)

    # --- Assign AI if needed ---
    if ps.ai_doppleganger is None:
        ps.ai_doppleganger = AIPlayer(
            player_to_steal=ps,
            players_code_names=[p.code_name for p in gs.players]
        )
        ai_ps = ps.ai_doppleganger.player_state
        ai_ps.written_to_file = True

        if ai_ps.code_name not in [p.code_name for p in active_players]:
            save_player_to_lobby_file(ai_ps)

        gs.players.append(ai_ps)
        master_logger.log(f"AI player {ai_ps.code_name} created and added to the game.")

    # --- Reload if needed ---
    if active_players != gs.players:
        gs.players = load_players_from_lobby(ps.lobby_id)
        ps.ai_doppleganger.players_code_names = [p.code_name for p in gs.players]
        ps.player_code_names = [p.code_name for p in gs.players]
        new_code_names = [
            p.code_name for p in gs.players if p.code_name not in ps.player_code_names]
        master_logger.log(
            f"New players detected: Adding {', '.join(new_code_names)} to active players.")

    # --- Setup chat log ---
    chat_log_path = f"./data/runtime/lobbies/lobby_{ps.lobby_id}/chat_log.txt"
    if not os.path.exists(chat_log_path):
        init_chat_log(chat_log_path)
        intro_msg = format_gm_message(
            "Welcome to Dopplebot! Everyone, please introduce yourselves.")
        append_message(chat_log_path, intro_msg)
        master_logger.log("Initialized chat log and added intro message.")

    # --- Start background message refresher
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
