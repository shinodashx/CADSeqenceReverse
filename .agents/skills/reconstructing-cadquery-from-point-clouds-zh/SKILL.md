---
name: reconstructing-cadquery-from-point-clouds-zh
description: "分析 NPY、PLY、XYZ 文件或粘贴的 XYZ 点列，用可编辑、逐步执行的 CadQuery CAD 特征序列重建并量化精度。用于点云到 CAD 逆向工程、尺寸还原及圆角接合修正；不使用网格转实体、点云包面或整体自由曲面拟合。中文工作流；与英文版二选一。"
---

# 点云到 CadQuery 序列重建

把点云当测量证据，而不是待转换的几何实体。**NPY、PLY、粘贴 XYZ 必须执行同一流程：读取 → 分析 → 特征与尺寸证据 → CAD 操作计划 → 序列建模 → 误差闭环。**

## 硬性规则

- PLY 只读取顶点 XYZ，即使有 faces 也不使用其面造型。禁止 Poisson／alpha shape／三角片缝合／网格转实体／整体 NURBS 拟合代替重建。
- 允许局部平面、圆、圆柱、圆弧等参数估计用于**测量**，以及在固定特征结构内优化少量有意义的尺寸；禁止逐点高阶样条或点云包面成为最终模型。
- 最终 `sequence_cq.py` 只依赖 CadQuery、标准库和明确参数，不读取点云、旧 STL／STEP／BRep 或分析脚本。用 S01、S02…显式线性步骤构建；不把主体藏进整模型函数／循环。重复几何优先阵列、镜像。
- 重建与功能改型分开保存；不根据物体类别补造隐藏轴承、刹车等。稀疏点云不能保证唯一恢复原 CAD 历史或任意绝对精度。

## 执行流程

1. **验收输入。** 文件直接读取；粘贴坐标原样保存。遇到截断、缺行、省略号先找完整附件，找不到就要求补全。记录原文件哈希、点数、索引、单位及公差；不静默缩放、转置、删点或去重。运行下方读取命令，查看统计和投影。
2. **重新理解。** 查看 XY/XZ/YZ、多角度与薄层截面；旋转件查看轴向—径向截面。建立主平面、轴、厚度、台阶、孔壁、长圆槽、凹槽、折弯和圆角。PCA 仅给轴候选；记录局部→世界变换。用原点索引分区，不能丢掉稀疏小特征。
3. **建立证据。** 写 `feature_evidence.csv`：特征／部件、原点索引文件、支持点数、实测值、采用值、残差、置信度、假设。区分观测、推断和未知；名义尺寸取整必须与实测比较。
4. **安排 CAD 操作。** 写 `feature_plan.md`：S 编号、body、依赖、construction plane、草图尺寸／约束、操作及方向、预期实体数、证据。按下表选择，不为凑清单强行用所有操作。
5. **执行并修正。** 编写独立序列，先主形体后局部特征；复杂 Boolean／圆角后检查每个实体有效、非空、正体积及数量。圆角接合与验收细则见 [references/checklist.md](references/checklist.md)，建模前阅读。不能跳过失败特征继续报成功。
6. **闭环验证。** 全量点到导出 CAD 表面的距离，加分区／关键尺寸／孔槽检查；部件表面与融合表面分别报告。复查最差点、细化网格、必要时 STEP 面距离复核。实际渲染并查看整体、背面、截面和接合放大图，修正后重验。
7. **交付。** 原输入来源与读取报告、证据表、计划、`sequence_cq.py`、STEP、需要的 STL、可复现验证与逐点误差、已查看的渲染。说明单位、公差、近似与未观测区域；未达标必须明示。只有要求运动时才增加运动脚本及状态检查。

| 几何证据 | CAD 操作 |
|---|---|
| 恒定截面、板、孔槽、凸台 | Sketch + Extrude／Cut／Hole／cskHole |
| 同轴台阶、锥面、回转槽 | 截面 Sketch + Revolve |
| 沿路径的恒定截面／连续变截面 | 约束路径 + Sweep／少量有证据截面 + Loft |
| 等厚开口薄壁 | Shell，检查开口面及偏置方向 |
| 连接过渡、去锐边 | 局部 Fillet／Chamfer |
| 重复、对称、组合、定位 | Circular pattern／Mirror／Boolean／Construction plane／Transform |
| 删除／替换 | 从活动 body／装配清单排除；工具体不导出 |

## 配套工具

`$SKILL_DIR` 为本技能目录。缺依赖时使用隔离环境；读取需 `numpy scipy plyfile matplotlib`，验证需 `numpy vtk`，STEP 复核和建模需 `cadquery`。测试过 Python 3.11／CadQuery 2.8。输出目录须新建或为空，原输入不可覆盖。

```bash
# 三种格式使用相同读取／分析入口；XYZ 粘贴保存为 input_points.txt
python "$SKILL_DIR/scripts/inspect_cloud.py" input.npy --out analysis
python "$SKILL_DIR/scripts/inspect_cloud.py" input.ply --out analysis
python "$SKILL_DIR/scripts/inspect_cloud.py" input_points.txt --out analysis
# N×6 等数据必须显式选择列；单位只有证据确认后才标 confirmed
# 可附加：--xyz-columns 0 1 2 --unit mm --unit-status confirmed

python "$SKILL_DIR/scripts/verify_surface.py" \
  --points analysis/points.npy --source-indices analysis/source_indices.npy \
  --mesh result/component_surfaces.stl --out validation \
  --threshold 0.1 --step result/components.step --exact-worst 20
# 0.1 只是命令示例，换成任务阈值。显式验收可加 --require-within-fraction 0.99
python "$SKILL_DIR/scripts/test_workflow.py"
```

读取工具保留重复点，拒绝非有限坐标；额外列须显式选择。验证工具计算点到三角**面**距离和可选 STEP 最差点复核，不自动完成反向覆盖、装配或强度验收。按检查表补全，不把脚本退出码当精度保证。
