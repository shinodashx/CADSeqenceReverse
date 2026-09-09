---
name: reconstructing-cadquery-numerically-en
description: "Analyzes NPY, PLY, or pasted point clouds using only XYZ values and Python, then reconstructs editable CadQuery feature sequences and quantifies accuracy. Use for numerical-only point-cloud-to-CAD reconstruction. English edition."
---

# Point Cloud → CadQuery Sequence · Numerical-only

**Analyze point clouds only with XYZ and Python; exclude point-cloud images from analysis and iteration.** Point clouds provide measurement evidence; rebuild all CAD geometry with parametric operations. Use finished-CAD visualization to inspect modeling quality.

## Workflow

1. **Read.** Use this skill's numerical reader for NPY, PLY, and pasted XYZ; take vertex XYZ from PLY and save pasted content verbatim. Preserve coordinates, row order, and duplicates; record hashes, indices, units, and transforms. Complete partial input before analysis.
2. **Analyze.** Identify datums, profiles, thicknesses, holes, slots, and transitions with coordinate distributions, layers, numerical thin sections, and axial–radial measurements. Test inner and outer walls, end faces, symmetry, and tangency separately; use PCA only for axis candidates. Use local fitting for measurement and save scripts and original-index partitions.
3. **Record evidence.** In `feature_evidence.csv`, record feature, region, support count/coverage, measured/adopted parameters, their residuals, and confidence. Separate observed, inferred, and unknown geometry; verify rounding and simplification. For constraint conflicts, first check units, coordinates, and evidence, then confirm unknowns that affect the result.
4. **Plan.** In `feature_plan.md`, define scope, scale basis, coordinate frame, unknown regions, accuracy targets, and checks. For each S step, record input→output body, dependencies, datum/sketch constraints, named parameters, operation, expected solid count, and evidence.
5. **Model.** Write a standalone `sequence_cq.py` that depends only on CadQuery, the standard library, and parameters. Make each explicit S01, S02… step one meaningful operation and retain named intermediates. Build datums and primary forms before dependent details; check solids and feature intent after key operations. Read the [checklist](references/checklist.md) before modeling.
6. **Accept and refine.** Validate BRep, full-cloud/regional errors, critical dimensions and assemblies, and actual exports separately. Locate cloud deviations with numerical tables; separately inspect CAD-only orthographic, opposed oblique, and necessary section/junction views. Follow the [refinement loop](references/refinement.md) to locate the responsible step, edit the sequence, re-export, and run regression checks.
7. **Deliver.** Provide the input report, evidence, plan, sequence, STEP/requested STL, validation commands and errors, revision comparisons, and inspected CAD-only renders; bind the report to final file hashes. Mark pass/fail/not evaluated/limited and remaining approximations. Stop when targets are met or stagnation is evidenced; save functional redesign separately and add motion when needed.

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

`$SKILL_DIR` is the skill directory and `$INPUT` is an NPY/PLY/XYZ file. Reading requires `numpy scipy plyfile`, surface validation requires `numpy vtk`, and modeling plus STEP checks require `cadquery`. Use a new or empty output directory.

```bash
python "$SKILL_DIR/scripts/inspect_cloud.py" "$INPUT" --out analysis
# Select extra columns explicitly: --xyz-columns 0 1 2; confirmed units: --unit mm --unit-status confirmed
python "$SKILL_DIR/scripts/verify_surface.py" \
  --points analysis/points.npy --source-indices analysis/source_indices.npy \
  --mesh result/component_surfaces.stl --out validation \
  --threshold "$TOLERANCE" --step result/components.step --exact-worst 20
python "$SKILL_DIR/scripts/test_workflow.py"
```

Set `$TOLERANCE` to the agreed threshold in task units. The tools provide point-to-triangle-face distances and optional STEP subset checks; accept coverage, topology, critical features, and assemblies separately with the checklist.
