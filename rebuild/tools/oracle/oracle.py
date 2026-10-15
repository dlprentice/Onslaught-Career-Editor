#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The per-function oracle: the rebuild's C# function against the retail function it ports, case by case, bit for bit.

    python rebuild/tools/oracle/oracle.py build   [--group G]    compile the VC6 driver and adapters, link the decomp's objects
    python rebuild/tools/oracle/oracle.py gen     [--fn F]       write the inputs (deterministic)
    python rebuild/tools/oracle/oracle.py run-vc6 [--group G]    run the retail-identical code under Wine at 0x007F and 0x027F
    python rebuild/tools/oracle/oracle.py run-cs                 run the C# adapters on the same inputs
    python rebuild/tools/oracle/oracle.py compare                per function: N cases, M differ, negative control K differ
    python rebuild/tools/oracle/oracle.py all

The retail side is bea-decomp's matched objects linked into a VC6 driver with a small per-function adapter that builds
the object the function reads; it runs under Wine at control word 0x007F. Adapters, driver, objects and outputs are
private and live in the oracle data root (ORACLE_FN_OUT, default <canonical checkout>/local-data/parity-oracle/fn).
Exit code 0: every function matches and every negative control differs (a check that cannot fail is a failure).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen  # noqa: E402

ROOT = HERE.parents[2]
CANONICAL = ROOT.parents[1] if ROOT.parent.name == ".worktrees" else ROOT
HOME = Path.home()
DECOMP = Path(os.environ.get("BEA_DECOMP", HOME / "Projects/game-dev/bea-decomp"))
VC6 = CANONICAL / "local-lab/third-party/msvc6-sp5-toolchain"
DX = CANONICAL / "local-lab/third-party/directx9-sdk-include"
BASE_PREFIX = Path("/var/tmp/bea-decomp-wine")
PREFIX = Path(os.environ.get("ORACLE_FN_WINEPREFIX", "/var/tmp/D-oracle-wine"))
OUT = Path(os.environ.get("ORACLE_FN_OUT", str(CANONICAL / "local-data/parity-oracle/fn")))
GAME = Path(os.environ.get("ONSLAUGHT_GAME_DIR", HOME / ".local/share/Steam/steamapps/common/Battle Engine Aquila"))
SPEC = json.loads((HERE / "functions.json").read_text())
CONTROL_WORD = "007f"
CONTROLS = ("027f",)
FLAGS = ["/O2", "/Ob2", "/GX", "/MT", "/QIfist", "/GR"]


def winpath(p: Path | str) -> str:
    return "Z:" + str(Path(p).resolve()).replace("/", "\\")


def prefix() -> Path:
    if not PREFIX.exists():
        staging = PREFIX.with_name(PREFIX.name + ".partial")
        shutil.rmtree(staging, ignore_errors=True)
        shutil.copytree(BASE_PREFIX, staging, symlinks=True, ignore=shutil.ignore_patterns(".bea-decomp.lock", "ONSLAUGHT2"))
        staging.rename(PREFIX)
    link = PREFIX / "drive_c/dev/ONSLAUGHT2"
    if not link.is_symlink() or link.resolve() != (DECOMP / "src").resolve():
        link.parent.mkdir(parents=True, exist_ok=True)
        link.unlink(missing_ok=True)
        link.symlink_to(DECOMP / "src")
    return PREFIX


def env() -> dict[str, str]:
    e = dict(os.environ, WINEPREFIX=str(prefix()), WINEDEBUG="-all", WINEDLLOVERRIDES="mscoree,mshtml=",
             WINEPATH=f"{winpath(VC6 / 'VC98/Bin')};{winpath(VC6 / 'Common/MSDev98/Bin')}",
             INCLUDE=";".join([winpath(DX / "Include"), winpath(DX / "Samples"), winpath(VC6 / "VC98/Include"), "C:\\dev\\ONSLAUGHT2"]),
             LIB=winpath(VC6 / "VC98/Lib"))
    e.pop("DISPLAY", None)
    e.pop("WAYLAND_DISPLAY", None)
    return e


def wine(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["wine", *args], env=env(), cwd=cwd, capture_output=True, text=True, timeout=1800)


def clean(text: str) -> str:
    return "\n".join(l for l in text.replace("\r", "").splitlines() if "MESA" not in l and "pci id" not in l)


def groups_of(only: str | None) -> list[str]:
    return [only] if only else sorted(SPEC["groups"])


def functions_of(group: str) -> list[str]:
    return [n for n, s in SPEC["functions"].items() if s["group"] == group]


def build(group_name: str) -> int:
    group = SPEC["groups"][group_name]
    work = OUT / "build" / group_name
    work.mkdir(parents=True, exist_ok=True)
    adapter = OUT / "adapters" / group["adapter"]
    driver = OUT / "driver/driver.cpp"
    for src in (driver, adapter):
        if not src.exists():
            print(f"missing private source {src}")
            return 1
    for src in (driver, adapter):
        r = wine([str(VC6 / "VC98/Bin/CL.EXE"), "/nologo", "/c", *FLAGS, f"/Fo{winpath(work)}\\", winpath(src)], work)
        if r.returncode != 0:
            print(clean(r.stdout + r.stderr))
            return r.returncode
    objs = [winpath(work / "driver.obj"), winpath(work / (Path(group["adapter"]).stem + ".obj"))]
    objs += [winpath(DECOMP / "build" / o) for o in group["objects"]]
    r = wine([str(VC6 / "VC98/Bin/LINK.EXE"), "/nologo", "/FORCE:UNRESOLVED", f"/out:{winpath(work / (group_name + '.exe'))}", *objs], work)
    text = clean(r.stdout + r.stderr)
    (work / "link.txt").write_text(text + "\n")
    print(f"{group_name}: linked {len(group['objects'])} object(s); {len([l for l in text.splitlines() if 'LNK2001' in l])} unresolved externals tolerated (never reached)")
    return 0 if (work / (group_name + ".exe")).exists() else 1


def images() -> None:
    img = OUT / "images"
    img.mkdir(parents=True, exist_ok=True)
    if any(g.get("images") for g in SPEC["groups"].values()) and not (img / "hf.bin").exists():
        import images as imgmod  # noqa: PLC0415
        imgmod.make(GAME, img)


def generate(only: str | None) -> None:
    images()
    for group in groups_of(None):
        lines = []
        for name in functions_of(group):
            spec = SPEC["functions"][name]
            if only and name != only:
                continue
            for words in gen.GENERATORS[spec["gen"]](name, spec["count"]):
                lines.append(name + "\t" + " ".join(f"{w:08x}" for w in words))
        if lines:
            (OUT / "cases").mkdir(parents=True, exist_ok=True)
            (OUT / "cases" / f"{group}.txt").write_text("\n".join(lines) + "\n")
            print(f"{group}: {len(lines)} cases")


def run_vc6(only: str | None) -> int:
    for group in groups_of(only):
        exe = OUT / "build" / group / f"{group}.exe"
        cases = OUT / "cases" / f"{group}.txt"
        if not exe.exists() or not cases.exists():
            print(f"{group}: needs build and gen first")
            return 1
        for cw in (CONTROL_WORD, *CONTROLS):
            out = OUT / "out" / f"{group}.vc6-{cw}.txt"
            out.parent.mkdir(parents=True, exist_ok=True)
            r = wine([winpath(exe), winpath(cases), winpath(out), cw, winpath(OUT / "images")], OUT / "build" / group)
            if r.returncode != 0:
                print(f"{group} at {cw}: exit {r.returncode}\n{clean(r.stderr)[-800:]}")
                return 1
            print(f"{group}: ran at control word 0x{cw}")
    return 0


def run_cs() -> int:
    project = HERE / "OnslaughtRebuild.Oracle/OnslaughtRebuild.Oracle.csproj"
    for group in groups_of(None):
        cases = OUT / "cases" / f"{group}.txt"
        if not cases.exists():
            continue
        out = OUT / "out" / f"{group}.cs.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["dotnet", "run", "-c", "Release", "--project", str(project), "--", str(cases), str(out), str(OUT / "images"), str(GAME)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:])
            return r.returncode
        print(f"{group}: C# adapters ran")
    return 0


def read_outputs(path: Path) -> list[tuple[str, str]]:
    return [(l.partition("\t")[0], l.partition("\t")[2]) for l in path.read_text().replace("\r", "").splitlines()]


def compare() -> int:
    status = 0
    print(f"{'function':32} {'retail':>10} {'cases':>7} {'differ':>7} {'control differ':>15}")
    for group in groups_of(None):
        cases = OUT / "cases" / f"{group}.txt"
        files = {k: OUT / "out" / f"{group}.{k}.txt" for k in ("vc6-" + CONTROL_WORD, "cs", *("vc6-" + c for c in CONTROLS))}
        if not cases.exists() or not all(p.exists() for p in files.values()):
            print(f"{group}: outputs missing")
            status = 1
            continue
        inputs = [l.partition("\t") for l in cases.read_text().splitlines()]
        vc = read_outputs(files["vc6-" + CONTROL_WORD])
        cs = read_outputs(files["cs"])
        ctl = {c: read_outputs(files["vc6-" + c]) for c in CONTROLS}
        per: dict[str, list[int]] = {}
        shown: dict[str, int] = {}
        for i, (name, _, ins) in enumerate(inputs):
            row = per.setdefault(name, [0, 0, 0])
            row[0] += 1
            if vc[i][1] != cs[i][1]:
                row[1] += 1
                if shown.get(name, 0) < 5:
                    shown[name] = shown.get(name, 0) + 1
                    print(f"  DIFF {name} in[{ins}] retail[{vc[i][1]}] cs[{cs[i][1]}]")
            if any(ctl[c][i][1] != cs[i][1] for c in CONTROLS):
                row[2] += 1
        for name in functions_of(group):
            if name not in per:
                continue
            n, m, k = per[name]
            flag = ""
            if m:
                flag = "  <-- DIFFERS"
                status = 1
            elif k == 0:
                flag = "  <-- NEGATIVE CONTROL SHOWS NO DIFFERENCE: this check cannot fail"
                status = 1
            print(f"{name:32} {SPEC['functions'][name]['retail']:>10} {n:>7} {m:>7} {k:>15}{flag}")
    return status


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["build", "gen", "run-vc6", "run-cs", "compare", "all"])
    ap.add_argument("--group")
    ap.add_argument("--fn")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    c = a.command
    if c in ("build", "all"):
        for g in groups_of(a.group):
            if build(g):
                return 1
    if c in ("gen", "all"):
        generate(a.fn)
    if c in ("run-vc6", "all") and run_vc6(a.group):
        return 1
    if c in ("run-cs", "all") and run_cs():
        return 1
    if c in ("compare", "all"):
        return compare()
    return 0


if __name__ == "__main__":
    sys.exit(main())
