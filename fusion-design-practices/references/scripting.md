# Scripting Conventions (Fusion MCP)

Accumulated patterns and hard-won fixes for scripting Autodesk Fusion via the MCP API.
For WCS / plane / axis setup, load `wcs.md` first.

---

## Session Setup

Every script must begin with this boilerplate. Never assume the design or root component exists without getting it from the app object.

```python
import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        root   = design.rootComponent
        # ... your code here
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
```

---

## WCS / Plane Selection

**Always detect orientation before choosing a sketch plane.** See `wcs.md` for the full helper and detection script. Quick summary:

| Preference | Front plane | Top plane | Depth axis |
|---|---|---|---|
| Z-Up (Fusion default) | `root.xZConstructionPlane` | `root.xYConstructionPlane` | Y |
| Y-Up (SolidWorks style) | `root.xYConstructionPlane` | `root.xZConstructionPlane` | Z |

**Kevin's confirmed setting: Z-Up.**
- Front sketch plane → `root.xZConstructionPlane`
- Extrude depth → along Y axis (positive Y = into/away from viewer in front view)

Never hardcode `xYConstructionPlane` as "front" — it is only correct in Y-Up mode.

---

## Sketches

```python
# Always add a sketch to a construction plane, not a BRep face
sketches = root.sketches
sk = sketches.add(root.xZConstructionPlane)  # Z-Up front plane

# Access sketch geometry collections
lines  = sk.sketchCurves.sketchLines
arcs   = sk.sketchCurves.sketchArcs
circles = sk.sketchCurves.sketchCircles
points = sk.sketchPoints

# Close the sketch when done
sk.isVisible = True  # keep visible for reference if needed
```

**Coordinate space warning:** Sketch coordinates are in the sketch's local 2D space, not world/document space. Never mix them. When you need a world-space point on a sketch, use `sketch.modelToSketchSpace()` / `sketchToModelSpace()`.

---

## Extrude Features

```python
prof = sk.profiles.item(0)  # select the profile to extrude

extrudes = root.features.extrudeFeatures
ext_input = extrudes.createInput(
    prof,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation  # or CutFeatureOperation, JoinFeatureOperation
)

# Distance extrude (most common)
distance = adsk.core.ValueInput.createByReal(value_in_cm)  # Fusion API units = cm
ext_input.setDistanceExtent(False, distance)

ext = extrudes.add(ext_input)
```

**Unit reminder:** The Fusion API works in **centimeters** internally. 1 mm = 0.1 cm. Always convert from mm before passing to `createByReal()`.

```python
def mm(val):
    return val * 0.1  # mm → cm for Fusion API
```

---

## Hole Features

**Never create holes by sketching a circle and cutting an extrude.** Always use `holeFeatures`.

Critical constraint: `holeFeatures.add()` requires the sketch to be on a **construction plane**, not a BRep body face. If you sketch on a face and then try to create a hole feature, it will fail.

```python
holes = root.features.holeFeatures

# Build the input — simple drilled hole
hole_input = holes.createSimpleInput(
    adsk.core.ValueInput.createByReal(mm(diameter))
)

# Position: point on a sketch that sits on a construction plane
# The sketch point must be the center of the hole
hole_input.setPositionBySketchPoint(sketch_point)

# Depth — through all
hole_input.setAllExtent(adsk.fusion.ExtentDirections.PositiveExtentDirection)
# or distance:
# hole_input.setDistanceExtent(adsk.core.ValueInput.createByReal(mm(depth)))

hole = holes.add(hole_input)
```

If the hole creation fails, delete **both** the failed feature and its sketch before retrying. Orphaned sketch geometry causes subsequent attempts to fail silently or produce wrong results.

---

## Fillets

```python
fillets = root.features.filletFeatures
fillet_input = fillets.createInput()

# Collect edges — get from BRep body
body = root.bRepBodies.item(0)
edges = adsk.core.ObjectCollection.create()
for edge in body.edges:
    edges.add(edge)

fillet_input.addConstantRadiusEdgeSet(
    edges,
    adsk.core.ValueInput.createByReal(mm(radius)),
    True  # tangent chain — set False when troubleshooting complex geometry
)

fillet = fillets.add(fillet_input)
```

**Tip:** When filleting fails on complex geometry, set the `tangentChain` arg to `False` to reduce the edge set being rounded. Fillet mixed-radius corners first, then remaining edges.

---

## Components & External Files

### Trigger Phrases

When the user says **"create component"** (or similar: "add component", "new component"), always prompt for component type before writing any script.

---

### Step 0 — Guard: Check Active Document Intent

**Before prompting or scripting anything**, check whether the active document allows components to be added. A `PartDesignIntentType` document cannot contain components — stop immediately if detected.

```python
design = adsk.fusion.Design.cast(app.activeProduct)

# designIntent values (adsk.fusion.DesignIntentTypes):
#   PartDesignIntentType     = 0
#   AssemblyDesignIntentType = 1
#   HybridDesignIntentType   = 2
PART_INTENT = adsk.fusion.DesignIntentTypes.PartDesignIntentType

if design.designIntent == PART_INTENT:
    ui.messageBox(
        'Cannot add a component to a Part document.\n'
        'Switch to an Assembly or Hybrid document first.'
    )
    return
```

If the check passes (intent is 1 or 2), continue to Step 1.

---

### Step 1 — Prompt for Design Intent

Ask the user:
> "Should this be a **Hybrid** component or an **Intent-based** component (Assembly or Part)?"

| Choice | Intent Constant | Value | Description |
|--------|----------------|-------|-------------|
| Hybrid | `DesignIntentTypes.HybridDesignIntentType` | `2` | Mixed solid/surface design, local component |
| Intent → Assembly | `DesignIntentTypes.AssemblyDesignIntentType` | `1` | External component, assembly document |
| Intent → Part | `DesignIntentTypes.PartDesignIntentType` | `0` | External component, part document |

After creating, always assign the design intent:
```python
design.designIntent = adsk.fusion.DesignIntentTypes.HybridDesignIntentType  # or Assembly/Part
```

---

### Step 2a — Hybrid Component (local)

Use the existing local component API. Place at origin. Assign a reasonable name derived from context or ask the user.

```python
transform = adsk.core.Matrix3D.create()  # identity = origin (0,0,0)
occ = root.occurrences.addNewComponent(transform)
comp = occ.component
comp.name = 'MyComponent'

# Assign hybrid intent
design = adsk.fusion.Design.cast(app.activeProduct)
design.designIntent = adsk.fusion.DesignIntentTypes.HybridDesignIntentType  # value = 2
```

---

### Step 2b — Intent-Based Component (external)

**First prompt the user for Assembly (1) or Part (0) intent.**

Then use `addNewExternalComponent`. `targetFolder` can be an empty string if no folder is needed.

```python
transform = adsk.core.Matrix3D.create()  # place at origin
componentName = 'MyExternalComponent'    # ask user or derive from context
targetFolder  = None                      # pass None for default folder, or a DataFolder object

occ = root.occurrences.addNewExternalComponent(componentName, targetFolder, transform)
comp = occ.component
comp.name = componentName

# Assign intent — use AssemblyDesignIntentType or PartDesignIntentType
design = adsk.fusion.Design.cast(app.activeProduct)
design.designIntent = adsk.fusion.DesignIntentTypes.AssemblyDesignIntentType  # or PartDesignIntentType
```

---

### Step 3 — Prompt to Activate

After creating (either type), always ask:
> "Should I activate the new component?"

**If yes — activate it:**
```python
ui.activeSelections.clear()
app.activeProduct.activeOccurrence = occ  # activate the new occurrence
```

**If no — leave root active.**

---

### Activating Parent / Root

Recognize all of these phrases as activation navigation commands:

| User says | Action |
|-----------|--------|
| "activate parent" / "return to parent" | Activate the parent occurrence of the currently active component |
| "activate root" / "return to root" | Activate the root component (deactivate all occurrences) |

```python
# Activate root (deactivate all — return to top level)
app.activeProduct.activeOccurrence = None

# Activate parent (one level up)
current_occ = app.activeProduct.activeOccurrence
if current_occ and current_occ.assemblyContext:
    app.activeProduct.activeOccurrence = current_occ.assemblyContext
else:
    app.activeProduct.activeOccurrence = None  # already at root, go to root
```

---

## Parameters

```python
params = design.userParameters

# Add a new parameter
params.add(
    'wall',
    adsk.core.ValueInput.createByReal(mm(3.0)),
    'mm',
    'Nominal wall thickness'
)

# Read an existing parameter value
wall_val = design.userParameters.itemByName('wall').value  # returns cm

# Use a parameter in a feature input
ext_input.setDistanceExtent(
    False,
    adsk.core.ValueInput.createByString('wall')  # reference by name
)
```

---

## Error Handling & Cleanup

**When a feature fails:**
1. Delete the failed feature from the timeline.
2. Delete its associated sketch.
3. Do not leave orphaned sketches — they cause silent failures on retry.
4. Rebuild the sketch cleanly, then recreate the feature.

**Incremental geometry changes:** When changing dimensions by large amounts (same rule as UI editing), modify in steps rather than jumping to the final value. This prevents the solver from flipping or failing geometry.

```python
# Don't do this for large changes:
param.expression = '110mm'

# Do this instead:
for val in ['45mm', '80mm', '110mm']:
    param.expression = val
    design.computeAll()
```

---

## MCP Connectivity

The Fusion MCP server runs on **localhost port 27182**. Claude (running in the cloud) cannot reach localhost directly.

**Required tunnel:** Use ngrok or equivalent to expose port 27182:
```bash
ngrok http 27182
```

Then configure the MCP client to use the ngrok URL. The tunnel must be running before any MCP tool calls will succeed.

**Launching Fusion:** Use the zsh script that finds and launches the most recently modified Fusion app bundle from the webdeploy production directory (avoids stale app bundle issues with multiple installed versions).

---

## Add-in Structure

Standard Fusion add-in layout:

```
MyAddin/
├── MyAddin.py          ← entry point, run() / stop()
├── MyAddin.manifest    ← version, author, description
└── commands/
    └── MyCommand/
        ├── __init__.py
        ├── entry.py    ← CommandCreatedEventHandler
        └── resources/
            ├── 16x16.png
            ├── 32x32.png
            ├── 16x16@1.5x.png  (optional)
            └── Dark/
                ├── 16x16.png
                └── 32x32.png
```

**Icon requirements:** Fusion expects PNG resources in a specific folder structure.
See `assets/` in this skill for icon templates. See `references/icons.md` (add when ready) for the full SVG→PNG conversion workflow (cairosvg, three sizes, light + Dark/ subfolder).

