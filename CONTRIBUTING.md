# 参与贡献

感谢关注。本仓库的核心约束是**离线、零依赖、可核验**，贡献前请先确认改动不破坏这三条。

## 环境

```bash
git clone https://github.com/stillsurge/embedded-toolkit.git
cd embedded-toolkit
python -m pip install -r requirements-dev.txt   # 只有 pytest
```

运行时（`shared/etk_core` 与各技能的 `scripts/`）**只能使用 Python 3.10+ 标准库**，不允许引入任何第三方包。

## 提交前必跑

```bash
python tools/sync_core.py      # 改动 shared/etk_core 后必须执行
python tools/check_repo.py     # 仓库质量门，必须输出「仓库检查通过。」
python -m pytest -q            # 单元与集成测试
```

CI 在 ubuntu / windows / macOS × Python 3.10 / 3.12 上跑这三条，任一失败即阻断。

**改动 `shared/etk_core` 却忘了 `sync_core.py`，质量门一定失败**——各技能必须自带核心库副本，这是分发前提。

## 质量门检查什么

| 检查项 | 判定 |
|---|---|
| 核心库同步 | 各技能 `scripts/etk_core/` 与 `shared/etk_core/` 逐文件一致 |
| SKILL.md | frontmatter 合法、`name` 与目录名一致、`description` ≤ 1024 字符、正文 ≤ 500 行 |
| 版本一致 | `metadata.version` 等于 `scripts/*.py` 的 `__version__` |
| 触发用例 | `tests/trigger/<技能名>.json` 存在，正例 ≥ 20、反例 ≥ 10 |
| Python 兼容 | 运行时代码通过 Python 3.10 语法解析 |
| 依赖约束 | 运行时代码只 import 标准库 |
| 演示数据 | 各技能 `assets/demo.svd` 与 `embedded-register-lookup` 的副本一致 |
| 安全约束 | 运行时代码不得调用 `eval` / `exec` / `compile` |

## 新增一个技能

1. 建 `skills/<技能名>/`，目录名必须匹配 `^[a-z0-9]+(-[a-z0-9]+)*$`。
2. `SKILL.md` 的 frontmatter 包含 `name`、`description`、`license`、`compatibility`、
   `metadata.author`、`metadata.version`；正文控制在 500 行以内，细节放 `references/`。
   `description` 前半段写**用户会说的症状句**（中文优先），后半段写英文触发词与「不用于」边界。
3. `scripts/` 放入口脚本，写 `__version__`，并与 `metadata.version` 保持一致。
4. 需要共用 SVD 解析时，运行 `python tools/sync_core.py` 生成 `scripts/etk_core/` 副本，不要手写。
5. `tests/trigger/<技能名>.json` 补正例 ≥ 20、反例 ≥ 10。
6. 在 `README.md` 技能表与 `docs/skills/` 补充说明，在 `.claude-plugin/plugin.json` 与
   `marketplace.json` 更新技能清单。
7. `CHANGELOG.md` 记一条。

## 提交信息

沿用仓库现有风格：`类型: 中文说明`，类型取 `feat` / `fix` / `docs` / `chore` / `refactor` / `test`。

说明部分写**改了什么、为什么**，涉及数值或评测的写清前后对比，例如：

```
fix: timing-calc 输出在 GBK 控制台因 µ 字符崩溃（stdout 统一 UTF-8）
feat: 覆盖面收口——flash 补 QSPI/XIP 坑、comm 树补物理层根因，评测 +2（232 例）
```

## 不要做的事

- 引入第三方运行时依赖，或把任何逻辑改为联网 / 调用外部 API。
- 在运行时代码里 `eval` / `exec` / 执行被检查的用户代码。
- 提交厂商 SVD 文件、SDK 源码或评测原始转录（`.gitignore` 已忽略 `*.svd` 与 `benchmarks/_trig_*`）。
- 只改文档数字不改实现，或只改实现不更新 `CHANGELOG.md` / `README.md`。

## 报告问题

用 issue 模板提交，寄存器类问题请附：芯片型号、SVD 来源（厂商包版本）、完整命令、实际输出与期望输出。
手册截图或对应页号能显著加快核对。
