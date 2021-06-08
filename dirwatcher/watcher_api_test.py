from pathlib import Path

import pytest

from dirwatcher import watcher_api


@pytest.fixture
def client():
    watcher_api.STORE_LOCATION = "store.json"
    with watcher_api.app.test_client() as client:
        yield client
    Path(watcher_api.STORE_LOCATION).unlink(missing_ok=True)


def test_save_current_state_saves_current_checkpoints_and_returns_200_if_directory_exist(client):
    result = client.post("/save", json={"toWatch": "dirwatcher"})
    assert result.status_code == 200


def test_save_current_state_saves_current_checkpoints_and_returns_400_if_directory_does_not_exist(client):
    result = client.post("/save", json={"toWatch": "does_not_exists"})
    assert (result.status_code, result.get_json()) == (400, {"error": "the directory you requested does not exist"})
