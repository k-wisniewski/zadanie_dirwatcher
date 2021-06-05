from pathlib import Path
from typing import Callable, Iterator


def make_traverser(path: Path) -> Callable[[], Iterator[Path]]:
    def list_dir():
        yield from (item for item in path.iterdir() if item.is_file())

    return list_dir
