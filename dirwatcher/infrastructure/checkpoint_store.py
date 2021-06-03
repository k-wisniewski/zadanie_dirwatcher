from pathlib import Path
import json

from dirwatcher.checkpoint_store_port import CheckpointStore


class CheckpointStoreAdapter(CheckpointStore):
    def __init__(self, store_path: Path = "store.json"):
        self._store_location = store_path

    def load_checkpoints(self) -> dict[Path, str]:
        with open(self._store_location, "r") as f:
            return {Path(k): v for k, v in json.load(f).items()}

    def save_checkpoints(self, hashes: dict[Path, str]):
        with open(self._store_location, "w") as f:
            json.dump({str(k): v for k, v in hashes.items()}, f)
