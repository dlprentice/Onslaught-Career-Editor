#!/usr/bin/env python3
"""Static FF/2 (CALL r/m) + absolute-pointer ownership for residual open-code spans.

Cheapest falsifier after E8-only envelope proof returned 0 external CALL xrefs:

  1. Decode every FF /2 (CALL r/m32) and FF /4 (JMP r/m32) in .text
  2. For CALL/JMP [disp32]: resolve the pointed-to dword; if it lands in a
     residual span (or at a candidate entry), record the site + owner
  3. For absolute image dwords that equal a residual VA: record ptr site,
     containing Gen10 function (if any), section, and 16B context
  4. Grade each residual entry candidate:

       INDIRECT_CALL_TARGET
         ≥1 CALL [mem] whose loaded dword equals the entry (or FF /2 path
         that resolves to entry via absolute m32)
       ABS_PTR_ONLY
         absolute dword(s) point at entry/span but no CALL-mem consumer found
       STILL_NO_INBOUND
         no E8 (from prior plate), no resolved CALL-mem, no abs ptr at entry

Does not invent function names. Does not mutate Gen10/Ghidra.
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


def section_at(va: int, image_base: int, sections) -> str:
    rva = va - image_base
    for name, sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            return name
    return "?"


def load_gen10_functions(tsv: Path) -> list[dict]:
    lines = tsv.read_text(encoding="utf-8").splitlines()
    hi = next(i for i, l in enumerate(lines) if l.startswith("entityKey\t"))
    cols = lines[hi].split("\t")
    rows = []
    for line in lines[hi + 1 :]:
        if not line.strip():
            continue
        parts = line.split("\t")
        rows.append({cols[j]: parts[j] if j < len(parts) else "" for j in range(len(cols))})
    return rows


def parse_body_ranges(row: dict, image_base: int = 0x400000) -> list[tuple[int, int]]:
    """Return list of [start,end) VAs from bodyRangesRva."""
    br = row.get("bodyRangesRva") or ""
    out = []
    for part in br.split(";"):
        part = part.strip()
        if not part or "-" not in part:
            continue
        a, b = part.split("-", 1)
        try:
            out.append((image_base + int(a, 16), image_base + int(b, 16)))
        except Exception:
            continue
    return out


def owner_function(va: int, gen10_ranges: list[tuple[int, int, str]]) -> str:
    for lo, hi, name in gen10_ranges:
        if lo <= va < hi:
            return name
    return ""


def decode_modrm_mem(
    data: bytes, rawptr: int, off: int, base_va: int, image_base: int
) -> dict | None:
    """Decode memory operand after FF opcode at off; return site info or None.

    Supports only forms that can resolve to an absolute target or pointer slot:
      - mod=00 rm=101: [disp32]  → absolute address of operand
      - mod=01/10 with rm=101 (disp32) same for ebp-relative we skip
    We primarily care about [disp32] absolute.
    """
    if off + 1 >= len(data) - rawptr:
        return None
    modrm = data[rawptr + off + 1]
    mod = (modrm >> 6) & 3
    reg = (modrm >> 3) & 7  # /digit
    rm = modrm & 7
    if reg not in (2, 4):  # CALL /2 or JMP /4
        return None
    kind = "CALL" if reg == 2 else "JMP"
    # SIB?
    pos = off + 2
    if mod != 3 and rm == 4:
        # SIB byte
        if rawptr + pos >= len(data):
            return None
        sib = data[rawptr + pos]
        pos += 1
        base = sib & 7
        if mod == 0 and base == 5:
            # [disp32]
            if rawptr + pos + 4 > len(data):
                return None
            disp = struct.unpack_from("<I", data, rawptr + pos)[0]
            site = base_va + off
            return {
                "kind": kind,
                "form": "SIB_disp32",
                "siteVa": site,
                "insnBytes": 2 + 1 + 4,  # FF modrm sib disp32
                "operandVa": disp,  # absolute address of memory operand
            }
        return None  # other SIB forms: register-relative, skip for ownership
    if mod == 0 and rm == 5:
        # [disp32]
        if rawptr + pos + 4 > len(data):
            return None
        disp = struct.unpack_from("<I", data, rawptr + pos)[0]
        site = base_va + off
        return {
            "kind": kind,
            "form": "disp32",
            "siteVa": site,
            "insnBytes": 6,
            "operandVa": disp,
        }
    if mod == 3:
        # CALL/JMP reg — cannot resolve statically without dataflow
        return {
            "kind": kind,
            "form": "reg",
            "siteVa": base_va + off,
            "insnBytes": 2,
            "operandVa": None,
            "reg": rm,
        }
    return None


def scan_ff_rm(data: bytes, image_base: int, sections) -> list[dict]:
    text = next((s for s in sections if s[0] == ".text"), None)
    if text is None:
        text = max(sections, key=lambda s: s[4])
    _name, vaddr, _vs, rawptr, rawsize = text
    base_va = image_base + vaddr
    out = []
    i = 0
    while i < rawsize - 2:
        if data[rawptr + i] != 0xFF:
            i += 1
            continue
        dec = decode_modrm_mem(data, rawptr, i, base_va, image_base)
        if dec is None:
            i += 1
            continue
        out.append(dec)
        i += max(1, dec.get("insnBytes", 1))
    return out


def scan_absolute_ptrs(
    data: bytes,
    image_base: int,
    sections,
    lo: int,
    hi: int,
    *,
    byte_step: int = 4,
) -> list[dict]:
    """Find image dwords equal to a VA in [lo, hi).

    byte_step=4 is the default PE-aligned pointer walk. For residual code
    islands, also run byte_step=1 on .text only to catch unaligned imm32
    embeddings (e.g. mov reg/mem, imm32) that a 4-byte stride misses.
    """
    hits = []
    seen = set()
    for name, vaddr, vsize, rawptr, rawsize in sections:
        step = byte_step
        if byte_step == 1 and name != ".text":
            # unaligned pass is .text-only (imm32 in code)
            continue
        for off in range(0, rawsize - 3, step):
            val = struct.unpack_from("<I", data, rawptr + off)[0]
            if not (lo <= val < hi):
                continue
            site = image_base + vaddr + off
            key = (site, val)
            if key in seen:
                continue
            seen.add(key)
            ctx_off = max(0, off - 8)
            ctx = data[rawptr + ctx_off : rawptr + off + 12]
            hits.append(
                {
                    "ptrSiteVa": site,
                    "targetVa": val,
                    "section": name,
                    "contextHex": ctx.hex(),
                    "scanStep": step,
                }
            )
    return hits


def analyze_spans(
    specimen: Path,
    spans: list[dict],
    gen10_tsv: Path | None,
) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen sha256 mismatch: {sha}")
    image_base, sections = pe_map(data)

    gen10 = load_gen10_functions(gen10_tsv) if gen10_tsv and gen10_tsv.is_file() else []
    gen10_ranges: list[tuple[int, int, str]] = []
    for r in gen10:
        name = r.get("currentName") or ""
        for a, b in parse_body_ranges(r, image_base):
            gen10_ranges.append((a, b, name))
    # also index by entry for quick name
    gen10_by_entry = {}
    for r in gen10:
        try:
            gen10_by_entry[int(r["entryVa"], 16)] = r.get("currentName") or ""
        except Exception:
            pass

    ff_ops = scan_ff_rm(data, image_base, sections)
    # Resolve CALL/JMP [disp32] → loaded dword
    resolved_mem_calls = []
    for op in ff_ops:
        if op.get("operandVa") is None:
            continue
        if op.get("form") not in ("disp32", "SIB_disp32"):
            continue
        ptr_slot = op["operandVa"]
        o = va_to_off(ptr_slot, image_base, sections)
        if o is None:
            continue
        target = struct.unpack_from("<I", data, o)[0]
        resolved_mem_calls.append(
            {
                **op,
                "ptrSlotVa": ptr_slot,
                "resolvedTargetVa": target,
                "ptrSlotSection": section_at(ptr_slot, image_base, sections),
                "callSiteOwner": owner_function(op["siteVa"], gen10_ranges),
            }
        )

    results = []
    for sp in spans:
        lo = int(sp["startVa"], 16)
        hi = int(sp["endVa"], 16)
        candidates = []
        for c in sp.get("candidates") or [sp["startVa"]]:
            candidates.append(int(c, 16) if isinstance(c, str) else int(c))
        candidates = sorted(set(c for c in candidates if lo <= c < hi))

        # Aligned PE walk + unaligned .text imm32 walk (sibling immediates).
        abs_hits = scan_absolute_ptrs(data, image_base, sections, lo, hi, byte_step=4)
        abs_hits += scan_absolute_ptrs(
            data, image_base, sections, lo, hi, byte_step=1
        )
        # de-dupe by (site, target) already inside scanner across steps
        dedup = {}
        for h in abs_hits:
            dedup[(h["ptrSiteVa"], h["targetVa"])] = h
        abs_hits = list(dedup.values())
        abs_hits.sort(key=lambda h: h["ptrSiteVa"])
        for h in abs_hits:
            h["ptrSiteOwner"] = owner_function(h["ptrSiteVa"], gen10_ranges)
            h["targetIsCandidate"] = h["targetVa"] in candidates
            h["internalToSpan"] = lo <= h["ptrSiteVa"] < hi
            h["ptrSiteVa"] = fmt_va(h["ptrSiteVa"])
            h["targetVa"] = fmt_va(h["targetVa"])

        # mem-calls that resolve into span
        mem_into = [
            m
            for m in resolved_mem_calls
            if lo <= m["resolvedTargetVa"] < hi
        ]
        mem_into_fmt = []
        for m in mem_into:
            mem_into_fmt.append(
                {
                    "kind": m["kind"],
                    "form": m["form"],
                    "siteVa": fmt_va(m["siteVa"]),
                    "ptrSlotVa": fmt_va(m["ptrSlotVa"]),
                    "resolvedTargetVa": fmt_va(m["resolvedTargetVa"]),
                    "ptrSlotSection": m["ptrSlotSection"],
                    "callSiteOwner": m["callSiteOwner"],
                    "targetIsCandidate": m["resolvedTargetVa"] in candidates,
                }
            )

        cand_rows = []
        for entry in candidates:
            mem_hits = [
                m for m in mem_into_fmt if int(m["resolvedTargetVa"], 16) == entry
            ]
            abs_at = [h for h in abs_hits if int(h["targetVa"], 16) == entry]
            if mem_hits:
                grade = "INDIRECT_CALL_TARGET"
                reason = f"call_mem_sites={len(mem_hits)}"
            elif abs_at:
                grade = "ABS_PTR_ONLY"
                reason = f"abs_ptrs={len(abs_at)} owners={[h.get('ptrSiteOwner') or h['section'] for h in abs_at]}"
            else:
                # any abs into span that is near entry? still entry-level STILL_NO
                grade = "STILL_NO_INBOUND"
                reason = "no_E8_no_call_mem_no_abs_at_entry"
            cand_rows.append(
                {
                    "entryVa": fmt_va(entry),
                    "grade": grade,
                    "reason": reason,
                    "callMemHits": mem_hits,
                    "absolutePtrsAtEntry": abs_at,
                    "gen10NameAtEntry": gen10_by_entry.get(entry, ""),
                }
            )

        # span-level grades
        n_indirect = sum(1 for c in cand_rows if c["grade"] == "INDIRECT_CALL_TARGET")
        n_abs = sum(1 for c in cand_rows if c["grade"] == "ABS_PTR_ONLY")
        n_none = sum(1 for c in cand_rows if c["grade"] == "STILL_NO_INBOUND")

        results.append(
            {
                "startVa": fmt_va(lo),
                "endVa": fmt_va(hi),
                "bytes": hi - lo,
                "prevFunc": sp.get("prevFunc", ""),
                "nextFunc": sp.get("nextFunc", ""),
                "absolutePtrCountIntoSpan": len(abs_hits),
                "absolutePtrs": abs_hits,
                "callMemResolvedIntoSpan": len(mem_into_fmt),
                "callMemHits": mem_into_fmt,
                "candidates": cand_rows,
                "gradeCounts": {
                    "INDIRECT_CALL_TARGET": n_indirect,
                    "ABS_PTR_ONLY": n_abs,
                    "STILL_NO_INBOUND": n_none,
                },
                "anyIndirectCallTarget": n_indirect > 0,
            }
        )

    # global FF stats
    form_counts = Counter(o.get("form") for o in ff_ops)
    return {
        "schema": "bea.re.residual-indirect-inbound.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_spans": len(results),
        "n_spans_with_indirect_call_target": sum(
            1 for r in results if r["anyIndirectCallTarget"]
        ),
        "ff_rm_scan": {
            "n_ff_rm_ops": len(ff_ops),
            "form_counts": dict(form_counts),
            "n_resolved_mem_calls": len(resolved_mem_calls),
        },
        "rows": results,
        "note": (
            "INDIRECT_CALL_TARGET = CALL/JMP [disp32] loads a dword equal to "
            "candidate entry. Register-indirect CALL reg not resolved (needs "
            "dataflow). No names invented. Gen10 not mutated."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--spans-json", type=Path, required=True)
    p.add_argument("--gen10-functions-tsv", type=Path, default=None)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    raw = json.loads(args.spans_json.read_text(encoding="utf-8"))
    spans = raw["spans"] if isinstance(raw, dict) and "spans" in raw else raw
    result = analyze_spans(args.specimen, spans, args.gen10_functions_tsv)
    summary = {k: v for k, v in result.items() if k != "rows"}
    compact = []
    for r in result["rows"]:
        compact.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r["bytes"],
                "prevFunc": r["prevFunc"],
                "nextFunc": r["nextFunc"],
                "absolutePtrCountIntoSpan": r["absolutePtrCountIntoSpan"],
                "callMemResolvedIntoSpan": r["callMemResolvedIntoSpan"],
                "gradeCounts": r["gradeCounts"],
                "anyIndirectCallTarget": r["anyIndirectCallTarget"],
                "callMemHits": r["callMemHits"],
                "absolutePtrs": [
                    {
                        "ptrSiteVa": h["ptrSiteVa"],
                        "targetVa": h["targetVa"],
                        "section": h["section"],
                        "ptrSiteOwner": h.get("ptrSiteOwner", ""),
                        "targetIsCandidate": h.get("targetIsCandidate", False),
                        "internalToSpan": h.get("internalToSpan", False),
                        "scanStep": h.get("scanStep"),
                    }
                    for h in r["absolutePtrs"]
                ],
                "candidateGrades": [
                    {
                        "entryVa": c["entryVa"],
                        "grade": c["grade"],
                        "reason": c["reason"],
                    }
                    for c in r["candidates"]
                ],
            }
        )
    summary["spanSummaries"] = compact
    print(json.dumps(summary, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = summary if args.summary_only else result
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("RESIDUAL_INDIRECT_INBOUND_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
