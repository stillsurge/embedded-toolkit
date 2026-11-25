// 参考实现（最小可综合）：UART 接收端，8N1
// 要点：起始位下降沿检测后等半位再确认（抗毛刺），数据位中点采样，停止位必须为 1
// 帧错误（停止位=0）丢弃不置 done——testbench 用回环对照验证收发一致
`timescale 1ns/1ps
module uart_rx #(
    parameter CLK_HZ = 1_000_000,
    parameter BAUD   = 100_000
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       rx,
    output reg  [7:0] rx_data = 0,
    output reg        rx_done = 0
);
    localparam BIT_CYC = CLK_HZ / BAUD;
    localparam HALF    = BIT_CYC / 2;
    reg [3:0]  cnt_bit = 0;    // 0=等起始 1..8=数据位 9=停止位
    reg [15:0] cnt_div = 0;
    reg [7:0]  sh = 0;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cnt_bit <= 0; cnt_div <= 0; sh <= 0; rx_done <= 0;
        end else begin
            rx_done <= 0;
            if (cnt_bit == 0) begin
                if (!rx) begin
                    if (cnt_div == HALF - 1) begin
                        if (!rx) begin            // 半位处仍为 0：确认起始位
                            cnt_bit <= 1; cnt_div <= 0; sh <= 0;
                        end else begin
                            cnt_div <= 0;         // 毛刺，放弃
                        end
                    end else begin
                        cnt_div <= cnt_div + 1;
                    end
                end else begin
                    cnt_div <= 0;
                end
            end else if (cnt_div == BIT_CYC - 1) begin
                cnt_div <= 0;                     // 之后每个 BIT_CYC 恰是各位中点
                if (cnt_bit < 9) begin
                    sh <= {rx, sh[7:1]};          // 数据位中点采样，LSB 先
                    cnt_bit <= cnt_bit + 1;
                end else begin
                    cnt_bit <= 0;
                    if (rx) begin                 // 停止位=1 才算收完
                        rx_data <= sh;
                        rx_done <= 1'b1;
                    end                           // 停止位=0：帧错误，丢弃
                end
            end else begin
                cnt_div <= cnt_div + 1;
            end
        end
    end
endmodule
