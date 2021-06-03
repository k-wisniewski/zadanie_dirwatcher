from pathlib import Path
from typing import Protocol


class Hasher(Protocol):
    def hash_content(self, path: Path) -> str:
        ...
