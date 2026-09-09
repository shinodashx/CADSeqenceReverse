# Modeling and Acceptance Checklist

## Input and evidence

- Read real N×3 NPY with `allow_pickle=False`; select extra columns explicitly. Read ASCII/binary PLY vertices by x/y/z fields and record ignored attributes. Safely parse text tuple arrays or line-based XYZ.
- Preserve coordinates, row order, duplicates, and zero-based original indices; report invalid data first and save cleanup reasons and mappings separately. Let programs validate input completeness and derive point-cloud feature evidence from inspected renders.
- Preserve original scale and state assumptions when units are unknown; estimate visually from displayed rulers or known dimensions. Keep point cloud and CAD in a common coordinate frame and record transforms; camera framing changes display only.
- Observe inner/outer walls, end faces, and transitions separately; establish holes from wall or boundary views and patterns/mirrors from multi-view consistency. Record uncertainty from short arcs, sparsity, and occlusion; use a few section-view-evidenced control parameters for freeform surfaces.

## Sequence and junctions

- Use `feature_plan.md` for scope, datums, unknowns, and observable targets. Record each step's input body, sketch/datum, parameters, operation, output, and check. Mark cloud numerical accuracy “not evaluated.”
- Keep `sequence_cq.py` as the geometry source and rebuild exports from it. Retain named intermediates; deliver a new replayable sequence whose Python file preserves the operation history.
- Check plane normals, extrusion directions, revolve axes, Sweep section orientation, Loft correspondence, Shell openings/thickness, pattern phase, and transform order.
- At junctions, verify CAD datums, tangent points, wall thickness, motion clearance, and slivers before applying local Fillet/Chamfer. Order them by adjacent topology and downstream features.
- Select edges by body, geometry type, position/direction/radius, and adjacent faces; verify count and location. For fillet failures, check radius, thin walls, and operation order; after edits recheck CAD tangency, thickness, holes/slots, and interference.
- Preserve functional-face fits and keep tool bodies as intermediates. Delete body means excluding it from active bodies/assembly lists and exporting retained final parts.

## Layered acceptance

- Replay in a clean process; check every delivered component and fused variant for valid BRep, expected solids, positive volume, critical CAD dimensions, through holes/slots, and wall thickness. Reimport STEP to verify scale/position; check STL closure, orientation, degenerate faces, and volume.
- Submit all points for rendering and cover critical regions with orthographic, opposed oblique, rear, local display-slice views; record visible and occluded extents. Observe cloud and CAD side by side with identical coordinates, camera, scale, and clipping, retaining an unclipped overview.
- Record profile, opening, connection, and transition agreement by view/region; estimate dimensions visually from rulers. Use local clipping only for display and reverse views to understand contact and occluded faces.
- Save STL linear/angular tessellation settings, refine display to recheck facets, and inspect model structure with CAD BRep sections. Record cloud-image comparison separately from kernel numerical checks on the new CAD.
- For multiple solids, check pairwise intersection volume, fit clearance, and numerical tolerance; locate and resolve positive-volume interference. For motion, retain separate parts, axes, travel, and parent transforms as needed and check contact/limit poses; state discrete sampling and engineering-performance scope.
- Inspect actual exports in orthographic, opposed oblique, section, and junction close-up views; compare fillet revisions with identical cameras. Check components and fused variants separately and explain removed contact faces.
- The rendering tool provides views; check CAD validity, mesh integrity, and assemblies separately with the kernel. When cloud numerical accuracy certification is needed, state this mode's evaluation scope and switch analysis mode with user confirmation.
- Follow the [refinement loop](refinement.md) for unmet items. Bind the report to source file, rendering commands/screenshots, sequence, and export hashes and include check results, target status, and remaining approximations; deliver functional redesign separately from faithful reconstruction.
