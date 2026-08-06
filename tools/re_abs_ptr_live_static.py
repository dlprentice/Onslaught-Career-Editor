#!/usr/bin/env python3
"""Static live-load classification for ABS_PTR_TEXT_RDATA residual candidates.

For each residual with absolute dword pointers in .text/.rdata into its span:

  1. Decode each pointer site (is it in a jump table / mov reg,imm / .rdata slot).
  2. Grade STATIC_JMP_TABLE / STATIC_MOV_IMM / STATIC_RDATA_SLOT / STATIC_AMBIGUOUS.
  3. Hash-bound specimen; no Gen10/Gen11 mutation.

Cheapest runtime falsifier remains: ba on execute of residual entry or TTD
entry count > 0 under a natural path that loads the pointer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)


def pe_map(data: bytes):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    ib = struct.unpack_from("<I", data, e + 24 + 28)[0]
    num = struct.unpack_from("<H", data, e + 6)[0]
    so = struct.unpack_from("<H", data, e + 20)[0]
    sec = e + 24 + so
    secs = []
    for i in range(num):
        o = sec + i * 40
        name = data[o : o + 8].split(b"\0")[0].decode("latin1", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        chars = struct.unpack_from("<I", data, o + 36)[0]
        secs.append((name, va, vsize, rawptr, rawsize, chars))
    return ib, secs


def v2o(va: int, ib: int, secs) -> int | None:
    rva = va - ib
    for _n, sva, vs, rp, rs, _c in secs:
        if sva <= rva < sva + max(vs, rs):
            d = rva - sva
            if d < rs:
                return rp + d
    return None


def sec_of(va: int, ib: int, secs) -> str | None:
    rva = va - ib
    for name, sva, vs, rp, rs, _c in secs:
        if sva <= rva < sva + max(vs, rs):
            return name
    return None


def classify_site(raw: bytes, ib: int, secs, src_va: int, target_va: int) -> dict:
    off = v2o(src_va, ib, secs)
    if off is None:
        return {"srcVa": f"0x{src_va:08x}", "error": "unmapped"}
    sec = sec_of(src_va, ib, secs)
    # context bytes around dword
    pre = raw[max(0, off - 8) : off]
    dword = raw[off : off + 4]
    post = raw[off + 4 : off + 12]
    imm = struct.unpack_from("<I", dword, 0)[0]
    form = "UNKNOWN"
    # B8+reg imm32 = mov reg, imm32
    if len(pre) >= 1 and 0xB8 <= pre[-1] <= 0xBF and imm == target_va:
        form = "MOV_REG_IMM32"
    # 68 imm32 = push
    elif len(pre) >= 1 and pre[-1] == 0x68 and imm == target_va:
        form = "PUSH_IMM32"
    # C7 05 abs imm = mov [abs], imm
    elif len(pre) >= 2 and pre[-2] == 0xC7 and pre[-1] == 0x05 and imm == target_va:
        form = "MOV_ABS_IMM32"
    # bare dword table in code (.text) with neighbors also code-ish
    elif sec == ".text" and imm == target_va:
        # check if previous/next dwords look like code VAs
        neighbors = 0
        for delta in (-4, 4, -8, 8):
            o2 = off + delta
            if 0 <= o2 < len(raw) - 4:
                v = struct.unpack_from("<I", raw, o2)[0]
                if 0x00401000 <= v < 0x00600000:
                    neighbors += 1
        form = "TEXT_DWORD_TABLE" if neighbors >= 1 else "TEXT_LONE_DWORD"
    elif sec and sec.lower().startswith(".rdata") and imm == target_va:
        form = "RDATA_DWORD"
    return {
        "srcVa": f"0x{src_va:08x}",
        "targetVa": f"0x{target_va:08x}",
        "section": sec,
        "form": form,
        "preHex": pre.hex(),
        "dwordHex": dword.hex(),
        "postHex": post.hex(),
    }


def analyze(specimen: Path, join_json: Path) -> dict:
    raw = specimen.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    ib, secs = pe_map(raw)
    data = json.loads(join_json.read_text(encoding="utf-8"))
    rows = data.get("rows", data)
    abs_rows = [r for r in rows if r.get("joinGrade") == "ABS_PTR_TEXT_RDATA"]
    out = []
    form_counts: dict[str, int] = {}
    for r in abs_rows:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        hits = []
        for h in r.get("absPtrHitsTextRdata") or []:
            src = int(h["srcVa"], 16)
            tgt = int(h["targetVa"], 16)
            hits.append(classify_site(raw, ib, secs, src, tgt))
        forms = [h.get("form") for h in hits]
        for f in forms:
            form_counts[f] = form_counts.get(f, 0) + 1
        # residual grade
        if any(f == "TEXT_DWORD_TABLE" for f in forms):
            grade = "STATIC_JMP_OR_DATA_TABLE_PTR"
        elif any(f in ("MOV_REG_IMM32", "PUSH_IMM32") for f in forms):
            grade = "STATIC_IMM_LOAD_OR_PUSH"
        elif any(f == "RDATA_DWORD" for f in forms):
            grade = "STATIC_RDATA_PTR"
        elif hits:
            grade = "STATIC_ABS_PTR_AMBIGUOUS"
        else:
            grade = "STATIC_NO_HITS"
        out.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r.get("bytes"),
                "prevFunc": r.get("prevFunc"),
                "nextFunc": r.get("nextFunc"),
                "nAbsPtrHits": r.get("nAbsPtrHitsTextRdata"),
                "hits": hits,
                "staticGrade": grade,
                "cheapestFalsifier": r.get("cheapestFalsifier"),
            }
        )
    return {
        "schema": "bea.re.abs-ptr-live-static.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_candidates": len(out),
        "formCounts": form_counts,
        "gradeCounts": {
            g: sum(1 for x in out if x["staticGrade"] == g)
            for g in sorted({x["staticGrade"] for x in out})
        },
        "candidates": out,
        "claims": [
            "Classifies absolute dword sites into form buckets on pristine PE.",
            "TEXT_DWORD_TABLE neighbors suggest jump/data tables (DispatchRemap-style).",
            "Does not prove runtime load without execute or data-read evidence.",
        ],
        "non_claims": [
            "Does not invent names.",
            "Does not mutate Gen10/Gen11.",
            "ABS_PTR alone is not terminal without live control-flow proof.",
        ],
        "cheapestRuntimeFalsifier": (
            "For TEXT_DWORD_TABLE residuals: TTD call-context entry on residual "
            "under path that exercises the table (e.g. DispatchRemap jump table)."
        ),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--join-json", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    args = p.parse_args(argv)
    result = analyze(args.specimen, args.join_json)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: result[k] for k in result if k != "candidates"},
            indent=2,
        )
    )
    for c in result["candidates"]:
        print(c["startVa"], c["staticGrade"], "hits", c["nAbsPtrHits"])
    print("ABS_PTR_STATIC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
