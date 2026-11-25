# 变更记录

版本号在两处维护：`.claude-plugin/plugin.json` 是插件聚合版本，各技能 `SKILL.md` 的
`metadata.version` 是技能独立版本。质量门 `tools/check_repo.py` 会校验技能版本与脚本
`__version__` 一致。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

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

技能从开发源 `D://work//.dev//ls//src` 同步：独立技能源 `src/skills/`（版本最新、
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
