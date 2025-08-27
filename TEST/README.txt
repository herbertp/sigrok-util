
The lpc-seq.csv contains a sequence of post code writes at
address 0x0080 starting with 0x00, 0x11, 0x22, ... up to
0xEE, 0xFF.

After building and installing sigrok with ...
$ cross-compile/linux/sigrok-cross-linux

... the decoder can be tested with:
$ LD_LIBRARY_PATH=~/sr/lib/ ~/sr/bin/sigrok-cli -i TEST/lpc-seq.csv -I csv:column_formats=t,l,l,l,l,l,l,l,l -P lpc:lframe=0:lad3=1:lad2=2:lad1=3:lad0=4:lreset=5:lclk=6 -A lpc

The specification for Intel LPC can be found in
TEST/low-pin-count-interface-specification.pdf

