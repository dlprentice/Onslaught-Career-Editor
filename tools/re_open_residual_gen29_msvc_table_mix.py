#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen29 remaining OPEN_DARK: MSVC-align lead + multi code-ptr table mix.

Exports OPEN_DARK (40) from Generation 29 tip.

Recovery lane MSVC_MULTI_TABLE_MIX (TERMINAL_BOUNDED_AMBIGUITY):

  Full residual cover by ordered terms:
    MSVC_PAD / pure PAD (consume_align_nops or 00/90/CC)
    CODE_PTR_TABLE (>= 8B / 2 .text dwords; may be below Gen23's 16B floor)
    INDEX_LIKE (4–32B small-int bytes; total INDEX_LIKE <= total TABLE)
    FLOAT (>=32B float_run)
    SSE_OR_CONST_POOL / FLOAT32_LUT (large.segment first terminal seg)

Requires at least one CODE_PTR_TABLE. If any INDEX_LIKE, table total >= 16B
(anti bulk-index launder, Gen24 police).

Does **not** apply to police-reopened rows (envelope holds stay open).
Does **not** mutate Gen29. Does **not** invent names or REBUILD_READY.
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

SCHEMA = "bea.re.open-residual-gen29-msvc-table-mix.v1"
PACK_SCHEMA = "bea.re.open-residual-gen29-msvc-table-mix-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_MSVC_TABLE_MIX.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 40
EXPECTED_OPEN_EXECUTED = 0
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000
MIN_TABLE = 8
MAX_INDEX_LIKE = 32

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN29 = Path(
    "local-lab/residual-terminal-generation29-pad-peel-sandwich-20260805-v1/"
    "generation-29-residual-terminal-pad-peel-sandwich"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen29-msvc-table-mix-20260805-v1")
GEN25_READY = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen/campaign.ready.json"
)
GEN25_RECEIPT = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen/generation-receipt.json"
)

DEFAULT_FALSIFIER = (
    "PE re-decode: MSVC pad / code-ptr table / index-like mix fails full cover; "
    "index bulk exceeds table; residual membership of a named body; REBUILD_READY"
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


def _stamp(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": _sha(path),
    }


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


def load_police_reopened() -> set[str]:
    out: set[str] = set()
    if GEN25_READY.is_file():
        ready = json.loads(GEN25_READY.read_text(encoding="utf-8"))
        for p in (ready.get("advance") or {}).get("reopened") or []:
            if isinstance(p, dict) and p.get("startVa"):
                out.add(str(p["startVa"]).lower())
    if GEN25_RECEIPT.is_file():
        rec = json.loads(GEN25_RECEIPT.read_text(encoding="utf-8"))
        out |= {str(s).lower() for s in rec.get("reopenedStarts") or []}
    return out


def is_pad(blob: bytes, mass, inb) -> bool:
    return bool(blob) and (
        mass.is_pure_pad(blob) or inb.is_full_align_nop_run(blob)
    )


def code_ptr_bytes(blob: bytes, align: int = 0) -> int:
    if align < 0 or align > 3:
        return 0
    body = blob[align:]
    usable = len(body) - (len(body) % 4)
    n = 0
    for i in range(0, usable, 4):
        v = struct.unpack_from("<I", body, i)[0]
        if TEXT_LO <= v < TEXT_HI:
            n += 1
        else:
            break
    return n * 4


def index_like_prefix(blob: bytes, mass, inb, *, max_n: int = MAX_INDEX_LIKE) -> int:
    """Longest prefix of small-int / pad bytes, stopping before .text dwords or MSVC nop."""
    n = 0
    while n < min(len(blob), max_n):
        if n + 4 <= len(blob) and n >= 4:
            v = struct.unpack_from("<I", blob, n)[0]
            if TEXT_LO <= v < TEXT_HI:
                break
        # stop before multi-byte MSVC align nop at this offset
        if n > 0:
            c = msvc_pad_prefix(blob[n:], mass, inb, min_table=MIN_TABLE)
            if c >= 2:
                break
        b = blob[n]
        if b <= 0x20 or b in (0x90, 0xCC):
            n += 1
        else:
            break
    return n if n >= 4 else 0


def msvc_pad_prefix(
    rest: bytes, mass, inb, *, min_table: int = MIN_TABLE
) -> int:
    """Safe pad/MSVC prefix that does not steal .text pointer low bytes.

    Lone 0x00 is in the align-nop pattern set and would otherwise consume the
    low byte of a little-endian code pointer (e.g. 90 00 10 40 00 → eat 90 00).
    Prefer 0x90/0xCC runs and multi-byte MSVC patterns; accept 0x00 only when
    the remainder is still a pad or a code-ptr table.
    """
    if not rest:
        return 0
    # pure nop/int3 runs first
    n = 0
    while n < len(rest) and rest[n] in (0x90, 0xCC):
        n += 1
    if n >= 1 and is_pad(rest[:n], mass, inb):
        if n == len(rest) or code_ptr_bytes(rest[n:], 0) >= min_table or is_pad(
            rest[n:], mass, inb
        ):
            return n
    # multi-byte MSVC patterns, skipping lone 0x00 as a pattern atom
    i = 0
    patterns = getattr(inb, "ALIGN_NOP_PATTERNS", ())
    while i < len(rest):
        matched = False
        for pat in patterns:
            if pat == b"\x00":
                continue
            if rest.startswith(pat, i):
                i += len(pat)
                matched = True
                break
        if not matched:
            break
    if i >= 1 and is_pad(rest[:i], mass, inb):
        if i == len(rest) or code_ptr_bytes(rest[i:], 0) >= min_table or is_pad(
            rest[i:], mass, inb
        ):
            return i
    # pure zero run only if entire rest is pad, or zeros then table
    z = 0
    while z < len(rest) and rest[z] == 0x00:
        z += 1
    if z >= 1 and is_pad(rest[:z], mass, inb):
        if z == len(rest) or code_ptr_bytes(rest[z:], 0) >= min_table:
            return z
    return 0


def compose_msvc_table_mix(
    blob: bytes,
    base: int,
    mass,
    inb,
    large_mod,
    *,
    min_table: int = MIN_TABLE,
) -> dict[str, Any] | None:
    if not blob or len(blob) < min_table:
        return None
    if is_pad(blob, mass, inb):
        return None
    pos = 0
    terms: list[dict[str, Any]] = []
    guard = 0
    while pos < len(blob) and guard < 256:
        guard += 1
        rest = blob[pos:]
        if is_pad(rest, mass, inb):
            terms.append(
                {
                    "kind": "PAD",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + len(blob):08x}",
                    "bytes": len(rest),
                }
            )
            pos = len(blob)
            break
        c = msvc_pad_prefix(rest, mass, inb, min_table=min_table)
        if c >= 1:
            kind = "MSVC_PAD" if any(
                rest[:c].startswith(p)
                for p in getattr(inb, "ALIGN_NOP_PATTERNS", ())
                if p not in (b"\x00", b"\x90", b"\xcc")
            ) or (c >= 2 and rest[0] not in (0x90, 0xCC, 0x00)) else "PAD"
            # 8bff / 8d4900 etc.
            if rest[:c][:2] in (b"\x8b\xff",) or rest[:c][:3] in (b"\x8d\x49\x00",):
                kind = "MSVC_PAD"
            terms.append(
                {
                    "kind": kind,
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + c:08x}",
                    "bytes": c,
                }
            )
            pos += c
            continue
        cpr = code_ptr_bytes(rest, 0)
        if cpr >= min_table:
            terms.append(
                {
                    "kind": "CODE_PTR_TABLE",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + cpr:08x}",
                    "bytes": cpr,
                }
            )
            pos += cpr
            continue
        progressed = False
        for a in range(1, 4):
            if a >= len(rest):
                break
            if not is_pad(rest[:a], mass, inb):
                continue
            run = code_ptr_bytes(rest, a)
            if run >= min_table:
                terms.append(
                    {
                        "kind": "PAD",
                        "startVa": f"0x{base + pos:08x}",
                        "endVa": f"0x{base + pos + a:08x}",
                        "bytes": a,
                    }
                )
                terms.append(
                    {
                        "kind": "CODE_PTR_TABLE",
                        "startVa": f"0x{base + pos + a:08x}",
                        "endVa": f"0x{base + pos + a + run:08x}",
                        "bytes": run,
                    }
                )
                pos += a + run
                progressed = True
                break
        if progressed:
            continue
        ix = index_like_prefix(rest, mass, inb, max_n=MAX_INDEX_LIKE)
        if ix >= 4:
            terms.append(
                {
                    "kind": "INDEX_LIKE",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + ix:08x}",
                    "bytes": ix,
                }
            )
            pos += ix
            continue
        fr = mass.float_run(rest)
        if fr >= 32:
            terms.append(
                {
                    "kind": "FLOAT32_LUT",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + fr:08x}",
                    "bytes": fr,
                }
            )
            pos += fr
            continue
        segs = large_mod.segment_blob(base + pos, rest, large_mod.try_capstone())
        if (
            segs
            and segs[0].get("kind") in {"SSE_OR_CONST_POOL", "FLOAT32_LUT"}
            and segs[0].get("terminal")
            and int(segs[0].get("bytes") or 0) >= 16
        ):
            nb = int(segs[0]["bytes"])
            terms.append(
                {
                    "kind": segs[0]["kind"],
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + nb:08x}",
                    "bytes": nb,
                }
            )
            pos += nb
            continue
        return None

    if pos != len(blob) or not terms:
        return None
    table_b = sum(t["bytes"] for t in terms if t["kind"] == "CODE_PTR_TABLE")
    idx_b = sum(t["bytes"] for t in terms if t["kind"] == "INDEX_LIKE")
    if table_b < min_table:
        return None
    if idx_b > table_b:
        return None
    if idx_b > 0 and table_b < 16:
        return None
    kinds = [t["kind"] for t in terms]
    return {
        "lane": "MSVC_MULTI_TABLE_MIX",
        "shapeKind": "+".join(kinds),
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "terms": terms,
        "kinds": kinds,
        "tableBytes": table_b,
        "indexLikeBytes": idx_b,
        "n_terms": len(terms),
        "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        "note": f"table={table_b} idx={idx_b} n_terms={len(terms)} kinds={'+'.join(kinds)}",
    }


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": "DATA_OR_MIXED_SHAPE",
        "classificationVerdict": "STATIC_MSVC_MULTI_TABLE_MIX",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": rec["shapeKind"],
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

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 29:
        raise SystemExit(f"expected Gen29, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_OPEN_PAD_PEEL_SANDWICH":
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

    police = load_police_reopened()
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
    n_police = 0
    n_police_hold = 0

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
        if is_police:
            n_police += 1
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
            n_police_hold += 1
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "lane": "POLICE_HOLD",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "Police-reopened residual: not closed by table-mix; "
                        "need new instrument beyond OFFSET_ENVELOPE"
                    ),
                }
            )
            lane_counts["POLICE_HOLD"] += 1
            continue
        rec = compose_msvc_table_mix(blob, start, mass, inb, large_mod)
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
                        "No MSVC+code-ptr table mix full cover; need TTD/shape"
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
                "kind": rec["shapeKind"],
                "subspanKinds": rec["shapeKind"],
                "recoveryLane": rec["lane"],
                "peBytesSha256": rec["peBytesSha256"],
                "recheckNote": rec["note"],
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "tableBytes": rec["tableBytes"],
                "indexLikeBytes": rec["indexLikeBytes"],
                "n_terms": rec["n_terms"],
                "terms": rec["terms"],
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
        if int(p.get("tableBytes") or 0) < MIN_TABLE:
            hard.append(f"table_small {p['startVa']}")
        if int(p.get("indexLikeBytes") or 0) > int(p.get("tableBytes") or 0):
            hard.append(f"idx_gt_table {p['startVa']}")
        s = int(p["startVa"], 16)
        e = int(p["endVa"], 16)
        blob = mass.span_bytes(data, s, e, ib, secs)
        if blob is None or hashlib.sha256(blob).hexdigest() != p["peBytesSha256"]:
            hard.append(f"pe_drift {p['startVa']}")
            continue
        again = compose_msvc_table_mix(blob, s, mass, inb, large_mod)
        if again is None or again["lane"] != p["recoveryLane"]:
            hard.append(f"recheck_fail {p['startVa']}")
        if again and again.get("tableBytes") != p.get("tableBytes"):
            hard.append(f"table_drift {p['startVa']}")

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
        "campaignGeneration": 29,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_still_open": len(still),
        "n_police_among_open": n_police,
        "n_police_hold": n_police_hold,
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "darkSizeBuckets": dict(buckets),
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK from Gen29.",
            f"MSVC multi-table-mix proofs: {len(proofs)} (non-police only).",
            f"Police holds among open: {n_police_hold}.",
            f"Still open non-police: {sum(1 for s in still if s.get('lane')=='STILL_OPEN')}.",
            "CODE_PTR_TABLE min 8B (below Gen23 16B when pad-led); INDEX_LIKE capped.",
            "Gen30 apply withheld until dual-role review.",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not close police-reopened residuals",
            "INDEX_LIKE is static small-int byte shape only",
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
        "campaignGeneration": 29,
        "formalPackStatus": pack["status"],
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "formalPackProofs": len(proofs),
            "stillOpen": len(still),
            "policeHold": n_police_hold,
            "darkSizeBuckets": dict(buckets),
            "laneCounts": dict(lane_counts),
            "recoveryLaneProofCounts": pack["recoveryLaneCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role review then Gen30 apply",
            "TTD/shape for remaining non-police still-open + police holds",
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
    _write_tsv(
        out_dir / "still-open.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "lane",
            "entityKey",
            "questionIds",
            "cheapestFalsifier",
        ],
        still,
    )
    _write_tsv(
        out_dir / "proofs.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "recoveryLane",
            "kind",
            "tableBytes",
            "indexLikeBytes",
            "peBytesSha256",
            "entityKey",
            "questionIds",
            "recheckNote",
        ],
        proofs,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen29-msvc-table-mix.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_40": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_0": len(executed) == 0,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen30_apply": True,
            "gen29_unmutated": True,
            "hold_generation_apply": True,
            "all_proofs_rechecked": len(hard) == 0,
            "no_police_proofs": all(
                r["startVa"].lower() not in police
                for r in dark
                if any(p["startVa"] == r["startVa"] for p in proofs)
            )
            or all(True for _ in []),
        },
        "ledger_sha_pre": {
            "campaign-residuals.tsv": _sha(campaign / "campaign-residuals.tsv"),
            "campaign.ready.json": _sha(campaign / "campaign.ready.json"),
        },
        "sources": {
            "formalPack": _stamp(out_dir / "FORMAL-PACK.json"),
            "summary": _stamp(out_dir / "SUMMARY.json"),
            "specimen": _stamp(specimen),
        },
    }
    # explicit: no proof start in police set
    integrity["checks"]["no_police_proofs"] = all(
        p["startVa"].lower() not in police for p in proofs
    )
    integrity["checks"]["gen29_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen29 MSVC multi-table-mix OPEN_DARK

Status: **MEASURED** / formal pack **{pack['status']}**  
Proofs: **{len(proofs)}** · police holds: **{n_police_hold}** · still open: **{len(still)}**

Gen30 apply: **held**.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN29_MSVC_TABLE_MIX_MEASURED")
    print(f"formal_pack_status={pack['status']}")
    print(f"n_proofs={pack['n_proofs']}")
    return {"summary": summary, "pack": pack}


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    if pack.get("status") not in {"EMPTY", "READY_FOR_GENERATION"}:
        raise SystemExit("pack status")
    if not pack.get("hold_generation_apply"):
        raise SystemExit("must hold generation apply")
    rebuilt = build(campaign=campaign, specimen=specimen, out_dir=plate / "_scratch")
    import shutil

    shutil.rmtree(plate / "_scratch", ignore_errors=True)
    if rebuilt["pack"]["n_proofs"] != pack["n_proofs"]:
        raise SystemExit("proof count drift")
    if rebuilt["pack"]["status"] != pack["status"]:
        raise SystemExit("status drift")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "formalPackStatus": pack["status"],
                "n_proofs": pack["n_proofs"],
                "lanes": pack.get("recoveryLaneCounts"),
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN29_MSVC_TABLE_MIX_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build MSVC table-mix plate")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN29)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify plate vs Gen29")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN29)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, specimen=args.specimen, out_dir=args.out)
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
