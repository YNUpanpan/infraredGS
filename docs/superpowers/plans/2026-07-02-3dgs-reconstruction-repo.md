# 3DGS 可见光与红外重建仓库 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一个中文文档优先、原始图片不入库、可复现 3DGS 可见光/红外重建实验仓库。

**Architecture:** 仓库分为文档层、配置层、数据清单层和服务器执行模板层。`prepare_dataset.py` 只做 inventory 和配对检查，不移动、不复制、不删除图片；服务器脚本只作为可修改模板，真实 CUDA/PyTorch/COLMAP 命令在上机确认环境后再收紧。

**Tech Stack:** Markdown、Python 3 标准库、pytest、Bash、Git、COLMAP、3DGS、CUDA、PyTorch。

---

## 文件结构

- 创建：`.gitignore`，负责阻止原始图片、COLMAP 输出、模型和实验生成物进入 Git。
- 创建：`README.md`，中文说明项目目标、数据边界、B/C 阶段流程和使用顺序。
- 创建：`configs/dataset.example.yaml`，记录本地和服务器数据路径示例。
- 创建：`configs/gaussian-splatting.example.yaml`，记录 3DGS 训练参数示例。
- 创建：`manifests/.gitkeep`，保留 manifest 目录。
- 创建：`scripts/prepare_dataset.py`，扫描图片、按序号配对、输出 CSV，不做文件移动。
- 创建：`tests/test_prepare_dataset.py`，覆盖配对、缺失、非目标文件忽略和 CSV 输出。
- 创建：`scripts/run_colmap_visible.sh`，可见光 COLMAP 模板。
- 创建：`scripts/run_colmap_thermal.sh`，红外 COLMAP 模板。
- 创建：`scripts/train_3dgs_visible.sh`，可见光 3DGS 训练模板。
- 创建：`scripts/train_3dgs_thermal.sh`，红外 3DGS 训练模板。
- 创建：`scripts/archive_results.sh`，实验结果归档模板。
- 创建：`docs/server-runbook.md`，中文服务器操作手册。
- 创建：`docs/reconstruction-design.md`，中文 B 阶段独立重建说明。
- 创建：`docs/fusion-plan.md`，中文 C 阶段融合说明。
- 创建：`docs/github-publish.md`，中文 GitHub 发布前检查流程。
- 修改：`AGENT.md`，记录本轮计划任务。

### Task 1: 仓库护栏与入口文档

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Modify: `AGENT.md`

- [ ] **Step 1: 写入 `.gitignore`**

创建 `.gitignore`，内容如下：

```gitignore
# 原始无人机影像，不进入 Git
*.JPG
*.jpg
*.JPEG
*.jpeg
*.png
*.tif
*.tiff
*.raw
*.MRK

# 本地或服务器数据目录
data/raw/
data/processed/

# COLMAP、3DGS 和实验输出
work/
outputs/
experiments/
*.db
*.bin
*.ply
*.pt
*.pth
*.ckpt

# Python 缓存与测试缓存
__pycache__/
.pytest_cache/
*.pyc

# 本地临时目录
.superpowers/
.git_template/
```

- [ ] **Step 2: 写入中文 `README.md`**

创建 `README.md`，内容如下：

```markdown
# 3DGS 可见光与红外无人机重建

本项目用于管理 339 张可见光无人机图像和 339 张红外无人机图像的 3D Gaussian Splatting 重建实验。

## 数据边界

- 原始图片不进入 Git 或 GitHub。
- Git 只跟踪文档、脚本、配置、manifest 和小型日志。
- `scripts/prepare_dataset.py` 默认只生成数据清单，不移动、不复制、不删除图片。

## 实验顺序

1. B 阶段：可见光和红外分别独立运行 COLMAP 与 3DGS。
2. C 阶段：使用可见光几何作为参考，再尝试红外配准与融合。

## 当前状态

当前仓库先准备本地文档和脚本模板；RTX 5090、Ubuntu 22.04 服务器暂不直接连接。

## 主要文件

- `AGENTS.md`：项目协作规范。
- `AGENT.md`：每次对话和任务日志。
- `docs/server-runbook.md`：服务器操作手册。
- `scripts/prepare_dataset.py`：数据配对和 manifest 生成工具。
- `configs/*.example.yaml`：配置示例。
```

- [ ] **Step 3: 更新 `AGENT.md`**

在 `AGENT.md` 追加：

```markdown
## 2026-07-02 Session 003

### 用户需求
- 继续推进已通过的设计 spec，进入 implementation plan。

### 已确认决策
- 使用 `superpowers:writing-plans` 生成实施计划。
- 本阶段只写计划，不直接开始实现脚本或移动数据。

### 已完成动作
- 创建实施计划 `docs/superpowers/plans/2026-07-02-3dgs-reconstruction-repo.md`。

### 下一步
- 用户选择执行方式：Subagent-Driven 或 Inline Execution。
```

- [ ] **Step 4: 验证 Git 不会纳入图片**

Run:

```powershell
git status --short -- *.JPG *.MRK
```

Expected: 仍可能显示未跟踪图片，因为 `.gitignore` 对已经按 shell 展开的显式路径不会隐藏；必须再运行：

```powershell
git status --short
```

Expected: 不显示 `DJI_*.JPG` 和 `.MRK` 文件。

- [ ] **Step 5: 提交 Task 1**

Run:

```powershell
git add .gitignore README.md AGENT.md
git diff --cached --name-only
git commit -m "Add repository guardrails and README"
```

Expected staged files:

```text
.gitignore
AGENT.md
README.md
```

### Task 2: 数据 manifest 工具与测试

**Files:**
- Create: `scripts/prepare_dataset.py`
- Create: `tests/test_prepare_dataset.py`
- Create: `manifests/.gitkeep`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_prepare_dataset.py`：

```python
import csv
from pathlib import Path

from scripts.prepare_dataset import build_manifest, write_manifest


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def test_build_manifest_pairs_visible_and_thermal_by_sequence(tmp_path):
    touch(tmp_path / "DJI_20260602140225_0400_V.JPG")
    touch(tmp_path / "DJI_20260602140225_0400_T.JPG")

    rows = build_manifest(tmp_path)

    assert rows == [
        {
            "sequence_id": "0400",
            "visible_filename": "DJI_20260602140225_0400_V.JPG",
            "thermal_filename": "DJI_20260602140225_0400_T.JPG",
            "visible_exists": "yes",
            "thermal_exists": "yes",
            "notes": "",
        }
    ]


def test_build_manifest_reports_missing_pair(tmp_path):
    touch(tmp_path / "DJI_20260602140225_0400_V.JPG")
    touch(tmp_path / "DJI_20260602140226_0401_T.JPG")

    rows = build_manifest(tmp_path)

    assert rows[0]["sequence_id"] == "0400"
    assert rows[0]["thermal_exists"] == "no"
    assert rows[0]["notes"] == "missing thermal"
    assert rows[1]["sequence_id"] == "0401"
    assert rows[1]["visible_exists"] == "no"
    assert rows[1]["notes"] == "missing visible"


def test_build_manifest_ignores_non_target_files(tmp_path):
    touch(tmp_path / "DJI_20260602140225_0400_V.JPG")
    touch(tmp_path / "notes.txt")
    touch(tmp_path / "preview.png")

    rows = build_manifest(tmp_path)

    assert len(rows) == 1
    assert rows[0]["sequence_id"] == "0400"


def test_write_manifest_outputs_csv(tmp_path):
    rows = [
        {
            "sequence_id": "0400",
            "visible_filename": "v.JPG",
            "thermal_filename": "t.JPG",
            "visible_exists": "yes",
            "thermal_exists": "yes",
            "notes": "",
        }
    ]
    output = tmp_path / "manifest.csv"

    write_manifest(rows, output)

    with output.open("r", encoding="utf-8", newline="") as handle:
        loaded = list(csv.DictReader(handle))
    assert loaded == rows
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
pytest tests/test_prepare_dataset.py -q
```

Expected: FAIL，错误包含 `ModuleNotFoundError` 或 `cannot import name 'build_manifest'`。

- [ ] **Step 3: 写最小实现**

创建 `scripts/prepare_dataset.py`：

```python
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = [
    "sequence_id",
    "visible_filename",
    "thermal_filename",
    "visible_exists",
    "thermal_exists",
    "notes",
]

IMAGE_PATTERN = re.compile(r"_(?P<sequence>\d{4})_(?P<kind>[VT])\.JPG$", re.IGNORECASE)


def scan_images(root: Path) -> dict[str, dict[str, str]]:
    pairs: dict[str, dict[str, str]] = {}
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        match = IMAGE_PATTERN.search(path.name)
        if match is None:
            continue
        sequence = match.group("sequence")
        kind = match.group("kind").upper()
        pairs.setdefault(sequence, {})
        if kind == "V":
            pairs[sequence]["visible"] = path.name
        elif kind == "T":
            pairs[sequence]["thermal"] = path.name
    return pairs


def build_manifest(root: Path) -> list[dict[str, str]]:
    pairs = scan_images(root)
    rows: list[dict[str, str]] = []
    for sequence in sorted(pairs):
        visible = pairs[sequence].get("visible", "")
        thermal = pairs[sequence].get("thermal", "")
        notes = ""
        if not visible:
            notes = "missing visible"
        elif not thermal:
            notes = "missing thermal"
        rows.append(
            {
                "sequence_id": sequence,
                "visible_filename": visible,
                "thermal_filename": thermal,
                "visible_exists": "yes" if visible else "no",
                "thermal_exists": "yes" if thermal else "no",
                "notes": notes,
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成可见光/红外无人机图像 manifest。")
    parser.add_argument("--input", type=Path, default=Path("."), help="原始图片所在目录")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("manifests/dataset_manifest.csv"),
        help="输出 CSV 路径",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_manifest(args.input)
    write_manifest(rows, args.output)
    complete = sum(1 for row in rows if row["visible_exists"] == "yes" and row["thermal_exists"] == "yes")
    print(f"manifest rows: {len(rows)}")
    print(f"complete pairs: {complete}")
    print(f"output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `manifests/.gitkeep`，内容为空。

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
pytest tests/test_prepare_dataset.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 5: 对当前数据生成 manifest**

Run:

```powershell
python scripts/prepare_dataset.py --input . --output manifests/dataset_manifest.csv
```

Expected:

```text
manifest rows: 339
complete pairs: 339
output: manifests/dataset_manifest.csv
```

- [ ] **Step 6: 提交 Task 2**

Run:

```powershell
git add scripts/prepare_dataset.py tests/test_prepare_dataset.py manifests/.gitkeep manifests/dataset_manifest.csv
git diff --cached --name-only
git commit -m "Add dataset manifest generator"
```

Expected staged files:

```text
manifests/.gitkeep
manifests/dataset_manifest.csv
scripts/prepare_dataset.py
tests/test_prepare_dataset.py
```

### Task 3: 配置示例与服务器脚本模板

**Files:**
- Create: `configs/dataset.example.yaml`
- Create: `configs/gaussian-splatting.example.yaml`
- Create: `scripts/run_colmap_visible.sh`
- Create: `scripts/run_colmap_thermal.sh`
- Create: `scripts/train_3dgs_visible.sh`
- Create: `scripts/train_3dgs_thermal.sh`
- Create: `scripts/archive_results.sh`

- [ ] **Step 1: 写配置示例**

创建 `configs/dataset.example.yaml`：

```yaml
project_root: ~/projects/uav-thermal-visible-3dgs
dataset_root: ~/datasets/uav_3dgs
experiment_root: ~/experiments/uav_3dgs

raw:
  visible: ~/datasets/uav_3dgs/raw/visible
  thermal: ~/datasets/uav_3dgs/raw/thermal

manifest: manifests/dataset_manifest.csv
```

创建 `configs/gaussian-splatting.example.yaml`：

```yaml
visible:
  source_path: ~/experiments/uav_3dgs/colmap_visible
  model_path: ~/experiments/uav_3dgs/outputs/3dgs_visible
  iterations: 30000

thermal:
  source_path: ~/experiments/uav_3dgs/colmap_thermal
  model_path: ~/experiments/uav_3dgs/outputs/3dgs_thermal
  iterations: 30000
```

- [ ] **Step 2: 写 COLMAP 模板**

创建 `scripts/run_colmap_visible.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

DATASET_ROOT="${DATASET_ROOT:-$HOME/datasets/uav_3dgs}"
EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"
IMAGE_DIR="$DATASET_ROOT/raw/visible"
WORK_DIR="$EXPERIMENT_ROOT/colmap_visible"

mkdir -p "$WORK_DIR/sparse" "$WORK_DIR/dense"

colmap feature_extractor \
  --database_path "$WORK_DIR/database.db" \
  --image_path "$IMAGE_DIR" \
  --ImageReader.single_camera 1

colmap exhaustive_matcher \
  --database_path "$WORK_DIR/database.db"

colmap mapper \
  --database_path "$WORK_DIR/database.db" \
  --image_path "$IMAGE_DIR" \
  --output_path "$WORK_DIR/sparse"
```

创建 `scripts/run_colmap_thermal.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

DATASET_ROOT="${DATASET_ROOT:-$HOME/datasets/uav_3dgs}"
EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"
IMAGE_DIR="$DATASET_ROOT/raw/thermal"
WORK_DIR="$EXPERIMENT_ROOT/colmap_thermal"

mkdir -p "$WORK_DIR/sparse" "$WORK_DIR/dense"

colmap feature_extractor \
  --database_path "$WORK_DIR/database.db" \
  --image_path "$IMAGE_DIR" \
  --ImageReader.single_camera 1

colmap exhaustive_matcher \
  --database_path "$WORK_DIR/database.db"

colmap mapper \
  --database_path "$WORK_DIR/database.db" \
  --image_path "$IMAGE_DIR" \
  --output_path "$WORK_DIR/sparse"
```

- [ ] **Step 3: 写 3DGS 训练模板**

创建 `scripts/train_3dgs_visible.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

GAUSSIAN_REPO="${GAUSSIAN_REPO:-$HOME/src/gaussian-splatting}"
EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"

python "$GAUSSIAN_REPO/train.py" \
  -s "$EXPERIMENT_ROOT/colmap_visible" \
  -m "$EXPERIMENT_ROOT/outputs/3dgs_visible" \
  --iterations "${ITERATIONS:-30000}"
```

创建 `scripts/train_3dgs_thermal.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

GAUSSIAN_REPO="${GAUSSIAN_REPO:-$HOME/src/gaussian-splatting}"
EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"

python "$GAUSSIAN_REPO/train.py" \
  -s "$EXPERIMENT_ROOT/colmap_thermal" \
  -m "$EXPERIMENT_ROOT/outputs/3dgs_thermal" \
  --iterations "${ITERATIONS:-30000}"
```

- [ ] **Step 4: 写归档模板**

创建 `scripts/archive_results.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"
REPORT_DIR="$EXPERIMENT_ROOT/outputs/reports"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$REPORT_DIR/run_$STAMP.md"

mkdir -p "$REPORT_DIR"

{
  echo "# 实验记录 $STAMP"
  echo
  echo "## 环境"
  nvidia-smi || true
  echo
  echo "## 输出目录"
  find "$EXPERIMENT_ROOT/outputs" -maxdepth 2 -type d | sort
} > "$REPORT"

echo "$REPORT"
```

- [ ] **Step 5: 检查脚本语法**

Run:

```powershell
bash -n scripts/run_colmap_visible.sh
bash -n scripts/run_colmap_thermal.sh
bash -n scripts/train_3dgs_visible.sh
bash -n scripts/train_3dgs_thermal.sh
bash -n scripts/archive_results.sh
```

Expected: 所有命令 exit 0，无输出。

- [ ] **Step 6: 提交 Task 3**

Run:

```powershell
git add configs scripts/*.sh
git diff --cached --name-only
git commit -m "Add server configuration and script templates"
```

Expected staged files include:

```text
configs/dataset.example.yaml
configs/gaussian-splatting.example.yaml
scripts/archive_results.sh
scripts/run_colmap_thermal.sh
scripts/run_colmap_visible.sh
scripts/train_3dgs_thermal.sh
scripts/train_3dgs_visible.sh
```

### Task 4: 中文操作文档

**Files:**
- Create: `docs/server-runbook.md`
- Create: `docs/reconstruction-design.md`
- Create: `docs/fusion-plan.md`
- Create: `docs/github-publish.md`

- [ ] **Step 1: 写 `docs/server-runbook.md`**

内容包含以下小节：

````markdown
# RTX 5090 Ubuntu 22.04 服务器操作手册

## 目标

在服务器上复现可见光和红外 3DGS 重建实验。

## 环境检查

运行：

```bash
nvidia-smi
nvcc --version
git --version
conda --version
df -h
```

记录 GPU、driver、CUDA、磁盘空间和 conda 状态。

## 推荐目录

```text
~/projects/uav-thermal-visible-3dgs/
~/datasets/uav_3dgs/raw/visible/
~/datasets/uav_3dgs/raw/thermal/
~/experiments/uav_3dgs/
```

## 执行顺序

1. 克隆或同步本仓库。
2. 把原始图片放到服务器数据目录，图片不进入 Git。
3. 运行 manifest 检查。
4. 运行可见光 COLMAP 和 3DGS。
5. 运行红外 COLMAP 和 3DGS。
6. 根据 B 阶段结果决定 C 阶段融合方式。
````

- [ ] **Step 2: 写 `docs/reconstruction-design.md`**

内容包含 B 阶段流程：可见光独立重建、红外独立重建、结果比较、失败记录。明确红外 COLMAP 失败时记录失败原因，而不是强行继续训练。

- [ ] **Step 3: 写 `docs/fusion-plan.md`**

内容包含 C 阶段流程：读取 manifest、生成 `pair_map.csv`、使用可见光 COLMAP 作为参考、判断是否需要标定或单应配准、输出 `fusion_report.md`。

- [ ] **Step 4: 写 `docs/github-publish.md`**

内容包含发布前检查命令：

```bash
git status --short
git diff --cached --name-only
git ls-files "*.JPG" "*.jpg" "*.MRK" "*.ply" "*.pt" "*.pth" "*.ckpt"
```

文档说明：如果 `git ls-files` 输出任何原始图片或大模型文件，停止发布并先修正。

- [ ] **Step 5: 检查 Markdown 语言规范**

Run:

```powershell
rg -n "占位内容|未补全|英文旧标题" AGENT.md AGENTS.md README.md docs --glob "!docs/superpowers/plans/**"
```

Expected: exit 1 或无输出。

- [ ] **Step 6: 提交 Task 4**

Run:

```powershell
git add docs/server-runbook.md docs/reconstruction-design.md docs/fusion-plan.md docs/github-publish.md
git commit -m "Add Chinese reconstruction documentation"
```

### Task 5: 总体验证与收尾记录

**Files:**
- Modify: `AGENT.md`

- [ ] **Step 1: 运行 Python 测试**

Run:

```powershell
pytest tests/test_prepare_dataset.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 2: 重新生成 manifest 并验证数量**

Run:

```powershell
python scripts/prepare_dataset.py --input . --output manifests/dataset_manifest.csv
```

Expected:

```text
manifest rows: 339
complete pairs: 339
output: manifests/dataset_manifest.csv
```

- [ ] **Step 3: 检查大文件未被跟踪**

Run:

```powershell
git ls-files "*.JPG" "*.jpg" "*.MRK" "*.ply" "*.pt" "*.pth" "*.ckpt"
```

Expected: 无输出。

- [ ] **Step 4: 检查工作区**

Run:

```powershell
git status --short
```

Expected: 只允许显示未跟踪的原始图片、`.MRK`、历史迁移日志或本地临时文件；不允许显示已计划提交但未提交的仓库文档、脚本、配置、测试。

- [ ] **Step 5: 更新 `AGENT.md`**

追加：

```markdown
### 实施结果
- 已创建仓库护栏、中文入口文档、数据 manifest 工具、测试、配置示例、服务器脚本模板和中文操作文档。
- 已验证 manifest 当前数据为 339 对完整可见光/红外图像。
- 已验证 Git 没有跟踪原始图片或大模型文件。
```

- [ ] **Step 6: 提交收尾记录**

Run:

```powershell
git add AGENT.md manifests/dataset_manifest.csv
git commit -m "Record repository setup verification"
```

## 自查结果

- Spec 覆盖：Task 1 覆盖仓库与数据边界；Task 2 覆盖 manifest；Task 3 覆盖服务器脚本模板；Task 4 覆盖中文 runbook、B 阶段、C 阶段、GitHub 发布；Task 5 覆盖验证与日志记录。
- 占位符检查：计划中没有使用“占位内容”“未补全”或含糊的补充说明作为实施步骤。
- 类型一致性：`build_manifest(root: Path)`、`write_manifest(rows, output)`、CSV 字段名和测试断言保持一致。
