# Source provenance

Imported into this project on 2026-09-07. The original repositories were only read, not modified. Upstream skill instructions and scripts are retained unchanged; each directory is independently usable.

| Local directory | Source directory | Recorded revision |
|---|---|---|
| `.agents/skills/reconstructing-cadquery-from-point-clouds-en/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-from-point-clouds-en/` | [41d6308](https://github.com/shinodashx/Point2CAD/commit/41d63084cf4520a0dccb0b979b7a7780b0b8873e) |
| `.agents/skills/reconstructing-cadquery-from-point-clouds-zh/` | `shinodashx/Point2CAD/skills/reconstructing-cadquery-from-point-clouds-zh/` | [41d6308](https://github.com/shinodashx/Point2CAD/commit/41d63084cf4520a0dccb0b979b7a7780b0b8873e) |
| `.agents/skills/reconstructing-cadquery-sequences-en/` | `shinodashx/step-to-cadquery-skills/skills/reconstructing-cadquery-sequences-en/` | [b4bd3b1](https://github.com/shinodashx/step-to-cadquery-skills/commit/b4bd3b1ae4488452d5a5f7007c82f8646bdff45a) |
| `.agents/skills/reconstructing-cadquery-sequences-zh/` | `shinodashx/step-to-cadquery-skills/skills/reconstructing-cadquery-sequences-zh/` | [b4bd3b1](https://github.com/shinodashx/step-to-cadquery-skills/commit/b4bd3b1ae4488452d5a5f7007c82f8646bdff45a) |

The Point2CAD root `requirements.txt` is also copied unchanged into both local language editions, so copying either whole skill retains its dependency specification. The project root requirements include the English edition's identical dependency file for convenient installation. The STEP source provides instructions only, with no scripts or dependency file. Both English and Simplified Chinese editions are included, with separate `README.md` and `README.zh-CN.md` documents. Select one language edition per task to avoid duplicate triggers.

## Process reference

[earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) informs the separation of authoring and inspection, deterministic validation plus multi-view review, and the repair/rebuild/recheck loop. The STEP skill already links to this reference. Its build123d/cadgen factories, imported-geometry modeling paths, network downloaders, and runtime are not included.

## Licensing

Neither Shinoda repository contained a license file at the revisions above. Attribution alone does not grant redistribution rights; confirm permission before publishing or redistributing their material. No new license is applied to the imported content here.

The text-to-cad reference is [MIT licensed](https://github.com/earthtojake/text-to-cad/blob/main/LICENSE), copyright 2026 Thompson Labs LLC. No executable code or resource files from that repository are copied into this project.

## Update policy

These are local snapshots, not submodules or live dependencies. To update, explicitly review a new upstream revision, compare the complete skill directory, retain local changes, run the bundled tests, and update this record. Do not silently refresh from upstream or change the original repositories.
