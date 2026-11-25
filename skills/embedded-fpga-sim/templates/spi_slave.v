// 参考实现（最小可综合）：SPI 从机，模式 0（CPOL=0/CPHA=0），8bit
// 接收：SCLK 上升沿采样，第 8 拍（bit_cnt==7）锁存完整字节到 rx_last
// 发送：回环对照——negedge cs 载入上一字节，negedge sclk 移位 MSB 先出
// （clk 端口保留兼容；SCLK 域与系统时钟域的同步简化不做，仅功能验证）
// testbench 用它验证 CS 时序 + 采样沿 + 回环断言 + 边界数据（00/FF）
`timescale 1ns/1ps
module spi_slave (
    input  wire      clk,     // 系统时钟（本模板未使用，端口保留）
    input  wire      cs,      // 低有效片选
    input  wire      sclk,
    input  wire      mosi,
    output wire      miso
);
    reg [7:0] shift_rx = 0;
    reg [2:0] bit_cnt  = 0;
    reg [7:0] rx_last  = 0;
    reg [7:0] tx       = 0;

    // 接收：bit_cnt==7 时是第 8 拍，此刻 {shift_rx[6:0], mosi} 即完整字节
    always @(posedge sclk or posedge cs) begin
        if (cs) begin
            bit_cnt <= 0;
        end else begin
            shift_rx <= {shift_rx[6:0], mosi};
            bit_cnt  <= bit_cnt + 1;
            if (bit_cnt == 3'd7)
                rx_last <= {shift_rx[6:0], mosi};
        end
    end

    // 发送（回环）：片选拉低载入上一字节，每个 SCLK 下降沿左移，MSB 先出
    always @(negedge cs)  tx <= rx_last;
    always @(negedge sclk) if (!cs) tx <= {tx[6:0], 1'b0};
    assign miso = (cs) ? 1'b0 : tx[7];
endmodule
