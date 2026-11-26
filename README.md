# 嵌入式开发工具箱

[![ci](https://github.com/stillsurge/embedded-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/stillsurge/embedded-toolkit/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/stillsurge/embedded-toolkit?label=release)](https://github.com/stillsurge/embedded-toolkit/releases)
[![license](https://img.shields.io/github/license/stillsurge/embedded-toolkit)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](#设计原则)

给 AI 编程助手用的嵌入式技能包，15 个技能，装完就能用，不联网、不装包。

模型会把不存在的位名编得很像真的（`USART_CR1_XXX`）、把超位宽的值算得很自信、在没开时钟的时候
就写寄存器。这三类错误编译都能过，上板才发现外设不动，回头查往往是一下午。

这 15 个技能把"查证"做成命令：结论离线算出，每条带 `source`（文件 / 设备 / 版本）与 `label`
（证据等级）。**AI 负责写得快，工具箱负责验得对。**

```bash
$ python skills/embedded-register-lookup/scripts/lookup.py lookup USART1.CR1 --demo
USART1.CR1  地址 0x40013800  偏移 0x00  宽度 32 位  访问 read-write  复位值 0x00000000
说明：控制寄存器 1
位域：
  bit 0      UE           访问 read-write  复位 0  USART 使能
  bit 1      RE           访问 read-write  复位 0  接收使能
  bit 2      TE           访问 read-write  复位 0  发送使能
  ...
[已核验] 来源：demo.svd（设备 ETK-DEMO，版本 1.0），SVD 选择方式：内置演示数据（--demo）
```

## 技能清单

按固件工程阶段分四组。命令、实测记录、已知边界在 [`docs/skills/`](docs/skills/) 各页。

### 设计与选型

| 技能 | 一句话 | 版本 |
|---|---|---|
| **嵌入式寄存器查询器**<br>`embedded-register-lookup` | 查寄存器 / 位域 / 复位值 / 中断号；地址反查、值解码、宏生成、双芯片对比 | 1.11.3 |
| **嵌入式时序计算器**<br>`embedded-timing-calc` | 37 个计算器：波特率、PWM、I2C 上拉、SPI 时序等，回显公式与合法性依据 | 1.1.2 |
| **元器件选型避坑指南**<br>`component-pitfalls` | 渠道分级、四类假芯片识别、五步验真、缺货替代链、220V 与锂电安全红线 | 1.0.0 |
| **原理图识别器**<br>`schematic-reader` | 解析 Altium / Cadence / KiCad / 立创 / OrCAD / EAGLE / 网表，输出引脚级网表与连通性查询 | 1.0.3 |
| **PCB 布局自查清单**<br>`hw-pcb-review` | 布局自查打勾与报告生成，覆盖电源、地、USB、晶振等高频出错点 | 1.0.0 |

### 编码与审查

| 技能 | 一句话 | 版本 |
|---|---|---|
| **嵌入式代码生成器**<br>`embedded-code-generator` | 15 类嵌入式 C 模块（PI 控制器、RS485、CRC、环形缓冲、SVPWM 等），产出可编译的 .h + .c | 1.1.1 |
| **嵌入式驱动模板库**<br>`embedded-driver-templates` | 9 款常用驱动模板（DHT11 / DS18B20 / SSD1306 / MPU6050 等）+ 外设初始化顺序查询 | 1.0.1 |
| **嵌入式C/C++代码审查器**<br>`embedded-code-reviewer` | 27 条规则查真雷：ISR 里调延时、共享变量缺 volatile、数组越界等，每条附 MISRA 编号与修复建议 | 1.1.2 |
| **嵌入式寄存器写入审计器**<br>`embedded-register-verify` | 核验 C/C++ 里的寄存器写入是否与芯片 SVD 一致，按「报 / 未判定 / 通过」分桶 | 1.17.0 |
| **嵌入式外设配置巡检器**<br>`embedded-peripheral-pitfalls` | 25 类外设 148 个配置坑，每坑 = 症状 + 对策 | 1.2.2 |

### 调试与升级

| 技能 | 一句话 | 版本 |
|---|---|---|
| **嵌入式故障诊断器**<br>`embedded-debug-trees` | 11 棵树 69 节点，先取证再判断，不直接开药 | 1.4.0 |
| **嵌入式OTA升级工具包**<br>`embedded-ota-toolkit` | OTA / Bootloader 升级链路静态审计，15 条防砖规则，可出报告并入 CI 门禁 | 1.2.0 |
| **FPGA 仿真工作台**<br>`embedded-fpga-sim` | testbench 模板与仿真判读，覆盖 counter / FIFO / SPI 从机 / CDC 等场景 | 1.0.0 |

### 测试与调参

| 技能 | 一句话 | 版本 |
|---|---|---|
| **产品出厂测试方案**<br>`embedded-production-test` | 按板型与规格生成产线测试规范，含电流上下限、节拍、老化温循 | 1.0.0 |
| **电机PID调参器**<br>`motor-pid-tuner` | 电流 / 速度 / 位置环参数计算，含 ZN 整定、离散化、抗饱和、死区补偿 | 1.1.1 |

> 驱动本机工具链的技能（Keil / J-Link / OpenOCD / 串口 / CAN）不在这里，用
> [`zhinkgit/embeddedskills`](https://github.com/zhinkgit/embeddedskills)（MIT）。两者不重叠，可以同时装。

## 安装

技能遵循 Agent Skills 开放标准，任何支持 Skills 的 Agent 都能装。

### 一条命令

```bash
npx skills add stillsurge/embedded-toolkit -a claude-code   # Claude Code
npx skills add stillsurge/embedded-toolkit -a cursor        # Cursor
npx skills add stillsurge/embedded-toolkit -a codex         # Codex
npx skills add stillsurge/embedded-toolkit -a qoder         # Qoder
npx skills add stillsurge/embedded-toolkit -a zcode         # ZCode

# 一次装多个（空格分隔，逗号会被拒绝）
npx skills add stillsurge/embedded-toolkit -a claude-code cursor codex qoder zcode --all

# 只装一个
npx skills add stillsurge/embedded-toolkit --skill embedded-register-lookup -a claude-code
```

加 `-g` 装到用户级目录（所有项目可用），不加则装到当前项目。`-a` 支持 79 个 Agent 目标；
拿不准标识就随便给个非法值，CLI 会把合法标识全打出来。

### 装完在哪个目录

| Agent | `-a` 标识 | 用户级目录 |
|---|---|---|
| Claude Code | `claude-code` | `~/.claude/skills/` |
| Cursor | `cursor` | `~/.agents/skills/` |
| Codex | `codex` | `~/.agents/skills/` |
| Qoder | `qoder` | `~/.qoder/skills/` |
| ZCode | `zcode` | `~/.zcode/skills/` |
| CodeBuddy | `codebuddy` | `~/.codebuddy/skills/` |

2026-11 在 Windows 上 `-g --copy` 实测。**WorkBuddy 读 `~/.workbuddy/skills/`**，与 CLI 的
`codebuddy` 目标不是一个目录，装完再复制一次：

```powershell
Copy-Item -Recurse "$HOME\.codebuddy\skills\embedded-*" "$HOME\.workbuddy\skills\"
```

### Claude Code 插件市场

```bash
/plugin marketplace add stillsurge/embedded-toolkit
/plugin install embedded-toolkit@embedded-toolkit
```

### 不用 CLI

从 [Releases](https://github.com/stillsurge/embedded-toolkit/releases) 下 zip：整包是
`embedded-toolkit-vX.Y.Z.zip`，单技能是 `<技能名>-vX.Y.Z.zip`。解压后把文件夹放进目标 Agent 的
技能目录即可。也可以直接复制仓库里的 `skills/<技能名>/`——每个技能自带依赖，放哪都能独立跑。

### 依赖

14 个技能只用 Python 3.10+ 标准库，无需 `pip install`。`schematic-reader` 解析 PDF 文本层时
可选 `PyMuPDF`（技能根有 `requirements.txt`，不加 `--install-pymupdf` 时只提示不安装）。

所有技能**不联网**、**不执行用户代码**，也不依赖本机烧录器 / 调试器。

## 五分钟上手

不用准备 SVD、不用真实芯片，内置合成演示数据（`--demo`）直接能跑：

```bash
python skills/embedded-register-lookup/scripts/lookup.py fields GPIOA.MODER --demo
python skills/embedded-register-lookup/scripts/lookup.py doctor                  # 本机 SVD 从哪来、有没有
python skills/embedded-register-lookup/scripts/lookup.py devices --filter STM32   # 本机有哪些芯片可用
python skills/embedded-register-verify/scripts/verify.py demo                     # 核验器自检，退出码 0 = 正常
```

换成真实芯片（需要本机 CMSIS-Pack，或直接给 SVD 文件）：

```bash
L=skills/embedded-register-lookup/scripts/lookup.py   # bash 简写；PowerShell 写完整路径

python $L lookup USART1.CR1.UE --chip STM32G431       # 按芯片名自动找 SVD
python $L addr 0x4001380C --svd ./STM32G431xx.svd     # 没有 Pack 就直接给文件
python $L decode RCC.CR 0x00040002 --chip STM32G431   # 按位解码寄存器值
python $L set TIM1.CR1 CEN=1 --chip STM32G431         # 算写入值
python $L set GPIOA.MODER MODE0=output --demo          # 字段有枚举时可用枚举名
python $L irq USART1 --chip STM32G431                 # 中断号 + NVIC 使能位
python $L macros USART1.CR1 --chip STM32G431          # CMSIS 风格宏
python $L diff USART1.CR1 --chip-a STM32F103C8 --chip-b STM32G431   # 双芯片对比
```

## 四个典型场景

**"这个位到底叫什么？复位值多少？"**

```bash
python skills/embedded-register-lookup/scripts/lookup.py lookup USART1.CR1.UE --chip STM32G431
```

**"AI 给我生成的初始化代码靠谱吗？"**

```bash
python skills/embedded-register-verify/scripts/verify.py check Core/Src --chip STM32G431
```

**"串口就是收不到数据"**

```bash
python skills/embedded-debug-trees/scripts/trees.py search "串口收不到数据"
```

**"I2C 上拉该选多大？"**

```bash
python skills/embedded-timing-calc/scripts/timing.py i2c-rp --bus fast --cb 200 --vdd 3.3
```

## 查 → 写 → 验

查询器与审计器共用同一份 SVD 和缓存规则，一次配置、一套数据：

```bash
L=skills/embedded-register-lookup/scripts/lookup.py
V=skills/embedded-register-verify/scripts/verify.py

python $L lookup USART1.CR1 --chip STM32G431     # 1. 写之前先拿事实
python $V check main.c --chip STM32G431           # 2. 写完核验
python $V check Core/Src --chip STM32G431 --checklist   # 目录级复查清单
python $V check --patch changes.diff --chip STM32G431   # 只验补丁新增行
```

审计输出分三桶：**报**（E01–E13，带行号 / 类别 / 建议）、**未判定**（HAL 调用、内核外设等范围外
内容，如实说明）、**通过**。退出码 1 表示检出问题。每条「报」都带 `next` 字段，是可直接执行的
查询命令，已带好本次的 `--chip` / `--svd` / `--demo`。

## 适用范围

| 维度 | 覆盖 |
|---|---|
| 芯片 / 厂商 | 任何有 CMSIS SVD 的芯片：ST、GigaDevice、Nordic、NXP、Renesas、Microchip 等；ESP32 系列、RP2040 由 SDK 自带 SVD 自动发现 |
| SVD 来源 | `--svd` 指定 / 项目内扫描（深度 ≤6）/ 环境变量 `ETK_SVD_DIR` / 本机 CMSIS-Pack 缓存 / PlatformIO、Arduino15、ESP-IDF、Pico SDK |
| 工具链 | Keil MDK、STM32CubeMX、PlatformIO、ESP-IDF、Arduino、Zephyr、nRF Connect SDK 的目录结构；Windows / macOS / Linux |
| 代码写法 | CMSIS 结构体与宏、厂商别名、地址别名宏、`HWREG`、C/C++ 与 Arduino；ESP-IDF 风格寄存器宏记「未判定」 |

**不覆盖**：引脚复用（AF 表）、时钟树、手册勘误、外挂器件命令。SVD 质量由厂商决定，发现错误以
手册为准并可提 issue。逐项对照验证做过 ST（STM32G431）、Nordic（nRF52840）、GigaDevice
（GD32F3x0）三家，其他厂商待补。

完整写法清单见 [`docs/skills/embedded-register-verify.md`](docs/skills/embedded-register-verify.md)。

## 配置

项目根目录放 `.etk/config.json` 可省去重复参数：

```json
{ "chip": "STM32G431RB", "svd": "tools/svd/STM32G431xx.svd" }
```

- 项目里的 `.svd` 会自动扫描（深度 ≤ 6）
- 解析结果缓存在本机（`%LOCALAPPDATA%\etk\cache` 或 `~/.cache/etk`），SVD 改动后自动失效；`ETK_NO_CACHE=1` 关闭
- 输出默认中文文本；`--format json` 给 Agent 解析，`--format md` 输出表格，`--out 文件` 存盘

## 让 AI 真的去查

强编码模型常凭记忆直接回答"这东西有哪些坑"。把下面这段加进项目 `CLAUDE.md` 或系统提示，能明显
提高查库率：

```
涉及寄存器位定义/复位值、外设配置阈值（上拉阻值/采样点/死区/波特率误差）、芯片细节或
"某外设有哪些坑"的问题，先运行 embedded-register-lookup / embedded-peripheral-pitfalls /
embedded-debug-trees / embedded-timing-calc 查询，再依据查询结果回答；不要凭记忆给出具体数值或位名。
```

触发率实测记录在 [`benchmarks/`](benchmarks/)（含未触发原因与反例零误触发数据）。

## 设计原则

- **零运行时依赖**：只使用 Python 3.10+ 标准库。
- **离线**：不联网，不调用任何外部 API。
- **只读**：不修改用户项目文件，写出只发生在 `--out` 指定的路径。
- **不执行被检查的代码**：审计器只做词法分析，不 `eval`、不运行用户代码。
- **不内置厂商文件**：SVD 由本机 CMSIS-Pack 或自备文件提供；仓库只带一份自编的合成演示数据。
- **每条结论有出处**：`source` 给出文件 / 设备 / 版本，`label` 给出证据等级。

## 参与开发

```bash
python -m pip install -r requirements-dev.txt
python tools/sync_core.py      # 改动 shared/etk_core 后必跑
python tools/check_repo.py     # 仓库质量门
python -m pytest -q            # 单元与集成测试
```

```
shared/etk_core/   共享核心源码（唯一来源，各技能带副本）
skills/<技能名>/     SKILL.md、scripts/、references/、assets/
docs/skills/       各技能的能力说明、命令与实测记录
tools/             同步、质量门、发布体检与评测脚本
tests/             单元测试、合成夹具、触发评测用例
```

贡献规则见 [CONTRIBUTING.md](CONTRIBUTING.md)，发版流程见 [docs/release-process.md](docs/release-process.md)，
版本变更见 [CHANGELOG.md](CHANGELOG.md)。

## 许可

MIT。厂商 SVD 的版权归原厂商，本仓库不包含这些文件。
