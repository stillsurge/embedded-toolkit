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
python tools/check_release.py  # 只改了 skills/ 或准备发版时必跑
```

CI 在 ubuntu / windows / macOS × Python 3.10 / 3.12 / 3.13 上跑前三条，任一失败即阻断。

**改动 `shared/etk_core` 却忘了 `sync_core.py`，质量门一定失败**——各技能必须自带核心库副本，这是分发前提。

## 收录前提

本仓库是**公开发布渠道**，不是开发仓库。技能内容在本地开发副本里迭代，达到发布标准才进这里；
推送即对外发布，包括分支和 PR。入库前该技能必须满足：

1. **已在平台上线**（WorkBuddy / SkillHub / ClawHub 任一），状态为已发布或 live，并在
   `release/published.json` 登记。本地做完但没上过平台的，先别进这里——用户 clone 下来会拿到
   平台查不到的版本，出问题无法回溯。
2. **自研或授权明确**。第三方项目不收；确需收录的必须保留原 LICENSE 与原作者署名。
3. **只收嵌入式相关**。通用工具、教学/毕设类技能不属于本仓库范围。
4. **版本可追溯**：`SKILL.md` 的 `metadata.version` = 脚本 `__version__` =
   `release/published.json` 的 `version` = 平台版本。

`release/published.json` 是白名单，也是唯一的判定依据。`state` 只有四种：

| state | 含义 | 能不能发版 |
|---|---|---|
| `synced` | 仓库与平台版本一致 | 可以 |
| `ahead` | 仓库比平台新，改动还没上平台 | 要写 `plan` 并 `--ack-pending` |
| `behind` | 仓库比平台旧，用户下到的是旧版本 | 发版前必须清零 |
| `unverified` | 平台状态待核实 | 要写 `plan`，发版前应查清 |

新增技能时漏登记，`check_repo.py` 会直接报「未登记」并失败。完整流程、版本号规则与发版命令见
[docs/release-process.md](docs/release-process.md)。

## 质量门检查什么

`python tools/check_repo.py` 退出码非 0 即不通过。

| 检查项 | 判定 |
|---|---|
| 发布白名单 | `skills/` 下每个目录都在 `release/published.json` 登记，反向也一致；非 `synced` 必须写 `plan`；`synced` 的平台版本必须等于仓库版本 |
| 核心库同步 | 带 `scripts/etk_core/` 的技能，副本与 `shared/etk_core/` 逐文件一致 |
| SKILL.md 存在 | `skills/<技能名>/SKILL.md` 必须存在 |
| frontmatter | 可解析；`name` 匹配 `^[a-z0-9]+(-[a-z0-9]+)*$`、≤64、等于目录名；`description` 非空且 ≤1024；`compatibility` ≤500；正文 ≤500 行 |
| 版本一致 | 脚本里写了 `__version__`，就必须等于 `metadata.version`；脚本没写版本号不阻断 |
| 触发用例 | **可选**。`tests/trigger/<技能名>.json` 存在时校验正例 ≥20、反例 ≥10；缺失不阻断 |
| Python 兼容 | 技能内全部 `.py`（不含 `tests/`）通过 Python 3.10 语法解析 |
| 依赖约束 | 只允许标准库、技能内本地模块，或在技能根 `requirements.txt` 声明；支持 `包名  # import: 模块名` 的映射写法 |
| 演示数据 | 存在 `assets/demo.svd` 的技能，其副本必须与 `embedded-register-lookup` 的一致 |
| 安全约束 | 运行时代码不得调用 `eval` / `exec` / `compile` |

另有一类**警告**（不阻断退出码，但建议处理）：`description` 超过 900 字符时提示。
上限 1024 是多个 Agent 的硬限制，ZCode 超限会**静默丢弃整个技能**——不报错、不截断，
用户只看到「装了没反应」。留出余量再加触发词。

## 新增一个技能

前提：**先在平台发布成功**。没上线的技能不进这个仓库，这是第一道门。

1. 在 `release/published.json` 加一条，`state: "synced"`，`platform` 写各平台实际版本。
   漏了这步质量门会报「未登记」。
2. 建 `skills/<技能名>/`，目录名必须匹配 `^[a-z0-9]+(-[a-z0-9]+)*$`，且与 `name` 完全一致。
3. `SKILL.md` 的 frontmatter 包含 `name`、`description`、`license`、`compatibility`、
   `metadata.author`、`metadata.version`；正文 ≤500 行，细节放 `references/`。
   `description` 前半段写**用户会说的症状句**（中文优先），后半段写英文触发词与「不用于」边界。
4. 入口脚本放 `scripts/`（或技能根目录也可，质量门两处都扫）；写 `__version__` 的话
   必须与 `metadata.version` 一致。
5. 需要共用 SVD 解析时，运行 `python tools/sync_core.py` 生成 `scripts/etk_core/` 副本，不要手写。
6. 有触发用例就放 `tests/trigger/<技能名>.json`（正例 ≥20、反例 ≥10）；没有也能入库。
7. 写 `docs/skills/<技能名>.md`（作用 / 版本 / 核心内容 / 命令 / 实测记录 / 边界），
   `README.md` 技能表补一行，`.claude-plugin/plugin.json` 与 `marketplace.json` 更新描述与
   tags，聚合版本升 minor，`CHANGELOG.md` 记一条。
8. 需要第三方包时，在技能根建 `requirements.txt`，用 `包名  # import: 模块名` 标注
   import 名不一致的情况（如 `PyMuPDF  # import: fitz`）。
9. `python tools/check_release.py` 通过后，打 tag 发版。细节见
   [docs/release-process.md](docs/release-process.md)。

## README 写什么、不写什么

README 的读者是**来找技能用的人**，不是维护者。一条信息该不该出现，看它能不能帮读者决定
"要不要装、怎么装、装了怎么用、值不值得信"。

**要写**：

- 解决什么问题——用症状描述（"位名编得像真的、超位宽的值、没开时钟就写"），不用形容词
- 每个技能干什么，一句话说到能判断用不用得上
- 怎么装：按 Agent 分，命令可直接复制
- 装完怎么跑：命令必须实测过；贴输出就必须是真实输出，不能手写
- 适用范围与不覆盖的部分：哪些芯片 / 工具链 / 写法行，哪些明确不做
- 约束条件：离线、零依赖、只读、不执行用户代码

**不要写**：

- 仓库自身状态：是不是发布渠道、技能上没上过线、收录边界、版本号怎么管
- 内部流程：发布体检、质量门、白名单、台账、tag 策略
- 自我评价："全部自研"、"成品"、"高质量"、"业界领先"这类，读者不看这个
- 没有信息量的规划："按阶段门推进"+"两个名词"，等于没说
- 未实测的示例输出

前两类放 `CONTRIBUTING.md` 与 `docs/release-process.md`，那是给维护者看的。README 里最多留一行链接。

## 提交信息

沿用仓库现有风格：`类型: 中文说明`，类型取 `feat` / `fix` / `docs` / `chore` / `refactor` / `test`。

说明部分写**改了什么、为什么**，涉及数值或评测的写清前后对比，例如：

```
fix: timing-calc 输出在 GBK 控制台因 µ 字符崩溃（stdout 统一 UTF-8）
feat: 覆盖面收口——flash 补 QSPI/XIP 坑、comm 树补物理层根因，评测 +2（232 例）
```

## 不要做的事

- **把没上过平台的技能推进来**，哪怕是分支或草稿 PR。这个仓库对外就是发布，推上去就等于发布了。
- 改技能内容却不升版本号。zip 名与内容对不上，用户反馈问题无法定位，也没法回滚。
- 引入第三方运行时依赖，或把任何逻辑改为联网 / 调用外部 API。
- 在运行时代码里 `eval` / `exec` / 执行被检查的用户代码。
- 提交厂商 SVD 文件、SDK 源码或评测原始转录（`.gitignore` 已忽略 `*.svd` 与 `benchmarks/_trig_*`）。
- 提交本机绝对路径、用户名或令牌。公开仓库泄露一次就会被缓存与 fork，删不干净。
- 只改文档数字不改实现，或只改实现不更新 `CHANGELOG.md` / `README.md`。

## 报告问题

用 issue 模板提交，寄存器类问题请附：芯片型号、SVD 来源（厂商包版本）、完整命令、实际输出与期望输出。
手册截图或对应页号能显著加快核对。
