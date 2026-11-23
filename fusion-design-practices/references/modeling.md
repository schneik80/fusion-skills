# Modeling Best Practices

Sourced from *Fusion Modeling Best Practices* — Kevin's accumulated guidelines.

## Design Intent

Design intent means building parameters, features, and sketches so the model updates predictably when requirements change.

- **One feature → multiple instances.** Four holes from a single hole feature is better than four separate hole features. Editing one is easier than editing four.
- Start modeling immediately if the design is a single component. For assemblies, create **separate documents** for each part and insert them.
- Use **external components** as the default. Avoid local components unless you specifically understand and need them.

## Parameters

- Define **user parameters** for any dimension used in more than one place (e.g., `wall`, `clearance`, `thread_dia`).
- Use a **consistent naming convention** — autocomplete and design intent both benefit.
- **Mark important parameters as Favorites** so they surface quickly in the parameter dialog.
- Use **equations** to express relationships: rib thickness as a percentage of wall thickness is smarter than a hardcoded value.
- If a parameter has restrictions (e.g., must be 0, 90, 180, or 270), describe the valid values in the **comment field**.

## Timeline Hygiene

- **Rename key features** in the timeline — unnamed timelines are hard to read and edit.
- Fix **yellow and red features immediately** — cascading failures are much harder to repair later.
- Do not leave unneeded features or suppressed features below the EOM marker when the design is complete.
- Avoid unnecessary features and work geometry — they clutter the timeline and slow updates.

## Feature Creation Rules

- **Avoid parent/child relationships** to fragile geometry. Do not reference:
  - Faces or edges of chamfers and fillets
  - Features inside a pattern or mirror (except the seed feature)
  - Edges or seams of non-analytic surfaces (lofts, complex blends)
  - Non-associative cross-component projected geometry that is fixed/grounded
- For concentric holes, use **explicit concentric positioning** (select the circular edge) rather than dragging to the snap point.
- **Pattern features, not sketches** — feature patterns are easier to edit and understand.
- Create **multiple features from a single shared sketch** where applicable — sketch-internal relationships are more robust than inter-feature relationships.
- For symmetric components, model half the body then use **Mirror Body** — faster and smarter than modeling the whole part.
- Add **cosmetic features** (decals, embossed text) late in the timeline.
- Add **fillets, chamfers, and draft** late in the timeline.

## Editing & Change Management

Do not take shortcuts. Edit the actual feature instead of working around it:

| ❌ Shortcut to avoid | ✅ Correct approach |
|---|---|
| Fill a hole to remove it | Delete the hole feature and repair if needed |
| Stack extrudes to make a part longer | Edit the dimension |
| Suppress then create new features | Edit the existing feature |
| Use Move Face to resize | Edit sketch/feature/dimension |

### Making Large Geometry Changes

When changing a feature value by a large amount, step through intermediate values:

1. Drag the **EOP marker** to just after the feature being changed.
2. Make the edit in stages (e.g., 1 → 3 → 6 → 10).
3. Roll the EOP right progressively and repair failures as they appear.

This is faster than letting the full model fail and repairing everything at once.

## Fillets on Difficult Geometry

- Turn off **chain edges** to reduce the edge set being rounded.
- Fillet **corners with mixed radii and convex/concave transitions** first.
- Finish the remaining edges afterward.
