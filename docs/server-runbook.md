# RTX 5090 Ubuntu 22.04 服务器操作手册

## 目标

在 RTX 5090、Ubuntu 22.04 服务器上复现可见光和红外 3DGS 重建实验。当前仓库只提供文档、配置和脚本模板；真实执行前必须先检查服务器的 driver、CUDA、PyTorch 和 COLMAP 环境。

## 环境检查

登录服务器后先运行：

```bash
nvidia-smi
nvcc --version
git --version
conda --version
df -h
```

记录以下信息：

- GPU 型号和显存。
- NVIDIA driver 版本。
- CUDA 版本。
- conda 是否可用。
- 数据盘和实验盘可用空间。

如果 `nvidia-smi` 或 `nvcc --version` 不可用，先不要运行训练脚本，应先修复驱动或 CUDA 环境。

## 推荐目录

```text
~/projects/uav-thermal-visible-3dgs/
~/datasets/uav_3dgs/raw/visible/
~/datasets/uav_3dgs/raw/thermal/
~/experiments/uav_3dgs/
```

含义：

- `~/projects/uav-thermal-visible-3dgs/`：Git 仓库。
- `~/datasets/uav_3dgs/raw/visible/`：可见光原始图片。
- `~/datasets/uav_3dgs/raw/thermal/`：红外原始图片。
- `~/experiments/uav_3dgs/`：COLMAP、3DGS 和报告输出。

## 数据准备

原始图片不进入 Git。建议把 `*_V.JPG` 放入 `raw/visible/`，把 `*_T.JPG` 放入 `raw/thermal/`。如果暂时保留在同一目录，也可以先用 `scripts/prepare_dataset.py` 生成 manifest 检查配对关系。

生成 manifest：

```bash
python scripts/prepare_dataset.py \
  --input /path/to/raw/images \
  --output manifests/dataset_manifest.csv
```

预期当前数据为：

```text
manifest rows: 339
complete pairs: 339
```

## 执行顺序

1. 克隆或同步本仓库。
2. 把原始图片放到服务器数据目录，图片不进入 Git。
3. 运行 manifest 检查。
4. 运行可见光 COLMAP。
5. 运行可见光 3DGS。
6. 运行红外 COLMAP。
7. 如果红外 COLMAP 输出可用，运行红外 3DGS。
8. 根据 B 阶段结果决定 C 阶段融合方式。

## B 阶段命令模板

```bash
export DATASET_ROOT="$HOME/datasets/uav_3dgs"
export EXPERIMENT_ROOT="$HOME/experiments/uav_3dgs"

bash scripts/run_colmap_visible.sh
bash scripts/train_3dgs_visible.sh

bash scripts/run_colmap_thermal.sh
bash scripts/train_3dgs_thermal.sh
```

如果红外 COLMAP 失败，应先保存日志和失败原因，不要强行训练红外 3DGS。

## 结果归档

每次实验结束后运行：

```bash
bash scripts/archive_results.sh
```

归档报告应记录命令、参数、耗时、输出目录和质量观察。后续写论文、报告或复现实验时，以这些记录为准。
