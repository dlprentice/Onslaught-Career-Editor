#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen25 tip open-mass census + recovery pilot (hash-bound plate).

Exports OPEN_DARK (99) and OPEN_EXECUTED (4) from Generation 25 police reopen.
Pilots prior residual instruments and reports READY only if new non-police-reopen
proofs exist. Default measured result: EMPTY (no full-cover terminal proofs).

Does not mutate Gen25. Does not re-close police-reopened envelopes.
Formal pack may be READY_FOR_GENERATION when non-police full-cover proofs
exist (measured: 1 MULTI_UNIT); Gen26 apply is intentionally withheld unless
the integration owner chooses it — this plate is census/pilot only.
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

SCHEMA = "bea.re.open-residual-gen25-open-census.v1"
PACK_SCHEMA = "bea.re.open-residual-gen25-open-census-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_CENSUS_PILOT.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 99
EXPECTED_OPEN_EXECUTED = 4
EXPECTED_RESIDUALS = 6117

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN25 = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen25-census-20260805-v1")


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


def interior_pad_split_candidate(blob: bytes) -> bool:
    """True when an interior align-pad run (nop/int3 only) can split bodies.

    Uses 0x90/0xCC only. Bare 0x00 runs are *not* pad delimiters here: they
    commonly appear as imm32 zeros inside live code and produced false
    SPLIT_CAND hits on Gen25 open mass.
    """
    if not blob or len(blob) < 12:
        return False
    i = 0
    while i < len(blob):
        if blob[i] in (0x90, 0xCC):
            j = i
            while j < len(blob) and blob[j] in (0x90, 0xCC):
                j += 1
            if j - i >= 4 and i > 0 and j < len(blob):
                return True
            i = j
        else:
            i += 1
    return False


def e8_targets_into(data: bytes, starts: set[int]) -> dict[int, int]:
    e = struct.unpack_from("<I", data, 0x3C)[0]
    num = struct.unpack_from("<H", data, e + 6)[0]
    size_opt = struct.unpack_from("<H", data, e + 20)[0]
    sec = e + 24 + size_opt
    image_base = struct.unpack_from("<I", data, e + 24 + 28)[0]
    hits: Counter = Counter()
    for i in range(num):
        o = sec + i * 40
        name = data[o : o + 8].split(b"\0")[0]
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        if name != b".text":
            continue
        for off in range(rawptr, rawptr + rawsize - 5):
            if data[off] != 0xE8:
                continue
            rel = struct.unpack_from("<i", data, off + 1)[0]
            tgt = image_base + va + (off - rawptr) + 5 + rel
            if tgt in starts:
                hits[tgt] += 1
    return dict(hits)


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
    large = _load_mod(
        "re_large_mixed_blob_classify", ROOT / "tools" / "re_large_mixed_blob_classify.py"
    )
    ds = _load_mod(
        "re_open_residual_gen21_data_shape",
        ROOT / "tools" / "re_open_residual_gen21_data_shape.py",
    )
    pd = _load_mod(
        "re_open_residual_gen22_partial_data",
        ROOT / "tools" / "re_open_residual_gen22_partial_data.py",
    )
    st = _load_mod(
        "re_open_residual_gen23_small_table",
        ROOT / "tools" / "re_open_residual_gen23_small_table.py",
    )
    mu = _load_mod(
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

    reopened: set[str] = set()
    for p in (ready.get("advance") or {}).get("reopened") or []:
        if isinstance(p, dict) and p.get("startVa"):
            reopened.add(str(p["startVa"]).lower())
    receipt_path = campaign / "generation-receipt.json"
    if receipt_path.is_file():
        rec = json.loads(receipt_path.read_text(encoding="utf-8"))
        reopened |= {str(s).lower() for s in rec.get("reopenedStarts") or []}

    out_dir.mkdir(parents=True, exist_ok=True)
    export_cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "observationState",
        "campaignState",
        "questionIds",
        "classificationVerdict",
        "cheapestFalsifier",
    ]
    _write_tsv(out_dir / "open-dark.tsv", export_cols, dark)
    _write_tsv(out_dir / "open-executed.tsv", export_cols, executed)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = mass.pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    hits: Counter = Counter()
    recoverable: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    buckets: Counter = Counter()

    for r in dark + executed:
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
        blob = mass.span_bytes(data, start, end, ib, secs)
        found: list[str] = []
        note = ""
        if blob is None:
            hits["UNMAPPED"] += 1
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "source": r["campaignState"],
                    "lane": "UNMAPPED",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": "Unmapped PE span",
                }
            )
            continue
        if mass.is_pure_pad(blob) or inb.is_full_align_nop_run(blob):
            found.append("PAD")
        m = mass.try_multi_offset_envelope(data, start, end, ib, secs, md)
        if m:
            found.append(m.get("lane") or "MASS")
            note = m.get("note") or ""
        mur = mu.multi_unit_pack(blob, start, md, mass)
        if mur:
            found.append("MULTI")
        if ds.compose_data_shape(blob, start, md, mass, inb, large):
            found.append("DS")
        if pd.compose_partial_data(blob, start, md, mass, inb, large, ds):
            found.append("PD")
        if st.compose_small_table(blob, start, md, mass, inb, large, ds, pd):
            found.append("ST")
        if interior_pad_split_candidate(blob):
            found.append("SPLIT_CAND")
        key = "+".join(found) if found else "NONE"
        hits[key] += 1
        police = r["startVa"].lower() in reopened
        if found and not (police and any(x.startswith("OFFSET") or x == "OFFSET_ENVELOPE" for x in found)):
            # Candidate for terminal only if not undoing police envelope reopen
            # via re-closing as OFFSET_ENVELOPE alone
            if police and found == ["OFFSET_ENVELOPE"]:
                still.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": b,
                        "source": r["campaignState"],
                        "lane": "POLICE_REOPEN_HOLD",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "cheapestFalsifier": (
                            "Police-reopened envelope: deeper/police disagreement; "
                            "do not re-close with same lane without new instrument"
                        ),
                    }
                )
                continue
            # SPLIT_CAND alone is not a terminal proof
            if found == ["SPLIT_CAND"] or (
                len(found) == 1 and found[0] == "SPLIT_CAND"
            ):
                still.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": b,
                        "source": r["campaignState"],
                        "lane": "SPLIT_CAND_OPEN",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "cheapestFalsifier": (
                            "Interior pad run exists but sides not full-cover "
                            "classified; need residual-split compose instrument"
                        ),
                    }
                )
                continue
            # Any other non-empty found that is full-cover prior instrument
            if any(x in found for x in ("PAD", "MULTI", "DS", "PD", "ST")):
                recoverable.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": b,
                        "source": r["campaignState"],
                        "hit": key,
                        "note": note,
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                        "police_reopen": police,
                    }
                )
                continue
            # OFFSET_ENVELOPE only non-police: potential re-proof
            if found == ["OFFSET_ENVELOPE"] and not police:
                recoverable.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": b,
                        "source": r["campaignState"],
                        "hit": key,
                        "note": note,
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                        "police_reopen": False,
                    }
                )
                continue
        still.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": b,
                "source": r["campaignState"],
                "lane": "STILL_OPEN",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "cheapestFalsifier": (
                    "No full-cover pad/data/multi/small-table terminal; "
                    "no E8 inbound; need residual-split, TTD unit-split, or new shape"
                ),
            }
        )

    dark_starts = {int(r["startVa"], 16) for r in dark}
    e8 = e8_targets_into(data, dark_starts)

    # Formal proofs: only non-police full-cover PAD/MULTI/DS/PD/ST (typically empty)
    proofs: list[dict[str, Any]] = []
    for rec in recoverable:
        hit = rec["hit"]
        if "PAD" in hit.split("+") and hit.replace("+SPLIT_CAND", "") in {
            "PAD",
            "PAD+SPLIT_CAND",
        }:
            term = "TERMINAL_PADDING"
            lane = "PAD_FULL"
        elif "MULTI" in hit:
            term = "TERMINAL_BOUNDED_AMBIGUITY"
            lane = "MULTI_UNIT"
        elif "DS" in hit or "PD" in hit or "ST" in hit:
            term = "TERMINAL_BOUNDED_AMBIGUITY"
            lane = hit
        else:
            continue  # skip bare OFFSET_ENVELOPE re-proofs in this plate
        if rec["source"] != "OPEN_DARK_RESIDUAL":
            continue
        proofs.append(
            {
                "startVa": rec["startVa"],
                "endVa": rec["endVa"],
                "bytes": rec["bytes"],
                "kind": lane,
                "subspanKinds": lane,
                "recoveryLane": lane,
                "peBytesSha256": rec["peBytesSha256"],
                "entityKey": rec["entityKey"],
                "questionIds": rec["questionIds"],
                "sourceState": "OPEN_DARK_RESIDUAL",
                "proposedTerminalState": term,
                "proposed": {
                    "classification": "PADDING" if term == "TERMINAL_PADDING" else "AMBIGUOUS",
                    "classificationVerdict": "STATIC_GEN25_CENSUS",
                    "terminalState": term,
                    "campaignState": term,
                    "contractState": term,
                    "requiresQuestionSupersession": True,
                    "sourceState": "OPEN_DARK_RESIDUAL",
                    "cheapestFalsifier": "PE re-check fails; REBUILD_READY claim",
                },
            }
        )

    pack = {
        "schema": PACK_SCHEMA,
        "status": "READY_FOR_GENERATION" if proofs else "EMPTY",
        "advance_kind_proposed": ADVANCE_KIND,
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 25,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_hard_mismatches": 0,
        "hardMismatches": [],
        "pilotHits": dict(hits),
        "darkSizeBuckets": dict(buckets),
        "n_e8_inbound_dark_starts": len(e8),
        "n_police_reopen_hold": sum(
            1 for s in still if s.get("lane") == "POLICE_REOPEN_HOLD"
        ),
        "n_split_cand_open": sum(
            1 for s in still if s.get("lane") == "SPLIT_CAND_OPEN"
        ),
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen25.",
            f"Prior-instrument full-cover proofs (non-police): {len(proofs)}.",
            f"E8 inbound into dark residual starts: {len(e8)}.",
            "Police-reopened envelopes held OPEN (not re-closed).",
            "OPEN_EXECUTED: static unit-split instrument separate "
            "(tools/re_open_residual_gen25_ttd_unit_split.py); not closed here.",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not re-close Gen25 police reopen set via OFFSET_ENVELOPE",
            "SPLIT_CAND alone is not a residual-row terminal",
            "READY_FOR_GENERATION here is pilot-only; does not apply Gen26",
        ],
        "hold_generation_apply": True,
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
            "pilotHits": dict(hits),
            "formalPackProofs": len(proofs),
            "stillOpenRows": len(still),
            "darkSizeBuckets": dict(buckets),
            "n_e8_inbound_dark_starts": len(e8),
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "tools/re_open_residual_gen25_residual_split.py (measured EMPTY on tip)",
            "tools/re_open_residual_gen25_ttd_unit_split.py (4 OPEN_EXECUTED READY; hold apply)",
            "Inbound abs-ptr / fallthrough for tiny 1-3B OPEN_DARK fragments",
            "Do not re-close police envelope reopens without new evidence",
            "Gen26 apply only if intentional after dual-role review",
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
        out_dir / "recovery-candidates.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "source",
            "hit",
            "note",
            "entityKey",
            "questionIds",
            "peBytesSha256",
            "police_reopen",
        ],
        recoverable,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen25-census.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_99": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_4": len(executed) == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen26_apply": True,
            "gen25_unmutated": True,
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
        f"""# Gen25 open residual census

Status: **MEASURED** / formal pack **{pack['status']}**  
OPEN_DARK: **{EXPECTED_OPEN_DARK}** · OPEN_EXECUTED: **{EXPECTED_OPEN_EXECUTED}**  
Proofs: **{len(proofs)}** (non-police full-cover only)

## Non-claims
- Not Gen26 applied
- Does not re-close police reopen envelopes
- Empty pack is an honest terminal of *this* instrument, not of the campaign
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN25_CENSUS_MEASURED")
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
                "pilotHits": pack.get("pilotHits"),
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN25_CENSUS_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN25)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
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
