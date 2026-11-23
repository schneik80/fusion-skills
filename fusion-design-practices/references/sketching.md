# Sketching Best Practices

Sourced from *Fusion Modeling Best Practices* — Kevin's accumulated guidelines.

## Plane & Origin Setup

- Use **component origin planes** as sketch planes.
- Constrain, project, or dimension to the **sketch origin** to anchor geometry.
- When the sketch origin isn't suitable, reference reliable, logical construction geometry instead.
- Only project geometry that is needed — excessive projections create unwanted relationships and confusion.

## Constraints & Dimensions

- Sketches must be **fully constrained** before use.
- Apply constraints and dimensions so that edits produce **predictable** shape changes.
- **Start with constraints, then add dimensions.** Prefer constraints over equivalent dimensions:
  - Perpendicular constraint > 90° angle dimension
  - Equal constraint > two dimensions set to the same parameter
- Minimize patterns and symmetry constraints — overuse causes long compute times.
- **Never use the Fix constraint** — it makes sketches difficult to edit.
- Use **construction lines** to clarify relationships.
- Use **centerlines** for geometry that will be revolved or needs symmetric dimensioning.

## Profiles & Geometry

- Avoid placing fillets and chamfers in sketches; add them as timeline features later unless there is a functional necessity.
- In **simple sketches**, trimming to clean loops is not required.
- In **complex sketches**, trim geometry to reduce profile count — easier profile selection and more stable on edits.
- Keep track of hidden profiles; restore visibility so other users aren't confused.

## Size Guidelines

| Sketch size | Guidance |
|---|---|
| Target | ~25 lines, 10–20 dimensions |
| Maximum practical | ~100 elements |
| Hard limit | 250 elements — beyond this, split or simplify |

Less is more. Break large sketches into smaller, focused ones to make editing easier.

## Making Large Dimension Edits

When changing a dimension by a large amount, step through intermediate values to avoid geometry flipping or solve failures.

*Example: changing 10 mm → 110 mm*
→ Edit to 45, then 80, then 110.

The same incremental approach applies to timeline feature edits (see `modeling.md`).
