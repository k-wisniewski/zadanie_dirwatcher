from pathlib import Path

import pytest

from dirwatcher.infrastructure import hasher, checkpoint_store
from dirwatcher.watcher_service import WatcherService


def fake_load_checkpoints_matching() -> dict[Path, str]:
    return {
        Path("file1.txt"): "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
        Path("file2.txt"): "bf470f3fe05eef6ba064ed3f9859aeddfeece239f9234f35448c95e943015b52",
    }


def fake_load_checkpoints_not_matching() -> dict[Path, str]:
    return {
        Path("file1.txt"): "7b4dbecac0c118e9d79fd47832430bc80309866805c5517f97b3352218e8a0c4",
    }


def fake_hasher(path: Path) -> str:
    hashes = {
        "file1.txt": "64496aedaadf981a8bd77f4ebb6e949eecaa15fb93cc3fa3fcb17acccd117e60",
        "file2.txt": "bf470f3fe05eef6ba064ed3f9859aeddfeece239f9234f35448c95e943015b52",
    }
    return hashes[str(path)]


@pytest.mark.parametrize("checkpoints_loader,expected_result", [
    (fake_load_checkpoints_matching, False),
    (fake_load_checkpoints_not_matching, True)
])
def test_has_anything_changed_should_indicate_if_files_match(checkpoints_loader, expected_result, monkeypatch):
    monkeypatch.setattr(hasher, "hash_content", fake_hasher)
    hasher.hash_content = fake_hasher
    monkeypatch.setattr(checkpoint_store, "load_checkpoints", checkpoints_loader)
    service_under_test = WatcherService(lambda: [Path('file1.txt'), Path('file2.txt')])

    result = service_under_test.has_anything_changed()

    assert result == expected_result
