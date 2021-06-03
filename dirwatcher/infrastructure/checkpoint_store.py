from pathlib import Path
import json

STORE_LOCATION = "store.json"


def load_checkpoints() -> dict[Path, str]:
    with open(STORE_LOCATION, "r") as f:
        return {Path(k): v for k, v in json.load(f).items()}


def save_checkpoints(hashes: dict[Path, str]):
    with open(STORE_LOCATION, "w") as f:
        json.dump({str(k): v for k, v in hashes.items()}, f)
