from hashlib import sha256
from pathlib import Path


class Hasher:

    def hash_content(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError("Cannot hash non-existent file")
        with open(path, "rb") as f:
            return sha256(f.read()).hexdigest()
