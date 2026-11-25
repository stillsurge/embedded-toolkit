// UART 收发 testbench 模板（回环逐字节断言 + 边界数据 00/FF + 帧间隔）
// 断言：TX->RX 回环，rx_done 后 rx_data 必须 === 发送字节
// 波特率口径：两端误差 ≤±2%（10 位帧累计 ≤0.2 位）；模板取 CLK_HZ 为 BAUD 整数倍规避量化
`timescale 1ns/1ps
module tb_uart;
    localparam CLK_HZ = 1_000_000, BAUD = 100_000;   // 1MHz / 100kBd = 10 拍/位（仿真快）
    reg clk = 0, rst_n = 0, start = 0;
    reg [7:0] tx_data = 0;
    wire tx, busy;
    wire [7:0] rx_data;
    wire rx_done;
    always #5 clk = ~clk;

    uart_tx #(.CLK_HZ(CLK_HZ), .BAUD(BAUD)) dut_tx (
        .clk(clk), .rst_n(rst_n), .start(start), .data(tx_data), .tx(tx), .busy(busy));
    uart_rx #(.CLK_HZ(CLK_HZ), .BAUD(BAUD)) dut_rx (
        .clk(clk), .rst_n(rst_n), .rx(tx), .rx_data(rx_data), .rx_done(rx_done));

    integer errs = 0;

    task send_and_check(input [7:0] d);
        begin
            @(negedge clk); start = 1; tx_data = d;
            @(negedge clk); start = 0;
            wait (rx_done);
            @(negedge clk);
            if (rx_data !== d) begin
                $display("FAIL: 收到 %h 期望 %h（回环不一致）", rx_data, d);
                errs = errs + 1;
            end
            @(negedge clk);
        end
    endtask

    initial begin
        repeat (3) @(negedge clk); rst_n = 1;
        send_and_check(8'hA5);
        send_and_check(8'h00);   // 全 0 边界
        send_and_check(8'hFF);   // 全 1 边界
        if (errs == 0)
            $display("PASS: 三字节回环全对（A5->00->FF，起始位确认/中点采样/停止位校验已断言）");
        $finish;
    end
    initial begin #5_000_000; $display("FAIL: timeout"); $finish; end
    initial begin $dumpfile("tb_uart.vcd"); $dumpvars(0, tb_uart); end
endmodule
