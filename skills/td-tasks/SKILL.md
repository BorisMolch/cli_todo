---
name: td-tasks
description: Manage project tasks using the `td` CLI tool. Use when a `.td/` directory exists in the project (or needs to be created), when the user mentions tasks, todos, focus, or work items, or when starting a session and needing to understand what to work on. Also use when the user says "td" or references task states (focus, active, later, done).
---

# td — Task State Manager

`td` is a local CLI tool for tracking task state and focus. Tasks are YAML files in `.td/tasks/`. States represent intent: `focus` (working now), `active` (taken on), `later` (parked), `done` (finished).

## Starting a Session

Check current project state before doing anything:

```bash
td ls --json          # machine-readable task list (excludes done)
td status             # quick counts: focus: 2  active: 3  later: 1  done: 5  total: 11
td ls --state focus   # what matters right now
```

## Commands

### Create and manage tasks

```bash
td init                              # initialize .td/ in current directory
td add "Build login form"            # create task (state: active)
td add "Fix bug" --state focus       # create in specific state
td add "Login UI" --parent auth      # create as child task
td add "Thing" --id custom-id        # override auto-generated slug
```

### Change state

```bash
td focus <id>       # → focus (working on it now)
td active <id>      # → active (taken on, not right now)
td later <id>       # → later (parked)
td done <id>        # → done (finished)
```

### View tasks

```bash
td ls                    # all non-done tasks, human-readable table
td ls --all              # include done tasks
td ls --state focus      # filter by state
td ls --json             # JSON output for programmatic use
td tree                  # hierarchical view
td tree <id>             # subtree from specific node
td show <id>             # full detail on one task
td status                # summary counts by state
```

### Modify and remove

```bash
td edit <id> --title "New title"
td edit <id> --notes "Updated info"
td edit <id> --parent other-task     # move under parent
td edit <id> --parent ""             # make root task
td mv <id> <parent-id>              # shorthand for edit --parent
td rm <id> --force                   # delete task (use --force to skip prompt)
```

## Conventions

- Mark tasks `done` when finishing work, not just when asked to.
- When starting work on something, `td focus <id>` it.
- After completing a task, run `td status` to stay oriented.
- Use `td ls --json` when you need to reason about task data programmatically.
- IDs are slugs derived from titles. They are immutable after creation.
- Tasks can be nested via `--parent` for hierarchical structure.
