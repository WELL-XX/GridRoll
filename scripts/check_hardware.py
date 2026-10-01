#!/usr/bin/env python3
"""Guard the wiring contract and row-major 47-key layout."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "left": {"row": [(0,29),(0,31),(1,6),(0,26)],
             "col": [(1,11),(1,10),(0,3),(0,28),(1,13),(0,30)]},
    "right": {"row": [(1,4),(0,30),(0,29),(0,31)],
              "col": [(0,24),(1,6),(0,3),(1,11),(1,10),(0,28)]},
}
for side, pins in EXPECTED.items():
    text=(ROOT/f"boards/shields/gridroll/gridroll_{side}.overlay").read_text()
    all_pins=[]
    for kind, expected in pins.items():
        section=re.search(rf"{kind}-gpios\s*=\s*(.*?);",text,re.S).group(1)
        found=[(int(p),int(n)) for p,n in re.findall(r"&gpio([01])\s+(\d+)",section)]
        assert found==expected, (side,kind,found)
        assert section.count("GPIO_ACTIVE_HIGH")==len(expected)
        assert section.count("GPIO_PULL_DOWN")== (4 if kind=="row" else 0)
        all_pins+=found
    extras=[(0,13),(0,24)] if side=="left" else [(0,12),(1,9),(0,13),(0,15)]
    assert len(set(all_pins+extras))==len(all_pins+extras), f"{side}: pin conflict"
    assert not set(all_pins+extras)&{(0,9),(0,10),(0,5)}, "reserved pin used"
    assert f"col-offset = <{0 if side=='left' else 6}>" in text
layout=(ROOT/"boards/shields/gridroll/gridroll-layouts.dtsi").read_text()
mapping=[(int(r),int(c)) for r,c in re.findall(r"RC\((\d+),\s*(\d+)\)",layout)]
assert mapping==[(r,c) for r in range(4) for c in range(12) if (r,c)!=(3,8)]
assert mapping.count((3,3))==1
assert len(re.findall(r"&key_physical_attrs",layout))==47
keymap=(ROOT/"config/gridroll.keymap").read_text()
layers=keymap.split('compatible = "zmk,keymap";',1)[1]
for layer in ["base","fn","mouse","system"]:
    content=re.search(rf"\b{layer}\s*\{{(.*?)\n\s*\}};",layers,re.S).group(1)
    bindings=re.search(r"\bbindings\s*=\s*<(.*?)>;",content,re.S).group(1)
    assert len(re.findall(r"&\w+",bindings))==47, layer
assert len(re.findall(r'status = "reserved"',keymap))==4
assert 'diode-direction = "col2row"' in (ROOT/"boards/shields/gridroll/gridroll.dtsi").read_text()
print("GPIO order/flags, pin reservations/conflicts, 47-key transform, physical layout and 8 layers passed")
