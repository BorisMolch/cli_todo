from __future__ import annotations

import json
from datetime import datetime

import click

from td.models import VALID_STATES, Task, slugify
from td.store import (
    delete_task,
    find_td_root,
    init_project,
    load_all_tasks,
    load_task,
    resolve_unique_id,
    save_task,
)


@click.group()
def cli():
    """td — a local task state manager."""


@cli.command()
def init():
    """Initialize .td/ in the current directory."""
    root = init_project()
    click.echo(f"Initialized .td/ in {root}")


@cli.command()
@click.argument("title")
@click.option("--parent", default=None, help="Parent task ID.")
@click.option(
    "--state",
    default=None,
    type=click.Choice(VALID_STATES, case_sensitive=False),
    help="Initial state (default: active).",
)
@click.option("--id", "custom_id", default=None, help="Custom task ID.")
def add(title: str, parent: str | None, state: str | None, custom_id: str | None):
    """Create a new task."""
    root = find_td_root()

    if custom_id:
        task_id = custom_id
        if (root / ".td" / "tasks" / f"{task_id}.yaml").exists():
            raise click.ClickException(f"Task ID '{task_id}' already exists.")
    else:
        base = slugify(title)
        if not base:
            raise click.ClickException("Title must produce a valid slug.")
        task_id = resolve_unique_id(root, base)

    if state is None:
        state = "active"

    now = datetime.now()
    task = Task(
        id=task_id,
        title=title,
        state=state,
        parent=parent,
        created=now,
        updated=now,
    )
    save_task(root, task)
    click.echo(task_id)


def _set_state(task_id: str, new_state: str) -> None:
    root = find_td_root()
    task = load_task(root, task_id)
    task.state = new_state
    task.updated = datetime.now()
    save_task(root, task)
    click.echo(f"{task_id} → {new_state}")


@cli.command()
@click.argument("id")
def focus(id: str):
    """Move a task to focus."""
    _set_state(id, "focus")


@cli.command()
@click.argument("id")
def active(id: str):
    """Move a task to active."""
    _set_state(id, "active")


@cli.command()
@click.argument("id")
def later(id: str):
    """Park a task for later."""
    _set_state(id, "later")


@cli.command()
@click.argument("id")
def done(id: str):
    """Mark a task as done."""
    _set_state(id, "done")


@cli.command(name="ls")
@click.option(
    "--state",
    "filter_state",
    default=None,
    type=click.Choice(VALID_STATES, case_sensitive=False),
    help="Filter by state.",
)
@click.option("--all", "show_all", is_flag=True, help="Show all tasks including done.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def ls_cmd(filter_state: str | None, show_all: bool, as_json: bool):
    """List tasks."""
    root = find_td_root()
    tasks = load_all_tasks(root)

    if filter_state:
        tasks = [t for t in tasks if t.state == filter_state]
    elif not show_all:
        tasks = [t for t in tasks if t.state != "done"]

    # Sort: focus first, then active, then later, then done
    state_order = {s: i for i, s in enumerate(VALID_STATES)}
    tasks.sort(key=lambda t: state_order.get(t.state, 99))

    if as_json:
        out = []
        for t in tasks:
            entry: dict = {"id": t.id, "title": t.title, "state": t.state}
            if t.parent:
                entry["parent"] = t.parent
            out.append(entry)
        click.echo(json.dumps(out, indent=2))
        return

    if not tasks:
        click.echo("No tasks.")
        return

    # Calculate column widths
    id_width = max(len(t.id) for t in tasks)
    state_width = max(len(t.state) for t in tasks)
    click.echo(f"{'STATE':<{state_width}}  {'ID':<{id_width}}  TITLE")
    for t in tasks:
        click.echo(f"{t.state:<{state_width}}  {t.id:<{id_width}}  {t.title}")


@cli.command()
@click.argument("id", required=False)
def tree(id: str | None):
    """Show tasks as a tree."""
    root = find_td_root()
    tasks = load_all_tasks(root)

    # By default hide done
    tasks = [t for t in tasks if t.state != "done"]

    task_map = {t.id: t for t in tasks}
    children: dict[str | None, list[Task]] = {}
    for t in tasks:
        children.setdefault(t.parent, []).append(t)

    def print_tree(parent_id: str | None, indent: int = 0) -> None:
        for t in children.get(parent_id, []):
            prefix = "  " * indent
            click.echo(f"{prefix}{t.id} [{t.state}]")
            print_tree(t.id, indent + 1)

    if id:
        if id not in task_map:
            raise click.ClickException(f"Task '{id}' not found.")
        t = task_map[id]
        click.echo(f"{t.id} [{t.state}]")
        print_tree(id, indent=1)
    else:
        print_tree(None)


@cli.command()
@click.argument("id")
def show(id: str):
    """Show full details of a task."""
    root = find_td_root()
    task = load_task(root, id)
    click.echo(f"id:      {task.id}")
    click.echo(f"title:   {task.title}")
    click.echo(f"state:   {task.state}")
    if task.parent:
        click.echo(f"parent:  {task.parent}")
    if task.notes:
        click.echo(f"notes:   {task.notes}")
    click.echo(f"created: {task.created}")
    click.echo(f"updated: {task.updated}")


@cli.command()
@click.argument("id")
@click.option("--title", default=None, help="New title.")
@click.option("--notes", default=None, help="New notes.")
@click.option("--parent", default=None, help="New parent ID (empty string to remove).")
def edit(id: str, title: str | None, notes: str | None, parent: str | None):
    """Edit a task's title, notes, or parent."""
    root = find_td_root()
    task = load_task(root, id)
    changed = False

    if title is not None:
        task.title = title
        changed = True
    if notes is not None:
        task.notes = notes if notes else None
        changed = True
    if parent is not None:
        task.parent = parent if parent else None
        changed = True

    if changed:
        task.updated = datetime.now()
        save_task(root, task)
        click.echo(f"Updated {id}")
    else:
        click.echo("Nothing to update.")


@cli.command()
@click.argument("id")
@click.argument("parent_id")
def mv(id: str, parent_id: str):
    """Move a task under a different parent."""
    root = find_td_root()
    task = load_task(root, id)
    task.parent = parent_id
    task.updated = datetime.now()
    save_task(root, task)
    click.echo(f"Moved {id} → {parent_id}")


@cli.command()
@click.argument("id")
@click.option("--force", is_flag=True, help="Skip confirmation.")
def rm(id: str, force: bool):
    """Remove a task."""
    root = find_td_root()
    # Verify it exists first
    load_task(root, id)

    if not force:
        click.confirm(f"Delete task '{id}'?", abort=True)

    delete_task(root, id)
    click.echo(f"Deleted {id}")


@cli.command()
def status():
    """Show summary counts by state."""
    root = find_td_root()
    tasks = load_all_tasks(root)
    counts = {s: 0 for s in VALID_STATES}
    for t in tasks:
        counts[t.state] = counts.get(t.state, 0) + 1
    total = len(tasks)
    parts = [f"{s}: {counts[s]}" for s in VALID_STATES]
    parts.append(f"total: {total}")
    click.echo("  ".join(parts))
