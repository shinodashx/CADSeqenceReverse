---
name: reconstructing-cadquery-visually-en
description: "Reconstructs editable CadQuery feature sequences by inspecting only rendered views of NPY, PLY, or pasted XYZ. Use for visual-only point-cloud-to-CAD reconstruction and multi-view iteration. English edition."
---

# Point Cloud → CadQuery Sequence · Visual-only

**Analyze point clouds only through rendered views.** Programs decode, validate completeness, and display data; exclude numerical XYZ feature analysis, fitting, and distance optimization from modeling. Rebuild all CAD geometry with parametric operations and use kernel checks for the CAD's own constraints, topology, and assemblies.

## Workflow

1. **Read.** Use this skill's rendering reader for NPY, PLY, and pasted XYZ; take vertex XYZ from PLY and save pasted content verbatim. Preserve coordinates and row order; record hashes, index convention, and units. Complete partial input before rendering.
2. **Observe.** Inspect orthographic, opposed oblique, rear, and necessary display-slice/local close-up views. Observe inner and outer walls, end faces, holes, slots, symmetry, and transitions separately; confirm features in at least two non-collinear views and record camera, scale, and clipping settings.
3. **Record evidence.** In `feature_evidence.csv`, record feature, screenshot and hash, image region, scale source, estimated range, adopted parameter, and confidence. Separate observed, inferred, and unknown geometry; estimate scale from displayed rulers or known dimensions. For constraint conflicts, first check viewpoint and scale; request critical dimensions that remain unidentifiable.
4. **Plan.** In `feature_plan.md`, define scope, scale basis, coordinate frame, unknown regions, visual targets, and CAD checks. For each S step, record input→output body, dependencies, datum/sketch constraints, named parameters, operation, expected solid count, and screenshot evidence.
5. **Model.** Write a standalone `sequence_cq.py` that depends only on CadQuery, the standard library, and parameters. Make each explicit S01, S02… step one meaningful operation and retain named intermediates. Build datums and primary forms before dependent details; check solids and feature intent after key operations. Read the [checklist](references/checklist.md) before modeling.
6. **Accept and refine.** Validate BRep, multi-view agreement, critical CAD features and assemblies, and actual exports separately. Observe cloud and model side by side with identical camera, scale, and clipping. Follow the [refinement loop](references/refinement.md) to locate the responsible step, edit the sequence, re-export, and recheck every view and previously passing region.
7. **Deliver.** Provide the input report, evidence, plan, sequence, STEP/requested STL, CAD-check commands, revision comparisons, and inspected renders; bind the report to final hashes. Mark pass/fail/limited and cloud numerical accuracy as “not evaluated.” Stop when visual targets are met or stagnation is evidenced; state remaining approximations, save functional redesign separately, and add motion when needed.

## Operation selection

| Feature | Operation |
|---|---|
| Constant sections, plates, bosses, holes, slots | Sketch + Extrude/Cut/Hole |
| Coaxial steps, cones, revolved grooves | Section Sketch + Revolve |
| Constant/varying section along a path | Sweep/a Loft with a few evidenced sections |
| Open uniform-thickness walls | Shell |
| Junction transitions, edge breaks | Local Fillet/Chamfer, ordered by adjacent topology |
| Repetition, symmetry, combination, placement | Circular pattern/Mirror/Boolean/Construction plane/Transform |
| Delete/replace body | Update active bodies and assembly list; export retained final parts |

## Tools

`$SKILL_DIR` is the skill directory and `$INPUT` is an NPY/PLY/XYZ file. Reading/rendering requires `numpy plyfile vtk`; modeling and CAD checks require `cadquery`. Use a new or empty output directory.

```bash
python "$SKILL_DIR/scripts/inspect_cloud.py" "$INPUT" --out views
# Select extra columns explicitly: --xyz-columns 0 1 2; confirmed units: --unit mm --unit-status confirmed
python "$SKILL_DIR/scripts/inspect_cloud.py" "$INPUT" \
  --cad-stl result/component_surfaces.stl --out comparison
# Display focus: --focus X Y Z --view-span H; use identical settings within a comparison
python "$SKILL_DIR/scripts/test_workflow.py"
```

The tool provides seven standard views; inspect them all and add opposed oblique views or display slices as observation requires. Repair the environment when rendering is unavailable, and report the blocker if it remains limited. Accept visual agreement and CAD quality separately.
