# Scripts

Reusable Fusion MCP utility scripts. Each script has a header comment
describing its purpose, inputs, and outputs.

| Script | Purpose | Reference |
|---|---|---|
| `build_hierarchy.py` | Build a complete external-component product structure (parts + sub-assemblies) from a nested-dict hierarchy. Distilled from PowerTools-Assemblies "Assembly Builder". | `references/assembly-builder.md` |
| `create_mirror.py` | Create a mirrored copy of the active saved design as a new external document. Derives all bodies, scales each component by -1 about its own origin, and saves next to the source. Distilled from PowerTools-PartsManagement "Create Mirrored Design". | `references/assemblies.md` → Mirrors |

To add a new script: include a top-of-file docstring describing usage,
required document state (e.g. "active Design, unsaved, empty root"), and
any input arguments. Cross-link the matching reference doc.
