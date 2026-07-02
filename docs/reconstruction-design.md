# B 阶段：可见光与红外独立重建

## 目标

B 阶段先分别建立两个基线：可见光 3DGS 和红外 3DGS。这个阶段不做跨模态融合，重点是确认两套数据各自能否完成 COLMAP 位姿估计和 3DGS 训练。

## 输入

```text
data/raw/visible/   # 可见光图片，文件名通常为 *_V.JPG
data/raw/thermal/   # 红外图片，文件名通常为 *_T.JPG
```

实际服务器路径可通过 `DATASET_ROOT` 环境变量指定。

## 可见光流程

1. 使用 `scripts/run_colmap_visible.sh` 运行 COLMAP。
2. 检查 `colmap_visible/sparse/` 是否生成有效模型。
3. 使用 `scripts/train_3dgs_visible.sh` 训练可见光 3DGS。
4. 记录输出路径、训练轮数、截图和质量观察。

可见光通常纹理更丰富，应作为本项目的主要几何基线。

## 红外流程

1. 使用 `scripts/run_colmap_thermal.sh` 运行 COLMAP。
2. 检查红外图像是否能形成稳定稀疏重建。
3. 如果 COLMAP 输出可用，再运行 `scripts/train_3dgs_thermal.sh`。
4. 如果 COLMAP 失败，记录失败原因，不强行继续训练。

红外可能因为纹理弱、视场差异、噪声或重复区域导致匹配不足。失败记录应包含 COLMAP 日志、失败图片序号和可能原因。

## 输出

```text
work/
  colmap_visible/
  colmap_thermal/

outputs/
  3dgs_visible/
  3dgs_thermal/
  reports/
```

## 成功标准

- 可见光流程产生可检查的 COLMAP 模型和 3DGS 输出。
- 红外流程产生独立模型，或产生清晰失败分析。
- 两条流程的命令、参数、日志和结果路径都有记录。
