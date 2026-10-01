#!/usr/bin/env python3
"""Check the actual HEX/UF2 payload, not just device-tree constants."""
import argparse, struct
from pathlib import Path
from intelhex import IntelHex
p=argparse.ArgumentParser()
p.add_argument("hex",type=Path)
p.add_argument("--kind",choices=["app","first-flash"],default="app")
p.add_argument("--uf2",type=Path)
a=p.parse_args()
h=IntelHex(str(a.hex)); addresses=h.addresses()
flash=[x for x in addresses if x<0x10000000]
assert flash, "empty flash image"
if a.kind=="app":
    assert all(0x26000<=x<0xec000 for x in flash), "application overlaps reserved flash"
else:
    assert all(x<0x26000 or 0xf4000<=x<0x100000 for x in flash), "bootstrap overlaps application/storage"
    assert any(x<0x1000 for x in flash), "MBR missing"
    assert any(0x1000<=x<0x26000 for x in flash), "SoftDevice missing"
    assert any(0xf4000<=x<0xfe000 for x in flash), "bootloader missing"
    regout=sum(h[0x10001304+i]<<(8*i) for i in range(4))
    bootaddr=sum(h[0x10001014+i]<<(8*i) for i in range(4))
    assert regout==5, f"REGOUT0 should be 3.3V (5), got {regout:#x}"
    assert bootaddr==0xf4000, f"invalid bootloader address {bootaddr:#x}"
if a.uf2:
    data=a.uf2.read_bytes(); assert len(data)%512==0
    covered={}
    for off in range(0,len(data),512):
        b=data[off:off+512]
        m1,m2,flags,addr,size,num,total,family=struct.unpack_from('<8I',b)
        assert (m1,m2)==(0x0a324655,0x9e5d5157)
        assert struct.unpack_from('<I',b,508)[0]==0x0ab16f30
        assert flags&0x2000 and family==0xada52840
        assert num==off//512 and total==len(data)//512
        assert 0<size<=476 and 0x26000<=addr and addr+size<=0xec000
        for i,v in enumerate(b[32:32+size]): covered[addr+i]=v
    assert all(covered.get(x)==h[x] for x in flash), "UF2 does not match HEX"
print(f"{a.hex.name}: address checks passed ({min(flash):#x}–{max(flash):#x})")
