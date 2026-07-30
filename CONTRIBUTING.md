# Git 协作与备份约定

本项目采用“小步提交、可恢复、禁止覆盖公共历史”的工作方式。

## 每次更新前

1. 确认工作区干净，并查看当前分支与最近提交。
2. 获取远端最新状态；只使用快进合并或功能分支，不直接覆盖远端历史。
3. 在当前稳定提交上创建备份标签：

   ```powershell
   git tag backup/YYYYMMDD-HHMM-topic
   git push origin backup/YYYYMMDD-HHMM-topic
   ```

4. 较大的功能从 `main` 创建 `feature/...` 分支；小型且已验证的初始化工作可以直接提交到 `main`。

## 每次推送前

1. 查看 `git status`、本次差异和待推送的提交列表。
2. 运行与改动相关的测试或启动验证。
3. 确认提交信息简短、明确，一次提交只表达一个完整目的。
4. 先确认备份标签已推送，再推送代码分支。
5. 不对 `main` 使用强制推送；遇到远端新提交时先停止并安全整合。

## 提交信息

采用 Conventional Commits 风格，例如：

```text
feat: add draggable transparent window
fix: keep pet inside screen bounds
docs: record asset sources
chore: update build configuration
```

## 素材与大文件

- 原始网络素材先放入 `assets/character/source/`，记录来源与许可状态。
- 未确认授权的素材不提交到公共仓库。
- 大体积二进制文件需要评估是否使用 Git LFS，不能直接塞入普通 Git 历史。

