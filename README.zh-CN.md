# CADsequenceReverse

**两个独立的重建任务，提供中英文 Agent Skill，用于生成可编辑的 CadQuery 特征序列。**

[![English](https://img.shields.io/badge/Language-English-blue)](README.md)

默认 README 为英文，本文件为独立的简体中文版。点云重建提供三种模式，每种均有中英文版；STEP 重建提供两个语言版本。每次任务选择一种模式和语言。

## 目录

- [任务目录](#任务目录)
- [项目结构](#项目结构)
- [安装与验证](#安装与验证)
- [任务一：点云 → CadQuery](#task-1)
- [任务二：STEP → CadQuery](#task-2)
- [验收与限制](#验收与限制)
- [来源与许可](#来源与许可)
- [English](README.md)

## 任务目录

| 任务 | 输入 | 简体中文技能 | English skill | 配套内容 |
|---|---|---|---|---|
| 点云重建：综合模式 | NPY、PLY、XYZ 文本、CSV、坐标数组 | [SKILL.md](.agents/skills/reconstructing-cadquery-from-point-clouds-zh/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-from-point-clouds-en/SKILL.md) | XYZ/Python 测量主导，视图辅助；表面验证与迭代清单 |
| 点云重建：纯数值模式 | 同上 | [SKILL.md](.agents/skills/reconstructing-cadquery-numerically/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-numerically-en/SKILL.md) | 数值读取器、表面验证；点云图像不参与分析 |
| 点云重建：纯可视化模式 | 同上 | [SKILL.md](.agents/skills/reconstructing-cadquery-visually/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-visually-en/SKILL.md) | 七视图及源相机锁定的 CAD 对比；点云数值精度未评估 |
| STEP 重建 | 完整 STEP/STP 文件或完整 STEP 文本 | [SKILL.md](.agents/skills/reconstructing-cadquery-sequences-zh/SKILL.md) | [SKILL.md](.agents/skills/reconstructing-cadquery-sequences-en/SKILL.md) | 测量、逐体建模、独立重放与验证流程 |

两个任务可以独立使用，不要求先后执行。它们生成新的特征模型，**不能通过导入原几何冒充重建**，也不是一键自动转换器。

## 项目结构

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

每个点云版本包含 `SKILL.md`、`requirements.txt`、`agents/openai.yaml`、`references/checklist.md`、`references/refinement.md`，以及 `scripts/inspect_cloud.py`、`scripts/test_workflow.py`。综合和纯数值模式另含 `scripts/verify_surface.py`，纯可视化模式不包含表面误差验证器。每个 STEP 版本包含独立自包含的 `SKILL.md`。

## 安装与验证

八个技能目录已放在当前项目的 `.agents/skills/`，不需要全局安装，也不修改原仓库。Amp 中重新加载技能即可使用；其他兼容代理可开启新会话。提示词中明确指定一种模式和语言。沿用上游命名：纯数值和纯可视化的中文目录没有语言后缀，英文目录以 `-en` 结尾。安装到其他项目时复制所选版本的**完整目录**，不要覆盖已有修改。同一模式的中英文脚本一致，不同模式的脚本并不相同。

在当前项目根目录使用 Python 3.11 创建隔离环境：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
for test in .agents/skills/*/scripts/test_workflow.py; do
  python "$test" || exit 1
done
```

依赖固定 CadQuery 2.8.0，其他依赖沿用上游要求，并非完整锁定环境。根目录依赖入口安装点云工具及两个任务共用的 CadQuery/OCP。STEP 技能不附带转换命令、渲染器或自动重建测试；代理仍需为具体任务准备并验证分析和渲染工具。这些技能不要求 cadgen、build123d、MCP 或外部模型服务。

<a id="task-1"></a>

## 任务一：点云 → CadQuery

**综合模式：读取 XYZ → Python 数值分析（视图辅助）→ 尺寸证据 → CAD 操作计划 → 显式顺序建模 → 误差验证与修正。**

示例提示：

> 使用 reconstructing-cadquery-from-point-clouds-zh 分析 input.ply，以 XYZ 数值和 Python 测量为主，视图为辅。先确认单位，建立特征与尺寸证据和 CAD 操作计划，再生成独立的 CadQuery 序列、STEP 和迭代验收报告。禁止点云包面或网格转实体。

激活环境后运行输入检查：

```bash
SKILL_DIR=.agents/skills/reconstructing-cadquery-from-point-clouds-zh
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply --out analysis
# NPY 和保存后的 XYZ 文本使用同一命令，只替换输入文件名。
# 多余列需要显式指定：--xyz-columns 0 1 2
# 仅在有证据时添加：--unit mm --unit-status confirmed
```

读取器生成 `input_report.json`、`points.npy`、`source_indices.npy`、`projections.png`，**不生成 CAD**。保留原单位、点序与重复点，忽略 PLY 面。

代理完成建模并导出后，执行表面验证：

```bash
python "$SKILL_DIR/scripts/verify_surface.py" \
  --points analysis/points.npy \
  --source-indices analysis/source_indices.npy \
  --mesh result/component_surfaces.stl \
  --out validation --threshold 0.1 \
  --step result/components.step --exact-worst 20 \
  --require-within-fraction 0.99
```

`result/` 文件必须已生成。`0.1` 阈值和 `0.99` 覆盖率只是示例，不是通用验收标准，应按任务单位、公差设置。输出目录必须新建或为空。验证器生成 `point_errors.csv` 和 `verification.json`；未达到指定覆盖率时返回非零状态。

交付：输入来源记录、`feature_evidence.csv`、`feature_plan.md`、独立的 `sequence_cq.py`、STEP、按需 STL、验证报告、逐轮比较和已检查渲染图，报告绑定最终文件哈希。详细标准见 [验收清单](.agents/skills/reconstructing-cadquery-from-point-clouds-zh/references/checklist.md) 和 [迭代流程](.agents/skills/reconstructing-cadquery-from-point-clouds-zh/references/refinement.md)。

### 纯数值模式

> 使用 reconstructing-cadquery-numerically 分析 input.ply，仅用 XYZ 数值和 Python，点云图像不参与分析和迭代。交付数值证据与误差，以及纯 CAD 质量检查。

将上述读取与验证命令的 `SKILL_DIR` 改为 `.agents/skills/reconstructing-cadquery-numerically`。读取器生成 JSON 报告和两个 NPY 数组，不生成投影图；最终仍需查看纯 CAD 渲染以检查产物质量。

### 纯可视化模式

> 使用 reconstructing-cadquery-visually，仅观察 input.ply 的实际渲染视图重建。对照同条件视图，另行验证新建 CAD，点云数值精度标为未评估。

```bash
SKILL_DIR=.agents/skills/reconstructing-cadquery-visually
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply --out views
# 新建 CAD 已导出 STL 后：
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply \
  --cad-stl result/component_surfaces.stl --out comparison
# 可选显示放大：--focus X Y Z --view-span H
```

读取器输出 `input_report.json` 和七张 PNG（`plus_x`、`minus_x`、`plus_y`、`minus_y`、`plus_z`、`minus_z`、`iso`），不输出测量数组或表面误差报告。点云与 CAD 面板共用按源点云取景的相机；同次比较保持焦点、比例及裁切一致。实际查看图片，并按需要补充相反斜视或显示切片。数值特征拟合与点云距离优化不参与建模；CAD 有效性、拓扑与装配仍需检查。

<a id="task-2"></a>

## 任务二：STEP → CadQuery

**检查源拓扑/单位 → 逐体测量 → 特征计划 → 逐体重建 → 脱离源文件重放 → 比较并检查导出物。**

示例提示：

> 使用 reconstructing-cadquery-sequences-zh 将 input.step 重建为显式、可编辑的 CadQuery 特征序列。保留源单位与装配位置，仅分析阶段可导入源 STEP。脱离原文件重放，比较缺失/多余材料与双向采样表面偏差，检查源模型和重建模型的同视角渲染，明确报告未满足的公差。

交付：`model_sequence.py`、参数/特征表、`model_rebuilt.step`、`model.stl`、`validation.json`、运行说明与已检查图像。建模代码公开 `result`、`bodies` 和有序 `history`，不得导入源几何，也不得把建模过程隐藏在工厂函数中。

## 验收与限制

- 审查代码、独立重放、重新导入导出的 STEP 后再验收；原始输入与派生产物分开存放。
- 确定性几何检查结合实际多视角检查，并遵守模式边界：综合模式图像疑点以数值复核，纯数值模式仅查看 CAD 图，纯可视化模式比较源/模型视图并另验 CAD 质量。修正责任特征后重建，复查修正区与原合格区。这一流程参考 [text-to-cad](https://github.com/earthtojake/text-to-cad)，不引入其工具链或建模工厂。
- 综合和纯数值模式的点到 STL 表面距离是单向误差，不是双向 Hausdorff 距离或完整 CAD 验收。可选 STEP 检查只覆盖所选点，除非明确检查全部点。纯可视化模式不评估点云数值精度。
- 稀疏点云无法证明隐藏结构，STEP 通常不含原始特征历史；不能保证唯一恢复、任意自由曲面完全一致、制造可用性或机构动力学。
- 六个点云版本各附带 7 组回归测试（共 42 项），验证读取和各模式的测量/渲染行为，**不代表任意模型都能自动重建**。每个实际模型仍需单独验收，并披露未执行的检查。

## 来源与许可

八个技能目录保留 [Point2CAD](https://github.com/shinodashx/Point2CAD) 和 [step-to-cadquery-skills](https://github.com/shinodashx/step-to-cadquery-skills) 上游的全部模式、中英文版本与配套文件。本项目补充目录组织、两份独立 README、来源记录与依赖入口。原仓库未修改，具体版本见 [SOURCES.md](SOURCES.md)。

两个 Shinoda 仓库在记录版本中未提供许可文件，本项目不擅自为其内容指定许可证；公开发布或再分发前请确认授权。text-to-cad 是 MIT 许可的流程参考，本项目未打包其代码。
