* SPICE path sim
.include /home/lunarch/pdk-env/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice
.lib tt
.include /home/lunarch/pdk-env/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice
VDD vdd 0 1.8
VGND gnd 0 0
VPB vpb 0 1.8
VNB vnb 0 0
Vin _0794_ 0 PWL(0 0 1n 1.8 2n 1.8)
X0 dp_rf_rf_4__1_ dp_rf_rf_5__1_ net1219 gnd gnd vdd vdd _0794_ sky130_fd_sc_hd__mux2_2
X1 dp_rf_rf_1__1_ net1182 _0794_ net1181 net1214 gnd gnd vdd vdd _0795_ sky130_fd_sc_hd__a221o_1
X2 dp_rf_rf_0__1_ net1109 _0795_ net1118 gnd gnd vdd vdd _0796_ sky130_fd_sc_hd__a22oi_1
X3 net1112 _0792_ _0793_ _0796_ gnd gnd vdd vdd _0797_ sky130_fd_sc_hd__a31oi_1
X4 _0785_ _0790_ _0797_ net1097 gnd gnd vdd vdd _0798_ sky130_fd_sc_hd__a22o_1
X5 net1105 _0776_ _0779_ _0798_ _0805_ gnd gnd vdd vdd _0149_ sky130_fd_sc_hd__a311oi_2
X6 _0149_ gnd gnd vdd vdd net986 sky130_fd_sc_hd__buf_4
X7 net986 gnd gnd vdd vdd net985 sky130_fd_sc_hd__buf_4
X8 net985 net1092 _3641_ gnd gnd vdd vdd dp_pcimm_a_1_ sky130_fd_sc_hd__o21ai_0
X9 dp_memsrcmux_d1_1_ dp_pcimm_a_1_ gnd gnd vdd vdd _0178_ _0163_ sky130_fd_sc_hd__ha_1
X10 _0002_ _0163_ _0178_ gnd gnd vdd vdd _3293_ sky130_fd_sc_hd__a21o_1
X11 _0186_ _3293_ _0185_ gnd gnd vdd vdd _3294_ sky130_fd_sc_hd__a21oi_1
X12 _3292_ _3294_ _0168_ gnd gnd vdd vdd _3295_ sky130_fd_sc_hd__o21bai_1
X13 _0021_ _3295_ _0020_ gnd gnd vdd vdd _3296_ sky130_fd_sc_hd__a21o_1
X14 _0023_ _3296_ _0022_ gnd gnd vdd vdd _3297_ sky130_fd_sc_hd__a21oi_1
X15 _3297_ _3299_ _3303_ gnd gnd vdd vdd _3304_ sky130_fd_sc_hd__o21ai_0
X16 _3304_ gnd gnd vdd vdd net816 sky130_fd_sc_hd__buf_4
X17 net816 _3308_ _3311_ _3312_ gnd gnd vdd vdd _3313_ sky130_fd_sc_hd__o211ai_1
X18 _3313_ gnd gnd vdd vdd net808 sky130_fd_sc_hd__buf_4
X19 net808 _3315_ _3316_ _3317_ gnd gnd vdd vdd _3318_ sky130_fd_sc_hd__a31oi_1
X20 _0196_ _0011_ _0009_ _3318_ _3321_ gnd gnd vdd vdd _3322_ sky130_fd_sc_hd__a41oi_1
X21 _3322_ _3323_ _3324_ _3325_ gnd gnd vdd vdd _3326_ sky130_fd_sc_hd__a211oi_1
X22 _3237_ _3326_ _3708_ _0007_ _0006_ gnd gnd vdd vdd _3709_ sky130_fd_sc_hd__a221o_1
X23 _0198_ _3709_ _0197_ gnd gnd vdd vdd _3710_ sky130_fd_sc_hd__a21oi_1
X24 _3707_ _3710_ gnd gnd vdd vdd _3711_ sky130_fd_sc_hd__xnor2_1
X25 _3478_ _3704_ _3711_ _3476_ gnd gnd vdd vdd _3737_ sky130_fd_sc_hd__a22oi_1
X26 net760 _3737_ gnd gnd vdd vdd dp_result2_31_ sky130_fd_sc_hd__nand2_1
X27 dp_result2_31_ gnd gnd vdd vdd net751 sky130_fd_sc_hd__buf_4
clknet clk 0 0
.tran 1p 3n
.ic v(_0794_)=0
.control
run
meas tran tin WHEN v(_0794_)=0.9
meas tran tout WHEN v(net751)=0.9
meas tran tdelay param='tout-tin'
.endc
.end
