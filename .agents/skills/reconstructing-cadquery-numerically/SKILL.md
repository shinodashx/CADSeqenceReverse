---
name: reconstructing-cadquery-numerically
description: "仅用 XYZ 数值和 Python 分析 NPY、PLY 或粘贴点云，重建可编辑 CadQuery 特征序列并量化精度。用于纯数值点云到 CAD 重建。中文版。"
---

# 点云 → CadQuery 序列 · 纯数值

**点云分析仅用 XYZ 与 Python，点云图像不参与分析和迭代。** 点云提供测量证据，全部 CAD 几何通过参数化操作重新构建；CAD 成品可视化用于检查建模质量。

## 流程

1. **读取。** NPY、PLY、粘贴 XYZ 使用本技能的数值读取器；PLY 取顶点 XYZ，粘贴内容原样保存。保留坐标、行序及重复点，记录哈希、索引、单位和变换；输入不完整时补全后分析。
2. **分析。** 用坐标分布、分层、数值薄截面及轴向—径向测量识别基准、轮廓、厚度、孔槽和过渡。分别检验内外壁、端面、对称和相切，PCA 只提供轴候选。局部拟合用于测量，保存脚本与原索引分区。
3. **记录证据。** `feature_evidence.csv` 记录特征、区域、支持点数／覆盖、实测／采用参数、各自残差、置信度。区分观测、推断、未知；尺寸取整与简化需复核。约束冲突先查单位、坐标和证据，再确认影响结果的未知量。
4. **规划。** `feature_plan.md` 写明范围、尺度依据、坐标系、未知区域、精度目标及检查方法；每个 S 步骤列出输入→输出 body、依赖、基准／草图约束、具名参数、操作、预期实体数和证据。
5. **建模。** 编写独立 `sequence_cq.py`，仅依赖 CadQuery、标准库和参数。显式 S01、S02…每步一个有意义的操作，保留命名中间结果。按依赖先基准与主形体再细节；关键操作后检查实体与特征意图。建模前读 [检查表](references/checklist.md)。
6. **验收与迭代。** 分别验证 BRep、全量／分区点云误差、关键尺寸及装配、实际导出物。以数值表定位点云偏差，另查看纯 CAD 正交、相反斜视及必要截面／接合图。按 [迭代流程](references/refinement.md) 定位责任步骤、修改序列、重新导出并回归检查。
7. **交付。** 提供读取报告、证据、计划、序列、STEP／所需 STL、验证命令与误差、逐轮比较和已查看的纯 CAD 渲染；报告绑定最终文件哈希。标明通过／未达标／未评估／受限及剩余近似。达到目标或有证据的停滞后结束；功能改型另存，运动按需增加。

## 操作选择

| 特征 | 操作 |
|---|---|
| 恒定截面、板、凸台、孔槽 | Sketch + Extrude／Cut／Hole |
| 同轴台阶、锥面、回转槽 | 截面 Sketch + Revolve |
| 沿路径恒定／变化截面 | Sweep／少量有证据截面的 Loft |
| 等厚开口薄壁 | Shell |
| 接合过渡、去锐边 | 局部 Fillet／Chamfer，按邻接拓扑安排次序 |
| 重复、对称、组合、定位 | Circular pattern／Mirror／Boolean／Construction plane／Transform |
| 删除／替换 body | 更新活动 body 与装配清单，导出最终保留件 |

## 工具

`$SKILL_DIR` 为技能目录，`$INPUT` 为 NPY／PLY／XYZ 文件。读取依赖 `numpy scipy plyfile`，表面验证依赖 `numpy vtk`，建模与 STEP 检查依赖 `cadquery`。使用新建或空输出目录。

```bash
python "$SKILL_DIR/scripts/inspect_cloud.py" "$INPUT" --out analysis
# 额外列显式选择：--xyz-columns 0 1 2；已确认单位：--unit mm --unit-status confirmed
python "$SKILL_DIR/scripts/verify_surface.py" \
  --points analysis/points.npy --source-indices analysis/source_indices.npy \
  --mesh result/component_surfaces.stl --out validation \
  --threshold "$TOLERANCE" --step result/components.step --exact-worst 20
python "$SKILL_DIR/scripts/test_workflow.py"
```

`$TOLERANCE` 使用任务单位下约定的阈值。工具提供点到三角面距离及可选 STEP 子集复核；覆盖、拓扑、关键特征和装配按检查表分别验收。
