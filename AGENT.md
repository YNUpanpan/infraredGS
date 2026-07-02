# Agent 工作日志

## 2026-07-02 Session 001

### 用户需求
- 为 339 张可见光无人机图像和 339 张红外无人机图像规划 3D Gaussian Splatting 三维重建流程。
- 后续使用 RTX 5090、Ubuntu 22.04 服务器，但当前阶段暂不连接或操作服务器。
- 每次对话任务都记录到 `AGENT.md`。
- 后续上传到 GitHub，但原始图片不进入仓库。

### 已确认决策
- GitHub 只跟踪文档、脚本、配置、manifest 和日志；原始图片不上传。
- 重建顺序：先做可见光和红外的独立 3DGS 重建，再尝试“可见光几何 + 红外配准”的融合流程。
- 初始交付物：可复现实验本地仓库设计、服务器 runbook、脚本模板。
- 服务器使用方式：当前只准备本地仓库和可复现文档，不直接操作 RTX 5090 服务器。
- GitHub 使用方式：先初始化本地 git 仓库，远端地址之后再配置。
- 仓库风格：采用“可复现实验仓库”，不做极简笔记仓库，也暂不做全自动 pipeline。

### 已完成动作
- 检查工作目录，确认包含 339 个 `*_V.JPG` 可见光文件和 339 个 `*_T.JPG` 红外文件。
- 确认工作目录最初还不是 git 仓库。
- 确认工作区最初没有 `AGENT.md` 或 `AGENTS.md` 文件。
- 按五个部分起草并确认高层设计：
  - 仓库与数据边界。
  - 可见光/红外独立重建流程。
  - 后续“可见光几何 + 红外配准”融合流程。
  - `AGENT.md`、本地 git 与后续 GitHub 发布流程。
  - RTX 5090、Ubuntu 22.04 服务器 runbook 和脚本模板范围。
- 写入设计文档 `docs/superpowers/specs/2026-07-02-3dgs-reconstruction-design.md`。
- 初始化本地 git 仓库，并提交 `AGENT.md` 与设计文档。

### 下一步
- 用户 review 已写入的设计 spec。
- 用户确认后，进入 implementation plan，规划 `.gitignore`、`README.md`、server runbook、脚本模板和 manifest 生成器。

## 2026-07-02 Session 002

### 用户需求
- 以后 `AGENTS.md` 和其他所有 `.md` 文件默认使用中文书写，除非是特定英文、命令、路径、文件名或专有技术名词。

### 已确认决策
- 项目 Markdown 文档默认使用中文。
- 保留必要英文：例如 `3DGS`、`COLMAP`、`GitHub`、`README.md`、命令、路径、配置键和文件名。

### 已完成动作
- 将既有 `AGENT.md` 转为中文。
- 将既有 3DGS reconstruction design spec 转为中文。
- 新增 `AGENTS.md`，记录项目级协作与文档语言规范。

### 下一步
- 提交中文化后的 Markdown 文档。

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

## 2026-07-02 Session 004

### 用户需求
- 选择 Inline Execution，在当前会话执行实施计划。

### 已确认决策
- 使用 `superpowers:executing-plans` 执行 `docs/superpowers/plans/2026-07-02-3dgs-reconstruction-repo.md`。
- 使用隔离 worktree 和分支 `codex/3dgs-repo-setup`，避免直接在 `master` 上实现。

### 已完成动作
- 在 `master` 上提交最小 `.gitignore`，忽略 `.worktrees/`。
- 创建隔离 worktree `.worktrees/codex-3dgs-repo-setup`。
- 开始 Task 1：仓库护栏与入口文档。

### 下一步
- 完成 `.gitignore`、`README.md` 和本轮日志更新，并提交 Task 1。

### 实施结果
- 已创建仓库护栏、中文入口文档、数据 manifest 工具、测试、配置示例、服务器脚本模板和中文操作文档。
- 已验证 manifest 当前数据为 339 对完整可见光/红外图像。
- 已验证 Git 没有跟踪原始图片、`.MRK`、点云、checkpoint 或大模型文件。
- 已在分支 `codex/3dgs-repo-setup` 按任务分步提交。
- 已将 `codex/3dgs-repo-setup` fast-forward 合并回 `master`。
- 合并后重新验证：`pytest` 通过 4 个测试，manifest 为 339 对完整配对，Git 未跟踪原始图片或模型大文件。
- 因项目规则禁止批量删除目录，保留 `.worktrees/codex-3dgs-repo-setup`，未自动清理 worktree 目录。

## 2026-07-02 Session 005

### 用户需求
- 将本地仓库上传到 GitHub 远端 `git@github.com:YNUpanpan/infraredGS.git`。

### 已确认决策
- 使用 SSH remote `git@github.com:YNUpanpan/infraredGS.git` 作为 `origin`。
- 上传前继续检查不跟踪原始图片、`.MRK`、点云、checkpoint 或模型大文件。
- 未跟踪的 `migration_robocopy_20260629.log` 不纳入本次提交和上传。

### 已完成动作
- 检查当前分支为 `master`。
- 检查当前尚未配置 Git remote。
- 检查大文件跟踪清单为空。

### 下一步
- 提交本轮 `AGENT.md` 记录。
- 配置 `origin` 并 push 到 GitHub。

### 实施结果
- 已添加 `origin`：`git@github.com:YNUpanpan/infraredGS.git`。
- 上传前验证通过：`pytest` 通过 4 个测试，大文件跟踪清单为空。
- 已执行 `git push -u origin master`，`master` 已推送到 GitHub 并跟踪 `origin/master`。
