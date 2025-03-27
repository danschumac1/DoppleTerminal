import os
from typing import List

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