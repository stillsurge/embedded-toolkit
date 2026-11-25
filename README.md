# 嵌入式开发工具箱（embedded-toolkit）

[![ci](https://github.com/stillsurge/embedded-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/stillsurge/embedded-toolkit/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/stillsurge/embedded-toolkit?label=release)](https://github.com/stillsurge/embedded-toolkit/releases)
[![license](https://img.shields.io/github/license/stillsurge/embedded-toolkit)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](#设计约束)

给 AI 编程助手用的嵌入式技能包。15 个已发布的自研技能，一条主线：**AI 负责写得快，工具箱负责验得对**。

> Evidence-first embedded dev skills for AI coding agents — register lookup & code verification from CMSIS-SVD,
> debug decision trees, peripheral pitfall lists and one-shot timing calculations.
> Offline, every answer cites its source.

## 为什么需要它

模型会把不存在的位名编得很像真的：`USART_CR1_XXX`、超过字段宽度的值、没开时钟就写的寄存器。这类错误
编译能过、跑起来才发现外设不动，排查成本高。

这 15 个技能把"查证"变成可执行命令：结论离线算出，每条带 `source`（文件 / 设备 / 版本）与 `label`（证据等级）。

## 15 个技能

全部为本仓库自研，且**均已在 WorkBuddy / SkillHub / ClawHub 发布上线**，本仓库只做 GitHub 侧的分发入口。
按固件工程阶段分四组。

### 设计与选型

| 技能 | 一句话 | 版本 |
|---|---|---|
| **嵌入式寄存器查询器**<br>`embedded-register-lookup` | 查寄存器 / 位域 / 复位值 / 中断号；地址反查、值解码、宏生成、双芯片对比 | 1.11.1 |
| **嵌入式时序计算器**<br>`embedded-timing-calc` | 37 个计算器：波特率、PWM、I2C 上拉、SPI 时序等，回显公式与合法性依据 | 1.1.1 |
| **元器件选型避坑指南**<br>`component-pitfalls` | 渠道四级分级、四类假芯片识别、五步验真、缺货替代链、220V 与锂电安全红线 | 1.0.0 |
| **原理图识别器**<br>`schematic-reader` | 解析 Altium / Cadence / KiCad / 立创 / OrCAD / EAGLE / 网表，输出引脚级网表与连通性查询 | 1.0.3 |
| **PCB 布局自查清单**<br>`hw-pcb-review` | 布局自查打勾与报告生成，覆盖电源、地、USB、晶振等高频出错点 | 1.0.0 |

### 编码与审查

| 技能 | 一句话 | 版本 |
|---|---|---|
| **嵌入式代码生成器**<br>`embedded-code-generator` | 15 类嵌入式 C 模块（PI 控制器、RS485、CRC、环形缓冲、SVPWM 等），产出可编译的 .h + .c | 1.1.1 |
| **嵌入式驱动模板库**<br>`embedded-driver-templates` | 9 款常用驱动模板（DHT11/DS18B20/SSD1306/MPU6050 等）+ 外设初始化顺序查询 | 1.0.0 |
| **嵌入式C/C++代码审查器**<br>`embedded-code-reviewer` | 27 条规则查真雷：ISR 里调延时、共享变量缺 volatile、数组越界等，每条附 MISRA 编号与修复建议 | 1.1.1 |
| **嵌入式寄存器写入审计器**<br>`embedded-register-verify` | 核验 C/C++ 里的寄存器写入是否与芯片 SVD 一致，按「报 / 未判定 / 通过」分桶 | 1.16.2 |
| **嵌入式外设配置巡检器**<br>`embedded-peripheral-pitfalls` | 25 类外设 148 个配置坑，每坑 = 症状 + 对策 | 1.2.1 |

### 调试与升级

| 技能 | 一句话 | 版本 |
|---|---|---|
| **嵌入式故障诊断器**<br>`embedded-debug-trees` | 12 棵树 77 节点，先取证再判断，不直接开药 | 1.3.1 |
| **嵌入式OTA升级工具包**<br>`embedded-ota-toolkit` | OTA/Bootloader 升级链路静态审计，15 条防砖规则，可出报告并入 CI 门禁 | 1.2.0 |
| **FPGA 仿真工作台**<br>`embedded-fpga-sim` | testbench 模板与仿真判读，覆盖 counter / FIFO / SPI 从机 / CDC 等场景 | 1.0.0 |

### 测试与调参

| 技能 | 一句话 | 版本 |
|---|---|---|
| **产品出厂测试方案**<br>`embedded-production-test` | 按板型与规格生成产线测试规范，含电流上下限、节拍、老化温循 | 1.0.0 |
| **电机PID调参器**<br>`motor-pid-tuner` | 电流 / 速度 / 位置环参数计算，含 ZN 整定、离散化、抗饱和、死区补偿 | 1.1.1 |

逐技能的规则、覆盖写法与实测记录见 [`docs/skills/`](docs/skills/)（覆盖五个核心知识技能）。

> 收录边界：只收**已在 WorkBuddy / SkillHub / ClawHub 发布上线**的自研技能。
> 本地还在开发或未上过平台的不放进公开仓库，避免用户拿到半成品。

> 关于工具链：Keil / J-Link / OpenOCD / 串口 / CAN 这类"驱动本机工具"的技能不在本仓库。
> 需要的话用 [`zhinkgit/embeddedskills`](https://github.com/zhinkgit/embeddedskills)（MIT），
> 与本仓库技能正交，可同时安装。

## 四个典型场景

**"这个位到底叫什么？复位值多少？"** → 百事通

```bash
python skills/embedded-register-lookup/scripts/lookup.py lookup USART1.CR1.UE --chip STM32G431
```

**"AI 给我生成的初始化代码靠谱吗？"** → 核验器

```bash
python skills/embedded-register-verify/scripts/verify.py check Core/Src --chip STM32G431
```

**"串口就是收不到数据"** → 决策树

```bash
python skills/embedded-debug-trees/scripts/trees.py search "串口收不到数据"
```

**"I2C 上拉该选多大？"** → 时序计算器

```bash
python skills/embedded-timing-calc/scripts/timing.py i2c-rp --bus fast --cb 200 --vdd 3.3
```

## 安装

本仓库只提供**技能**（Agent Skills 开放标准），不包含专家包。任何支持 Skills 的 Agent 都能直接安装。

### 一条命令装到你的 Agent

```bash
npx skills add stillsurge/embedded-toolkit -a claude-code   # Claude Code
npx skills add stillsurge/embedded-toolkit -a cursor        # Cursor
npx skills add stillsurge/embedded-toolkit -a codex         # Codex
npx skills add stillsurge/embedded-toolkit -a qoder         # Qoder
npx skills add stillsurge/embedded-toolkit -a zcode         # ZCode

# 一次装到多个（多值用空格分隔，逗号会被拒绝）
npx skills add stillsurge/embedded-toolkit -a claude-code cursor codex qoder zcode --all
```

`skills` CLI 当前支持 **79 个 Agent 目标**，包括 Claude Code、Cursor、Codex、Qoder、ZCode、
CodeBuddy、Trae、Windsurf、Cline、Roo、OpenCode、Gemini CLI、GitHub Copilot、Kiro、通义灵码等。
完整列表：随便给一个非法的 `-a` 值，CLI 会把合法标识全打印出来。

加 `-g` 装到用户级目录（所有项目可用），不加则装到当前项目目录。

**只装其中一个**：

```bash
npx skills add stillsurge/embedded-toolkit --skill embedded-register-lookup -a claude-code
```

`--skill` 后面跟技能名，多个技能用空格分隔（`--skill a b`，不能用逗号）。

### 实测落盘位置

| Agent | `-a` 标识 | 用户级目录 |
|---|---|---|
| Claude Code | `claude-code` | `~/.claude/skills/` |
| Cursor | `cursor` | `~/.agents/skills/` |
| Codex | `codex` | `~/.agents/skills/` |
| Qoder | `qoder` | `~/.qoder/skills/` |
| ZCode | `zcode` | `~/.zcode/skills/` |
| CodeBuddy | `codebuddy` | `~/.codebuddy/skills/` |

以上为 2026-11-25 在 Windows 上 `-g --copy` 的实测结果。

**WorkBuddy 用户注意**：WorkBuddy 读的是 `~/.workbuddy/skills/`，而 CLI 的 `codebuddy` 目标落到
`~/.codebuddy/skills/`，两者不是同一目录。装完再复制一次：

```powershell
Copy-Item -Recurse "$HOME\.codebuddy\skills\embedded-*" "$HOME\.workbuddy\skills\"
```

复制后在 WorkBuddy 里刷新技能列表即可看到。

### Claude Code 插件市场

```bash
/plugin marketplace add stillsurge/embedded-toolkit
/plugin install embedded-toolkit@embedded-toolkit
```

### 手动安装（不用 CLI）

从 [Releases](https://github.com/stillsurge/embedded-toolkit/releases) 下载 zip，解压后把 `skills/` 下的
文件夹复制到目标 Agent 的技能目录。

| 包 | 适用 |
|---|---|
| `embedded-toolkit-vX.Y.Z.zip` | 全部 15 个技能 |
| `<技能名>-vX.Y.Z.zip` | 单个技能，按需下载 |

也可以直接复制仓库里的 `skills/<技能名>/` 整个文件夹，复制到任何位置都能独立运行。

### 依赖说明

15 个技能里 14 个只用 Python 3.10+ 标准库；`schematic-reader` 解析 PDF 需 pymupdf（可选，缺省时只提示不安装）：

| 技能 | 依赖 |
|---|---|
| 14 个 | 无第三方包。`lookup` 与 `verify` 自带 `etk_core` 副本，其余为纯知识库或模板 |
| `schematic-reader` | 可选 `PyMuPDF`（仅 PDF 文本层需要）；技能根目录有 `requirements.txt`，不加 `--install-pymupdf` 时只提示不安装 |

所有技能都**不联网**、**不执行用户代码**，也不依赖任何本机烧录器/调试器。

**让 Agent 更愿意查库（建议）**：强编码模型常凭记忆直接回答"配置有哪些坑"类问题。把下面一段加进项目的
`CLAUDE.md` 或系统提示，可显著提高查库率：

```
涉及寄存器位定义/复位值、外设配置阈值（上拉阻值/采样点/死区/波特率误差）、芯片细节或"某外设有哪些坑"的问题，
先运行 embedded-register-lookup / embedded-peripheral-pitfalls / embedded-debug-trees / embedded-timing-calc 查询，
再依据查询结果回答；不要凭记忆给出具体数值或位名。
```

**实测状态**：触发评测三轮已完成。首轮核验器 22 正 + 10 反（Claude Code 29/32、OpenCode 31/32）、
百事通 35 正 + 10 反（Claude Code 39/45、OpenCode 41/45），合计 140/154 = 90.9%，漏报与边界如实记录于
[`benchmarks/trigger-results.md`](benchmarks/trigger-results.md)。知识技能触发轮（2026-10-20，
路由 `deepseek_for_coding`）：决策树 52.5%、避坑 14.3%，**反例 33/33 零误触发**；未触发主因是强路由模型
对咨询型问题直接作答，危害面收敛在寄存器级事实题，见
[`benchmarks/trigger-results-trees.md`](benchmarks/trigger-results-trees.md)。Trae CN / WorkBuddy / Codex / Cursor 待人工。

## 快速上手

零配置试用：内置合成演示芯片（`--demo`，非真实芯片），不需要装任何 SVD。

```bash
python skills/embedded-register-lookup/scripts/lookup.py fields GPIOA.MODER --demo
python skills/embedded-register-lookup/scripts/lookup.py doctor                   # 本机 SVD 从哪来、有没有
python skills/embedded-register-lookup/scripts/lookup.py devices --filter STM32   # 本机有哪些芯片可用
python skills/embedded-register-verify/scripts/verify.py check skills/embedded-register-verify/examples/verify_demo.c --demo
```

配好芯片后（或直接给 SVD 文件）：

```bash
L=skills/embedded-register-lookup/scripts/lookup.py   # 以下用 $L 简写（bash）；PowerShell 请写完整路径

python $L lookup USART1.CR1.UE --chip STM32G431     # 芯片名：自动在本机 CMSIS-Pack / 项目目录找 SVD
python $L addr 0x4001380C --svd ./STM32G431xx.svd   # 没有 Pack 时直接给文件
python $L decode RCC.CR 0x00040002 --chip STM32G431 # 按位解码寄存器值
python $L fields TIM1.CR1 --chip STM32G431          # 位域速查：掩码、复位、枚举
python $L diagram TIM1.CR1 --chip STM32G431         # 位图布局
python $L set TIM1.CR1 CEN=1 --chip STM32G431         # 算写入值（值用数字）
python $L set GPIOA.MODER MODE0=output --demo        # 字段带枚举时可直接用枚举名
python $L irq USART1 --chip STM32G431               # 中断号 + NVIC 使能位
python $L macros USART1.CR1 --chip STM32G431        # CMSIS 风格宏
python $L diff USART1.CR1 --chip-a STM32F103C8 --chip-b STM32G431  # 双芯片对比
python $L lint --chip STM32G431                     # 体检 SVD 质量
```

核验器：

```bash
V=skills/embedded-register-verify/scripts/verify.py   # 同上

python $V check Core/Src --chip STM32G431         # 目录
python $V check main.c --chip STM32G431 --checklist
python $V check --patch changes.diff --chip STM32G431   # git diff 模式
```

核验输出分三桶：**报**（E01–E13，附行号 / 类别 / 建议）、**未判定**（HAL 调用、内核外设等范围外内容，
如实说明）、**通过**；退出码 1 表示检出问题。

## 查 → 写 → 验闭环

百事通与核验器共用同一份 SVD 与查找 / 缓存规则，一次安装、一套数据：

1. **查**：写代码前拿事实（位域、掩码、复位值、枚举、写读语义）。
2. **验**：写完（尤其 AI 生成）用核验器检查；报告分「报 / 未判定 / 通过」。
3. **闭环**：每条「报」都带 `next` 字段——可直接执行的百事通命令（已带本次 `--svd` / `--chip` / `--demo` 参数）。
   `--explain` 还能把寄存器定义内联进报告。
4. 修复后用同一条命令复验。

```bash
# 验：发现 USART1.CR1 的位域宏写错，报告里直接给出下一步
python skills/embedded-register-verify/scripts/verify.py check main.c --chip STM32G431
#   [报] E03 第 42 行：宏 USART_CR1_XXX 对应的位域 XXX 在 USART1.CR1 中不存在
#       下一步：embedded-register-lookup lookup USART1.CR1 --chip STM32G431
```

## 适配范围

| 维度 | 覆盖 |
|---|---|
| 芯片 / 厂商 | 任何有 CMSIS SVD 的芯片：ST、GigaDevice、Nordic、NXP、Renesas、Microchip 等（Keil / cpackget 设备包）；ESP32 系列、RP2040 由 SDK 自带 SVD 自动发现 |
| SVD 来源 | `--svd` 指定 / 项目内扫描（深度 ≤6）/ 环境变量 `ETK_SVD_DIR` / 本机 CMSIS-Pack 缓存 / PlatformIO、Arduino15、ESP-IDF、Pico SDK 自带 SVD |
| 工具链 | Keil MDK、STM32CubeMX、PlatformIO、ESP-IDF、Arduino、Zephyr、nRF Connect SDK 的目录结构；Windows / macOS / Linux；Python 3.10+；24 个零依赖，`schematic-reader` 的 PDF 解析为可选依赖 |
| 代码写法 | CMSIS 结构体与宏、厂商别名、地址别名宏、`HWREG`、C/C++ 与 Arduino；ESP-IDF 风格寄存器宏明确记「未判定」 |

完整写法清单见 [`docs/skills/embedded-register-verify.md`](docs/skills/embedded-register-verify.md)。

## 配置

每个项目可在根目录放 `.etk/config.json`，省去重复参数：

```json
{ "chip": "STM32G431RB", "svd": "tools/svd/STM32G431xx.svd" }
```

- 项目目录里的 `.svd` 会被自动扫描（深度 ≤ 6）
- 解析结果缓存在本机（`%LOCALAPPDATA%\etk\cache` 或 `~/.cache/etk`），SVD 改动后自动失效；`ETK_NO_CACHE=1` 关闭
- 输出格式：默认中文文本；`--format json` 输出统一信封供 Agent 解析；`--format md` 输出 Markdown 表格；`--out 文件` 保存

## 设计约束

- **零运行时依赖**：只使用 Python 3.10+ 标准库，无需 `pip install`。
- **离线**：不联网，不调用任何外部 API。
- **只读**：不修改用户项目文件，写出只发生在 `--out` 指定的路径。
- **不执行被检查的代码**：核验器只做词法分析，不 `eval`、不运行用户代码（仓库质量门会检查）。
- **不内置厂商文件**：SVD 由本机 CMSIS-Pack 或自备文件提供；仅附一份自编的合成演示数据（`--demo`）。
- **每条结论有出处**：`source` 给出文件 / 设备 / 版本，`label` 给出证据等级。

## 开发

```bash
python -m pip install -r requirements-dev.txt

python tools/sync_core.py     # 把 shared/etk_core 同步到各技能（技能必须自带核心库）
python tools/check_repo.py    # 仓库质量门：同步、SKILL.md 规范、3.10 语法、仅标准库、不 eval
python -m pytest -q           # 单元与集成测试

# 真实厂商 SVD 测试（可选）：指向本机 .svd 目录，多个目录用系统路径分隔符连接
ETK_TEST_SVD_DIR=/path/to/svd-dir python -m pytest tests/test_real_svd.py
```

```
shared/etk_core/     共享核心源码（唯一来源）
skills/<技能名>/     每个技能一个文件夹：SKILL.md、scripts/（含 etk_core 副本）、references/
tools/               同步与质量检查工具
tests/               单元测试、合成夹具、触发评测用例（tests/trigger/）
benchmarks/          真实样本核对记录与基准数据
docs/skills/         各技能的详细能力说明
.claude-plugin/      Claude Code 插件与市场清单
```

改动 `shared/etk_core` 后必须运行 `python tools/sync_core.py`，否则质量门失败。

贡献流程、质量门检查项与新增技能的步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)；版本变更见
[CHANGELOG.md](CHANGELOG.md)。

## 限制

- SVD 质量由厂商决定。发现错误时以手册为准，并在 issue 中反馈。
- 已在 ST（STM32G431）、Nordic（nRF52840）、GigaDevice（GD32F3x0）三家 SVD 上完成逐项对照验证，其他厂商待补。
- 不覆盖引脚复用（AF 表）、时钟树、手册勘误、外挂器件命令。
- 触发评测尚未覆盖 Trae CN / WorkBuddy / Codex / Cursor。

## 路线图

按阶段门推进：接线排障、原理图审查官。

## 许可

MIT。厂商 SVD 文件的版权归原厂商所有，本仓库不包含这些文件。
