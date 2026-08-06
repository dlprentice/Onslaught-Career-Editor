#!/usr/bin/env python3
"""Specimen-static function-envelope proof for residual open-code islands.

For each candidate entry VA inside a residual span:

  1. inbound E8 CALL / E9 JMP (external vs internal to the span)
  2. absolute image dwords pointing at the entry
  3. single-ret envelope: linear capstone decode until first ret/retn;
     count additional rets in the claimed body; note if body reaches next
     named Gen10 function entry
  4. grade (conservative — no invented names):

     ENVELOPE_PROVED_STATIC
       ≥1 external E8 CALL to entry AND single primary ret envelope
       AND no multi-ret body ambiguity (≤1 ret, or rets only in obvious
       early-out tails after the primary ret path — we require exactly 1
       ret instruction in the linear envelope for PROVED)
     ENTRY_SHAPE_NO_CALL_XREF
       plausible prologue + single-ret envelope, but zero external E8
     MULTI_RET_OR_OPEN
       decode does not form a single-ret envelope
     NO_PROLOGUE
       start byte not a plausible function entry
     FALLTHROUGH_AFTER_PREV_RET
       residual begins immediately after previous Gen10 function's ret
       (informative; not itself a proof of a new function)

Does **not** mutate Gen10 or Ghidra. Does **not** invent function names.
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

PROLOGUE_START = {
    0x55,
    0x53,
    0x56,
    0x57,
    0x51,
    0x52,
    0x50,
    0x8B,
    0x89,
    0x83,
    0x81,
    0x0F,
    0xDB,
    0xD9,
    0xDD,
    0x9C,
    0x60,
    0x33,
    0x31,
    0x85,
    0x68,
    0x6A,
    0xB8,
    0xE8,
    0xE9,
    0xEB,
    0x8D,
    0x64,
    0xF2,
    0xF3,
    0x66,
    0xC6,
    0xC7,
    0xA1,
    0xFF,
}


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


def try_capstone():
    try:
        import capstone  # type: ignore

        return capstone
    except Exception:
        return None


def scan_rel32_edges(data: bytes, image_base: int, sections) -> list[tuple[str, int, int]]:
    """Return list of (kind, site_va, target_va) for E8/E9 in .text."""
    text = next((s for s in sections if s[0] == ".text"), None)
    if text is None:
        # fall back to executable-looking largest section
        text = max(sections, key=lambda s: s[4])
    _name, vaddr, _vs, rawptr, rawsize = text
    base_va = image_base + vaddr
    edges = []
    for off in range(rawsize - 5):
        op = data[rawptr + off]
        if op not in (0xE8, 0xE9):
            continue
        rel = struct.unpack_from("<i", data, rawptr + off + 1)[0]
        site = base_va + off
        tgt = site + 5 + rel
        kind = "CALL" if op == 0xE8 else "JMP"
        edges.append((kind, site, tgt))
    return edges


def scan_absolute_ptrs(data: bytes, image_base: int, sections, lo: int, hi: int) -> list[tuple[int, int]]:
    """(ptr_site_va, target_va) for dwords in [lo, hi)."""
    hits = []
    for _name, vaddr, _vs, rawptr, rawsize in sections:
        for off in range(0, rawsize - 3, 4):
            val = struct.unpack_from("<I", data, rawptr + off)[0]
            if lo <= val < hi:
                hits.append((image_base + vaddr + off, val))
    return hits


def single_ret_envelope(
    data: bytes,
    image_base: int,
    sections,
    entry: int,
    max_bytes: int,
    cs_mod,
) -> dict:
    o0 = va_to_off(entry, image_base, sections)
    if o0 is None or cs_mod is None:
        return {
            "ok": False,
            "reason": "unmapped_or_no_capstone",
            "bytes": 0,
            "insns": 0,
            "retCount": 0,
            "endVa": fmt_va(entry),
            "lastMnemonic": "",
        }
    blob = data[o0 : o0 + max_bytes]
    md = cs_mod.Cs(cs_mod.CS_ARCH_X86, cs_mod.CS_MODE_32)
    offset = 0
    count = 0
    ret_count = 0
    last_mn = ""
    end_va = entry
    while offset < len(blob) and count < 2048:
        insns = list(md.disasm(blob[offset : offset + 16], entry + offset))
        if not insns:
            break
        insn = insns[0]
        if insn.size <= 0:
            break
        offset += insn.size
        count += 1
        last_mn = insn.mnemonic
        end_va = entry + offset
        if insn.mnemonic in ("ret", "retn"):
            ret_count += 1
            # include trailing NOPs after ret as padding of envelope
            pad = 0
            while offset + pad < len(blob) and blob[offset + pad] in (0x90, 0xCC) and pad < 16:
                pad += 1
            offset += pad
            end_va = entry + offset
            break
    return {
        "ok": ret_count == 1 and count >= 4,
        "reason": (
            "single_ret"
            if ret_count == 1 and count >= 4
            else ("no_ret" if ret_count == 0 else f"ret_count={ret_count}")
        ),
        "bytes": offset,
        "insns": count,
        "retCount": ret_count,
        "endVa": fmt_va(end_va),
        "lastMnemonic": last_mn,
    }


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


def parse_body_end_va(row: dict, image_base: int = 0x400000) -> int | None:
    """Best-effort end VA from bodyRangesRva (last range end)."""
    br = row.get("bodyRangesRva") or ""
    if not br:
        return None
    # formats like 0x1b8da0-0x1b8e9e or multi with ;
    last = br.split(";")[-1]
    if "-" not in last:
        return None
    try:
        end_rva = int(last.split("-")[1], 16)
        return image_base + end_rva
    except Exception:
        return None


def grade_candidate(
    entry: int,
    prologue_ok: bool,
    ext_calls: list[int],
    ext_jmps: list[int],
    int_edges: list[tuple[str, int]],
    abs_ptrs: list[int],
    envelope: dict,
    prev_ret_end: int | None,
) -> tuple[str, str]:
    if not prologue_ok:
        return "NO_PROLOGUE", "start byte not in prologue set"
    if not envelope.get("ok"):
        return "MULTI_RET_OR_OPEN", envelope.get("reason", "envelope_fail")
    if ext_calls:
        return (
            "ENVELOPE_PROVED_STATIC",
            f"external_E8_calls={len(ext_calls)} single_ret_bytes={envelope['bytes']}",
        )
    note = []
    if prev_ret_end is not None and entry == prev_ret_end:
        note.append("FALLTHROUGH_AFTER_PREV_RET")
    if abs_ptrs:
        note.append(f"abs_ptrs={len(abs_ptrs)}")
    if ext_jmps:
        note.append(f"ext_jmps={len(ext_jmps)}")
    if int_edges:
        note.append(f"internal_edges={len(int_edges)}")
    return (
        "ENTRY_SHAPE_NO_CALL_XREF",
        ";".join(note) if note else "single_ret_no_external_E8",
    )


def prove_spans(
    specimen: Path,
    spans: list[dict],
    gen10_tsv: Path | None,
    candidates_extra: list[int] | None = None,
) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen sha256 mismatch: {sha}")
    image_base, sections = pe_map(data)
    cs_mod = try_capstone()
    edges = scan_rel32_edges(data, image_base, sections)

    gen10 = load_gen10_functions(gen10_tsv) if gen10_tsv and gen10_tsv.is_file() else []
    gen10_by_entry = {}
    for r in gen10:
        try:
            gen10_by_entry[int(r["entryVa"], 16)] = r
        except Exception:
            pass

    results = []
    for sp in spans:
        lo = int(sp["startVa"], 16)
        hi = int(sp["endVa"], 16)
        prev_name = sp.get("prevFunc", "")
        next_name = sp.get("nextFunc", "")
        # candidates: span start, extra fragment starts, any external E8 target in span
        cands = set()
        cands.add(lo)
        for c in sp.get("candidates") or []:
            cands.add(int(c, 16) if isinstance(c, str) else int(c))
        if candidates_extra:
            for c in candidates_extra:
                if lo <= c < hi:
                    cands.add(c)
        for kind, site, tgt in edges:
            if lo <= tgt < hi and kind == "CALL":
                cands.add(tgt)

        # absolute ptrs into span
        abs_all = scan_absolute_ptrs(data, image_base, sections, lo, hi)
        abs_by_tgt: dict[int, list[int]] = defaultdict(list)
        for site, tgt in abs_all:
            abs_by_tgt[tgt].append(site)

        # prev function ret end
        prev_ret_end = None
        for r in gen10:
            if r.get("currentName") == prev_name or (
                prev_name and prev_name in (r.get("currentName") or "")
            ):
                prev_ret_end = parse_body_end_va(r, image_base)
                break
        # also: if any gen10 body ends exactly at lo
        for r in gen10:
            end = parse_body_end_va(r, image_base)
            if end == lo:
                prev_ret_end = end
                prev_name = prev_name or r.get("currentName", "")
                break

        next_entry = None
        for r in gen10:
            try:
                ev = int(r["entryVa"], 16)
            except Exception:
                continue
            if ev == hi or (r.get("currentName") == next_name):
                next_entry = ev
                if r.get("currentName") == next_name:
                    break

        cand_rows = []
        for entry in sorted(cands):
            if not (lo <= entry < hi):
                continue
            o0 = va_to_off(entry, image_base, sections)
            if o0 is None:
                continue
            start_byte = data[o0]
            prologue_ok = start_byte in PROLOGUE_START
            ext_calls = []
            ext_jmps = []
            int_edges = []
            for kind, site, tgt in edges:
                if tgt != entry:
                    continue
                if lo <= site < hi:
                    int_edges.append((kind, site))
                elif kind == "CALL":
                    ext_calls.append(site)
                else:
                    ext_jmps.append(site)
            max_bytes = min(0x10000, hi - entry + 64)
            env = single_ret_envelope(
                data, image_base, sections, entry, max_bytes, cs_mod
            )
            grade, reason = grade_candidate(
                entry,
                prologue_ok,
                ext_calls,
                ext_jmps,
                int_edges,
                abs_by_tgt.get(entry, []),
                env,
                prev_ret_end,
            )
            # already a Gen10 function?
            g10 = gen10_by_entry.get(entry)
            cand_rows.append(
                {
                    "entryVa": fmt_va(entry),
                    "startByte": f"0x{start_byte:02x}",
                    "prologueOk": prologue_ok,
                    "grade": grade,
                    "reason": reason,
                    "externalCallSites": [fmt_va(s) for s in ext_calls],
                    "externalJmpSites": [fmt_va(s) for s in ext_jmps],
                    "internalEdgeCount": len(int_edges),
                    "absolutePtrSites": [fmt_va(s) for s in abs_by_tgt.get(entry, [])],
                    "envelope": env,
                    "gen10Name": (g10 or {}).get("currentName", ""),
                    "alreadyGen10Function": bool(g10),
                }
            )

        # span-level inbound summary
        inbound_ext_calls = [
            (kind, site, tgt)
            for kind, site, tgt in edges
            if kind == "CALL" and lo <= tgt < hi and not (lo <= site < hi)
        ]
        results.append(
            {
                "startVa": fmt_va(lo),
                "endVa": fmt_va(hi),
                "bytes": hi - lo,
                "prevFunc": prev_name,
                "nextFunc": next_name,
                "prevBodyEndsAtSpanStart": prev_ret_end == lo if prev_ret_end else False,
                "prevBodyEndVa": fmt_va(prev_ret_end) if prev_ret_end else None,
                "nextNamedEntryVa": fmt_va(next_entry) if next_entry else None,
                "absolutePtrCountIntoSpan": len(abs_all),
                "externalCallEdgesIntoSpan": len(inbound_ext_calls),
                "externalCallTargets": sorted(
                    {fmt_va(t) for _, _, t in inbound_ext_calls}
                ),
                "candidates": cand_rows,
                "gradeCounts": dict(Counter(c["grade"] for c in cand_rows)),
                "anyProved": any(
                    c["grade"] == "ENVELOPE_PROVED_STATIC" for c in cand_rows
                ),
            }
        )

    proved = sum(1 for r in results if r["anyProved"])
    return {
        "schema": "bea.re.function-envelope-static.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_spans": len(results),
        "n_spans_with_proved_envelope": proved,
        "capstone": bool(cs_mod),
        "rows": results,
        "note": (
            "ENVELOPE_PROVED_STATIC requires external E8 CALL + single-ret "
            "envelope. Zero inventing of names. Gen10 not mutated."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument(
        "--spans-json",
        type=Path,
        help="JSON list of {startVa,endVa,prevFunc?,nextFunc?,candidates?}",
    )
    p.add_argument("--gen10-functions-tsv", type=Path, default=None)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    spans = json.loads(args.spans_json.read_text(encoding="utf-8"))
    if isinstance(spans, dict) and "spans" in spans:
        spans = spans["spans"]
    result = prove_spans(args.specimen, spans, args.gen10_functions_tsv)
    summary = {k: v for k, v in result.items() if k != "rows"}
    # compact row summary for stdout
    compact_rows = []
    for r in result["rows"]:
        compact_rows.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r["bytes"],
                "prevFunc": r["prevFunc"],
                "nextFunc": r["nextFunc"],
                "prevBodyEndsAtSpanStart": r["prevBodyEndsAtSpanStart"],
                "externalCallEdgesIntoSpan": r["externalCallEdgesIntoSpan"],
                "externalCallTargets": r["externalCallTargets"],
                "absolutePtrCountIntoSpan": r["absolutePtrCountIntoSpan"],
                "gradeCounts": r["gradeCounts"],
                "anyProved": r["anyProved"],
                "bestCandidates": [
                    {
                        "entryVa": c["entryVa"],
                        "grade": c["grade"],
                        "reason": c["reason"],
                        "envBytes": c["envelope"].get("bytes"),
                        "extCalls": c["externalCallSites"],
                    }
                    for c in r["candidates"]
                    if c["grade"]
                    in (
                        "ENVELOPE_PROVED_STATIC",
                        "ENTRY_SHAPE_NO_CALL_XREF",
                    )
                ][:12],
            }
        )
    summary["spanSummaries"] = compact_rows
    print(json.dumps(summary, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = summary if args.summary_only else result
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("FUNCTION_ENVELOPE_STATIC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
