from pathlib import Path

STORE_LOCATION = "store.json"


def load_checkpoints() -> dict[Path, str]:
    ...


def save_checkpoints(hashes: dict[Path, str]):
    ...
