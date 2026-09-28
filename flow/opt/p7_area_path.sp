* SPICE path sim
.include /home/lunarch/pdk-env/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice
.lib tt
.include /home/lunarch/pdk-env/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice
VDD vdd 0 1.8
VGND gnd 0 0
VPB vpb 0 1.8
VNB vnb 0 0
Vin _02907_ 0 PWL(0 0 1n 1.8 2n 1.8)
X0 net848 net896 dp_rf_rf_3__0_ gnd gnd vdd vdd _02907_ sky130_fd_sc_hd__nand3_1
X1 _02906_ _02907_ gnd gnd vdd vdd _02908_ sky130_fd_sc_hd__nand2_1
X2 _02908_ net812 gnd gnd vdd vdd _02909_ sky130_fd_sc_hd__nand2_1
X3 _02905_ _02909_ gnd gnd vdd vdd _02910_ sky130_fd_sc_hd__nand2_1
X4 _02910_ net804 gnd gnd vdd vdd _02911_ sky130_fd_sc_hd__nand2_1
X5 _02911_ _02921_ gnd gnd vdd vdd _02922_ sky130_fd_sc_hd__nand2_1
X6 _02922_ gnd gnd vdd vdd _02923_ sky130_fd_sc_hd__inv_1
X7 _02901_ _02923_ gnd gnd vdd vdd _02924_ sky130_fd_sc_hd__nand2_1
X8 _02924_ net800 gnd gnd vdd vdd _02925_ sky130_fd_sc_hd__nand2_1
X9 _02925_ _02969_ gnd gnd vdd vdd dp_alu_a2_0_ sky130_fd_sc_hd__nand2_1
X10 dp_alu_a2_0_ gnd gnd vdd vdd net712 sky130_fd_sc_hd__buf_4
X11 net712 net794 gnd gnd vdd vdd _07440_ sky130_fd_sc_hd__nand2_1
X12 _00239_ net794 _07440_ gnd gnd vdd vdd dp_pcimm_a_0_ sky130_fd_sc_hd__o21ai_0
X13 _00002_ _00186_ _00163_ _06805_ gnd gnd vdd vdd _06806_ sky130_fd_sc_hd__a31oi_1
X14 _06803_ _06806_ _06807_ gnd gnd vdd vdd _06808_ sky130_fd_sc_hd__o21ai_0
X15 _06808_ _06810_ _06811_ gnd gnd vdd vdd _06812_ sky130_fd_sc_hd__a21boi_0
X16 _06802_ _06812_ _06813_ gnd gnd vdd vdd _06814_ sky130_fd_sc_hd__o21ai_0
X17 _06814_ _06817_ _06820_ gnd gnd vdd vdd _06821_ sky130_fd_sc_hd__a21oi_1
X18 _06801_ _06821_ _06822_ gnd gnd vdd vdd _06823_ sky130_fd_sc_hd__o21ai_0
X19 _06823_ _06825_ _06827_ gnd gnd vdd vdd _06828_ sky130_fd_sc_hd__a21oi_1
X20 _06800_ _06828_ _06833_ gnd gnd vdd vdd _06834_ sky130_fd_sc_hd__o21ai_0
X21 _06834_ _06836_ _06838_ _06844_ gnd gnd vdd vdd _06845_ sky130_fd_sc_hd__a31oi_1
X22 _06796_ _06845_ _06849_ gnd gnd vdd vdd _06850_ sky130_fd_sc_hd__o21ai_0
X23 _06791_ _06850_ gnd gnd vdd vdd _06851_ sky130_fd_sc_hd__xor2_1
X24 net691 net690 _06851_ gnd gnd vdd vdd _07048_ sky130_fd_sc_hd__nand3_1
X25 _07047_ net806 _07048_ gnd gnd vdd vdd _07049_ sky130_fd_sc_hd__nand3_1
X26 _07049_ _07063_ gnd gnd vdd vdd dp_result2_29_ sky130_fd_sc_hd__nand2_1
X27 dp_result2_29_ gnd gnd vdd vdd net672 sky130_fd_sc_hd__buf_4
clknet clk 0 0
.tran 1p 3n
.ic v(_02907_)=0
.control
run
meas tran tin WHEN v(_02907_)=0.9
meas tran tout WHEN v(net672)=0.9
meas tran tdelay param='tout-tin'
.endc
.end
