#!/usr/bin/env python3
"""Diff two ExportFullFunctionInventory.java exports.

An aggressive Ghidra analyser is not evaluated by "did the function count go
up".  It is evaluated by what it did to work that was already correct.  This
reports the four failure modes explicitly, and separates the DANGEROUS class -
a function carrying a USER_DEFINED (reviewed, graded) name that was deleted, or
whose body moved under it - from the benign churn of default-named functions.

Usage: ghidra_inventory_diff.py <before.tsv> <after.tsv> [--json out.json]
       [--sample-created N] [--pristine BEA.exe]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import struct
import sys
from pathlib import Path

# Fields whose change is worth reporting per surviving function.
TRACKED = (
    "name",
    "nameSource",
    "sigSource",
    "bodyBytes",
    "bodyMin",
    "bodyMax",
    "bodyRanges",
    "bodyDigest",
    "instrCount",
    "paramCount",
    "callingConv",
    "returnType",
    "isThunk",
    "noReturn",
    "signature",
)


def load(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return {row["address"]: row for row in rows}


def text_section(pe_path: Path) -> tuple[int, int, int, bytes]:
    raw = pe_path.read_bytes()
    pe = struct.unpack("<I", raw[0x3C:0x40])[0]
    nsec = struct.unpack("<H", raw[pe + 6 : pe + 8])[0]
    optsize = struct.unpack("<H", raw[pe + 20 : pe + 22])[0]
    for i in range(nsec):
        off = pe + 24 + optsize + 40 * i
        name = raw[off : off + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, va, _rsize, roff = struct.unpack("<IIII", raw[off + 8 : off + 24])
        if name == ".text":
            return 0x400000 + va, vsize, roff, raw
    raise SystemExit("no .text section found")


def classify_created(rows, pe_path: Path, limit: int) -> dict:
    """Sample created functions and say what fraction is plausibly real code.

    The test is deliberately crude and stated as such: an MSVC 32-bit function
    entry overwhelmingly begins with one of a small set of prologue shapes.  A
    created "function" whose first bytes are none of those, or which is pure
    filler, is a candidate false positive that a human must look at.  This
    counts, it does not adjudicate.
    """
    base, vsize, roff, raw = text_section(pe_path)

    def read(va: int, n: int) -> bytes:
        off = roff + (va - base)
        return raw[off : off + n]

    prologues = (
        b"\x55\x8b\xec",  # push ebp; mov ebp,esp
        b"\x53",  # push ebx
        b"\x56",  # push esi
        b"\x57",  # push edi
        b"\x8b\xff",  # mov edi,edi (hotpatch pad)
        b"\x83\xec",  # sub esp,imm8
        b"\x81\xec",  # sub esp,imm32
        b"\x8b\x44\x24",  # mov eax,[esp+x]
        b"\x8b\x4c\x24",
        b"\x8b\x54\x24",
        b"\x51",
        b"\x52",
        b"\x50",
        b"\x6a",  # push imm8
        b"\xa1",  # mov eax,[mem]
        b"\xb8",  # mov eax,imm32
        b"\xe9",  # jmp rel32 (thunk)
        b"\xff\x25",  # jmp [mem] (import thunk)
        b"\xc3",  # ret (stub)
        b"\x33\xc0",  # xor eax,eax
        b"\x8b\x0d",
        b"\x8b\x15",
    )
    buckets = collections.Counter()
    samples = []
    for row in rows:
        va = int(row["address"], 16)
        if not (base <= va < base + vsize):
            buckets["outside_text"] += 1
            continue
        head = read(va, 16)
        if not head:
            buckets["unreadable"] += 1
            continue
        if head[0] in (0xCC, 0x00) or set(head) <= {0x90}:
            verdict = "filler_or_padding"
        elif any(head.startswith(p) for p in prologues):
            verdict = "plausible_prologue"
        else:
            verdict = "unrecognised_head"
        buckets[verdict] += 1
        if len(samples) < limit or verdict != "plausible_prologue":
            samples.append(
                {
                    "address": row["address"],
                    "name": row["name"],
                    "bodyBytes": row["bodyBytes"],
                    "instrCount": row["instrCount"],
                    "verdict": verdict,
                    "head": head.hex(),
                }
            )
    return {"buckets": dict(buckets), "samples": samples[: max(limit, 40)]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--sample-created", type=int, default=25)
    ap.add_argument("--pristine", type=Path)
    args = ap.parse_args()

    before = load(args.before)
    after = load(args.after)

    created_keys = sorted(set(after) - set(before))
    destroyed_keys = sorted(set(before) - set(after))
    shared = sorted(set(before) & set(after))

    changes: dict[str, list] = collections.defaultdict(list)
    for key in shared:
        b, a = before[key], after[key]
        for field in TRACKED:
            if b.get(field) != a.get(field):
                changes[field].append({"address": key, "name": b["name"], "before": b.get(field), "after": a.get(field)})

    # THE DANGEROUS CLASS.  A reviewed name is one whose symbol source is
    # USER_DEFINED; that is the only machine-checkable marker this database
    # carries for "a human graded this".
    graded_before = {k for k, v in before.items() if v["nameSource"] == "USER_DEFINED"}
    graded_destroyed = [
        {"address": k, "name": before[k]["name"], "bodyBytes": before[k]["bodyBytes"]}
        for k in destroyed_keys
        if k in graded_before
    ]
    graded_renamed = [
        c for c in changes["name"] if before[c["address"]]["nameSource"] == "USER_DEFINED"
    ]
    graded_demoted = [
        c
        for c in changes["nameSource"]
        if c["before"] == "USER_DEFINED"
    ]
    graded_bounds_moved = [
        {
            "address": c["address"],
            "name": before[c["address"]]["name"],
            "beforeDigest": c["before"],
            "afterDigest": c["after"],
            "beforeBytes": before[c["address"]]["bodyBytes"],
            "afterBytes": after[c["address"]]["bodyBytes"],
            "beforeMax": before[c["address"]]["bodyMax"],
            "afterMax": after[c["address"]]["bodyMax"],
        }
        for c in changes["bodyDigest"]
        if c["address"] in graded_before
    ]

    report = {
        "beforeFile": str(args.before),
        "afterFile": str(args.after),
        "counts": {
            "before": len(before),
            "after": len(after),
            "created": len(created_keys),
            "destroyed": len(destroyed_keys),
            "boundsChanged": len(changes["bodyDigest"]),
            "namesChanged": len(changes["name"]),
            "signaturesChanged": len(changes["signature"]),
            "paramCountChanged": len(changes["paramCount"]),
            "callingConvChanged": len(changes["callingConv"]),
            "returnTypeChanged": len(changes["returnType"]),
            "sigSourceChanged": len(changes["sigSource"]),
            "instrCountChanged": len(changes["instrCount"]),
            "noReturnChanged": len(changes["noReturn"]),
            "thunkFlagChanged": len(changes["isThunk"]),
        },
        "dangerous": {
            "gradedFunctionsDestroyed": graded_destroyed,
            "gradedFunctionsRenamed": graded_renamed,
            "gradedNameSourceDemoted": graded_demoted,
            "gradedBoundsMoved": graded_bounds_moved,
            "gradedDestroyedCount": len(graded_destroyed),
            "gradedRenamedCount": len(graded_renamed),
            "gradedDemotedCount": len(graded_demoted),
            "gradedBoundsMovedCount": len(graded_bounds_moved),
        },
        "created": [
            {
                "address": k,
                "name": after[k]["name"],
                "bodyBytes": after[k]["bodyBytes"],
                "instrCount": after[k]["instrCount"],
                "nameSource": after[k]["nameSource"],
            }
            for k in created_keys
        ],
        "destroyed": [
            {
                "address": k,
                "name": before[k]["name"],
                "nameSource": before[k]["nameSource"],
                "bodyBytes": before[k]["bodyBytes"],
            }
            for k in destroyed_keys
        ],
        "changesByField": {k: v for k, v in changes.items()},
    }

    if args.pristine and created_keys:
        report["createdFalsePositiveAssessment"] = classify_created(
            [after[k] for k in created_keys], args.pristine, args.sample_created
        )

    counts = report["counts"]
    print(
        "DIFF before={before} after={after} created={created} destroyed={destroyed} "
        "boundsChanged={boundsChanged} namesChanged={namesChanged} "
        "signaturesChanged={signaturesChanged} paramCountChanged={paramCountChanged}".format(**counts)
    )
    dangerous = report["dangerous"]
    print(
        "DANGEROUS gradedDestroyed={gradedDestroyedCount} gradedRenamed={gradedRenamedCount} "
        "gradedDemoted={gradedDemotedCount} gradedBoundsMoved={gradedBoundsMovedCount}".format(**dangerous)
    )
    if "createdFalsePositiveAssessment" in report:
        print("CREATED_HEADS " + json.dumps(report["createdFalsePositiveAssessment"]["buckets"]))

    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
