
TEST/lpc-seq.csv contains a sequence of post code writes at
address 0x0080 starting with 0x00, 0x11, 0x22, ... up to
0xEE, 0xFF.

The decoder can be tested with:
$ LD_LIBRARY_PATH=~/sr/lib/ ~/sr/bin/sigrok-cli -i TEST/lpc-seq.csv -I csv:column_formats=t,l,l,l,l,l,l,l,l -P lpc:lframe=0:lad3=1:lad2=2:lad1=3:lad0=4:lreset=5:lclk=6 -A lpc

The expected output should be something like this:

lpc-1: Start of cycle for a target
lpc-1: Grant for bus master 0
lpc-1: Cycle type: I/O write
lpc-1: Address: 0x0080
lpc-1: DATA: 0x00
lpc-1: Stop/abort (end of a cycle for a target)

lpc-1: Start of cycle for a target
lpc-1: Grant for bus master 0
lpc-1: Cycle type: I/O write
lpc-1: Address: 0x0080
lpc-1: DATA: 0x11
lpc-1: Stop/abort (end of a cycle for a target)

lpc-1: Start of cycle for a target
lpc-1: Grant for bus master 0
lpc-1: Cycle type: I/O write
lpc-1: Address: 0x0080
lpc-1: DATA: 0x22
lpc-1: Stop/abort (end of a cycle for a target)

...

The source for the decoder can be found in lpc/
and no install is required for testing.

The specification for Intel LPC can be found in
TEST/low-pin-count-interface-specification.pdf

