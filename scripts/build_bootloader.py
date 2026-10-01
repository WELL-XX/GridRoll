#!/usr/bin/env python3
"""Build the custom bootloader and the two upstream regression boards."""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument("--source",type=Path,required=True)
p.add_argument("--out",type=Path,required=True)
p.add_argument("--cross-compile",default="arm-none-eabi-")
a=p.parse_args(); source=a.source.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
lock=json.loads((ROOT/"bootloader/upstream.json").read_text())
actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=source,text=True).strip()
assert actual==lock["revision"], f"Unexpected bootloader revision {actual}"
shutil.copytree(ROOT/"bootloader/gridroll",source/"src/boards/gridroll",dirs_exist_ok=True)
for board in ["gridroll","feather_nrf52840_express","feather_nrf52832"]:
    log=out/f"bootloader-{board}.log"
    command=["make",f"BOARD={board}","GIT_VERSION=0.11.0","_VER3=0 11 0",
             f"PYTHON={sys.executable}",f"CROSS_COMPILE={a.cross_compile}","-j4","all"]
    print(f"Building bootloader {board}",flush=True)
    with log.open("w") as f: rc=subprocess.run(command,cwd=source,stdout=f,stderr=subprocess.STDOUT).returncode
    if rc: print(log.read_text()[-6000:]); sys.exit(rc)
merged=source/"_build/build-gridroll/gridroll_bootloader-0.11.0_s140_6.1.1.hex"
result=out/"GridRoll-first-flash.hex"
subprocess.run([sys.executable,str(ROOT/"scripts/package_bootstrap.py"),str(merged),str(result)],check=True)
subprocess.run([sys.executable,str(ROOT/"scripts/check_addresses.py"),str(result),"--kind","first-flash"],check=True)
licenses=out/"licenses"; licenses.mkdir(exist_ok=True)
for src,dst in [("LICENSE","Adafruit-Bootloader-MIT.txt"),
    ("lib/softdevice/s140_nrf52_6.1.1/s140_nrf52_6.1.1_license-agreement.txt","Nordic-S140-6.1.1.txt"),
    ("lib/nrfx/LICENSE","Nordic-nrfx.txt"),("lib/tinyusb/LICENSE","TinyUSB-MIT.txt"),
    ("lib/uf2/LICENSE.txt","UF2-MIT.txt")]:
    shutil.copyfile(source/src,licenses/dst)
shutil.copyfile(ROOT/"THIRD_PARTY_NOTICES.md",out/"THIRD_PARTY_NOTICES.md")
