from enum import Enum
from pathlib import Path
from typing import Callable, Iterator

from dirwatcher.infrastructure import checkpoint_store, hasher


class Change(Enum):
    NEW = 1
    DELETED = 2
    CONTENT_CHANGED = 3


class NoPriorCheckpointSavedError(Exception):
    pass


class WatcherService:

    def __init__(self, dir_lister: Callable[[], list[Path]]):
        self.dir_lister = dir_lister

    def has_anything_changed(self) -> bool:
        """
        Verifies if any of the watched files has changed.

        :raises:
        NoPriorCheckpointSavedError - when there's no previously saved checkpoint to check against
        :return:
        True - if there is a change
        False - if there isn't
        """
        try:
            checkpoints = checkpoint_store.load_checkpoints()
        except FileNotFoundError as e:
            raise NoPriorCheckpointSavedError(e) from e
        else:
            current_checkpoints = self._hash_dir()
            return checkpoints != current_checkpoints

    def checkpoint_current_state(self):
        """
        Calculates hashes of each of the watched files
        and saves the mapping path->hash using checkpoint_store.save_checkpoints
        :return:
        None
        """
        raise NotImplementedError

    def get_changes_since_last_checkpoint(self) -> dict[Change, Iterator[Path]]:
        """
        Returns a dict of all the changes that happened since the last checkpoint.
        There are 3 types of possible changes:
        1. some of the files have been deleted
        2. some of the files have been added
        3. some of the files have had their content changed

        :raises:
        NoPriorCheckpointSavedError - when there's no previously saved checkpoint to check against
        :return:
        A dict, where:
         - the list of paths affected by the change of type 1 is available under the key Change.DELETED
         - the list of paths affected by the change of type 2 is available under the key Change.NEW
         - the list of paths affected by the change of type 3 is available under the key Change.CONTENT_CHANGED
        """
        raise NotImplementedError

    def _hash_dir(self) -> dict[Path, str]:
        return {item: hasher.hash_content(item) for item in self.dir_lister()}
