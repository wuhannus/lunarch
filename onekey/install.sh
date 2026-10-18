#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# lunarch — one-key installer for the AI-driven RTL -> GDS flow (slide 7)
#
#   curl -fsSL https://raw.githubusercontent.com/wuhannus/lunarch/main/onekey/install.sh | bash
#
# It encodes the same 10 steps the AI agent executed:
#   toolchain -> 1_synth -> 2_floorplan -> 3_place -> 4_cts -> 5_route
#   -> 6_finish -> sign-off (DRC/LVS) -> optimize -> simulate
#
# Requirements: WSL2 / Ubuntu 24.04 (or 22.04), x86-64, >= 30 GB free disk,
#               sudo access. First run builds OpenROAD + Yosys (~30-90 min).
# ---------------------------------------------------------------------------
set -euo pipefail

LUNARCH_HOME="${LUNARCH_HOME:-$HOME/lunarch-flow}"
ORFS_DIR="${ORFS_DIR:-$LUNARCH_HOME/OpenROAD-flow-scripts}"
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 4)}"
DESIGN_CFG="./designs/sky130hd/riscv32i/config.mk"
FLOW_ONLY=0
SKIP_SIGNOFF=0
CLEAN=0

usage() {
  cat <<EOF
lunarch one-key installer

  --flow-only      skip installation/build, only run the flow
  --skip-signoff   skip DRC + LVS
  --clean          clean previous flow results before running
  -t, --threads N  build with N threads (default: nproc)
  -h, --help       show this help

Environment:
  LUNARCH_HOME     install root                (default: \$HOME/lunarch-flow)
  ORFS_DIR         OpenROAD-flow-scripts dir   (default: \$LUNARCH_HOME/OpenROAD-flow-scripts)
  JOBS             build parallelism           (default: nproc)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --flow-only) FLOW_ONLY=1 ;;
    --skip-signoff) SKIP_SIGNOFF=1 ;;
    --clean) CLEAN=1 ;;
    -t|--threads) JOBS="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
  shift
done

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m  OK  %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m  !!  %s\033[0m\n' "$*"; }
die()  { printf '\n\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- preflight
preflight() {
  log "Preflight"
  [[ "$(uname -s)" == "Linux" ]] || die "Linux required (use WSL2 + Ubuntu 24.04 on Windows)."
  command -v sudo >/dev/null || die "sudo is required."
  command -v git  >/dev/null || die "git is required."
  local free_gb
  free_gb=$(df -Pk "$HOME" | awk 'NR==2 {printf "%d", $4/1024/1024}')
  if [[ "$free_gb" -lt 25 ]]; then
    warn "Only ${free_gb} GB free under \$HOME — OpenROAD + PDK need ~30 GB."
  fi
  mkdir -p "$LUNARCH_HOME"
  ok "$(uname -sr)  |  $(nproc) threads  |  ${free_gb} GB free"
}

# ---------------------------------------------------------------- stage 1
install_deps() {
  log "Step 1/10  Toolchain — system dependencies"
  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get update -qq
  sudo apt-get install -y -qq \
    git cmake build-essential bison flex gawk \
    libreadline-dev libffi-dev zlib1g-dev tcl-dev \
    python3 python3-pip python3-venv pkg-config \
    libboost-all-dev libeigen3-dev libspdlog-dev libfmt-dev \
    graphviz xdot >/dev/null
  if ! command -v klayout >/dev/null; then
    sudo apt-get install -y -qq klayout >/dev/null 2>&1 \
      || warn "klayout not available via apt — DRC/LVS will need it (see onekey/README.md)."
  fi
  ok "dependencies installed"
}

# ---------------------------------------------------------------- stage 2
build_tools() {
  log "Step 2/10  Toolchain — OpenROAD Flow Scripts (OpenROAD + Yosys)"
  if [[ ! -d "$ORFS_DIR" ]]; then
    git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git "$ORFS_DIR"
  else
    git -C "$ORFS_DIR" submodule update --init --recursive
  fi

  if [[ -x "$ORFS_DIR/tools/install/OpenROAD/bin/openroad" && \
        -x "$ORFS_DIR/tools/install/yosys/bin/yosys" ]]; then
    ok "OpenROAD + Yosys already built — skipping"
  else
    ( cd "$ORFS_DIR" && sudo ./setup.sh )
    ( cd "$ORFS_DIR" && ./build_openroad.sh --local --threads "$JOBS" )
    ok "OpenROAD + Yosys built"
  fi
}

# ---------------------------------------------------------------- flow
run_flow() {
  log "Step 3/10  Flow — synthesis → floorplan → place → CTS → route → finish"
  # shellcheck disable=SC1091
  source "$ORFS_DIR/env.sh"

  local OPENROAD_EXE="$ORFS_DIR/tools/install/OpenROAD/bin/openroad"
  local YOSYS_EXE="$ORFS_DIR/tools/install/yosys/bin/yosys"
  local KLAYOUT_CMD
  KLAYOUT_CMD="$(command -v klayout || true)"

  cd "$ORFS_DIR/flow"
  if [[ "$CLEAN" == "1" ]]; then
    rm -rf results/sky130hd/riscv32i reports/sky130hd/riscv32i logs/sky130hd/riscv32i
  fi

  make DESIGN_CONFIG="$DESIGN_CFG" \
       OPENROAD_EXE="$OPENROAD_EXE" YOSYS_EXE="$YOSYS_EXE" KLAYOUT_CMD="$KLAYOUT_CMD"

  local R="results/sky130hd/riscv32i/base"
  [[ -f "$R/6_final.gds" ]] && ok "6_final.gds generated" || die "flow did not produce 6_final.gds"

  if [[ "$SKIP_SIGNOFF" == "1" ]]; then
    warn "sign-off skipped (--skip-signoff)"
  else
    log "Step 8/10  Sign-off — DRC + LVS"
    if [[ -z "$KLAYOUT_CMD" ]]; then
      warn "klayout not found — skipping DRC/LVS"
    else
      make DESIGN_CONFIG="$DESIGN_CFG" \
           OPENROAD_EXE="$OPENROAD_EXE" YOSYS_EXE="$YOSYS_EXE" \
           KLAYOUT_CMD="$KLAYOUT_CMD" drc lvs
      ok "DRC / LVS complete"
    fi
  fi

  # ------------------------------------------------------------ artifacts
  local ART="$LUNARCH_HOME/artifacts"
  mkdir -p "$ART"
  cp -f "$R"/6_final.gds "$R"/6_final.def "$R"/6_final.v "$R"/6_final.spef "$ART"/ 2>/dev/null || true
  cp -f reports/sky130hd/riscv32i/base/6_finish.rpt "$ART"/ 2>/dev/null || true
  cp -f "$R"/6_drc.lyrdb "$R"/6_lvs.lvsdb "$ART"/ 2>/dev/null || true
  ok "artifacts -> $ART"
}

# ---------------------------------------------------------------- main
preflight
if [[ "$FLOW_ONLY" == "0" ]]; then
  install_deps
  build_tools
fi
run_flow

log "Done"
cat <<EOF

  Artifacts : $LUNARCH_HOME/artifacts
  ORFS      : $ORFS_DIR
  Re-run    : $(basename "$0") --flow-only

EOF
