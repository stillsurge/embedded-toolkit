// 参考实现（最小可综合）：同步 FIFO，DEPTH 深度，标准满/空判定（不覆盖旧数据）
// testbench 用它验证四状态：空读/满写/同时读写/满写不覆盖
`timescale 1ns/1ps
module fifo #(
    parameter DEPTH = 8,
    parameter WIDTH = 8,
    parameter AW = $clog2(DEPTH)
) (
    input  wire             clk,
    input  wire             rst_n,
    input  wire             wr_en,
    input  wire [WIDTH-1:0] wr_data,
    input  wire             rd_en,
    output wire [WIDTH-1:0] rd_data,
    output wire             full,
    output wire             empty
);
    reg [WIDTH-1:0] mem [0:DEPTH-1];
    reg [AW:0] wptr = 0, rptr = 0;   // 多一位用于满/空区分

    assign full  = (wptr[AW] != rptr[AW]) && (wptr[AW-1:0] == rptr[AW-1:0]);
    assign empty = (wptr == rptr);
    assign rd_data = mem[rptr[AW-1:0]];

    always @(posedge clk) begin
        if (!rst_n) begin
            wptr <= 0;
            rptr <= 0;
        end else begin
            // 满=丢弃新写入（testbench 状态 3 核对此约定）
            if (wr_en && !full)
                mem[wptr[AW-1:0]] <= wr_data;
            if (wr_en && !full)
                wptr <= wptr + 1'b1;
            if (rd_en && !empty)
                rptr <= rptr + 1'b1;
        end
    end
endmodule
