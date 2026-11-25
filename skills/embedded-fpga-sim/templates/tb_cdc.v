// CDC 打两拍同步器模板（两域互质周期技巧）——断言驱动
// 断言：sig_b 脉宽 ≈ sig_a 脉宽（亚稳态未破坏电平传递）、快→慢延迟 ≈ 2 个慢域周期
// 边界：仅限单比特电平信号——多 bit 总线不得逐位打两拍（会撕裂），
//       走格雷码（计数器类）/握手（数据有效类）/异步 FIFO（数据流类）
`timescale 1ns/1ps
module tb_cdc;
    // 两域周期互质（10ns/13ns）——让亚稳态窗口充分暴露
    reg clk_a = 0, clk_b = 0, rst_n = 0;
    reg sig_a = 0;
    wire sig_b;
    always #5  clk_a = ~clk_a;   // 100MHz
    always #6.5 clk_b = ~clk_b;  // ~77MHz 互质

    // DUT：打两拍
    reg [1:0] sync = 0;
    always @(posedge clk_b or negedge rst_n)
        if (!rst_n) sync <= 0; else sync <= {sync[0], sig_a};
    assign sig_b = sync[1];

    // 采样：沿时刻记账
    time t_a_rise = 0, t_a_fall = 0, t_b_rise = 0, t_b_fall = 0;
    always @(posedge sig_a) t_a_rise = $time;
    always @(negedge sig_a) t_a_fall = $time;
    always @(posedge sig_b) t_b_rise = $time;
    always @(negedge sig_b) t_b_fall = $time;

    integer errs = 0;
    initial begin
        $timeformat(-9, 0, " ns", 1);   // 显示口径统一为 ns
        repeat (3) @(negedge clk_a); rst_n = 1;
        // 快域脉宽 ≥ 慢域 2 周期（26ns）——否则慢域采不到
        #30  sig_a = 1;
        #60  sig_a = 0;
        #150;
        // $time 为 timescale 单位整数（本文件 1ns → 值即 ns），判定线按 ns 写
        // 断言 1：脉宽保持——60ns 源脉宽经两拍同步后允许 ±1 个慢域周期（13ns）的相位量化误差
        if (t_b_fall - t_b_rise < 47 || t_b_fall - t_b_rise > 75) begin
            $display("FAIL: sig_b 脉宽 %0d ns，期望 47~75 ns（电平被破坏或慢域丢采）", t_b_fall - t_b_rise);
            errs = errs + 1;
        end
        // 断言 2：快→慢延迟 = 2 个慢域周期（26ns）+ 相位量化偏移（0~13ns）→ 15~40ns 窗
        if (t_b_rise - t_a_rise < 15 || t_b_rise - t_a_rise > 40) begin
            $display("FAIL: 上升延迟 %0d ns，期望 15~40 ns（2 个慢域周期 + 相位量化）", t_b_rise - t_a_rise);
            errs = errs + 1;
        end
        if (t_b_fall - t_a_fall < 15 || t_b_fall - t_a_fall > 40) begin
            $display("FAIL: 下降延迟 %0d ns，期望 15~40 ns", t_b_fall - t_a_fall);
            errs = errs + 1;
        end
        if (errs == 0)
            $display("PASS: 脉宽保持 + 两拍延迟均符合（sig_a 60ns -> sig_b，延迟约 2 个 clk_b）");
        $finish;
    end
    initial begin #1_000_000; $display("FAIL: timeout"); $finish; end
    initial begin $dumpfile("tb_cdc.vcd"); $dumpvars(0, tb_cdc); end
endmodule
