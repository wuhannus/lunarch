#!/bin/bash
# Swap in Kogge-Stone adders and re-run the flow at 5.0 ns (200 MHz target).
cd /home/lunarch/orfs-clean/flow
export PATH=/usr/local/bin:/usr/bin:/bin
export TERM=dumb
export KEPLER_FORMAL_EXE=/home/lunarch/orfs-clean/tools/install/kepler-formal/bin/kepler-formal
export LD_LIBRARY_PATH=/home/lunarch/orfs-clean/tools/install/kepler-formal/lib
SRC=designs/src/riscv32i
SDC=designs/sky130hd/riscv32i/constraint.sdc
CFG=designs/sky130hd/riscv32i/config.mk
R=reports/sky130hd/riscv32i/base
O=results/sky130hd/riscv32i/base
D=/mnt/d/opencode/lunarch/flow/opt/ks
mkdir -p "$D"
rm -f /home/lunarch/ks_done.txt

# ---- swap in Kogge-Stone adders ----
cp "$SRC/alu.v" /home/lunarch/alu.v.orig
cp "$SRC/adder.v" /home/lunarch/adder.v.orig
cp /mnt/d/opencode/ks_adder.v "$SRC/ks_adder.v"
cp /mnt/d/opencode/alu_ks.v "$SRC/alu.v"
cat > "$SRC/adder.v" <<'EOF'
module adder (input [31:0] a, b,
              output [31:0] y);
   ks_adder #(32) u_ks (.a(a), .b(b), .cin(1'b0), .sum(y));
endmodule // adder
EOF

cp "$CFG" /home/lunarch/config.mk.bak
sed -i 's/^export CORE_UTILIZATION/#export CORE_UTILIZATION/' "$CFG"

sed -i 's/^set clk_period .*/set clk_period 5.0/' "$SDC"
rm -rf "$O"
make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
  OPENROAD_EXE=/usr/local/bin/openroad YOSYS_EXE=/usr/local/bin/yosys \
  KLAYOUT_CMD=/usr/bin/klayout \
  "DIE_AREA=0 0 376.625 376.625" "CORE_AREA=1.38 2.72 375.36 375.36" \
  ABC_AREA=0 TNS_END_PERCENT=100 > "$D/ks_5ns.log" 2>&1
echo "KS_EXIT=$?" >> "$D/ks_5ns.log"
cp "$R/6_finish.rpt" "$D/ks_5ns.rpt" 2>/dev/null
grep -m1 '^DIEAREA' "$O/6_final.def" >> "$D/ks_5ns.log" 2>/dev/null

# ---- restore ----
cp /home/lunarch/alu.v.orig "$SRC/alu.v"
cp /home/lunarch/adder.v.orig "$SRC/adder.v"
rm -f "$SRC/ks_adder.v"
cp /home/lunarch/config.mk.bak "$CFG"
sed -i 's/^set clk_period .*/set clk_period 7.0/' "$SDC"
echo DONE > /home/lunarch/ks_done.txt
