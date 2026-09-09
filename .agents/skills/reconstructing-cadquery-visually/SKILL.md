---
name: reconstructing-cadquery-visually
description: "仅观察 NPY、PLY 或粘贴 XYZ 的渲染视图，重建可编辑 CadQuery 特征序列。用于纯可视化点云到 CAD 重建与多视图迭代。中文版。"
---

# 点云 → CadQuery 序列 · 纯可视化

**点云分析仅依据渲染视图。** 程序负责解码、完整性校验和显示；XYZ 数值特征分析、拟合及距离优化不参与建模。全部 CAD 几何通过参数化操作重新构建，CAD 自身的约束、拓扑和装配用内核检查。

## 流程

1. **读取。** NPY、PLY、粘贴 XYZ 使用本技能的渲染读取器；PLY 取顶点 XYZ，粘贴内容原样保存。保留坐标与行序，记录哈希、索引规则和单位；输入不完整时补全后绘制。
2. **观察。** 查看正交、相反斜视、背面及必要显示切片／局部放大图。分别观察内外壁、端面、孔槽、对称和过渡；用至少两个非共线视角复核特征，记录相机、比例及裁切设置。
3. **记录证据。** `feature_evidence.csv` 记录特征、截图与哈希、图中区域、尺度来源、估计范围、采用参数及置信度。区分观测、推断、未知；由图上标尺或已知尺寸估计尺度。约束冲突先查视角与尺度，关键尺寸不可辨识时请求补充。
4. **规划。** `feature_plan.md` 写明范围、尺度依据、坐标系、未知区域、视觉目标及 CAD 检查方法；每个 S 步骤列出输入→输出 body、依赖、基准／草图约束、具名参数、操作、预期实体数和截图证据。
5. **建模。** 编写独立 `sequence_cq.py`，仅依赖 CadQuery、标准库和参数。显式 S01、S02…每步一个有意义的操作，保留命名中间结果。按依赖先基准与主形体再细节；关键操作后检查实体与特征意图。建模前读 [检查表](references/checklist.md)。
6. **验收与迭代。** 分别验证 BRep、多视图一致性、关键 CAD 特征及装配、实际导出物。点云与模型按相同相机、比例及裁切条件并排观察。按 [迭代流程](references/refinement.md) 定位责任步骤、修改序列、重新导出并复查全部视图和原合格区域。
7. **交付。** 提供读取报告、证据、计划、序列、STEP／所需 STL、CAD 检查命令、逐轮比较和已查看渲染；报告绑定最终哈希。标明通过／未达标／受限，点云数值精度标“未评估”。达到视觉目标或有证据的停滞后结束；说明剩余近似，功能改型另存，运动按需增加。

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

`$SKILL_DIR` 为技能目录，`$INPUT` 为 NPY／PLY／XYZ 文件。读取／渲染依赖 `numpy plyfile vtk`，建模与 CAD 检查依赖 `cadquery`。使用新建或空输出目录。

```bash
python "$SKILL_DIR/scripts/inspect_cloud.py" "$INPUT" --out views
# 额外列显式选择：--xyz-columns 0 1 2；已确认单位：--unit mm --unit-status confirmed
python "$SKILL_DIR/scripts/inspect_cloud.py" "$INPUT" \
  --cad-stl result/component_surfaces.stl --out comparison
# 显示放大：--focus X Y Z --view-span H；同次比较采用相同设置
python "$SKILL_DIR/scripts/test_workflow.py"
```

工具提供七个标准视图，需实际查看；按观察需要补充相反斜视或显示切片。渲染不可用时先修复环境，仍受限则报告阻塞。视觉一致性与 CAD 质量分别验收。
