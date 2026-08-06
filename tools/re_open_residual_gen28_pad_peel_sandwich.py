#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen28 remaining OPEN_DARK: pad-peel compose + sandwich full-linear instrument.

Exports OPEN_DARK (58) from Generation 28 tip.

Recovery lanes (TERMINAL_BOUNDED_AMBIGUITY / TERMINAL_PADDING):

  PAD_PEEL_SMALL_TABLE / PAD_PEEL_DATA_SHAPE / PAD_PEEL_PARTIAL_DATA /
  PAD_PEEL_MULTI / PAD_PEEL_ENVELOPE
    peel maximal pure/MSVC lead+trail pad; prior full-cover compose on head;
    require at least one pad side (new vs Gen21–24 whole-residual compose).
    Envelope peel only on non-police rows.

  PURE_PAD
    whole residual pure/MSVC pad.

  SANDWICH_FULL_LINEAR
    full linear decode of residual; prev residual endVa==start and
    next residual startVa==end both TERMINAL_*; non-police only.

Does **not** re-close police OFFSET_ENVELOPE via envelope alone.
Does **not** mutate Gen28. Does **not** invent names or REBUILD_READY.
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

SCHEMA = "bea.re.open-residual-gen28-pad-peel-sandwich.v1"
PACK_SCHEMA = "bea.re.open-residual-gen28-pad-peel-sandwich-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_PAD_PEEL_SANDWICH.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 58
EXPECTED_OPEN_EXECUTED = 0
EXPECTED_RESIDUALS = 6117

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN28 = Path(
    "local-lab/residual-terminal-generation28-open-dark-unit-split-20260805-v1/"
    "generation-28-residual-terminal-open-dark-unit-split"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen28-pad-peel-sandwich-20260805-v1")
GEN25_READY = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen/campaign.ready.json"
)
GEN25_RECEIPT = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen/generation-receipt.json"
)

DEFAULT_FALSIFIER = (
    "PE re-decode: pad peel + head compose fails; sandwich neighbors not terminal "
    "or linear decode breaks; residual membership of a named body; REBUILD_READY claim"
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


def peel_pad(blob: bytes, mass, inb, *, max_side: int = 128) -> tuple[int, int, bytes]:
    """Maximal pure/MSVC lead and trail pad; return (lead, trail, head)."""
    if not blob:
        return 0, 0, b""
    lead = 0
    for L in range(1, min(max_side, len(blob)) + 1):
        if is_pad(blob[:L], mass, inb):
            lead = L
        else:
            break
    trail = 0
    body_avail = len(blob) - lead
    for T in range(1, min(max_side, body_avail) + 1):
        if is_pad(blob[-T:], mass, inb):
            trail = T
        else:
            break
    head = blob[lead : len(blob) - trail if trail else len(blob)]
    return lead, trail, head


def full_linear_decode(blob: bytes, base: int, md) -> dict[str, Any] | None:
    if not blob or md is None:
        return None
    insns = list(md.disasm(blob, base))
    covered = 0
    non_pad = 0
    n = 0
    last_m = ""
    for insn in insns:
        if covered + insn.size > len(blob):
            break
        covered += insn.size
        n += 1
        last_m = insn.mnemonic
        if insn.mnemonic not in {"nop", "int3"}:
            non_pad += 1
    if covered != len(blob) or non_pad < 1 or n < 1:
        return None
    return {"n_insns": n, "non_pad": non_pad, "last": last_m}


def compose_pad_peel(
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
    *,
    police: bool,
) -> dict[str, Any] | None:
    if not blob:
        return None
    if is_pad(blob, mass, inb):
        return {
            "lane": "PURE_PAD",
            "shapeKind": "PURE_PAD",
            "terminalState": "TERMINAL_PADDING",
            "lead": 0,
            "trail": 0,
            "headBytes": 0,
            "note": f"pure pad {len(blob)}B",
        }
    lead, trail, head = peel_pad(blob, mass, inb)
    if lead + trail < 1 or not head:
        return None
    hbase = base + lead
    head_rec = None
    lane = None
    if st_mod.compose_small_table(
        head, hbase, md, mass, inb, large_mod, ds_mod, pd_mod
    ):
        head_rec = st_mod.compose_small_table(
            head, hbase, md, mass, inb, large_mod, ds_mod, pd_mod
        )
        lane = "PAD_PEEL_SMALL_TABLE"
    elif ds_mod.compose_data_shape(head, hbase, md, mass, inb, large_mod):
        head_rec = ds_mod.compose_data_shape(head, hbase, md, mass, inb, large_mod)
        lane = "PAD_PEEL_DATA_SHAPE"
    elif pd_mod.compose_partial_data(head, hbase, md, mass, inb, large_mod, ds_mod):
        head_rec = pd_mod.compose_partial_data(
            head, hbase, md, mass, inb, large_mod, ds_mod
        )
        lane = "PAD_PEEL_PARTIAL_DATA"
    elif mu_mod.multi_unit_pack(head, hbase, md, mass):
        head_rec = mu_mod.multi_unit_pack(head, hbase, md, mass)
        lane = "PAD_PEEL_MULTI"
    elif not police and mass.try_envelope_at(head, hbase, md):
        head_rec = mass.try_envelope_at(head, hbase, md)
        lane = "PAD_PEEL_ENVELOPE"
    if lane is None or head_rec is None:
        return None
    # re-verify peel sides still pad
    if lead and not is_pad(blob[:lead], mass, inb):
        return None
    if trail and not is_pad(blob[-trail:], mass, inb):
        return None
    shape = (
        (head_rec.get("shapeKind") if isinstance(head_rec, dict) else None)
        or (head_rec.get("lane") if isinstance(head_rec, dict) else None)
        or lane
    )
    term = "TERMINAL_BOUNDED_AMBIGUITY"
    if isinstance(head_rec, dict) and head_rec.get("terminalState") == "TERMINAL_DATA":
        # mixed with pad sides → bounded ambiguity
        term = "TERMINAL_BOUNDED_AMBIGUITY"
    return {
        "lane": lane,
        "shapeKind": f"{lane}/{shape}",
        "terminalState": term,
        "lead": lead,
        "trail": trail,
        "headBytes": len(head),
        "headRec": {
            k: head_rec[k]
            for k in head_rec
            if k in {"lane", "shapeKind", "note", "kinds", "n_code", "tableBytes"}
        }
        if isinstance(head_rec, dict)
        else {},
        "note": f"lead={lead} trail={trail} head={len(head)} lane={lane}",
    }


def compose_sandwich(
    blob: bytes,
    base: int,
    end: int,
    md,
    prev: dict[str, str] | None,
    nxt: dict[str, str] | None,
    *,
    police: bool,
) -> dict[str, Any] | None:
    if police or not blob or prev is None or nxt is None:
        return None
    if not (prev.get("campaignState") or "").startswith("TERMINAL"):
        return None
    if not (nxt.get("campaignState") or "").startswith("TERMINAL"):
        return None
    if int(prev["endVa"], 16) != base:
        return None
    if int(nxt["startVa"], 16) != end:
        return None
    lin = full_linear_decode(blob, base, md)
    if lin is None:
        return None
    return {
        "lane": "SANDWICH_FULL_LINEAR",
        "shapeKind": f"SANDWICH_FULL_LINEAR/n{lin['n_insns']}",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "n_insns": lin["n_insns"],
        "non_pad": lin["non_pad"],
        "last": lin["last"],
        "prevState": prev.get("campaignState"),
        "nextState": nxt.get("campaignState"),
        "note": (
            f"sandwich full-linear n={lin['n_insns']} non_pad={lin['non_pad']} "
            f"prev={prev.get('campaignState')} next={nxt.get('campaignState')}"
        ),
    }


def classify_open_dark(
    blob: bytes,
    start: int,
    end: int,
    md,
    mass,
    inb,
    large_mod,
    ds_mod,
    pd_mod,
    st_mod,
    mu_mod,
    prev: dict[str, str] | None,
    nxt: dict[str, str] | None,
    *,
    police: bool,
) -> dict[str, Any] | None:
    peel = compose_pad_peel(
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
        police=police,
    )
    if peel is not None:
        return peel
    return compose_sandwich(blob, start, end, md, prev, nxt, police=police)


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    term = rec.get("terminalState") or "TERMINAL_BOUNDED_AMBIGUITY"
    return {
        "classification": "PADDING" if term == "TERMINAL_PADDING" else "AMBIGUOUS",
        "classificationVerdict": f"STATIC_PAD_PEEL_SANDWICH/{rec['lane']}",
        "terminalState": term,
        "campaignState": term,
        "bytePattern": (
            "PAD_BYTES" if term == "TERMINAL_PADDING" else "MIXED_OR_CODE_LIKE_BYTES"
        ),
        "contractState": term,
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
    if int(ready.get("generation") or 0) != 28:
        raise SystemExit(f"expected Gen28, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_OPEN_DARK_UNIT_SPLIT":
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

    by_end = {int(r["endVa"], 16): r for r in residuals}
    by_start = {int(r["startVa"], 16): r for r in residuals}
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
        rec = classify_open_dark(
            blob,
            start,
            end,
            md,
            mass,
            inb,
            large_mod,
            ds_mod,
            pd_mod,
            st_mod,
            mu_mod,
            by_end.get(start),
            by_start.get(end),
            police=is_police,
        )
        if rec is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "lane": "POLICE_HOLD" if is_police else "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "Police reopen hold / no pad-peel compose / no sandwich "
                        "full-linear; need abs-ptr, TTD, or new shape"
                    ),
                }
            )
            lane_counts["POLICE_HOLD" if is_police else "STILL_OPEN"] += 1
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
                "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                "recheckNote": rec.get("note") or "",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "police_reopen": is_police,
                "detail": {
                    k: v
                    for k, v in rec.items()
                    if k
                    not in {
                        "lane",
                        "shapeKind",
                        "note",
                        "terminalState",
                        "headRec",
                    }
                },
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
        term = p["proposedTerminalState"]
        if term not in {"TERMINAL_BOUNDED_AMBIGUITY", "TERMINAL_PADDING"}:
            hard.append(f"bad_term {p['startVa']}")
        s = int(p["startVa"], 16)
        e = int(p["endVa"], 16)
        blob = mass.span_bytes(data, s, e, ib, secs)
        if blob is None or hashlib.sha256(blob).hexdigest() != p["peBytesSha256"]:
            hard.append(f"pe_drift {p['startVa']}")
            continue
        again = classify_open_dark(
            blob,
            s,
            e,
            md,
            mass,
            inb,
            large_mod,
            ds_mod,
            pd_mod,
            st_mod,
            mu_mod,
            by_end.get(s),
            by_start.get(e),
            police=bool(p.get("police_reopen")),
        )
        if again is None or again["lane"] != p["recoveryLane"]:
            hard.append(f"recheck_fail {p['startVa']}")
        if p["recoveryLane"] == "PAD_PEEL_ENVELOPE" and p.get("police_reopen"):
            hard.append(f"police_env {p['startVa']}")

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
        "campaignGeneration": 28,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_still_open": len(still),
        "n_police_among_open": n_police,
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "darkSizeBuckets": dict(buckets),
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK from Gen28.",
            f"Pad-peel/sandwich proofs: {len(proofs)} "
            f"({dict(Counter(p['recoveryLane'] for p in proofs))}).",
            f"Police among open input: {n_police} (envelope re-close still refused).",
            f"Still open: {len(still)}.",
            "Gen29 apply withheld until dual-role review.",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not re-close police OFFSET_ENVELOPE via envelope peel",
            "Sandwich is residual-adjacency full-linear shape only",
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
        "campaignGeneration": 28,
        "formalPackStatus": pack["status"],
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "formalPackProofs": len(proofs),
            "stillOpen": len(still),
            "policeAmongOpen": n_police,
            "darkSizeBuckets": dict(buckets),
            "laneCounts": dict(lane_counts),
            "recoveryLaneProofCounts": pack["recoveryLaneCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role review then Gen29 apply",
            "Abs-ptr/TTD for remaining still-open + police holds",
            "Do not re-close police envelopes without new instrument",
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
            "police_reopen",
        ],
        proofs,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen28-pad-peel-sandwich.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_58": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_0": len(executed) == 0,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen29_apply": True,
            "gen28_unmutated": True,
            "hold_generation_apply": True,
            "all_proofs_rechecked": len(hard) == 0,
            "no_police_envelope_peel": all(
                not (
                    p.get("police_reopen")
                    and p["recoveryLane"] == "PAD_PEEL_ENVELOPE"
                )
                for p in proofs
            ),
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
    integrity["checks"]["gen28_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen28 pad-peel + sandwich OPEN_DARK

Status: **MEASURED** / formal pack **{pack['status']}**  
Proofs: **{len(proofs)}** · still open: **{len(still)}** · police among open: **{n_police}**

Gen29 apply: **held**.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN28_PAD_PEEL_SANDWICH_MEASURED")
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
    print("OPEN_RESIDUAL_GEN28_PAD_PEEL_SANDWICH_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build pad-peel/sandwich plate")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN28)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify plate vs Gen28")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN28)
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
