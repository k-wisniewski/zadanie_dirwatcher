from pathlib import Path
import logging
from flask import Flask, request

from dirwatcher.infrastructure.checkpoint_store import CheckpointStoreAdapter
from dirwatcher.infrastructure.hasher import Hasher
from dirwatcher.infrastructure.traverser import make_traverser
from dirwatcher.watcher_service import WatcherService, NoPriorCheckpointSavedError, InvalidDirectoryRequested

app = Flask("dirwatcher")
logger = logging.getLogger(__name__)
STORE_LOCATION = "store.json"


@app.route("/save", methods=["POST"])
def save_current_state():
    directory = request.json["toWatch"]
    service = WatcherService(make_traverser(Path(directory)), CheckpointStoreAdapter(), Hasher())
    try:
        service.checkpoint_current_state()
    except InvalidDirectoryRequested as e:
        logger.error(e)
        return {"error": "the directory you requested does not exist"}, 400
    return "OK", 200
