from datetime import datetime

from td.models import VALID_STATES, Task, slugify


class TestSlugify:
    def test_basic(self):
        assert slugify("Build login form") == "build-login-form"

    def test_special_characters(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_leading_trailing(self):
        assert slugify("  --hello--  ") == "hello"

    def test_consecutive_separators(self):
        assert slugify("a   b---c") == "a-b-c"

    def test_numbers(self):
        assert slugify("Step 1: Do thing") == "step-1-do-thing"

    def test_empty_after_strip(self):
        assert slugify("!!!") == ""

    def test_already_slug(self):
        assert slugify("my-task") == "my-task"


class TestTask:
    def _make_task(self, **overrides) -> Task:
        defaults = {
            "id": "test-task",
            "title": "Test task",
            "state": "active",
            "created": datetime(2026, 1, 1, 12, 0, 0),
            "updated": datetime(2026, 1, 1, 12, 0, 0),
        }
        defaults.update(overrides)
        return Task(**defaults)

    def test_to_dict_minimal(self):
        task = self._make_task()
        d = task.to_dict()
        assert d["id"] == "test-task"
        assert d["title"] == "Test task"
        assert d["state"] == "active"
        assert "parent" not in d
        assert "notes" not in d

    def test_to_dict_with_optionals(self):
        task = self._make_task(parent="parent-id", notes="Some notes")
        d = task.to_dict()
        assert d["parent"] == "parent-id"
        assert d["notes"] == "Some notes"

    def test_round_trip(self):
        task = self._make_task(parent="p", notes="n")
        d = task.to_dict()
        restored = Task.from_dict(d)
        assert restored.id == task.id
        assert restored.title == task.title
        assert restored.state == task.state
        assert restored.parent == task.parent
        assert restored.notes == task.notes
        assert restored.created == task.created
        assert restored.updated == task.updated

    def test_valid_states(self):
        assert VALID_STATES == ("focus", "active", "later", "done")
