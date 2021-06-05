import pytest
import shutil

from dirwatcher.infrastructure.traverser import make_traverser
from pathlib import Path


@pytest.fixture(scope="function")
def prefilled_tmp_dir(tmpdir):
    tmp = Path(tmpdir)
    tmp.mkdir(exist_ok=True)
    (tmp / "inner_folder").mkdir()
    (tmp / "something.txt").touch(exist_ok=True)
    (tmp / "something_else.txt").touch(exist_ok=True)
    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture()
def tmp_dir_without_files(tmpdir):
    tmp = Path(tmpdir)
    tmp.mkdir(exist_ok=True)
    (tmp / "inner_folder").mkdir()
    yield tmp
    shutil.rmtree(tmp)


def test_make_traverser_returns_function_that_lists_dir(prefilled_tmp_dir):
    traverser = make_traverser(prefilled_tmp_dir)
    dir_iterator = traverser()

    assert next(dir_iterator) == prefilled_tmp_dir / "something.txt"
    assert next(dir_iterator) == prefilled_tmp_dir / "something_else.txt"


def test_list_dir_returns_only_files(prefilled_tmp_dir):
    dir_iterator = make_traverser(prefilled_tmp_dir)()
    for item in dir_iterator:
        assert item.is_file()


def test_list_dir_returns_nothing_for_directory_with_no_files(tmp_dir_without_files):
    dir_iterator = make_traverser(tmp_dir_without_files)()
    with pytest.raises(StopIteration):
        next(dir_iterator)
