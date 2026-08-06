#!/usr/bin/env python3
"""Re-grade residual entry returns with stream-aligned disasm + k-frame parse.

Takes an existing CDB log (from runtime-jpeg / slot-read plates) and:
  1. Parses HIT_CAND_* entry hits (eip, dds first dword, k frames when present).
  2. Stream-aligns each candidate ret address against pristine PE: is it an
     instruction boundary immediately after a CALL?
  3. Classifies ret vs residual own-span and sibling residual spans.
  4. Emits hash-bound regrade receipt — does not invent names.

Usage:
  python tools/re_entry_ret_regrade.py \\
    --specimen local-lab/.../BEA.exe \\
    --plan-json local-lab/runtime-jpeg-.../static-plan.json \\
    --cdb-log local-lab/runtime-jpeg-.../cdb-stdout.txt \\
    --json-out local-lab/runtime-jpeg-.../entry-ret-regrade.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore


def pe_map(data: bytes):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    ib = struct.unpack_from("<I", data, e + 24 + 28)[0]
    num = struct.unpack_from("<H", data, e + 6)[0]
    so = struct.unpack_from("<H", data, e + 20)[0]
    sec = e + 24 + so
    secs = []
    for i in range(num):
        o = sec + i * 40
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        secs.append((va, vsize, rawptr, rawsize))
    return ib, secs


def v2o(va: int, ib: int, secs) -> int | None:
    rva = va - ib
    for sva, vs, rp, rs in secs:
        if sva <= rva < sva + max(vs, rs):
            d = rva - sva
            if d < rs:
                return rp + d
    return None


def stream_align_ret(raw: bytes, ib, secs, ret_va: int, lookback: int = 48) -> dict:
    """Check whether ret_va is an instruction boundary after a CALL.

    Tries multiple stream starts in the lookback window so a single mid-insn
    start cannot falsely mark a real post-call site as misaligned.
    """
    if Cs is None:
        return {"error": "capstone_missing"}
    # Outside image (USER32 etc.): cannot stream-align against PE
    off_ret = v2o(ret_va, ib, secs)
    if off_ret is None:
        return {
            "retVa": f"0x{ret_va:08x}",
            "instructionBoundary": None,
            "insnAtRet": None,
            "immediatelyAfterCall": None,
            "priorCall": None,
            "grade": "OUTSIDE_PE_IMAGE",
        }

    md = Cs(CS_ARCH_X86, CS_MODE_32)
    best = None
    # Prefer starts that land a CALL ending exactly at ret_va
    for delta in range(lookback, 0, -1):
        start = ret_va - delta
        if start < ib:
            continue
        off = v2o(start, ib, secs)
        if off is None:
            continue
        chunk = raw[off : off + delta + 16]
        last_call = None
        at_boundary = False
        insn_at = None
        for i in md.disasm(chunk, start):
            if i.address == ret_va:
                at_boundary = True
                insn_at = f"{i.mnemonic} {i.op_str}"
                break
            if i.mnemonic == "call":
                last_call = {
                    "va": f"0x{i.address:08x}",
                    "len": i.size,
                    "ops": i.op_str,
                    "nextVa": f"0x{i.address + i.size:08x}",
                }
            if i.address > ret_va:
                break
        after_call = last_call is not None and int(last_call["nextVa"], 16) == ret_va
        cand = {
            "retVa": f"0x{ret_va:08x}",
            "instructionBoundary": at_boundary,
            "insnAtRet": insn_at,
            "immediatelyAfterCall": after_call,
            "priorCall": last_call,
            "streamStart": f"0x{start:08x}",
            "grade": (
                "POST_CALL_ALIGNED"
                if after_call and at_boundary
                else "ALIGNED_NOT_POST_CALL"
                if at_boundary
                else "MID_INSTRUCTION_OR_MISALIGNED"
            ),
        }
        if cand["grade"] == "POST_CALL_ALIGNED":
            return cand
        if best is None or (
            cand["grade"] == "ALIGNED_NOT_POST_CALL"
            and best["grade"] == "MID_INSTRUCTION_OR_MISALIGNED"
        ):
            best = cand
    return best or {
        "retVa": f"0x{ret_va:08x}",
        "grade": "MID_INSTRUCTION_OR_MISALIGNED",
    }


def parse_entry_hits(text: str) -> list[dict]:
    lines = text.splitlines()
    hits = []
    i = 0
    while i < len(lines):
        m = re.match(r"^HIT_CAND_([0-9a-fA-F]+)\s*$", lines[i].strip())
        if not m:
            i += 1
            continue
        cand = m.group(1).lower()
        eip = None
        dds_first = None
        k_ret = None
        k_frames = []
        in_k = False
        for j in range(i + 1, min(i + 40, len(lines))):
            s = lines[j].strip()
            if s.startswith("HIT_") or s.startswith("PROBE_") or s.startswith("EXIT_"):
                break
            if s.startswith("ChildEBP") or s.startswith("RetAddr"):
                in_k = True
                continue
            if "WARNING: Stack unwind" in s:
                in_k = True
                continue
            em = re.match(r"^eip=([0-9a-fA-F]+)", s, re.I)
            if em:
                eip = em.group(1).lower()
                continue
            # stack/data dump: addr + one or more hex dwords (dds/dd)
            dm = re.match(
                r"^([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\b(.*)$",
                s,
            )
            if not dm or eip is None or "WARNING" in s:
                continue
            rest = dm.group(3).strip()
            # k frame: only after ChildEBP header; third field is symbolic
            is_k_line = in_k and rest and not re.match(r"^[0-9a-fA-F]{8}\b", rest)
            if is_k_line:
                k_frames.append(
                    {
                        "ebp": dm.group(1).lower(),
                        "ret": dm.group(2).lower(),
                        "sym": rest,
                    }
                )
                if k_ret is None:
                    k_ret = dm.group(2).lower()
            elif dds_first is None and not in_k:
                # first dds line after eip: [esp] = return address
                dds_first = dm.group(2).lower()
        hits.append(
            {
                "candidateVa": f"0x{cand}",
                "eip": f"0x{eip}" if eip else None,
                "ddsFirstDword": f"0x{dds_first}" if dds_first else None,
                "kRetAddr": f"0x{k_ret}" if k_ret else None,
                "kFrames": k_frames[:6],
            }
        )
        i += 1
    return hits


def regrade(specimen: Path, plan: dict, log_text: str) -> dict:
    raw = specimen.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    ib, secs = pe_map(raw)
    spans = []
    for c in plan.get("candidates") or []:
        spans.append(
            {
                "candidateVa": c["candidateVa"].lower(),
                "start": int(c["candidateVa"], 16),
                "end": int(c["endVa"], 16),
            }
        )
    hits = parse_entry_hits(log_text)
    out_hits = []
    for h in hits:
        cand = h["candidateVa"].lower()
        own = next((s for s in spans if s["candidateVa"] == cand), None)
        # Prefer dds [esp] first dword: at function entry that is the true
        # return address. cdb "k" without symbols often emits wrong frames
        # ("Stack unwind information not available") and must not override dds.
        # Use k when it agrees with dds, or when dds is absent.
        dds = h.get("ddsFirstDword")
        kret = h.get("kRetAddr")
        if dds and kret and dds == kret:
            preferred = dds
            source = "k_and_dds_agree"
        elif dds:
            preferred = dds
            source = "dds"
        elif kret:
            preferred = kret
            source = "k"
        else:
            preferred = None
            source = None
        align = None
        loc = None
        if preferred:
            rva = int(preferred, 16)
            align = stream_align_ret(raw, ib, secs, rva)
            if own:
                in_own = own["start"] <= rva < own["end"]
                sibling = None
                for s in spans:
                    if s["candidateVa"] == cand:
                        continue
                    if s["start"] <= rva < s["end"]:
                        sibling = s["candidateVa"]
                        break
                if in_own:
                    loc = "OWN_RESIDUAL"
                elif sibling:
                    loc = f"SIBLING_RESIDUAL:{sibling}"
                elif 0x00400000 <= rva < 0x00A00000:
                    loc = "BEA_OUTSIDE_CANDIDATE_SPANS"
                else:
                    loc = "NON_BEA"
            else:
                loc = "UNKNOWN_SPAN"
        # final entry grade
        entry_grade = "ENTRY_NO_RET"
        if h.get("eip") and preferred:
            ag = (align or {}).get("grade")
            # USER32 / non-image rets: k-frame symbol is authority; cannot PE-align
            if loc == "NON_BEA" or ag == "OUTSIDE_PE_IMAGE":
                sym = ""
                if h.get("kFrames"):
                    sym = h["kFrames"][0].get("sym") or ""
                if "USER32" in sym or "ntdll" in sym or loc == "NON_BEA":
                    entry_grade = "ENTRY_KFRAME_NON_BEA"
                else:
                    entry_grade = "ENTRY_RET_OUTSIDE_PE"
            elif ag == "POST_CALL_ALIGNED":
                if loc == "OWN_RESIDUAL":
                    entry_grade = "ENTRY_POST_CALL_OWN_SPAN"
                elif loc and loc.startswith("SIBLING"):
                    entry_grade = "ENTRY_POST_CALL_SIBLING_SPAN"
                elif loc == "BEA_OUTSIDE_CANDIDATE_SPANS":
                    entry_grade = "ENTRY_POST_CALL_BEA_EXTERNAL"
                else:
                    entry_grade = "ENTRY_POST_CALL"
            elif align and align.get("instructionBoundary"):
                entry_grade = "ENTRY_ALIGNED_RET_NOT_POST_CALL"
            else:
                entry_grade = "ENTRY_RET_MISALIGNED"
        elif h.get("eip"):
            entry_grade = "ENTRY_EIP_ONLY"
        out_hits.append(
            {
                **h,
                "preferredRet": preferred,
                "retSource": source,
                "retLocality": loc,
                "align": align,
                "entryRetGrade": entry_grade,
            }
        )

    counts: dict[str, int] = {}
    for h in out_hits:
        g = h["entryRetGrade"]
        counts[g] = counts.get(g, 0) + 1

    return {
        "schema": "bea.re.entry-ret-regrade.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "nHits": len(out_hits),
        "gradeCounts": counts,
        "hits": out_hits,
        "claims": [
            "Entry eip==candidate is independent of ret-address quality.",
            "preferredRet is dds [esp] first dword at entry (true return); k used only when it agrees or dds is absent.",
            "POST_CALL_ALIGNED requires multi-start stream-aligned disasm showing CALL ending at retVa.",
        ],
        "non_claims": [
            "Does not invent names.",
            "Does not mutate Gen10/Gen11.",
            "cdb k without symbols is often wrong after 'unwind not available'; do not treat it as authority over dds.",
        ],
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--plan-json", type=Path, required=True)
    p.add_argument("--cdb-log", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    args = p.parse_args(argv)
    plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
    log = args.cdb_log.read_text(encoding="utf-8", errors="replace")
    result = regrade(args.specimen, plan, log)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in result if k != "hits"}, indent=2))
    for h in result["hits"]:
        print(
            h["candidateVa"],
            h["entryRetGrade"],
            "ret",
            h.get("preferredRet"),
            "src",
            h.get("retSource"),
            "loc",
            h.get("retLocality"),
            "align",
            (h.get("align") or {}).get("grade"),
        )
    print("ENTRY_RET_REGRADE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
