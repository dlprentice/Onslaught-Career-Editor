#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen32 remaining OPEN_DARK: large-island / mixed-walk residual resolve.

Exports OPEN_DARK (24) from Generation 32 tip. Non-police only.

Lanes (TERMINAL_BOUNDED_AMBIGUITY):

  WHOLE_MIXED_WALK
    Full residual covered by greedy walk: image/code pointer tables (glue 0–3),
    index/byte-table remainders (≤128B mid-walk only), permissive linear code,
    small/flag dwords, pad, incomplete LE-pointer slack (1–3B at edges).

  SEGMENT_ISLAND_RESOLVE
    large.segment_blob walk; terminal segs kept; OPEN_CODE_FRAGMENT →
    BOUNDED_CODE_SHAPE; UNRESOLVED islands covered by the same walk.

Does **not** close police-reopened OFFSET_ENVELOPE holds.
Does **not** invent function names or REBUILD_READY.
Does **not** accept whole residuals solely as loose byte-tables (len>64 must
use structured steps).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

SCHEMA = "bea.re.open-residual-gen32-large-island-resolve.v1"
PACK_SCHEMA = "bea.re.open-residual-gen32-large-island-resolve-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_LARGE_ISLAND_RESOLVE.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 24
EXPECTED_OPEN_EXECUTED = 0
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000
RDATA_LO = 0x005D0000
RDATA_HI = 0x00700000

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN32 = Path(
    "local-lab/residual-terminal-generation32-deep-segment-resolve-20260805-v1/"
    "generation-32-residual-terminal-deep-segment-resolve"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen32-large-island-resolve-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE re-decode: large-island mixed walk / segment island resolve fails full "
    "cover; residual membership of a named body; REBUILD_READY claim"
)


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


def is_text_ptr(v: int) -> bool:
    return TEXT_LO <= v < TEXT_HI


def is_img_ptr(v: int) -> bool:
    return is_text_ptr(v) or RDATA_LO <= v < RDATA_HI


def ptr_run(blob: bytes, min_d: int = 2) -> int:
    run = 0
    for i in range(0, len(blob) - 3, 4):
        if is_img_ptr(struct.unpack_from("<I", blob, i)[0]):
            run += 1
        else:
            break
    return run * 4 if run >= min_d else 0


def is_small_byte(b: int) -> bool:
    return b <= 0x40 or b in (0x90, 0xCC)


def is_byte_table(blob: bytes) -> bool:
    if len(blob) < 8:
        return False
    if sum(1 for b in blob if b <= 0xC0) / len(blob) >= 0.92:
        return True
    if len(blob) >= 16 and len(set(blob)) <= max(8, len(blob) // 3):
        return True
    return False


def slack_ok(blob: bytes) -> bool:
    if not blob:
        return True
    if len(blob) > 3:
        return False
    if all(is_small_byte(b) for b in blob):
        return True
    padded = blob + b"\x00" * (4 - len(blob))
    return is_img_ptr(struct.unpack_from("<I", padded)[0])


def index_prefix(blob: bytes, max_n: int = 64) -> int:
    n = 0
    limit = min(len(blob), max_n)
    while n < limit:
        if n + 8 <= len(blob) and ptr_run(blob[n:], 2) >= 8:
            break
        if is_small_byte(blob[n]):
            n += 1
            continue
        if blob[n : n + 2] == b"\x8b\xff":
            n += 2
            continue
        if blob[n] == 0x90:
            n += 1
            continue
        break
    return n


def linear_code(blob: bytes, cs_mod, max_bytes: int = 2048) -> tuple[int, int]:
    if not blob or cs_mod is None:
        return 0, 0
    md = cs_mod.Cs(cs_mod.CS_ARCH_X86, cs_mod.CS_MODE_32)
    off = 0
    n = 0
    limit = min(len(blob), max_bytes)
    while off < limit and n < 512:
        if off + 8 <= limit and all(blob[off + k] == 0 for k in range(8)):
            break
        if off + 4 <= limit and all(blob[off + k] == 0xCC for k in range(4)):
            break
        insns = list(md.disasm(blob[off : off + 15], 0))
        if not insns:
            break
        insn = insns[0]
        if insn.size <= 0:
            break
        off += insn.size
        n += 1
    return off, n


def ffff_record16_run(blob: bytes) -> int:
    """Run of 16-byte records whose first dword is a *ffff mask (D3DX-ish)."""
    if len(blob) < 32:
        return 0
    n = 0
    while n + 16 <= len(blob):
        d0 = struct.unpack_from("<I", blob, n)[0]
        if (d0 & 0xFFFF) != 0xFFFF:
            break
        n += 16
    # incomplete trailing record after ≥2 full records
    if n >= 32 and 0 < len(blob) - n < 16:
        n = len(blob)
    return n if n >= 32 else 0


def is_data_dword(v: int) -> bool:
    if is_img_ptr(v):
        return True
    if v <= 0x01000000:
        return True
    if (v & 0xFFFF) == 0xFFFF:
        return True
    if v == 0x03FFFF80:
        return True
    if (v & 0xFF000000) in (0x80000000, 0x03000000, 0x2C000000):
        return True
    # high-byte-only size / flag words (e.g. 0x2c000000 already covered)
    if (v & 0x00FFFFFF) == 0 and (v >> 24) <= 0x40:
        return True
    return False


def walk_cover(piece: bytes, mass, inb, cs_mod) -> bool:
    """Structured full cover; no early whole-piece byte-table for len>64."""
    if not piece:
        return True
    pos = 0
    steps = 0
    structured = 0
    while pos < len(piece) and steps < 800:
        steps += 1
        r = piece[pos:]
        if mass.is_pure_pad(r) or inb.is_full_align_nop_run(r):
            return True
        if pos > 0 and is_byte_table(r) and len(r) <= 128:
            return True
        if pos > 0 and slack_ok(r):
            return True

        rr = ffff_record16_run(r)
        if rr >= 32:
            pos += rr
            structured += 1
            continue

        advanced = False
        for g in range(0, 4):
            if g > len(r):
                break
            t = ptr_run(r[g:], 2)
            if t >= 8:
                pos += g + t
                structured += 1
                advanced = True
                break
        if advanced:
            continue

        pref = index_prefix(r, 64)
        if pref >= 1:
            rest = r[pref:]
            t = ptr_run(rest, 2)
            if t >= 8:
                pos += pref + t
                structured += 1
                continue
            if pref >= 4 and is_byte_table(r) and len(r) <= 128:
                return structured > 0 or len(piece) <= 64
            if pref >= 4 and slack_ok(rest):
                pos += pref
                continue

        if r[:2] == b"\x8b\xff":
            t = ptr_run(r[2:], 2)
            if t >= 8:
                pos += 2 + t
                structured += 1
                continue

        cr, ni = linear_code(r, cs_mod)
        if cr >= 4 and ni >= 1:
            pos += cr
            structured += 1
            continue

        sd = 0
        for i in range(0, len(r) - 3, 4):
            v = struct.unpack_from("<I", r, i)[0]
            if is_data_dword(v):
                sd += 4
            else:
                break
        if sd >= 8:
            pos += sd
            structured += 1
            continue

        if r[0] in (0x0F, 0x00, 0x90, 0xCC):
            pos += 1
            continue

        return False

    if pos >= len(piece) or slack_ok(piece[pos:]):
        if len(piece) <= 64:
            return True
        return structured > 0
    return False


def segment_island_resolve(
    blob: bytes, base: int, mass, inb, large_mod
) -> dict[str, Any] | None:
    cs = large_mod.try_capstone()
    segs = large_mod.segment_blob(base, blob, cs)
    if not segs:
        return None
    terms: list[dict[str, Any]] = []
    off = 0
    for sg in segs:
        nb = int(sg["bytes"])
        piece = blob[off : off + nb]
        if len(piece) != nb:
            return None
        kind = str(sg.get("kind") or "")
        if sg.get("terminal"):
            terms.append(
                {
                    "kind": kind,
                    "startVa": f"0x{base + off:08x}",
                    "endVa": f"0x{base + off + nb:08x}",
                    "bytes": nb,
                }
            )
        elif kind == "OPEN_CODE_FRAGMENT":
            terms.append(
                {
                    "kind": "BOUNDED_CODE_SHAPE",
                    "startVa": f"0x{base + off:08x}",
                    "endVa": f"0x{base + off + nb:08x}",
                    "bytes": nb,
                }
            )
        elif kind == "UNRESOLVED_BYTES":
            if not walk_cover(piece, mass, inb, cs):
                return None
            terms.append(
                {
                    "kind": "ISLAND_RESOLVED",
                    "startVa": f"0x{base + off:08x}",
                    "endVa": f"0x{base + off + nb:08x}",
                    "bytes": nb,
                }
            )
        else:
            return None
        off += nb
    if off != len(blob) or not terms:
        return None
    kinds = [t["kind"] for t in terms]
    return {
        "lane": "SEGMENT_ISLAND_RESOLVE",
        "shapeKind": "+".join(kinds),
        "terms": terms,
        "n_terms": len(terms),
        "note": f"n_terms={len(terms)} kinds={'+'.join(kinds)}",
    }


def classify_open_dark(
    blob: bytes, base: int, mass, inb, large_mod
) -> dict[str, Any] | None:
    cs = large_mod.try_capstone()
    if walk_cover(blob, mass, inb, cs):
        return {
            "lane": "WHOLE_MIXED_WALK",
            "shapeKind": "WHOLE_MIXED_WALK",
            "terms": [
                {
                    "kind": "WHOLE_MIXED_WALK",
                    "startVa": f"0x{base:08x}",
                    "endVa": f"0x{base + len(blob):08x}",
                    "bytes": len(blob),
                }
            ],
            "n_terms": 1,
            "note": f"whole_mixed_walk bytes={len(blob)}",
            "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
            "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        }
    seg = segment_island_resolve(blob, base, mass, inb, large_mod)
    if seg is not None:
        seg["terminalState"] = "TERMINAL_BOUNDED_AMBIGUITY"
        seg["peBytesSha256"] = hashlib.sha256(blob).hexdigest()
        return seg
    return None


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": "AMBIGUOUS",
        "classificationVerdict": f"STATIC_LARGE_ISLAND/{rec['lane']}",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": rec.get("shapeKind") or rec["lane"],
        "recoveryLane": rec["lane"],
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER,
        "sourceState": "OPEN_DARK_RESIDUAL",
    }


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    mass = _load_mod(
        "re_open_dark_code_like_mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
    )
    inb = _load_mod(
        "re_open_dark_still_open_inbound",
        ROOT / "tools" / "re_open_dark_still_open_inbound.py",
    )
    large_mod = _load_mod(
        "re_large_mixed_blob_classify", ROOT / "tools" / "re_large_mixed_blob_classify.py"
    )
    mtm_mod = _load_mod(
        "re_open_residual_gen29_msvc_table_mix",
        ROOT / "tools" / "re_open_residual_gen29_msvc_table_mix.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 32:
        raise SystemExit(f"expected Gen32, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_OPEN_DEEP_SEGMENT_RESOLVE":
        raise SystemExit(f"unexpected advance {(ready.get('advance') or {}).get('kind')}")

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"residuals {len(residuals)}")
    dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    executed = [
        r for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
    ]
    if len(dark) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"OPEN_DARK {len(dark)}")
    if len(executed) != EXPECTED_OPEN_EXECUTED:
        raise SystemExit(f"OPEN_EXECUTED {len(executed)}")

    police = mtm_mod.load_police_reopened()
    out_dir.mkdir(parents=True, exist_ok=True)
    export_cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "observationState",
        "campaignState",
        "questionIds",
        "prevFunc",
        "nextFunc",
        "cheapestFalsifier",
    ]
    _write_tsv(out_dir / "open-dark.tsv", export_cols, dark)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = mass.pe_map(data)

    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    buckets: Counter = Counter()
    lane_counts: Counter = Counter()

    for r in dark:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        b = end - start
        if b <= 3:
            buckets["1-3"] += 1
        elif b <= 15:
            buckets["4-15"] += 1
        elif b <= 63:
            buckets["16-63"] += 1
        elif b <= 255:
            buckets["64-255"] += 1
        else:
            buckets["256+"] += 1
        is_police = r["startVa"].lower() in police
        blob = mass.span_bytes(data, start, end, ib, secs)
        if blob is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "lane": "UNMAPPED",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": "Unmapped PE span",
                }
            )
            lane_counts["UNMAPPED"] += 1
            continue
        if is_police:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "lane": "POLICE_HOLD",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "Police-reopened OFFSET_ENVELOPE hold; do not re-close "
                        "without new instrument"
                    ),
                }
            )
            lane_counts["POLICE_HOLD"] += 1
            continue
        rec = classify_open_dark(blob, start, mass, inb, large_mod)
        if rec is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "No large-island mixed walk / segment island full cover; "
                        "need TTD or new shape"
                    ),
                }
            )
            lane_counts["STILL_OPEN"] += 1
            continue
        prop = proposed_for(rec)
        proofs.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": b,
                "kind": rec.get("shapeKind") or rec["lane"],
                "subspanKinds": rec.get("shapeKind") or rec["lane"],
                "recoveryLane": rec["lane"],
                "peBytesSha256": rec["peBytesSha256"],
                "recheckNote": rec.get("note") or "",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "terms": rec.get("terms"),
                "proposedTerminalState": prop["terminalState"],
                "proposed": prop,
            }
        )
        lane_counts[rec["lane"]] += 1

    hard: list[str] = []
    for p in proofs:
        if p["sourceState"] != "OPEN_DARK_RESIDUAL":
            hard.append(f"non_dark {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        if p["proposedTerminalState"] != "TERMINAL_BOUNDED_AMBIGUITY":
            hard.append(f"bad_term {p['startVa']}")
        if p["startVa"].lower() in police:
            hard.append(f"police_proof {p['startVa']}")
        s = int(p["startVa"], 16)
        e = int(p["endVa"], 16)
        blob = mass.span_bytes(data, s, e, ib, secs)
        if blob is None or hashlib.sha256(blob).hexdigest() != p["peBytesSha256"]:
            hard.append(f"pe_drift {p['startVa']}")
            continue
        again = classify_open_dark(blob, s, mass, inb, large_mod)
        if again is None or again["lane"] != p["recoveryLane"]:
            hard.append(f"recheck_fail {p['startVa']}")

    pack: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "status": (
            "READY_FOR_GENERATION"
            if proofs and not hard
            else "EMPTY"
            if not proofs and not hard
            else "BLOCKED"
        ),
        "advance_kind_proposed": ADVANCE_KIND,
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 32,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_still_open": len(still),
        "n_police_hold": sum(1 for s in still if s.get("lane") == "POLICE_HOLD"),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "darkSizeBuckets": dict(buckets),
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK from Gen32.",
            f"Large-island / mixed-walk proofs: {len(proofs)} (non-police only).",
            f"Police holds: {sum(1 for s in still if s.get('lane')=='POLICE_HOLD')}.",
            f"Still open non-police: {sum(1 for s in still if s.get('lane')=='STILL_OPEN')}.",
            "Whole-residual mixed walk prefers structured ptr/code steps; "
            "byte-table only for ≤128B remainders.",
            "Gen33 apply withheld until dual-role review.",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not re-close police OFFSET_ENVELOPE holds",
            "WHOLE_MIXED_WALK / BOUNDED_CODE_SHAPE are residual-row shape only",
        ],
        "proofs": proofs,
    }

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 32,
        "formalPackStatus": pack["status"],
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "formalPackProofs": len(proofs),
            "stillOpen": len(still),
            "policeHold": pack["n_police_hold"],
            "darkSizeBuckets": dict(buckets),
            "laneCounts": dict(lane_counts),
            "recoveryLaneProofCounts": pack["recoveryLaneCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role review then Gen33 apply",
            "Police OFFSET_ENVELOPE holds need separate instrument/TTD",
        ],
        "proofStarts": [p["startVa"] for p in proofs],
        "parentResidualsSha256": _sha(campaign / "campaign-residuals.tsv"),
    }

    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    proof_cols = [
        "startVa",
        "endVa",
        "bytes",
        "recoveryLane",
        "kind",
        "peBytesSha256",
        "entityKey",
        "questionIds",
        "recheckNote",
    ]
    _write_tsv(out_dir / "proofs.tsv", proof_cols, proofs)
    still_cols = [
        "startVa",
        "endVa",
        "bytes",
        "lane",
        "entityKey",
        "questionIds",
        "cheapestFalsifier",
    ]
    _write_tsv(out_dir / "still-open.tsv", still_cols, still)
    (out_dir / "README.md").write_text(
        "# Gen32 large-island / mixed-walk OPEN_DARK\n\n"
        f"Status: **MEASURED** / formal pack **{pack['status']}**  \n"
        f"Proofs: **{len(proofs)}** · police holds: "
        f"**{pack['n_police_hold']}**\n\n"
        "Gen33 apply: **held**.\n",
        encoding="utf-8",
    )
    integrity = {
        "schema": SCHEMA + ".integrity",
        "specimen_sha256": SPECIMEN_SHA256,
        "parentResidualsSha256": summary["parentResidualsSha256"],
        "formalPackSha256": _sha(out_dir / "FORMAL-PACK.json"),
        "n_proofs": len(proofs),
        "status": pack["status"],
    }
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN32_LARGE_ISLAND_RESOLVE_MEASURED")
    print(f"formal_pack_status={pack['status']}")
    print(f"n_proofs={len(proofs)}")
    return summary


def verify(*, plate: Path) -> dict[str, Any]:
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    if pack.get("n_hard_mismatches", 1) != 0:
        raise SystemExit(f"hard mismatches: {pack.get('hardMismatches')}")
    if pack.get("status") not in {"READY_FOR_GENERATION", "EMPTY"}:
        raise SystemExit(f"pack status {pack.get('status')}")
    if pack.get("n_police_hold", 0) < 1 and pack.get("n_proofs", 0) == 0:
        pass
    out = {
        "status": "VERIFIED",
        "formalPackStatus": pack.get("status"),
        "n_proofs": pack.get("n_proofs"),
        "lanes": pack.get("recoveryLaneCounts"),
        "policeHold": pack.get("n_police_hold"),
        "summaryProofs": summary.get("counts", {}).get("formalPackProofs"),
    }
    print(json.dumps(out, indent=2))
    print("OPEN_RESIDUAL_GEN32_LARGE_ISLAND_RESOLVE_VERIFIED")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN32)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, specimen=args.specimen, out_dir=args.out)
        return 0
    verify(plate=args.plate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
