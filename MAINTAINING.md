# 维护手册

这份文档是这个仓库的说明书和履历：它是什么、为什么长成这样、以后怎么改、改的时候别踩哪些坑。
要动这个仓库，先读这里；看完还不够，再看 `README.md`（给用户）和 `CONTRIBUTING.md`（给贡献者）。

---

## 一、这个仓库是什么

**一句话**：给 AI 编程助手用的嵌入式技能包，15 个技能，离线运行，零第三方运行时依赖。

**它不是**：开发仓库、版本管理仓库、备份仓库。它是**分发渠道**——clone 下来的人默认拿到的是
能直接装、直接跑的成品。所以任何推送到 `main` 都等于对外发布，没有"先传上去回头再改"这一说。

### 收什么，不收什么

| 收 | 不收 |
|---|---|
| 嵌入式相关的技能 | 通用工具、教学/毕设类 |
| 自己开发（或授权明确）的 | 第三方项目（需要用就去原仓库装） |
| 已经实际发布过的成品 | 本地做完但没人用过的东西 |

### 现在有什么

| 分组 | 数量 | 技能 |
|---|---|---|
| 设计与选型 | 5 | 寄存器查询、时序计算、外设巡检、元器件避坑、原理图识别 |
| 编码与审查 | 5 | 代码生成、驱动模板、C/C++ 审查（27 条规则）、寄存器写入审计、PCB 自查 |
| 调试与升级 | 3 | 故障诊断（11 棵树 69 节点）、OTA 防砖、FPGA 仿真 |
| 测试与调参 | 2 | 出厂测试方案、电机 PID 调参 |

规模：211 个文件 / 2.17 MB；14 个技能零第三方依赖，`schematic-reader` 的可选依赖 `pymupdf`
缺失时只提示不静默安装。

### 和本地开发副本的关系

```
本地开发副本（不在本仓库）  ──人工判断──►  本仓库 main  ──打包──►  任何分发渠道
        半成品/实验                                  ↑
                                                  tag + Release
```

中间那一步是人判断：这个技能现在算不算"发布程度"。**没有自动同步**，也不该有。

---

## 二、履历

所有 tag 都落在 2026-11-25 到 2026-11-26 两天内——此前这个仓库长期没人管，用两天集中收拾出来的。

| 版本 | 日期 | 做了什么 |
|---|---|---|
| v1.0.0 | 11-25 | 清理起点：作者名统一 `fangcun`，删掉 30 个开发期 release 与 tag，Python 下限提到 3.10 |
| v1.1.0 – v1.3.0 | 11-25 | 修 README 里照抄必失败的命令、清 `.gitignore` 的 GBK 编码、CI 从 `ubuntu-latest` 迁走 |
| v1.4.0 | 11-25 | **收录标准定死**：只收已发布的自研嵌入式技能，25 个收敛为 15 个 |
| v1.4.1 | 11-25 | 修 `--html` 崩溃、质量门只扫 `scripts/` 的漏洞、文档补到 15 页；`filter-branch` 重写历史清掉第三方技能，`.git` 5.4MB → 1.7MB |
| v1.5.0 | 11-26 | 6 个落后技能回灌、README 按读者视角重排、发布门禁落地 |
| （未发版） | 11-26 | 社交预览图、`requirements-dev.txt` 补 Pillow、**移除门禁里所有外部平台版本比对** |

### 三个转折，值得记住原因

**一、判定依据换了四次才对。** 决定"哪些技能能进仓库"时，先后用过：本机安装目录（混进 12 个
第三方技能）→ 人工回想清单（漏了一大半）→ 扫开发源（数量对了但没查发布状态）→ 发布台账
（正确）。教训：判定依据必须是能查证的记录，不能是记忆或目录结构。

**二、GitHub 页面和仓库内容是两套东西。** v1.5.0 的包没问题，但仓库首页的 About 还写着
"五个技能 / 12 棵树 77 节点"，四个 Release 的说明都只有一行 `Full Changelog`。
改仓库文件不等于改 GitHub 页面——后者要靠 API 或网页单独改。

**三、门禁不能拿外部状态当判据。** 曾经把"各平台已发布版本"写进白名单并让发版门禁依赖它，
结果是 GitHub 的发版被别处的进度绑死：3 个技能没上过平台，`main` 就永远发不了版。
现在这条已彻底删掉——**仓库源码状态就是唯一判据**。

---

## 三、目录结构

```
README.md                给用户看的：这是什么、怎么装、怎么用
CONTRIBUTING.md          给贡献者看的：收录前提、质量门、提交流程
CHANGELOG.md             仓库层面变更记录（对外发布视角）
MAINTAINING.md           本文件，给维护者看
LICENSE                  MIT
requirements-dev.txt     仅开发用：pytest + Pillow（Pillow 只为生成社交预览图）
skills/<技能名>/          15 个技能，每个一个目录
  SKILL.md               必需。frontmatter + 给 Agent 读的指令
  README_安装说明.md      可选。给人读的介绍（商品页文案）
  scripts/               入口脚本；带 etk_core 副本的技能会有 scripts/etk_core/
  references/            细则、规则表、检查清单
  assets/                数据文件（SVD 演示数据、阈值表、驱动模板）
  examples/              可直接跑的示例
  tests/                 技能自带测试
  requirements.txt       可选。有第三方依赖时才建
shared/etk_core/         共享核心源码（唯一来源，改完跑 sync_core.py 同步到各技能）
tools/                   检查工具与构建脚本
tests/                   仓库级测试、夹具、触发评测用例
benchmarks/              实测记录与基准数据
docs/skills/             每个技能一页详细说明
release/published.json   发布白名单（哪些技能允许出现在这里）
.claude-plugin/          Claude Code 插件与市场清单
.github/                 CI、release workflow、issue/PR 模板、社交预览图
```

---

## 四、六条硬规则

1. **仓库是唯一真源。** 往外分发都从本仓库 `git archive` 打包，不要从本地开发副本打包。
   两份代码一分叉，谁也说不清别人装的是哪份。

2. **没实际发布过的不进来。** 本地跑得再顺也不行——用户拿到的是没人验证过的半成品，
   出问题无法回溯。

3. **改了技能内容，版本号必须变。** 否则 zip 名和内容对不上，回滚无从下手。
   `check_release.py` 会对比上个 tag，改了没升版本直接失败。

4. **一个版本号，三处一致。** `SKILL.md` 的 `metadata.version` = 脚本 `__version__` =
   `release/published.json` 的 `version`。只看仓库内部，不比对任何外部服务。

5. **只收嵌入式、只收自研。** 第三方技能需要用就去原仓库装，不在这里二次分发。

6. **不联网、不 `eval`/`exec`/执行用户代码。** 技能必须离线可用，质量门会拦。

### 版本号怎么升

| 版本 | 位置 | 什么时候动 |
|---|---|---|
| 仓库聚合版本 | `.claude-plugin/plugin.json` | 增删技能、改流程 → minor；纯修文档/脚本 → patch |
| 技能版本 | `SKILL.md` 的 `metadata.version` + 脚本 `__version__` | 行为变化 → minor；纯 bugfix / 文案 → patch |

---

## 五、操作手册

### 5.1 改一个已有技能

```bash
# 1. 在开发副本里改，改完同步到 skills/<技能名>/
# 2. 升版本：SKILL.md 的 metadata.version + 脚本 __version__ 一起改
# 3. 更新文档三处：docs/skills/<技能名>.md、README.md 技能表、CHANGELOG.md
# 4. 同步白名单：release/published.json 里该条目的 version
# 5. 体检
python tools/check_repo.py
python tools/check_release.py
# 6. 提交推送
git add -A && git commit -m "fix: <技能名> 1.x.y——<一句话>"
git push origin main
```

### 5.2 新增技能

1. 先在开发副本把技能做完，自己实际用一轮。
2. `release/published.json` 加一条：`version` 与 `SKILL.md` 一致，`releasedAt` 写首次发布日期。
3. 技能目录放进 `skills/`，`SKILL.md` 用标准 frontmatter（`name` / `description` / `license` /
   `compatibility` / `metadata.author` / `metadata.version`）。
4. 补 `docs/skills/<技能名>.md`，README 技能表加一行。
5. `CHANGELOG.md` 记一条；`plugin.json` 与 `marketplace.json` 升 minor、更新描述。
6. 跑 `check_release.py`，通过后打 tag。

漏第 2 步会被质量门拦住：`skills/` 下有目录但白名单没登记，报"未登记"。

`SKILL.md` 的硬要求：目录名 = `name`，匹配 `^[a-z0-9]+(-[a-z0-9]+)*$`；`description` ≤1024 字符
（超 900 会警告）；正文 ≤500 行，细则放 `references/`。

### 5.3 退役技能

1. 从任何已分发的渠道撤下。
2. `release/published.json` 删条目，`skills/` 删目录，README 与 `docs/skills/` 删对应项。
3. `CHANGELOG.md` 写明退役原因与替代方案。
4. 历史 tag 与 Release 不动——已经发出去的包不能收回，删了反而让人以为从没存在过。

### 5.4 只改文档

`docs/`、`README.md`、`CONTRIBUTING.md`、`MAINTAINING.md`、`CHANGELOG.md`、`.github/`、`tools/`、
`release/`、`requirements-dev.txt` 这类改动不改变用户拿到的技能内容，**可以直接推 `main`，不必打 tag**。

`skills/` 下任何一个字节变了，就必须走完整流程。

### 5.5 发版

```bash
# 1. 确认聚合版本已升、CHANGELOG 有对应段落
# 2. 体检（不带任何豁免参数）
python tools/check_release.py
# 3. 打 tag 并推送，workflow 会自动打包出 16 个附件（整包 + 15 单包）
git tag -a v1.6.0 -m "v1.6.0"
git push origin v1.6.0
```

`release.yml` 会校验：tag 版本必须等于 `plugin.json` 版本，`CHANGELOG.md` 必须有 `## [该版本]`
段，否则直接失败、不出 Release。

### 5.6 往外分发

```bash
git archive --format=zip --prefix=embedded-toolkit/ -o /tmp/etk.zip HEAD
```

原则是**从仓库打包，不从开发副本打包**。开发副本随时会改，仓库这份有 tag、有 CHANGELOG、
有 Release 附件——从开发副本打包，等于把一段没有版本号的历史发给别人。

### 5.7 改共享核心库

`shared/etk_core/` 是唯一来源，`skills/*/scripts/etk_core/` 是副本，不能手改。

```bash
# 改 shared/etk_core/*.py
python tools/sync_core.py          # 同步到各技能副本
python tools/sync_core.py --check  # 只校验一致性
```

改核心库会影响所有带副本的技能，每个受影响技能的版本都要升。

---

## 六、三道闸

| 闸 | 何时跑 | 查什么 | 失败后果 |
|---|---|---|---|
| `tools/check_repo.py` | 每次提交、CI | 核心库同步、SKILL.md 规范、Python 3.10 语法、仅标准库、不 eval、白名单一致、演示数据一致 | 阻断合并与发版 |
| `tools/check_release.py` | 打 tag 前 | 上面全部 + pytest + 版本递增 + 索引卫生 + 隐私 + 文档页齐全 + plugin.json 版本在 CHANGELOG 有段 + 打包预演 | 阻断发版 |
| `.github/workflows/release.yml` | push tag | tag 版本 = `plugin.json` 版本；CHANGELOG 有该版本段 | 不出 Release |

CI 矩阵：`ubuntu-latest` / `windows-latest` / `macos-latest` × Python 3.10 / 3.12 / 3.13，共 9 个 job。
本地与 CI 跑的是同一套参数，没有"CI 豁免"这种东西。

**这些检查只看仓库自己的状态，不查任何外部服务。**

---

## 七、踩过的坑

每一条都是真发生过的，不是假想。

### 内容与文档

| 现象 | 原因 | 现在怎么防 |
|---|---|---|
| README 里三条命令照抄全失败 | 路径写错、参数名写错（`--mode fast` 实为 `--bus fast`）、枚举值不存在 | 文档里的命令必须实跑一遍再写进去 |
| 审查器写"28 条规则"，实际 27 条 | 表格表头被算进条数，四处口径只改了三处 | 改数字时全仓 `grep` 一遍，`plugin.json`/`marketplace.json` 也算 |
| 手写的示例输出是假的 | 编了 `UESM` 位域，实跑发现 demo 里是 `RE/TE/RXNEIE` | 示例输出必须从实跑结果里复制 |
| About 描述写着"五个技能"而仓库有 15 个 | 改仓库文件不改 GitHub 页面，两套东西 | 见第八节检查清单 |

### 门禁与流程

| 现象 | 原因 | 现在怎么防 |
|---|---|---|
| "改了内容没升版本"检查完全失效 | Windows 下 `os.path.join` 生成反斜杠，`git show tag:skills\x\SKILL.md` 返回 128，旧版本恒为 `None` | 路径显式用正斜杠；这条用变异测试验过（改文件→报错，还原→消失） |
| 未提交的工作树改动漏检 | `changed_skills` 只看 `git diff since..HEAD` | 改成 `git diff since`（含工作树）+ `git status --porcelain`（含未跟踪） |
| 质量门漏扫 5 个入口脚本 | 只扫 `skills/*/scripts/*.py`，而 `reviewer.py`、`main.py` 在技能根目录 | 改为遍历技能内全部 `.py`，覆盖 25 → 31 个文件 |
| 发版被平台进度绑死 | 白名单里记录各平台已发布版本，门禁依赖它 | 已删除。门禁只看仓库自身状态 |

### 浏览器操作

| 现象 | 原因 | 现在怎么防 |
|---|---|---|
| 点不到 GitHub 的社交预览上传按钮 | 下拉菜单被视口底边裁掉，坐标点不中 | 键盘 `Space` 展开 + `Tab`/`Enter` 导航 |
| 系统文件对话框截不到、点不到 | 它是 OS 级窗口，网页截图看不到 | `EnumWindows` 找 `#32770` → `SetWindowTextW` 写入路径 → `WM_LBUTTONDOWN/UP` 打按钮中心。注意 `BM_CLICK` 和 `WM_COMMAND` 无效 |
| Chrome 打不开 GitHub Settings | 只登录了 Edge，Chrome 未登录（Settings 返回 404） | 先验证登录态；未登录会 404 而不是跳登录页 |

### 字体与图片

| 现象 | 原因 |
|---|---|
| 生成图上中文全是方块 | Consolas 没有汉字。中文行必须用中文字体单独绘制 |
| 对勾 `✓` 显示成方块 | 微软雅黑不含 `U+2713`，得用 `draw.line` 手绘 |

---

## 八、检查清单

### 改完技能内容

- [ ] `SKILL.md` 与脚本 `__version__` 同步升版本
- [ ] `release/published.json` 的 `version` 已同步
- [ ] `docs/skills/<技能名>.md` 版本号已同步
- [ ] `README.md` 技能表的版本列已同步
- [ ] `CHANGELOG.md` 记了一条
- [ ] `python tools/check_repo.py` 通过
- [ ] `python -m pytest -q` 全绿
- [ ] `python tools/check_release.py` 通过

### 发版前

- [ ] `plugin.json` 聚合版本已升
- [ ] `CHANGELOG.md` 有 `## [新版本]` 段
- [ ] `check_release.py` **不带任何参数**通过
- [ ] 改动过 `shared/etk_core` 的话，`sync_core.py --check` 一致

### 发版后

- [ ] Release 附件数 = 技能数 + 1（整包）
- [ ] 下载整包解压，随便挑一个技能跑 `--help` 和一条真实命令
- [ ] **补写 Release 说明**。workflow 用 `--generate-notes` 生成的是提交标题列表，
      一屏字读不出这版改了什么。按 `CHANGELOG.md` 对应段落重写成「装到的是什么 + 修了什么」，
      用 `PATCH /repos/{owner}/{repo}/releases/{id}` 更新 `body`
- [ ] 动了技能数量或定位文案的话，重跑 `tools/make_social_preview.py` 并重新上传社交预览图
- [ ] 记一笔到项目记忆：版本、要点、遗留项

### GitHub 页面侧（仓库文件之外，需要单独改）

| 项 | 怎么改 | 能否自动化 |
|---|---|---|
| About 描述 | `PATCH /repos/{owner}/{repo}` 的 `description` | 可（REST） |
| Topics | `PUT /repos/{owner}/{repo}/topics` | 可（REST） |
| Release 说明 | `PATCH /repos/{owner}/{repo}/releases/{id}` 的 `body` | 可（REST） |
| 社交预览图 | Settings → Social preview → Edit → Upload | **不可，只能网页手动** |

社交预览图约束：1280×640、≤1 MB、列表页缩略约 400px 宽所以主标题不小于 72px、图上命令输出
必须实跑、无版本号之类会过期的数字。

---

## 九、定期体检

**每月一次**（技能内容与下游脱节最容易在这里暴露）：

```bash
git status                      # 工作树干净吗
python tools/check_repo.py      # 质量门
python tools/check_release.py --skip-tests   # 结构体检
```

再加两项人工核对——机器查不出来的：

1. 抽一个技能，按 `SKILL.md` 里写的命令实际跑一遍，看输出是否还和文档一致。
2. 打开 GitHub 仓库首页与 Releases 页，看描述、Topics、最新 Release 说明是否还准确。

**每次改技能后**：跑完整 `check_release.py`。

---

## 十、已知问题

| 问题 | 现状 | 该怎么办 |
|---|---|---|
| `marketplace.json` 没有 `version` 字段 | Claude Code 市场格式只要求 `plugin.json` 有版本 | 保持现状，别为对齐而加 |
| 技能自带 `CHANGELOG` 只有 3 个技能有 | 那是技能内部细粒度记录（含平台驳回原因等技术细节），与根 `CHANGELOG` 不同层 | 有则维护，没有不必新建 |
| `README_安装说明.md` 只有 9 个技能有 | 面向人的商品页文案，非必需 | 同上，有则维护 |
| `schematic-reader` 可选依赖 `pymupdf` | 缺依赖时只提示，不静默安装 | 保持，不要把可选依赖变成必需 |

---

## 十一、命令速查

```bash
# 体检
python tools/check_repo.py                   # 仓库质量门
python tools/check_release.py                # 发版前全量体检
python tools/check_release.py --skip-tests   # 只查结构
python tools/check_release.py --since v1.4.1 # 指定比对基线
python -m pytest -q                          # 全部测试

# 核心库
python tools/sync_core.py
python tools/sync_core.py --check

# 构建辅助
python tools/make_social_preview.py          # 生成社交预览图（需要 Pillow）
python tools/knowledge_bench.py              # 触发评测

# 本地验证某个技能能装
npx --yes skills add . --list                # 应列出 15 个

# 打包往外发
git archive --format=zip --prefix=embedded-toolkit/ -o /tmp/etk.zip HEAD

# 发版
git tag -a v1.6.0 -m "v1.6.0" && git push origin v1.6.0
```
