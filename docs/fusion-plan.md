# C 阶段：可见光几何与红外配准融合

## 目标

C 阶段在 B 阶段之后执行。它不替代可见光和红外的独立基线，而是新增一条融合实验线：使用可见光 COLMAP 的稳定几何和相机位姿作为参考，再尝试把红外图像按序号或标定关系绑定到同一轨迹上。

## 输入

- `manifests/dataset_manifest.csv`：可见光/红外配对清单。
- `work/colmap_visible/`：可见光 COLMAP 参考结果。
- `work/colmap_thermal/`：红外独立 COLMAP 结果，可选。
- 原始 `*_V.JPG` 和 `*_T.JPG` 图片。

## Pair Map

先从 manifest 生成 `work/fusion/pair_map.csv`。字段建议为：

```text
sequence_id,visible_filename,thermal_filename,visible_camera_id,thermal_camera_id,registration_status,notes
```

`registration_status` 可使用：

- `paired`：文件名序号已配对，但尚未验证几何对齐。
- `direct_bind_ok`：红外可直接绑定到可见光位姿。
- `needs_calibration`：需要额外标定或单应配准。
- `rejected`：该对图像无法用于融合。

## 融合路线

1. 读取 manifest，确认 339 对图像完整。
2. 复制或引用可见光 COLMAP 结果作为 `visible_colmap_reference`。
3. 按序号把红外图像与可见光相机位姿建立对应关系。
4. 抽样检查红外和可见光视场差异。
5. 如果视场差异小，尝试 direct bind。
6. 如果视场差异明显，增加标定、仿射或单应配准。
7. 输出诊断图和 `reports/fusion_report.md`。

## 诊断重点

- 红外图像是否与可见光图像同序号同步。
- 两种传感器分辨率、视场和畸变是否明显不同。
- 热红外纹理是否能支持局部配准。
- 融合结果是否出现明显错位、漂移或重影。

## 暂不自动化的部分

真实的跨模态配准参数需要 B 阶段结果和样例图共同决定。因此当前仓库只记录融合方案和目录结构，不把 C 阶段写成固定一键脚本。
