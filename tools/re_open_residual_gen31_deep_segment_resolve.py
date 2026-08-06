#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen31 remaining OPEN_DARK: deep segment-resolve + SEH linear trail.

Exports OPEN_DARK (26) from Generation 31 tip. Non-police only.

Lanes (TERMINAL_BOUNDED_AMBIGUITY):

  SEH_PLUS_LINEAR
    MSVC SEH filter (push [ebp+disp8]; call; pop ecx; ret) + trail that
    fully linear-decodes (n_insns>=1). Stricter SEH_* from Gen30 applied first.

  SEGMENT_DEEP / DEEP_MTM
    large.segment_blob walk; open subspans resolved via:
      - existing pad/MTM/table/idx/float/multi/envelope/SEH/exact
      - DEEP_MTM: MSVC multi-table-mix plus short IDX_GLUE (1–16 small-int
        bytes immediately before a CODE_PTR_TABLE >=8B)
    Full residual cover only. idx total still cannot exceed table total.

Does **not** close police-reopened OFFSET_ENVELOPE holds.
Does **not** mutate Gen31. Does **not** invent names or REBUILD_READY.
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

SCHEMA = "bea.re.open-residual-gen31-deep-segment-resolve.v1"
PACK_SCHEMA = "bea.re.open-residual-gen31-deep-segment-resolve-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_DEEP_SEGMENT_RESOLVE.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 26
EXPECTED_OPEN_EXECUTED = 0
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000
MIN_TABLE = 8

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN31 = Path(
    "local-lab/residual-terminal-generation31-seh-segment-resolve-20260805-v1/"
    "generation-31-residual-terminal-seh-segment-resolve"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen31-deep-segment-resolve-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE re-decode: deep segment / SEH linear / index-glue table mix fails; "
    "residual membership of a named body; REBUILD_READY claim"
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


def is_pad(blob: bytes, mass, inb) -> bool:
    return bool(blob) and (
        mass.is_pure_pad(blob) or inb.is_full_align_nop_run(blob)
    )


def index_glue(blob: bytes, *, max_n: int = 16) -> int:
    """1..max_n small-int bytes immediately before a .text code-ptr table."""
    n = 0
    while n < min(len(blob), max_n):
        if n + 4 <= len(blob) and n >= 1:
            v = struct.unpack_from("<I", blob, n)[0]
            if TEXT_LO <= v < TEXT_HI:
                break
        if blob[n] <= 0x20 or blob[n] in (0x90, 0xCC):
            n += 1
        else:
            break
    return n if n >= 1 else 0


def compose_deep_mtm(
    blob: bytes,
    base: int,
    mass,
    inb,
    large_mod,
    mtm_mod,
    *,
    min_table: int = MIN_TABLE,
) -> dict[str, Any] | None:
    """MSVC table-mix with short IDX_GLUE (1–16) before tables."""
    rec = mtm_mod.compose_msvc_table_mix(
        blob, base, mass, inb, large_mod, min_table=min_table
    )
    if rec is not None:
        return {
            "lane": "DEEP_MTM",
            "shapeKind": rec["shapeKind"],
            "terms": rec["terms"],
            "tableBytes": rec["tableBytes"],
            "indexLikeBytes": rec["indexLikeBytes"],
            "n_terms": rec["n_terms"],
            "note": "via_standard_mtm " + rec["note"],
        }

    pos = 0
    terms: list[dict[str, Any]] = []
    table_b = 0
    idx_b = 0
    guard = 0
    while pos < len(blob) and guard < 400:
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
        c = mtm_mod.msvc_pad_prefix(rest, mass, inb, min_table=min_table)
        if c >= 1:
            terms.append(
                {
                    "kind": "MSVC_PAD",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + c:08x}",
                    "bytes": c,
                }
            )
            pos += c
            continue
        cpr = mtm_mod.code_ptr_bytes(rest, 0)
        if cpr >= min_table:
            terms.append(
                {
                    "kind": "CODE_PTR_TABLE",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + cpr:08x}",
                    "bytes": cpr,
                }
            )
            table_b += cpr
            pos += cpr
            continue
        g = index_glue(rest, max_n=16)
        if g >= 1 and g < len(rest):
            cpr2 = mtm_mod.code_ptr_bytes(rest[g:], 0)
            if cpr2 >= min_table:
                terms.append(
                    {
                        "kind": "IDX_GLUE",
                        "startVa": f"0x{base + pos:08x}",
                        "endVa": f"0x{base + pos + g:08x}",
                        "bytes": g,
                    }
                )
                terms.append(
                    {
                        "kind": "CODE_PTR_TABLE",
                        "startVa": f"0x{base + pos + g:08x}",
                        "endVa": f"0x{base + pos + g + cpr2:08x}",
                        "bytes": cpr2,
                    }
                )
                idx_b += g
                table_b += cpr2
                pos += g + cpr2
                continue
        ix = mtm_mod.index_like_prefix(rest, mass, inb, max_n=32)
        if ix >= 4:
            terms.append(
                {
                    "kind": "INDEX_LIKE",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + ix:08x}",
                    "bytes": ix,
                }
            )
            idx_b += ix
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

    if pos != len(blob) or not terms or table_b < min_table:
        return None
    if idx_b > table_b:
        return None
    kinds = [t["kind"] for t in terms]
    return {
        "lane": "DEEP_MTM",
        "shapeKind": "+".join(kinds),
        "terms": terms,
        "tableBytes": table_b,
        "indexLikeBytes": idx_b,
        "n_terms": len(terms),
        "note": f"deep table={table_b} idx={idx_b} n_terms={len(terms)}",
    }


def seh_plus_linear(
    blob: bytes, base: int, md, mass, inb, mu_mod, ssr_mod
) -> dict[str, Any] | None:
    """SEH filter + any full-linear trail (exception-handler sibling body)."""
    seh = ssr_mod.seh_compose(blob, base, md, mass, inb, mu_mod)
    if seh is not None:
        return seh
    if len(blob) < 10:
        return None
    if not (
        blob[0] == 0xFF
        and blob[1] == 0x75
        and blob[3] == 0xE8
        and blob[8] == 0x59
        and blob[9] == 0xC3
    ):
        return None
    trail = blob[10:]
    info = ssr_mod.exact_cover_info(trail, base + 10, md)
    if info is None or info["n_insns"] < 1:
        return None
    return {
        "lane": "SEH_PLUS_LINEAR",
        "shapeKind": f"SEH_PLUS_LINEAR/{info['last']}/n{info['n_insns']}",
        "sehBytes": 10,
        "trailBytes": len(trail),
        "trailLast": info["last"],
        "trailInsns": info["n_insns"],
        "note": (
            f"seh=10 trail={len(trail)} last={info['last']} "
            f"n_insns={info['n_insns']}"
        ),
    }


def resolve_piece(
    piece: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    mu_mod,
    mtm_mod,
    ssr_mod,
) -> dict[str, Any] | None:
    if not piece:
        return None
    if is_pad(piece, mass, inb):
        return {"kind": "PAD", "bytes": len(piece)}
    alt = ssr_mod.resolve_piece(
        piece, base, md, mass, inb, large_mod, mu_mod, mtm_mod
    )
    if alt is not None:
        return {"kind": alt, "bytes": len(piece)}
    deep = compose_deep_mtm(piece, base, mass, inb, large_mod, mtm_mod)
    if deep is not None:
        return {
            "kind": deep["lane"],
            "bytes": len(piece),
            "detail": deep,
        }
    seh = seh_plus_linear(piece, base, md, mass, inb, mu_mod, ssr_mod)
    if seh is not None:
        return {"kind": seh["lane"], "bytes": len(piece), "detail": seh}
    return None


def segment_deep(
    blob: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    mu_mod,
    mtm_mod,
    ssr_mod,
) -> dict[str, Any] | None:
    segs = large_mod.segment_blob(base, blob, large_mod.try_capstone())
    if not segs:
        return None
    terms: list[dict[str, Any]] = []
    off = 0
    for sg in segs:
        nb = int(sg["bytes"])
        piece = blob[off : off + nb]
        if len(piece) != nb:
            return None
        if sg.get("terminal"):
            kind = str(sg.get("kind") or "TERMINAL_SEG")
            terms.append(
                {
                    "kind": kind,
                    "startVa": f"0x{base + off:08x}",
                    "endVa": f"0x{base + off + nb:08x}",
                    "bytes": nb,
                    "sourceSeg": kind,
                }
            )
        else:
            resolved = resolve_piece(
                piece, base + off, md, mass, inb, large_mod, mu_mod, mtm_mod, ssr_mod
            )
            if resolved is None:
                return None
            terms.append(
                {
                    "kind": resolved["kind"],
                    "startVa": f"0x{base + off:08x}",
                    "endVa": f"0x{base + off + nb:08x}",
                    "bytes": nb,
                    "sourceSeg": str(sg.get("kind") or ""),
                }
            )
        off += nb
    if off != len(blob) or not terms:
        return None
    kinds = [t["kind"] for t in terms]
    return {
        "lane": "SEGMENT_DEEP",
        "shapeKind": "+".join(kinds),
        "terms": terms,
        "kinds": kinds,
        "n_terms": len(terms),
        "note": f"n_terms={len(terms)} kinds={'+'.join(kinds)}",
    }


def classify_open_dark(
    blob: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    mu_mod,
    mtm_mod,
    ssr_mod,
) -> dict[str, Any] | None:
    # whole residual SEH (+ linear trail)
    seh = seh_plus_linear(blob, base, md, mass, inb, mu_mod, ssr_mod)
    if seh is not None:
        seh["terminalState"] = "TERMINAL_BOUNDED_AMBIGUITY"
        seh["peBytesSha256"] = hashlib.sha256(blob).hexdigest()
        if "shapeKind" not in seh:
            seh["shapeKind"] = seh["lane"]
        return seh
    # whole deep MTM
    deep = compose_deep_mtm(blob, base, mass, inb, large_mod, mtm_mod)
    if deep is not None:
        deep["terminalState"] = "TERMINAL_BOUNDED_AMBIGUITY"
        deep["peBytesSha256"] = hashlib.sha256(blob).hexdigest()
        return deep
    # segment deep
    seg = segment_deep(
        blob, base, md, mass, inb, large_mod, mu_mod, mtm_mod, ssr_mod
    )
    if seg is not None:
        seg["terminalState"] = "TERMINAL_BOUNDED_AMBIGUITY"
        seg["peBytesSha256"] = hashlib.sha256(blob).hexdigest()
        return seg
    return None


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": "AMBIGUOUS",
        "classificationVerdict": f"STATIC_DEEP_SEGMENT/{rec['lane']}",
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
    mu_mod = _load_mod(
        "re_open_residual_gen19_multi_unit",
        ROOT / "tools" / "re_open_residual_gen19_multi_unit.py",
    )
    mtm_mod = _load_mod(
        "re_open_residual_gen29_msvc_table_mix",
        ROOT / "tools" / "re_open_residual_gen29_msvc_table_mix.py",
    )
    ssr_mod = _load_mod(
        "re_open_residual_gen30_seh_segment_resolve",
        ROOT / "tools" / "re_open_residual_gen30_seh_segment_resolve.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 31:
        raise SystemExit(f"expected Gen31, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_OPEN_SEH_SEGMENT_RESOLVE":
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
    md = Cs(CS_ARCH_X86, CS_MODE_32)

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
        rec = classify_open_dark(
            blob, start, md, mass, inb, large_mod, mu_mod, mtm_mod, ssr_mod
        )
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
                        "No deep segment / SEH linear / index-glue table full cover; "
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
        again = classify_open_dark(
            blob, s, md, mass, inb, large_mod, mu_mod, mtm_mod, ssr_mod
        )
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
        "campaignGeneration": 31,
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
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK from Gen31.",
            f"Deep segment / SEH linear proofs: {len(proofs)} (non-police only).",
            f"Police holds: {sum(1 for s in still if s.get('lane')=='POLICE_HOLD')}.",
            f"Still open non-police: {sum(1 for s in still if s.get('lane')=='STILL_OPEN')}.",
            "IDX_GLUE allows 1–16 small-int bytes before CODE_PTR_TABLE.",
            "Gen32 apply withheld until dual-role review.",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not re-close police OFFSET_ENVELOPE holds",
            "SEH_PLUS_LINEAR is residual-row shape only (filter + sibling body)",
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
        "campaignGeneration": 31,
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
            "Dual-role review then Gen32 apply",
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
            "peBytesSha256",
            "entityKey",
            "questionIds",
            "recheckNote",
        ],
        proofs,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen31-deep-segment-resolve.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_26": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_0": len(executed) == 0,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen32_apply": True,
            "gen31_unmutated": True,
            "hold_generation_apply": True,
            "all_proofs_rechecked": len(hard) == 0,
            "no_police_proofs": all(p["startVa"].lower() not in police for p in proofs),
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
    integrity["checks"]["gen31_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen31 deep segment-resolve OPEN_DARK

Status: **MEASURED** / formal pack **{pack['status']}**  
Proofs: **{len(proofs)}** · police holds: **{pack['n_police_hold']}**

Gen32 apply: **held**.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN31_DEEP_SEGMENT_RESOLVE_MEASURED")
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
    print("OPEN_RESIDUAL_GEN31_DEEP_SEGMENT_RESOLVE_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build deep segment-resolve plate")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN31)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify plate vs Gen31")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN31)
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
