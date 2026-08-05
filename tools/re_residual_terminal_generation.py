#!/usr/bin/env python3
"""Generation-11 residual-terminal padding bulk advance.

Parent: Generation 10 TTD call-context campaign (unmutated).
Advance: apply a residual-terminal formal pack (pure PE padding proofs) by:
  - setting residual TERMINAL_PADDING fields
  - closing DARK_TEXT_CLASSIFICATION questions as CLOSED_SURVIVED
  - aligning residual contracts to TERMINAL_PADDING + refuter SURVIVED
  - recording bulk adjudications with evidence hashes

Does not invent function names. Does not claim REBUILD_READY.
Does not reinterpret schema-v3/v4 call-context evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.campaign.v5"
ADVANCE_KIND = "RESIDUAL_TERMINAL_PADDING_BULK"
ADVANCE_SCHEMA = "bea.re.residual-terminal-padding-bulk-advance.v1"
OVERLAY_SCHEMA = "bea.re.residual-terminal-padding-formal.v1"
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
PARENT_GEN10 = Path(
    "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
    "generation-10-ttd-call-context-observation-v2"
)
DEFAULT_OUT = Path(
    "local-lab/residual-terminal-generation11-padding-20260805-v1/"
    "generation-11-residual-terminal-padding"
)
DEFAULT_PACK = Path(
    "local-lab/residual-terminal-formal-pack-padding-20260805-v1/FORMAL-PACK.json"
)

RESIDUAL_COLUMNS = [
    "entityKey", "startVa", "endVa", "bytes", "observedBytes",
    "observationState", "classification", "classificationVerdict", "terminalState",
    "bytePattern", "prevFunc", "nextFunc", "campaignState", "lever",
    "requiresElevation", "cheapestFalsifier", "questionIds", "lastMeasurementDate",
]
QUESTION_COLUMNS = [
    "questionId", "questionType", "entityKey", "priority", "score", "state",
    "requiresElevation", "recommendedInstrument", "question", "cheapestFalsifier",
    "source", "currentOwner", "generation", "attemptCount",
    "parentQuestionId", "lastOutcome", "lastMeasurementDate",
]
CONTRACT_COLUMNS = [
    "contractId", "entityKey", "entityKind", "entryVa", "currentName", "nativeShippedName",
    "contractState", "semanticGrade", "receiver", "inputs", "returns", "writes",
    "sideEffects", "preconditions", "failureModes", "authorVerdict", "runtimeVerdict",
    "refuterVerdict", "questionIds", "evidenceRefs", "cheapestFalsifier",
    "rebuildOwner", "rebuildImplementation", "parityTests", "rebuildState",
    "remainingUncertainty", "supersedesEntityKeys", "lastMeasurementDate",
]
ADJUDICATION_COLUMNS = [
    "adjudicationId", "baseContractId", "entityKey", "overlaySchema",
    "overlayReadySha256", "questionIdsAddressed", "refuterVerdict",
    "refuterEvidenceSha256", "semanticPromotionApplied", "terminalState",
    "successorQuestionIds", "remainingUncertainty", "measuredAtUtc",
]
SUPERSESSION_COLUMNS = [
    "supersessionId", "oldEntityKey", "newEntityKey", "kind", "verdict",
    "evidenceRefs", "measuredAtUtc",
]

FALSIFIER = (
    "Any non-matching pad byte, instruction/function membership, "
    "incoming flow/reference, or overlap contradicts terminal padding classification."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _short_id(prefix: str, material: str) -> str:
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:14]
    return f"{prefix}-{digest}"


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def _file_stamp(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_generation(
    *,
    parent: Path,
    formal_pack: Path,
    out: Path,
    measured_at: str | None = None,
) -> dict:
    measured_at = measured_at or _utc_now()
    pack = json.loads(formal_pack.read_text(encoding="utf-8"))
    if pack.get("status") != "READY_FOR_GENERATION":
        raise SystemExit(f"formal pack not READY_FOR_GENERATION: {pack.get('status')}")
    if pack.get("specimen_sha256") != PRISTINE_SHA256:
        raise SystemExit("formal pack specimen mismatch")
    if int(pack.get("n_mismatches", 1)) != 0:
        raise SystemExit("formal pack has mismatches")
    proofs = pack["proofs"]
    if len(proofs) != 5012:
        raise SystemExit(f"expected 5012 proofs, got {len(proofs)}")

    # Parent integrity via Gen10 sealed verify
    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(parent_ready.get("generation", -1)) != 10:
        raise SystemExit("parent must be generation 10")

    residuals = _read_tsv(parent / "campaign-residuals.tsv")
    questions = _read_tsv(parent / "campaign-questions.tsv")
    contracts = _read_tsv(parent / "campaign-contracts.tsv")
    adjudications = _read_tsv(parent / "campaign-adjudications.tsv")
    supersessions = _read_tsv(parent / "campaign-supersessions.tsv")
    functions = _read_tsv(parent / "campaign-functions.tsv")
    scenarios = _read_tsv(parent / "campaign-scenarios.tsv")
    levers = _read_tsv(parent / "campaign-levers.tsv")

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_entity = {c["entityKey"]: c for c in contracts}
    q_by_id = {q["questionId"]: q for q in questions}

    pack_sha = _sha_file(formal_pack)
    evidence_root = formal_pack.resolve().parent
    evidence_refs_common = [
        f"{formal_pack.resolve()}#sha256={pack_sha}",
        f"{(evidence_root / 'SUMMARY.json').resolve()}#sha256={_sha_file(evidence_root / 'SUMMARY.json')}",
    ]

    closed_qids: list[str] = []
    updated_entities: list[str] = []
    skipped_already = 0
    missing = 0

    for proof in proofs:
        start = proof["startVa"].lower()
        residual = res_by_start.get(start)
        if residual is None:
            missing += 1
            continue
        if residual.get("campaignState") == "TERMINAL_PADDING":
            skipped_already += 1
            # still ensure fields consistent
            continue

        ek = residual["entityKey"]
        qids = [q for q in (residual.get("questionIds") or "").split(";") if q]
        # residual fields
        residual["classification"] = "PADDING"
        residual["classificationVerdict"] = "FORMAL_STATIC_PROOF_SURVIVED"
        residual["terminalState"] = "TERMINAL_PADDING"
        residual["campaignState"] = "TERMINAL_PADDING"
        residual["bytePattern"] = "PADDING_LIKE_BYTES"
        residual["lever"] = "NONE"
        residual["cheapestFalsifier"] = FALSIFIER
        residual["questionIds"] = ""
        residual["lastMeasurementDate"] = measured_at[:10]
        updated_entities.append(ek)

        # contract
        contract = con_by_entity.get(ek)
        if contract is None:
            raise SystemExit(f"missing contract for {ek}")
        contract["contractState"] = "TERMINAL_PADDING"
        contract["semanticGrade"] = "C0_OPAQUE"
        contract["authorVerdict"] = "STATIC_FORMAL_PROOF"
        contract["runtimeVerdict"] = "UNSCORED"
        contract["refuterVerdict"] = "SURVIVED"
        contract["questionIds"] = ""
        contract["evidenceRefs"] = ";".join(
            evidence_refs_common + [f"pe-uniform-pad#sha256={proof['peBytesSha256']}"]
        )
        contract["cheapestFalsifier"] = FALSIFIER
        contract["rebuildOwner"] = "UNASSIGNED"
        contract["rebuildImplementation"] = "UNMAPPED"
        contract["parityTests"] = "UNMAPPED"
        contract["rebuildState"] = "NOT_READY"
        contract["remainingUncertainty"] = (
            "No behavior contract is claimed; this range is structurally proven alignment padding."
        )
        contract["lastMeasurementDate"] = measured_at[:10]

        # questions
        for qid in qids:
            q = q_by_id.get(qid)
            if q is None:
                continue
            q["state"] = "CLOSED_SURVIVED"
            q["lastOutcome"] = "SURVIVED"
            q["lastMeasurementDate"] = measured_at[:10]
            q["attemptCount"] = str(int(q.get("attemptCount") or "0") + 1)
            closed_qids.append(qid)

        # adjudication per residual
        adj_id = _short_id("A", f"residual-terminal|{ek}|{proof['peBytesSha256']}")
        adjudications.append(
            {
                "adjudicationId": adj_id,
                "baseContractId": contract["contractId"],
                "entityKey": ek,
                "overlaySchema": OVERLAY_SCHEMA,
                "overlayReadySha256": pack_sha,
                "questionIdsAddressed": ";".join(qids),
                "refuterVerdict": "SURVIVED",
                "refuterEvidenceSha256": proof["peBytesSha256"],
                "semanticPromotionApplied": "False",
                "terminalState": "TERMINAL_PADDING",
                "successorQuestionIds": "",
                "remainingUncertainty": "Alignment padding only; no function/behavior claim.",
                "measuredAtUtc": measured_at,
            }
        )

        # entity supersession: same key (identity stable) — record proof bind
        sup_id = _short_id("S", f"residual-terminal-pad|{ek}|{proof['peBytesSha256']}")
        supersessions.append(
            {
                "supersessionId": sup_id,
                "oldEntityKey": ek,
                "newEntityKey": ek,
                "kind": ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": f"pe-uniform-pad#sha256={proof['peBytesSha256']}",
                "measuredAtUtc": measured_at,
            }
        )

    if missing:
        raise SystemExit(f"{missing} formal-pack rows missing from parent residuals")
    if len(updated_entities) != 4997:
        # 5012 - 15 already terminal
        raise SystemExit(
            f"expected to update 4997 residuals, updated {len(updated_entities)} "
            f"(already_terminal_skipped={skipped_already})"
        )
    if len(closed_qids) != 4997:
        raise SystemExit(f"expected 4997 closed questions, got {len(closed_qids)}")

    # write out campaign
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # copy sealed reducer from parent for provenance (read-only copy)
    reducer_src = parent / "_reducer"
    if reducer_src.is_dir():
        shutil.copytree(reducer_src, out / "_reducer")

    _write_tsv(out / "campaign-functions.tsv", list(functions[0].keys()), functions)
    _write_tsv(out / "campaign-residuals.tsv", RESIDUAL_COLUMNS, residuals)
    _write_tsv(out / "campaign-questions.tsv", QUESTION_COLUMNS, questions)
    _write_tsv(out / "campaign-contracts.tsv", CONTRACT_COLUMNS, contracts)
    _write_tsv(out / "campaign-scenarios.tsv", list(scenarios[0].keys()), scenarios)
    _write_tsv(out / "campaign-levers.tsv", list(levers[0].keys()), levers)
    _write_tsv(out / "campaign-adjudications.tsv", ADJUDICATION_COLUMNS, adjudications)
    _write_tsv(out / "campaign-supersessions.tsv", SUPERSESSION_COLUMNS, supersessions)

    # counts
    term_pad = sum(1 for r in residuals if r.get("campaignState") == "TERMINAL_PADDING")
    open_dark = sum(1 for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL")
    open_exec = sum(1 for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL")
    q_open = sum(1 for q in questions if q.get("state") == "OPEN")
    q_closed = sum(1 for q in questions if q.get("state") == "CLOSED_SURVIVED")

    counts = {
        "functions": len(functions),
        "residuals": len(residuals),
        "questions": len(questions),
        "scenarios": len(scenarios),
        "levers": len(levers),
        "contracts": len(contracts),
        "adjudications": len(adjudications),
        "supersessions": len(supersessions),
        "residualTerminalPadding": term_pad,
        "residualOpenDark": open_dark,
        "residualOpenExecuted": open_exec,
        "questionsOpen": q_open,
        "questionsClosedSurvived": q_closed,
        "residualTerminalsAddedThisGeneration": len(updated_entities),
        "questionsClosedThisGeneration": len(closed_qids),
    }

    ready = {
        "schema": SCHEMA,
        "reducer": {
            "id": "residual-terminal-padding-bulk-v1",
            "note": "Generation 11 residual-terminal padding bulk; verify via tools/re_residual_terminal_generation.py verify",
        },
        "generatedAtUtc": measured_at,
        "generation": 11,
        "parentCampaign": {
            "path": str(parent.resolve()),
            "ready": _file_stamp(parent / "campaign.ready.json"),
            "generation": 10,
        },
        "sourceSnapshot": parent_ready.get("sourceSnapshot"),
        "advance": {
            "kind": ADVANCE_KIND,
            "schema": ADVANCE_SCHEMA,
            "verdict": "SURVIVED",
            "formalPack": _file_stamp(formal_pack),
            "overlaySchema": OVERLAY_SCHEMA,
            "overlayReadySha256": pack_sha,
            "measuredAtUtc": measured_at,
            "promotions": {
                "residualTerminalPaddingAdded": len(updated_entities),
                "questionsClosedSurvived": len(closed_qids),
                "alreadyTerminalUnchanged": skipped_already,
            },
            "delta": {
                "namesChanged": 0,
                "writesProved": 0,
                "rebuildParityProved": 0,
                "ghidraMutated": False,
                "functionsChanged": 0,
                "residualsTerminalized": len(updated_entities),
            },
            "semanticLimitations": [
                "TERMINAL_PADDING is alignment-structure only; not a function name or behavior contract.",
                "MIXED/EXECUTED residuals are unchanged.",
                "REBUILD_READY not claimed.",
            ],
        },
        "counts": counts,
        "policies": parent_ready.get("policies"),
        "outputs": {
            "campaignResiduals": "campaign-residuals.tsv",
            "campaignQuestions": "campaign-questions.tsv",
            "campaignContracts": "campaign-contracts.tsv",
            "campaignAdjudications": "campaign-adjudications.tsv",
            "campaignSupersessions": "campaign-supersessions.tsv",
        },
    }
    (out / "campaign.ready.json").write_text(
        json.dumps(ready, indent=2) + "\n", encoding="utf-8"
    )

    # receipt for apply
    receipt = {
        "schema": "bea.re.residual-terminal-generation-receipt.v1",
        "status": "APPLIED",
        "generation": 11,
        "out": str(out.resolve()),
        "parent": str(parent.resolve()),
        "formalPackSha256": pack_sha,
        "counts": counts,
        "readySha256": _sha_file(out / "campaign.ready.json"),
        "measuredAtUtc": measured_at,
    }
    (out / "generation-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    return receipt


def verify_generation(campaign: Path, formal_pack: Path, parent: Path) -> dict:
    """Verify Gen11 residual-terminal padding generation without Gen10-specific TTD checks."""
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation", -1)) != 11:
        raise SystemExit(f"expected generation 11, got {ready.get('generation')}")
    advance = ready.get("advance") or {}
    if advance.get("kind") != ADVANCE_KIND:
        raise SystemExit(f"unexpected advance kind {advance.get('kind')}")

    # Parent still verifies as Gen10 authority
    import subprocess

    parent_verify = subprocess.run(
        [
            sys.executable,
            "-B",
            str(parent / "_reducer" / "tools" / "re_campaign.py"),
            "verify",
            "--campaign",
            str(parent),
        ],
        cwd=str(Path.cwd()),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "BEA_REPO_ROOT": str(Path.cwd())},
    )
    if parent_verify.returncode != 0 or "CAMPAIGN_VERIFIED" not in (parent_verify.stdout or ""):
        raise SystemExit(
            "parent Gen10 verify failed:\n"
            + (parent_verify.stdout or "")
            + (parent_verify.stderr or "")
        )

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    questions = _read_tsv(campaign / "campaign-questions.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    pack = json.loads(formal_pack.read_text(encoding="utf-8"))

    if len(functions) != 8124 or len(residuals) != 6117:
        raise SystemExit("function/residual cardinality drifted from Gen10")

    term = [r for r in residuals if r.get("campaignState") == "TERMINAL_PADDING"]
    if len(term) != 5012:
        raise SystemExit(f"expected 5012 TERMINAL_PADDING, got {len(term)}")

    # every formal pack proof is terminal with empty questions
    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_ek = {c["entityKey"]: c for c in contracts}
    for proof in pack["proofs"]:
        r = res_by_start.get(proof["startVa"].lower())
        if r is None:
            raise SystemExit(f"missing residual {proof['startVa']}")
        if r.get("campaignState") != "TERMINAL_PADDING":
            raise SystemExit(f"not terminal {proof['startVa']}")
        if r.get("classification") != "PADDING":
            raise SystemExit(f"classification {proof['startVa']}")
        if r.get("classificationVerdict") != "FORMAL_STATIC_PROOF_SURVIVED":
            raise SystemExit(f"verdict {proof['startVa']}")
        if (r.get("questionIds") or "").strip():
            raise SystemExit(f"residual still has questions {proof['startVa']}")
        c = con_by_ek[r["entityKey"]]
        if c.get("contractState") != "TERMINAL_PADDING":
            raise SystemExit(f"contract state {proof['startVa']}")
        if c.get("refuterVerdict") != "SURVIVED":
            raise SystemExit(f"contract refuter {proof['startVa']}")
        if (c.get("questionIds") or "").strip():
            raise SystemExit(f"contract questions {proof['startVa']}")

    # closed questions: every pack-linked qid CLOSED_SURVIVED
    q_by_id = {q["questionId"]: q for q in questions}
    closed = 0
    for proof in pack["proofs"]:
        r_parent_q = proof.get("questionIds") or ""
        for qid in [x for x in r_parent_q.split(";") if x]:
            q = q_by_id.get(qid)
            if q is None:
                raise SystemExit(f"missing question {qid}")
            if q.get("state") != "CLOSED_SURVIVED" or q.get("lastOutcome") != "SURVIVED":
                raise SystemExit(f"question not closed {qid}")
            closed += 1
    if closed != 4997:
        raise SystemExit(f"expected 4997 closed pack questions, got {closed}")

    # no UNSCORED-as-success on terminals: residual terminal must have falsifier
    empty_f = sum(1 for r in term if not (r.get("cheapestFalsifier") or "").strip())
    if empty_f:
        raise SystemExit(f"{empty_f} terminal residuals lack cheapestFalsifier")

    # residual state partition
    states = Counter(r.get("campaignState") for r in residuals)
    if states.get("TERMINAL_PADDING") != 5012:
        raise SystemExit(states)
    if states.get("OPEN_EXECUTED_RESIDUAL") != 108:
        raise SystemExit(f"executed residual count drifted: {states}")
    if states.get("OPEN_DARK_RESIDUAL") != 997:
        raise SystemExit(f"open dark residual count drifted: {states}")

    result = {
        "status": "CAMPAIGN_VERIFIED",
        "generation": 11,
        "counts": ready.get("counts"),
        "residualStates": dict(states),
        "parentVerified": True,
        "formalPackSha256": _sha_file(formal_pack),
        "readySha256": _sha_file(campaign / "campaign.ready.json"),
    }
    print("CAMPAIGN_VERIFIED", json.dumps(result["counts"]))
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build generation 11 from Gen10 + formal pack")
    b.add_argument("--parent", type=Path, default=PARENT_GEN10)
    b.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)

    v = sub.add_parser("verify", help="verify generation 11 residual-terminal campaign")
    v.add_argument("--campaign", type=Path, default=DEFAULT_OUT)
    v.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    v.add_argument("--parent", type=Path, default=PARENT_GEN10)

    args = p.parse_args(argv)
    if args.cmd == "build":
        receipt = build_generation(
            parent=args.parent, formal_pack=args.formal_pack, out=args.out
        )
        print(json.dumps(receipt, indent=2))
        print("RESIDUAL_TERMINAL_GENERATION_APPLIED")
        return 0
    if args.cmd == "verify":
        verify_generation(args.campaign, args.formal_pack, args.parent)
        print("RESIDUAL_TERMINAL_GENERATION_VERIFIED")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
