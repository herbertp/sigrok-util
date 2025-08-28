
import sigrokdecode as srd

class Decoder(srd.Decoder):
    api_version = 3
    id = "lpc"
    name = "LPC"
    longname = "Low Pin Count"
    desc = "Low Pin Count bus."
    license = "gplv2+"
    inputs = ["logic"]
    outputs = []
    tags = ["PC"]

    channels = (
        {"id": "lclk", "name": "LCLK", "desc": "LPC Clock"},
        {"id": "lframe", "name": "LFRAME#", "desc": "LPC Frame"},
        {"id": "lad0", "name": "LAD0", "desc": "LPC Address/Data 0"},
        {"id": "lad1", "name": "LAD1", "desc": "LPC Address/Data 1"},
        {"id": "lad2", "name": "LAD2", "desc": "LPC Address/Data 2"},
        {"id": "lad3", "name": "LAD3", "desc": "LPC Address/Data 3"},
        {"id": "lreset", "name": "LRESET#", "desc": "LPC Reset"},
    )

    annotations = (
        ("start", "Start of cycle"),
        ("cycle-type", "Cycle type"),
        ("address", "Address"),
        ("data", "Data"),
        ("stop", "Stop of cycle"),
    )
    annotation_rows = (
        ("fields", "Fields", (0, 1, 2, 3, 4)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "IDLE"
        self.pins = None

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def get_lad(self):
        lad0 = self.pins[2]
        lad1 = self.pins[3]
        lad2 = self.pins[4]
        lad3 = self.pins[5]
        return (lad3 << 3) | (lad2 << 2) | (lad1 << 1) | lad0

    def decode(self):
        while True:
            if self.state == "IDLE":
                self.pins = self.wait({1: "f"}) # lframe
                self.state = "START_FIELD"
                self.put(self.samplenum, self.samplenum, self.out_ann, [0, ["Start of cycle for a target", "Start"]])

            elif self.state == "START_FIELD":
                self.pins = self.wait({0: "f"}) # lclk
                lad = self.get_lad()
                if lad == 0:
                    self.state = "CYCLE_TYPE"
                else:
                    self.state = "ABORT_CYCLE"

            elif self.state == "CYCLE_TYPE":
                self.pins = self.wait({0: "f"}) # lclk
                lad = self.get_lad()
                if lad == 2: # I/O Write
                    self.put(self.samplenum, self.samplenum, self.out_ann, [1, ["I/O write", "IOW"]])
                    self.state = "ADDRESS"
                    self.address = 0
                    self.nibble_count = 0
                else:
                    self.state = "ABORT_CYCLE"

            elif self.state == "ADDRESS":
                self.pins = self.wait({0: "f"}) # lclk
                lad = self.get_lad()
                self.address |= (lad << (4 * self.nibble_count))
                self.nibble_count += 1
                if self.nibble_count == 4:
                    self.put(self.samplenum, self.samplenum, self.out_ann, [2, ["Address: 0x%04x" % self.address, "Addr"]])
                    self.state = "DATA"
                    self.data = 0
                    self.nibble_count = 0

            elif self.state == "DATA":
                self.pins = self.wait({0: "f"}) # lclk
                lad = self.get_lad()
                self.data |= (lad << (4 * self.nibble_count))
                self.nibble_count += 1
                if self.nibble_count == 2:
                    self.put(self.samplenum, self.samplenum, self.out_ann, [3, ["DATA: 0x%02x" % self.data, "Data"]])
                    self.state = "SYNC"

            elif self.state == "SYNC":
                self.pins = self.wait({0: "f"}) # lclk
                lad = self.get_lad()
                if lad == 0xf:
                    self.state = "STOP"
                else:
                    self.state = "ABORT_CYCLE"

            elif self.state == "STOP":
                self.pins = self.wait({1: "r"}) # lframe
                self.put(self.samplenum, self.samplenum, self.out_ann, [4, ["Stop/abort (end of a cycle for a target)", "Stop"]])
                self.state = "IDLE"

            elif self.state == "ABORT_CYCLE":
                self.pins = self.wait({1: "r"}) # lframe
                self.state = "IDLE"
