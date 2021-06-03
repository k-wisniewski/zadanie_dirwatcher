import abc
from pathlib import Path


class CheckpointStore(abc.ABC):
    @abc.abstractmethod
    def load_checkpoints(self) -> dict[Path, str]:
        ...

    @abc.abstractmethod
    def save_checkpoints(self, hashes: dict[Path, str]):
        ...
