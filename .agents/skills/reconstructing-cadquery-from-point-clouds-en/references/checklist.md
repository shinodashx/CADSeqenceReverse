# Modeling and Acceptance Checklist

## Input and measurement

- NPY: `allow_pickle=False`, real N×3; select extra columns explicitly, never automatically transpose 3×N. PLY: read x/y/z fields from ASCII/binary, ignore and record faces/colors/normals. Text: coordinate arrays or whitespace/comma XYZ rows, never `eval`.
- Source indices are zero-based data-row/vertex indices. Reject invalid points by default; document reasons and mappings for any separate cleanup. Preserve duplicates, but also use unique-point/spatial-region statistics to avoid density bias.
- Keep original scale and mark unknown units; declare any provisional millimeter interpretation. Record unit conversion and rigid transforms; points, model, and thresholds must share coordinates. PCA does not establish handedness/axis signs; never silently move the model using ICP to improve residuals.
- Require wall/boundary evidence for holes; missing samples are not holes. Narrow arcs poorly constrain radii. Measure straight/bent wall thickness separately, and end faces/recesses/steps of revolved parts separately. Verify patterns/symmetry before imposing them.
- Keep local optimization small and interpretable. Use a few constrained Sketch/Sweep/Loft sections for complex freeform shapes only when supported, labeling approximations. Do not interpolate every point or chase noise; request more sections/dimensions when needed.

## Sequences and fillet junctions

- Each S step states “input body → datum/sketch → parameterized operation → output body → check.” Preserve named intermediates, not imported bodies. This is a new replayable sequence, not uniquely recovered history; STEP does not preserve Python features.
- Check workplane normals, extrusion direction, revolve axes, sweep section orientation, loft correspondence/twist, shell openings/thickness, pattern phase, and transform order.
- Before filleting a junction, rule out datum misalignment, incorrect thickness, and slivers/micro-steps from rounded clipping coordinates. Never smooth away actual motion clearances.
- Load-bearing concave roots often belong after Union but before holes/slots; edge chamfers often follow root fillets. Adjust to local topology rather than putting all fillets last.
- Select edges by body, geometry, coordinates/direction/radius, and adjacent faces; verify selection count/location. Avoid unstable edge indices and indiscriminate global `edges().fillet()`.
- On failure, inspect radius, adjacent faces, thin walls, and feature order—never `try/except: pass`. Recheck thickness, interference, and tangency after added/removed material. Smooth highlights do not prove geometric tangency.
- Preserve bearing seats, friction faces, locating shoulders, and guide fits. Exclude tool bodies. “Delete body” means explicit active-body/assembly exclusion, not recovered native deletion history.

## Accuracy and final geometry

- Establish surface/key-dimension targets from units, measurement noise, and use. Point spacing is not measurement accuracy. Without a target, report measurements without claiming absolute acceptance.
- Report N, mean, RMS, median, P95, maximum, threshold coverage, and worst source indices globally and by region. Do not delete outliers to improve scores; investigate hole walls, contact faces, and modeling errors first.
- Default distances are one-way unsigned point→nearest triangle face, not nearest vertex or bidirectional Hausdorff. Model→scan samples help detect extra surfaces only in observed regions; label sparse/occluded regions unknown.
- Record linear/angular tessellation settings and check convergence with finer meshes. Cross-check critical points against a Compound of STEP **Faces**, not solid-set distance that may return zero for interior points. Label subset counts; do not call them full-cloud STEP validation.
- Fusion removes contact faces: validate component surfaces and the final fused body separately. This distinction materially changed errors in the caster reconstruction; never report only the smaller result.
- Rebuild in a clean process; reimport STEP to check validity, solid count, key positions, and scale. Check individual STL watertightness, winding, degeneracy, and positive volume; probe/section holes, slots, and walls.
- `verify_surface.py` only supplies full-cloud triangle residuals and optional STEP checks. Add reverse coverage, semantic regions, STL integrity, and assembly checks separately. `--require-within-fraction` enforces only the declared surface-coverage criterion, not every quality gate.
- Inspect actual exported CAD overall/back/section/junction views and residual distributions; use identical-camera before/after views for fillet refinement. Disclose unavailable rendering/inspection rather than using AI-generated illustrations as evidence.

## Assemblies and redesign (only when needed)

- Preserve fixed/rotating/floating bodies, axes, travel, stops, and parent transforms. Never fuse moving bodies and rotate the entire model to imitate a mechanism.
- Check released/contact/limit poses and angular samples; do not silently exempt fasteners from positive-volume interference checks. Discrete checks are not a continuous sweep proof; animation is not friction/braking dynamics.
- Save the faithful reconstruction baseline first. Put tread/brake redesigns in a separate sequence and validate against new design goals, not a claim that the original cloud proves new features.
- Report units/transforms, targets, distance definitions, commands/results, approximations, and deliverables. Static contact is not clamp force; do not guarantee loads, traction, or manufacturing tolerances.

## Skill references and installation

Adapted the concise core/on-demand resources structure from [Codex Skills](https://developers.openai.com/codex/skills/) and [OpenAI skill-creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md), and actual-artifact inspection from the [PDF skill](https://github.com/openai/skills/blob/main/skills/.curated/pdf/SKILL.md). No third-party executable skill tools are imported.

Both language editions contain equivalent rules and identical scripts. Choose one complete directory for project `.agents/skills/` or user `~/.agents/skills/`, retaining subdirectories; install one to avoid duplicate triggers. `agents/openai.yaml` only supplies Codex display metadata, with no MCP. Orb-local files are not automatically published persistently; download them or explicitly authorize publication to a skills repository.
