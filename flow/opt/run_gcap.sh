#!/bin/bash
# Two extra p7_area variants limited to low-logical-effort cells.
cd /home/lunarch/orfs-clean/flow
export PATH=/usr/local/bin:/usr/bin:/bin
export TERM=dumb
export KEPLER_FORMAL_EXE=/home/lunarch/orfs-clean/tools/install/kepler-formal/bin/kepler-formal
export LD_LIBRARY_PATH=/home/lunarch/orfs-clean/tools/install/kepler-formal/lib
SDC=designs/sky130hd/riscv32i/constraint.sdc
CFG=designs/sky130hd/riscv32i/config.mk
R=reports/sky130hd/riscv32i/base
O=results/sky130hd/riscv32i/base
D=/mnt/d/opencode/lunarch/flow/opt/paths
rm -f /home/lunarch/gcap_done.txt

cp "$CFG" /home/lunarch/config.mk.bak
sed -i 's/^export CORE_UTILIZATION/#export CORE_UTILIZATION/' "$CFG"
sed -i 's/^set clk_period .*/set clk_period 7.0/' "$SDC"

run_make() {
  make DESIGN_CONFIG=./designs/sky130hd/riscv32i/config.mk \
    OPENROAD_EXE=/usr/local/bin/openroad YOSYS_EXE=/usr/local/bin/yosys \
    KLAYOUT_CMD=/usr/bin/klayout \
    "DIE_AREA=0 0 376.625 376.625" "CORE_AREA=1.38 2.72 375.36 375.36" "$@"
}

for tag in g2 g15; do
  DU=$(cat /mnt/d/opencode/dontuse_${tag}.txt)
  mkdir -p "$D/p7_area_${tag}"
  rm -rf "$O"
  run_make ABC_AREA=1 TNS_END_PERCENT=100 "DONT_USE_CELLS=$DU" \
    > "$D/p7_area_${tag}/run.log" 2>&1
  echo "$tag exit=$?" >> /home/lunarch/gcap_done.txt
  cp "$R/6_finish.rpt" "$D/p7_area_${tag}/6_finish.rpt" 2>/dev/null
  cp "$O/6_final.def" "$D/p7_area_${tag}/6_final.def" 2>/dev/null
  cp "$O/6_final.v" "$D/p7_area_${tag}/6_final.v" 2>/dev/null
  cp "$O/6_final.spef" "$D/p7_area_${tag}/6_final.spef" 2>/dev/null
  cp "$O/6_final.odb" "$D/p7_area_${tag}/6_final.odb" 2>/dev/null
done

cp /home/lunarch/config.mk.bak "$CFG"
sed -i 's/^set clk_period .*/set clk_period 7.0/' "$SDC"
echo ALLDONE >> /home/lunarch/gcap_done.txt
