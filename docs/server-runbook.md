# RTX 5090 Ubuntu 22.04 服务器操作手册

## 目标

在 RTX 5090、Ubuntu 22.04 服务器上复现可见光和红外 3DGS 重建实验。当前仓库只提供文档、配置和脚本模板；真实执行前必须先检查服务器的 driver、CUDA、PyTorch 和 COLMAP 环境。

## 已确认服务器信息

当前服务器连接入口：

```text
pch@10.76.7.127
```

用户选择当前阶段采用 A 方案：只根据服务器信息继续完善命令手册，暂不由 Codex 通过 SSH 远程执行。

已从截图确认的环境：

```text
NVIDIA-SMI: 570.144
Driver Version: 570.144
CUDA Version: 12.8
GPU 0: NVIDIA GeForce RTX 5090, 32607 MiB
GPU 1: NVIDIA GeForce RTX 5090, 32607 MiB
nvcc: release 12.8, V12.8.61
git: 2.34.1
conda: 24.1.2
/dev/nvme0n1p2: 3.6T total, 797G available, 78% used
```

结论：GPU、driver、CUDA compiler、git、conda 都可用；磁盘剩余约 797G，足够先进行本批 678 张图像的 COLMAP 与 3DGS 基线实验，但训练输出和中间结果仍应定期归档。

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

本项目在该服务器上统一放到 `/home/pch/myGS` 下：

```text
/home/pch/myGS/infraredGS/
/home/pch/myGS/datasets/uav_3dgs/raw/visible/
/home/pch/myGS/datasets/uav_3dgs/raw/thermal/
/home/pch/myGS/experiments/uav_3dgs/
/home/pch/myGS/src/
```

含义：

- `/home/pch/myGS/infraredGS/`：本 Git 仓库。
- `/home/pch/myGS/datasets/uav_3dgs/raw/visible/`：可见光原始图片。
- `/home/pch/myGS/datasets/uav_3dgs/raw/thermal/`：红外原始图片。
- `/home/pch/myGS/experiments/uav_3dgs/`：COLMAP、3DGS 和报告输出。
- `/home/pch/myGS/src/`：第三方源码，例如官方 Gaussian Splatting 仓库或 COLMAP 源码。

创建目录：

```bash
mkdir -p /home/pch/myGS/datasets/uav_3dgs/raw/visible
mkdir -p /home/pch/myGS/datasets/uav_3dgs/raw/thermal
mkdir -p /home/pch/myGS/experiments/uav_3dgs
mkdir -p /home/pch/myGS/src
```

克隆本仓库：

```bash
cd /home/pch/myGS
git clone git@github.com:YNUpanpan/infraredGS.git
cd /home/pch/myGS/infraredGS
```

## 数据准备

原始图片不进入 Git。建议把 `*_V.JPG` 放入 `raw/visible/`，把 `*_T.JPG` 放入 `raw/thermal/`。如果暂时保留在同一目录，也可以先用 `scripts/prepare_dataset.py` 生成 manifest 检查配对关系。

推荐数据目录：

```text
/home/pch/myGS/datasets/uav_3dgs/raw/visible/
/home/pch/myGS/datasets/uav_3dgs/raw/thermal/
```

如果先把 678 张图片传到同一个临时目录，例如 `/home/pch/myGS/datasets/uav_3dgs/raw/all/`，先运行 manifest 检查，不要批量删除或覆盖文件。

如果可见光和红外已经分开放在 `visible/` 与 `thermal/` 目录，生成 manifest：

```bash
cd /home/pch/myGS/infraredGS

python scripts/prepare_dataset.py \
  --visible-dir /home/pch/myGS/datasets/uav_3dgs/raw/visible \
  --thermal-dir /home/pch/myGS/datasets/uav_3dgs/raw/thermal \
  --output manifests/dataset_manifest.csv
```

预期当前数据为：

```text
manifest rows: 339
complete pairs: 339
```

如果 678 张图片暂时放在同一个目录，也可以使用旧写法：

```bash
python scripts/prepare_dataset.py \
  --input /path/to/raw/images \
  --output manifests/dataset_manifest.csv
```

## 第三方源码准备

本仓库的 3DGS 训练脚本默认依赖官方 `gaussian-splatting` 仓库，并通过 `GAUSSIAN_REPO` 指向源码目录。服务器当前推荐放在：

```text
/home/pch/myGS/src/gaussian-splatting
```

如果该目录不存在，先克隆官方源码。官方仓库包含子模块，因此使用 `--recursive`：

```bash
cd /home/pch/myGS/src
git clone --recursive https://github.com/graphdeco-inria/gaussian-splatting.git

ls -lah /home/pch/myGS/src/gaussian-splatting
ls -lah /home/pch/myGS/src/gaussian-splatting/train.py
```

如果网络中断或子模块没有拉完整，进入仓库后补拉子模块：

```bash
cd /home/pch/myGS/src/gaussian-splatting
git submodule update --init --recursive
```

暂时不要删除 `/home/pch/myGS/src` 下已有目录；如果已有同名目录但内容不完整，先截图或输出 `git status` 后再决定如何处理。

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
cd /home/pch/myGS/infraredGS

export DATASET_ROOT="/home/pch/myGS/datasets/uav_3dgs"
export EXPERIMENT_ROOT="/home/pch/myGS/experiments/uav_3dgs"
export GAUSSIAN_REPO="/home/pch/myGS/src/gaussian-splatting"

bash scripts/run_colmap_visible.sh
bash scripts/train_3dgs_visible.sh

bash scripts/run_colmap_thermal.sh
bash scripts/train_3dgs_thermal.sh
```

如果红外 COLMAP 失败，应先保存日志和失败原因，不要强行训练红外 3DGS。

双 GPU 使用建议：

```bash
CUDA_VISIBLE_DEVICES=0 bash scripts/train_3dgs_visible.sh
CUDA_VISIBLE_DEVICES=1 bash scripts/train_3dgs_thermal.sh
```

先不要同时启动两个长训练任务。建议先跑可见光基线，确认 COLMAP 和 3DGS 输出正常后，再跑红外基线。

## 结果归档

每次实验结束后运行：

```bash
bash scripts/archive_results.sh
```

归档报告应记录命令、参数、耗时、输出目录和质量观察。后续写论文、报告或复现实验时，以这些记录为准。
