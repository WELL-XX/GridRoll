#!/usr/bin/env python3
"""Add deterministic 3.3V UICR initialization to the upstream SD+boot HEX."""
import argparse
from intelhex import IntelHex
p=argparse.ArgumentParser()
p.add_argument("merged_hex")
p.add_argument("output_hex")
a=p.parse_args()
h=IntelHex(a.merged_hex)
for i,b in enumerate((5,0,0,0)): h[0x10001304+i]=b
h.write_hex_file(a.output_hex)
