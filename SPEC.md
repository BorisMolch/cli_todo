# td — Product Specification v0.1

> td is a local, structured task state system that helps you and an LLM maintain focus, intent, and continuity across project work.

---

## Problem

You need a stable, structured memory of what you're working on, what you've parked, and what you've committed to — that both you and an LLM can reason about across sessions.

Not assignments. Not workflows. Not boards. Just **state + focus**.

---

## State Model

| State    | Meaning                                          |
|----------|--------------------------------------------------|
| `focus`  | In my working set right now                      |
| `active` | I've taken this on, not working on it this moment|
| `later`  | Explicitly parked                                |
| `done`   | Finished                                         |

States represent intent, not progress.

No transition rules. Any state can move to any other state. The human (or LLM) decides.

---

## Task Schema

Each task is a single YAML file in `.td/tasks/`.

```yaml
id: login-ui
title: Build login form
state: active
parent: auth
notes: |
  Needs validation and error handling.
  Should support email + password.
created: 2026-02-10T14:30:00
updated: 2026-02-10T14:30:00
```

### Fields

| Field     | Type     | Required | Description                           |
|-----------|----------|----------|---------------------------------------|
| `id`      | string   | yes      | Slug derived from title, unique       |
| `title`   | string   | yes      | One-line description                  |
| `state`   | enum     | yes      | focus / active / later / done         |
| `parent`  | string   | no       | ID of parent task (for tree structure)|
| `notes`   | string   | no       | Free-form longer description          |
| `created` | datetime | yes      | When the task was created             |
| `updated` | datetime | yes      | Last modification time                |

`parent` may be omitted or set to `null` for root tasks.

That's it. No priority, no assignee, no due date, no tags in v1.

---

## ID Strategy

- Auto-generated slug from title: `"Build login form"` → `build-login-form`
- On collision, append `-2`, `-3`, etc.
- User can override: `td add "Login form" --id my-custom-id`
- IDs are immutable after creation (renaming title doesn't change ID)
- IDs must be filesystem-safe: lowercase, `a-z`, `0-9`, `-` only

---

## On-Disk Layout

```
project/
  .td/
    config.yaml          # project metadata, defaults (optional)
    tasks/
      auth.yaml
      login-ui.yaml
      token-refresh.yaml
```

### config.yaml

```yaml
project: my-app
default_state: active
```

---

## CLI Commands

### Project

```
td init                              Initialize .td/ in current directory
```

### Creating Tasks

```
td add "Build login form"            Create task (state: active by default)
td add "Login UI" --parent auth      Create as child of 'auth'
td add "Quick fix" --state focus     Create directly in focus state
td add "Someday thing" --state later Create in later state
```

### Changing State

```
td focus <id>                        Move to focus
td active <id>                       Move to active
td later <id>                        Park it
td done <id>                         Mark finished
```

### Viewing Tasks

```
td ls                                List all non-done tasks
td ls --state focus                  Filter by state
td ls --state done                   Show completed tasks
td ls --all                          Show everything including done
td ls --json                         Machine-readable output (for LLMs/scripts)

td tree                              Hierarchical view of all non-done tasks
td tree <id>                         Subtree from a specific node

td show <id>                         Full detail on one task

td status                            Summary counts by state
```

By default, `done` tasks are hidden. Use `--state done` or `--all` to see them.

### Modifying Tasks

```
td edit <id> --title "New title"     Change title (ID stays the same)
td edit <id> --notes "Updated info"  Change notes
td edit <id> --parent other-task     Move under a different parent
td edit <id> --parent ""             Remove from parent (make root)

td mv <id> <parent-id>              Alias for td edit <id> --parent <parent-id>
```

### Removing Tasks

```
td rm <id>                           Delete task (confirms by default)
td rm <id> --force                   Delete without confirmation
```

---

## Output Format

### `td ls` (default, human)

```
STATE   ID              TITLE
focus   login-ui        Build login form
focus   token-refresh   Implement token refresh
active  auth            Authentication system
active  api-routes      Set up API routes
later   dark-mode       Add dark mode support
```

### `td ls --json` (machine/LLM)

```json
[
  {"id": "login-ui", "title": "Build login form", "state": "focus", "parent": "auth"},
  {"id": "token-refresh", "title": "Implement token refresh", "state": "focus", "parent": "auth"}
]
```

### `td tree`

```
auth [active]
  login-ui [focus]
  token-refresh [focus]
api-routes [active]
dark-mode [later]
```

### `td status`

```
focus: 2  active: 2  later: 1  done: 0  total: 5
```

---

## LLM Integration

An LLM interacts with `td` through the same CLI as a human:

1. **Read state**: `td ls --json` or `td show <id>` to understand current project state
2. **Modify state**: `td add`, `td done`, `td focus` etc. as regular CLI commands

An LLM session can start with:
```
$ td ls --state focus --json
```
...and immediately know what matters right now.

The CLI is the actuator. No special API needed.

---

## Resolved Decisions

| Decision                    | Choice                           | Rationale                                                  |
|-----------------------------|----------------------------------|------------------------------------------------------------|
| `td done` behavior          | Flip state, keep file in place   | Moving files complicates tree logic and greps. Git tracks history. |
| `td rm` confirmation        | Yes, unless `--force`            | Safety beats speed for destructive ops. LLMs use `--force`. |
| `td mv` alias               | Yes, thin alias for `edit --parent` | Ergonomics. Same code, nicer UX.                          |

---

## Technical Decisions

| Decision           | Choice                | Rationale                                    |
|--------------------|-----------------------|----------------------------------------------|
| Language           | Python                | Fast to prototype, pip-installable           |
| Storage            | YAML (one file/task)  | Git-friendly, greppable, LLM-readable        |
| CLI framework      | `click`               | Clean, composable, well-documented           |
| YAML library       | `ruamel.yaml`         | Preserves formatting, round-trip safe        |
| Distribution       | `pip install td-cli`  | Standard Python packaging                    |
| Min Python version | 3.10+                 | Modern features, match statements            |

---

## What Is Explicitly NOT in V1

- Assignments / assignee
- Due dates
- Priority levels
- Tags / labels
- Comments / discussion
- Change history / log
- Sync / remote
- Permissions
- Notifications
- Board view
- Sprint / milestone grouping

**If it doesn't support focus, intent, and continuity — it doesn't ship.**
