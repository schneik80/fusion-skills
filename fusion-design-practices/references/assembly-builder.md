# Assembly Builder (Programmatic Product Structure)

Build a complete external-component hierarchy in one pass from a structured
description of the product. Use this when the user asks to "scaffold an
assembly", "build the product structure", "create the BOM hierarchy", or
"set up the components for *<machine name>*".

The patterns here are extracted from the IMA PowerTools-Assemblies *Assembly
Builder* command and have been validated in production. Treat them as the
canonical way to programmatically populate a new Fusion design with a
multi-level product structure.

---

## Workflow Overview

The full operation is a **research → structure → build** pipeline:

1. **Research** the typical product structure of the requested mechanical
   design (see "Researching Product Structure" below).
2. **Convert** that research into a hierarchy dict using the schema in this
   file.
3. **Validate** preconditions on the active document (4 guards, in order).
4. **Build** top-down, creating external components and setting intent per
   node, recursing only for assembly/hybrid nodes.
5. **Resolve shared components** (parts referenced by more than one parent)
   in a second pass after a save.

Steps 3–5 are mechanical and identical every run. Steps 1–2 are the
judgement-heavy part — see end of file.

---

## Hierarchy Schema (MCP-Friendly)

When driving this from Claude / MCP, express the hierarchy as a nested
Python dict. This is **the recommended input format** for new sessions —
much simpler than the Drawflow graph the original add-in consumes.

```python
# Tree of dicts. Every node has: name, intent, optional children, optional shared_id.
hierarchy = {
    "name": "Linear Stage Assembly",
    "intent": "assembly",                  # root must be "assembly" or "hybrid"
    "children": [
        {
            "name": "Base Plate",
            "intent": "part",              # parts are leaves — no children
        },
        {
            "name": "Carriage Subassembly",
            "intent": "assembly",
            "children": [
                {"name": "Carriage Body",      "intent": "part"},
                {"name": "Linear Bearing Block","intent": "part",
                 "shared_id": "lbb_8mm"},     # shared — also used in End Stop
            ],
        },
        {
            "name": "Drive Subassembly",
            "intent": "assembly",
            "children": [
                {"name": "Stepper Motor",     "intent": "part"},
                {"name": "Coupler",           "intent": "part"},
                {"name": "Lead Screw",        "intent": "part"},
                {"name": "Lead Nut",          "intent": "part"},
            ],
        },
        {
            "name": "End Stop",
            "intent": "assembly",
            "children": [
                {"name": "End Stop Bracket",   "intent": "part"},
                {"name": "Linear Bearing Block","intent": "part",
                 "shared_id": "lbb_8mm"},     # same component as in Carriage
            ],
        },
    ],
}
```

### Field rules

| Field | Required | Values | Notes |
|---|---|---|---|
| `name` | yes | string | Becomes the component name and the external doc name. |
| `intent` | yes | `"part"`, `"assembly"`, `"hybrid"` | Maps to the `DesignIntentTypes` constants below. |
| `children` | conditional | list of nodes | Required for `assembly` / `hybrid`. **Forbidden** for `part` — parts are leaves. |
| `shared_id` | optional | string | Tag identifying nodes that should resolve to the **same** external file. The first occurrence is created; subsequent occurrences are inserted by reference after a save. |

### Intent → API constant map

```python
INTENT_MAP = {
    "part":     adsk.fusion.DesignIntentTypes.PartDesignIntentType,      # 0
    "assembly": adsk.fusion.DesignIntentTypes.AssemblyDesignIntentType,  # 1
    "hybrid":   adsk.fusion.DesignIntentTypes.HybridDesignIntentType,    # 2
}
```

---

## Pre-Flight Guards (4 checks, in order)

Run these **before** creating anything. If any fail, stop and report — do not
attempt partial builds.

```python
def _validate_target_document(app, ui):
    """Return (design, doc) on success, raise RuntimeError with user-readable message on failure."""
    product = app.activeProduct
    if not product or not isinstance(product, adsk.fusion.Design):
        raise RuntimeError("Assembly Builder requires an active Fusion Design.")

    design = adsk.fusion.Design.cast(product)
    doc = app.activeDocument

    # Guard 1 — must be a new, unsaved document
    if doc.isSaved:
        raise RuntimeError(
            "Assembly Builder only works on new, unsaved documents. "
            "Create a new Design (File > New Design) and try again."
        )

    # Guard 2 — must be Assembly or Hybrid intent (not Part)
    if design.designIntent == adsk.fusion.DesignIntentTypes.PartDesignIntentType:
        raise RuntimeError(
            "Active design has Part intent. Switch to Assembly or Hybrid, "
            "or create a new document."
        )

    # Guard 3 — root must be empty
    if design.rootComponent.occurrences.count > 0:
        raise RuntimeError(
            "Active design already has components. Start with an empty Design."
        )

    return design, doc
```

**Why all four matter:**

- **Active Design check** — prevents the script firing in CAM/Drawing/Render workspaces.
- **Unsaved check** — `addNewExternalComponent` behavior on already-saved docs creates external files in the project root rather than under the active document; the new-doc guarantee keeps file placement predictable.
- **Intent check** — Part-intent documents cannot contain occurrences. The API will refuse `addNewExternalComponent` and the error is opaque if you don't pre-check.
- **Empty-root check** — prevents accidentally appending a generated structure to a partially-built design and making a mess.

---

## Build Algorithm (Top-Down with Deferred Shared Inserts)

This is the proven core. Two passes:

1. **Pass 1 — Create** Recurse top-down. For each non-shared node create the
   external component and set its intent. For each shared node already
   created, **defer** the extra insert.
2. **Pass 2 — Resolve shared** After Pass 1, save the document so each
   external component has a `DataFile`. Then walk the deferred list and
   insert each shared component by reference into its additional parents.

```python
import adsk.core, adsk.fusion

INTENT_MAP = {
    "part":     adsk.fusion.DesignIntentTypes.PartDesignIntentType,
    "assembly": adsk.fusion.DesignIntentTypes.AssemblyDesignIntentType,
    "hybrid":   adsk.fusion.DesignIntentTypes.HybridDesignIntentType,
}


def build_hierarchy(hierarchy: dict) -> str:
    """
    Build a Fusion product structure from a nested hierarchy dict.
    Returns a human-readable result message.
    """
    app = adsk.core.Application.get()
    ui = app.userInterface

    # 0 — guards
    design, doc = _validate_target_document(app, ui)

    folder = app.data.activeProject.rootFolder      # default target folder
    transform = adsk.core.Matrix3D.create()         # identity = origin
    root_comp = design.rootComponent

    # 1 — set the root document's intent to match the root node
    root_intent = INTENT_MAP.get(
        hierarchy.get("intent"),
        adsk.fusion.DesignIntentTypes.AssemblyDesignIntentType,
    )
    design.designIntent = root_intent

    # State for shared-component handling
    created_by_shared_id: dict[str, adsk.fusion.Occurrence] = {}
    deferred_inserts: list[tuple] = []  # [(parent_comp, shared_id, name), ...]
    created_count = 0

    def create_children(parent_comp: adsk.fusion.Component, node: dict):
        nonlocal created_count
        for child in node.get("children", []) or []:
            name        = child["name"]
            intent_key  = child["intent"]
            shared_id   = child.get("shared_id")

            # If this is a shared node already created, defer to Pass 2
            if shared_id and shared_id in created_by_shared_id:
                deferred_inserts.append((parent_comp, shared_id, name))
                continue

            # Pass 1 — create external component
            occ = parent_comp.occurrences.addNewExternalComponent(
                name, folder, transform
            )
            if not occ:
                # Skip silently — addNewExternalComponent returns None on failure
                continue

            created_count += 1
            child_comp = occ.component

            # Set intent on the child's OWN design (not the parent design)
            intent = INTENT_MAP.get(intent_key)
            if intent is not None:
                try:
                    child_comp.parentDesign.designIntent = intent
                except Exception:
                    pass  # best-effort; some configurations may reject

            # Track first creation under its shared_id so siblings can reuse it
            if shared_id:
                created_by_shared_id[shared_id] = occ

            # Recurse only for assemblies/hybrids — parts are leaves
            if intent_key in ("assembly", "hybrid"):
                create_children(child_comp, child)

    # Pass 1
    create_children(root_comp, hierarchy)

    # Pass 2 — resolve deferred shared inserts
    if deferred_inserts:
        doc.save("Assembly Builder: enabling shared component references")
        adsk.doEvents()

        for parent_comp, shared_id, _name in deferred_inserts:
            seed_occ = created_by_shared_id.get(shared_id)
            if not seed_occ:
                continue
            try:
                data_file = seed_occ.component.parentDesign.parentDocument.dataFile
                if data_file:
                    parent_comp.occurrences.addByInsert(data_file, transform, True)
                    created_count += 1
            except Exception:
                pass

    msg = f"Created {created_count} component(s)."
    if deferred_inserts:
        msg += f" ({len(deferred_inserts)} shared reference(s) inserted.)"
    return msg
```

### Critical correctness points (do not "simplify" these away)

1. **Intent goes on the child's design, not the parent's.** Each external
   component lives in its own document. Use:
   ```python
   child_comp.parentDesign.designIntent = ...
   ```
   Setting `design.designIntent` (the root design) only changes the root
   document. This is the most common mistake.

2. **Recurse only for `assembly` and `hybrid`.** A `part` node is a leaf. If
   `children` is present on a `part` node, treat it as an authoring error
   (raise during validation, see below) — silently ignoring children
   produces a structure that doesn't match the user's intent.

3. **Shared inserts must happen *after* a save.** `addByInsert` requires a
   `DataFile`, which only exists after the host document is saved. Trying
   it before the save returns nothing or raises.

4. **`addByInsert(data_file, transform, isReference=True)`** — the third
   argument controls whether the inserted component is a reference (live
   link) or a copy. We always pass `True` because shared components are
   meant to update together.

5. **Identity transform is correct for product-structure scaffolding.**
   Every occurrence is placed at the parent's origin. Positioning happens
   later via joints / Ground to Parent — not at structural creation time.

6. **`folder = app.data.activeProject.rootFolder`** is the proven target
   folder argument. Passing `None` works in some cases but is undocumented;
   the project root folder is reliable.

---

## Recommended Pre-Build Validation

Before invoking `build_hierarchy`, validate the dict in pure Python so
errors surface immediately and don't leave a half-built document:

```python
def validate_hierarchy(node: dict, path: str = "root") -> list[str]:
    """Return a list of human-readable error messages. Empty list = valid."""
    errors = []
    if "name" not in node or not str(node.get("name", "")).strip():
        errors.append(f"{path}: missing or empty 'name'")
    intent = node.get("intent")
    if intent not in ("part", "assembly", "hybrid"):
        errors.append(f"{path}: invalid intent {intent!r}")
    children = node.get("children", []) or []
    if intent == "part" and children:
        errors.append(f"{path} ({node.get('name')}): part nodes cannot have children")
    if intent in ("assembly", "hybrid") and not children:
        errors.append(f"{path} ({node.get('name')}): {intent} node has no children")
    for i, ch in enumerate(children):
        errors.extend(validate_hierarchy(ch, f"{path}/{node.get('name')}[{i}]"))
    return errors
```

Call this first. If it returns anything, present the errors to the user
and stop — do not call `build_hierarchy`.

---

## Researching Product Structure

When the user says *"scaffold a planetary gearbox"* or *"set up a typical
linear stage"*, the structure dict is the **deliverable of research, not a
guess**. Workflow:

1. **Identify the canonical machine elements.** Use web search if not
   already known. For a planetary gearbox: sun gear, ring gear, planet
   carrier, planet gears, output shaft, input shaft, housing, bearings,
   fasteners.
2. **Decide the assembly hierarchy** — what naturally groups into a
   sub-assembly vs. lives at the top level. Generally: anything that is
   pre-assembled before final assembly is a sub-assembly. A planet carrier
   with its planet gears mounted on pins is a sub-assembly; the housing is
   typically a single part.
3. **Identify shared components.** Multiple identical bearings, fasteners,
   or planet gears should share a `shared_id` so they resolve to a single
   external file.
4. **Show the structure to the user as a tree before building** — give
   them a chance to add/remove/rename. Do **not** call `build_hierarchy`
   without confirmation; it produces real files in their active project.

### Default presentation format

Always render the proposed structure to the user as an indented tree
with intent tags before the build call:

```
Planetary Gearbox  [assembly]
├── Housing  [part]
├── Input Shaft Subassembly  [assembly]
│   ├── Input Shaft  [part]
│   ├── Sun Gear  [part]
│   └── Bearing 6204  [part, shared:b6204]
├── Carrier Subassembly  [assembly]
│   ├── Planet Carrier  [part]
│   ├── Planet Gear  [part, shared:pgear]   (×3 instances)
│   └── Planet Pin  [part, shared:ppin]     (×3 instances)
├── Ring Gear  [part]
└── Output Shaft Subassembly  [assembly]
    ├── Output Shaft  [part]
    └── Bearing 6204  [part, shared:b6204]  (shared with input)
```

Then ask: *"Build this structure as-is, or want to change anything first?"*

---

## Drawflow JSON (Original Add-In Format)

The PowerTools Assembly Builder palette stores the graph as Drawflow JSON
with this shape:

```python
{
    "drawflow": {
        "Home": {
            "data": {
                "<node_id>": {
                    "name": "part" | "assembly" | "hybrid",
                    "data": {"name": "<component name>"},
                    "class": "is-root" | "",
                    "inputs":  {"input_1":  {"connections": [{"node": "<id>"}]}},
                    "outputs": {"output_1": {"connections": [{"node": "<id>"}]}},
                },
                ...
            }
        }
    }
}
```

Use this format only when round-tripping with the actual palette. For
direct MCP scripting, prefer the nested-dict schema above and convert if
needed. The original recursion and shared-node detection live in
`entry.py` of the `PTAT-AssemblyBuilder` command.

---

## Example: Full MCP Session

This is the canonical end-to-end script. Execute via `fusion_mcp_execute`.

```python
import adsk.core, adsk.fusion, traceback

# (Paste INTENT_MAP, _validate_target_document, validate_hierarchy,
#  and build_hierarchy from above.)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        hierarchy = {
            "name": "Linear Stage",
            "intent": "assembly",
            "children": [
                {"name": "Base Plate", "intent": "part"},
                {
                    "name": "Carriage",
                    "intent": "assembly",
                    "children": [
                        {"name": "Carriage Body", "intent": "part"},
                        {"name": "Bearing Block", "intent": "part",
                         "shared_id": "bb"},
                    ],
                },
                {
                    "name": "End Stop",
                    "intent": "assembly",
                    "children": [
                        {"name": "End Stop Bracket", "intent": "part"},
                        {"name": "Bearing Block", "intent": "part",
                         "shared_id": "bb"},
                    ],
                },
            ],
        }

        errors = validate_hierarchy(hierarchy)
        if errors:
            ui.messageBox("Invalid hierarchy:\n" + "\n".join(errors))
            return

        result = build_hierarchy(hierarchy)
        ui.messageBox(result)

    except:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")
```

---

## Failure Modes & Recovery

| Symptom | Cause | Fix |
|---|---|---|
| `addNewExternalComponent` returns `None` | Document was saved before build, or root not empty, or Part intent | Verify all 4 pre-flight guards passed. |
| Shared insert raises "no DataFile" | `doc.save()` skipped or returned without completing | Ensure `adsk.doEvents()` is called after save; check the user has write access to the active project. |
| Intent reverts to default after build | Tried to set intent on `design.designIntent` instead of `child_comp.parentDesign.designIntent` | Use the child's own design — see Critical Point #1. |
| Structure built but components stacked at origin | Expected — identity transform is the design choice | Position later via joints / Ground to Parent. |
| Build aborts halfway, partial structure left | One of the create calls raised an unhandled exception | The active doc is still unsaved. Close without saving and re-run from a fresh new document. |

---

## When NOT to Use This

- **Single-document part** — just open a new Part-intent design and start sketching. The whole pipeline assumes hierarchy.
- **Modifying an existing assembly** — guards explicitly forbid this. To
  add components to a populated assembly, use the regular `create component`
  flow in `scripting.md` § *Components & External Files*.
- **When the user wants joints/positions** — this scaffolds *structure*,
  not motion. Joints come after.
