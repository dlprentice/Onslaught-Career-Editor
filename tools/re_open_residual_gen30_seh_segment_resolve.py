#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen30 remaining OPEN_DARK: SEH filter stubs + segment-resolve compose.

Exports OPEN_DARK (30) from Generation 30 tip. Non-police only.

Lanes (TERMINAL_BOUNDED_AMBIGUITY):

  SEH_FILTER_STUB / SEH_PLUS_EXACT_INSN / SEH_PLUS_MULTI / SEH_PLUS_ENVELOPE
    MSVC SEH filter pattern: push [ebp+disp8]; call rel32; pop ecx; ret
    optional pure/MSVC pad trail, single exact insn trail, multi-unit trail,
    or envelope trail.

  SEGMENT_RESOLVE
    large.segment_blob full walk; each terminal segment kept; each non-terminal
    piece re-resolved via pad / MSVC table-mix / pure table / index-like /
    float / multi-unit / envelope / SEH / short exact insn (≤8B, 1 insn) /
    body ending ret/jmp (non_pad≥2). Full residual cover only.

Does **not** close police-reopened OFFSET_ENVELOPE holds.
Does **not** mutate Gen30. Does **not** invent names or REBUILD_READY.
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

SCHEMA = "bea.re.open-residual-gen30-seh-segment-resolve.v1"
PACK_SCHEMA = "bea.re.open-residual-gen30-seh-segment-resolve-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_SEH_SEGMENT_RESOLVE.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 30
EXPECTED_OPEN_EXECUTED = 0
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN30 = Path(
    "local-lab/residual-terminal-generation30-msvc-table-mix-20260805-v1/"
    "generation-30-residual-terminal-msvc-table-mix"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen30-seh-segment-resolve-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE re-decode: SEH pattern / segment resolve fails full cover; "
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


def exact_cover_info(blob: bytes, base: int, md) -> dict[str, Any] | None:
    if not blob or md is None:
        return None
    insns = list(md.disasm(blob, base))
    cov = 0
    n = 0
    last = ""
    non_pad = 0
    for insn in insns:
        if cov + insn.size > len(blob):
            break
        cov += insn.size
        n += 1
        last = insn.mnemonic
        if insn.mnemonic not in {"nop", "int3"}:
            non_pad += 1
    if cov != len(blob) or n < 1:
        return None
    return {"n_insns": n, "last": last, "non_pad": non_pad}


def seh_compose(blob: bytes, base: int, md, mass, inb, mu_mod) -> dict[str, Any] | None:
    """MSVC SEH filter: push [ebp+disp8]; call; pop ecx; ret (+ constrained trail)."""
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
    if not trail:
        return {
            "lane": "SEH_FILTER_STUB",
            "shapeKind": "SEH_FILTER_STUB",
            "trailKind": "NONE",
            "sehBytes": 10,
            "trailBytes": 0,
        }
    if is_pad(trail, mass, inb):
        return {
            "lane": "SEH_FILTER_STUB",
            "shapeKind": "SEH_FILTER_STUB+PAD",
            "trailKind": "PAD",
            "sehBytes": 10,
            "trailBytes": len(trail),
        }
    if mu_mod.multi_unit_pack(trail, base + 10, md, mass):
        return {
            "lane": "SEH_PLUS_MULTI",
            "shapeKind": "SEH_PLUS_MULTI",
            "trailKind": "MULTI",
            "sehBytes": 10,
            "trailBytes": len(trail),
        }
    if mass.try_envelope_at(trail, base + 10, md):
        return {
            "lane": "SEH_PLUS_ENVELOPE",
            "shapeKind": "SEH_PLUS_ENVELOPE",
            "trailKind": "ENV",
            "sehBytes": 10,
            "trailBytes": len(trail),
        }
    info = exact_cover_info(trail, base + 10, md)
    if info and info["n_insns"] == 1:
        return {
            "lane": "SEH_PLUS_EXACT_INSN",
            "shapeKind": f"SEH_PLUS_EXACT_INSN/{info['last']}",
            "trailKind": "EXACT_INSN",
            "sehBytes": 10,
            "trailBytes": len(trail),
            "trailLast": info["last"],
        }
    if (
        info
        and info["last"] in {"ret", "retn", "jmp"}
        and info["non_pad"] >= 2
    ):
        return {
            "lane": "SEH_PLUS_BODY_CT",
            "shapeKind": f"SEH_PLUS_BODY_CT/{info['last']}",
            "trailKind": "BODY_CT",
            "sehBytes": 10,
            "trailBytes": len(trail),
            "trailLast": info["last"],
        }
    if mu_mod.multi_unit_pack(blob, base, md, mass):
        return {
            "lane": "MULTI_SEH_LEAD",
            "shapeKind": "MULTI_SEH_LEAD",
            "trailKind": "MULTI_WHOLE",
            "sehBytes": 10,
            "trailBytes": len(trail),
        }
    return None


def resolve_piece(
    piece: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    mu_mod,
    mtm_mod,
) -> str | None:
    if not piece:
        return None
    if is_pad(piece, mass, inb):
        return "PAD"
    rec = mtm_mod.compose_msvc_table_mix(piece, base, mass, inb, large_mod)
    if rec is not None:
        return "MTM"
    if len(piece) >= 8 and len(piece) % 4 == 0:
        if all(
            TEXT_LO <= struct.unpack_from("<I", piece, i)[0] < TEXT_HI
            for i in range(0, len(piece), 4)
        ):
            return "TABLE"
    if 4 <= len(piece) <= 64 and all(
        b <= 0x20 or b in (0x90, 0xCC) for b in piece
    ):
        return "IDX"
    fr = mass.float_run(piece)
    if fr == len(piece) and fr >= 32:
        return "FLOAT"
    if mu_mod.multi_unit_pack(piece, base, md, mass):
        return "MULTI"
    if mass.try_envelope_at(piece, base, md):
        return "ENV"
    seh = seh_compose(piece, base, md, mass, inb, mu_mod)
    if seh is not None:
        return seh["lane"]
    info = exact_cover_info(piece, base, md)
    if info and info["n_insns"] == 1 and len(piece) <= 8:
        return "EXACT_INSN"
    if (
        info
        and info["last"] in {"ret", "retn", "jmp"}
        and info["non_pad"] >= 2
    ):
        return "BODY_CT"
    return None


def segment_resolve(
    blob: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    mu_mod,
    mtm_mod,
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
        else:
            alt = resolve_piece(
                piece, base + off, md, mass, inb, large_mod, mu_mod, mtm_mod
            )
            if alt is None:
                return None
            kind = alt
        terms.append(
            {
                "kind": kind,
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
        "lane": "SEGMENT_RESOLVE",
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
) -> dict[str, Any] | None:
    seh = seh_compose(blob, base, md, mass, inb, mu_mod)
    if seh is not None:
        seh["terminalState"] = "TERMINAL_BOUNDED_AMBIGUITY"
        seh["peBytesSha256"] = hashlib.sha256(blob).hexdigest()
        seh["note"] = (
            f"seh={seh.get('sehBytes')} trail={seh.get('trailBytes')} "
            f"trailKind={seh.get('trailKind')}"
        )
        return seh
    seg = segment_resolve(
        blob, base, md, mass, inb, large_mod, mu_mod, mtm_mod
    )
    if seg is not None:
        seg["terminalState"] = "TERMINAL_BOUNDED_AMBIGUITY"
        seg["peBytesSha256"] = hashlib.sha256(blob).hexdigest()
        return seg
    return None


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": "AMBIGUOUS",
        "classificationVerdict": f"STATIC_SEH_SEGMENT/{rec['lane']}",
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
    mu_mod = _load_mod(
        "re_open_residual_gen19_multi_unit",
        ROOT / "tools" / "re_open_residual_gen19_multi_unit.py",
    )
    mtm_mod = _load_mod(
        "re_open_residual_gen29_msvc_table_mix",
        ROOT / "tools" / "re_open_residual_gen29_msvc_table_mix.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 30:
        raise SystemExit(f"expected Gen30, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_OPEN_MSVC_TABLE_MIX":
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
    n_police = 0

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
            blob, start, md, mass, inb, large_mod, mu_mod, mtm_mod
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
                        "No SEH stub / segment-resolve full cover; need TTD or new shape"
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
                "recheckNote": rec.get("note") or "",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "detail": {
                    k: v
                    for k, v in rec.items()
                    if k
                    not in {
                        "lane",
                        "shapeKind",
                        "note",
                        "terminalState",
                        "peBytesSha256",
                        "terms",
                    }
                },
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
            blob, s, md, mass, inb, large_mod, mu_mod, mtm_mod
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
        "campaignGeneration": 30,
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
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK from Gen30.",
            f"SEH/segment-resolve proofs: {len(proofs)} (non-police only).",
            f"Police holds: {sum(1 for s in still if s.get('lane')=='POLICE_HOLD')}.",
            f"Still open non-police: {sum(1 for s in still if s.get('lane')=='STILL_OPEN')}.",
            "Gen31 apply withheld until dual-role review.",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not re-close police OFFSET_ENVELOPE holds",
            "SEGMENT_RESOLVE reuses table-mix/pad/multi on open subspans only",
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
        "campaignGeneration": 30,
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
            "Dual-role review then Gen31 apply",
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
        "schema": "bea.re.open-residual-gen30-seh-segment-resolve.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_30": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_0": len(executed) == 0,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen31_apply": True,
            "gen30_unmutated": True,
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
    integrity["checks"]["gen30_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen30 SEH + segment-resolve OPEN_DARK

Status: **MEASURED** / formal pack **{pack['status']}**  
Proofs: **{len(proofs)}** · police holds: **{pack['n_police_hold']}**

Gen31 apply: **held**.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN30_SEH_SEGMENT_RESOLVE_MEASURED")
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
    print("OPEN_RESIDUAL_GEN30_SEH_SEGMENT_RESOLVE_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build SEH/segment-resolve plate")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN30)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify plate vs Gen30")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN30)
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
