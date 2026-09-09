# CADsequenceReverse

**Two independent reconstruction tasks with bilingual Agent Skills for editable CadQuery feature sequences.**

[![简体中文](https://img.shields.io/badge/语言-简体中文-blue)](README.zh-CN.md)

English is the default documentation language. The button opens the separate Simplified Chinese README. Point-cloud reconstruction offers three modes, each in English and Simplified Chinese; STEP reconstruction has two language editions. Select one mode and language per task.

## Contents

- [Task directory](#task-directory)
- [Project layout](#project-layout)
- [Setup](#setup)
- [Task 1 — Point cloud → CadQuery](#task-1)
- [Task 2 — STEP → CadQuery](#task-2)
- [Validation and limitations](#validation-and-limitations)
- [Sources and licensing](#sources-and-licensing)
- [简体中文](README.zh-CN.md)

## Task directory

| Task | Input | English skill | 简体中文技能 | Included tools |
|---|---|---|---|---|
| 1a. Point cloud — full (hybrid) | NPY, PLY, XYZ/text, CSV, coordinate arrays | [SKILL.md](.agents/skills/reconstructing-cadquery-from-point-clouds-en/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-from-point-clouds-zh/SKILL.md) | XYZ/Python measurement leads; views assist; surface verifier and refinement checklist |
| 1b. Point cloud — numerical-only | Same point-cloud formats | [SKILL.md](.agents/skills/reconstructing-cadquery-numerically-en/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-numerically/SKILL.md) | Numerical reader and surface verifier; no point-cloud images in analysis |
| 1c. Point cloud — visual-only | Same point-cloud formats | [SKILL.md](.agents/skills/reconstructing-cadquery-visually-en/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-visually/SKILL.md) | Seven rendered views and source-locked CAD comparison; cloud numerical accuracy not evaluated |
| 2. STEP reconstruction | Complete STEP/STP files or complete STEP text | [SKILL.md](.agents/skills/reconstructing-cadquery-sequences-en/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-sequences-zh/SKILL.md) | Self-contained measurement, modeling, replay, and validation instructions |

These are separate tasks, not a mandatory two-stage pipeline. Both produce new feature-based models, **not imported source geometry disguised as reconstruction**. Neither is a one-command automatic converter.

## Project layout

```text
CADsequenceReverse/
├── README.md
├── README.zh-CN.md
├── SOURCES.md
├── requirements.txt
└── .agents/skills/
    ├── reconstructing-cadquery-from-point-clouds-en/
    ├── reconstructing-cadquery-from-point-clouds-zh/
    ├── reconstructing-cadquery-numerically-en/
    ├── reconstructing-cadquery-numerically/
    ├── reconstructing-cadquery-visually-en/
    ├── reconstructing-cadquery-visually/
    ├── reconstructing-cadquery-sequences-en/
    └── reconstructing-cadquery-sequences-zh/
```

Each point-cloud edition contains `SKILL.md`, `requirements.txt`, `agents/openai.yaml`, `references/checklist.md`, `references/refinement.md`, and `scripts/inspect_cloud.py` / `scripts/test_workflow.py`. Full and numerical-only editions also contain `scripts/verify_surface.py`; visual-only editions do not. Each STEP edition contains a self-contained `SKILL.md`.

## Setup

All eight editions already live in this project's `.agents/skills/`; no global installation or change to either source repository is needed. Reload skills in Amp after adding them, or start a new session in a compatible agent. Explicitly name one mode and language in your prompt. Upstream uses names without a language suffix for the Chinese numerical-only and visual-only editions; their English editions end in `-en`. When installing elsewhere, copy the selected **whole directory** and do not overwrite existing work. Scripts are identical across the two languages of the same mode, not across modes.

From this repository root, use Python 3.11 and an isolated environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
for test in .agents/skills/*/scripts/test_workflow.py; do
  python "$test" || exit 1
done
```

CadQuery is pinned to 2.8.0; other dependencies follow the upstream requirements and are not a full lockfile. The root requirements install the point-cloud toolkit and CadQuery/OCP for both tasks. The STEP skill has no bundled conversion CLI, renderer, or automated reconstruction test suite; the agent must prepare and verify task-specific analysis/rendering tools. No `cadgen`, build123d, MCP server, or external model service is required by these skills.

<a id="task-1"></a>

## Task 1 — Point cloud → CadQuery

**Full mode: read XYZ → analyze with Python (views assist) → record dimensional evidence → plan features → build an explicit sequence → measure and refine.**

Example prompt:

> Use reconstructing-cadquery-from-point-clouds-en to analyze `input.ply`, leading with XYZ values and Python measurements and using views as support. Establish units, feature evidence, and a CAD operation plan before modeling. Deliver a standalone CadQuery sequence, STEP, and an iterative validation report. Do not wrap the cloud or convert a mesh to a solid.

Run input inspection after activating the environment:

```bash
SKILL_DIR=.agents/skills/reconstructing-cadquery-from-point-clouds-en
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply --out analysis
# NPY and saved XYZ text use the same command with a different input filename.
# For extra columns, explicitly add: --xyz-columns 0 1 2
# Only with evidence, add: --unit mm --unit-status confirmed
```

The reader writes `input_report.json`, `points.npy`, `source_indices.npy`, and `projections.png`. It does **not** build CAD. Preserve original units, point order, and duplicates; PLY faces are ignored.

After the agent has built and exported the model, run surface verification:

```bash
python "$SKILL_DIR/scripts/verify_surface.py" \
  --points analysis/points.npy \
  --source-indices analysis/source_indices.npy \
  --mesh result/component_surfaces.stl \
  --out validation --threshold 0.1 \
  --step result/components.step --exact-worst 20 \
  --require-within-fraction 0.99
```

The `result/` files above must already exist. Threshold `0.1` and coverage `0.99` are examples, not universal acceptance criteria; choose them from the task's units and tolerance. Output directories must be new or empty. The verifier writes `point_errors.csv` and `verification.json`, returning a nonzero status when the requested coverage fails.

Deliver input provenance, `feature_evidence.csv`, `feature_plan.md`, standalone `sequence_cq.py`, STEP, requested STL, validation reports, revision comparisons, and inspected renders. Bind reports to final file hashes. See the [acceptance checklist](.agents/skills/reconstructing-cadquery-from-point-clouds-en/references/checklist.md) and [refinement loop](.agents/skills/reconstructing-cadquery-from-point-clouds-en/references/refinement.md).

### Numerical-only mode

> Use reconstructing-cadquery-numerically-en to analyze `input.ply` using only XYZ values and Python. Do not use point-cloud images for analysis or iteration. Deliver numerical evidence and errors, plus CAD-only quality inspection.

Use the inspection and verification commands above with `SKILL_DIR=.agents/skills/reconstructing-cadquery-numerically-en`. Its reader outputs the JSON report and two NPY arrays, but no projection image. CAD-only rendering remains part of final artifact inspection.

### Visual-only mode

> Use reconstructing-cadquery-visually-en to reconstruct `input.ply` from actual rendered views only. Compare matched views and validate the new CAD separately. Mark point-cloud numerical accuracy as not evaluated.

```bash
SKILL_DIR=.agents/skills/reconstructing-cadquery-visually-en
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply --out views
# After generating the reconstructed CAD's STL:
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply \
  --cad-stl result/component_surfaces.stl --out comparison
# Optional display-only zoom: --focus X Y Z --view-span H
```

This reader writes `input_report.json` and seven PNGs (`plus_x`, `minus_x`, `plus_y`, `minus_y`, `plus_z`, `minus_z`, `iso`), not measurement arrays or surface-error reports. The cloud and CAD panels share the source-framed camera; keep focus, scale, and clipping identical in each comparison. Inspect the actual images and supplement opposed oblique views or display slices when needed. Numerical feature fitting and cloud-distance optimization are excluded; CAD validity, topology, and assembly checks remain required.

<a id="task-2"></a>

## Task 2 — STEP → CadQuery

**Inspect source topology/units → measure each body → plan features → rebuild body by body → replay without the source → compare and inspect exports.**

Example prompt:

> Use reconstructing-cadquery-sequences-en to reconstruct `input.step` as an explicit, editable CadQuery sequence. Preserve the source units and assembly placement. Keep STEP imports in analysis only. Replay without the source file, compare missing/excess material and bidirectional sampled surface deviation, and inspect matched source/rebuilt views. Report unmet tolerances.

Deliver `model_sequence.py`, a parameter/feature table, `model_rebuilt.step`, `model.stl`, `validation.json`, run instructions, and inspected images. Modeling code must expose `result`, `bodies`, and ordered `history`; it must not import the source geometry or conceal modeling inside a factory function.

## Validation and limitations

- Review generated code, independently replay it, and reimport the exported STEP before accepting it. Keep original inputs separate from derived outputs.
- Pair deterministic geometry checks with actual multi-view inspection, respecting the selected mode: full-mode image concerns are resolved numerically, numerical-only uses CAD-only images, and visual-only compares source/model views while checking CAD quality separately. Repair the responsible feature, rebuild, and rerun corrected and previously passing regions. This process is informed by [text-to-cad](https://github.com/earthtojake/text-to-cad), without importing its toolchain or model factories.
- In full and numerical-only modes, point-to-STL distances are one-way measurements, not bidirectional Hausdorff distances or complete CAD acceptance. Optional STEP checks cover only selected points unless all are requested. Visual-only does not evaluate point-cloud numerical accuracy.
- Sparse scans do not establish hidden geometry. STEP usually lacks original feature history. Neither task guarantees unique history recovery, arbitrary freeform equivalence, manufacturing fitness, or mechanism dynamics.
- The six point-cloud suites contain seven tests each (42 total), covering reading and mode-specific measurement/rendering, **not automatic reconstruction of arbitrary CAD**. Validate each generated model separately and disclose checks that could not run.

## Sources and licensing

The eight skill directories preserve all upstream modes, both language editions, and supporting files. This project adds organization, separate bilingual READMEs, provenance, and dependency entry points. Original repositories are not modified. See [SOURCES.md](SOURCES.md) for pinned source revisions and import details.

Neither Shinoda source repository contained a license file at the recorded revision; this project does not assign a new license to their content. Confirm permission before publishing or redistributing it. `text-to-cad` is an MIT-licensed process reference; its code is not bundled here.
