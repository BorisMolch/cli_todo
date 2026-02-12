# td

A local task state manager for your projects. Designed for humans and LLMs.

`td` tracks what you're working on, what you've parked, and what's done — using simple state labels instead of complex workflows.

## Install

```bash
pipx install td-todo-cli
```

## Quick Start

```bash
cd my-project
td init                          # create .td/ in your project
td add "Build auth system"       # create a task (state: active)
td add "Login UI" --parent build-auth-system --state focus
td ls                            # see all non-done tasks
td tree                          # hierarchical view
td done login-ui                 # mark finished
td status                        # focus: 0  active: 1  later: 0  done: 1  total: 2
```

## States

| State    | Meaning                            |
|----------|------------------------------------|
| `focus`  | In my working set right now        |
| `active` | Taken on, not working on it now    |
| `later`  | Explicitly parked                  |
| `done`   | Finished                           |

States represent intent, not progress. Any state can move to any other.

## Commands

```
td init                              Initialize .td/ in current directory
td add <title>                       Create task (default: active)
td focus <id>                        Move to focus
td active <id>                       Move to active
td later <id>                        Park it
td done <id>                         Mark finished
td ls                                List non-done tasks
td ls --state focus                  Filter by state
td ls --all                          Include done
td ls --json                         Machine-readable output
td tree                              Hierarchical view
td tree <id>                         Subtree from a node
td show <id>                         Full detail on one task
td status                            Summary counts
td edit <id> --title/--notes/--parent   Modify a task
td mv <id> <parent-id>              Move under a parent
td rm <id>                           Delete (confirms first)
td rm <id> --force                   Delete without confirmation
```

## LLM Integration

An LLM interacts with `td` through the same CLI:

```bash
td ls --json            # understand current project state
td ls --state focus     # know what matters right now
td add "Fix bug"        # create tasks
td done fix-bug         # mark work complete
```

No special API needed. The CLI is the interface.

## Storage

Tasks are individual YAML files in `.td/tasks/`, designed to be git-friendly and human-readable:

```yaml
id: login-ui
title: Build login form
state: focus
parent: auth
created: 2026-02-10T14:30:00
updated: 2026-02-10T14:30:00
```

## Development

```bash
git clone https://github.com/BorisMolch/td-cli.git
cd td-cli
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

MIT
