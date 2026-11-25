// 参考实现（最小可综合）：UART 发送端，8N1（1 起始位 + 8 数据 LSB 先 + 1 停止位）
// 用法：busy=0 时 start 置一拍发起；BIT_CYC = CLK_HZ/BAUD 取整——选 CLK_HZ 为 BAUD 整数倍避免量化误差
// testbench 用它验证回环逐字节断言 + 边界数据（00/FF）
`timescale 1ns/1ps
module uart_tx #(
    parameter CLK_HZ = 1_000_000,
    parameter BAUD   = 100_000
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,    // busy=0 时置一拍发起
    input  wire [7:0] data,
    output reg        tx = 1'b1,
    output wire       busy
);
    localparam BIT_CYC = CLK_HZ / BAUD;   // 每位时钟数
    reg [3:0]  cnt_bit = 0;               // 0=空闲 1..8=数据位 9=停止位
    reg [15:0] cnt_div = 0;
    reg [7:0]  sh = 0;
    assign busy = (cnt_bit != 0);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cnt_bit <= 0; cnt_div <= 0; sh <= 0; tx <= 1'b1;
        end else if (cnt_bit == 0) begin
            tx <= 1'b1;
            if (start) begin
                sh <= data; cnt_bit <= 1; cnt_div <= 0;
                tx <= 1'b0;                    // 起始位
            end
        end else if (cnt_div == BIT_CYC - 1) begin
            cnt_div <= 0;
            if (cnt_bit == 9) begin
                cnt_bit <= 0; tx <= 1'b1;      // 停止位段结束回空闲
            end else begin
                cnt_bit <= cnt_bit + 1;
                tx <= sh[0];                   // 数据位 LSB 先出——8 个数据段各出 1 位
                sh <= sh >> 1;
            end
        end else begin
            cnt_div <= cnt_div + 1;
        end
    end
endmodule
