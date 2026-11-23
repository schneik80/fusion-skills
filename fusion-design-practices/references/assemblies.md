# Assembly Best Practices

Sourced from *Fusion Modeling Best Practices* — Kevin's accumulated guidelines.

> **Programmatically scaffolding a full product structure from a research-derived design?** Load `references/assembly-builder.md` instead — it has the proven recursive-build pattern with shared-component handling, extracted from PowerTools-Assemblies.

## Structure & Strategy

- **Use external parts** as often as possible. Large flat assemblies are hard to manage.
- Plan sub-assemblies before inserting components — think about hierarchy early.
- Keep assemblies near the **world origin**. Assemblies far from origin or at odd angles are difficult to measure and reuse.
- Think carefully about what the **first component** should be before inserting anything.
- Use **Ground to Parent** (not Pin, Capture Position, or Move) to fix components.
- Use **folders in Autodesk Fusion Team** to organize major systems. Keep folders under ~200 files.
- Learn and use **skeleton modeling** for complex parametric assemblies.

## Contexts & Associativity

- When creating associative features, **reuse an existing context** when possible.
- Manage contexts actively — the **blue dot** marks out-of-date contexts; update them.
- Avoid creating cross-component references unless they are required for associative parametric design.

## Joint Origins & Mating

- If a face or axis is a key mating surface, create a **joint origin** in the component (not the assembly) to assemble to.
- For frequently reused mating conditions, capture them as joint origins — saves time and avoids constraint problems later.
- When mating symmetric components, mate to **center planes**; return to the assembly plane when practical.

## Mirrors

- Use **Mirror Component sparingly**.
- Preferred approach for a mirrored part:
  1. Derive the seed into a new document.
  2. Scale the body by 1.
  3. Edit the parameter and change the scale factor to −1.
- To automate this workflow via MCP, see `scripts/create_mirror.py` — it derives all bodies from the active saved design, scales each component by -1 about its own origin, and saves the result as `{source}-mirror` next to the source.

## Visibility & Display

- Use **Isolate** to reduce screen clutter and focus on relevant components.
- Use **browser folder visibility overrides** for quick temporary changes only — leaving them on causes sketches, planes, and bodies to disappear, which confuses users.
- Apply **physical materials** to all components to keep COG and mass properties accurate.

## Analysis

- Run an **interference check** before finalizing the assembly.
- **Turn off the contact solver** after analyzing contact motion — leave it on and model updates slow down.

## Component Properties & BOM

- Standardize on component properties and keep them filled out accurately.
- Consistent properties make sorting, searching, and BOM column population automatic.

---

## Exploded Views (Animation Workspace)

- Use the **staging area** to author exploded views — this avoids capturing sequences and makes views easier to modify later.
- When moves need trail lines, enable **Split Transforms**.
- The animation is stored in the **assembly document** — coordinate with collaborators before modifying; exploded views needed for drawings may require a separate document workflow.
- **Camera workflow for drawings:**
  1. Set the camera in the Animation workspace.
  2. Switch to the Design workspace.
  3. Immediately create a new named camera matching the storyboard name.
  This ensures drawing views use the correct camera/storyboard pairing.

---

## Personal Workflow (Kevin's conventions)

These reflect the user's established patterns — treat as first-class requirements:

- When creating a component, always prompt for **design intent type** before scripting:
  - **Hybrid** (`HybridDesignIntentType = 2`) → local component, mixed solid/surface, created with `addNewComponent`
  - **Intent: Assembly** (`AssemblyDesignIntentType = 1`) → external component, created with `addNewExternalComponent`
  - **Intent: Part** (`PartDesignIntentType = 0`) → external component, created with `addNewExternalComponent`
- After creating any component, prompt the user whether to **activate** it.
- To navigate back up: "activate parent" / "return to parent" moves one level up; "activate root" / "return to root" deactivates all and returns to top level.
- From the in-place edit menu at the top center of the graphics area, use **Create Context** to reference required assembly geometry.
- Activate context only when assembly info is needed for associative references.
- Avoid creating references unless required for associative parametric design.
- Use **solid/surface/work geometry and sketches in assemblies** as layout geometry to simplify designs and cross-part relationships.
