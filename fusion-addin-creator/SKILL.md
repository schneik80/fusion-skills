---
name: fusion-addin-creator
description: >
  Scaffold a new Autodesk Fusion 360 add-in from the standard template.
  Use this skill whenever the user asks to create, scaffold, generate, or start a new
  Fusion add-in, Fusion script project, Fusion plugin, or says things like "new addin",
  "create an addin", "bootstrap a Fusion add-in", "start a new Fusion project", or
  "scaffold an addin". Also trigger when the user mentions NewAddIn, the Fusion addin
  template, or wants to duplicate/copy an existing addin structure.
---

# Fusion Add-In Creator

Scaffolds a complete Autodesk Fusion 360 add-in by cloning the standard `NewAddIn`
template and customising every file for the user's project.

## Overview of What This Skill Does

1. **Collect information** from the user (name, company, metadata, output path)
2. **Sanitise** the name into a safe folder/identifier
3. **Copy** the template tree to the target location
4. **Rename & patch** every file that references `NewAddIn`
5. **Confirm** success and tell the user how to load the add-in in Fusion

---

## Step 1 — Collect User Information Interactively

Gather information across **two conversational turns**, keeping each turn focused.

---

### Turn 1 — Core Identity (ask these three together as open-ended prose questions)

Ask the user for these three things in a single friendly message:

1. **Add-in name** — the human-readable display name (spaces allowed, e.g. `My Cool Tool`)
2. **Description** — one sentence describing what the add-in does
3. **Company name** — short identifier used as an internal ID prefix (no spaces, e.g. `ACME`)

Do **not** ask about version, location, or startup in this turn.

---

### Turn 2 — Confirm Defaults

After receiving the three core fields, present the derived `SAFE_NAME` (see below) and
then confirm the remaining defaults with the user in **one single yes/no prompt**:

> "Here's what I'll use for the remaining settings — reply **yes** to confirm or let me
> know what to change:"
>
> - **Version:** `1.0.0`
> - **Output location:** `/Users/schneik/Source`
> - **Run on startup:** Yes
> - **Folder name:** `<SAFE_NAME>`

Use `ask_user_input_v0` with a single yes/no choice for this confirmation. If the user
says no, ask them which field(s) to change and re-confirm once updated.

Only proceed to Step 3 once the user has confirmed.

---

### Deriving the safe folder/ID name

Once you have the display name, compute `SAFE_NAME` with these rules (apply in order):

```python
import re, unicodedata

def safe_name(display_name: str) -> str:
    # 1. Normalise unicode
    s = unicodedata.normalize('NFKD', display_name)
    s = s.encode('ascii', 'ignore').decode('ascii')
    # 2. Replace spaces and hyphens with nothing (CamelCase-friendly) or underscore
    #    Keep alphanumeric only; collapse runs of non-alnum to a single underscore
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')
    # 3. Must start with a letter
    if s and not s[0].isalpha():
        s = 'AddIn_' + s
    return s or 'MyAddIn'
```

Show the user the computed `SAFE_NAME` and `COMPANY_NAME` and ask them to confirm or
adjust before proceeding to file generation.

---

## Step 2 — Template Source

The canonical template lives at:

```
/Users/schneik/Source/NewAddIn/
```

**Always copy from this path.** Do not re-create files from scratch.

### Template tree

```
NewAddIn/
├── .vscode/
│   └── launch.json
├── commands/
│   ├── __init__.py
│   ├── commandDialog/
│   │   ├── __init__.py
│   │   ├── entry.py
│   │   └── resources/   (16x16.png, 32x32.png, 64x64.png)
│   ├── paletteSend/
│   │   ├── __init__.py
│   │   ├── entry.py
│   │   └── resources/   (16x16.png, 32x32.png, 64x64.png)
│   └── paletteShow/
│       ├── __init__.py
│       ├── entry.py
│       └── resources/
│           ├── 16x16.png, 32x32.png, 64x64.png
│           └── html/
│               ├── index.html
│               └── static/palette.js
├── lib/
│   └── fusionAddInUtils/
│       ├── __init__.py
│       ├── event_utils.py
│       └── general_utils.py
├── AddInIcon.svg
├── config.py
├── NewAddIn.manifest
└── NewAddIn.py
```

---

## Step 3 — Scaffold the Add-in

Use the `bash_tool` to execute all file operations. Do this in one coherent script.

### 3a. Copy the template

```bash
cp -r /Users/schneik/Source/NewAddIn "<OUTPUT_DIR>/<SAFE_NAME>"
```

### 3b. Rename the root-level files that carry the old name

```bash
cd "<OUTPUT_DIR>/<SAFE_NAME>"
mv NewAddIn.py         <SAFE_NAME>.py
mv NewAddIn.manifest   <SAFE_NAME>.manifest
```

### 3c. Patch text content — substitutions to make

Use `sed` (macOS/Linux) or Python `str.replace` to patch every text file.
The table below lists every substitution needed:

| File | Find | Replace |
|---|---|---|
| `<SAFE_NAME>.manifest` | entire JSON | rewrite with user values (see template below) |
| `config.py` | `ADDIN_NAME = os.path.basename(...)` line is already dynamic — no change needed | — |
| `config.py` | `COMPANY_NAME = 'ACME'` | `COMPANY_NAME = '<COMPANY_NAME>'` |
| `<SAFE_NAME>.py` | (no literal references to `NewAddIn` — file is generic) | — |
| `.vscode/launch.json` | (no name references — leave as-is) | — |

> **Note:** `ADDIN_NAME` in `config.py` is derived at runtime from the folder name via
> `os.path.basename(os.path.dirname(__file__))`, so renaming the folder is sufficient —
> no source edit needed.

### 3d. Manifest template

Write this exact JSON to `<SAFE_NAME>.manifest` (fill in user values):

```json
{
    "autodeskProduct": "Fusion",
    "type": "addin",
    "author": "<COMPANY_NAME>",
    "description": {
        "": "<DESCRIPTION>"
    },
    "version": "1.0.0",
    "runOnStartup": true,
    "supportedOS": "windows|mac",
    "editEnabled": true,
    "iconFilename": "AddInIcon.svg"
}
```

### 3e. Patch `config.py` — company name

```python
# Read config.py, replace the COMPANY_NAME line
content = open('config.py').read()
content = content.replace("COMPANY_NAME = 'ACME'", f"COMPANY_NAME = '{COMPANY_NAME}'")
open('config.py', 'w').write(content)
```

### 3f. Verify the result

After patching, print the final directory tree and the contents of the manifest and
`config.py` so the user can confirm everything looks correct.

---

## Step 4 — Confirm & Guide the User

Once files are created, tell the user:

1. **Where the add-in was created**: full path
2. **How to load it in Fusion 360**:
   - Open Fusion 360
   - Go to **Utilities → Add-Ins** (or press **Shift+S**)
   - Click the **Add-Ins** tab → **My Add-Ins**
   - Click **+** and browse to `<OUTPUT_DIR>/<SAFE_NAME>`
   - Click **Run** to start the add-in
3. **Where to start coding**: `commands/commandDialog/entry.py` is the main command entry
   point — look for the `TODO` comments.
4. **Company name note**: The `COMPANY_NAME` in `config.py` is used as a prefix for all
   internal Fusion UI element IDs. Keep it short and unique.

---

## Error Handling

- If the target directory already exists, **stop and ask** the user whether to overwrite,
  pick a different name, or cancel — never silently clobber.
- If the template source `/Users/schneik/Source/NewAddIn` is not found, tell the user and
  ask them to provide an alternative template path.
- If `SAFE_NAME` ends up identical to `NewAddIn`, warn the user that this will conflict
  with the template folder and ask them to choose a different name.
