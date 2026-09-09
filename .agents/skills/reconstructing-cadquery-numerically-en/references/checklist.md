# Modeling and Acceptance Checklist

## Input and evidence

- Read real N×3 NPY with `allow_pickle=False`; select extra columns explicitly. Read ASCII/binary PLY vertices by x/y/z fields and record ignored attributes. Safely parse text tuple arrays or line-based XYZ.
- Preserve coordinates, row order, duplicates, and zero-based original indices; report invalid data first and save cleanup reasons and mappings separately. Record hashes for source and normalized output; verify conversion through coordinate and index consistency.
- Preserve original scale and state assumptions when units are unknown. Record unit conversions and rigid transforms so cloud, CAD, and thresholds share a frame; verify PCA axis direction and handedness.
- Measure inner/outer walls, end faces, and transitions separately; establish holes from wall or boundary evidence and patterns/mirrors from transformed consistency. Record uncertainty from short arcs, sparsity, and occlusion; use a few numerically section-evidenced control parameters for freeform surfaces.

## Sequence and junctions

- Use `feature_plan.md` for scope, datums, unknowns, and acceptance targets; label diagnostic thresholds separately from manufacturing tolerances. Record each step's input body, sketch/datum, parameters, operation, output, and check.
- Keep `sequence_cq.py` as the geometry source and rebuild exports from it. Retain named intermediates; deliver a new replayable sequence whose Python file preserves the operation history.
- Check plane normals, extrusion directions, revolve axes, Sweep section orientation, Loft correspondence, Shell openings/thickness, pattern phase, and transform order.
- At junctions, verify datums, tangent points, wall thickness, motion clearance, and slivers before applying local Fillet/Chamfer. Order them by adjacent topology and downstream features.
- Select edges by body, geometry type, position/direction/radius, and adjacent faces; verify count and location. For fillet failures, check radius, thin walls, and operation order; after edits recheck tangency, thickness, holes/slots, and interference.
- Preserve functional-face fits and keep tool bodies as intermediates. Delete body means excluding it from active bodies/assembly lists and exporting retained final parts.

## Layered acceptance

- Replay in a clean process; check every delivered component and fused variant for valid BRep, expected solids, positive volume, critical dimensions, through holes/slots, and wall thickness. Reimport STEP to verify scale/position; check STL closure, orientation, degenerate faces, and volume.
- Report N, mean, RMS, median, P95, maximum, within-threshold fraction, and worst original indices globally and by region. Retain every input point; also check spatial coverage and density bias.
- Default error is one-way unsigned point→nearest triangle-face distance. Record linear/angular tessellation and recompute with finer meshes for convergence; check critical points against a Compound of STEP **Faces**, label subset size, and avoid zero-distance ambiguity inside solids.
- Use reverse model-surface samples→scan-point distance as a coverage diagnostic; record sampling method/seed and spacing, distinguishing visible, contact, and occluded regions. Validate component surfaces and the final fused body separately and explain removed contact faces.
- For multiple solids, check pairwise intersection volume, fit clearance, and numerical tolerance; locate and resolve positive-volume interference. For motion, retain separate parts, axes, travel, and parent transforms as needed and check contact/limit poses; state discrete sampling and engineering-performance scope.
- Read cloud deviations only from numerical tables, including sections and residual distributions. Separately inspect CAD-only exports in orthographic, opposed oblique, section, and junction close-up views; compare fillet revisions with identical cameras and use CAD images for artifact-quality checks.
- `verify_surface.py` provides full triangle-face residuals and optional STEP subset checks; check reverse coverage, regional semantics, mesh integrity, and assemblies separately. `--require-within-fraction` accepts only the specified surface-threshold fraction.
- Follow the [refinement loop](refinement.md) for unmet items. Bind the report to final input/sequence/export hashes and include commands, results, target status, and remaining approximations; deliver functional redesign separately from faithful reconstruction.
