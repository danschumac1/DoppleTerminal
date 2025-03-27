# src/game_io.py

from abc import ABC, abstractmethod
from typing import List
from utils.states import PlayerState

class GameIO(ABC):
    @abstractmethod
    def get_input(self, ps: PlayerState) -> str:
        pass

    @abstractmethod
    def send_output(self, messages: List[str]) -> None:
        pass


class TerminalIO(GameIO):
    def get_input(self, ps: PlayerState) -> str:
        return input(f"{ps.color}{ps.code_name}: ")

    def send_output(self, messages: List[str]) -> None:
        for msg in messages:
            print(msg)


# Placeholder for a future NetworkIO version
class NetworkIO(GameIO):
    def __init__(self, socket):
        self.socket = socket

    def get_input(self, ps: PlayerState) -> str:
        data = self.socket.recv(4096).decode()
        return data.strip()

    def send_output(self, messages: List[str]) -> None:
        payload = "\n".join(messages)
        self.socket.sendall(payload.encode())
