# 变更记录

版本号在两处维护：`.claude-plugin/plugin.json` 是插件聚合版本，各技能 `SKILL.md` 的
`metadata.version` 是技能独立版本。质量门 `tools/check_repo.py` 会校验技能版本与脚本
`__version__` 一致。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [1.1.0] - 2026-11-25

技能从 5 个扩到 **12 个**，全部为本仓库自研。收录标准：只收自己开发的嵌入式技能，
不收第三方技能包。

### 新增技能（7 个）

| 技能 | 内容 |
|---|---|
| `embedded-driver-templates` | 9 款常用驱动模板（DHT11/DS18B20/HC-05/HC-SR04/MPU6050/SSD1306/SG90/28BYJ-48/ESP8266-AT），算法层纯 C99、平台差异收在 port 层；另含外设初始化顺序查询 |
| `schematic-reader` | 解析 Altium / Cadence / KiCad / 立创 EDA / 通用网表，输出引脚级网表供连通性查询；只给确定性解析事实，不做审查判断 |
| `component-pitfalls` | 采购避坑：渠道四级分级、四类假芯片识别、五步验真法、缺货替代链、220V 与锂电安全红线 |
| `silent-toolchain-failure-diagnosis` | 诊断「工具装了但静默失败」：rc≠0 却无 stdout/stderr、被误判成沙箱/权限/网络问题 |
| `mcu-hardfault-live-verify` | 真机故障注入 → 抓寄存器 → 反查出错函数，验证排障能力在真实芯片上成立 |
| `hw-tool-safety-isolation` | 给会真正操作硬件的工具/脚本/MCP 加默认安全隔离与强制检查 |
| `mcu-debug-installer` | mcu-debug-mcp 的安装引导与首次连接验收，适配任意 stdio MCP 宿主 |

### 明确不收录

以下为第三方开源项目，与本仓库技能正交，需要时按各自仓库安装：

- `zhinkgit/embeddedskills`（MIT）——11 个工具链技能：keil、eide、gcc、jlink、openocd、
  probe-rs、serial、can、net、terminal、workflow。它们驱动本机已装的 Keil/J-Link/OpenOCD，
  本质是工具封装而非芯片知识，且版权属原作者。
- `jzl-maker/EA-SKILL`（MIT，Copyright (c) 2026 jzl-maker）——嵌入式 AI 开发管家。

### 依赖口径

12 个技能里 11 个纯标准库；仅 `schematic-reader` 需 `PyMuPDF` 解析 PDF 原理图，
已在该技能根目录声明 `requirements.txt`。质量门支持声明第三方依赖，并识别包名与
import 名不一致的情况（PyMuPDF→fitz）。

### 质量门适配

导入这批技能时暴露三处过窄规则，已修正：标准库判定由手写白名单改为
`sys.stdlib_module_names`（原白名单漏掉 sqlite3/subprocess/shutil/importlib）；
技能内本地模块（如 `engine.py`）纳入白名单；触发评测用例从「必须有」改为
「有则校验下限」，纯知识技能不再被阻断。

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
