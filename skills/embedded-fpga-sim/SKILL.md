---
name: embedded-fpga-sim
description: RTL 仿真工作台：通用 testbench 骨架（时钟复位/超时看门狗/VCD dump）、常用模块模板（计数器/FIFO 四状态/CDC 打两拍/SPI·UART 收发）、仿真判读要点（X 态传播/复位完整性/状态机非法态）、Gowin Simulation 注意事项。管综合之前——RTL 功能确认靠仿真，不靠综合后调试。
license: MIT
compatibility: Python 3.10+，仅标准库；仿真需本机安装 Icarus Verilog（iverilog）；不联网、不执行用户代码。
metadata:
  author: fangcun
  version: "1.0.0"
  display_name: FPGA 仿真工作台
  display_name_en: FPGA Simulation Workbench
  examples_zh:
  - 帮我写个 FIFO 的 testbench
  - 这个跨时钟域信号处理对吗
  - 波形上全是 X 态怎么找源头
---

# FPGA 仿真工作台（embedded-fpga-sim）

RTL 写完**先仿真确认功能，再跑综合**——三个阶段（仿真查功能 / 综合查可综合性 / PnR 查时序）
各查各的，跳过任何一个都算欠债。本技能管第一阶段。

## 何时使用

- RTL 模块写完 → 骨架起步写 testbench
- FIFO/CDC/串口这类常见模块 → 直接套模板（四状态全覆盖/互质双时钟技巧已内置）
- 波形上有 X 态/状态机跑飞 → 按判读要点表定位
- Gowin 仿真器配置（仿真库/VCD 大小/PLL 仿真模型）→ 注意事项节



## 可直接复制的 .v 模板文件

`templates/` 下五个 testbench 文件（tb_fifo.v / tb_cdc.v / tb_counter.v / tb_spi.v / tb_uart.v）+ **四个参考 DUT**
（counter.v / fifo.v / spi_slave.v / uart_tx.v+uart_rx.v 收发对，最小可综合实现）——**开箱即跑，断言驱动**：tb 内置 FAIL/PASS 判定
（回环逐位比对、读回顺序核对），打印 PASS 才算过，不是"跑完没报错"就算过：

```bash
# Icarus Verilog 实测通过（Gowin Simulation 同样适用，把参考 DUT 换成你的模块名）
iverilog -g2012 -o sim.vvp templates/tb_fifo.v templates/fifo.v && vvp sim.vvp
iverilog -g2012 -o sim.vvp templates/tb_counter.v templates/counter.v && vvp sim.vvp
iverilog -g2012 -o sim.vvp templates/tb_spi.v templates/spi_slave.v && vvp sim.vvp
iverilog -g2012 -o sim.vvp templates/tb_uart.v templates/uart_tx.v templates/uart_rx.v && vvp sim.vvp
iverilog -g2012 -o sim.vvp templates/tb_cdc.v && vvp sim.vvp   # 自带同步器，无需 DUT
```

各文件内置超时看门狗与 VCD dump；参考 DUT 的行为约定（FIFO 满丢弃新写入、计数器 TOP 回零等）
写在各 .v 文件头注释里——换成你的 DUT 时，先确认约定一致再跑断言。
## 常见翻车链（本技能的定位）

```
仿真过了 → 综合出 latch（组合逻辑 if/else 不完整）→ 时序不收敛
   ↑ 本技能管这里
```

## 模板清单

| 模板 | 覆盖判读要点 |
|---|---|
| 通用骨架 | 时钟复位时序、负沿驱动正沿采样、超时看门狗、VCD dump |
| 计数器/分频器 | 复位清零、off-by-one、使能冻结 |
| FIFO | 空读/满写/同时读写/满写不覆盖旧数据——四状态全覆盖 |
| CDC 打两拍 | 两域互质周期技巧、脉宽 ≥ 慢域 2 周期、延迟固定 2 拍——**仅限单比特电平，多 bit 走格雷码/握手/异步 FIFO** |
| SPI 收发 | 采样沿对齐、回环逐位断言（MSB 先出）、全 0/全 1 边界数据 |
| UART 收发 | 起始位半位确认（抗毛刺）、中点采样、LSB 先出、停止位校验（帧错误丢弃）、回环逐字节断言、波特率误差 ≤±2% |

## 与 fpga-trees 的分工

- `embedded-fpga-sim`（本技能）：**综合之前**——功能对不对
- `embedded-fpga-trees`：**综合之后**——排障决策树/日志解析/时序报告/约束审查

两个都装 = 仿真到时序的全流程；只装本技能 = 管好"烧板子之前"。
