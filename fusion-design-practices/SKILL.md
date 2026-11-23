---
name: fusion-design-practices
description: "Apply the user's personal Autodesk Fusion design best practices and hard-won conventions whenever working with fusion-mcp. Use this skill for ANY Autodesk Fusion design task — scripting, modeling, assemblies, sketching, feature creation, WCS / orientation setup, troubleshooting, or scaffolding a complete product structure / BOM hierarchy from a research-derived design. Trigger on keywords like: fusion, sketch, component, assembly, extrude, fillet, chamfer, pattern, mirror, joint, parameter, timeline, body, origin plane, context, ground, derive, hole, loft, sweep, EOP, BOM, interference, scaffold, product structure, assembly hierarchy, build assembly, planetary gearbox, linear stage, WCS, Z-Up, Y-Up, orientation. If fusion-mcp is involved in any way, consult this skill first before writing or executing any script."
---

# Autodesk Fusion Design Practices

This skill captures accumulated best practices for Autodesk Fusion modeling. Always apply the relevant sections before generating scripts or giving modeling guidance.

## Quick Reference

| Task | Load Reference |
|------|----------------|
| **Starting any session / new design** | `references/wcs.md` (detect orientation FIRST) |
| Starting a sketch | `references/sketching.md` |
| Building features, parameters, timeline | `references/modeling.md` |
| Assembly structure, joints, contexts | `references/assemblies.md` |
| Exploded views / animations | `references/assemblies.md` → *Exploded Views* section |
| Scaffold a product structure / BOM hierarchy | `references/assembly-builder.md` |
| Mirror an existing part document | `references/assemblies.md` → *Mirrors* + `scripts/create_mirror.py` |
| Scripting conventions (MCP) | `references/scripting.md` |
| Icons / UI assets | `assets/` *(add when ready)* |

## Core Principles (Always Apply)

These apply regardless of task — internalize before reading detail files:

1. **Use origin geometry** — sketch on component origin planes, not body faces. Dimension/constrain to origin or reliable construction geometry.
2. **Fully constrain sketches** — under-constrained sketches break on edits.
3. **Fix errors immediately** — yellow/red timeline features compound into larger failures.
4. **Rename key features and parameters** — unnamed timelines are hard for any user (including future-you) to edit.
5. **Favor single features over multiples** — one hole feature producing 4 holes beats four hole features.
6. **Add fillets, chamfers, decals, and text late** — cosmetic features near the end of the timeline prevent fragile parent/child chains.
7. **No fix constraints** — they make sketches impossible to edit.
8. **External components preferred** — avoid local components unless you have a clear reason.

## When to Load References

- **Any Fusion session start / new design** → load `references/wcs.md` FIRST to detect orientation before any other modeling work
- **Sketching task** → load `references/sketching.md` first
- **Modeling/features/parameters** → load `references/modeling.md`
- **Assembly, joints, contexts, BOM** → load `references/assemblies.md`
- **"Scaffold a <machine>"** / "build the product structure" / "set up components for X" → load `references/assembly-builder.md`
- **Unsure** → load all of them; they are concise

## Personal Workflow Notes

These reflect the user's established workflow — honor these as first-class constraints:

- All components created as **external** by default.
- Use **Create Context** (in-place edit menu) to reference assembly geometry; activate root, save, then open component in its own tab.
- Use **Ground to Parent** to position in-context components — not Pin, Capture Position, or Move.
- Solid/surface/work geometry and sketches used in assemblies as **layout geometry** to simplify cross-part relationships.
- Avoid creating cross-part references unless strictly required for associative parametric design.
