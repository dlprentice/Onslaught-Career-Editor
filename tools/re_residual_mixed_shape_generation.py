#!/usr/bin/env python3
"""Generation-12 residual-terminal MIXED-shape bulk advance.

Parent: Generation 11 residual-terminal padding bulk (unmutated).
Advance: apply residual-mixed-shape formal pack proofs by:
  - setting residual TERMINAL_DATA or TERMINAL_BOUNDED_AMBIGUITY fields
  - closing linked residual questions as CLOSED_SURVIVED
  - aligning residual contracts to matching terminal states + refuter SURVIVED
  - recording bulk adjudications / supersessions with evidence hashes

Does not invent function names. Does not claim REBUILD_READY.
Does not mutate Generation 10 or Generation 11 in place.
Does not reinterpret schema-v3/v4 call-context evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.campaign.v5"
ADVANCE_KIND = "RESIDUAL_TERMINAL_MIXED_SHAPE_BULK"
ADVANCE_SCHEMA = "bea.re.residual-terminal-mixed-shape-bulk-advance.v1"
OVERLAY_SCHEMA = "bea.re.residual-terminal-mixed-shape-formal.v1"
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
PARENT_GEN11 = Path(
    "local-lab/residual-terminal-generation11-padding-xrefclean-20260805-v1/"
    "generation-11-residual-terminal-padding"
)
PARENT_GEN10 = Path(
    "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
    "generation-10-ttd-call-context-observation-v2"
)
DEFAULT_OUT = Path(
    "local-lab/residual-terminal-generation12-mixed-shape-20260805-v1/"
    "generation-12-residual-terminal-mixed-shape"
)
DEFAULT_PACK = Path(
    "local-lab/residual-mixed-shape-formal-pack-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_PAD_PACK = Path(
    "local-lab/residual-terminal-formal-pack-padding-xrefclean-20260805-v1/FORMAL-PACK.json"
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

ALLOWED_TERMINAL = {
    "TERMINAL_DATA",
    "TERMINAL_BOUNDED_AMBIGUITY",
    "TERMINAL_PADDING",  # not expected from MIXED pack but tolerated if proposed
}

DEFAULT_FALSIFIER = (
    "PE byte change in span; failed kind re-check; inbound code reference proving "
    "non-terminal semantics; or residual membership of a named function body"
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


def _split_qids(raw: str) -> list[str]:
    if not raw:
        return []
    # campaign uses ';'; formal pack may carry single ids or ';' joins
    parts: list[str] = []
    for chunk in raw.replace(",", ";").split(";"):
        q = chunk.strip()
        if q:
            parts.append(q)
    return parts


def _uncertainty_for(terminal_state: str, kind: str) -> str:
    if terminal_state == "TERMINAL_DATA":
        return (
            f"Shape-terminal DATA ({kind}); not a behavior contract or free CALL entry; "
            "no REBUILD_READY claim."
        )
    if terminal_state == "TERMINAL_BOUNDED_AMBIGUITY":
        return (
            f"Shape-terminal bounded ambiguity ({kind}); static decode envelope only; "
            "not entry proof, not REBUILD_READY."
        )
    return f"Shape-terminal {terminal_state} ({kind}); no REBUILD_READY claim."


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
    if int(pack.get("n_hard_mismatches", pack.get("n_mismatches", 1))) != 0:
        raise SystemExit("formal pack has hard mismatches")
    if pack.get("advance_kind_proposed") != "RESIDUAL_TERMINAL_MIXED_SHAPE_BULK.v1":
        raise SystemExit(
            f"unexpected advance_kind_proposed {pack.get('advance_kind_proposed')}"
        )
    proofs = pack["proofs"]
    if not proofs:
        raise SystemExit("formal pack has zero proofs")
    n_proofs = len(proofs)
    n_need_q = sum(
        1 for p in proofs if p.get("proposed", {}).get("requiresQuestionSupersession")
    )

    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(parent_ready.get("generation", -1)) != 11:
        raise SystemExit(
            f"parent must be generation 11 residual-terminal padding, got "
            f"{parent_ready.get('generation')}"
        )
    parent_advance = parent_ready.get("advance") or {}
    if parent_advance.get("kind") != "RESIDUAL_TERMINAL_PADDING_BULK":
        raise SystemExit(
            f"parent advance kind must be RESIDUAL_TERMINAL_PADDING_BULK, got "
            f"{parent_advance.get('kind')}"
        )

    residuals = _read_tsv(parent / "campaign-residuals.tsv")
    questions = _read_tsv(parent / "campaign-questions.tsv")
    contracts = _read_tsv(parent / "campaign-contracts.tsv")
    adjudications = _read_tsv(parent / "campaign-adjudications.tsv")
    supersessions = _read_tsv(parent / "campaign-supersessions.tsv")
    functions = _read_tsv(parent / "campaign-functions.tsv")
    scenarios = _read_tsv(parent / "campaign-scenarios.tsv")
    levers = _read_tsv(parent / "campaign-levers.tsv")

    if len(functions) != 8124 or len(residuals) != 6117:
        raise SystemExit("parent cardinality drifted from Gen10/Gen11")

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_entity = {c["entityKey"]: c for c in contracts}
    q_by_id = {q["questionId"]: q for q in questions}

    pack_sha = _sha_file(formal_pack)
    evidence_root = formal_pack.resolve().parent
    summary_path = evidence_root / "SUMMARY.json"
    evidence_refs_common = [
        f"{formal_pack.resolve()}#sha256={pack_sha}",
    ]
    if summary_path.is_file():
        evidence_refs_common.append(
            f"{summary_path.resolve()}#sha256={_sha_file(summary_path)}"
        )

    closed_qids: list[str] = []
    updated_entities: list[str] = []
    skipped_already = 0
    missing = 0
    term_data_added = 0
    term_ambig_added = 0

    for proof in proofs:
        proposed = proof.get("proposed") or {}
        terminal_state = proposed.get("terminalState") or ""
        campaign_state = proposed.get("campaignState") or terminal_state
        classification = proposed.get("classification") or ""
        verdict = proposed.get("classificationVerdict") or "FORMAL_STATIC_PROOF_SURVIVED"
        byte_pattern = proposed.get("bytePattern") or ""
        contract_state = proposed.get("contractState") or terminal_state
        falsifier = proposed.get("cheapestFalsifier") or DEFAULT_FALSIFIER
        shape_kind = proposed.get("shapeKind") or proof.get("kind") or ""

        if terminal_state not in ALLOWED_TERMINAL:
            raise SystemExit(
                f"proof {proof.get('startVa')} has disallowed terminalState {terminal_state}"
            )
        if not proposed.get("requiresQuestionSupersession", False):
            # pack currently has all require supersession; refuse silent already-clean
            # only if questions empty on residual
            pass

        start = proof["startVa"].lower()
        residual = res_by_start.get(start)
        if residual is None:
            missing += 1
            continue

        # Preserve Gen11 padding terminals; skip if already terminalized identically
        existing = residual.get("campaignState") or ""
        if existing in {
            "TERMINAL_PADDING",
            "TERMINAL_DATA",
            "TERMINAL_BOUNDED_AMBIGUITY",
            "TERMINAL_REBUILD_READY",
        }:
            if existing == campaign_state:
                skipped_already += 1
                continue
            raise SystemExit(
                f"residual {proof['startVa']} already terminal as {existing}; "
                f"refusing overwrite with {campaign_state}"
            )
        if existing != "OPEN_DARK_RESIDUAL":
            raise SystemExit(
                f"residual {proof['startVa']} expected OPEN_DARK_RESIDUAL, got {existing}"
            )

        ek = residual["entityKey"]
        qids = _split_qids(residual.get("questionIds") or "")
        # prefer residual-linked qids; fall back to pack proof qids
        if not qids:
            qids = _split_qids(proof.get("questionIds") or "")
        if proposed.get("requiresQuestionSupersession") and not qids:
            raise SystemExit(f"proof {proof['startVa']} requires supersession but has no qids")

        residual["classification"] = classification
        residual["classificationVerdict"] = verdict
        residual["terminalState"] = terminal_state
        residual["campaignState"] = campaign_state
        residual["bytePattern"] = byte_pattern
        residual["lever"] = "NONE"
        residual["cheapestFalsifier"] = falsifier
        residual["questionIds"] = ""
        residual["lastMeasurementDate"] = measured_at[:10]
        updated_entities.append(ek)
        if terminal_state == "TERMINAL_DATA":
            term_data_added += 1
        elif terminal_state == "TERMINAL_BOUNDED_AMBIGUITY":
            term_ambig_added += 1

        contract = con_by_entity.get(ek)
        if contract is None:
            raise SystemExit(f"missing contract for {ek}")
        if contract.get("entityKind") != "TEXT_RESIDUAL":
            raise SystemExit(f"contract entityKind not TEXT_RESIDUAL for {ek}")
        contract["contractState"] = contract_state
        contract["semanticGrade"] = "C0_OPAQUE"
        contract["authorVerdict"] = "STATIC_FORMAL_PROOF"
        contract["runtimeVerdict"] = "UNSCORED"
        contract["refuterVerdict"] = "SURVIVED"
        contract["questionIds"] = ""
        contract["evidenceRefs"] = ";".join(
            evidence_refs_common
            + [f"pe-shape#{shape_kind}#sha256={proof['peBytesSha256']}"]
        )
        contract["cheapestFalsifier"] = falsifier
        contract["rebuildOwner"] = "UNASSIGNED"
        contract["rebuildImplementation"] = "UNMAPPED"
        contract["parityTests"] = "UNMAPPED"
        contract["rebuildState"] = "NOT_READY"
        contract["remainingUncertainty"] = _uncertainty_for(terminal_state, shape_kind)
        contract["lastMeasurementDate"] = measured_at[:10]

        for qid in qids:
            q = q_by_id.get(qid)
            if q is None:
                raise SystemExit(f"missing question {qid} for {proof['startVa']}")
            if q.get("state") == "CLOSED_SURVIVED" and q.get("lastOutcome") == "SURVIVED":
                # already closed — count once if we address it
                closed_qids.append(qid)
                continue
            q["state"] = "CLOSED_SURVIVED"
            q["lastOutcome"] = "SURVIVED"
            q["lastMeasurementDate"] = measured_at[:10]
            q["attemptCount"] = str(int(q.get("attemptCount") or "0") + 1)
            closed_qids.append(qid)

        adj_id = _short_id("A", f"residual-mixed-shape|{ek}|{proof['peBytesSha256']}")
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
                "terminalState": terminal_state,
                "successorQuestionIds": "",
                "remainingUncertainty": _uncertainty_for(terminal_state, shape_kind),
                "measuredAtUtc": measured_at,
            }
        )

        sup_id = _short_id("S", f"residual-mixed-shape|{ek}|{proof['peBytesSha256']}")
        supersessions.append(
            {
                "supersessionId": sup_id,
                "oldEntityKey": ek,
                "newEntityKey": ek,
                "kind": ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": f"pe-shape#{shape_kind}#sha256={proof['peBytesSha256']}",
                "measuredAtUtc": measured_at,
            }
        )

    if missing:
        raise SystemExit(f"{missing} formal-pack rows missing from parent residuals")
    if len(updated_entities) != n_proofs - skipped_already:
        # all proofs should update unless already terminal
        if skipped_already == 0 and len(updated_entities) != n_proofs:
            raise SystemExit(
                f"expected to update {n_proofs} residuals, updated {len(updated_entities)}"
            )
    if len(set(closed_qids)) != n_need_q:
        raise SystemExit(
            f"expected {n_need_q} unique closed questions, got {len(set(closed_qids))}"
        )
    if len(closed_qids) < n_need_q:
        raise SystemExit(f"expected >= {n_need_q} closed question events, got {len(closed_qids)}")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

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

    term_pad = sum(1 for r in residuals if r.get("campaignState") == "TERMINAL_PADDING")
    term_data = sum(1 for r in residuals if r.get("campaignState") == "TERMINAL_DATA")
    term_ambig = sum(
        1 for r in residuals if r.get("campaignState") == "TERMINAL_BOUNDED_AMBIGUITY"
    )
    open_dark = sum(1 for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL")
    open_exec = sum(
        1 for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
    )
    q_open = sum(1 for q in questions if q.get("state") == "OPEN")
    q_closed = sum(1 for q in questions if q.get("state") == "CLOSED_SURVIVED")

    parent_pad = int((parent_ready.get("counts") or {}).get("residualTerminalPadding") or 0)
    if term_pad != parent_pad:
        raise SystemExit(
            f"padding terminals drifted: parent {parent_pad} child {term_pad}"
        )

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
        "residualTerminalData": term_data,
        "residualTerminalBoundedAmbiguity": term_ambig,
        "residualOpenDark": open_dark,
        "residualOpenExecuted": open_exec,
        "questionsOpen": q_open,
        "questionsClosedSurvived": q_closed,
        "residualTerminalsAddedThisGeneration": len(updated_entities),
        "questionsClosedThisGeneration": len(set(closed_qids)),
        "terminalDataAddedThisGeneration": term_data_added,
        "terminalBoundedAmbiguityAddedThisGeneration": term_ambig_added,
    }

    # partition check
    terminal_total = term_pad + term_data + term_ambig
    if terminal_total + open_dark + open_exec != 6117:
        raise SystemExit(
            f"residual partition incomplete: pad={term_pad} data={term_data} "
            f"ambig={term_ambig} dark={open_dark} exec={open_exec}"
        )
    if open_exec != 108:
        raise SystemExit(f"executed residual count drifted: {open_exec}")

    ready = {
        "schema": SCHEMA,
        "reducer": {
            "id": "residual-terminal-mixed-shape-bulk-v1",
            "note": (
                "Generation 12 residual-terminal MIXED-shape bulk; "
                "verify via tools/re_residual_mixed_shape_generation.py verify"
            ),
        },
        "generatedAtUtc": measured_at,
        "generation": 12,
        "parentCampaign": {
            "path": str(parent.resolve()),
            "ready": _file_stamp(parent / "campaign.ready.json"),
            "generation": 11,
            "advanceKind": parent_advance.get("kind"),
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
                "residualTerminalDataAdded": term_data_added,
                "residualTerminalBoundedAmbiguityAdded": term_ambig_added,
                "residualTerminalsAdded": len(updated_entities),
                "questionsClosedSurvived": len(set(closed_qids)),
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
                "TERMINAL_DATA is shape/data-structure only; not a behavior contract.",
                "TERMINAL_BOUNDED_AMBIGUITY is static decode-envelope only; not CALL entry proof.",
                "REBUILD_READY not claimed.",
                "EXECUTED residuals unchanged.",
                "Gen11 TERMINAL_PADDING preserved.",
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

    receipt = {
        "schema": "bea.re.residual-mixed-shape-generation-receipt.v1",
        "status": "APPLIED",
        "generation": 12,
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


def _verify_parent_gen11(parent: Path, pad_pack: Path, gen10: Path) -> None:
    """Re-run Gen11 padding verify (shipped tool) as parent integrity gate."""
    script = Path("tools/re_residual_terminal_generation.py")
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(script),
            "verify",
            "--campaign",
            str(parent),
            "--formal-pack",
            str(pad_pack),
            "--parent",
            str(gen10),
        ],
        cwd=str(Path.cwd()),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={
            **{k: v for k, v in __import__("os").environ.items()},
            "BEA_REPO_ROOT": str(Path.cwd()),
        },
    )
    out = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode != 0 or "RESIDUAL_TERMINAL_GENERATION_VERIFIED" not in out:
        raise SystemExit(f"parent Gen11 verify failed:\n{out}")


def verify_generation(
    campaign: Path,
    formal_pack: Path,
    parent: Path,
    *,
    pad_pack: Path = DEFAULT_PAD_PACK,
    gen10: Path = PARENT_GEN10,
) -> dict:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation", -1)) != 12:
        raise SystemExit(f"expected generation 12, got {ready.get('generation')}")
    advance = ready.get("advance") or {}
    if advance.get("kind") != ADVANCE_KIND:
        raise SystemExit(f"unexpected advance kind {advance.get('kind')}")

    _verify_parent_gen11(parent, pad_pack, gen10)

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    questions = _read_tsv(campaign / "campaign-questions.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    pack = json.loads(formal_pack.read_text(encoding="utf-8"))

    if len(functions) != 8124 or len(residuals) != 6117:
        raise SystemExit("function/residual cardinality drifted")

    n_proofs = len(pack["proofs"])
    n_need_q = sum(
        1 for p in pack["proofs"] if p.get("proposed", {}).get("requiresQuestionSupersession")
    )

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_ek = {c["entityKey"]: c for c in contracts}
    q_by_id = {q["questionId"]: q for q in questions}

    for proof in pack["proofs"]:
        proposed = proof.get("proposed") or {}
        terminal_state = proposed.get("terminalState")
        classification = proposed.get("classification")
        r = res_by_start.get(proof["startVa"].lower())
        if r is None:
            raise SystemExit(f"missing residual {proof['startVa']}")
        if r.get("campaignState") != terminal_state:
            raise SystemExit(
                f"not terminal {proof['startVa']}: {r.get('campaignState')} != {terminal_state}"
            )
        if r.get("classification") != classification:
            raise SystemExit(f"classification {proof['startVa']}")
        if r.get("classificationVerdict") != "FORMAL_STATIC_PROOF_SURVIVED":
            raise SystemExit(f"verdict {proof['startVa']}")
        if (r.get("questionIds") or "").strip():
            raise SystemExit(f"residual still has questions {proof['startVa']}")
        if not (r.get("cheapestFalsifier") or "").strip():
            raise SystemExit(f"terminal residual lacks falsifier {proof['startVa']}")
        c = con_by_ek[r["entityKey"]]
        if c.get("contractState") != (proposed.get("contractState") or terminal_state):
            raise SystemExit(f"contract state {proof['startVa']}")
        if c.get("refuterVerdict") != "SURVIVED":
            raise SystemExit(f"contract refuter {proof['startVa']}")
        if (c.get("questionIds") or "").strip():
            raise SystemExit(f"contract questions {proof['startVa']}")
        if c.get("rebuildState") == "REBUILD_READY":
            raise SystemExit(f"REBUILD_READY leaked for {proof['startVa']}")

    closed = 0
    for proof in pack["proofs"]:
        for qid in _split_qids(proof.get("questionIds") or ""):
            q = q_by_id.get(qid)
            if q is None:
                raise SystemExit(f"missing question {qid}")
            if q.get("state") != "CLOSED_SURVIVED" or q.get("lastOutcome") != "SURVIVED":
                raise SystemExit(f"question not closed {qid}")
            closed += 1
    if closed != n_need_q:
        raise SystemExit(f"expected {n_need_q} closed pack questions, got {closed}")

    states = Counter(r.get("campaignState") for r in residuals)
    term_pad = states.get("TERMINAL_PADDING", 0)
    term_data = states.get("TERMINAL_DATA", 0)
    term_ambig = states.get("TERMINAL_BOUNDED_AMBIGUITY", 0)
    open_dark = states.get("OPEN_DARK_RESIDUAL", 0)
    open_exec = states.get("OPEN_EXECUTED_RESIDUAL", 0)

    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    parent_pad = int((parent_ready.get("counts") or {}).get("residualTerminalPadding") or 0)
    if term_pad != parent_pad:
        raise SystemExit(f"padding terminals drifted: {term_pad} vs parent {parent_pad}")
    if term_data + term_ambig < n_proofs:
        raise SystemExit(
            f"expected >= {n_proofs} MIXED terminals, got data={term_data} ambig={term_ambig}"
        )
    if open_exec != 108:
        raise SystemExit(f"executed residual count drifted: {open_exec}")
    if term_pad + term_data + term_ambig + open_dark + open_exec != 6117:
        raise SystemExit(f"residual partition incomplete: {dict(states)}")

    # ready counts agreement
    rc = ready.get("counts") or {}
    if int(rc.get("residualTerminalsAddedThisGeneration", -1)) != n_proofs:
        # allow if some skipped already terminal — pack expects all open
        if int(rc.get("residualTerminalsAddedThisGeneration", -1)) not in {n_proofs}:
            raise SystemExit(
                f"ready residualTerminalsAddedThisGeneration mismatch: "
                f"{rc.get('residualTerminalsAddedThisGeneration')} vs {n_proofs}"
            )

    result = {
        "status": "CAMPAIGN_VERIFIED",
        "generation": 12,
        "counts": ready.get("counts"),
        "residualStates": dict(states),
        "parentVerified": True,
        "formalPackSha256": _sha_file(formal_pack),
        "readySha256": _sha_file(campaign / "campaign.ready.json"),
        "nProofs": n_proofs,
        "nQuestionsClosed": closed,
    }
    print("CAMPAIGN_VERIFIED", json.dumps(result["counts"]))
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build generation 12 from Gen11 + MIXED formal pack")
    b.add_argument("--parent", type=Path, default=PARENT_GEN11)
    b.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)

    v = sub.add_parser("verify", help="verify generation 12 MIXED-shape residual-terminal campaign")
    v.add_argument("--campaign", type=Path, default=DEFAULT_OUT)
    v.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    v.add_argument("--parent", type=Path, default=PARENT_GEN11)
    v.add_argument("--pad-pack", type=Path, default=DEFAULT_PAD_PACK)
    v.add_argument("--gen10", type=Path, default=PARENT_GEN10)

    args = p.parse_args(argv)
    if args.cmd == "build":
        receipt = build_generation(
            parent=args.parent, formal_pack=args.formal_pack, out=args.out
        )
        print(json.dumps(receipt, indent=2))
        print("RESIDUAL_MIXED_SHAPE_GENERATION_APPLIED")
        return 0
    if args.cmd == "verify":
        verify_generation(
            args.campaign,
            args.formal_pack,
            args.parent,
            pad_pack=args.pad_pack,
            gen10=args.gen10,
        )
        print("RESIDUAL_MIXED_SHAPE_GENERATION_VERIFIED")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
