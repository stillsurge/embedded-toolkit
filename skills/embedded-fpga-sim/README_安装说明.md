# FPGA 仿真工作台（embedded-fpga-sim）

**RTL 写完先仿真确认功能，再跑综合——仿真查功能、综合查可综合性、PnR 查时序，三阶段各查各的。**

常见翻车链：仿真过了 → 综合出 latch → 时序不收敛。本技能管第一阶段：testbench 骨架与四个常用模块的现成模板、波形判读要点表、Gowin Simulation 注意事项。

## 它解决什么问题

| 你遇到的 | 它给你的 |
|----------|----------|
| testbench 每次从零写 | 通用骨架（时钟复位/负沿驱动/超时看门狗/VCD dump）直接套 |
| FIFO 的 bug 总在边角状态 | FIFO 模板四状态全覆盖：空读/满写/同时读写/满写不覆盖 |
| 跨时钟域偶发出错 | CDC 打两拍模板 + 两域互质周期技巧让亚稳态窗口暴露（仅单比特；多比特走格雷码/握手） |
| 波形上一片 X 不知道哪来的 | 判读要点表：X 态传播回溯到源头寄存器 |
| Gowin 仿真配置懵 | PLL 仿真模型/仿真库编译/VCD 大小控制注意事项 |

## 模板清单

通用骨架 / 计数器分频器 / FIFO（四状态断言）/ CDC 打两拍（仅单比特）/ SPI 收发（回环断言）/ UART 收发（回环断言）——见 `references/testbench模板与仿真判读.md`。

## 作为 Agent Skill 使用

装进任意支持 Agent Skill 标准的 AI 助手后，直接说人话："帮我写个 FIFO 的 testbench" / "这个跨时钟域信号处理对吗" / "波形上全是 X 态怎么找源头"。

### 包结构

- `SKILL.md` —— 技能说明书（AI 按需读取）
- `references/testbench模板与仿真判读.md` —— 骨架+四模块模板+判读要点+Gowin 注意事项
- `templates/tb_fifo.v / tb_cdc.v / tb_counter.v / tb_spi.v / tb_uart.v` —— 可直接复制的 testbench 文件（内置超时看门狗+VCD dump）
- `templates/counter.v / fifo.v / spi_slave.v / uart_tx.v+uart_rx.v` —— 最小可综合参考 DUT（与 testbench 配套开箱即跑，iverilog 实测通过）

## 定位边界

管**综合之前的功能验证**；综合告警（latch/位宽截断）与时序收敛走 `embedded-fpga-trees`（两 skill 分工：仿真=功能对不对，trees=综合后哪里翻车）；只覆盖 Verilog + Gowin（Xilinx/Altera 不在范围内）。

## 复核方式

模板全部可在本地仿真器复跑：Icarus Verilog（开源）或 Gowin Simulation——把模板贴进工程、接上你的 DUT、跑起来对波形，判读要点表逐条对照。

## 真实输出样例

问：「FIFO 写到满之后数据会丢吗？」

> **看你的设计约定**——判读要点第 3 条：full=1 时写入，检查两件事：
> 1. 写指针是否不动（不覆盖旧数据）
> 2. 有无溢出标志置位
> `templates/tb_fifo.v` 四状态断言直接复用：空读不动指针 → 写满断言 full → 满写断言写指针不动 → 同拍读写弹 1 弃 1 → 读回全序列核对（证明旧数据未被覆盖）。
> 【模板约定为"满后丢弃新写入"——若要"覆盖最旧"，改写指针逻辑后重跑四状态】

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-11-04 | 首发：通用骨架+四模块模板（计数器/FIFO/CDC/串口）+判读要点表+Gowin 注意事项 |
