# CADsequenceReverse

**Two independent Agent Skills for reverse-engineering editable CadQuery feature sequences.**

[![简体中文](https://img.shields.io/badge/语言-简体中文-blue)](README.zh-CN.md)

English is the default documentation language. The button opens the separate Simplified Chinese README. Both tasks include complete English and Simplified Chinese skill editions; select one edition per task, not both in the same run.

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
| 1. Point-cloud reconstruction | NPY, PLY, XYZ/text, CSV, coordinate arrays | [SKILL.md](.agents/skills/reconstructing-cadquery-from-point-clouds-en/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-from-point-clouds-zh/SKILL.md) | Reader, surface-distance verifier, regression tests, acceptance checklist |
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
    │   ├── SKILL.md
    │   ├── requirements.txt
    │   ├── agents/openai.yaml
    │   ├── references/checklist.md
    │   └── scripts/
    │       ├── inspect_cloud.py
    │       ├── verify_surface.py
    │       └── test_workflow.py
    ├── reconstructing-cadquery-from-point-clouds-zh/
    │   ├── SKILL.md
    │   ├── requirements.txt
    │   ├── agents/openai.yaml
    │   ├── references/checklist.md
    │   └── scripts/
    │       ├── inspect_cloud.py
    │       ├── verify_surface.py
    │       └── test_workflow.py
    ├── reconstructing-cadquery-sequences-en/
    │   └── SKILL.md
    └── reconstructing-cadquery-sequences-zh/
        └── SKILL.md
```

## Setup

All four editions already live in this project's `.agents/skills/`; no global installation or change to either source repository is needed. Reload skills in Amp after adding them, or start a new session in a compatible agent. Explicitly name the `-en` or `-zh` edition in your prompt; do not load both language editions for the same task. When installing elsewhere, choose one language per task, copy its **whole directory**, and do not overwrite existing work. The point-cloud editions contain translated instructions/checklists/display metadata and identical executable scripts.

From this repository root, use Python 3.11 and an isolated environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python .agents/skills/reconstructing-cadquery-from-point-clouds-en/scripts/test_workflow.py
python .agents/skills/reconstructing-cadquery-from-point-clouds-zh/scripts/test_workflow.py
```

CadQuery is pinned to 2.8.0; other dependencies follow the upstream requirements and are not a full lockfile. The root requirements install the point-cloud toolkit and CadQuery/OCP for both tasks. The STEP skill has no bundled conversion CLI, renderer, or automated reconstruction test suite; the agent must prepare and verify task-specific analysis/rendering tools. No `cadgen`, build123d, MCP server, or external model service is required by these skills.

<a id="task-1"></a>

## Task 1 — Point cloud → CadQuery

**Read → analyze projections/sections → record dimensional evidence → plan features → build an explicit sequence → measure and refine.**

Example prompt:

> Use reconstructing-cadquery-from-point-clouds-en to analyze `input.ply`. Establish units, feature evidence, and a CAD operation plan before modeling. Deliver a standalone CadQuery sequence, STEP, and measured error reports. Do not wrap the cloud or convert a mesh to a solid.

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

Deliver input provenance, `feature_evidence.csv`, `feature_plan.md`, standalone `sequence_cq.py`, STEP, requested STL, validation reports, and inspected renders. See the [acceptance checklist](.agents/skills/reconstructing-cadquery-from-point-clouds-en/references/checklist.md).

<a id="task-2"></a>

## Task 2 — STEP → CadQuery

**Inspect source topology/units → measure each body → plan features → rebuild body by body → replay without the source → compare and inspect exports.**

Example prompt:

> Use reconstructing-cadquery-sequences-en to reconstruct `input.step` as an explicit, editable CadQuery sequence. Preserve the source units and assembly placement. Keep STEP imports in analysis only. Replay without the source file, compare missing/excess material and bidirectional sampled surface deviation, and inspect matched source/rebuilt views. Report unmet tolerances.

Deliver `model_sequence.py`, a parameter/feature table, `model_rebuilt.step`, `model.stl`, `validation.json`, run instructions, and inspected images. Modeling code must expose `result`, `bodies`, and ordered `history`; it must not import the source geometry or conceal modeling inside a factory function.

## Validation and limitations

- Review generated code, independently replay it, and reimport the exported STEP before accepting it. Keep original inputs separate from derived outputs.
- Pair deterministic geometry checks with actual multi-view inspection. Turn visual concerns into measurements; repair the responsible feature, rebuild, and rerun affected checks. This process is informed by [text-to-cad](https://github.com/earthtojake/text-to-cad), without importing its toolchain or model factories.
- Point-to-STL distances are one-way measurements, not bidirectional Hausdorff distances or complete CAD acceptance. Optional STEP checks cover only the selected points unless all points are requested.
- Sparse scans do not establish hidden geometry. STEP usually lacks original feature history. Neither task guarantees unique history recovery, arbitrary freeform equivalence, manufacturing fitness, or mechanism dynamics.
- The included seven regression tests check point-cloud reading and surface measurement, **not automatic reconstruction of arbitrary CAD**. Validate each generated model separately and disclose checks that could not run.

## Sources and licensing

The four skill directories preserve both upstream language editions and supporting files. This project adds organization, separate bilingual READMEs, provenance, and a dependency entry point. Original repositories are not modified. See [SOURCES.md](SOURCES.md) for pinned source revisions and import details.

Neither Shinoda source repository contained a license file at the recorded revision; this project does not assign a new license to their content. Confirm permission before publishing or redistributing it. `text-to-cad` is an MIT-licensed process reference; its code is not bundled here.
