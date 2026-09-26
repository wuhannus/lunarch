#!/bin/bash
# AI-driven PPA sweep: clk_period x ABC_AREA, die pinned to baseline.
cd /home/lunarch/orfs-clean/flow
export PATH=/usr/local/bin:/usr/bin:/bin
export TERM=dumb
export KEPLER_FORMAL_EXE=/home/lunarch/orfs-clean/tools/install/kepler-formal/bin/kepler-formal
export LD_LIBRARY_PATH=/home/lunarch/orfs-clean/tools/install/kepler-formal/lib
SDC=designs/sky130hd/riscv32i/constraint.sdc
CFG=designs/sky130hd/riscv32i/config.mk
R=reports/sky130hd/riscv32i/base
O=results/sky130hd/riscv32i/base
D=/mnt/d/opencode/lunarch/flow/opt/sweep
mkdir -p "$D"
rm -f /home/lunarch/sweep_done.txt
echo "name,clk_ns,abc_area,wns,tns,period_min,fmax_mhz,power_mw,cells,die_um" > "$D/sweep.csv"

cp "$CFG" /home/lunarch/config.mk.bak
sed -i 's/^export CORE_UTILIZATION/#export CORE_UTILIZATION/' "$CFG"

run_make() {
  make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
    OPENROAD_EXE=/usr/local/bin/openroad YOSYS_EXE=/usr/local/bin/yosys \
    KLAYOUT_CMD=/usr/bin/klayout \
    "DIE_AREA=0 0 376.625 376.625" "CORE_AREA=1.38 2.72 375.36 375.36" "$@"
}

collect() {
  local name="$1" clk="$2" area="$3"
  local rpt="$R/6_finish.rpt"
  local wns tns pmin fmax pw cells die
  wns=$(grep -m1 '^wns max' "$rpt" | awk '{print $3}')
  tns=$(grep -m1 '^tns max' "$rpt" | awk '{print $3}')
  pmin=$(grep -m1 'clk period_min' "$rpt" | sed -E 's/.*= *([0-9.]+).*/\1/')
  fmax=$(grep -m1 'clk period_min' "$rpt" | sed -E 's/.*fmax = *([0-9.]+).*/\1/')
  pw=$(awk '/finish report_power/{f=1} f && /^Total/{print $5; exit}' "$rpt")
  cells=$(grep -cE 'sky130_fd_sc_hd__' "$O/6_final.v" 2>/dev/null)
  die=$(grep -m1 '^DIEAREA' "$O/6_final.def" 2>/dev/null | sed -E 's/.*\( ([0-9]+) [0-9]+ \) ;/\1/')
  cp "$rpt" "$D/${name}.rpt"
  echo "${name},${clk},${area},${wns},${tns},${pmin},${fmax},${pw},${cells},${die}" >> "$D/sweep.csv"
  echo "DONE ${name}: wns=${wns} fmax=${fmax} power=${pw}" >> /home/lunarch/sweep_progress.log
}

run_point() {
  local name="$1" clk="$2" area="$3"
  sed -i "s/^set clk_period .*/set clk_period ${clk}/" "$SDC"
  rm -rf "$O"
  run_make ABC_AREA=${area} TNS_END_PERCENT=100 > "$D/${name}.log" 2>&1
  echo "${name} exit=$?" >> "$D/${name}.log"
  collect "$name" "$clk" "$area"
}

run_point p7_delay 7.0 0
run_point p10_delay 10.0 0
run_point p7_area 7.0 1
run_point p10_area 10.0 1

cp /home/lunarch/config.mk.bak "$CFG"
sed -i 's/^set clk_period .*/set clk_period 7.0/' "$SDC"
echo DONE > /home/lunarch/sweep_done.txt
