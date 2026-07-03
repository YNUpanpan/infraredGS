# 服务器 COLMAP 与 3DGS 执行计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `/home/pch/myGS` 服务器项目目录下，先完成可见光 COLMAP 基线，再新建干净 3DGS conda 环境并训练可见光 3DGS，之后再推进红外和融合。

**Architecture:** 当前阶段按“数据确认 -> 可见光 COLMAP -> 新建 3DGS 环境 -> 可见光 3DGS -> 红外 COLMAP/3DGS -> C 阶段融合”的顺序执行。COLMAP 使用服务器已有 `/usr/bin/colmap` 先跑通基线；3DGS 使用独立 conda 环境，避免污染已有 `ntrgs`、`ntrgsE` 等环境。所有服务器生成结果放在 `/home/pch/myGS/experiments/uav_3dgs`，不进入 Git。

**Tech Stack:** Ubuntu 22.04、RTX 5090、CUDA 12.8、COLMAP 3.7、conda、PyTorch、官方 `graphdeco-inria/gaussian-splatting`、本仓库 Bash 脚本。

---

## 当前已完成

- [x] 本地仓库已建立并推送到 `git@github.com:YNUpanpan/infraredGS.git`。
- [x] 原始图片未进入 GitHub。
- [x] 可见光 339 张、红外 339 张已上传到服务器。
- [x] 服务器已生成 `manifests/dataset_manifest.csv`，样例行显示可见光/红外配对正常。
- [x] 服务器环境已确认：2 张 RTX 5090、driver 570.144、CUDA 12.8、conda 可用。
- [x] 服务器已有 `/usr/bin/colmap`，版本 `COLMAP 3.7`，但显示 `without CUDA`。
- [x] 官方 `gaussian-splatting` 源码和子模块已克隆到 `/home/pch/myGS/src/gaussian-splatting`，`train.py` 已存在。
- [x] 现有 `ntrgs` 环境中没有 `torch`，不适合作为 3DGS 训练环境。

## 当前未完成

- [ ] 还没有运行可见光 COLMAP。
- [ ] 还没有确认 COLMAP 输出是否满足 3DGS 输入格式。
- [ ] 还没有新建专用 3DGS conda 环境。
- [ ] 还没有编译/安装 `gaussian-splatting` 的 Python 依赖和 CUDA 扩展。
- [ ] 还没有训练可见光 3DGS。
- [ ] 还没有运行红外 COLMAP。
- [ ] 还没有训练红外 3DGS。
- [ ] 还没有进入 C 阶段可见光/红外融合。

## Task 1: 服务器同步与基线状态确认

**Files:**
- Read only: `/home/pch/myGS/infraredGS`
- Read only: `/home/pch/myGS/datasets/uav_3dgs/raw/visible`
- Read only: `/home/pch/myGS/datasets/uav_3dgs/raw/thermal`

- [ ] **Step 1: 同步仓库**

```bash
cd /home/pch/myGS/infraredGS
git pull --ff-only
git status
```

Expected:

```text
Your branch is up to date with 'origin/master'.
modified: manifests/dataset_manifest.csv
```

- [ ] **Step 2: 确认图片数量**

```bash
find /home/pch/myGS/datasets/uav_3dgs/raw/visible -maxdepth 1 -type f -name '*_V.JPG' | wc -l
find /home/pch/myGS/datasets/uav_3dgs/raw/thermal -maxdepth 1 -type f -name '*_T.JPG' | wc -l
```

Expected:

```text
339
339
```

## Task 2: 先运行可见光 COLMAP

**Files:**
- Execute: `scripts/run_colmap_visible.sh`
- Output: `/home/pch/myGS/experiments/uav_3dgs/colmap_visible`

- [ ] **Step 1: 设置路径并创建日志目录**

```bash
cd /home/pch/myGS/infraredGS
export DATASET_ROOT="/home/pch/myGS/datasets/uav_3dgs"
export EXPERIMENT_ROOT="/home/pch/myGS/experiments/uav_3dgs"
mkdir -p "$EXPERIMENT_ROOT/logs"
```

- [ ] **Step 2: 运行可见光 COLMAP**

```bash
bash scripts/run_colmap_visible.sh 2>&1 | tee "$EXPERIMENT_ROOT/logs/colmap_visible_$(date +%Y%m%d_%H%M%S).log"
```

Expected:
- `feature_extractor` 完成。
- `exhaustive_matcher` 完成。
- `mapper` 生成 sparse model。

- [ ] **Step 3: 检查 COLMAP 输出**

```bash
ls -lah /home/pch/myGS/experiments/uav_3dgs/colmap_visible
find /home/pch/myGS/experiments/uav_3dgs/colmap_visible/sparse -maxdepth 3 -type f | sort | head -20
```

Expected:
- 存在 `database.db`。
- `sparse` 下存在 `cameras.bin`、`images.bin`、`points3D.bin` 或对应 COLMAP 输出文件。

## Task 3: 新建专用 3DGS conda 环境

**Files:**
- Create on server: conda env `gaussian_splatting`
- Read: `/home/pch/myGS/src/gaussian-splatting/environment.yml`

- [ ] **Step 1: 查看官方环境文件**

```bash
cd /home/pch/myGS/src/gaussian-splatting
sed -n '1,200p' environment.yml
```

- [ ] **Step 2: 新建专用环境**

优先使用官方环境文件，但环境名改为 `gaussian_splatting`：

```bash
cd /home/pch/myGS/src/gaussian-splatting
conda env create -f environment.yml -n gaussian_splatting
```

如果官方环境文件因版本过旧或网络问题失败，停止并把完整报错发回，不要在旧环境里硬装。

- [ ] **Step 3: 验证 PyTorch 和 GPU**

```bash
conda activate gaussian_splatting
python -V
python -c "import torch; print('torch', torch.__version__); print('cuda', torch.version.cuda); print('available', torch.cuda.is_available()); print('gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"
```

Expected:
- `torch` 能导入。
- `torch.cuda.is_available()` 为 `True`。
- GPU 名称显示 RTX 5090 或兼容名称。

## Task 4: 安装或验证 3DGS Python 扩展

**Files:**
- Execute in: `/home/pch/myGS/src/gaussian-splatting`
- Source submodules:
  - `submodules/diff-gaussian-rasterization`
  - `submodules/simple-knn`
  - `submodules/fused-ssim`

- [ ] **Step 1: 在新环境中安装源码依赖**

```bash
conda activate gaussian_splatting
cd /home/pch/myGS/src/gaussian-splatting
pip install -e submodules/diff-gaussian-rasterization
pip install -e submodules/simple-knn
pip install -e submodules/fused-ssim
```

如果 RTX 5090 架构导致 CUDA 扩展编译失败，停止并保存完整报错；下一步再决定 PyTorch/CUDA 版本或编译参数。

- [ ] **Step 2: 验证扩展导入**

```bash
conda activate gaussian_splatting
python -c "import diff_gaussian_rasterization; import simple_knn; print('3DGS extensions ok')"
```

Expected:

```text
3DGS extensions ok
```

## Task 5: 训练可见光 3DGS

**Files:**
- Execute: `scripts/train_3dgs_visible.sh`
- Input: `/home/pch/myGS/experiments/uav_3dgs/colmap_visible`
- Output: `/home/pch/myGS/experiments/uav_3dgs/outputs/3dgs_visible`

- [ ] **Step 1: 先做短训练冒烟测试**

```bash
conda activate gaussian_splatting
cd /home/pch/myGS/infraredGS
export EXPERIMENT_ROOT="/home/pch/myGS/experiments/uav_3dgs"
export GAUSSIAN_REPO="/home/pch/myGS/src/gaussian-splatting"
export ITERATIONS=1000
CUDA_VISIBLE_DEVICES=0 bash scripts/train_3dgs_visible.sh 2>&1 | tee "$EXPERIMENT_ROOT/logs/3dgs_visible_smoke_$(date +%Y%m%d_%H%M%S).log"
```

- [ ] **Step 2: 检查短训练输出**

```bash
ls -lah /home/pch/myGS/experiments/uav_3dgs/outputs/3dgs_visible
find /home/pch/myGS/experiments/uav_3dgs/outputs/3dgs_visible -maxdepth 3 -type f | sort | head -30
```

Expected:
- 模型输出目录存在。
- 训练没有在导入、CUDA 扩展、COLMAP 输入格式处失败。

- [ ] **Step 3: 再决定是否跑完整 30000 iterations**

只有短训练成功后再运行：

```bash
conda activate gaussian_splatting
cd /home/pch/myGS/infraredGS
export EXPERIMENT_ROOT="/home/pch/myGS/experiments/uav_3dgs"
export GAUSSIAN_REPO="/home/pch/myGS/src/gaussian-splatting"
export ITERATIONS=30000
CUDA_VISIBLE_DEVICES=0 bash scripts/train_3dgs_visible.sh 2>&1 | tee "$EXPERIMENT_ROOT/logs/3dgs_visible_full_$(date +%Y%m%d_%H%M%S).log"
```

## Task 6: 红外与融合后续

**Files:**
- Execute later: `scripts/run_colmap_thermal.sh`
- Execute later: `scripts/train_3dgs_thermal.sh`

- [ ] **Step 1: 可见光链路成功后再运行红外 COLMAP**

```bash
cd /home/pch/myGS/infraredGS
export DATASET_ROOT="/home/pch/myGS/datasets/uav_3dgs"
export EXPERIMENT_ROOT="/home/pch/myGS/experiments/uav_3dgs"
bash scripts/run_colmap_thermal.sh 2>&1 | tee "$EXPERIMENT_ROOT/logs/colmap_thermal_$(date +%Y%m%d_%H%M%S).log"
```

- [ ] **Step 2: 根据红外 COLMAP 结果决定是否训练红外 3DGS**

如果红外 COLMAP 失败，先记录失败原因，不强行训练。只有 `sparse` 输出可用后再运行红外 3DGS。

- [ ] **Step 3: C 阶段融合暂不开始**

C 阶段要等可见光和红外至少有可比较的重建结果后再设计，不在当前阶段抢跑。

## 自查结果

- 目标已重新收束：先可见光 COLMAP，再 3DGS 环境和训练。
- 已明确当前没有跑过 COLMAP，不能声称进入训练阶段。
- 已明确新建专用 conda 环境，不再尝试复用 `ntrgs`。
- 已保留服务器生成的 `manifests/dataset_manifest.csv`，不删除、不覆盖。
