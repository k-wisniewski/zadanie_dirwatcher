from enum import Enum
from pathlib import Path


class Change(Enum):
    NEW = 1
    DELETED = 2
    CONTENT_CHANGED = 3


class NoPriorCheckpointSavedError(Exception):
    pass


class WatcherService:

    def has_anything_changed(self) -> bool:
        """
        Verifies if any of the watched files has changed.

        :raises:
        NoPriorCheckpointSavedError - when there's no previously saved checkpoint to check against
        :return:
        True - if there is a change
        False - if there isn't
        """
        raise NotImplementedError

    def checkpoint_current_state(self):
        """
        Calculates hashes of each of the watched files
        and saves the mapping path->hash using checkpoint_store.save_checkpoints
        :return:
        None
        """
        raise NotImplementedError

    def get_changes_since_last_checkpoint(self) -> dict[Change, list[Path]]:
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
