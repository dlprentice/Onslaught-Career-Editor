#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen25 residual-split compose instrument (pad-delimited multi-span).

Exports OPEN_DARK (99) + OPEN_EXECUTED (4) from Generation 25 police reopen.

Recovery lane RESIDUAL_PAD_SPLIT:
  residual fully covered by ordered segments BODY|PAD|BODY|… where:
    - PAD is a pure 0x90/0xCC run of length >= 4 (not bare 0x00 imm noise)
    - each BODY is independently closed by a prior full-cover instrument
      (pure/MSVC pad, multi-unit, data-shape, partial-data, small-table,
       or full-cover code envelope)
  Terminal: TERMINAL_BOUNDED_AMBIGUITY only (mixed subspans).

Does **not** mutate Gen25. Does **not** invent names or REBUILD_READY.
Does **not** apply Gen26 — formal pack only; hold_generation_apply=True.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

SCHEMA = "bea.re.open-residual-gen25-residual-split.v1"
PACK_SCHEMA = "bea.re.open-residual-gen25-residual-split-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_RESIDUAL_SPLIT.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 99
EXPECTED_OPEN_EXECUTED = 4
EXPECTED_RESIDUALS = 6117
MIN_PAD_RUN = 4
PAD_BYTES = frozenset({0x90, 0xCC})

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN25 = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen25-residual-split-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE byte change; pad-run no longer pure 0x90/0xCC; body re-check fails "
    "prior full-cover instrument; residual membership of a named body; "
    "REBUILD_READY claim"
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


def find_pad_split_segments(
    blob: bytes, *, min_pad: int = MIN_PAD_RUN
) -> list[tuple[str, int, int]] | None:
    """Return [(kind, lo, hi), ...] with at least one interior PAD, or None."""
    if not blob or len(blob) < min_pad + 2:
        return None
    raw: list[tuple[str, int, int]] = []
    i = 0
    while i < len(blob):
        if blob[i] in PAD_BYTES:
            j = i
            while j < len(blob) and blob[j] in PAD_BYTES:
                j += 1
            kind = "PAD" if (j - i) >= min_pad else "BODY"
            raw.append((kind, i, j))
            i = j
        else:
            j = i
            while j < len(blob) and blob[j] not in PAD_BYTES:
                j += 1
            raw.append(("BODY", i, j))
            i = j
    # merge consecutive same kind
    segs: list[tuple[str, int, int]] = []
    for kind, lo, hi in raw:
        if segs and segs[-1][0] == kind:
            segs[-1] = (kind, segs[-1][1], hi)
        else:
            segs.append((kind, lo, hi))
    pads = [s for s in segs if s[0] == "PAD"]
    if not pads:
        return None
    # require at least one interior pad with body both sides across the residual
    has_interior = any(lo > 0 and hi < len(blob) for _k, lo, hi in pads)
    if not has_interior:
        return None
    if len(segs) < 3:
        return None
    return segs


def classify_body(
    part: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    ds_mod,
    pd_mod,
    st_mod,
    mu_mod,
) -> dict[str, Any] | None:
    """Return terminal subspan kind for a BODY piece, or None if still open."""
    if not part:
        return None
    if mass.is_pure_pad(part) or inb.is_full_align_nop_run(part):
        return {
            "kind": "PAD_BODY",
            "terminalState": "TERMINAL_PADDING",
            "lane": "PAD",
        }
    mur = mu_mod.multi_unit_pack(part, base, md, mass)
    if mur is not None:
        return {
            "kind": "MULTI_UNIT",
            "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
            "lane": mur.get("lane") or "MULTI_UNIT",
        }
    ds = ds_mod.compose_data_shape(part, base, md, mass, inb, large_mod)
    if ds is not None:
        return {
            "kind": "DATA_SHAPE",
            "terminalState": ds.get("terminalState") or "TERMINAL_BOUNDED_AMBIGUITY",
            "lane": ds.get("lane") or "DATA_SHAPE",
        }
    pd = pd_mod.compose_partial_data(part, base, md, mass, inb, large_mod, ds_mod)
    if pd is not None:
        return {
            "kind": "PARTIAL_DATA",
            "terminalState": pd.get("terminalState") or "TERMINAL_BOUNDED_AMBIGUITY",
            "lane": pd.get("lane") or "PARTIAL_DATA",
        }
    st = st_mod.compose_small_table(
        part, base, md, mass, inb, large_mod, ds_mod, pd_mod
    )
    if st is not None:
        return {
            "kind": "SMALL_TABLE",
            "terminalState": st.get("terminalState") or "TERMINAL_BOUNDED_AMBIGUITY",
            "lane": st.get("lane") or "SMALL_TABLE",
        }
    env = mass.try_envelope_at(part, base, md)
    if env is not None:
        return {
            "kind": "CODE_ENVELOPE",
            "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
            "lane": "STATIC_CODE_DECODE_ENVELOPE",
        }
    return None


def compose_residual_split(
    blob: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    ds_mod,
    pd_mod,
    st_mod,
    mu_mod,
) -> dict[str, Any] | None:
    """Full-cover pad-split compose, or None."""
    segs = find_pad_split_segments(blob)
    if segs is None:
        return None
    terms: list[dict[str, Any]] = []
    for kind, lo, hi in segs:
        piece = blob[lo:hi]
        if kind == "PAD":
            if not all(b in PAD_BYTES for b in piece):
                return None
            terms.append(
                {
                    "kind": "ALIGN_PAD_INTERIOR",
                    "startVa": f"0x{base + lo:08x}",
                    "endVa": f"0x{base + hi:08x}",
                    "bytes": hi - lo,
                    "terminalState": "TERMINAL_PADDING",
                }
            )
            continue
        body = classify_body(
            piece, base + lo, md, mass, inb, large_mod, ds_mod, pd_mod, st_mod, mu_mod
        )
        if body is None:
            return None
        terms.append(
            {
                "kind": body["kind"],
                "startVa": f"0x{base + lo:08x}",
                "endVa": f"0x{base + hi:08x}",
                "bytes": hi - lo,
                "terminalState": body["terminalState"],
                "lane": body["lane"],
            }
        )
    if len(terms) < 3:
        return None
    if not any(t["kind"] == "ALIGN_PAD_INTERIOR" for t in terms):
        return None
    if not any(t["kind"] != "ALIGN_PAD_INTERIOR" for t in terms):
        return None
    kinds = [t["kind"] for t in terms]
    return {
        "lane": "RESIDUAL_PAD_SPLIT",
        "terms": terms,
        "kinds": kinds,
        "shapeKind": "+".join(kinds),
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "n_segments": len(terms),
        "n_pad_segments": sum(1 for t in terms if t["kind"] == "ALIGN_PAD_INTERIOR"),
        "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        "note": f"n_seg={len(terms)} kinds={'+'.join(kinds)}",
    }


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": "AMBIGUOUS",
        "classificationVerdict": "STATIC_RESIDUAL_PAD_SPLIT",
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
    ds_mod = _load_mod(
        "re_open_residual_gen21_data_shape",
        ROOT / "tools" / "re_open_residual_gen21_data_shape.py",
    )
    pd_mod = _load_mod(
        "re_open_residual_gen22_partial_data",
        ROOT / "tools" / "re_open_residual_gen22_partial_data.py",
    )
    st_mod = _load_mod(
        "re_open_residual_gen23_small_table",
        ROOT / "tools" / "re_open_residual_gen23_small_table.py",
    )
    mu_mod = _load_mod(
        "re_open_residual_gen19_multi_unit",
        ROOT / "tools" / "re_open_residual_gen19_multi_unit.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 25:
        raise SystemExit(f"expected Gen25, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_POLICE_REOPEN":
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

    out_dir.mkdir(parents=True, exist_ok=True)
    export_cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "observationState",
        "campaignState",
        "questionIds",
        "cheapestFalsifier",
    ]
    _write_tsv(out_dir / "open-dark.tsv", export_cols, dark)
    _write_tsv(out_dir / "open-executed.tsv", export_cols, executed)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = mass.pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    split_cand: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()

    for r in dark + executed:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        blob = mass.span_bytes(data, start, end, ib, secs)
        src = r["campaignState"]
        if blob is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": end - start,
                    "source": src,
                    "lane": "UNMAPPED",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": "Unmapped PE span",
                }
            )
            lane_counts["UNMAPPED"] += 1
            continue
        segs = find_pad_split_segments(blob)
        if segs is not None and src == "OPEN_DARK_RESIDUAL":
            split_cand.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": end - start,
                    "n_segments": len(segs),
                    "n_pad": sum(1 for k, _, __ in segs if k == "PAD"),
                    "entityKey": r.get("entityKey") or "",
                }
            )
        rec = None
        if src == "OPEN_DARK_RESIDUAL":
            rec = compose_residual_split(
                blob,
                start,
                md,
                mass,
                inb,
                large_mod,
                ds_mod,
                pd_mod,
                st_mod,
                mu_mod,
            )
        if rec is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": end - start,
                    "source": src,
                    "lane": (
                        "SPLIT_STRUCT_OPEN"
                        if segs is not None
                        else "STILL_OPEN"
                    ),
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "Pad-split structure present but body side(s) not full-cover "
                        "terminal"
                        if segs is not None
                        else (
                            "No interior 0x90/0xCC pad-split; need unit-split, TTD, "
                            "or new shape"
                        )
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
                "bytes": end - start,
                "kind": rec["shapeKind"],
                "subspanKinds": rec["shapeKind"],
                "recoveryLane": rec["lane"],
                "peBytesSha256": rec["peBytesSha256"],
                "recheckNote": rec["note"],
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": src,
                "n_segments": rec["n_segments"],
                "proposedTerminalState": prop["terminalState"],
                "proposed": prop,
                "terms": rec["terms"],
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
        "campaignGeneration": 25,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_split_structure_candidates": len(split_cand),
        "n_still_open": len(still),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "hold_generation_apply": True,
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen25.",
            f"Pad-split full-cover proofs: {len(proofs)}.",
            f"Interior 0x90/0xCC split structures (not full-cover): {len(split_cand)}.",
            "Pad delimiter is nop/int3 only (not bare 0x00 imm noise).",
            "OPEN_EXECUTED not closed by this static pad-split lane.",
            "Gen26 apply withheld (hold_generation_apply).",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not re-close police OFFSET_ENVELOPE via pad-split alone",
            "Split structure without full body cover is not a residual terminal",
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
        "campaignGeneration": 25,
        "formalPackStatus": pack["status"],
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
            "formalPackProofs": len(proofs),
            "splitStructureCandidates": len(split_cand),
            "stillOpen": len(still),
            "laneCounts": dict(lane_counts),
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "TTD/static unit-split for 4 OPEN_EXECUTED",
            "New shape / abs-ptr / fallthrough for remaining OPEN_DARK",
            "Do not apply Gen26 from EMPTY residual-split pack",
        ],
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
            "source",
            "lane",
            "entityKey",
            "questionIds",
            "cheapestFalsifier",
        ],
        still,
    )
    _write_tsv(
        out_dir / "split-structure-candidates.tsv",
        ["startVa", "endVa", "bytes", "n_segments", "n_pad", "entityKey"],
        split_cand,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen25-residual-split.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_99": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_4": len(executed) == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen26_apply": True,
            "gen25_unmutated": True,
            "hold_generation_apply": True,
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
    integrity["checks"]["gen25_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen25 residual-split compose

Status: **MEASURED** / formal pack **{pack['status']}**  
Proofs: **{len(proofs)}** · split structures: **{len(split_cand)}**

Pad delimiter: **0x90/0xCC only** (not bare 0x00).  
Gen26 apply: **held**.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN25_RESIDUAL_SPLIT_MEASURED")
    print(f"formal_pack_status={pack['status']}")
    print(f"n_proofs={pack['n_proofs']}")
    return {"summary": summary, "pack": pack}


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark")
    if summary["counts"]["n_open_executed_input"] != EXPECTED_OPEN_EXECUTED:
        raise SystemExit("open executed")
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
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN25_RESIDUAL_SPLIT_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build residual-split plate")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN25)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify plate vs Gen25")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN25)
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
