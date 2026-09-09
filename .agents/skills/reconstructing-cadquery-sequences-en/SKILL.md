---
name: reconstructing-cadquery-sequences-en
description: "Reconstructs STEP/STP as independently replayable CadQuery CAD feature sequences, validates accuracy, and exports STL/STEP and images. Use for STEP reverse engineering and explicit body-by-body sequence code; never substitute imported geometry or surface/mesh fitting for modeling. English edition; use instead of the Chinese edition."
---

# STEP → CadQuery Sequence Reconstruction

**Read, measure, understand the design, then rebuild with CAD features and verify.** Deliver executable sequence code, not a STEP converter. This skill works independently; do not also load the Chinese edition.

## Mandatory rules

- **Separate analysis from generation:** Analysis/validation programs may import STEP for inspection. The final modeling program must not read STEP, BREP, STL, meshes, or cached source Shapes. Transfer only meaningful design measurements into code.
- **Features, not geometry transfer:** Do not copy source Faces/Edges, sew source topology, embed B-rep data, copy spline poles, or fit point clouds/surfaces. Use sections for measurement, not as geometry to serialize into the output.
- **One body at a time, top-level execution:** Name sketches, bodies, and cutting tools; construct them with CAD operations, then explicitly `union/cut/intersect`. Do not define modeling functions, lambdas, factory classes, or `build_model()`. Analysis, validation, and rendering tools may use functions.
- **A real sequence:** Select operations for design reasons, not to satisfy an operation checklist. Do not hide construction in enormous coordinate tables or interpreters. `Compound/Assembly` may only combine feature-built bodies.
- **No silent accuracy tradeoffs:** Do not omit small fillets, zero tilts, force coaxiality/mirroring, or substitute approximate surfaces. If tolerances cannot be met, explain why and obtain approval for approximation before treating that output as complete.
- STEP generally lacks the original feature history, and reconstruction is not unique. Do not claim recovery of the original history or guarantee exact parameterization of arbitrary freeform surfaces.

## 1. Check input and environment

- Accept a complete `.step/.stp` or preserve complete pasted text verbatim. Check HEADER/DATA, closing markers, unique entity IDs, reference completeness, and external assembly files. Request missing input; never fabricate entities to repair truncation.
- Preserve the source and its hash; check CadQuery/OCP and rendering tools. The preceding workflow ran with CadQuery 2.8.0; still verify the version used for this task.
- Resolve STEP unit contexts, imported units, and instance transforms. Default outputs to mm; never multiply already-converted geometry by 25.4 again. Account for every in-scope part and instance.

## 2. Measure and plan

- For each logical body, record its frame, bounds, volume/area, centroid, surface types, holes/grooves, axes, radii, thicknesses, tilts, symmetry, and assembly relationships. Distinguish measurements from inferences.
- Create a compact table: `stage | target body | plane/sketch | CAD operation | parameter/unit/evidence | expected result/tolerance`. Measure and reason before coding.
- Honor user tolerances. If absent, disclose provisional diagnostic limits, such as 0.01 mm linear deviation and 1e-4 relative volume difference, adapted to scale and critical fits. These are not universal manufacturing standards; never relax them merely to pass.

## 3. Select features and build body by body

| Design evidence | Preferred operations |
|---|---|
| Constant section; coaxial rotational profile | Sketch + Extrude; half-section Revolve / Revolve cut |
| Curved path or changing cross-sections | Sweep; Loft with explicit sections, guides, and orientation—not fitting in place of reasoning |
| Rounded/beveled edges; thin walls | Fillet; Chamfer; Shell or outer body minus inner body |
| Through/blind/stepped holes; local removal | Hole / counterbore; separate tool + Boolean cut |
| Measured repetition/symmetry | Rectangular/Circular pattern; Mirror |
| Placement, combination, tool removal | Construction plane; Transform; Union/Cut/Intersect; exclude discarded bodies |

- Build each base, then additions/removals, holes, and local finishing in dependency order. `delete body` means excluding tools/temporary bodies from the result, not deleting input files.
- Fuse only components intended to form one solid. Source solid count need not equal design part count; explain repartitioning and map parts to source regions.
- Select fillet/chamfer edges by direction, position, type, length, or adjacency; assert selection counts instead of relying on unstable edge indices. Investigate dimensions/selectors on failure; never swallow errors and skip features.
- Overshoot through-cut tools beyond entry/exit faces to avoid coincident-face failures, without changing blind-hole depths or final dimensions. Avoid near-tangent booleans and check that removal actually occurred. Delay fragile fillets where feature dependencies permit.
- Save a Shape snapshot after each operation in ordered `history`; check `isValid()`, positive volume, expected solid counts, and material changes. Expose `result`, `bodies`, and `history`; make parameter units explicit and convert consistently once.

## 4. Replay independently and close the accuracy loop

1. Review generated code and dependencies for source geometry, dynamic imports, encoded data, and hidden modeling wrappers. Run reviewed code in a fresh directory without source STEP or geometry caches; do not execute unreviewed external code.
2. Export and reimport the reconstructed STEP. Compare logical parts in original coordinates: critical dimensions, positions, hole/shell connectivity, bounds, centroids, areas, and volumes. Face-count differences are diagnostic, not automatic failure; do not auto-align away placement errors.
3. Compute `source.cut(rebuilt)` and `rebuilt.cut(source)`; report missing/excess material and symmetric-difference volume. Sum actual solid volumes only; use source volume as the relative denominator. Boolean failure is not zero error.
4. Check surface deviation in both directions: sample each face and measure point-to-**surface collection** distance on the other model. Report maximum sampled distance/location and sampling density/method; refine small holes, thin walls, fillets, and hotspots. Whole-Shape minimum distance is not maximum deviation; finite samples do not certify a continuous-surface error bound.
5. Diagnose units/transforms first, then specific base, hole/groove, tilt/eccentricity, and fillet stages. Correct, replay, and revalidate the whole model. Report CAD reconstruction error separately from STL discretization; finer meshing cannot fix wrong CAD.
6. Explicitly flag unmet tolerances, incomplete input, or verification limits; never label these “identical.” A skill alone cannot guarantee high accuracy for arbitrary STEP: the current reconstruction needs measured evidence.

## 5. Deliver and inspect rendered results

- Actually generate `model_sequence.py`, a parameter/feature table, `model_rebuilt.step`, `model.stl`, `validation.json`, run instructions, and images; add per-part exports when needed. Document dependencies, commands, units, accuracy, and limitations.
- Treat reconstructed STEP as the CAD validation artifact and STL as a derived mesh. Check every STL component for watertightness, consistent winding, and positive volume; record meshing parameters. Separate source code, original input, and derived artifacts; never mistake stale exports for new results.
- Render and inspect source STEP and **reconstructed STEP** separately from matching viewpoints: opposed isometric views, necessary orthographic/section views, and feature stages. Inspect STL separately for discretization; source or STL images cannot replace reconstructed-CAD inspection.
- Turn every visual suspicion into a dimensional/topological check. Repair the responsible sequence section, rebuild, and rerun failed checks plus potentially affected neighboring features. Report only checks actually executed.
- Provide downloadable code/model packages and inspected images. Claim completion only with independent replay, geometry checks, export reimport, and visual inspection evidence. Similar volume, watertightness, valid solids, or similar appearance alone cannot prove accuracy.

## Lessons from the case and optional motion

- The earlier caster replaced approximately 0.488° tilted conical grooves with coaxial grooves and left some inner transitions sharp, with about 0.2094% volume difference. This is an **approximation example, not a high-accuracy acceptance standard**. Preserve actual tilted construction planes and local finishing; do not pattern asymmetric windows.
- Add motion only when requested: fixed parts may be fused, but keep wheel/hub bodies independent and rotate about the actual wheel-center axis, not the world origin. Test several angles for center/volume invariance, fixed-frame position, and interference; inspect the actual animation.
- Symmetric wheels may use a disclosed display-only angle marker. STL stores no motion, and ordinary STEP does not automatically carry joints/motors. Distinguish static fused exports, separated assemblies, and kinematic demonstrations; do not claim printable movement or valid dynamics without clearance/contact/force verification.

References: [OpenAI skill-creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md), [text-to-cad CAD skill](https://github.com/earthtojake/text-to-cad/blob/main/skills/cad/SKILL.md). Adapt its validation/repair loop, not its build123d/cadgen factories or imported-STEP results; installing that toolchain is not required. Keep this file self-contained.
