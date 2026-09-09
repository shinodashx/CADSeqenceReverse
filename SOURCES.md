# Source provenance

Initially imported on 2026-09-07; synchronized with the upstream `main` snapshots below on 2026-09-08. The original repositories were only read, not modified. Upstream skill instructions and scripts are retained unchanged; each directory is independently usable. Only files are imported, not upstream Git history or co-author trailers.

| Local directory | Source directory | Recorded revision |
|---|---|---|
| `.agents/skills/reconstructing-cadquery-from-point-clouds-en/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-from-point-clouds-en/` | [46213b4](https://github.com/shinodashx/Point2CAD/commit/46213b4ce20ba8f315732501c57a0fe9f11058f5) |
| `.agents/skills/reconstructing-cadquery-from-point-clouds-zh/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-from-point-clouds-zh/` | [46213b4](https://github.com/shinodashx/Point2CAD/commit/46213b4ce20ba8f315732501c57a0fe9f11058f5) |
| `.agents/skills/reconstructing-cadquery-numerically-en/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-numerically-en/` | [46213b4](https://github.com/shinodashx/Point2CAD/commit/46213b4ce20ba8f315732501c57a0fe9f11058f5) |
| `.agents/skills/reconstructing-cadquery-numerically/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-numerically/` | [46213b4](https://github.com/shinodashx/Point2CAD/commit/46213b4ce20ba8f315732501c57a0fe9f11058f5) |
| `.agents/skills/reconstructing-cadquery-visually-en/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-visually-en/` | [46213b4](https://github.com/shinodashx/Point2CAD/commit/46213b4ce20ba8f315732501c57a0fe9f11058f5) |
| `.agents/skills/reconstructing-cadquery-visually/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-visually/` | [46213b4](https://github.com/shinodashx/Point2CAD/commit/46213b4ce20ba8f315732501c57a0fe9f11058f5) |
| `.agents/skills/reconstructing-cadquery-sequences-en/` | `shinodashx/step-to-cadquery-skills/skills/reconstructing-cadquery-sequences-en/` | [4e8e196](https://github.com/shinodashx/step-to-cadquery-skills/commit/4e8e1966297187ed9cb375faaf628b88378952e8) |
| `.agents/skills/reconstructing-cadquery-sequences-zh/` | `shinodashx/step-to-cadquery-skills/skills/reconstructing-cadquery-sequences-zh/` | [4e8e196](https://github.com/shinodashx/step-to-cadquery-skills/commit/4e8e1966297187ed9cb375faaf628b88378952e8) |

The Point2CAD root `requirements.txt` is copied unchanged into all six local point-cloud editions, so copying any whole skill retains the shared dependency specification. The project root requirements include the full English edition's identical dependency file for convenient installation. The STEP source provides instructions only, with no scripts or dependency file. Both English and Simplified Chinese editions are included, with separate `README.md` and `README.zh-CN.md` documents. Select one mode and language per task. The Chinese numerical-only and visual-only names intentionally follow upstream without a `-zh` suffix.

This update adds the numerical-only and visual-only point-cloud modes and per-mode refinement references. Full mode is XYZ/Python-led with supporting views. Visual-only supplies matched-camera renders and explicitly leaves point-cloud numerical accuracy unevaluated. STEP instructions remove case-specific history and optional-motion guidance while retaining independent replay and geometric verification.

## Process reference

[earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) informs the separation of authoring and inspection, deterministic validation plus multi-view review, and the repair/rebuild/recheck loop. Point2CAD's upstream README links to this reference. Its build123d/cadgen factories, imported-geometry modeling paths, network downloaders, and runtime are not included.

## Licensing

Neither Shinoda repository contained a license file at the revisions above. Attribution alone does not grant redistribution rights; confirm permission before publishing or redistributing their material. No new license is applied to the imported content here.

The text-to-cad reference is [MIT licensed](https://github.com/earthtojake/text-to-cad/blob/main/LICENSE), copyright 2026 Thompson Labs LLC. No executable code or resource files from that repository are copied into this project.

## Update policy

These are local snapshots, not submodules or live dependencies. To update, explicitly review a new upstream revision, compare the complete skill directory, retain local changes, run the bundled tests, and update this record. Do not silently refresh from upstream or change the original repositories.
