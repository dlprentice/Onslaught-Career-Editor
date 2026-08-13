"""Recover the Mission script-command registry from the shipped image.

`ScriptCommandRegistry__InitBuiltins @ 0x0052FF30` populates a record array based
at 0x0064CE20 by storing constants and register-held immediates into absolute
addresses. The records are 0x40 bytes: the command name pointer at +0x00 and the
handler function pointer at +0x30.

This abstractly interprets the initializer's stores -- tracking `mov reg, imm`,
`xor reg, reg` and `mov [abs], reg|imm` -- to reconstruct the table, then reads
the name/handler pairs out of it. The result is a name for each handler taken
from the game's own data rather than inferred.

Read-only. Emits registry.tsv and extract.ready.json beside this file.
Promotes nothing: naming a Ghidra function is a separate, gated action.
"""
import hashlib
import os
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG

REPO = Path(__file__).resolve().parents[1]
LANE = Path(
    os.environ.get('BEA_OUT', REPO / 'local-lab'))
SPECIMEN = REPO / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
SPECIMEN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROJECTION = REPO / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-12.tsv"
BASE = 0x00400000
INIT = 0x0052FF30
TABLE = 0x0064CE20
STRIDE = 0x40
NAME_OFF, FN_OFF = 0x00, 0x30

data = SPECIMEN.read_bytes()
assert hashlib.sha256(data).hexdigest() == SPECIMEN_SHA, "specimen identity mismatch"

names, rng = {}, {}
for line in PROJECTION.read_text(encoding="utf-8").splitlines():
    if line.startswith("#") or line.startswith("address"):
        continue
    a, n, lo, hi = line.split("\t")
    names[int(a, 16)] = n
    rng[int(a, 16)] = (int(lo, 16), int(hi, 16))
code_lo = min(v[0] for v in rng.values())
code_hi = max(v[1] for v in rng.values())


def cstr(va, limit=64):
    off = va - BASE
    if not (0 <= off < len(data)):
        return None
    end = data.find(b"\x00", off)
    if end < 0 or end - off > limit:
        return None
    s = data[off:end]
    return s.decode("ascii") if s and all(32 <= c < 127 for c in s) else None


md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
lo, hi = rng[INIT]

regs, mem, unknown_stores = {}, {}, 0
for ins in md.disasm(data[lo - BASE: hi - BASE + 1], lo):
    ops = ins.operands
    if ins.mnemonic == "xor" and len(ops) == 2 and ops[0].type == X86_OP_REG \
            and ops[1].type == X86_OP_REG and ops[0].reg == ops[1].reg:
        regs[ins.reg_name(ops[0].reg)] = 0
    elif ins.mnemonic == "mov" and len(ops) == 2 and ops[0].type == X86_OP_REG \
            and ops[1].type == X86_OP_IMM:
        regs[ins.reg_name(ops[0].reg)] = ops[1].imm & 0xFFFFFFFF
    elif ins.mnemonic == "mov" and len(ops) == 2 and ops[0].type == X86_OP_MEM \
            and ops[0].mem.base == 0 and ops[0].mem.index == 0:
        addr = ops[0].mem.disp & 0xFFFFFFFF
        if ops[1].type == X86_OP_IMM:
            mem[addr] = ops[1].imm & 0xFFFFFFFF
        elif ops[1].type == X86_OP_REG:
            r = ins.reg_name(ops[1].reg)
            if r in regs:
                mem[addr] = regs[r]
            else:
                unknown_stores += 1
    elif ins.mnemonic in ("call",):
        regs.clear()          # a call clobbers volatile registers


def slot(addr):
    if addr in mem:
        return mem[addr]
    off = addr - BASE
    if 0 <= off + 4 <= len(data):
        return struct.unpack_from("<I", data, off)[0]
    return None


records, stop = [], None
for i in range(0, 512):
    rec = TABLE + i * STRIDE
    nptr, fptr = slot(rec + NAME_OFF), slot(rec + FN_OFF)
    cmd = cstr(nptr) if nptr else None
    if not cmd:
        stop = i
        break
    resolved = names.get(fptr)
    inside = next((names[f] for f, (a, b) in rng.items() if a <= (fptr or 0) <= b), None)
    records.append({
        "index": i, "recordVa": f"0x{rec:08X}", "command": cmd,
        "handlerVa": f"0x{fptr:08X}" if fptr else None,
        "handlerName": resolved or inside,
        "handlerIsFunctionEntry": fptr in names if fptr else False,
        "handlerIsCode": bool(fptr and code_lo <= fptr <= code_hi),
    })

unnamed = [r for r in records
           if r["handlerName"] and r["handlerName"].startswith("FUN_")]
noop = [r for r in records if r["handlerName"] == "SharedVFunc__NoOp_Ret0C"]

tsv = ["index\tcommand\thandlerVa\tcurrentGhidraName\tisFunctionEntry"]
for r in records:
    tsv.append(f"{r['index']}\t{r['command']}\t{r['handlerVa']}\t"
               f"{r['handlerName'] or ''}\t{r['handlerIsFunctionEntry']}")
tsv_text = "\n".join(tsv) + "\n"
(LANE / "registry.tsv").write_text(tsv_text, encoding="utf-8", newline="\n")

out = {"schemaVersion": "bea.re.mission-native-registry.v1",
       "specimenSha256": SPECIMEN_SHA,
       "initialiserVa": f"0x{INIT:08X}", "tableVa": f"0x{TABLE:08X}",
       "recordStride": STRIDE, "nameOffset": NAME_OFF, "handlerOffset": FN_OFF,
       "recordsRecovered": len(records), "stoppedAtIndex": stop,
       "storesWithUntrackedRegister": unknown_stores,
       "handlersResolvingToAFunctionEntry":
           sum(1 for r in records if r["handlerIsFunctionEntry"]),
       "handlersOnStillDefaultNames": [
           {"command": r["command"], "handlerVa": r["handlerVa"],
            "currentName": r["handlerName"]} for r in unnamed],
       "handlersOnSharedNoOp": len(noop),
       "outputTsv": {"name": "registry.tsv", "bytes": len(tsv_text.encode()),
                     "sha256": hashlib.sha256(tsv_text.encode()).hexdigest()},
       "claimBoundary": (
           "The command name is the game's own registry string for that handler slot. "
           "It is not proof of the handler's original C++ function name, and it "
           "establishes no behaviour, signature, or argument contract. Records whose "
           "handler is the shared no-op are registered but unimplemented on this path. "
           "Nothing here is promoted to Ghidra.")}

payload = json.dumps(out, indent=2, sort_keys=True) + "\n"
(LANE / "extract.ready.json").write_text(payload, encoding="utf-8", newline="\n")
print(f"extract.ready.json bytes={len(payload.encode())} "
      f"sha256={hashlib.sha256(payload.encode()).hexdigest()}")
print(f"registry.tsv bytes={len(tsv_text.encode())} "
      f"sha256={out['outputTsv']['sha256']}\n")
print(f"records recovered              : {len(records)} (stopped at index {stop})")
print(f"handlers that are function entries: {out['handlersResolvingToAFunctionEntry']}")
print(f"handlers on the shared no-op   : {len(noop)}")
print(f"stores with an untracked register: {unknown_stores}")
print(f"\ncommands whose handler is still a default FUN_ name ({len(unnamed)}):")
for r in unnamed:
    print(f"  {r['command']:<34} {r['handlerVa']}  {r['handlerName']}")
