// Parameterised Kogge-Stone parallel-prefix adder (log-depth).
module ks_adder #(
    parameter W = 33
) (
    input  [W-1:0] a,
    input  [W-1:0] b,
    input          cin,
    output [W-1:0] sum
);
    localparam L = $clog2(W);
    wire [W-1:0] g0 = a & b;
    wire [W-1:0] p0 = a ^ b;

    wire [W-1:0] G [0:L];
    wire [W-1:0] P [0:L];
    assign G[0] = g0;
    assign P[0] = p0;

    genvar i, lvl;
    generate
        for (lvl = 1; lvl <= L; lvl = lvl + 1) begin : lvl_gen
            for (i = 0; i < W; i = i + 1) begin : bit_gen
                if (i >= (1 << (lvl - 1))) begin : has_pred
                    assign G[lvl][i] = G[lvl-1][i] | (P[lvl-1][i] & G[lvl-1][i-(1<<(lvl-1))]);
                    assign P[lvl][i] = P[lvl-1][i] & P[lvl-1][i-(1<<(lvl-1))];
                end else begin : no_pred
                    assign G[lvl][i] = G[lvl-1][i];
                    assign P[lvl][i] = P[lvl-1][i];
                end
            end
        end
    endgenerate

    wire [W:0] c;
    assign c[0] = cin;
    assign c[W:1] = G[L] | (P[L] & {W{cin}});
    assign sum = p0 ^ c[W-1:0];
endmodule
