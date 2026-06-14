<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>lunarch — Open-Source Agile AI Chip Architecture</title>
<style>
:root{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#c9d1d9;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--yellow:#d2991d;--red:#f85149;--purple:#a371f7}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;line-height:1.6;padding:2rem}
.container{max-width:1000px;margin:0 auto}
h1{font-size:2rem;margin-bottom:.25rem}
h2{font-size:1.3rem;margin:2rem 0 1rem;padding-bottom:.4rem;border-bottom:1px solid var(--border)}
.subtitle{color:var(--muted);font-size:1.1rem;margin-bottom:2rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:1.25rem;margin:1rem 0}
.badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:.75rem;font-weight:600}
.b-v1{background:#1a3a1a;color:var(--green)}.b-v2{background:#1a1a3a;color:var(--purple)}.b-fut{background:#3a2e0a;color:var(--yellow)}
table{width:100%;border-collapse:collapse;margin:1rem 0}
th,td{padding:.6rem .8rem;text-align:left;border-bottom:1px solid var(--border);font-size:.88rem}
th{color:var(--muted);font-weight:600;font-size:.82rem;white-space:nowrap}
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem}
.hl{border-left:3px solid var(--green);padding:.5rem 1rem;margin:.75rem 0;border-radius:0 6px 6px 0;background:#1a2a1a}
.footer{color:var(--muted);font-size:.8rem;margin-top:3rem;text-align:center}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
</style>
</head>
<body>
<div class="container">

<h1>lunarch</h1>
<p class="subtitle">Lunahan Architecture — AI-assisted design of AI chips.<br>Open-source RISC-V cores from Python to GDS, purpose-built for the agentic AI era.</p>

<div class="card">
  <p><strong>lunarch</strong> (Lunahan Architecture) is an open-source family of RISC-V processor cores designed end-to-end using AI-assisted agile methodology — Python describes the hardware, MLIR compiles it, and an open-source PDK produces physical layouts. The cores span three generations, each targeting a specific optimization goal: baseline validation, memory efficiency, and agentic AI acceleration.</p>
</div>

<h2>Projects</h2>

<div class="grid">
  <div class="card" style="border-top:3px solid var(--green)">
    <h3><span class="badge b-v1">v1.0</span> lunahan_v1</h3>
    <p>Baseline 5-stage RV32IMC core. DFF-based caches. Full Python→MLIR→GDS flow.</p>
    <table>
      <tr><td>Area</td><td>0.056 mm²</td></tr>
      <tr><td>Power</td><td>0.95 mW</td></tr>
      <tr><td>MHz</td><td>100 (max 438)</td></tr>
      <tr><td>Cells</td><td>2,706 (1,224 DFFs)</td></tr>
      <tr><td>ISA</td><td>RV32IMC</td></tr>
    </table>
    <a href="https://github.com/wuhannus/lunahan_v1">→ wuhannus/lunahan_v1</a>
  </div>

  <div class="card" style="border-top:3px solid var(--accent)">
    <h3><span class="badge b-v1">v1.1</span> lunahan_v1_sram</h3>
    <p>SRAM variant. sky130 SRAM macros for caches + regfile. Formal equivalence verified.</p>
    <table>
      <tr><td>Area</td><td>0.020 mm² (−64%)</td></tr>
      <tr><td>Power</td><td>0.94 mW (−1%)</td></tr>
      <tr><td>MHz</td><td>100 (max 234)</td></tr>
      <tr><td>DFFs</td><td>250 (−80%)</td></tr>
      <tr><td>SRAM</td><td>3 macros (9KB)</td></tr>
    </table>
    <a href="https://github.com/wuhannus/lunahan_v1_sram">→ wuhannus/lunahan_v1_sram</a>
  </div>

  <div class="card" style="border-top:3px solid var(--purple)">
    <h3><span class="badge b-v2">v2.0</span> lunahan_v2 "Orion"</h3>
    <p>Agentic AI core. 4 hardware contexts, sparse tensor unit, KV-cache, custom ISA.</p>
    <table>
      <tr><td>Area</td><td>0.176 mm²</td></tr>
      <tr><td>Power</td><td>3.50 mW</td></tr>
      <tr><td>MHz</td><td>100 (max 234)</td></tr>
      <tr><td>Contexts</td><td>4 (1-cycle switch)</td></tr>
      <tr><td>ISA</td><td>RV32IMC + 11 ext</td></tr>
    </table>
    <a href="https://github.com/wuhannus/lunahan_v2">→ wuhannus/lunahan_v2</a>
  </div>
</div>

<h2>Design Philosophy</h2>

<div class="card">
  <p>All three cores share a unified methodology:</p>
  <table>
    <tr><th>Phase</th><th>Tool</th><th>Output</th></tr>
    <tr><td><strong>1. RTL Design</strong></td><td>pyCircuit V5 (Python)</td><td>Hardware described in Python</td></tr>
    <tr><td><strong>2. MLIR Emission</strong></td><td>pycircuit.emit</td><td>.pyc MLIR dialect IR</td></tr>
    <tr><td><strong>3. Compilation</strong></td><td>pycc (LLVM 19 + MLIR)</td><td>Verilog + C++ simulation</td></tr>
    <tr><td><strong>4. Verification</strong></td><td>Golden model + 10 checkers</td><td>ISA compliance, pipeline, timing</td></tr>
    <tr><td><strong>5. Physical Design</strong></td><td>OpenROAD + sky130 PDK</td><td>GDSII, SPEF, STA, DRC, power</td></tr>
    <tr><td><strong>6. Performance</strong></td><td>Cycle-accurate profiler</td><td>IPC, CPI, cache, PPA correlation</td></tr>
  </table>
</div>

<h2>Why "lunarch"?</h2>

<div class="card">
  <p><strong>lunarch</strong> = <strong>Luna</strong> (moon, from 月/lunar — symbol of illumination and constant renewal) + <strong>Arch</strong> (architecture). It stands for:</p>
  <ul>
    <li><strong>L</strong>unahan — the creator's name</li>
    <li><strong>U</strong>nified — one methodology across generations</li>
    <li><strong>N</strong>ext-generation — purpose-built for AI workloads</li>
    <li><strong>A</strong>gile — Python→MLIR→GDS in days, not months</li>
    <li><strong>R</strong>ISC-V — open ISA, no licensing</li>
    <li><strong>C</strong>hips — from architecture to physical layout</li>
    <li><strong>H</strong>ardware-software co-design — SDK + RTL in one repo</li>
  </ul>
</div>

<h2>Roadmap</h2>

<div class="card">
  <table>
    <tr><th>Phase</th><th>Timeline</th><th>Goal</th></tr>
    <tr><td><span class="badge b-v1">v1.x</span></td><td>Done</td><td>Foundation: Python→GDS flow validated, DFF + SRAM variants</td></tr>
    <tr><td><span class="badge b-v2">v2.x</span></td><td>Q3-Q4 2025</td><td>Agentic ISA: hardware context switching, sparse tensor unit</td></tr>
    <tr><td><span class="badge b-fut">v3.x</span></td><td>2026</td><td>NPU co-design: open-source NPU with RISC-V instruction interface</td></tr>
    <tr><td><span class="badge b-fut">v4.x</span></td><td>2027</td><td>Silicon: TinyTapeout/Efabless shuttle, first open-source agentic AI SoC</td></tr>
  </table>
</div>

<h2>Get Started</h2>

<pre><code># Clone the umbrella
git clone https://github.com/wuhannus/lunarch.git

# Explore each core
cd lunahan_v1   # Baseline RISC-V
cd lunahan_v2   # Agentic AI core

# Run physical design
python3 phys/scripts/physical_design.py

# Profile performance
python3 perf/profile_agent.py

# Try the Agent SDK
cd sw && python3 agent_sdk.py</code></pre>

<div class="footer">
  May 2025 · Dr. Han Wu + DeepSeek V4 Pro · MIT License · Open-source agile AI chip architecture<br>
  <a href="https://github.com/wuhannus/lunarch">github.com/wuhannus/lunarch</a>
</div>

</div>
</body>
</html>
