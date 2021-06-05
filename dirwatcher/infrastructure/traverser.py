from pathlib import Path
from typing import Callable, Iterator


def make_traverser(path: Path) -> Callable[[], Iterator[Path]]:
    pass
