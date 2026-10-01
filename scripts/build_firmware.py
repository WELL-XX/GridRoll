#!/usr/bin/env python3
"""Build and validate all application artifacts with the locked west workspace."""
import argparse, os, shutil, subprocess, sys
import yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGETS={entry["artifact-name"].removeprefix("GridRoll-"): entry
         for entry in yaml.safe_load((ROOT/"build.yaml").read_text())["include"]}
p=argparse.ArgumentParser()
p.add_argument("--workspace",type=Path,required=True)
p.add_argument("--out",type=Path,required=True)
p.add_argument("--only",choices=TARGETS)
a=p.parse_args(); workspace=a.workspace.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
for name,entry in TARGETS.items():
    if a.only and a.only!=name: continue
    shield=entry["shield"]; snippets=entry.get("snippet", "").split(); stem=entry["artifact-name"]
    build=workspace/"build"/name
    command=["west","build","-p","-s",str(workspace/"zmk/app"),"-d",str(build),
             "-b",entry["board"]]
    if snippets: command += ["-S"," ".join(snippets)]
    command += ["--",f"-DZephyr_DIR={workspace}/zephyr/share/zephyr-package/cmake",
                f"-DZMK_CONFIG={ROOT}/config",f"-DZMK_EXTRA_MODULES={ROOT}",f"-DSHIELD={shield}"]
    log=out/f"{stem}.log"
    print(f"Building {stem}; log: {log}",flush=True)
    with log.open("w") as f:
        rc=subprocess.run(command,cwd=workspace,stdout=f,stderr=subprocess.STDOUT).returncode
    if rc:
        print(log.read_text()[-6000:]); sys.exit(rc)
    config=(build/"zephyr/.config").read_text()
    if name in ("right","right-diagnostics"):
        for flag in ["CONFIG_ZMK_SPLIT_ROLE_CENTRAL=y","CONFIG_ZMK_STUDIO=y",
                     "CONFIG_GRIDROLL_PAW3222=y","CONFIG_ZMK_RUNTIME_INPUT_PROCESSOR_STUDIO_RPC=y"]:
            assert flag in config, f"{name}: missing {flag}"
    if name=="left":
        assert "CONFIG_ZMK_SPLIT_ROLE_CENTRAL=y" not in config
        assert "CONFIG_ZMK_STUDIO=y" not in config
        assert "CONFIG_GRIDROLL_PAW3222=y" not in config
    for ext in ["uf2","hex"]: shutil.copyfile(build/f"zephyr/zmk.{ext}",out/f"{stem}.{ext}")
    shutil.copyfile(build/"zephyr/.config",out/f"{stem}.config")
    shutil.copyfile(build/"zephyr/zephyr.dts",out/f"{stem}.dts")
    subprocess.run([sys.executable,str(ROOT/"scripts/check_addresses.py"),str(out/f"{stem}.hex"),
                    "--uf2",str(out/f"{stem}.uf2")],check=True)
