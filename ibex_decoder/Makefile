# defaults
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/ibex_pkg.sv \
	$(PWD)/ibex_decoder_wrap.sv \
	$(PWD)/ibex_decoder.sv
# use VHDL_SOURCES for VHDL files

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = ibex_decoder_wrap

# MODULE is the basename of the Python test file
MODULE = ibex_decoder_cocotb

EXTRA_ARGS += --trace-fst --trace-structs \
	-Wno-fatal -CFLAGS "-std=c++14 -Wall -O3"

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
