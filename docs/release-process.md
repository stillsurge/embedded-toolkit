# 发布流程

本仓库是**发布渠道**，不是版本管理仓库。clone 下来的人默认拿到的是能直接装、直接跑的
成品；因此任何推送都等于对外发布，没有"先传上去回头再改"这一说。

一句话规则：**技能内容在本地开发副本里迭代，达到发布标准才进本仓库。**

## 1. 三个区

| 区域 | 位置 | 允许放什么 | 谁能看到 |
|---|---|---|---|
| 开发区 | 本地开发副本（不在本仓库） | 半成品、实验分支、临时脚本 | 只有你 |
| 发布区 | 本仓库 `main` + tag + Release | 已发布、版本可追溯的成品 | 所有人 |
| 归档区 | 本地历史批次包 | 每次发布出去的原始 zip | 内部 |

开发区到发布区**没有自动同步**。中间那一步是人判断：这个技能现在算不算"发布程度"。

**仓库是唯一真源。** 往任何渠道分发（自己的平台、第三方市场、直接发给别人）都从本仓库
打包，不要在开发区另改一份再发出去——那样两个地方的代码会分叉，谁也说不清用户装的是哪份。

## 2. 什么算"到发布程度"

四条全部满足才算。缺一条就继续留在开发区。

| 编号 | 条件 | 怎么证明 |
|---|---|---|
| R1 | 已发布过 | 通得过真实使用，发过一次；在 `release/published.json` 登记 |
| R2 | 已通过质量门与测试 | `python tools/check_release.py` 退出码 0 |
| R3 | 版本可追溯 | `SKILL.md` 的 `metadata.version` = 脚本 `__version__` = `release/published.json` |
| R4 | 文档同步 | README 技能表、`docs/skills/<技能名>.md`、`CHANGELOG.md` 三处都写了 |

R1 是硬前提。本地做完、跑得很顺、但没发过的东西不能进仓库——用户拿到的是没人验证过的
半成品，出了问题也没法回溯。

R3 只比对仓库内部三处，不看外部任何地方。仓库里 `SKILL.md` 的版本就是唯一权威：
它和 `published.json` 不一致、或和脚本 `__version__` 不一致，质量门直接失败。

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
# 4. 同步白名单：release/published.json 里该条目的 version
# 5. 体检
python tools/check_repo.py
python tools/check_release.py
# 6. 提交并推送
git add -A && git commit -m "feat: <技能名> 1.x.y——<一句话>"
git push origin main
# 7. 发版（聚合版本变了才需要）
git tag -a v1.6.0 -m "v1.6.0"
git push origin v1.6.0
```

顺序不能颠倒：先升级本仓库这份，再打 tag，最后才往外分发。分发出去的包必须能对应到
某个 tag——否则收到包的人报问题，你没法定位他手上是哪一版。

### 4.1.1 往外分发时从仓库打包

要往任何地方发（自己的平台、第三方市场、单独发给别人），从本仓库打包，不要从开发区打包：

```bash
git archive --format=zip --prefix=embedded-toolkit/ -o /tmp/etk.zip HEAD
```

理由很直接：开发区那份随时会改，仓库这份有 tag、有 CHANGELOG、有 Release 附件。
从开发区打包，就等于把一段没有版本号的历史发给别人。

### 4.2 新增技能

1. **先在开发区把技能做完**，自己实际用一轮，确认能站住。
2. 在 `release/published.json` 加一条，`version` 与 `SKILL.md` 一致，`releasedAt` 写首次发布日期。
3. 把技能目录放进 `skills/`，`SKILL.md` 用标准 frontmatter（`name` / `description` /
   `license` / `compatibility` / `metadata`）。
4. 补 `docs/skills/<技能名>.md`，README 技能表加一行。
5. `CHANGELOG.md` 记一条，`plugin.json` 与 `marketplace.json` 升 minor 版本、更新描述。
6. 跑 `check_release.py`，通过后打 tag。

漏第 2 步会直接被质量门拦住：`skills/` 下有目录但白名单没登记，报"未登记"。

### 4.3 退役技能

1. 从任何已分发的渠道撤下。
2. `release/published.json` 删条目。
3. 删 `skills/<技能名>/` 与 `docs/skills/<技能名>.md`。
4. `CHANGELOG.md` 写清为什么退、替代品是什么。
5. 聚合版本升 minor（用户装的东西少了，属于破坏性变更）。

历史 tag 与 Release 不动——已经发出去的包不能收回，删了反而让人以为从没存在过。

## 5. 只改治理文件时

`docs/`、`README.md`、`CHANGELOG.md`、`.github/`、`tools/`、`release/`、
`requirements-dev.txt` 这类改动不改变用户拿到的技能内容，可以直接推 `main`，不必打 tag。
但如果动了 `skills/` 下任何一个字节，就必须按第 4 节走完整流程。

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
| 版本递增 | 相对上个 tag 有内容改动的技能，版本必须变 |
| 索引卫生 | 不得提交 `__pycache__` / `.pytest_cache` / `*.pyc` |
| 隐私 | 不得出现本机绝对路径、用户名、令牌（公开仓库泄露一次就是永久） |
| 文档 | 每个技能在 `docs/skills/` 有页 |
| 元数据 | `plugin.json` 的版本在 `CHANGELOG.md` 里有对应段落 |
| 体积 | `skills/` 打包后 ≤5 MB |

以上全部只看仓库自己的状态，不查任何外部服务的版本。CI 与本地跑的是同一套检查，参数一致。

## 7. 常见错法

| 错法 | 后果 |
|---|---|
| 边开发边推 `main` | 用户 clone 到半成品，没人验证过 |
| 改了内容不升版本 | zip 名与内容不符，回滚无从下手 |
| 先打 tag 再补 `published.json` | 发布记录与代码脱节，下次体检报版本不一致 |
| 白名单登记了但没真发过 | 谎报，R1 失效，整个门禁失去意义 |
| 从开发区打包往外发 | 同一版本两处代码分叉，收到的包对不上任何 tag |
| 用外部平台格式的 SKILL.md 覆盖仓库 | 扁平 `version`/`slug` 不符合 Agent Skills 标准，其他 Agent 装不上 |
| 把未发布技能"先传上去占位" | 就是本流程要杜绝的行为 |

## 8. 每次发版后

1. 核对 Release 附件数 = 技能数 + 1（整包），逐个确认体积正常。
2. 下载整包解压，随机挑一个技能跑 `--help` 与一条真实命令。
3. 记一笔到项目记忆：版本、变更要点、遗留项。
5. 如果这次动了技能数量或定位文案，重跑 `tools/make_social_preview.py` 并重新上传社交预览图（见 9.3）。

## 9. GitHub 页面上的东西，哪些能自动化

仓库里改完不等于 GitHub 上就对了。页面上的元数据是另一套，且自动化程度不一样：

| 项 | 怎么做 | 能否自动 |
|---|---|---|
| About 描述 | `PATCH /repos/{owner}/{repo}`，字段 `description` | 可（REST） |
| Topics | `PUT /repos/{owner}/{repo}/topics` | 可（REST） |
| Release 说明 | `PATCH /repos/{owner}/{repo}/releases/{id}`，字段 `body` | 可（REST） |
| 社交预览图 | Settings → Social preview → Edit → Upload | **不可，只能网页手动** |

### 9.1 About 描述与 topics

这两项在仓库首页最显眼，也最容易和工作树脱节。改完 `README` 里的技能数量，记得同步改：
描述里写死的「15 个技能」不会自己变。查当前值：

```bash
curl -s https://api.github.com/repos/stillsurge/embedded-toolkit | grep -E '"description"|"topics"'
```

### 9.2 Release 说明

`--generate-notes` 生成的是提交标题列表，可用性取决于提交信息质量。版本跨度大时，
按 `CHANGELOG.md` 的对应段落重写一遍，写清楚「装到的是什么」和「修了什么」。
只有一行 `Full Changelog` 等于没写——下载页的人看不出这版和上版差在哪。

### 9.3 社交预览图

GitHub 至今没有提供设置 social preview 的 API（截至 2026-11，REST 与 GraphQL 都没有，
社区从 2022 年提到现在仍未支持）。这一步只能在
`https://github.com/{owner}/{repo}/settings` 页面手动上传。

当前已设置（2026-11-26），`og:image` 指向 `repository-images.githubusercontent.com`。
换图时重复下面三步：改脚本 → 重跑 → 页面重新上传。

图由 `tools/make_social_preview.py` 生成，输出 1280×640 PNG。改完重跑即可：

```bash
python tools/make_social_preview.py    # 需要 Pillow，仅构建期使用
```

图上的约束，改脚本时别破坏：

- **尺寸 1280×640**（2:1）。列表页缩略显示约 400px 宽，所以主标题不小于 72px，
  正文不小于 18px，再小的信息等于没有。
- **命令输出必须是实跑结果**，不能手写示意。图里那行 `lookup.py lookup USART1.CR1 --demo`
  的输出是从真实执行结果里抄的——这套工具的核心卖点是「每条结论带出处」，图上写假的就自相矛盾。
- **两类字体坑**：Consolas 没有汉字，中文行会渲染成方块；微软雅黑不含 `U+2713`，
  对勾也得用 `draw.line` 手绘。

