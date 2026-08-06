#!/usr/bin/env python3
"""Peephole: mov/push imm32(=candidate) near FF/2 CALL-reg or call [reg+disp].

Cheapest static falsifier after E8 + CALL [disp32] returned zero inbound for
residual open-code islands. Targets externally owned candidates first:

  0x005b4ed0, 0x005b5370  (imm32 in CDXTexture__InitJpegDctQuantPipeline)
  0x005adf50              (imm32 in CDXTexture__InitBlockCoefficientHistory)

Also accepts additional candidate VAs via JSON.

What it looks for (specimen-static, pristine only):

  1. Sites where a little-endian imm32 equals a candidate VA:
       - B8+rd id        mov r32, imm32
       - C7 /0 ... id    mov r/m32, imm32 (modrm forms)
       - 68 id           push imm32
  2. Within a byte window (default ±48 around the imm) any of:
       - FF /2 reg       CALL r32
       - FF /2 [reg+disp8/32]  CALL [reg+disp]  (slot consumer)
       - FF /4 reg / [reg+disp] JMP forms (noted, weaker)
  3. Grade:
       SLOT_CONSUMER_NEAR_IMM
         CALL [reg+disp] within window of imm32(=candidate)
       CALL_REG_NEAR_IMM
         CALL reg within window of imm32(=candidate)
         (same-reg preference when mov targets that reg)
       IMM_ONLY_NO_NEAR_CALL
         imm32 found, no CALL-reg/mem in window
       NO_IMM
         candidate never appears as imm32 in .text

Does not invent names. Does not mutate Gen10/Ghidra.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

# Externally owned candidates from residual-indirect-inbound plate
DEFAULT_CANDIDATES = [
    0x005B4ED0,  # InitJpegDctQuantPipeline embeds
    0x005B5370,  # InitJpegDctQuantPipeline embeds
    0x005ADF50,  # InitBlockCoefficientHistory embeds
]

REG_NAMES = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"]


def pe_map(data: bytes):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    opt = e_lfanew + 24
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_off = e_lfanew + 24 + size_opt
    sections = []
    for i in range(num_sections):
        o = sec_off + i * 40
        name = data[o : o + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((name, va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for _name, sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            if rva - sva >= rawsize:
                return None
            return rawptr + (rva - sva)
    return None


def fmt_va(va: int) -> str:
    return f"0x{va:08x}"


def load_gen10_ranges(tsv: Path | None, image_base: int) -> list[tuple[int, int, str]]:
    if tsv is None or not tsv.is_file():
        return []
    lines = tsv.read_text(encoding="utf-8").splitlines()
    hi = next(i for i, l in enumerate(lines) if l.startswith("entityKey\t"))
    cols = lines[hi].split("\t")
    ranges: list[tuple[int, int, str]] = []
    for line in lines[hi + 1 :]:
        if not line.strip():
            continue
        parts = line.split("\t")
        row = {cols[j]: parts[j] if j < len(parts) else "" for j in range(len(cols))}
        name = row.get("currentName") or ""
        br = row.get("bodyRangesRva") or ""
        for part in br.split(";"):
            part = part.strip()
            if not part or "-" not in part:
                continue
            a, b = part.split("-", 1)
            try:
                ranges.append(
                    (image_base + int(a, 16), image_base + int(b, 16), name)
                )
            except Exception:
                continue
    return ranges


def owner_at(va: int, ranges: list[tuple[int, int, str]]) -> str:
    for lo, hi, name in ranges:
        if lo <= va < hi:
            return name
    return ""


def find_imm32_sites(
    data: bytes, image_base: int, sections, candidates: set[int]
) -> list[dict]:
    """Find .text sites encoding imm32 equal to a candidate.

    Returns sites with kind, dest reg (if any), and VA of the imm field.
    """
    text = next((s for s in sections if s[0] == ".text"), None)
    if text is None:
        return []
    _name, vaddr, _vs, rawptr, rawsize = text
    base_va = image_base + vaddr
    hits: list[dict] = []

    # 1) mov r32, imm32  = B8+rd id  (5 bytes)
    for off in range(0, rawsize - 5):
        op = data[rawptr + off]
        if 0xB8 <= op <= 0xBF:
            imm = struct.unpack_from("<I", data, rawptr + off + 1)[0]
            if imm in candidates:
                hits.append(
                    {
                        "kind": "MOV_R32_IMM32",
                        "siteVa": base_va + off,
                        "immVa": base_va + off + 1,
                        "immValue": imm,
                        "destReg": op - 0xB8,
                        "destRegName": REG_NAMES[op - 0xB8],
                        "insnBytes": 5,
                    }
                )

    # 2) push imm32 = 68 id
    for off in range(0, rawsize - 5):
        if data[rawptr + off] != 0x68:
            continue
        imm = struct.unpack_from("<I", data, rawptr + off + 1)[0]
        if imm in candidates:
            hits.append(
                {
                    "kind": "PUSH_IMM32",
                    "siteVa": base_va + off,
                    "immVa": base_va + off + 1,
                    "immValue": imm,
                    "destReg": None,
                    "destRegName": None,
                    "insnBytes": 5,
                }
            )

    # 3) mov r/m32, imm32 = C7 /0
    for off in range(0, rawsize - 6):
        if data[rawptr + off] != 0xC7:
            continue
        modrm = data[rawptr + off + 1]
        mod = (modrm >> 6) & 3
        reg = (modrm >> 3) & 7
        rm = modrm & 7
        if reg != 0:
            continue
        pos = off + 2
        dest_reg = None
        if mod == 3:
            # C7 C0+rd id  mov r32, imm32 (less common than B8)
            dest_reg = rm
            if rawptr + pos + 4 > len(data):
                continue
            imm = struct.unpack_from("<I", data, rawptr + pos)[0]
            if imm not in candidates:
                continue
            hits.append(
                {
                    "kind": "MOV_RM32_IMM32_REG",
                    "siteVa": base_va + off,
                    "immVa": base_va + pos,
                    "immValue": imm,
                    "destReg": dest_reg,
                    "destRegName": REG_NAMES[dest_reg],
                    "insnBytes": 6,
                }
            )
            continue
        # memory forms — skip SIB complexity partially
        if rm == 4:
            if rawptr + pos >= len(data):
                continue
            sib = data[rawptr + pos]
            pos += 1
            base = sib & 7
            if mod == 0 and base == 5:
                pos += 4  # disp32
            elif mod == 1:
                pos += 1
            elif mod == 2:
                pos += 4
        else:
            if mod == 0 and rm == 5:
                pos += 4
            elif mod == 1:
                pos += 1
            elif mod == 2:
                pos += 4
        if rawptr + pos + 4 > len(data):
            continue
        imm = struct.unpack_from("<I", data, rawptr + pos)[0]
        if imm not in candidates:
            continue
        hits.append(
            {
                "kind": "MOV_RM32_IMM32_MEM",
                "siteVa": base_va + off,
                "immVa": base_va + pos,
                "immValue": imm,
                "destReg": None,
                "destRegName": None,
                "insnBytes": pos + 4 - off,
            }
        )

    # de-dupe by (siteVa, immValue, kind)
    seen = set()
    out = []
    for h in hits:
        key = (h["siteVa"], h["immValue"], h["kind"])
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    out.sort(key=lambda h: h["siteVa"])
    return out


def find_call_reg_and_mem_in_window(
    data: bytes,
    image_base: int,
    sections,
    window_lo: int,
    window_hi: int,
) -> list[dict]:
    """Find FF /2 and FF /4 forms (reg and [reg+disp]) in [window_lo, window_hi)."""
    text = next((s for s in sections if s[0] == ".text"), None)
    if text is None:
        return []
    _name, vaddr, _vs, rawptr, rawsize = text
    base_va = image_base + vaddr
    # convert window VAs to offsets in .text
    lo_off = window_lo - base_va
    hi_off = window_hi - base_va
    lo_off = max(0, lo_off)
    hi_off = min(rawsize - 2, hi_off)
    found = []
    i = lo_off
    while i < hi_off:
        if data[rawptr + i] != 0xFF:
            i += 1
            continue
        modrm = data[rawptr + i + 1]
        mod = (modrm >> 6) & 3
        reg = (modrm >> 3) & 7
        rm = modrm & 7
        if reg not in (2, 4):
            i += 1
            continue
        kind = "CALL" if reg == 2 else "JMP"
        site = base_va + i
        if mod == 3:
            found.append(
                {
                    "kind": kind,
                    "form": "reg",
                    "siteVa": site,
                    "reg": rm,
                    "regName": REG_NAMES[rm],
                    "disp": None,
                    "insnBytes": 2,
                }
            )
            i += 2
            continue
        # mem forms with optional SIB / disp
        pos = i + 2
        disp = 0
        if rm == 4:
            if pos >= rawsize:
                i += 1
                continue
            sib = data[rawptr + pos]
            pos += 1
            base = sib & 7
            if mod == 0 and base == 5:
                if pos + 4 > rawsize:
                    i += 1
                    continue
                disp = struct.unpack_from("<i", data, rawptr + pos)[0]
                pos += 4
            elif mod == 1:
                if pos >= rawsize:
                    i += 1
                    continue
                disp = struct.unpack_from("<b", data, rawptr + pos)[0]
                pos += 1
            elif mod == 2:
                if pos + 4 > rawsize:
                    i += 1
                    continue
                disp = struct.unpack_from("<i", data, rawptr + pos)[0]
                pos += 4
            found.append(
                {
                    "kind": kind,
                    "form": "sib_mem",
                    "siteVa": site,
                    "reg": None,
                    "regName": None,
                    "disp": disp,
                    "insnBytes": pos - i,
                }
            )
            i = pos
            continue
        # non-SIB mem
        if mod == 0 and rm == 5:
            # [disp32] absolute — already covered by prior plate; still note
            if pos + 4 > rawsize:
                i += 1
                continue
            disp_u = struct.unpack_from("<I", data, rawptr + pos)[0]
            found.append(
                {
                    "kind": kind,
                    "form": "disp32_abs",
                    "siteVa": site,
                    "reg": None,
                    "regName": None,
                    "disp": disp_u,
                    "insnBytes": 6,
                }
            )
            i = pos + 4
            continue
        if mod == 0:
            found.append(
                {
                    "kind": kind,
                    "form": "mem_reg",
                    "siteVa": site,
                    "reg": rm,
                    "regName": REG_NAMES[rm],
                    "disp": 0,
                    "insnBytes": 2,
                }
            )
            i += 2
            continue
        if mod == 1:
            if pos >= rawsize:
                i += 1
                continue
            disp = struct.unpack_from("<b", data, rawptr + pos)[0]
            found.append(
                {
                    "kind": kind,
                    "form": "mem_reg_disp8",
                    "siteVa": site,
                    "reg": rm,
                    "regName": REG_NAMES[rm],
                    "disp": disp,
                    "insnBytes": 3,
                }
            )
            i = pos + 1
            continue
        if mod == 2:
            if pos + 4 > rawsize:
                i += 1
                continue
            disp = struct.unpack_from("<i", data, rawptr + pos)[0]
            found.append(
                {
                    "kind": kind,
                    "form": "mem_reg_disp32",
                    "siteVa": site,
                    "reg": rm,
                    "regName": REG_NAMES[rm],
                    "disp": disp,
                    "insnBytes": 6,
                }
            )
            i = pos + 4
            continue
        i += 1
    return found


def analyze(
    specimen: Path,
    candidates: list[int],
    window: int,
    gen10_tsv: Path | None,
) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen sha256 mismatch: {sha}")
    image_base, sections = pe_map(data)
    cand_set = set(candidates)
    ranges = load_gen10_ranges(gen10_tsv, image_base)

    imm_sites = find_imm32_sites(data, image_base, sections, cand_set)
    by_cand: dict[int, list[dict]] = defaultdict(list)

    for site in imm_sites:
        site["owner"] = owner_at(site["siteVa"], ranges)
        # window around the instruction (not just the imm field)
        wlo = site["siteVa"] - window
        whi = site["siteVa"] + site["insnBytes"] + window
        calls = find_call_reg_and_mem_in_window(
            data, image_base, sections, wlo, whi
        )
        # prefer CALL over JMP; mem forms for slot consumers
        call_reg = [
            c
            for c in calls
            if c["kind"] == "CALL" and c["form"] == "reg"
        ]
        call_mem = [
            c
            for c in calls
            if c["kind"] == "CALL"
            and c["form"] in ("mem_reg", "mem_reg_disp8", "mem_reg_disp32", "sib_mem")
        ]
        # Calls that appear *after* the imm site (possible consumers).
        after_calls_mem = [c for c in call_mem if c["siteVa"] > site["siteVa"]]
        after_calls_reg = [c for c in call_reg if c["siteVa"] > site["siteVa"]]
        same_reg_calls = []
        if site.get("destReg") is not None:
            same_reg_calls = [
                c
                for c in after_calls_reg
                if c.get("reg") == site["destReg"]
            ]

        # Pattern: mov [mem], imm32(=candidate) is a slot INSTALL, not a call.
        # Nearby CALL [reg] *before* the store is typically an allocator
        # (alloc then fill vtable/callback fields). Do not grade that as consumer.
        is_mem_install = site["kind"] in (
            "MOV_RM32_IMM32_MEM",
            "MOV_RM32_IMM32_REG",
        ) and site.get("destReg") is None

        if same_reg_calls:
            grade = "CALL_REG_NEAR_IMM"
            reason = (
                f"same_reg_CALL_{site['destRegName']}_after_imm"
                f"_sites={len(same_reg_calls)}"
            )
        elif after_calls_mem and not is_mem_install:
            # CALL [mem] after a mov-reg-imm may be a true consumer (weak).
            grade = "SLOT_CONSUMER_NEAR_IMM"
            reason = f"call_mem_after_imm={len(after_calls_mem)}"
        elif is_mem_install:
            grade = "CALLBACK_SLOT_INSTALL"
            reason = (
                f"mov_mem_imm32 install; "
                f"call_mem_before={len(call_mem) - len(after_calls_mem)} "
                f"call_mem_after={len(after_calls_mem)} "
                f"(before typically allocator, not consumer)"
            )
        elif after_calls_reg:
            grade = "CALL_REG_NEAR_IMM"
            reason = f"any_CALL_reg_after_imm={len(after_calls_reg)}"
        elif call_mem or call_reg:
            grade = "IMM_ONLY_NO_NEAR_CALL"
            reason = (
                f"imm_kind={site['kind']}; "
                f"nearby_calls_only_before_imm "
                f"(call_mem={len(call_mem)} call_reg={len(call_reg)})"
            )
        else:
            grade = "IMM_ONLY_NO_NEAR_CALL"
            reason = f"imm_kind={site['kind']}"

        site["windowLo"] = wlo
        site["windowHi"] = whi
        site["grade"] = grade
        site["reason"] = reason
        site["nearCallReg"] = call_reg
        site["nearCallMem"] = call_mem
        site["sameRegCallReg"] = same_reg_calls
        by_cand[site["immValue"]].append(site)

    cand_rows = []
    for c in candidates:
        sites = by_cand.get(c, [])
        if not sites:
            cand_rows.append(
                {
                    "candidateVa": fmt_va(c),
                    "grade": "NO_IMM",
                    "reason": "no_imm32_in_text",
                    "nImmSites": 0,
                    "sites": [],
                }
            )
            continue
        # best grade priority (call evidence > install > bare imm)
        order = {
            "SLOT_CONSUMER_NEAR_IMM": 0,
            "CALL_REG_NEAR_IMM": 1,
            "CALLBACK_SLOT_INSTALL": 2,
            "IMM_ONLY_NO_NEAR_CALL": 3,
            "NO_IMM": 4,
        }
        best = min(sites, key=lambda s: order.get(s["grade"], 9))
        cand_rows.append(
            {
                "candidateVa": fmt_va(c),
                "grade": best["grade"],
                "reason": best["reason"],
                "nImmSites": len(sites),
                "bestSiteVa": fmt_va(best["siteVa"]),
                "bestOwner": best.get("owner", ""),
                "sites": [
                    {
                        "kind": s["kind"],
                        "siteVa": fmt_va(s["siteVa"]),
                        "owner": s.get("owner", ""),
                        "destRegName": s.get("destRegName"),
                        "grade": s["grade"],
                        "reason": s["reason"],
                        "nNearCallReg": len(s["nearCallReg"]),
                        "nNearCallMem": len(s["nearCallMem"]),
                        "nSameRegCall": len(s["sameRegCallReg"]),
                        "nearCallRegSites": [
                            {
                                "siteVa": fmt_va(c["siteVa"]),
                                "regName": c.get("regName"),
                            }
                            for c in s["nearCallReg"][:8]
                        ],
                        "nearCallMemSites": [
                            {
                                "siteVa": fmt_va(c["siteVa"]),
                                "form": c["form"],
                                "regName": c.get("regName"),
                                "disp": c.get("disp"),
                            }
                            for c in s["nearCallMem"][:8]
                        ],
                    }
                    for s in sites
                ],
            }
        )

    grade_counts = Counter(r["grade"] for r in cand_rows)
    return {
        "schema": "bea.re.callreg-imm-peephole.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "windowBytes": window,
        "candidates": [fmt_va(c) for c in candidates],
        "n_imm_sites_total": len(imm_sites),
        "gradeCounts": dict(grade_counts),
        "n_slot_consumer": grade_counts.get("SLOT_CONSUMER_NEAR_IMM", 0),
        "n_call_reg_near": grade_counts.get("CALL_REG_NEAR_IMM", 0),
        "n_callback_install": grade_counts.get("CALLBACK_SLOT_INSTALL", 0),
        "n_imm_only": grade_counts.get("IMM_ONLY_NO_NEAR_CALL", 0),
        "n_no_imm": grade_counts.get("NO_IMM", 0),
        "rows": cand_rows,
        "note": (
            "CALLBACK_SLOT_INSTALL = mov [mem], imm32(=candidate) with nearby "
            "CALL [reg] typically an allocator, not a call to the candidate. "
            "CALL_REG / SLOT_CONSUMER grades require call *after* imm and are "
            "still co-location hypotheses without full dataflow. "
            "No names invented. Gen10 not mutated."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument(
        "--candidates",
        nargs="*",
        default=None,
        help="candidate VAs (hex); default externally owned trio",
    )
    p.add_argument("--window", type=int, default=48)
    p.add_argument("--gen10-functions-tsv", type=Path, default=None)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    if args.candidates:
        cands = [int(x, 0) for x in args.candidates]
    else:
        cands = list(DEFAULT_CANDIDATES)
    result = analyze(args.specimen, cands, args.window, args.gen10_functions_tsv)
    print(json.dumps(result, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("CALLREG_IMM_PEEPHOLE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
