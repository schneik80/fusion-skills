---
name: fusion-wcs-orientation
description: >
  Detect and apply the correct Fusion 360 WCS (World Coordinate System) orientation before
  modeling anything. Use this skill at the START of every Fusion design task — before
  choosing sketch planes, writing extrude directions, or placing geometry. ALWAYS trigger
  this skill when: starting a new design, modeling any object in Fusion, choosing which
  plane to sketch on, or any time orientation of a model might matter. Fusion users have
  two common setups: Z-Up (Fusion default, front = XZ plane) or Y-Up (SolidWorks / mechanical
  CAD convention, front = XY plane). Getting this wrong means everything ends up sideways
  or upside-down. This skill detects the user's setting from the Fusion API and tells you
  exactly which plane to use and which axis to extrude along.
---

# Fusion 360 WCS Orientation Detection

## Why This Matters

Fusion 360 supports two WCS orientations, set in **Preferences → General → Default Modeling Orientation**:

| Setting | "Up" axis | Front view plane | Depth axis |
|---------|-----------|-----------------|------------|
| **Z-Up** (Fusion default) | Z+ | XZ plane (Y+ = into screen) | Y axis |
| **Y-Up** (SolidWorks / mech. CAD) | Y+ | XY plane (Z+ = toward camera) | Z axis |

Using the wrong plane means your model is rotated 90° relative to what the user sees as "front."

---

## Step 1: Detect the User's Setting

**Always run this script first** before any modeling work:

```python
import adsk.core, adsk.fusion

def run(_context):
    app = adsk.core.Application.get()
    gp = app.preferences.generalPreferences
    orient = gp.defaultModelingOrientation

    Z_UP = adsk.core.DefaultModelingOrientations.ZUpModelingOrientation  # value = 1
    Y_UP = adsk.core.DefaultModelingOrientations.YUpModelingOrientation  # value = 0

    if orient == Z_UP:
        print('ORIENTATION: Z-UP')
    else:
        print('ORIENTATION: Y-UP')
```

The result tells you everything — no guessing, no heuristics.

---

## Step 2: Apply the Correct Plane Mapping

### Z-Up orientation (value = 1, Fusion default)

```python
root = design.rootComponent
front_plane  = root.xZConstructionPlane  # What user sees as "front"
side_plane   = root.yZConstructionPlane  # Right side
top_plane    = root.xYConstructionPlane  # Top-down plan view

# Extrude direction: use Y axis for "depth into the model"
# When sketching a front profile, extrude along +Y
```

Coordinate semantics:
- X+ = right
- Z+ = up  
- Y+ = into the screen (away from the user in front view)

### Y-Up orientation (value = 0, SolidWorks / mech. CAD convention)

```python
root = design.rootComponent
front_plane  = root.xYConstructionPlane  # What user sees as "front"
side_plane   = root.yZConstructionPlane  # Right side (rotated)
top_plane    = root.xZConstructionPlane  # Top-down plan view

# Extrude direction: use Z axis for "depth into the model"
# When sketching a front profile, extrude along +Z
```

Coordinate semantics:
- X+ = right
- Y+ = up
- Z+ = toward the camera in front view

---

## Step 3: Helper Function to Use in Scripts

Include this at the top of any modeling script to get the correct planes automatically:

```python
import adsk.core, adsk.fusion

def get_orientation(root):
    """
    Returns a dict with the correct plane references and axis labels
    based on the user's WCS preference.
    """
    app = adsk.core.Application.get()
    orient = app.preferences.generalPreferences.defaultModelingOrientation
    Z_UP = adsk.core.DefaultModelingOrientations.ZUpModelingOrientation

    if orient == Z_UP:
        return {
            'mode': 'Z-UP',
            'front':  root.xZConstructionPlane,
            'top':    root.xYConstructionPlane,
            'side':   root.yZConstructionPlane,
            'depth_axis': 'Y',   # extrude "into" model along Y
            'up_axis': 'Z',
            'right_axis': 'X',
        }
    else:
        return {
            'mode': 'Y-UP',
            'front':  root.xYConstructionPlane,
            'top':    root.xZConstructionPlane,
            'side':   root.yZConstructionPlane,
            'depth_axis': 'Z',   # extrude "into" model along Z
            'up_axis': 'Y',
            'right_axis': 'X',
        }

# Usage:
# ori = get_orientation(root)
# sk = root.sketches.add(ori['front'])
# print(f"User is in {ori['mode']} mode — front plane is {ori['front'].name}")
```

---

## Quick Reference Card

```
                Z-UP (Fusion default)        Y-UP (SolidWorks-style)
                ─────────────────────        ──────────────────────
Front view:     XZ plane                     XY plane
Top view:       XY plane                     XZ plane
Side view:      YZ plane                     YZ plane
"Up" axis:      Z+                           Y+
Depth axis:     Y  (for extrudes)            Z  (for extrudes)
Cam up vector:  (0, 0, 1)                    (0, 1, 0)
```

---

## Common Mistakes to Avoid

1. **Don't hardcode `root.xYConstructionPlane` as "front"** — it's only front in Y-Up mode.
2. **Don't assume extrude direction** — in Z-Up, extruding a front sketch along Z goes "up", not "into" the model.
3. **Camera up-vector can also be used as a cross-check** — in Z-Up, `camera.upVector ≈ (0,0,1)`; in Y-Up, `≈ (0,1,0)`. But prefer the preferences API as it's authoritative.
4. **The setting persists per-user, not per-document** — it's a global preference. Don't re-detect it per feature; detect once per session.

---

## Integration with Other Skills

When using this skill alongside `fusion-design-practices`:
- Use `ori['front']` wherever that skill says "use component origin planes."
- The "logical" sketch plane for a typical object profile is always `ori['front']`.
- For top-down layout sketches (plan views), use `ori['top']`.
