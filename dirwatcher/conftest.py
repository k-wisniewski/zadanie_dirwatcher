from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def tmpdir_with_file(tmpdir):
    test_path = tmpdir / "file.txt"
    store_path = tmpdir / "store.json"
    with open(test_path, "w") as f:
        f.write("Hello darkness my old friend")
    yield tmpdir, test_path, store_path
    Path(test_path).unlink(missing_ok=True)
