# Testbench 模板与仿真判读要点（Gowin / 通用 Verilog）

> 仿真在综合**之前**——RTL 写完先仿真确认功能，再跑综合。本模板给常见模块的
> testbench 骨架与判读要点，配套 Gowin Simulation（基于 Yosys+Verilator 或 Icarus）。

---

## 一、通用 testbench 骨架

```verilog
`timescale 1ns / 1ps

module tb_<模块名>;

    // 1. 时钟与复位
    reg clk = 0;
    reg rst_n = 0;
    always #5 clk = ~clk;          // 100MHz（周期 10ns，按实际改）

    // 2. 被测模块（DUT）端口连线
    <DUT 例化>

    // 3. 激励
    initial begin
        // 复位时序：上电保持复位 ≥2 个时钟周期，在时钟下降沿释放
        repeat (3) @(negedge clk);
        rst_n = 1;
        // 激励序列（按模块功能填）
        repeat (20) @(negedge clk);
        $finish;
    end

    // 4. 超时看门狗——防仿真挂死
    initial begin
        #1_000_000;                // 1ms 仿真超时
        $display("FAIL: simulation timeout");
        $finish;
    end

    // 5. 波形 dump（Gowin Simulation / 通用 VCD）
    initial begin
        $dumpfile("tb_<模块名>.vcd");
        $dumpvars(0, tb_<模块名>);   // 0 = 全层级
    end
endmodule
```

**骨架要点**：
- 激励全部用 `@(negedge clk)` 对齐——负沿驱动、正沿采样，避免竞态
- **必须有超时看门狗**——组合环路写错时仿真永不结束
- 复位释放沿与时钟沿对齐，异步释放同步化

---

## 二、常用模块 testbench 模板

### 2.1 计数器 / 分频器

```verilog
// 判读要点：
// 1. 计数值在复位后从 0 开始
// 2. 计到 TOP 值后回 0（或翻转输出）——检查 off-by-one
// 3. 使能信号无效时计数值冻结（不自增）
initial begin
    // rst_n 从 0 起保持——直接查值，不要 @(negedge rst_n)（rst_n 起始即 0，等不到沿会挂死）
    @(negedge clk);
    if (cnt !== 0) $display("FAIL: cnt not 0 during reset = %d", cnt);
    rst_n = 1;                  // 下降沿（时钟负沿）释放复位
    repeat (5) @(negedge clk);  // 释放后数 5 拍
    if (cnt !== 5) $display("FAIL: cnt after 5 clk = %d, expect 5", cnt);
end
```

### 2.2 FIFO

```verilog
// 判读要点（四状态全覆盖——漏一个状态就是潜在 bug）：
// 1. 空读：empty=1 时读——读指针不动，不允许出 X
// 2. 正常读写：写 N 个读 N 个，数据顺序一致
// 3. 满写：full=1 时写——写指针不动（按约定丢弃新写入），不允许覆盖旧数据
// 4. 同时读写（非空非满）：读写指针独立推进
// 读回核对是关键——满写后把剩余数据全部读出比对，才能证明旧数据没被覆盖：
task test_fifo_full;
    integer i;
    reg [7:0] exp;
    begin
        // 写满
        repeat (DEPTH) begin
            @(negedge clk); wr_en = 1; wr_data = wr_data + 1;
        end
        @(negedge clk); wr_en = 0;
        if (!full) $display("FAIL: full not asserted after %0d writes", DEPTH);
        // 满状态下再写一次——写指针不得动（丢弃新写入）
        @(negedge clk); wr_en = 1; wr_data = 8'hEE;
        @(negedge clk); wr_en = 0;
        if (dut.wptr !== DEPTH) $display("FAIL: 满写推进了写指针（EE 被接受）");
        // 同时读写：弹出一个，同拍写入应被丢弃
        @(negedge clk); wr_en = 1; rd_en = 1; wr_data = 8'hFF;
        @(negedge clk); wr_en = 0; rd_en = 0;
        // 读回核对：剩余数据必须还是 2..DEPTH 原序——证明 EE/FF 都没写进去
        for (exp = 2; exp <= DEPTH; exp = exp + 1) begin
            @(negedge clk); rd_en = 1; #1;
            if (rd_data !== exp) $display("FAIL: 读到 %h 期望 %h（旧数据被覆盖）", rd_data, exp);
            @(posedge clk); #1 rd_en = 0;
        end
        if (!empty) $display("FAIL: 读完后未空");
    end
endtask
```

### 2.3 跨时钟域（CDC）——打两拍同步器

```verilog
// 判读要点（CDC 是仿真最难抓的，重点看这四条）：
// 1. 电平信号跨域后，目的域采样到的值稳定（无毛刺）
// 2. 打两拍后延迟固定为 2 个目的域时钟周期——用于时序预算
// 3. 快→慢域：源信号脉宽必须 ≥ 慢域 2 个周期（否则慢域采不到）
// 4. 边界：打两拍只管单比特电平——多 bit 总线逐位打两拍会撕裂，
//    必须走格雷码（计数器类）/握手（数据有效类）/异步 FIFO（数据流类）
// 仿真技巧：两域时钟周期故意取互质关系（如 10ns/13ns），让亚稳态窗口充分暴露
reg [1:0] sync_ff = 0;
always @(posedge clk_dst or negedge rst_n) begin
    if (!rst_n) sync_ff <= 0;
    else        sync_ff <= {sync_ff[0], signal_src};  // 打两拍
end
wire signal_dst = sync_ff[1];
```

### 2.4 串行接口（SPI/UART）收发

```verilog
// SPI 判读要点：
// 1. 发送时序：CS 拉低 → 时钟沿与数据变化对齐（SPI 采样沿前数据稳定）→ CS 拉高
// 2. 回环断言：从机输出"上一收到的字节"时逐位比对（MSB 先出）——不带断言的 SPI tb 只是空转
// 3. 全 0x00 / 全 0xFF 边界数据——掩掉"看起来对"的默认值
task spi_send_byte(input [7:0] d);
    integer i;
begin
    @(negedge clk); cs = 0;
    for (i = 7; i >= 0; i = i - 1) begin
        @(negedge clk); mosi = d[i];
        @(negedge clk); sclk = 1;   // 采样沿
        @(negedge clk); sclk = 0;
    end
    @(negedge clk); cs = 1;
end
endtask
```

**UART 侧模板**：`templates/tb_uart.v + uart_tx.v + uart_rx.v` 开箱即跑（回环逐字节断言：A5/00/FF）。
判读要点：

1. **起始位抗毛刺**：下降沿检测后等半位再确认仍为 0 才起始——直接置位计数会被线路毛刺触发
2. **中点采样**：确认起始位后每过一个 BIT_CYC 恰好是各位中点，建立裕量最大化
3. **数据 LSB 先出；停止位必须为 1**——停止位为 0 按帧错误丢弃（模板 UART RX 如此处理），比静默收错数据安全
4. **波特率误差 ≤±2%**（10 位帧累计 ≤0.2 位偏差）；`BIT_CYC = CLK_HZ/BAUD` 取整有量化损耗——选 CLK_HZ 为 BAUD 整数倍规避

---

## 三、仿真判读要点（波形通用）

| 检查项 | 方法 |
|---|---|
| 复位完整性 | 复位期间所有寄存器输出 = 复位值（波形上一条平线，无 X） |
| 未初始化信号（X 态传播） | 波形上**红色/未知态**——任何 X 传播到输出都是 bug（找到源头寄存器） |
| 建立保持 | 时钟沿前后数据是否在窗口内稳定（Gowin 时序报告管综合后，仿真只管功能） |
| 计数/状态机 | 状态机转到非法状态（default 分支）→ 缺 state 保护 |
| 数据完整性 | 写读序列比对（task 自动比对优于肉眼看波形） |
| 死循环/挂死 | 超时看门狗触发 = 组合环路或握手死锁 |

---

## 四、Gowin Simulation 注意事项

1. **仿真器选择**：Gowin 支持 Icarus Verilog（开源）与内置仿真器——工程里固定一种，避免结果差异
2. **仿真库**：用到 Gowin 原语（BSRAM/PLL/DLL）时需编译器件仿真库（`gowin/lib/` 下），纯 RTL 模块不用
3. **PLL/DLL 仿真**：锁相环在仿真中需要配置仿真模型参数（相位/频率对齐要等锁定信号），锁定前输出无意义
4. **VCD 文件**：大设计 dump 全信号会 GB 级——只 dump 关注层级 `$dumpvars(1, tb_top)`

---

## 五、仿真通过 ≠ 综合通过（两个阶段查不同的事）

| 阶段 | 查什么 | 工具 |
|---|---|---|
| 仿真 | **功能对不对**（逻辑行为） | testbench + VCD |
| 综合 | **可综合性**（latch 推断/位宽截断告警） | Gowin 综合 log |
| PnR | **时序收敛**（WNS/TNS） | 时序报告 |

常见翻车链：仿真过了 → 综合出 latch（组合逻辑不完整 if/else）→ 时序不收敛。
三个阶段各查各的，跳过任何一个都算欠债。
