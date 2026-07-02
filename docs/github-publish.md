# GitHub 发布前检查

## 目标

发布到 GitHub 前，确认仓库只包含文档、脚本、配置、manifest 和小型文本日志，不包含原始图片、COLMAP 输出、模型 checkpoint 或 3DGS 大文件。

## 必做检查

```bash
git status --short
git diff --cached --name-only
git ls-files "*.JPG" "*.jpg" "*.MRK" "*.ply" "*.pt" "*.pth" "*.ckpt"
```

如果 `git ls-files` 输出任何原始图片或大模型文件，停止发布并先修正 `.gitignore` 或暂存区。

## 添加远端

确认检查通过后，再配置 GitHub remote：

```bash
git remote add origin <github-repo-url>
git push -u origin <branch-name>
```

`<github-repo-url>` 和 `<branch-name>` 需要替换为真实仓库地址和分支名。

## 后续提交规则

- 每次任务后更新 `AGENT.md`。
- 每次提交前运行发布前检查。
- 不把 `data/raw/`、`work/`、`outputs/`、`experiments/` 中的生成物加入 Git。
- 如果需要分享大体积结果，使用外部存储或专门的数据管理方式，不直接放入普通 GitHub 仓库。
