# General Reconstruction and Refinement

## Select features

- Compare plane/cylinder, line/arc, extrusion/revolution, and uniform offset/independent walls with identical camera, scale, and display clipping. Save screenshots and region locations; cross-check candidates with additional views.
- Observe end-face orientation, inner/outer walls, transitions, and repeated layouts separately before selecting operations. A section invariant along a line supports Extrude/Sweep; one invariant around an axis supports Revolve; varying sections support Loft.
- Save visually estimated ranges, adopted values, and final view differences separately. Select a few interpretable parameters from multi-view consistency and record unidentifiable dimensions; solve geometric constraints in the new CAD.

## Close the loop every revision

1. **Save a baseline.** Save sequence, screenshot evidence, parameter changes, CAD-check results, and hashes; fix input, frame, units, visual targets, cameras, and tessellation settings.
2. **Locate responsibility.** Inspect every baseline view and trace differences to the first abnormal S step. Distinguish input/display scale, feature hypothesis, estimated dimension, selector/topology, operation order, and export/rendering issues.
3. **Propose a change.** State screenshot counterevidence, candidate operation, and expected improvement region; correct feature type before related dimensions. Change only the responsible step and necessary dependencies; preserve verified features.
4. **Rebuild and check.** Regenerate from the sequence; refresh edge/face selectors after topology changes and verify counts. Recheck the failure first, then every delivered solid, hole/slot, wall thickness, and assembly.
5. **Retest identically.** Rerender actual exports and compare the corrected region, previously passing regions, and critical features view by view; add rear and junction close-ups and record improvements, regressions, uncertainty, and CAD-check results.
6. **Evaluate the candidate.** Keep improvements that are geometrically valid, view-supported, and satisfy critical constraints; record local regressions and revision comparisons. Continue repairing localizable issues and use current-artifact checks in the final report.

## Junction and validation diagnostics

- Correct CAD coordinate truncation, non-tangent sketches, slivers, and misalignment before choosing kernel tolerance from units, smallest feature, and target; recheck volume, holes/slots, and interference after adjustment.
- Observe source-cloud transitions in multiple views and verify fillet addition/removal with CAD tangent points, sections, and adjacent faces. Resolve display overlap or clipping concerns with opaque views, BRep intersection volumes, and CAD sections.
- Repair camera, rendering, or stale-artifact issues before evaluating the model; base source-cloud parameter choices and iteration on view inspection throughout.

## Completion criteria

- **Visual targets met:** Global/local targets agree; solid, mesh, assembly, and export checks pass; actual renders are inspected. Label “visual approximation; cloud numerical accuracy not evaluated.”
- **Limited:** If parameters remain unidentifiable or regressions persist after additional views, display slices, and alternative structures, retain the best valid approximation and list remaining regions, candidates tried, and required views, scales, or denser data.
- Deliver the replayable sequence, reproducible rendering and CAD-check commands, revision comparisons, and final file hashes.
