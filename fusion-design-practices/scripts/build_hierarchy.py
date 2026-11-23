# build_hierarchy.py
#
# Standalone Autodesk Fusion script that builds a multi-level external-component
# product structure from a nested-dict hierarchy. Distilled from the IMA
# PowerTools-Assemblies "Assembly Builder" command.
#
# Usage:
#   1. Open a NEW Fusion design (File > New Design — leave it unsaved).
#   2. Edit the `HIERARCHY` dict at the bottom of this file.
#   3. Run via fusion_mcp_execute, or paste into the Scripts editor.
#
# See references/assembly-builder.md for the full schema and rationale.

import adsk.core
import adsk.fusion
import traceback


INTENT_MAP = {
    "part":     adsk.fusion.DesignIntentTypes.PartDesignIntentType,
    "assembly": adsk.fusion.DesignIntentTypes.AssemblyDesignIntentType,
    "hybrid":   adsk.fusion.DesignIntentTypes.HybridDesignIntentType,
}


def validate_hierarchy(node, path="root"):
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


def _validate_target_document(app):
    product = app.activeProduct
    if not product or not isinstance(product, adsk.fusion.Design):
        raise RuntimeError("Assembly Builder requires an active Fusion Design.")

    design = adsk.fusion.Design.cast(product)
    doc = app.activeDocument

    if doc.isSaved:
        raise RuntimeError(
            "Assembly Builder only works on new, unsaved documents. "
            "Create a new Design (File > New Design) and try again."
        )

    if design.designIntent == adsk.fusion.DesignIntentTypes.PartDesignIntentType:
        raise RuntimeError(
            "Active design has Part intent. Switch to Assembly or Hybrid, "
            "or create a new document."
        )

    if design.rootComponent.occurrences.count > 0:
        raise RuntimeError(
            "Active design already has components. Start with an empty Design."
        )

    return design, doc


def build_hierarchy(hierarchy):
    app = adsk.core.Application.get()
    design, doc = _validate_target_document(app)

    folder = app.data.activeProject.rootFolder
    transform = adsk.core.Matrix3D.create()
    root_comp = design.rootComponent

    design.designIntent = INTENT_MAP.get(
        hierarchy.get("intent"),
        adsk.fusion.DesignIntentTypes.AssemblyDesignIntentType,
    )

    created_by_shared_id = {}      # shared_id -> first Occurrence
    deferred_inserts = []          # [(parent_comp, shared_id, name)]
    created_count = 0

    def create_children(parent_comp, node):
        nonlocal created_count
        for child in node.get("children", []) or []:
            name       = child["name"]
            intent_key = child["intent"]
            shared_id  = child.get("shared_id")

            if shared_id and shared_id in created_by_shared_id:
                deferred_inserts.append((parent_comp, shared_id, name))
                continue

            occ = parent_comp.occurrences.addNewExternalComponent(
                name, folder, transform
            )
            if not occ:
                continue

            created_count += 1
            child_comp = occ.component

            intent = INTENT_MAP.get(intent_key)
            if intent is not None:
                try:
                    child_comp.parentDesign.designIntent = intent
                except Exception:
                    pass

            if shared_id:
                created_by_shared_id[shared_id] = occ

            if intent_key in ("assembly", "hybrid"):
                create_children(child_comp, child)

    create_children(root_comp, hierarchy)

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


# ---- Edit this hierarchy and run -----------------------------------------

HIERARCHY = {
    "name": "Linear Stage",
    "intent": "assembly",
    "children": [
        {"name": "Base Plate", "intent": "part"},
        {
            "name": "Carriage",
            "intent": "assembly",
            "children": [
                {"name": "Carriage Body",  "intent": "part"},
                {"name": "Bearing Block",  "intent": "part", "shared_id": "bb"},
            ],
        },
        {
            "name": "End Stop",
            "intent": "assembly",
            "children": [
                {"name": "End Stop Bracket", "intent": "part"},
                {"name": "Bearing Block",    "intent": "part", "shared_id": "bb"},
            ],
        },
    ],
}


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        errors = validate_hierarchy(HIERARCHY)
        if errors:
            ui.messageBox("Invalid hierarchy:\n" + "\n".join(errors))
            return

        result = build_hierarchy(HIERARCHY)
        ui.messageBox(result)

    except Exception:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")
