// 计数器/分频器 testbench 模板
`timescale 1ns/1ps
module tb_counter;
    reg clk = 0, rst_n = 0, en = 0;
    wire [7:0] cnt;
    always #5 clk = ~clk;
    counter #(.TOP(9)) dut (.clk(clk), .rst_n(rst_n), .en(en), .cnt(cnt));

    integer errs = 0;
    initial begin
        // 复位期检查：cnt==0
        @(negedge clk);
        if (cnt !== 0) begin $display("FAIL: 复位期 cnt=%d", cnt); errs = errs + 1; end
        repeat (2) @(negedge clk);
        rst_n = 1;
        // 使能后数 5 拍
        en = 1;
        repeat (5) @(negedge clk);
        if (cnt !== 5) begin $display("FAIL: 5 拍后 cnt=%d, expect 5", cnt); errs = errs + 1; end
        // 冻结检查：en=0 计数停
        en = 0;
        repeat (3) @(negedge clk);
        if (cnt !== 5) begin $display("FAIL: en=0 后 cnt 变了=%d", cnt); errs = errs + 1; end
        if (errs == 0)
            $display("PASS: counter 三状态全过（复位期=0 / 使能计数 / 冻结不变）");
        $finish;
    end
    initial begin #100_000; $display("FAIL: timeout"); $finish; end
    initial begin $dumpfile("tb_counter.vcd"); $dumpvars(0, tb_counter); end
endmodule
