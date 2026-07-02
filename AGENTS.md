# 项目协作规范

## 文档语言

- `AGENTS.md`、`AGENT.md`、`README.md`、`docs/**/*.md` 以及项目内其他 Markdown 文档默认使用中文书写。
- 只有在表达命令、路径、文件名、配置键、代码标识符、软件名、论文/算法名或专有技术名词时保留英文，例如 `3DGS`、`COLMAP`、`GitHub`、`CUDA`、`PyTorch`、`README.md`。

## 文件删除限制

- 禁止批量删除文件或目录。
- 不使用 `del /s`、`rd /s`、`rmdir /s`、`Remove-Item -Recurse`、`rm -rf`。
- 如需删除文件，只能一次删除一个明确路径的文件。
- 如果需要批量删除文件，应停止操作，并请用户手动删除。

## 数据与 Git 规则

- 原始无人机图片不进入 Git 或 GitHub。
- Git 仓库只跟踪文档、脚本、配置、manifest、日志和小型文本产物。
- 在执行 `git add` 前，应确认不会把 `*.JPG`、重建输出、模型 checkpoint 或 COLMAP 生成物加入暂存区。
