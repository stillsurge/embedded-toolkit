# 嵌入式开发工具箱（embedded-toolkit）

[![ci](https://github.com/stillsurge/embedded-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/stillsurge/embedded-toolkit/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/stillsurge/embedded-toolkit?label=release)](https://github.com/stillsurge/embedded-toolkit/releases)
[![license](https://img.shields.io/github/license/stillsurge/embedded-toolkit)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](#设计约束)

给 AI 编程助手用的嵌入式技能包。五个技能，一条主线：**AI 负责写得快，工具箱负责验得对**。

> Evidence-first embedded dev skills for AI coding agents — register lookup & code verification from CMSIS-SVD,
> debug decision trees, peripheral pitfall lists and one-shot timing calculations.
> Offline, every answer cites its source.

## 为什么需要它

模型会把不存在的位名编得很像真的：`USART_CR1_XXX`、超过字段宽度的值、没开时钟就写的寄存器。这类错误
编译能过、跑起来才发现外设不动，排查成本高。

这五个技能把"查证"变成可执行命令：结论离线算出，每条带 `source`（文件 / 设备 / 版本）与 `label`（证据等级）。

## 五个技能

| 技能 | 一句话 | 版本 | 实测证据 |
|---|---|---|---|
| **寄存器百事通**<br>`embedded-register-lookup` | 查寄存器 / 位域 / 复位值 / 中断号；地址反查、值解码、宏生成、双芯片对比 | 1.11.1 | 19 家厂商 SVD 冒烟 |
| **寄存器核验器**<br>`embedded-register-verify` | 核验 C/C++ 里的寄存器写入，按「报 / 未判定 / 通过」分桶 | 1.16.2 | 注入集召回 229/229；9 个真实 SDK 0 误报 |
| **排障决策树**<br>`embedded-debug-trees` | 12 棵树 77 节点，先取证再判断，不直接开药 | 1.3.1 | 检索评测 CI 强制 |
| **外设避坑清单**<br>`embedded-peripheral-pitfalls` | 25 类外设 148 个配置坑，每坑 = 症状 + 对策 | 1.2.1 | 检索评测 CI 强制 |
| **时序计算器**<br>`embedded-timing-calc` | 37 个计算器，结果回显公式与合法性依据 | 1.1.1 | demo 自检通过 |

逐技能的规则、覆盖写法与实测记录见 [`docs/skills/`](docs/skills/)。

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

```bash
# Claude Code（插件市场）
/plugin marketplace add stillsurge/embedded-toolkit
/plugin install embedded-toolkit@embedded-toolkit

# 其他 Agent（Agent Skills 标准）
npx skills add stillsurge/embedded-toolkit
```

也可以把 `skills/<技能名>/` 整个文件夹复制到该 Agent 的技能目录（如 `.agents/skills/`、`.trae/skills/`），
或按技能页导入。每个技能自带所需的 `etk_core` 副本，不需要额外安装。

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
| 工具链 | Keil MDK、STM32CubeMX、PlatformIO、ESP-IDF、Arduino、Zephyr、nRF Connect SDK 的目录结构；Windows / macOS / Linux；Python 3.10+，零依赖、离线 |
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

## 限制

- SVD 质量由厂商决定。发现错误时以手册为准，并在 issue 中反馈。
- 已在 ST（STM32G431）、Nordic（nRF52840）、GigaDevice（GD32F3x0）三家 SVD 上完成逐项对照验证，其他厂商待补。
- 不覆盖引脚复用（AF 表）、时钟树、手册勘误、外挂器件命令。
- 触发评测尚未覆盖 Trae CN / WorkBuddy / Codex / Cursor。

## 路线图

按阶段门推进：接线排障、原理图审查官。

## 许可

MIT。厂商 SVD 文件的版权归原厂商所有，本仓库不包含这些文件。
