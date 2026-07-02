# 3DGS 可见光与红外无人机重建设计

## 背景

数据集包含 339 张可见光无人机图像和 339 张红外无人机图像，采集方式为环绕飞行拍摄。当前本地工作区中包含 DJI 风格的配对文件名，例如 `*_V.JPG` 和 `*_T.JPG`，并包含一个时间戳 `.MRK` 文件。目标计算环境是 RTX 5090、Ubuntu 22.04 服务器，但当前阶段不连接或操作该服务器。

项目会整理成一个可复现实验仓库。Git 只跟踪文档、脚本、配置、manifest 和日志。原始图片、COLMAP 工作产物、模型 checkpoint、Gaussian 输出和其他大体积生成物都保留在 Git 之外。

## 目标

- 建立轻量级本地仓库结构，用于复现 3DGS 实验。
- 将所有任务决策和执行动作记录到 `AGENT.md`。
- 准备一套流程：先运行可见光和红外独立重建，再尝试“可见光几何 + 红外配准”的融合。
- 准备 Ubuntu 22.04、RTX 5090 服务器说明和脚本模板，同时不假设服务器环境已经配置完成。
- 确保所有原始无人机图片不进入 GitHub。

## 非目标

- 不上传 678 张原始图片到 GitHub。
- 当前阶段不直接操作 RTX 5090 服务器。
- 在检查真实服务器环境前，不构建一键式全自动 pipeline。
- 不批量删除文件或目录。

## 仓库设计

仓库应组织为可复现实验项目：

```text
project/
  AGENTS.md
  AGENT.md
  README.md
  .gitignore
  docs/
    server-runbook.md
    reconstruction-design.md
    fusion-plan.md
    github-publish.md
  scripts/
    prepare_dataset.py
    run_colmap_visible.sh
    run_colmap_thermal.sh
    train_3dgs_visible.sh
    train_3dgs_thermal.sh
    archive_results.sh
  configs/
    dataset.example.yaml
    gaussian-splatting.example.yaml
  manifests/
    dataset_manifest.csv
```

原始数据可以先保留在当前目录，后续也可以迁移到本地或服务器数据目录。Git 忽略规则必须排除原始图片和生成物，包括 `*.JPG`、`data/raw/`、`work/`、`outputs/`、`*.ply`、checkpoint、COLMAP 数据库和模型二进制文件。

## 数据 Manifest

`scripts/prepare_dataset.py` 会检查可见光和红外文件名，按序号配对记录，并写入 `manifests/dataset_manifest.csv`。manifest 至少包含：

- 序号。
- 可见光文件名。
- 红外文件名。
- 可见光文件是否存在。
- 红外文件是否存在。
- 备注。

当前数据看起来包含 339 个可见光文件和 339 个红外文件。设计上假设同序号文件名，例如 `0400_V.JPG` 与 `0400_T.JPG`，代表一组配对采集，但 manifest 步骤会显式验证这一点。

## B 阶段：独立重建

第一阶段分别运行可见光和红外重建流程：

```text
data/raw/
  visible/
  thermal/

work/
  colmap_visible/
  colmap_thermal/

outputs/
  3dgs_visible/
  3dgs_thermal/
  reports/
```

可见光流程：

1. 使用可见光图像作为 COLMAP 输入。
2. 生成相机位姿、稀疏重建和 3DGS 兼容输入。
3. 训练可见光 3DGS 模型。
4. 归档日志、命令、关键参数和视觉质量观察。

红外流程：

1. 使用红外图像作为 COLMAP 输入。
2. 尝试独立估计相机位姿并生成稀疏重建。
3. 如果 COLMAP 输出可用，则训练红外 3DGS 模型。
4. 记录红外特有失败模式，例如纹理弱、重复区域多或匹配质量不足。

B 阶段成功标准是得到两个可比较的基线：尽可能稳定的可见光模型，以及红外模型或清晰的失败分析。

## C 阶段：可见光几何 + 红外融合

C 阶段依赖 B 阶段结果。它不替代独立基线，而是创建第三条实验线：

```text
work/
  fusion/
    pair_map.csv
    visible_colmap_reference/
    thermal_registered/
    transforms/
    diagnostics/

outputs/
  fusion_visible_geometry_thermal_view/
  reports/fusion_report.md
```

融合流程：

1. 通过 manifest 确认可见光/红外图像配对关系。
2. 使用可见光 COLMAP 位姿和稀疏几何作为稳定参考。
3. 如果双传感器对齐足够好，则按序号把红外图像绑定到可见光位姿。
4. 如果直接绑定不够准确，则增加标定、仿射、单应或其他配准步骤。
5. 输出诊断结果，检查红外视图是否能与可见光几何对齐。
6. 在 `fusion_report.md` 中记录融合假设、失败样例和所需标定工作。

## 服务器 Runbook 范围

`docs/server-runbook.md` 将覆盖：

- Ubuntu 22.04 系统检查：GPU、driver、CUDA、磁盘、conda、git、编译工具。
- 服务器上的推荐项目目录、数据目录和实验目录。
- COLMAP 安装或编译策略。
- 面向 RTX 5090 的 PyTorch/CUDA 与 3DGS 依赖策略。
- 数据传输要求，原始图片保留在 Git 仓库之外。
- B 阶段可见光和红外执行命令。
- C 阶段融合准备和诊断。
- 结果归档与实验记录格式。

由于 RTX 5090 可能需要较新的 CUDA 和 PyTorch 构建，runbook 必须要求操作者在真实服务器上先确认 `nvidia-smi`、driver 版本、CUDA 版本和 PyTorch CUDA 兼容性，再最终确定安装命令。

## Git 与 GitHub 流程

初始仓库只做本地 git。GitHub remote 在忽略规则和仓库结构确认后再配置。

后续发布流程：

1. 检查 `git status`。
2. 确认没有原始图片、checkpoint、COLMAP 输出或模型文件进入 staging。
3. 添加 GitHub remote。
4. push 本地仓库。
5. 之后每次任务继续提交 `AGENT.md` 更新。

## 安全约束

- 不使用批量删除命令，例如 `rm -rf`、`del /s`、`rd /s`、`rmdir /s` 或递归 `Remove-Item`。
- 如果需要清理大量文件，停止操作并请用户手动处理。
- 如果不可避免且已获批准，只能一次删除一个明确路径的文件。
- 原始图片不进入版本控制。

## 待实施项目

- 在本设计经用户 review 后，创建 `.gitignore`、`README.md`、docs、configs、manifests 和 scripts。
- 决定 `prepare_dataset.py` 只做 inventory、复制文件，还是移动文件。最安全默认值是只做 inventory；任何文件移动前都需要用户明确确认。
- 在最终确定 CUDA/PyTorch 安装命令前，检查真实 RTX 5090 服务器环境。
