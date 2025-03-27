from dataclasses import asdict
import json
import os
from typing import List, Tuple
from time import sleep

from utils.states import PlayerState

def init_chat_log(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("")  # Start fresh

def append_message(path:str, message: str):
    with open(path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def read_new_messages(path, last_line: int) -> Tuple[List[str], int]:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = lines[last_line:]
    return [line.strip() for line in new_lines], len(lines)

class SequentialAssigner:
    def __init__(self, list_path: str, index_path: str):
        self.list_path = list_path
        self.index_path = index_path
        self.items = self._load_items()

    def _load_items(self) -> List[str]:
        if not os.path.exists(self.list_path):
            raise FileNotFoundError(f"Missing data file: {self.list_path}")

        with open(self.list_path, "r") as f:
            items = [line.strip() for line in f if line.strip()]

        if not items:
            raise ValueError(f"List at {self.list_path} is empty.")

        return items

    def assign(self) -> str:
        idx = 0
        if os.path.exists(self.index_path):
            with open(self.index_path, "r") as f:
                try:
                    idx = int(f.read().strip())
                except ValueError:
                    idx = 0

        if idx >= len(self.items):
            idx = 0

        selected_item = self.items[idx]
        next_idx = (idx + 1) % len(self.items)

        with open(self.index_path, "w") as f:
            f.write(str(next_idx))

        return selected_item
    
def save_player_to_lobby_file(ps: PlayerState) -> None:
    """
    Save a player to the shared players.json for their lobby.
    """
    lobby_path = f"./data/runtime/lobbies/lobby_{ps.lobby_id}"
    os.makedirs(lobby_path, exist_ok=True)
    file_path = os.path.join(lobby_path, "players.json")

    players = []

    # Load existing players if file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                players = json.load(f)
            except json.JSONDecodeError:
                pass  # start fresh if it's corrupt or empty

    # Avoid duplicates by code_name
    if not any(p["code_name"] == ps.code_name for p in players):
        players.append(asdict(ps))

    # Save updated list
    with open(file_path, "w") as f:
        json.dump(players, f, indent=2)

def load_players_from_lobby(lobby_id: str) -> list[PlayerState]:
    file_path = f"./data/runtime/lobbies/lobby_{lobby_id}/players.json"
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as f:
        data = json.load(f)
        return [PlayerState(**p) for p in data]
