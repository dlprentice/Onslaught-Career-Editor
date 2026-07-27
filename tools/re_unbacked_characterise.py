# SPDX-License-Identifier: GPL-3.0-or-later
"""Characterise the UNBACKED name-grade cohort mechanically, from bytes.

Read-only. Takes the pristine specimen, the name-grade ledger output, and the
mechanical verifier output (for measured function extents), and emits one row
per function with:

  grade, start, end, size, insns
  is_thunk        body is a single JMP rel32 (5 bytes) to another function
  callers         direct E8/E9 rel32 sites in .text resolving to this start
  callees         distinct direct call targets from inside this function
  ptr_refs        absolute DWORD references to this start found in .rdata/.data
                  (vtable slots, dispatch tables, callback tables)
  depth           BFS depth from the supplied roots over the direct call graph
                  (-1 = not reached by direct calls)

Usage:
  py -3 tools/re_unbacked_characterise.py \
      --binary <pristine BEA.exe> --grades <name-grades.tsv> \
      [--verify <re-verify.tsv>] [--roots-name-regex RE] --out-tsv <out.tsv>
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import re
import struct
import sys
from collections import defaultdict, deque
from pathlib import Path

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"


class Pe:
    def __init__(self, path: Path) -> None:
        self.data = path.read_bytes()
        pe = struct.unpack_from("<I", self.data, 0x3C)[0]
        ns = struct.unpack_from("<H", self.data, pe + 6)[0]
        opt = struct.unpack_from("<H", self.data, pe + 20)[0]
        self.image_base = struct.unpack_from("<I", self.data, pe + 24 + 28)[0]
        sec = pe + 24 + opt
        self.sections = []
        for i in range(ns):
            o = sec + i * 40
            name = self.data[o : o + 8].rstrip(b"\0").decode("ascii", "replace")
            vs, va, rs, rp = struct.unpack_from("<IIII", self.data, o + 8)
            self.sections.append((name, self.image_base + va, vs, rp, rs))

    def sec(self, name: str):
        for s in self.sections:
            if s[0] == name:
                return s
        raise KeyError(name)

    def off(self, va: int) -> int | None:
        for _n, base, vs, rp, rs in self.sections:
            if base <= va < base + max(vs, rs):
                d = va - base
                if d < rs:
                    return rp + d
        return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", type=Path, required=True)
    ap.add_argument("--grades", type=Path, required=True)
    ap.add_argument("--verify", type=Path)
    ap.add_argument("--roots-name-regex", default=r"^_?(WinMain|entry|_mainCRTStartup)")
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--allow-any-binary", action="store_true")
    args = ap.parse_args(argv)

    img = Pe(args.binary)
    digest = hashlib.sha256(img.data).hexdigest()
    if digest != PRISTINE_SHA256 and not args.allow_any_binary:
        print(f"refusing: sha256 {digest} != pristine {PRISTINE_SHA256}", file=sys.stderr)
        return 2
    print(f"specimen sha256 {digest}", file=sys.stderr)

    grades: dict[int, tuple[str, str]] = {}
    with args.grades.open(encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            grades[int(p[0], 16)] = (p[1], p[2])

    extents: dict[int, tuple[int, int]] = {}
    if args.verify:
        with args.verify.open(encoding="utf-8") as fh:
            hdr = next(fh).rstrip("\n").split("\t")
            ix = {n: i for i, n in enumerate(hdr)}
            for line in fh:
                p = line.rstrip("\n").split("\t")
                try:
                    va = int(p[ix["address"]], 16)
                    extents[va] = (int(p[ix["size"]]), int(p[ix["instructions"]]))
                except (ValueError, KeyError, IndexError):
                    continue

    starts = sorted(grades)
    sset = set(starts)

    # measured extent where available, else next-start gap
    ends: dict[int, int] = {}
    for i, va in enumerate(starts):
        if va in extents:
            ends[va] = va + extents[va][0]
        else:
            ends[va] = starts[i + 1] if i + 1 < len(starts) else va + 16

    _n, tbase, tvs, trp, trs = img.sec(".text")
    tend = tbase + tvs

    # single pass: every E8/E9 rel32 in .text
    callers: dict[int, int] = defaultdict(int)
    jmp_only_target: dict[int, int] = {}
    edges: dict[int, set[int]] = defaultdict(set)
    site_targets: list[tuple[int, int, int]] = []  # (site, target, opcode)
    data = img.data
    for o in range(trs - 5):
        op = data[trp + o]
        if op != 0xE8 and op != 0xE9:
            continue
        rel = struct.unpack_from("<i", data, trp + o + 1)[0]
        site = tbase + o
        tgt = (site + 5 + rel) & 0xFFFFFFFF
        if not (tbase <= tgt < tend):
            continue
        site_targets.append((site, tgt, op))

    for site, tgt, op in site_targets:
        if tgt in sset:
            callers[tgt] += 1
        i = bisect.bisect_right(starts, site) - 1
        if i >= 0:
            owner = starts[i]
            if site < ends[owner]:
                edges[owner].add(tgt)
                if op == 0xE9 and site == owner and ends[owner] - owner <= 8:
                    jmp_only_target[owner] = tgt

    # absolute DWORD refs to function starts, from .rdata and .data
    ptr_refs: dict[int, int] = defaultdict(int)
    for sname in (".rdata", ".data"):
        _n2, base2, vs2, rp2, rs2 = img.sec(sname)
        for o in range(0, rs2 - 3, 4):
            v = struct.unpack_from("<I", data, rp2 + o)[0]
            if v in sset:
                ptr_refs[v] += 1

    # BFS depth from roots
    rx = re.compile(args.roots_name_regex)
    roots = [va for va in starts if rx.search(grades[va][0])]
    depth: dict[int, int] = {}
    dq = deque()
    for r in roots:
        depth[r] = 0
        dq.append(r)
    while dq:
        cur = dq.popleft()
        for nxt in edges.get(cur, ()):  # direct calls only
            if nxt in sset and nxt not in depth:
                depth[nxt] = depth[cur] + 1
                dq.append(nxt)

    with args.out_tsv.open("w", encoding="utf-8", newline="\n") as out:
        out.write("address\tname\tgrade\tstart\tend\tsize\tinsns\tis_thunk\tthunk_target\t"
                  "callers\tcallees\tptr_refs\tdepth\n")
        for va in starts:
            name, grade = grades[va]
            size = ends[va] - va
            insns = extents.get(va, (0, 0))[1]
            th = va in jmp_only_target
            out.write(
                f"0x{va:08x}\t{name}\t{grade}\t0x{va:08x}\t0x{ends[va]:08x}\t{size}\t{insns}\t"
                f"{int(th)}\t{('0x%08x' % jmp_only_target[va]) if th else ''}\t"
                f"{callers.get(va,0)}\t{len(edges.get(va,()))}\t{ptr_refs.get(va,0)}\t"
                f"{depth.get(va,-1)}\n"
            )
    print(f"roots: {len(roots)} {[grades[r][0] for r in roots][:8]}", file=sys.stderr)
    print(f"functions: {len(starts)}  direct call sites: {len(site_targets)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
