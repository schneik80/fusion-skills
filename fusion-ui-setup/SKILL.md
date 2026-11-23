---
name: fusion-ui-setup
description: "Run this skill at the START of every Fusion 360 / fusion-mcp session, before doing any design work. Trigger immediately whenever fusion-mcp is first used, a new Fusion session begins, or the user says anything like 'start fusion', 'open fusion', 'new fusion session', 'set up fusion', or 'clean up the fusion ui'. This skill customizes the Fusion 360 UI by hiding distracting panels so the viewport is clean and ready for design work. Always asks the user for permission before applying the cleanup — never runs automatically."
---

# Fusion UI Setup

Run this at the start of every fusion-mcp session to clean up the Fusion 360 UI.

## Ask First (Required)

**Always ask before applying the cleanup.** Some users prefer to keep panels like the Browser or Data Panel open, and the cleanup is a visible change to their workspace.

Before running the script, ask the user a short question such as:

> "Want me to run the standard UI cleanup (hide Browser, Activity Feed, Data Panel, Text Commands, Command Toolbar)?"

Only proceed to the **Script to run** section if the user confirms (e.g. "yes", "go", "do it"). If they decline or want a partial cleanup, skip the script or run only the commands they asked for. Do not infer consent from earlier turns or from the user simply saying "start a fusion session" — those phrases trigger the skill but do **not** authorize the change.

## What it does

Executes five commands to hide UI panels that clutter the workspace:

| Panel | Command ID |
|---|---|
| Browser | `HideBrowserCommand` |
| Comments / Activity Feed | `HideActivityFeedCommand` |
| Data Panel | `DashboardModeCloseCommand` |
| Text Commands | `HideTextCommandsCommand` |
| Command Toolbar | `HideCommandToolbarCommand` |

## Script to run

Use `fusion-mcp:execute_api_script` with the following Python:

```python
import adsk.core

commands_to_run = [
    "HideBrowserCommand",
    "HideActivityFeedCommand",
    "DashboardModeCloseCommand",
    "HideTextCommandsCommand",
    "HideCommandToolbarCommand",
]

app = adsk.core.Application.get()
ui = app.userInterface
cmdDefs = ui.commandDefinitions

for cmd_id in commands_to_run:
    try:
        cmd = cmdDefs.itemById(cmd_id)
        if cmd:
            cmd.execute()
        else:
            ui.messageBox(f"Command not found: {cmd_id}")
    except Exception as e:
        ui.messageBox(f"Error running {cmd_id}: {str(e)}")
```

## After running

Confirm all panels are hidden, then proceed with the user's design task.
If any command was not found or errored, note it but continue — the UI may already be in the desired state.
