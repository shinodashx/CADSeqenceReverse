# General Reconstruction and Refinement

## Select features

- Compare plane/cylinder, line/arc, extrusion/revolution, and uniform offset/independent walls on the same original-index regions. Record support, coverage, and residuals; cross-check candidates with spatially separated sections.
- Test end-face normals, inner/outer walls, tangent points, and repeated transforms separately before selecting operations. A section invariant along a line supports Extrude/Sweep; one invariant around an axis supports Revolve; varying sections support Loft.
- Save measured values, adopted values, and final CAD distances separately and quantify rounding and simplification effects. Select a few interpretable parameters from section consistency and residual structure; record unidentifiable dimensions.

## Close the loop every revision

1. **Save a baseline.** Save sequence, evidence, parameter changes, check results, and hashes; fix input, frame, units, targets, regions, and tessellation settings.
2. **Locate responsibility.** Inspect out-of-tolerance points and spatial clusters and trace them to the first abnormal S step. Distinguish input/scale, feature hypothesis, dimension, selector/topology, operation order, and export/validation issues.
3. **Propose a change.** State counterevidence, candidate operation, and expected improvement region; correct feature type before related dimensions. Change only the responsible step and necessary dependencies; preserve verified features.
4. **Rebuild and check.** Regenerate from the sequence; refresh edge/face selectors after topology changes and verify counts. Recheck the failure first, then every delivered solid, hole/slot, wall thickness, and assembly.
5. **Retest identically.** Compare all checklist metrics for the full cloud, corrected region, previously passing regions, and critical features; use finer meshes and STEP faces to separate geometric and tessellation errors. Reinspect actual exports and corresponding regions.
6. **Evaluate the candidate.** Keep improvements that are geometrically valid, evidence-supported, and satisfy critical constraints; record local regressions and revision comparisons. Continue repairing localizable issues and use current-artifact checks in the final report.

## Junction and validation diagnostics

- Correct coordinate truncation, non-tangent sketches, slivers, and misalignment before choosing kernel tolerance from units, smallest feature, and target; recheck volume, holes/slots, and interference after adjustment.
- Verify fillet addition/removal with tangent points, sections, adjacent faces, and local residuals. Resolve display overlap or clipping concerns with opaque views, BRep intersection volumes, and sections.
- Repair validator, camera, or stale-artifact issues before evaluating the model.

## Completion criteria

- **Met:** Global/regional and critical-dimension targets are satisfied; solid, mesh, assembly, and export checks pass; actual renders are inspected.
- **Limited:** If parameters remain unidentifiable or regressions persist after testing alternative structures and numerical errors, retain the best valid approximation and list remaining regions/original indices, candidates tried, and required sections, dimensions, or denser data.
- Deliver the replayable sequence, recomputable evidence and validation commands, revision comparisons, and final file hashes.
