from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

from td.models import Task

yaml = YAML()
yaml.default_flow_style = False


def find_td_root(start: str = ".") -> Path:
    """Walk up from *start* looking for a .td/ directory. Return its parent."""
    current = Path(start).resolve()
    while True:
        if (current / ".td").is_dir():
            return current
        if current.parent == current:
            raise FileNotFoundError(
                "No .td/ directory found. Run 'td init' first."
            )
        current = current.parent


def init_project(path: str = ".") -> Path:
    """Create .td/ structure and default config. Return the project root."""
    root = Path(path).resolve()
    td_dir = root / ".td"
    tasks_dir = td_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    config_path = td_dir / "config.yaml"
    if not config_path.exists():
        config = {"project": root.name, "default_state": "active"}
        with open(config_path, "w") as f:
            yaml.dump(config, f)

    return root


def load_config(root: Path) -> dict:
    config_path = root / ".td" / "config.yaml"
    with open(config_path) as f:
        return yaml.load(f) or {}


def save_task(root: Path, task: Task) -> Path:
    task_path = root / ".td" / "tasks" / f"{task.id}.yaml"
    with open(task_path, "w") as f:
        yaml.dump(task.to_dict(), f)
    return task_path


def load_task(root: Path, task_id: str) -> Task:
    task_path = root / ".td" / "tasks" / f"{task_id}.yaml"
    if not task_path.exists():
        raise FileNotFoundError(f"Task '{task_id}' not found.")
    with open(task_path) as f:
        data = yaml.load(f)
    return Task.from_dict(data)


def load_all_tasks(root: Path) -> list[Task]:
    tasks_dir = root / ".td" / "tasks"
    tasks: list[Task] = []
    for p in sorted(tasks_dir.glob("*.yaml")):
        with open(p) as f:
            data = yaml.load(f)
        if data:
            tasks.append(Task.from_dict(data))
    return tasks


def delete_task(root: Path, task_id: str) -> None:
    task_path = root / ".td" / "tasks" / f"{task_id}.yaml"
    if not task_path.exists():
        raise FileNotFoundError(f"Task '{task_id}' not found.")
    task_path.unlink()


def task_exists(root: Path, task_id: str) -> bool:
    return (root / ".td" / "tasks" / f"{task_id}.yaml").exists()


def resolve_unique_id(root: Path, base_slug: str) -> str:
    """Return base_slug if available, otherwise append -2, -3, … until unique."""
    if not task_exists(root, base_slug):
        return base_slug
    n = 2
    while task_exists(root, f"{base_slug}-{n}"):
        n += 1
    return f"{base_slug}-{n}"
