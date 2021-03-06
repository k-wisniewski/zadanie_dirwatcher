import contextlib
import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from dirwatcher.watcher_cli import cli


@contextlib.contextmanager
def no_permissions(path):
    prior = None
    if os.path.exists(path):
        prior = os.stat(path).st_mode
        os.chmod(path, 0o0000)
    yield str(path)
    if prior:
        os.chmod(path, prior)


def store_contains_expected_content(store_path, test_path):
    with open(store_path) as f:
        return json.load(f) == {str(test_path): "c96342da4b936bcdb65d4944be522afae30660417dd2ef1c8fe8c4b951e22fc4"}


def test_cli_should_accept_a_path_to_watch_as_an_argument_and_use_default_location_for_checkpoint_store(
        tmpdir_with_file
):
    tmpdir, test_path, *_ = tmpdir_with_file
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir):
        result = runner.invoke(cli, [str(tmpdir), "watch"])
        assert result.exit_code == 0
        assert store_contains_expected_content("store.json", test_path)


def test_cli_should_accept_a_store_location_as_an_option(tmpdir_with_file):
    tmpdir, test_path, store_path = tmpdir_with_file
    store_path = tmpdir / "store.json"
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem(temp_dir=tmpdir):
        result = runner.invoke(cli, ["--store", str(store_path), str(tmpdir), "watch"])
        assert result.exit_code == 0
        assert store_contains_expected_content(store_path, test_path)


def test_cli_should_not_allow_dirs_as_store_paths(tmpdir):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir):
        result = runner.invoke(cli, ["--store", ".", str(tmpdir), "watch"])
        assert result.exit_code > 0


def test_cli_should_not_allow_files_as_arguments(tmpdir_with_file):
    tmpdir, test_path, *_ = tmpdir_with_file
    with open(test_path, "w") as f:
        f.write("Hello darkness my old friend")
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir):
        result = runner.invoke(cli, [str(test_path), "watch"])
        assert result.exit_code > 0


def test_cli_should_not_allow_unreadable_dirs_as_arguments(tmpdir_with_file):
    tmpdir, test_path, *_ = tmpdir_with_file
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir), no_permissions(tmpdir) as directory:
        result = runner.invoke(cli, [directory, "watch"])
        assert result.exit_code > 0


def test_cli_should_not_allow_unreadable_files_as_store_paths(tmpdir_with_file):
    tmpdir, test_path, store_path, *_ = tmpdir_with_file
    Path(store_path).touch()
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir), no_permissions(store_path) as store:
        result = runner.invoke(cli, ["--store", store, str(tmpdir), "watch"])
        assert result.exit_code > 0


def test_get_should_return_new_files_if_new_option_passed_and_prior_checkpoint_available(tmpdir_with_file):
    tmpdir, test_path, *_ = tmpdir_with_file
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir):
        result = runner.invoke(cli, [str(tmpdir), "watch"])
        assert result.exit_code == 0
        new_file_path = tmpdir / "new_file.txt"
        with open(new_file_path, "w") as f:
            f.write("I'm new here")

        result = runner.invoke(cli, [str(tmpdir), "get", "--new"])
        assert result.exit_code == 0
        print(result.stdout)
        assert result.stdout == f"New files: [PosixPath('{new_file_path}')]\n"


def test_get_should_return_deleted_files_if_deleted_option_passed_and_prior_checkpoint_available(tmpdir_with_file):
    tmpdir, test_path, *_ = tmpdir_with_file
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir):
        result = runner.invoke(cli, [str(tmpdir), "watch"])
        assert result.exit_code == 0
        Path(test_path).unlink()

        result = runner.invoke(cli, [str(tmpdir), "get", "--deleted"])
        assert result.exit_code == 0
        print(result.stdout)
        assert result.stdout == f"Deleted files: [PosixPath('{test_path}')]\n"


def test_get_should_return_changed_files_if_changed_option_passed_and_prior_checkpoint_available(tmpdir_with_file):
    tmpdir, test_path, *_ = tmpdir_with_file
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmpdir):
        result = runner.invoke(cli, [str(tmpdir), "watch"])
        assert result.exit_code == 0
        with open(test_path, "w") as f:
            f.write("I'm new here")

        result = runner.invoke(cli, [str(tmpdir), "get", "--content-changed"])
        assert result.exit_code == 0
        print(result.stdout)
        assert result.stdout == f"Content changed: [PosixPath('{test_path}')]\n"
