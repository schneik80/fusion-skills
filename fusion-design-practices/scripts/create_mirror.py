# create_mirror.py
#
# Standalone Autodesk Fusion script that creates a mirrored copy of the active
# design as a new external document. Distilled from the IMA PowerTools-PartsManagement
# "Create Mirrored Design" command.
#
# How it works:
#   1. Derives all bRep bodies from every component of the source design into a
#      new untitled document.
#   2. For each component (root + every unique component in the occurrence tree),
#      adds a Scale feature anchored at that component's originConstructionPoint
#      with factor 1.0.
#   3. Edits each Scale feature's scaleFactor expression to "-1" — flipping the
#      geometry through the component origin. This is the canonical Fusion mirror
#      workflow (see references/assemblies.md → Mirrors).
#   4. Saves the new document next to the source as "{source}-mirror".
#
# Usage:
#   1. Open and SAVE the source design you want to mirror.
#   2. (Optional) Adjust CONFIG below — mirror name suffix, save comments.
#   3. Run via fusion_mcp_execute, or paste into the Scripts editor.
#
# Prerequisites:
#   - Active document must be a saved Fusion design (has a dataFile).
#   - Source design must contain at least one bRep body.
#
# See references/assemblies.md → Mirrors for the underlying convention.

import adsk.core
import adsk.fusion
import traceback


# ---- CONFIG --------------------------------------------------------------

MIRROR_NAME_SUFFIX = "-mirror"
INITIAL_SAVE_COMMENT = "Mirrored derived design"
SCALE_SAVE_COMMENT = "Created scale features at 1 and edited scale parameters to -1"


# ---- Validation ----------------------------------------------------------


def _validate_source(app):
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        raise RuntimeError("No active Fusion design.")

    active_document = app.activeDocument
    if not active_document:
        raise RuntimeError("No active document.")

    source_data_file = active_document.dataFile
    if not source_data_file:
        raise RuntimeError(
            "Save the current design to Fusion before running this script."
        )

    return design, active_document, source_data_file


# ---- Step 1: derive bodies into a new document ---------------------------


def _collect_source_bodies(source_design):
    """Collect every bRep body from every component of the source."""
    source_entities = []
    for component in source_design.allComponents:
        for body in component.bRepBodies:
            source_entities.append(body)
    return source_entities


def _derive_into_new_document(app, source_design):
    new_document = app.documents.add(
        adsk.core.DocumentTypes.FusionDesignDocumentType
    )
    target_design = adsk.fusion.Design.cast(app.activeProduct)
    if not target_design:
        raise RuntimeError("Failed to create target design document.")

    root_comp = target_design.rootComponent
    derive_features = root_comp.features.deriveFeatures

    source_bodies = _collect_source_bodies(source_design)
    if len(source_bodies) == 0:
        raise RuntimeError("No source bodies found to derive.")

    derive_input = derive_features.createInput(source_design)
    derive_input.sourceEntities = source_bodies
    derive_features.add(derive_input)

    if _count_bodies_in_root(root_comp) == 0:
        raise RuntimeError("No bodies were derived into the new document.")

    return new_document, target_design


def _count_bodies_in_root(root_comp):
    body_count = root_comp.bRepBodies.count
    for occ in root_comp.allOccurrences:
        body_count += occ.bRepBodies.count
    return body_count


# ---- Step 2: save the new document next to the source -------------------


def _save_mirror_document(new_document, source_data_file, mirror_name):
    folder = source_data_file.parentFolder
    if not folder:
        raise RuntimeError("Unable to determine destination folder for mirror design.")

    save_ok = new_document.saveAs(mirror_name, folder, INITIAL_SAVE_COMMENT, "")
    if not save_ok:
        raise RuntimeError(f"Save As failed for {mirror_name}.")


# ---- Step 3: scale every component by -1 --------------------------------


def _collect_component_bodies(component):
    entities = adsk.core.ObjectCollection.create()
    for body in component.bRepBodies:
        entities.add(body)
    return entities


def _add_scale_feature(scale_features, entities, base_point, scale_value):
    scale_input = scale_features.createInput(entities, base_point, scale_value)
    scale_feature = scale_features.add(scale_input)
    if not scale_feature:
        raise RuntimeError("Failed to create scale feature.")
    return scale_feature


def _set_scale_to_negative_one(scale_feature):
    # Fusion rejects negative values on createInput, so we create at 1.0
    # then flip the parameter expression after the fact.
    scale_param = scale_feature.scaleFactor
    if not scale_param:
        raise RuntimeError("Unable to access the scale factor parameter.")
    if scale_param.expression != "-1":
        scale_param.expression = "-1"


def _apply_negative_scale(target_design):
    """
    Iterate root + every UNIQUE component (deduped by entityToken) in the
    occurrence tree, scaling each component's bodies by -1 about its own
    originConstructionPoint.

    Dedup matters: a component instanced N times in allOccurrences would
    otherwise be scaled N times.
    """
    root_comp = target_design.rootComponent
    scale_value = adsk.core.ValueInput.createByReal(1.0)

    components_to_scale = [root_comp]
    seen_tokens = set()

    for occ in root_comp.allOccurrences:
        comp = occ.component
        token = comp.entityToken
        if token in seen_tokens:
            continue
        seen_tokens.add(token)
        components_to_scale.append(comp)

    did_scale = False
    for component in components_to_scale:
        body_entities = _collect_component_bodies(component)
        if body_entities.count == 0:
            continue

        scale_feature = _add_scale_feature(
            component.features.scaleFeatures,
            body_entities,
            component.originConstructionPoint,
            scale_value,
        )
        _set_scale_to_negative_one(scale_feature)
        did_scale = True

    if not did_scale:
        raise RuntimeError("No valid derived bodies found to scale.")


# ---- Orchestration -------------------------------------------------------


def create_mirror():
    app = adsk.core.Application.get()
    source_design, source_document, source_data_file = _validate_source(app)

    source_name = source_document.name
    mirror_name = f"{source_name}{MIRROR_NAME_SUFFIX}"

    new_document, target_design = _derive_into_new_document(app, source_design)

    # Save the file first so the post-derive scale operation can be saved as
    # the next version with its own descriptive comment.
    _save_mirror_document(new_document, source_data_file, mirror_name)

    _apply_negative_scale(target_design)

    new_document.save(SCALE_SAVE_COMMENT)

    return mirror_name


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        mirror_name = create_mirror()
        ui.messageBox(f"Created mirrored design: {mirror_name}")

    except Exception:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")
