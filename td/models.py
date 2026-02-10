from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

VALID_STATES = ("focus", "active", "later", "done")


def slugify(title: str) -> str:
    """Convert a title to a filesystem-safe slug."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s


@dataclass
class Task:
    id: str
    title: str
    state: str
    created: datetime
    updated: datetime
    parent: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict:
        d: dict = {
            "id": self.id,
            "title": self.title,
            "state": self.state,
        }
        if self.parent is not None:
            d["parent"] = self.parent
        if self.notes is not None:
            d["notes"] = self.notes
        d["created"] = self.created
        d["updated"] = self.updated
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            title=data["title"],
            state=data["state"],
            parent=data.get("parent"),
            notes=data.get("notes"),
            created=data["created"],
            updated=data["updated"],
        )
