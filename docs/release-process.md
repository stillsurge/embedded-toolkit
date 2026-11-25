# 发布流程

本仓库是**发布渠道**，不是版本管理仓库。clone 下来的人默认拿到的是能直接装、直接跑的
成品；因此任何推送都等于对外发布，没有"先传上去回头再改"这一说。

一句话规则：**技能内容在本地开发副本里迭代，达到发布标准才进本仓库。**

## 1. 三个区

| 区域 | 位置 | 允许放什么 | 谁能看到 |
|---|---|---|---|
| 开发区 | 本地开发副本（不在本仓库） | 半成品、实验分支、临时脚本 | 只有你 |
| 发布区 | 本仓库 `main` + tag + Release | 已上平台、版本可追溯的成品 | 所有人 |
| 归档区 | 平台发布台账 + 批次包 | 每次上传的原始 zip | 内部 |

开发区到发布区**没有自动同步**。中间那一步是人判断：这个技能现在算不算"发布程度"。

## 2. 什么算"到发布程度"

四条全部满足才算。缺一条就继续留在开发区。

| 编号 | 条件 | 怎么证明 |
|---|---|---|
| R1 | 已在平台上线 | [WorkBuddy / SkillHub / ClawHub] 任一有 live 记录，版本号可查 |
| R2 | 已通过质量门与测试 | `python tools/check_release.py` 退出码 0 |
| R3 | 版本可追溯 | `SKILL.md` 的 `metadata.version` = 脚本 `__version__` = `release/published.json` = 平台版本 |
| R4 | 文档同步 | README 技能表、`docs/skills/<技能名>.md`、`CHANGELOG.md` 三处都写了 |

R1 是硬前提。本地做完、跑得很顺、但没上过平台的技能，**不能进仓库**——用户下到的是
平台查不到的版本，出了问题没法回溯，也没法通过平台更新推给已安装的人。

R3 里"平台版本"允许两种情况：

- `synced`：完全一致，正常状态。
- `ahead`：仓库比平台新，说明改动还没上平台。**必须**在 `release/published.json` 的
  `plan` 里写清什么时候上，否则质量门直接失败。发版前还要 `--ack-pending` 显式确认。

`behind`（仓库比平台旧）是最糟的状态：用户在 GitHub 下到的是旧版本，问题修了但没人拿到。
一旦出现，下次发版前必须清零。

## 3. 版本号

两套版本号，各管各的：

| 版本 | 位置 | 什么时候动 |
|---|---|---|
| 仓库聚合版本 | `.claude-plugin/plugin.json` | 增删技能、改流程 → minor；纯修文档/脚本 → patch |
| 技能版本 | `SKILL.md` 的 `metadata.version` + 脚本 `__version__` | 技能行为变化 → minor；纯 bugfix → patch |

铁律：**技能内容有任何改动，版本号必须变。** 改了内容不改版本，用户拿到的 zip 文件名
和实际内容对不上，出问题无法定位，也没法回滚。`check_release.py` 会对比上一个 tag，
改了但没升版本直接失败。

## 4. 标准发布流程

### 4.1 升级已有技能

```bash
# 1. 在开发区改，改完同步到本仓库对应目录
# 2. 升版本（SKILL.md 的 metadata.version 与脚本 __version__ 一起改）
# 3. 更新文档：docs/skills/<技能名>.md、README 技能表、CHANGELOG.md
# 4. 同步平台状态：release/published.json 里该条目的 version 与 platform
# 5. 体检
python tools/check_repo.py
python tools/check_release.py
# 6. 提交并推送
git add -A && git commit -m "feat: <技能名> 1.x.y——<一句话>"
git push origin main
# 7. 发版（聚合版本变了才需要）
git tag -a v1.5.0 -m "v1.5.0"
git push origin v1.5.0
```

顺序不能颠倒：先上平台、再改 `published.json`、最后打 tag。反过来就是"仓库先于平台"，
又回到 `ahead` 状态。

### 4.1.1 平台发布之后必须回灌

平台上传成功不等于结束。上传用的是开发区那份代码，本仓库那份还是旧的——不回灌就会变成
`behind`：用户在 GitHub 下到的是带 bug 的旧版本，而平台上早就修好了。

每次平台发布后固定做三件事：

1. 把开发区该技能目录同步到 `skills/<技能名>/`（`SKILL.md` 保留本仓库的标准
   frontmatter 格式，不能直接覆盖成平台格式）。
2. `release/published.json` 里该条目：`version` 改成新版本，`platform` 各平台版本同步，
   `state` 改 `synced`，`plan` 清空。
3. `python tools/check_release.py --skip-tests` 确认没有残留 `behind`。

`behind` 一旦出现就在每次 CI 里被点名，直到回灌为止——这是刻意设计的噪音，避免它被忘掉。

### 4.2 新增技能

1. **先在开发区把技能做完**，打包上平台，拿到 live。
2. 在 `release/published.json` 加一条，`state: "synced"`，`platform` 写实际版本。
3. 把技能目录放进 `skills/`，`SKILL.md` 用标准 frontmatter（`name` / `description` /
   `license` / `compatibility` / `metadata`）。
4. 补 `docs/skills/<技能名>.md`，README 技能表加一行。
5. `CHANGELOG.md` 记一条，`plugin.json` 与 `marketplace.json` 升 minor 版本、更新描述。
6. 跑 `check_release.py`，通过后打 tag。

漏第 2 步会直接被质量门拦住：`skills/` 下有目录但白名单没登记，报"未登记"。

### 4.3 退役技能

1. 平台下架。
2. `release/published.json` 删条目。
3. 删 `skills/<技能名>/` 与 `docs/skills/<技能名>.md`。
4. `CHANGELOG.md` 写清为什么退、替代品是什么。
5. 聚合版本升 minor（用户装的东西少了，属于破坏性变更）。

历史 tag 与 Release 不动——已经发出去的包不能收回，删了反而让人以为从没存在过。

## 5. 只改治理文件时

`docs/`、`README.md`、`CHANGELOG.md`、`.github/`、`tools/`、`release/` 这类改动不改变
用户拿到的技能内容，可以直接推 `main`，不必打 tag。但如果动了 `skills/` 下任何一个字节，
就必须按第 4 节走完整流程。

## 6. 门禁矩阵

| 检查 | 何时跑 | 失败会怎样 |
|---|---|---|
| `tools/check_repo.py` | 每次提交、CI 三平台 × 三 Python | 阻断合并与发版 |
| `tools/check_release.py` | 打 tag 前手动 | 阻断发版 |
| `.github/workflows/release.yml` | push tag | tag 版本 ≠ `plugin.json` 版本、或 CHANGELOG 缺该版本段，直接失败，不出 Release |
| `.github/workflows/ci.yml` | push / PR | 质量门或测试失败即红 |

`check_release.py` 查的具体项：

| 项 | 判定 |
|---|---|
| 质量门 | `check_repo.py` 全绿 |
| 测试 | `pytest -q` 全绿 |
| 平台对齐 | 非 `synced` 的技能必须 `--ack-pending` 才放行 |
| 版本递增 | 相对上个 tag 有内容改动的技能，版本必须变 |
| 索引卫生 | 不得提交 `__pycache__` / `.pytest_cache` / `*.pyc` |
| 隐私 | 不得出现本机绝对路径、用户名、令牌（公开仓库泄露一次就是永久） |
| 文档 | 每个技能在 `docs/skills/` 有页 |
| 元数据 | `plugin.json` 的版本在 `CHANGELOG.md` 里有对应段落 |
| 体积 | `skills/` 打包后 ≤5 MB |

`release.yml` 里跑的是 `check_release.py --ack-pending`：确认动作发生在本地（打 tag 之前
你亲自看过待对齐清单），CI 负责的是把它记录下来并核对客观项。要绝对严格就把这个参数去掉，
代价是还有 `ahead` 项时完全发不了版。

## 7. 常见错法

| 错法 | 后果 |
|---|---|
| 边开发边推 `main` | 用户 clone 到半成品，平台上也查不到这个版本 |
| 改了内容不升版本 | zip 名与内容不符，回滚无从下手 |
| 先打 tag 再补 `published.json` | 发布记录与代码脱节，下次体检报 `behind` |
| 白名单登记了但平台没上 | `state` 写 `synced` 是谎报，R1 失效，整个门禁失去意义 |
| 用平台格式的 SKILL.md 直接覆盖仓库 | 平台格式（扁平 `version`/`slug`）不符合 Agent Skills 标准，其他 Agent 装不上 |
| 把未发布技能"先传上去占位" | 就是本流程要杜绝的行为 |

## 8. 每次发版后

1. 核对 Release 附件数 = 技能数 + 1（整包），逐个确认体积正常。
2. 下载整包解压，随机挑一个技能跑 `--help` 与一条真实命令。
3. 把发布结果写回平台台账（版本、时间、附件名）。
4. 记一笔到项目记忆：版本、变更要点、遗留项。
