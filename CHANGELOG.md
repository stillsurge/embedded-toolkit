# 变更记录

版本号在两处维护：`.claude-plugin/plugin.json` 是插件聚合版本，各技能 `SKILL.md` 的
`metadata.version` 是技能独立版本。质量门 `tools/check_repo.py` 会校验技能版本与脚本
`__version__` 一致。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

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
