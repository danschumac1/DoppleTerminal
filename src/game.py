import os
from prompt_toolkit.shortcuts import PromptSession, print_formatted_text
from prompt_toolkit.formatted_text import ANSI

from utils.asthetics import format_gm_message, print_color, clear_screen
from utils.states import GameState, ScreenState, PlayerState
from utils.constants import DEBUG_PS
from utils.chatbot.ai import AIPlayer
import asyncio

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

def get_color_for_code_name(code_name: str, gs: GameState) -> str:
    for player in gs.players:
        if player.code_name == code_name:
            return player.color_name
    raise ValueError(f"Unknown code_name in chat: '{code_name}'")

async def play_game(ss: ScreenState, gs: GameState, ps: PlayerState = None) -> tuple[ScreenState, GameState, PlayerState]:
    session = PromptSession()

    # --- Debug fallback ---
    if ps is None or ps.code_name == "":
        print_color("AUTO DEBUG MODE ENABLED — using fallback player.", "RED")
        ps = DEBUG_PS

    # --- Save the player if needed ---
    if not ps.written_to_file:
        clear_screen()
        ps.written_to_file = True
        save_player_to_lobby_file(ps)

    # --- Load all players so far ---
    new_load = load_players_from_lobby(ps.lobby_id)

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

        # ✅ Now it's safe to check if it's already saved
        if ai_ps.code_name not in [p.code_name for p in new_load]:
            save_player_to_lobby_file(ai_ps)

        gs.players.append(ai_ps)

    # --- Reload if needed ---
    if new_load != gs.players:
        gs.players = load_players_from_lobby(ps.lobby_id)
        ps.ai_doppleganger.players_code_names = [p.code_name for p in gs.players]
        ps.player_code_names = [p.code_name for p in gs.players]


    # --- Setup chat log ---
    chat_log_path = f"./data/runtime/lobbies/lobby_{ps.lobby_id}/chat_log.txt"
    if not os.path.exists(chat_log_path):
        init_chat_log(chat_log_path)
        intro_msg = format_gm_message("Welcome to Dopplebot! Everyone, please introduce yourselves.")
        append_message(chat_log_path, intro_msg)

    last_line = 0

    # --- Start background message refresher
    refresh_task = asyncio.create_task(refresh_messages_loop(chat_log_path, gs, ps))

    try:
        while True:
            try:
                user_input = await session.prompt_async(
                    ANSI(f"{ps.color}{ps.code_name}\x1b[0m: ")
                )
            except KeyboardInterrupt:
                print_formatted_text(ANSI(format_gm_message("You exited the game.")))
                break

            if user_input.strip().lower() == "exit":
                print_formatted_text(ANSI(format_gm_message("Game exited early.")))
                break

            # Save player message
            player_msg = f"{ps.code_name}: {user_input}"
            append_message(chat_log_path, player_msg)

            # Let AI respond
            ai_response = ps.ai_doppleganger.decide_to_respond([player_msg])
            if ai_response and not ai_response.startswith("Wait for"):
                ai_msg = f"{ps.ai_doppleganger.player_state.code_name}: {ai_response}"
                append_message(chat_log_path, ai_msg)

    finally:
        refresh_task.cancel()
        await asyncio.sleep(0.1)  # Let the task fully cancel


    return ScreenState.SCORE, gs, ps