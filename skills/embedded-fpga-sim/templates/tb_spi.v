// SPI 收发 testbench 模板（CS 时序 + 采样沿 + 回环断言 + 边界数据 00/FF）
// 断言口径：模式 0 主机在 SCLK 上升沿采样；从机回环输出上一字节（MSB 先出），
// 所以第 2/3 字节期间每个采样沿 miso 必须 === 上一字节的同位。
`timescale 1ns/1ps
module tb_spi;
    reg clk = 0, cs = 1, sclk = 0, mosi = 0;
    wire miso;
    always #5 clk = ~clk;
    spi_slave dut (.clk(clk), .cs(cs), .sclk(sclk), .mosi(mosi), .miso(miso));

    integer errs = 0;

    // check=1 时逐位校验回环：主机采样沿上 miso 必须等于 echo 的同位
    task send_byte(input [7:0] d, input check, input [7:0] echo);
        integer i;
        begin
            cs = 0;
            for (i = 7; i >= 0; i = i - 1) begin
                mosi = d[i];
                #10 sclk = 1;   // 上升沿：主机采样 mosi；同沿核对回环 miso
                #1;
                if (check && miso !== echo[i]) begin
                    $display("FAIL: bit%0d miso=%b 期望 %b（回环字节 %h）", i, miso, echo[i], echo);
                    errs = errs + 1;
                end
                #9 sclk = 0;
            end
            cs = 1;
        end
    endtask

    initial begin
        repeat (3) @(negedge clk);
        send_byte(8'hA5, 0, 8'h00);   // 首字节：从机没有上一字节可回环，不校验
        send_byte(8'h00, 1, 8'hA5);   // 发全 0 边界数据；回环应输出上一字节 A5
        send_byte(8'hFF, 1, 8'h00);   // 发全 1 边界数据；回环应输出上一字节 00
        if (errs == 0)
            $display("PASS: 三字节回环全对（A5->00->FF，采样沿/CS 包络/MSB 先出已断言）");
        $finish;
    end
    initial begin #100_000; $display("FAIL: timeout"); $finish; end
    initial begin $dumpfile("tb_spi.vcd"); $dumpvars(0, tb_spi); end
endmodule
