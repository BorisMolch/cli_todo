import os
from datetime import datetime

import pytest

from td.models import Task
from td.store import (
    delete_task,
    find_td_root,
    init_project,
    load_all_tasks,
    load_task,
    resolve_unique_id,
    save_task,
    task_exists,
)


@pytest.fixture
def project(tmp_path):
    """Create an initialized td project in a temp directory."""
    init_project(str(tmp_path))
    return tmp_path


def make_task(id="test-task", title="Test task", state="active", **kwargs) -> Task:
    now = datetime(2026, 1, 1, 12, 0, 0)
    return Task(id=id, title=title, state=state, created=now, updated=now, **kwargs)


class TestInitProject:
    def test_creates_structure(self, tmp_path):
        init_project(str(tmp_path))
        assert (tmp_path / ".td").is_dir()
        assert (tmp_path / ".td" / "tasks").is_dir()
        assert (tmp_path / ".td" / "config.yaml").exists()

    def test_idempotent(self, tmp_path):
        init_project(str(tmp_path))
        init_project(str(tmp_path))
        assert (tmp_path / ".td" / "config.yaml").exists()


class TestFindTdRoot:
    def test_finds_root(self, project):
        assert find_td_root(str(project)) == project

    def test_finds_from_subdirectory(self, project):
        sub = project / "src" / "deep"
        sub.mkdir(parents=True)
        assert find_td_root(str(sub)) == project

    def test_raises_when_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            find_td_root(str(tmp_path))


class TestSaveLoadTask:
    def test_save_and_load(self, project):
        task = make_task()
        save_task(project, task)
        loaded = load_task(project, "test-task")
        assert loaded.id == task.id
        assert loaded.title == task.title
        assert loaded.state == task.state

    def test_load_missing_raises(self, project):
        with pytest.raises(FileNotFoundError):
            load_task(project, "nope")


class TestLoadAllTasks:
    def test_loads_multiple(self, project):
        save_task(project, make_task(id="a", title="A"))
        save_task(project, make_task(id="b", title="B"))
        tasks = load_all_tasks(project)
        ids = [t.id for t in tasks]
        assert "a" in ids
        assert "b" in ids

    def test_empty(self, project):
        assert load_all_tasks(project) == []


class TestDeleteTask:
    def test_delete(self, project):
        save_task(project, make_task())
        assert task_exists(project, "test-task")
        delete_task(project, "test-task")
        assert not task_exists(project, "test-task")

    def test_delete_missing_raises(self, project):
        with pytest.raises(FileNotFoundError):
            delete_task(project, "nope")


class TestResolveUniqueId:
    def test_no_collision(self, project):
        assert resolve_unique_id(project, "new-task") == "new-task"

    def test_collision(self, project):
        save_task(project, make_task(id="task"))
        assert resolve_unique_id(project, "task") == "task-2"

    def test_multiple_collisions(self, project):
        save_task(project, make_task(id="task"))
        save_task(project, make_task(id="task-2"))
        assert resolve_unique_id(project, "task") == "task-3"
