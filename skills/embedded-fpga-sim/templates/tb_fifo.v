// FIFO testbench 四状态模板（空读/满写丢弃/同时读写/读回核对）——断言驱动
// 行为约定（fifo.v 头注释）：满=丢弃新写入；读回核对证明旧数据未被覆盖
`timescale 1ns/1ps
module tb_fifo;
    localparam DEPTH = 8, WIDTH = 8;
    reg clk = 0, rst_n = 0;
    reg wr_en = 0, rd_en = 0;
    reg [WIDTH-1:0] wr_data = 0;
    wire [WIDTH-1:0] rd_data;
    wire full, empty;
    always #5 clk = ~clk;

    fifo #(.DEPTH(DEPTH), .WIDTH(WIDTH)) dut (.*);

    integer errs = 0;
    reg [WIDTH-1:0] exp;

    initial begin
        repeat (3) @(negedge clk);
        rst_n = 1;
        // 状态1：空读——读指针不得移动，empty 保持
        @(negedge clk); rd_en = 1;
        @(negedge clk); rd_en = 0;
        if (dut.rptr !== 0) begin $display("FAIL: 空读挪动了读指针 rptr=%0d", dut.rptr); errs = errs + 1; end
        if (empty !== 1'b1) begin $display("FAIL: 空读后 empty=%b", empty); errs = errs + 1; end
        // 状态2：写满 1..8，full 必须置位
        repeat (DEPTH) begin
            @(negedge clk); wr_en = 1; wr_data = wr_data + 1;
        end
        @(negedge clk); wr_en = 0;
        if (full !== 1'b1) begin $display("FAIL: 写满 %0d 个后 full 未置位", DEPTH); errs = errs + 1; end
        // 状态3：满写 EE——写指针不得动（丢弃新写入）
        @(negedge clk); wr_en = 1; wr_data = 8'hEE;
        @(negedge clk); wr_en = 0;
        if (dut.wptr !== DEPTH) begin $display("FAIL: 满写推进了写指针 wptr=%0d", dut.wptr); errs = errs + 1; end
        // 状态4：同时读写——弹出一个（rptr 推进），FF 同拍写入应被丢弃
        @(negedge clk); wr_en = 1; rd_en = 1; wr_data = 8'hFF;
        @(negedge clk); wr_en = 0; rd_en = 0;
        if (dut.wptr !== DEPTH) begin $display("FAIL: 满时同拍写被接受 wptr=%0d", dut.wptr); errs = errs + 1; end
        if (dut.rptr !== 1) begin $display("FAIL: 同时读写未弹出 rptr=%0d", dut.rptr); errs = errs + 1; end
        // 读回核对：剩余 7 个必须还是 2..8 原序——证明 EE/FF 都没写进去
        for (exp = 2; exp <= DEPTH; exp = exp + 1) begin
            @(negedge clk); rd_en = 1; #1;
            if (rd_data !== exp) begin
                $display("FAIL: 读到 %h 期望 %h（旧数据被覆盖）", rd_data, exp);
                errs = errs + 1;
            end
            @(posedge clk); #1 rd_en = 0;
        end
        @(negedge clk);
        if (empty !== 1'b1) begin $display("FAIL: 读完后 empty=%b", empty); errs = errs + 1; end
        if (errs == 0)
            $display("PASS: 四状态全过（空读不动指针 / 满写丢弃 / 同读写弹1弃1 / 读回 2..%0d 原序一致）", DEPTH);
        $finish;
    end
    initial begin #100_000; $display("FAIL: timeout"); $finish; end
    initial begin $dumpfile("tb_fifo.vcd"); $dumpvars(0, tb_fifo); end
endmodule
