import click
from pathlib import Path

from dirwatcher.infrastructure.checkpoint_store import CheckpointStoreAdapter
from dirwatcher.infrastructure.hasher import Hasher
from dirwatcher.infrastructure.traverser import make_traverser
from dirwatcher.watcher_service import WatcherService


@click.group()
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path))
@click.option(
    "--store",
    default="store.json",
    help="Path to where the application should store checkpoints",
    type=click.Path(file_okay=True, dir_okay=False, readable=True, writable=True, path_type=Path))
@click.pass_context
def cli(ctx, path, store):
    """
    A simple utility that can watch for changes to the files in the specified directory - cli mode

    PATH: Directory to watch.
    """
    ctx.ensure_object(dict)
    ctx.obj["path"] = path
    ctx.obj["store"] = store


@click.command()
@click.pass_context
def watch(ctx: click.Context):
    """
    Start monitoring particular directory
    """
    store, path = ctx.obj["store"], ctx.obj["path"]
    if store.exists():
        exit(click.echo("Checkpoints store already exists - choose another location."))

    watcher_service = WatcherService(
        make_traverser(path),
        CheckpointStoreAdapter(store_path=store),
        Hasher()
    )
    try:
        watcher_service.checkpoint_current_state()
    except FileNotFoundError as e:
        exit(click.echo(f"Could not checkpoint current state due to: {e}"))


cli.add_command(watch)
