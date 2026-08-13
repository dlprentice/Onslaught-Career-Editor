"""The PC retail binary carries its own __FILE__/__LINE__ source coordinates.

Discovered while chasing an unrelated question: three unnamed IScript functions
push `0x486`, `0x495`, `0x4a4` immediately before a pointer to
`C:\\dev\\ONSLAUGHT2\\MissionScript\\IScript.cpp`, and 1158/1173/1188 are exactly
the Xbox anchor lines for those same three functions. The pattern is a debug
allocator taking (file, line).

This scans every known function body for `push <line>` followed by
`push <pointer-to-a-source-path>` and joins each hit to its enclosing function,
producing a PC-native source-coordinate table that owes nothing to the Xbox lane.

Read-only. Emits pc-source-coordinates.tsv and scan.ready.json beside this file.
"""
import hashlib
import os
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from capstone.x86 import X86_OP_IMM

REPO = Path(__file__).resolve().parents[1]
LANE = Path(
    os.environ.get('BEA_OUT', REPO / 'local-lab'))
SPECIMEN = REPO / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
SPECIMEN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROJECTION = REPO / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-12.tsv"
BASE = 0x00400000

data = SPECIMEN.read_bytes()
assert hashlib.sha256(data).hexdigest() == SPECIMEN_SHA, "specimen identity mismatch"

names, rng = {}, {}
for line in PROJECTION.read_text(encoding="utf-8").splitlines():
    if line.startswith("#") or line.startswith("address"):
        continue
    a, n, lo, hi = line.split("\t")
    names[int(a, 16)] = n
    rng[int(a, 16)] = (int(lo, 16), int(hi, 16))

# Index every printable-ASCII run that looks like a source path.
SOURCE_RE = re.compile(r"^[A-Za-z]:\\.*\.(?:cpp|c|h|hpp|inl)$", re.IGNORECASE)
paths = {}
for m in re.finditer(rb"[\x20-\x7e]{6,}", data):
    s = m.group().decode("ascii")
    if SOURCE_RE.match(s):
        paths[BASE + m.start()] = s

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

hits = []
for va, (lo, hi) in sorted(rng.items()):
    prev_imm = prev_addr = None
    for ins in md.disasm(data[lo - BASE: hi - BASE + 1], lo):
        if ins.mnemonic == "push" and ins.operands and ins.operands[0].type == X86_OP_IMM:
            imm = ins.operands[0].imm & 0xFFFFFFFF
            if imm in paths and prev_imm is not None and 0 < prev_imm < 100000:
                hits.append({
                    "sourcePath": paths[imm], "sourceLine": prev_imm,
                    "pushLineAt": prev_addr, "pushPathAt": ins.address,
                    "functionVa": va, "functionName": names[va]})
            prev_imm, prev_addr = imm, ins.address
        else:
            prev_imm = prev_addr = None

by_path = Counter(h["sourcePath"] for h in hits)
by_func = defaultdict(set)
for h in hits:
    by_func[h["functionVa"]].add(h["sourcePath"])
multi = {f"0x{va:08X} {names[va]}": sorted(p) for va, p in by_func.items() if len(p) > 1}

tsv = ["sourcePath\tsourceLine\tfunctionVa\tfunctionName\tpushLineAt\tpushPathAt"]
for h in sorted(hits, key=lambda x: (x["sourcePath"].lower(), x["sourceLine"], x["functionVa"])):
    tsv.append(f"{h['sourcePath']}\t{h['sourceLine']}\t0x{h['functionVa']:08X}\t"
               f"{h['functionName']}\t0x{h['pushLineAt']:08X}\t0x{h['pushPathAt']:08X}")
tsv_text = "\n".join(tsv) + "\n"
(LANE / "pc-source-coordinates.tsv").write_text(tsv_text, encoding="utf-8", newline="\n")

receipt = {
    "schemaVersion": "bea.re.pc-native-source-coordinates.v1",
    "specimenSha256": SPECIMEN_SHA,
    "nameProjectionSha256": hashlib.sha256(PROJECTION.read_bytes()).hexdigest(),
    "sourcePathStringsInImage": len(paths),
    "coordinateCount": len(hits),
    "distinctSourcePaths": len(by_path),
    "distinctFunctions": len(by_func),
    "functionsSpanningMultiplePaths": multi,
    "pathHistogram": dict(by_path.most_common()),
    "outputTsv": {"name": "pc-source-coordinates.tsv", "bytes": len(tsv_text.encode()),
                  "sha256": hashlib.sha256(tsv_text.encode()).hexdigest()},
    "method": ("Within known function bodies, a `push <imm>` whose immediate points at a "
               "drive-rooted source path, immediately preceded by a `push <imm>` in "
               "1..99999, is read as a (line, file) debug-allocator argument pair."),
    "claimBoundary": (
        "A coordinate proves the compiler emitted that file and line at that "
        "instruction. It does not prove the enclosing function is wholly defined in "
        "that file: inlining can carry a coordinate across files, which is why "
        "functionsSpanningMultiplePaths is reported. It gives no file contents, no "
        "function boundary, and no semantic claim."),
}
payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
(LANE / "scan.ready.json").write_text(payload, encoding="utf-8", newline="\n")

print(f"scan.ready.json bytes={len(payload.encode())} "
      f"sha256={hashlib.sha256(payload.encode()).hexdigest()}")
print(f"pc-source-coordinates.tsv bytes={len(tsv_text.encode())} "
      f"sha256={receipt['outputTsv']['sha256']}\n")
print(f"source-path strings in image : {len(paths)}")
print(f"source coordinates recovered : {len(hits)}")
print(f"distinct source paths        : {len(by_path)}")
print(f"distinct PC functions        : {len(by_func)}")
print(f"functions spanning >1 path   : {len(multi)}")
print("\ntop source paths by coordinate count:")
for p, c in by_path.most_common(25):
    print(f"  {c:>5}  {p}")
