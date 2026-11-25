// 参考实现（最小可综合）：8 位计数器，TOP 到 0 之间循环计数，en 使能
// testbench 用它验证三状态：复位期=0 / 使能计数 / 冻结不变
`timescale 1ns/1ps
module counter #(parameter TOP = 9) (
    input  wire       clk,
    input  wire       rst_n,   // 低有效同步复位
    input  wire       en,
    output reg  [7:0] cnt
);
    always @(posedge clk) begin
        if (!rst_n)
            cnt <= 8'd0;
        else if (en)
            cnt <= (cnt >= TOP) ? 8'd0 : cnt + 8'd1;
    end
endmodule
