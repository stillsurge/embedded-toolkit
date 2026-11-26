# 变更记录

版本号在两处维护：`.claude-plugin/plugin.json` 是插件聚合版本，各技能 `SKILL.md` 的
`metadata.version` 是技能独立版本。质量门 `tools/check_repo.py` 会校验技能版本与脚本
`__version__` 一致。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### 新增

- **仓库社交预览图**：`tools/make_social_preview.py` 生成 1280×640 的 `.github/social-preview.png`，
  技能数量或定位文案变了重跑即可。图上的命令输出取自 `lookup.py lookup USART1.CR1 --demo` 的
  真实输出，不是手写的示意。
  脚本依赖 Pillow，属构建辅助，不参与运行时，也不在质量门的模块白名单扫描范围内（只扫
  `shared/` 与 `skills/`）。

### 修复

1.5.0 发布后发现的三处 GitHub 侧问题，都属于"页面上的话与实际不符"，不影响包内容。

### 修复

- **仓库 About 描述还停在五个技能**：GitHub 仓库首页标题旁那句写着「五个技能 / 排障决策树 12 棵 / 77 节点」，
  而仓库早已是 15 个技能、11 棵 69 节点。已改为 15 个技能的准确描述，topics 从 11 个补到 20 个
  （补 misra、code-review、debugging、pid-control、ota、pcb、fpga、schematic、claude-code、ai-agent）。
- **Release 说明只有一行 Full Changelog**：v1.2.0 / v1.4.0 / v1.4.1 / v1.5.0 四个版本的说明都是
  自动生成的一行链接，下载页的人看不出这版改了什么。四个版本都按 CHANGELOG 补成可读的说明。
- **插件市场描述与实际不符**：`.claude-plugin/plugin.json` 与 `marketplace.json` 里写着
  「均已在 WorkBuddy / SkillHub / ClawHub 发布上线」「故障诊断树 12 棵」。前者不实（3 个技能
  只在 WorkBuddy 市场），后者过期（11 棵）。改为只讲能力、不讲发布渠道。
- `docs/skills/embedded-fpga-sim.md` 的边界写着「用 `embedded-fpga-trees`」，但该技能不在本仓库，
  读者去找会扑空。改为「不在本仓库范围」。

### 已知问题

三个技能的 SKILL.md 里还引用着不在本仓库的技能，暂未修改——改 `SKILL.md` 属于技能内容变更，
按流程必须升版本，而它们当前与已发布版本一致，为一句文案制造版本漂移不划算。等它们下次自然
升版时一并改：

- `hw-pcb-review` 引用 `hw-review-checklist`（原理图审查，已退场不单独发布）
- `embedded-production-test` 引用 `embedded-unit-test-gen`（未发布）
- `embedded-debug-trees` 的 `trees.py` 注释提到 `embedded-fpga-trees`（未发布）

## [1.5.0] - 2026-11-26

把「什么算发布、什么时候能推上来」从口头约定变成可执行的门禁。此前的状态是：仓库里既有
未上平台的改动（`ahead`），也有落后平台的旧版本（`behind`），但没有任何机制能发现。

### 发布流程

- 新增 `docs/release-process.md`：三区模型（开发区 / 发布区 / 归档区）、四条发布准入
  条件（R1 已上平台 / R2 过门禁 / R3 版本可追溯 / R4 文档同步）、版本号规则、升级与新增与
  退役三条操作路径、门禁矩阵、七种常见错法。
- 新增 `release/published.json`：发布白名单，也是「能不能进这个仓库」的唯一判定依据。
  每条记录仓库版本、各平台已发布版本、`state`（`synced` / `ahead` / `behind` / `unverified`）
  与 `plan`。非 `synced` 必须写清待办，否则质量门失败。
- `tools/check_repo.py` 新增 `check_published()`：技能目录与白名单双向比对，未登记的报
  「新技能必须先上平台发布、再登记入库」，版本三处（白名单 / `SKILL.md` / 平台）必须一致。
  另在通过时打印一份未对齐清单，让问题在每次 CI 都被看见。
- 新增 `tools/check_release.py`：发布前体检，查质量门、测试、平台对齐、版本递增、索引卫生
  （禁止提交 `__pycache__`/`*.pyc`）、隐私泄露（本机绝对路径 / 用户名 / 令牌）、文档页齐全、
  `plugin.json` 版本在 CHANGELOG 有对应段、打包体积与文件数预演。
- `release.yml` 新增发版守卫：tag 版本必须等于 `plugin.json` 版本、`CHANGELOG.md` 必须有该
  版本段，否则直接失败、不出 Release。并改为 `fetch-depth: 0` 以支持版本递增检查。
- `CONTRIBUTING.md` 的收录前提、质量门表格、新增技能步骤按实际规则重写；PR 模板拆出
  「发布合规」小节。

### 已知待办

平台状态已按 2026-11-26 实测重写（ClawHub `api/v1/skills/<slug>` 逐条查），发现三件事：

- `component-pitfalls` **确实已上线**（ClawHub 1.0.0，166 次下载），此前台账记 `not_published` 是错的，已改 `synced`。
- `embedded-fpga-sim`、`embedded-production-test`、`hw-pcb-review` 在 ClawHub 上**不存在**，发布渠道是
  WorkBuddy 市场（依据仍只有台账的人工确认记录），白名单里标 `workbuddy` 并写明依据。
- 剩 3 个 `ahead`：`embedded-code-generator` 1.1.1、`embedded-code-reviewer` 1.1.2、
  `motor-pid-tuner` 1.1.1。仓库版本比 ClawHub 高，改动都是真修复（`--html` 崩溃、报告页脚版本号、
  映射表补全），回退等于把 bug 放回去。带 `plan` 放行，但下一批发布窗口必须推上平台。

### 回灌：6 个技能与平台版本对齐

仓库此前比平台旧，用户从 GitHub 下到的是旧版本。按平台已发布内容同步：

| 技能 | 仓库旧版 | 对齐后 | 实质变化 |
|---|---|---|---|
| `embedded-debug-trees` | 1.3.1 | **1.4.0** | FPGA/RTL 拆出独立技能，12 棵树 77 节点 → 11 棵 69 节点 |
| `embedded-register-verify` | 1.16.2 | **1.17.0** | 新增 `demo` / `doctor` 子命令；README 与 SKILL 补「先跑 demo」上手动线 |
| `embedded-register-lookup` | 1.11.1 | **1.11.3** | 帮助文本统一品牌名 |
| `embedded-timing-calc` | 1.1.1 | **1.1.2** | 版本号 |
| `embedded-peripheral-pitfalls` | 1.2.1 | **1.2.2** | 版本号、帮助文本统一品牌名 |
| `embedded-driver-templates` | 1.0.0 | **1.0.1** | 驱动文件由 `assets/drivers/<名>/` 压平为 `assets/<名>__<文件>`（平台 Skill 包只支持两级目录），引擎按前缀聚合 |

随之处理的三处连带问题：

- `assets/drivers/` 是压平前的重复副本（45 个文件，与顶层 `__` 平铺文件逐字节相同），已删除，
  打包体积少 45 个文件。
- `tools/knowledge_bench.py` 里 8 条指向 `fpga-rtl` 的评测用例随树一起移除，用例总数 241 → 233，
  仍远高于 100 条门槛。
- `examples/demo_cases.txt` 还留着「症状 12（fpga-rtl）」与 `show ...|fpga-rtl` 的示例，同步清掉。

### README 重构

按读者视角重排：开头给一个真实命令输出，讲清解决什么问题；技能清单 → 安装 → 五分钟上手 →
典型场景 → 查写验闭环 → 适用范围与不覆盖 → 配置 → 设计原则 → 参与开发。

删掉的是仓库治理语言——"本仓库是发布渠道"、"全部自研、均已上线"、"收录边界"、路线图，
以及一段没有读者关心的触发率长文（压成一句并指向 `benchmarks/`）。`CONTRIBUTING.md` 新增
「README 写什么、不写什么」一节，把这条界线写成规则，避免以后又塞回去。

开头示例输出是用 `--demo` 实跑后粘的，不是手写。

### 修复

- `shared/etk_core/cache.py` 的 `cache_dir()` 补兜底：home 展开失败时（Windows 上
  `USERPROFILE` 与 `HOMEDRIVE/HOMEPATH` 都缺失）`expanduser("~")` 会返回字面量 `~`，
  原实现会在用户当前工作目录里造一个 `~/.cache/etk` 目录，污染项目目录。改为退回系统临时目录。
  此修复由 `sync_core.py` 同步到 lookup / verify 的技能副本。
- `.claude-plugin/plugin.json` 与 `marketplace.json` 的「审查 28 条」改为 27 条（四处口径
  此前修过，这两个 JSON 漏了）。
- `references/misra-mapping.md` 缺规则 27（数组形参上 `sizeof`）一行，表格只到 26 条。
  审查器因此升到 **1.1.2**（补齐映射表属于内容变更，按流程必须升版本），并补上
  `reviewer.py` 的 `__version__`，让版本一致性检查能覆盖到它。
- `check_release.py` 的版本递增检查在 Windows 上静默失效：`os.path.join` 产生反斜杠，
  `git show tag:skills\x\SKILL.md` 返回 128，检查结果恒为空。改为显式正斜杠后，
  用「改动未升版本」和「还原」两步变异测试确认能拦住。

## [1.4.1] - 2026-11-25

公开仓库全面体检后的一轮修复：两个真实缺陷、一处文档误导、文档覆盖补齐，
以及 git 历史清理。

### 修复

- **审查器 `--html` 必崩**：`generate_html_report` 里 `scan_desc` 只在审查成功时
  赋值，而入口无论成败都调用它，于是「文件不存在」「语法错误」这类场景一加
  `--html` 就抛 `UnboundLocalError`。已给默认值兜底，失败时报告写明原因。
- **调参报告页脚版本号过期**：`report_gen.py` 硬编码 `1.0.0`（实际 1.1.1），
  用户拿到的报告自带错误版本。改为 `__version__` 变量；`main.py` 同步补上
  `__version__`，让质量门的版本一致性检查能覆盖到。
- **`--mode report` 是错的**：29 种模式表里把 report 写成 `--mode report`，
  但 `main.py` 的 choices 没有它，实际是独立脚本 `report_gen.py`。已标注。

### 质量门加固

- `_runtime_files()` 原来只扫 `skills/*/scripts/*.py`，`reviewer.py`、`main.py`、
  `ota_audit.py`、`ota_tool.py`、`report_gen.py` 这 5 个放在技能根目录的入口脚本
  从未经过「非标准库模块」与「禁 eval/exec/compile」检查。改为遍历技能内全部
  `.py`（排除 `__pycache__`/`tests`/`etk_core`），覆盖 25 → 31 个文件。
- 新增非阻断告警：`description` 超 900 字符时提示。上限 1024 是多个 Agent 的硬
  限制，ZCode 超限会静默丢弃整个技能。
- `CONTRIBUTING.md` 的质量门表格按实际规则重写（原来写的「trigger 用例必须存在」
  「版本必须等于 `__version__`」「只 import 标准库」都已是旧规则），并新增
  「收录前提」：必须已在平台上线、必须自研或授权明确、只收嵌入式相关。

### 文档

- `docs/skills/` 由 5 页补到 **15 页**，每个技能一页（作用 / 版本 / 核心内容 /
  命令 / 实测记录 / 边界）。写文档时又抓出两处照抄会失败的命令：驱动模板库入口
  是 `driver_templates.py` 而非 `engine.py`；PCB 清单无 `--class` 参数。
- README 适配范围表残留的「24 个零依赖」改为 14 个；issue 模板的过期版本号同步。
- CHANGELOG 里 3 处本地开发路径改为通用表述。

### 仓库治理

- `.gitignore` 补 `.benchmarks/`。
- `release.yml` 改为幂等：tag 已有 Release 时改为 `gh release upload --clobber`，
  避免重打 tag 或 force push 时 `gh release create` 因「已存在」失败。
- **git 历史清理**：历史里曾提交过 12 个第三方技能（zhinkgit/embeddedskills、
  EA-SKILL）、4 个内部工具技能、以及 4.5MB 评测转录（含本机绝对路径与 session
  id）。用 `filter-branch` 只删这些路径，72 个提交与 3 个 tag 全部保留。
  `.git` 由 5.4MB 降至 1.7MB，重写后重新验证：历史里只剩当前 15 个技能。

## [1.4.0] - 2026-11-25

收录标准改为**只收已在平台上线的技能**：公开仓库面向外部用户，放进去的必须是能直接
装来用的成品，不能是本地还没上过平台的半成品。

判定依据不再靠人工回想清单，改用发布档案 仓库外部的发布档案（发布台账 JSON）
（该文件自述「判定是否已发布唯一依据是本台账 status + 确认备注」），合并 `assets`
（平台资产）与 `_待提交清单`（本地待提交）两块，取 `status=published` 或
`skillhub`/`clawhub` 为 `live` 的条目。

### 移出 10 个未发布技能

以下技能在台账中状态为 `not_published`，或明确列入 `_不单独发布`（源码保留在专家包 /
主仓内，不作为独立技能发布），全部从公开仓库移出：

| 技能 | 台账状态 |
|---|---|
| `embedded-foc-diagnose` | `_不单独发布` |
| `embedded-fpga-trees` | `_不单独发布` |
| `embedded-protocol-consistency` | `_不单独发布` |
| `embedded-protocol-parser` | `_不单独发布` |
| `embedded-firmware-size` | `_不单独发布` |
| `embedded-unit-test-gen` | `_不单独发布` |
| `hw-calc` | `_不单独发布` |
| `hw-component-lib` | `_不单独发布` |
| `hw-review-checklist` | `_不单独发布` |
| `mcu-debug-installer` | `_不单独发布`（2026-10-27 已拍板退场：专家人设已内置连接引导） |

### 保留 15 个

均已上线（`skillhub` 或 `clawhub` 为 `live`，或 `status=published`）：

`embedded-register-lookup`、`embedded-register-verify`、`embedded-timing-calc`、
`embedded-debug-trees`、`embedded-peripheral-pitfalls`、`embedded-driver-templates`、
`embedded-code-generator`、`embedded-code-reviewer`、`embedded-ota-toolkit`、
`embedded-fpga-sim`、`embedded-production-test`、`motor-pid-tuner`、
`schematic-reader`、`component-pitfalls`、`hw-pcb-review`

### 其他

- README 技能表由 25 项收回 15 项，补「收录边界」说明
- 依赖口径：15 个中 14 个纯标准库，仅 `schematic-reader` 的 PDF 文本层需可选 `pymupdf`
- `plugin.json` 聚合版本 1.3.0 → 1.4.0

## [1.3.0] - 2026-11-25

技能从 14 个扩到 **25 个**。前几轮依赖人工清单判断范围，清单本身不完整；
本轮改为直接扫描开发源 开发源目录 全部嵌入式相关技能，按源盘点入册。

### 新增 11 个

| 技能 | 中文名 | 版本 |
|---|---|---|
| `hw-calc` | 硬件计算器（37 项通用 + 晶振 CL、去耦容量） | 1.1.2 |
| `hw-component-lib` | 器件选型库 | 1.0.0 |
| `hw-review-checklist` | 硬件审查清单 | 1.0.0 |
| `schematic-reader` | 原理图识别器 | 1.0.3 |
| `embedded-protocol-consistency` | 嵌入式协议一致性检查器 | 1.0.0 |
| `embedded-protocol-parser` | 嵌入式协议报文解析器 | 1.0.0 |
| `embedded-fpga-trees` | FPGA/RTL 故障诊断器 | 1.1.0 |
| `embedded-foc-diagnose` | FOC 故障诊断器 | 1.1.0 |
| `embedded-unit-test-gen` | 嵌入式单元测试生成器 | 1.0.0 |
| `embedded-firmware-size` | 嵌入式固件体积分析器 | 1.0.0 |
| `mcu-debug-installer` | MCU 调试 MCP 安装引导 | 1.1.1 |

### 收录判据

只扫开发源下的嵌入式相关专家包（embedded-dev / embedded-debugger / embedded-fpga /
embedded-protocol / embedded-tester / hardware-design / motor-control）、团队包
`team/embedded-team/skills` 与独立技能源 `src/skills`。教学类 `grad-project-*` 不计。

同名技能取文件数与版本高者：例如 `embedded-debug-trees` 保留仓库侧 1.3.1，
而非团队包内被重置的 1.0.0。

### 版本对齐

三处 `SKILL.md` 与脚本 `__version__` 不一致已修正：`embedded-fpga-trees` 的
`gowin_log.py`/`rtl_check.py` 升到 1.1.0；`hw-calc` 的 `SKILL.md` 改为脚本的 1.1.2。

### frontmatter

15 个文件存在重复的 frontmatter 结束符 `---`（拼接时多写一次），已全部清理。

### 依赖

25 个中 24 个零第三方依赖；`schematic-reader` 的 PDF 文本层需 pymupdf，
默认只提示安装命令，显式 `--install-pymupdf` 才会安装，其余格式用自带纯 Python 解析器。

## [1.2.0] - 2026-11-25

技能从 12 个扩到 **14 个**，全部为自研。收录标准：只收自己开发的嵌入式技能。

### 完整技能清单

| 阶段 | 技能 | 版本 |
|---|---|---|
| 设计与选型 | `embedded-register-lookup` 嵌入式寄存器查询器 | 1.11.1 |
| | `embedded-timing-calc` 嵌入式时序计算器 | 1.1.1 |
| | `component-pitfalls` 元器件选型避坑指南 | 1.0.0 |
| | `hw-pcb-review` PCB 布局自查清单 | 1.0.0 |
| 编码与审查 | `embedded-code-generator` 嵌入式代码生成器 | 1.1.1 |
| | `embedded-driver-templates` 嵌入式驱动模板库 | 1.0.0 |
| | `embedded-code-reviewer` 嵌入式C/C++代码审查器 | 1.1.1 |
| | `embedded-register-verify` 嵌入式寄存器写入审计器 | 1.16.2 |
| | `embedded-peripheral-pitfalls` 嵌入式外设配置巡检器 | 1.2.1 |
| 调试与升级 | `embedded-debug-trees` 嵌入式故障诊断器 | 1.3.1 |
| | `embedded-ota-toolkit` 嵌入式OTA升级工具包 | 1.2.0 |
| | `embedded-fpga-sim` FPGA 仿真工作台 | 1.0.0 |
| 测试与调参 | `embedded-production-test` 产品出厂测试方案 | 1.0.0 |
| | `motor-pid-tuner` 电机PID调参器 | 1.1.1 |

### 依赖

14 个全部只依赖 Python 3.10+ 标准库，零 `pip install`。`lookup` 与 `verify` 自带
`etk_core` 副本。`fpga-sim` 的仿真需本机 Icarus Verilog，`code-generator` 可选
用本机 arm-none-eabi-gcc 编译验证，均非运行必需。

### 开发源说明

技能从开发源同步：独立技能源 `src/skills/`（版本最新、
含测试）优先，专家包内技能取 `src/team/embedded-team/skills/`。
`packages/` 下的打包产物是裁剪版（剥离 assets 或 scripts），不可作为同步源。

### 明确不收录

- `zhinkgit/embeddedskills`（第三方 MIT）：keil/eide/gcc/jlink/openocd/probe-rs/
  serial/can/net/terminal/workflow。属工具封装，非自研。
- `jzl-maker/EA-SKILL`（第三方 MIT）：ea-skill。
- 毕设导师类（grad-project / capstone 共 10 个）：教学场景，非嵌入式工程。

### 质量门适配

三处修正：标准库判定改用 `sys.stdlib_module_names`；frontmatter 解析器支持 YAML
列表项（`examples_zh`）；技能内本地模块纳入白名单。

## [1.1.0] - 2026-11-25

技能从 5 个扩到 12 个（自研）：在原有 5 个核心技能上加入 `embedded-driver-templates`、
`schematic-reader`、`component-pitfalls`、`silent-toolchain-failure-diagnosis`、
`mcu-hardfault-live-verify`、`hw-tool-safety-isolation`、`mcu-debug-installer`。
其中后四个为内部工具，已在 1.2.0 按「只收对外发布的自研技能」标准移出。

## [1.0.0] - 2026-11-25

首个正式版本。此前的 v1.0.0 ~ v1.24.2 全部是 2026-10-15 至 10-21 的开发期迭代，未作为对外
版本发布，其 release 与 tag 已于 2026-11-25 清理，记录保留在文末。

### 包含的五个技能

| 技能 | 版本 | 内容 |
|---|---|---|
| `embedded-register-lookup` | 1.11.1 | CMSIS-SVD 寄存器 / 位域 / 复位值 / 中断号查询，地址反查、值解码、宏生成、双芯片对比、SVD 质量检查、SDK 自带 SVD 自动发现 |
| `embedded-register-verify` | 1.16.2 | C/C++ 寄存器写入核验，E01–E13 规则，报 / 未判定 / 通过三桶输出；注入集召回 229/229，9 个真实 SDK 0 误报 |
| `embedded-debug-trees` | 1.3.1 | 12 棵排障决策树 / 77 节点，每步先取证再判断 |
| `embedded-peripheral-pitfalls` | 1.2.1 | 25 类外设 / 148 个配置坑，症状 + 对策 |
| `embedded-timing-calc` | 1.1.1 | 37 个时序计算器，结果带公式回显与合法性判定 |

### 工程

- Python 支持下限提高到 **3.10**（3.9 已于 2025-10 结束维护）；运行时仍为零第三方依赖、离线。
- CI 覆盖 ubuntu / windows / macOS × Python 3.10 / 3.12 / 3.13，`checkout` 与 `setup-python`
  升到 v7，工作流令牌权限收窄为 `contents: read`。
- 质量门 `tools/check_repo.py` 的语法检查基准同步改为 3.10。
- 作者名统一为 `fangcun`（`plugin.json`、`marketplace.json`、5 个 `SKILL.md`、`LICENSE`）。
- 新增 `.gitattributes`，仓库文本统一 LF。

### 文档

- README 重构：技能表从单单元格最长 1753 字符拆为五列概览 + `docs/skills/` 逐技能详情。
- 修正三处照抄必失败的命令：`examples/verify_demo.c` 路径、`set` 的 `DIR=UP` 枚举示例、
  `timing.py i2c-rp` 的参数名。
- 新增 `CONTRIBUTING.md`、issue 表单与 PR 模板。

## 开发期迭代记录（未对外发布）

以下版本仅存在于开发阶段，release 与 tag 已清理，保留变更内容供追溯。

### 1.24.2 - 2026-10-21

- 作者名与五个技能的市场能力介绍改写（痛点 + 硬指标）。

### 1.24.1 - 2026-10-21

- 三个新技能的 `--help` 补使用示例（用户旅程审计发现新人首跑断点）；trees 1.3.1 / pitfalls 1.2.1 / timing 1.1.1。
- 补时序审查单收编闭环与 v1.3.0 FPGA 触发抽测记录。

### 1.24.0 - 2026-10-20

- 决策树补 CAN/CAN-FD 树与 DMA 坑类别（11 树 / 23 类），依据字段补齐。
- 覆盖面收口：flash 补 QSPI/XIP 坑，通信树补物理层根因（共地 / 接反 / 电平），评测 +2（232 例）。
- 五技能全量体检：核验语义、时序公式、检索量具、元数据一致性。
- `timing-calc` 输出在 GBK 控制台因 `µ` 字符崩溃，stdout 统一 UTF-8。
- 测试辅助函数改用 `write_bytes`，兼容当时的 Python 3.9 下限（CI 修复）。
- 把关复核：usb-enum 描述符口径、mpu 背景区域语义（PRIVDEFENA 非 region 0），补 `next`×20 / `see`×18 闭环。
- 避坑清单依据字段补齐至 148/148；README 增加「让 Agent 更愿意查库」建议配置。
- 回填触发轮（`deepseek_for_coding`）：决策树 52.5% / 避坑 14.3%，反例 33/33 零误触发。

### 1.22.1 - 2026-10-20

- 知识技能 description 重构：中文症状句前置；真机 A/B 后 +10pp（决策树 49%→59%、避坑 38%→47%）。

### 1.22.0 - 2026-10-19

- 知识技能并入：排障决策树 v1.1.0 + 外设避坑清单 v1.1.0。
- 清理误入仓库的评测原始产物与嵌套重复目录。

### 1.21.1 - 2026-10-17

- 核验器 E13 规则（写 1 清零寄存器读改写）、pico-sdk 生态支持（verify 1.16.0）。
- 交付体检修正：E13 覆盖判定、闭环提示、`--define` 警告（verify 1.16.1 / lookup 1.11.0）。

### 1.21.0 - 2026-10-17

- 细节深化 III：C/C++ `enum` 常量求值、补丁模式用整文件做上下文（verify 1.15.0）。

### 1.20.0 及更早

见 git 历史（`git log --oneline`）。
