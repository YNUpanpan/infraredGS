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
