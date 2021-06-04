from pathlib import Path

import pytest

from dirwatcher.checkpoint_store_port import CheckpointStore
from dirwatcher.watcher_service import WatcherService, NoPriorCheckpointSavedError, Change


class _FakeCheckpointStoreAdapter(CheckpointStore):

    def __init__(self, mock_loaded_hashes: dict[Path, str], simulate_no_prior_state=False):
        self._loaded_hashes = mock_loaded_hashes
        self._saved_hashes = []
        self._simulate_no_prior_state = simulate_no_prior_state

    @property
    def saved_checkpoints(self):
        return self._saved_hashes

    def load_checkpoints(self) -> dict[Path, str]:
        if self._simulate_no_prior_state:
            raise NoPriorCheckpointSavedError()
        return self._loaded_hashes

    def save_checkpoints(self, hashes: dict[Path, str]):
        self._saved_hashes = hashes


class _FakeHasher:
    def hash_content(self, path: Path) -> str:
        hashes = {
            "file1.txt": "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
            "file2.txt": "bf470f3fe05eef6ba064ed3f9859aeddfeece239f9234f35448c95e943015b52",
        }
        return hashes[str(path)]


@pytest.mark.parametrize("store_contents,expected_result", [
    ({
         Path("file1.txt"): "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
         Path("file2.txt"): "bf470f3fe05eef6ba064ed3f9859aeddfeece239f9234f35448c95e943015b52",
     }, False),
    ({
         Path("file1.txt"): "7b4dbecac0c118e9d79fd47832430bc80309866805c5517f97b3352218e8a0c4",
     }, True)
])
def test_has_anything_changed_should_indicate_if_files_match(store_contents, expected_result):
    service_under_test = WatcherService(
        lambda: [Path('file1.txt'), Path('file2.txt')],
        _FakeCheckpointStoreAdapter(store_contents),
        _FakeHasher()
    )

    result = service_under_test.has_anything_changed()

    assert result == expected_result


def test_has_anything_changed_should_raise_if_no_prior_checkpoint_found():
    service_under_test = WatcherService(
        lambda: [Path('file1.txt'), Path('file2.txt')],
        _FakeCheckpointStoreAdapter({}, True),
        _FakeHasher()
    )
    with pytest.raises(NoPriorCheckpointSavedError):
        service_under_test.has_anything_changed()


def test_checkpoint_current_state_hashes_watched_files_and_saves_the_mapping():
    store = _FakeCheckpointStoreAdapter({})
    service_under_test = WatcherService(
        lambda: [Path('file1.txt'), Path('file2.txt')], store, _FakeHasher())
    service_under_test.checkpoint_current_state()
    assert store.saved_checkpoints == {
        Path("file1.txt"): "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
        Path("file2.txt"): "bf470f3fe05eef6ba064ed3f9859aeddfeece239f9234f35448c95e943015b52",
    }


def test_checkpoint_current_state_does_nothing_if_there_are_no_files_to_watch():
    store = _FakeCheckpointStoreAdapter({})
    service_under_test = WatcherService(lambda: [], store, _FakeHasher())
    service_under_test.checkpoint_current_state()
    assert store.saved_checkpoints == {}


def test_get_changes_since_last_checkpoint_should_raise_if_no_prior_checkpoint_found():
    service_under_test = WatcherService(
        lambda: [Path('file1.txt'), Path('file2.txt')],
        _FakeCheckpointStoreAdapter({}, True),
        _FakeHasher()
    )
    with pytest.raises(NoPriorCheckpointSavedError):
        service_under_test.get_changes_since_last_checkpoint()


def test_get_changes_since_last_checkpoint_should_notice_new_files():
    service_under_test = WatcherService(
        lambda: [Path('file1.txt'), Path('file2.txt')],
        _FakeCheckpointStoreAdapter({
            Path("file1.txt"): "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
        }),
        _FakeHasher()
    )

    result = service_under_test.get_changes_since_last_checkpoint()

    assert result.get(Change.NEW) == [Path("file2.txt")]
    assert result.get(Change.DELETED) == []
    assert result.get(Change.CONTENT_CHANGED) == []


def test_get_changes_since_last_checkpoint_should_notice_deleted_files():
    service_under_test = WatcherService(
        lambda: [Path('file1.txt')],
        _FakeCheckpointStoreAdapter({
            Path("file1.txt"): "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
            Path("file2.txt"): "bf470f3fe05eef6ba064ed3f9859aeddfeece239f9234f35448c95e943015b52",
        }),
        _FakeHasher()
    )

    result = service_under_test.get_changes_since_last_checkpoint()

    assert result.get(Change.NEW) == []
    assert result.get(Change.DELETED) == [Path("file2.txt")]
    assert result.get(Change.CONTENT_CHANGED) == []


def test_get_changes_since_last_checkpoint_should_notice_changed_files():
    service_under_test = WatcherService(
        lambda: [Path("file1.txt"), Path("file2.txt")],
        _FakeCheckpointStoreAdapter({
            Path("file1.txt"): "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
            Path("file2.txt"): "7b4dbecac0c118e9d79fd47832430bc80309866805c5517f97b3352218e8a0c4",
        }),
        _FakeHasher()
    )

    result = service_under_test.get_changes_since_last_checkpoint()

    assert result.get(Change.NEW) == []
    assert result.get(Change.DELETED) == []
    assert result.get(Change.CONTENT_CHANGED) == [Path("file2.txt")]
