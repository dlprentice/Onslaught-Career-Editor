#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Formal residual-terminal pack for Gen12 OPEN DARK pad/data candidates only.

Consumes the 12-row ``formal-pack-eligible-pad-data.tsv`` from the open-dark
frontier plate (TINY_PAD_GAP + CODE_ADDRESS_TABLE_PREFIX whole spans). Hard-
rejects STATIC_CODE_DECODE_ENVELOPE and any non pad/data kind.

Does **not** mutate Gen10/Gen11/Gen12. Produces READY_FOR_GENERATION proofs
for a future residual-terminal generation reducer only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.open-dark-pad-data-formal-pack.v1"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_PROOFS = 12
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

# Only these kinds may enter residual-row proofs from this pack.
ALLOWED_KINDS = {
    "TINY_PAD_GAP",
    "ALIGN_PAD_PREFIX",
    "ZERO_RUN_PREFIX",
    "MOSTLY_ALIGN_PADDING",
    "CODE_ADDRESS_TABLE_PREFIX",
    "FLOAT32_TABLE_PREFIX",
    "INDEX_OR_BYTE_TABLE",
}
FORBIDDEN_KINDS = {
    "STATIC_CODE_DECODE_ENVELOPE",
    "CODE_LIKE_PARTIAL",
    "LARGE_MIXED_BLOB",
    "UNRESOLVED_TAIL",
    "OPEN_CODE_FRAGMENT",
}

DEFAULT_CANDIDATES = Path(
    "local-lab/residual-open-dark-frontier-gen12-20260805-v1/"
    "formal-pack-eligible-pad-data.tsv"
)
DEFAULT_DEEPER = Path(
    "local-lab/residual-open-dark-frontier-gen12-20260805-v1/deeper-rows.json"
)
DEFAULT_GEN12 = Path(
    "local-lab/residual-terminal-generation12-mixed-shape-20260805-v1/"
    "generation-12-residual-terminal-mixed-shape"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-dark-pad-data-formal-pack-20260805-v1")


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
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            delta = rva - sva
            if delta >= rawsize:
                return None
            return rawptr + delta
    return None


def span_bytes(data: bytes, start: int, end: int, image_base: int, sections) -> bytes | None:
    if end <= start:
        return None
    o0 = va_to_off(start, image_base, sections)
    if o0 is None or va_to_off(end - 1, image_base, sections) is None:
        return None
    blob = data[o0 : o0 + (end - start)]
    if len(blob) != end - start:
        return None
    return blob


def recheck_kind(kind: str, blob: bytes) -> tuple[bool, str]:
    if not blob:
        return False, "empty"
    if kind in {
        "ALIGN_PAD_PREFIX",
        "MOSTLY_ALIGN_PADDING",
        "ZERO_RUN_PREFIX",
        "TINY_PAD_GAP",
    }:
        if all(b in (0x00, 0x90, 0xCC) for b in blob):
            return True, "pad_bytes_only"
        return False, "non_pad_byte"
    if kind == "CODE_ADDRESS_TABLE_PREFIX":
        usable = len(blob) - (len(blob) % 4)
        if usable < 32:
            return False, "too_short_for_code_ptr_table"
        n = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                n += 1
            else:
                break
        if n >= 8 and n * 4 == usable:
            return True, f"code_ptrs={n}"
        if n >= 8 and n * 4 >= usable * 0.95:
            return True, f"code_ptrs={n}_frac"
        return False, f"code_ptr_run={n}"
    if kind == "FLOAT32_TABLE_PREFIX":
        usable = len(blob) - (len(blob) % 4)
        if usable < 32:
            return False, "too_short_for_float_table"
        ok = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                break
            f = struct.unpack_from("<f", blob, i)[0]
            if f != f or abs(f) == float("inf"):
                break
            if abs(f) > 1e10:
                break
            ok += 1
        if ok >= 8 and ok * 4 >= usable * 0.9:
            return True, f"floats={ok}"
        return False, f"float_run={ok}"
    if kind == "INDEX_OR_BYTE_TABLE":
        # Dense low-byte dwords already filtered upstream; re-bind PE only with
        # a weak density check.
        if len(blob) < 16:
            return False, "too_short"
        usable = len(blob) - (len(blob) % 4)
        low = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if v <= 0xFFFF:
                low += 1
        if low * 4 >= usable * 0.85:
            return True, f"low_dwords={low}"
        return False, f"low_dwords={low}"
    return False, f"forbidden_or_unknown_kind={kind}"


def proposed_for_kind(kind: str) -> dict[str, str]:
    if kind in {
        "ALIGN_PAD_PREFIX",
        "MOSTLY_ALIGN_PADDING",
        "ZERO_RUN_PREFIX",
        "TINY_PAD_GAP",
    }:
        return {
            "classification": "PADDING",
            "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
            "terminalState": "TERMINAL_PADDING",
            "campaignState": "TERMINAL_PADDING",
            "bytePattern": "PADDING_LIKE_BYTES",
            "contractState": "TERMINAL_PADDING",
        }
    if kind in {
        "CODE_ADDRESS_TABLE_PREFIX",
        "FLOAT32_TABLE_PREFIX",
        "INDEX_OR_BYTE_TABLE",
    }:
        return {
            "classification": "DATA",
            "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
            "terminalState": "TERMINAL_DATA",
            "campaignState": "TERMINAL_DATA",
            "bytePattern": "DATA_LIKE_BYTES",
            "contractState": "TERMINAL_DATA",
        }
    raise SystemExit(f"no proposal for kind {kind}")


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(rows, delimiter="\t"))


def load_campaign_residuals(path: Path) -> dict[str, dict[str, str]]:
    by: dict[str, dict[str, str]] = {}
    for row in _read_tsv(path):
        by[row["startVa"].lower()] = row
    return by


def build_pack(
    *,
    specimen: Path,
    candidates_tsv: Path,
    deeper_rows_json: Path,
    campaign: Path,
) -> dict[str, Any]:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != SPECIMEN_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    image_base, sections = pe_map(data)

    ready = campaign / "campaign.ready.json"
    ready_obj = json.loads(ready.read_text(encoding="utf-8"))
    if int(ready_obj.get("generation") or 0) != 12:
        raise SystemExit(f"expected Gen12 campaign, got {ready_obj.get('generation')}")

    cands = _read_tsv(candidates_tsv)
    if len(cands) != EXPECTED_PROOFS:
        raise SystemExit(f"expected {EXPECTED_PROOFS} candidates, got {len(cands)}")

    deeper_rows = json.loads(deeper_rows_json.read_text(encoding="utf-8"))
    if not isinstance(deeper_rows, list):
        deeper_rows = deeper_rows.get("rows") or []
    deeper_by = {r["startVa"].lower(): r for r in deeper_rows}

    camp = load_campaign_residuals(campaign / "campaign-residuals.tsv")
    open_dark = [
        r for r in camp.values() if r.get("campaignState") == "OPEN_DARK_RESIDUAL"
    ]
    if len(open_dark) != 667:
        raise SystemExit(f"Gen12 OPEN_DARK count {len(open_dark)} != 667")

    proofs: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for c in cands:
        if c.get("formalPackEligible") != "True":
            failures.append({"startVa": c.get("startVa"), "reason": "not_eligible"})
            continue
        if c.get("candidateLane") and c.get("candidateLane") != "PAD_OR_DATA":
            failures.append(
                {"startVa": c.get("startVa"), "reason": f"bad_lane:{c.get('candidateLane')}"}
            )
            continue

        start_s = (c.get("startVa") or "").lower()
        end_s = (c.get("endVa") or "").lower()
        start = int(c["startVa"], 16)
        end = int(c["endVa"], 16)
        deeper = deeper_by.get(start_s)
        if deeper is None:
            failures.append({"startVa": c.get("startVa"), "reason": "missing_deeper_row"})
            continue
        if not deeper.get("wholeSpanTerminal"):
            failures.append({"startVa": c.get("startVa"), "reason": "not_whole_span"})
            continue
        terms = [s for s in (deeper.get("subspans") or []) if s.get("terminal")]
        if len(terms) != 1:
            failures.append(
                {
                    "startVa": c.get("startVa"),
                    "reason": f"expected_one_terminal_subspan_got_{len(terms)}",
                }
            )
            continue
        term = terms[0]
        kind = term.get("kind") or ""
        if kind in FORBIDDEN_KINDS:
            failures.append(
                {"startVa": c.get("startVa"), "reason": f"forbidden_kind:{kind}"}
            )
            continue
        if kind not in ALLOWED_KINDS:
            failures.append(
                {"startVa": c.get("startVa"), "reason": f"kind_not_allowed:{kind}"}
            )
            continue
        if term["startVa"].lower() != start_s or term["endVa"].lower() != end_s:
            failures.append(
                {"startVa": c.get("startVa"), "reason": "subspan_bounds_mismatch"}
            )
            continue
        # Candidate TSV kinds must not smuggle envelope
        tsv_kinds = (c.get("subspanKinds") or "").split(";")
        if any(k in FORBIDDEN_KINDS for k in tsv_kinds):
            failures.append(
                {"startVa": c.get("startVa"), "reason": "tsv_forbidden_kind"}
            )
            continue

        camp_row = camp.get(start_s, {})
        if not camp_row:
            failures.append({"startVa": c.get("startVa"), "reason": "missing_campaign_row"})
            continue
        if camp_row.get("campaignState") != "OPEN_DARK_RESIDUAL":
            failures.append(
                {
                    "startVa": c.get("startVa"),
                    "reason": f"campaignState={camp_row.get('campaignState')}",
                }
            )
            continue
        if camp_row.get("observationState") == "EXECUTED":
            failures.append({"startVa": c.get("startVa"), "reason": "executed_excluded"})
            continue
        # Bounds must match campaign residual exactly
        if camp_row.get("startVa", "").lower() != start_s:
            failures.append({"startVa": c.get("startVa"), "reason": "campaign_start_mismatch"})
            continue
        if camp_row.get("endVa", "").lower() != end_s:
            # tolerate 0x padding differences via int compare
            if int(camp_row.get("endVa") or "0", 16) != end:
                failures.append(
                    {"startVa": c.get("startVa"), "reason": "campaign_end_mismatch"}
                )
                continue

        blob = span_bytes(data, start, end, image_base, sections)
        if blob is None:
            failures.append({"startVa": c.get("startVa"), "reason": "unmapped_span"})
            continue
        ok, note = recheck_kind(kind, blob)
        if not ok:
            failures.append(
                {
                    "startVa": c.get("startVa"),
                    "reason": f"recheck_failed:{note}",
                    "kind": kind,
                }
            )
            continue

        qids = (camp_row.get("questionIds") or "").strip()
        prop = proposed_for_kind(kind)
        prop["cheapestFalsifier"] = (
            "PE byte change in span; failed kind re-check; inbound code reference proving "
            "non-terminal semantics; or residual membership of a named function body"
        )
        prop["requiresQuestionSupersession"] = bool(qids)
        prop["shapeKind"] = kind
        prop["shapeReason"] = term.get("reason") or note

        proofs.append(
            {
                "startVa": c["startVa"],
                "endVa": c["endVa"],
                "bytes": len(blob),
                "kind": kind,
                "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                "recheckNote": note,
                "entityKey": camp_row.get("entityKey") or "",
                "questionIds": qids,
                "campaignState": camp_row.get("campaignState") or "",
                "classificationVerdict": camp_row.get("classificationVerdict") or "",
                "observationState": camp_row.get("observationState") or "",
                "proposed": prop,
            }
        )

    if failures:
        raise SystemExit(
            "formal pack hard failures:\n"
            + "\n".join(json.dumps(f) for f in failures)
        )
    if len(proofs) != EXPECTED_PROOFS:
        raise SystemExit(f"proof count {len(proofs)} != {EXPECTED_PROOFS}")
    if any(p["kind"] in FORBIDDEN_KINDS for p in proofs):
        raise SystemExit("forbidden kind in proofs")

    kind_counts = dict(Counter(p["kind"] for p in proofs))
    term_counts = dict(Counter(p["proposed"]["terminalState"] for p in proofs))
    needs_q = sum(1 for p in proofs if p["proposed"]["requiresQuestionSupersession"])

    pack = {
        "schema": SCHEMA,
        "status": "READY_FOR_GENERATION",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": sha,
        "n_proofs": len(proofs),
        "n_hard_mismatches": 0,
        "n_require_question_supersession": needs_q,
        "n_already_clean": len(proofs) - needs_q,
        "kindCounts": kind_counts,
        "proposedTerminalStateCounts": term_counts,
        "expectedProofs": EXPECTED_PROOFS,
        "advance_kind_proposed": "RESIDUAL_TERMINAL_OPEN_DARK_PAD_DATA.v1",
        "parent_generation": 12,
        "parent_residual_classification_authority": (
            "Gen12 residual-terminal mixed-shape is residual-classification authority; "
            "this pack proposes pad/data residual-row terminals only for OPEN_DARK rows"
        ),
        "source": {
            "candidates": str(candidates_tsv).replace("\\", "/"),
            "deeperRows": str(deeper_rows_json).replace("\\", "/"),
            "campaign": str(campaign).replace("\\", "/"),
        },
        "claims": [
            f"Exactly {EXPECTED_PROOFS} whole-span pad/data OPEN_DARK residuals have PE-rechecked formal proofs.",
            f"Kinds: {kind_counts}.",
            f"Proposed terminals: {term_counts}.",
            f"Question supersession required for {needs_q}/{len(proofs)} proofs.",
            "STATIC_CODE_DECODE_ENVELOPE and all code-envelope shapes are excluded by construction.",
            "No Gen10/Gen11/Gen12 ledger mutation; generation apply is a separate reducer step.",
        ],
        "non_claims": [
            "Does not mutate Gen10/Gen11/Gen12 ledgers",
            "Does not close questions without explicit supersession + generation reducer",
            "Does not invent function names or claim REBUILD_READY",
            "Does not admit CODE envelopes or EXECUTED residuals",
            "CODE_ADDRESS_TABLE is TERMINAL_DATA shape, not a live jump-table runtime proof",
            "Admitting without question supersession would launder OPEN questions",
        ],
        "proofs": proofs,
        "hardMismatches": [],
    }
    return pack


def write_plate(pack: dict[str, Any], out_dir: Path, *, campaign: Path, specimen: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )

    # TSV of proofs without full proposed blob nesting for greppability
    cols = [
        "startVa",
        "endVa",
        "bytes",
        "kind",
        "peBytesSha256",
        "recheckNote",
        "entityKey",
        "questionIds",
        "proposedTerminalState",
        "proposedClassification",
        "requiresQuestionSupersession",
    ]
    with (out_dir / "proofs.tsv").open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        writer = csv.DictWriter(handle, fieldnames=cols, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for p in pack["proofs"]:
            writer.writerow(
                {
                    "startVa": p["startVa"],
                    "endVa": p["endVa"],
                    "bytes": p["bytes"],
                    "kind": p["kind"],
                    "peBytesSha256": p["peBytesSha256"],
                    "recheckNote": p["recheckNote"],
                    "entityKey": p["entityKey"],
                    "questionIds": p["questionIds"],
                    "proposedTerminalState": p["proposed"]["terminalState"],
                    "proposedClassification": p["proposed"]["classification"],
                    "requiresQuestionSupersession": p["proposed"]["requiresQuestionSupersession"],
                }
            )

    summary = {
        k: pack[k]
        for k in pack
        if k
        not in {
            "proofs",
            "hardMismatches",
        }
    }
    summary["schema"] = SCHEMA
    summary["status"] = pack["status"]
    summary["plate"] = str(out_dir).replace("\\", "/")
    summary["n_proofs"] = pack["n_proofs"]
    summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    integrity = {
        "schema": "bea.re.open-dark-pad-data-formal-pack.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "n_proofs_12": pack["n_proofs"] == EXPECTED_PROOFS,
            "no_hard_mismatches": pack["n_hard_mismatches"] == 0,
            "specimen_pristine": pack["specimen_sha256"] == SPECIMEN_SHA256,
            "no_forbidden_kinds": all(
                p["kind"] not in FORBIDDEN_KINDS for p in pack["proofs"]
            ),
            "all_kinds_allowed": all(p["kind"] in ALLOWED_KINDS for p in pack["proofs"]),
            "all_open_dark": all(
                p["campaignState"] == "OPEN_DARK_RESIDUAL" for p in pack["proofs"]
            ),
            "no_executed": all(p["observationState"] != "EXECUTED" for p in pack["proofs"]),
            "ready_for_generation": pack["status"] == "READY_FOR_GENERATION",
        },
        "ledger_sha_pre": {
            "campaign-residuals.tsv": _sha(campaign / "campaign-residuals.tsv"),
            "campaign-functions.tsv": _sha(campaign / "campaign-functions.tsv"),
            "campaign.ready.json": _sha(campaign / "campaign.ready.json"),
        },
        "sources": {
            "formalPack": _stamp(out_dir / "FORMAL-PACK.json"),
            "summary": _stamp(out_dir / "SUMMARY.json"),
            "proofsTsv": _stamp(out_dir / "proofs.tsv"),
            "specimen": _stamp(specimen),
            "campaignReady": _stamp(campaign / "campaign.ready.json"),
        },
        "falsifier": [
            "Re-run tools/re_open_dark_pad_data_formal_pack.py build: n_proofs must be 12",
            "Any proof with kind STATIC_CODE_DECODE_ENVELOPE",
            "Gen12 campaign-residuals.tsv sha diverges from ledger_sha_pre",
            "PE recheck fails for any proof span",
        ],
    }
    integrity["checks"]["gen12_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"]["gen12_residuals_unchanged"]
    integrity["sources"]["summary"] = _stamp(out_dir / "SUMMARY.json")
    (out_dir / "INTEGRITY.json").write_text(json.dumps(integrity, indent=2) + "\n", encoding="utf-8")

    (out_dir / "README.md").write_text(
        f"""# OPEN DARK pad/data formal pack (Gen12)

Status: **{pack['status']}**  
Schema: `{SCHEMA}`  
Proofs: **{pack['n_proofs']}** (pad/data only)

## Proposed terminals

| State | Count |
|-------|------:|
{chr(10).join(f'| {k} | {v} |' for k, v in sorted(pack['proposedTerminalStateCounts'].items()))}

## Kinds

| Kind | Count |
|------|------:|
{chr(10).join(f'| {k} | {v} |' for k, v in sorted(pack['kindCounts'].items()))}

## Non-claims

- Not applied to Gen12 yet (formal pack only)
- No CODE envelopes
- No function names / REBUILD_READY
- Question supersession required for open questions before residual-row terminal

## Next

Apply only via residual-terminal generation reducer with question supersession;
do not mutate Gen12 in place.
""",
        encoding="utf-8",
    )


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if pack["n_proofs"] != EXPECTED_PROOFS:
        raise SystemExit("n_proofs drift")
    if summary["n_proofs"] != EXPECTED_PROOFS:
        raise SystemExit("summary n_proofs drift")
    if pack["status"] != "READY_FOR_GENERATION":
        raise SystemExit(f"status {pack['status']}")
    if any(p["kind"] in FORBIDDEN_KINDS for p in pack["proofs"]):
        raise SystemExit("forbidden kind in pack")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        path = campaign / name
        live = _sha(path)
        if live != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    # Re-derive pack and compare proof VAs + pe hashes
    rebuilt = build_pack(
        specimen=specimen,
        candidates_tsv=Path(
            pack.get("source", {}).get("candidates")
            or DEFAULT_CANDIDATES
        ),
        deeper_rows_json=Path(
            pack.get("source", {}).get("deeperRows") or DEFAULT_DEEPER
        ),
        campaign=campaign,
    )
    a = {(p["startVa"].lower(), p["peBytesSha256"], p["kind"]) for p in pack["proofs"]}
    b = {(p["startVa"].lower(), p["peBytesSha256"], p["kind"]) for p in rebuilt["proofs"]}
    if a != b:
        raise SystemExit(f"proof set drift: only_plate={a-b} only_rebuild={b-a}")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "n_proofs": pack["n_proofs"],
                "kindCounts": pack["kindCounts"],
                "proposedTerminalStateCounts": pack["proposedTerminalStateCounts"],
            },
            indent=2,
        )
    )
    print("OPEN_DARK_PAD_DATA_FORMAL_PACK_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    b.add_argument("--deeper-rows", type=Path, default=DEFAULT_DEEPER)
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN12)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, required=True)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN12)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        pack = build_pack(
            specimen=args.specimen,
            candidates_tsv=args.candidates,
            deeper_rows_json=args.deeper_rows,
            campaign=args.campaign,
        )
        write_plate(pack, args.out, campaign=args.campaign, specimen=args.specimen)
        print(
            json.dumps(
                {
                    "status": pack["status"],
                    "n_proofs": pack["n_proofs"],
                    "kindCounts": pack["kindCounts"],
                    "proposedTerminalStateCounts": pack["proposedTerminalStateCounts"],
                },
                indent=2,
            )
        )
        print("OPEN_DARK_PAD_DATA_FORMAL_PACK_OK")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
