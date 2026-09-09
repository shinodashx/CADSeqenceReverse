---
name: reconstructing-cadquery-from-point-clouds-en
description: "Analyzes NPY, PLY, XYZ files or pasted XYZ coordinates and reconstructs editable, sequential CadQuery CAD features with measured accuracy. Use for point-cloud-to-CAD reverse engineering, dimension recovery, and fillet/junction refinement, not mesh conversion or global surface fitting. English workflow; choose this or the Chinese edition."
---

# Point Clouds to Sequential CadQuery Reconstruction

Treat points as measurement evidence, not geometry to convert. **NPY, PLY, and pasted XYZ must follow the same path: read → analyze → feature/dimension evidence → CAD operation plan → sequential modeling → error-driven refinement.**

## Non-negotiable rules

- Read only XYZ vertices from PLY, even when faces exist. Never substitute Poisson/alpha-shape reconstruction, triangle sewing, mesh-to-solid conversion, or global NURBS fitting for CAD reconstruction.
- Allow local plane/circle/cylinder/arc estimation for **measurement**, and optimization of a few meaningful dimensions within a fixed feature structure. Do not build the final model through per-point high-order splines or cloud wrapping.
- Make the final `sequence_cq.py` depend only on CadQuery, the standard library, and explicit parameters—not point clouds, old STL/STEP/BRep geometry, or analysis scripts. Use explicit linear S01, S02… steps, not whole-model functions/loops. Prefer patterns and mirrors for repetition.
- Keep faithful reconstruction separate from functional redesign. Do not invent hidden bearings or brakes from an object category. Sparse points cannot guarantee unique recovery of original CAD history or arbitrary absolute accuracy.

## Workflow

1. **Accept input.** Read files directly; preserve pasted coordinates verbatim. For truncation, missing rows, or ellipses, find the complete attachment or request it. Record source hash, point count, indices, units, and tolerance. Never silently scale, transpose, delete, or deduplicate. Run the reader below and inspect statistics and projections.
2. **Understand afresh.** Inspect XY/XZ/YZ, multiple views, and thin slices; use axial–radial sections for revolved parts. Identify planes, axes, thicknesses, steps, hole walls, slots, recesses, bends, and fillets. Treat PCA as axis candidates only; record local-to-world transforms. Partition using source indices without losing sparse small features.
3. **Record evidence.** Write `feature_evidence.csv`: feature/body, source-index file, support count, measured/adopted parameters, residuals, confidence, and assumptions. Separate observed, inferred, and unknown geometry. Compare nominal rounding against measurements.
4. **Plan CAD operations.** Write `feature_plan.md`: S number, body, dependencies, construction plane, sketch dimensions/constraints, operation/direction, expected solid count, and evidence. Select from the table; do not force every operation into the model.
5. **Build and refine.** Write a standalone sequence, primary bodies before details. After complex Booleans/fillets, check every solid for validity, non-emptiness, positive volume, and expected count. Read [references/checklist.md](references/checklist.md) before modeling for junction and acceptance rules. Never skip a failed feature and report success.
6. **Close the accuracy loop.** Measure all points against exported CAD surfaces; add regional, dimensional, and hole/slot checks. Report component and fused surfaces separately. Investigate worst points, refine tessellation, and cross-check STEP faces when needed. Render and inspect overall/back/section/junction views, then rebuild and recheck corrections.
7. **Deliver.** Provide input provenance/report, evidence, plan, `sequence_cq.py`, STEP, requested STL, reproducible validation and per-point errors, and inspected renders. State units, tolerances, approximations, and unobserved regions; disclose unmet targets. Add motion scripts/state checks only when motion is requested.

| Geometric evidence | CAD operations |
|---|---|
| Constant sections, plates, holes, slots, bosses | Sketch + Extrude/Cut/Hole/cskHole |
| Coaxial steps, cones, revolved recesses | Section Sketch + Revolve |
| Constant section along a path / varying sections | Constrained path + Sweep / a few evidenced sections + Loft |
| Open, uniform-thickness walls | Shell, checking removed faces and offset direction |
| Junction transitions, edge breaks | Local Fillet/Chamfer |
| Repetition, symmetry, combination, placement | Circular pattern/Mirror/Boolean/Construction plane/Transform |
| Deletion/replacement | Exclude from active bodies/assembly; do not export tool bodies |

## Tools

`$SKILL_DIR` is this skill's directory. Use an isolated environment for missing dependencies: reading needs `numpy scipy plyfile matplotlib`; verification needs `numpy vtk`; modeling and STEP cross-checks need `cadquery`. Tested with Python 3.11/CadQuery 2.8. Output directories must be new or empty; never overwrite source input.

```bash
# All input formats use the same reading/analysis entry; save pasted XYZ as input_points.txt.
python "$SKILL_DIR/scripts/inspect_cloud.py" input.npy --out analysis
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply --out analysis
python "$SKILL_DIR/scripts/inspect_cloud.py" input_points.txt --out analysis
# Explicitly select XYZ for N×6 etc.; mark units confirmed only with evidence.
# Optional: --xyz-columns 0 1 2 --unit mm --unit-status confirmed

python "$SKILL_DIR/scripts/verify_surface.py" \
  --points analysis/points.npy --source-indices analysis/source_indices.npy \
  --mesh result/component_surfaces.stl --out validation \
  --threshold 0.1 --step result/components.step --exact-worst 20
# 0.1 is illustrative, not a universal tolerance. To enforce a target: --require-within-fraction 0.99
python "$SKILL_DIR/scripts/test_workflow.py"
```

The reader preserves duplicates and rejects nonfinite coordinates; extra columns require explicit selection. The verifier measures point-to-triangle **surface** distances and optional worst-point STEP checks. It does not automatically validate reverse coverage, assemblies, or strength. Complete the checklist; a successful command is not an accuracy guarantee.
