#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generation-13 residual-terminal OPEN DARK pad/data bulk advance.

Parent: Generation 12 residual-terminal MIXED-shape (unmutated).
Advance: apply open-dark pad/data formal pack proofs by:
  - setting residual TERMINAL_PADDING or TERMINAL_DATA fields
  - closing linked residual questions as CLOSED_SURVIVED
  - aligning residual contracts to matching terminal states + refuter SURVIVED
  - recording bulk adjudications / supersessions with evidence hashes

Does not invent function names. Does not claim REBUILD_READY.
Does not mutate Generation 10, 11, or 12 in place.
Does not admit CODE envelopes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.campaign.v5"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_DARK_PAD_DATA"
ADVANCE_SCHEMA = "bea.re.residual-terminal-open-dark-pad-data-bulk-advance.v1"
OVERLAY_SCHEMA = "bea.re.open-dark-pad-data-formal-pack.v1"
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_PROOFS = 12
EXPECTED_PAD_ADDED = 10
EXPECTED_DATA_ADDED = 2

PARENT_GEN12 = Path(
    "local-lab/residual-terminal-generation12-mixed-shape-20260805-v1/"
    "generation-12-residual-terminal-mixed-shape"
)
PARENT_GEN11 = Path(
    "local-lab/residual-terminal-generation11-padding-xrefclean-20260805-v1/"
    "generation-11-residual-terminal-padding"
)
PARENT_GEN10 = Path(
    "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
    "generation-10-ttd-call-context-observation-v2"
)
DEFAULT_PACK = Path(
    "local-lab/open-dark-pad-data-formal-pack-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_MIXED_PACK = Path(
    "local-lab/residual-mixed-shape-formal-pack-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_PAD_PACK = Path(
    "local-lab/residual-terminal-formal-pack-padding-xrefclean-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_OUT = Path(
    "local-lab/residual-terminal-generation13-open-dark-pad-data-20260805-v1/"
    "generation-13-residual-terminal-open-dark-pad-data"
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

ALLOWED_TERMINAL = {"TERMINAL_PADDING", "TERMINAL_DATA"}
FORBIDDEN_KINDS = {
    "STATIC_CODE_DECODE_ENVELOPE",
    "CODE_LIKE_PARTIAL",
    "LARGE_MIXED_BLOB",
    "OPEN_CODE_FRAGMENT",
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
    parts: list[str] = []
    for chunk in raw.replace(",", ";").split(";"):
        q = chunk.strip()
        if q:
            parts.append(q)
    return parts


def _uncertainty_for(terminal_state: str, kind: str) -> str:
    if terminal_state == "TERMINAL_PADDING":
        return (
            f"Formal PE pad terminal ({kind}); pure 00/90/CC only; "
            "not a behavior contract; no REBUILD_READY claim."
        )
    if terminal_state == "TERMINAL_DATA":
        return (
            f"Shape-terminal DATA ({kind}); not a live jump-table runtime proof; "
            "not a behavior contract; no REBUILD_READY claim."
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
    if int(pack.get("n_hard_mismatches", 1)) != 0:
        raise SystemExit("formal pack has hard mismatches")
    if pack.get("advance_kind_proposed") != "RESIDUAL_TERMINAL_OPEN_DARK_PAD_DATA.v1":
        raise SystemExit(
            f"unexpected advance_kind_proposed {pack.get('advance_kind_proposed')}"
        )
    if int(pack.get("n_proofs") or 0) != EXPECTED_PROOFS:
        raise SystemExit(f"expected {EXPECTED_PROOFS} proofs, got {pack.get('n_proofs')}")
    proofs = pack["proofs"]
    if len(proofs) != EXPECTED_PROOFS:
        raise SystemExit(f"proofs len {len(proofs)} != {EXPECTED_PROOFS}")
    for p in proofs:
        kind = p.get("kind") or ""
        if kind in FORBIDDEN_KINDS:
            raise SystemExit(f"forbidden kind in pack: {kind} at {p.get('startVa')}")
        term = (p.get("proposed") or {}).get("terminalState")
        if term not in ALLOWED_TERMINAL:
            raise SystemExit(f"disallowed terminal {term} at {p.get('startVa')}")

    n_proofs = len(proofs)
    n_need_q = sum(
        1 for p in proofs if p.get("proposed", {}).get("requiresQuestionSupersession")
    )
    if n_need_q != EXPECTED_PROOFS:
        raise SystemExit(f"expected all {EXPECTED_PROOFS} proofs need supersession, got {n_need_q}")

    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(parent_ready.get("generation", -1)) != 12:
        raise SystemExit(
            f"parent must be generation 12 residual-terminal mixed-shape, got "
            f"{parent_ready.get('generation')}"
        )
    parent_advance = parent_ready.get("advance") or {}
    if parent_advance.get("kind") != "RESIDUAL_TERMINAL_MIXED_SHAPE_BULK":
        raise SystemExit(
            f"parent advance kind must be RESIDUAL_TERMINAL_MIXED_SHAPE_BULK, got "
            f"{parent_advance.get('kind')}"
        )

    parent_res_sha = _sha_file(parent / "campaign-residuals.tsv")
    parent_fn_sha = _sha_file(parent / "campaign-functions.tsv")
    parent_ready_sha = _sha_file(parent / "campaign.ready.json")

    residuals = _read_tsv(parent / "campaign-residuals.tsv")
    questions = _read_tsv(parent / "campaign-questions.tsv")
    contracts = _read_tsv(parent / "campaign-contracts.tsv")
    adjudications = _read_tsv(parent / "campaign-adjudications.tsv")
    supersessions = _read_tsv(parent / "campaign-supersessions.tsv")
    functions = _read_tsv(parent / "campaign-functions.tsv")
    scenarios = _read_tsv(parent / "campaign-scenarios.tsv")
    levers = _read_tsv(parent / "campaign-levers.tsv")

    if len(functions) != 8124 or len(residuals) != 6117:
        raise SystemExit("parent cardinality drifted")

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_entity = {c["entityKey"]: c for c in contracts}
    q_by_id = {q["questionId"]: q for q in questions}

    pack_sha = _sha_file(formal_pack)
    evidence_root = formal_pack.resolve().parent
    summary_path = evidence_root / "SUMMARY.json"
    evidence_refs_common = [f"{formal_pack.resolve()}#sha256={pack_sha}"]
    if summary_path.is_file():
        evidence_refs_common.append(
            f"{summary_path.resolve()}#sha256={_sha_file(summary_path)}"
        )

    closed_qids: list[str] = []
    updated_entities: list[str] = []
    term_pad_added = 0
    term_data_added = 0

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
                f"proof {proof.get('startVa')} disallowed terminalState {terminal_state}"
            )
        if shape_kind in FORBIDDEN_KINDS:
            raise SystemExit(f"forbidden shapeKind {shape_kind}")

        start = proof["startVa"].lower()
        residual = res_by_start.get(start)
        if residual is None:
            raise SystemExit(f"missing residual {proof['startVa']}")

        existing = residual.get("campaignState") or ""
        if existing != "OPEN_DARK_RESIDUAL":
            raise SystemExit(
                f"residual {proof['startVa']} expected OPEN_DARK_RESIDUAL, got {existing}"
            )
        if residual.get("observationState") == "EXECUTED":
            raise SystemExit(f"refusing EXECUTED residual {proof['startVa']}")

        ek = residual["entityKey"]
        if ek != proof.get("entityKey"):
            raise SystemExit(
                f"entityKey mismatch {proof['startVa']}: "
                f"campaign={ek} pack={proof.get('entityKey')}"
            )

        qids = _split_qids(residual.get("questionIds") or "")
        if not qids:
            qids = _split_qids(proof.get("questionIds") or "")
        if not qids:
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
        if terminal_state == "TERMINAL_PADDING":
            term_pad_added += 1
        elif terminal_state == "TERMINAL_DATA":
            term_data_added += 1

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
                closed_qids.append(qid)
                continue
            q["state"] = "CLOSED_SURVIVED"
            q["lastOutcome"] = "SURVIVED"
            q["lastMeasurementDate"] = measured_at[:10]
            q["attemptCount"] = str(int(q.get("attemptCount") or "0") + 1)
            closed_qids.append(qid)

        adj_id = _short_id("A", f"open-dark-pad-data|{ek}|{proof['peBytesSha256']}")
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

        sup_id = _short_id("S", f"open-dark-pad-data|{ek}|{proof['peBytesSha256']}")
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

    if len(updated_entities) != n_proofs:
        raise SystemExit(f"expected to update {n_proofs} residuals, updated {len(updated_entities)}")
    if term_pad_added != EXPECTED_PAD_ADDED:
        raise SystemExit(f"pad added {term_pad_added} != {EXPECTED_PAD_ADDED}")
    if term_data_added != EXPECTED_DATA_ADDED:
        raise SystemExit(f"data added {term_data_added} != {EXPECTED_DATA_ADDED}")
    if len(set(closed_qids)) != n_need_q:
        raise SystemExit(
            f"expected {n_need_q} unique closed questions, got {len(set(closed_qids))}"
        )

    # Parent Gen12 must still be byte-identical after read (we only mutate copies)
    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated during build")
    if _sha_file(parent / "campaign-functions.tsv") != parent_fn_sha:
        raise SystemExit("parent functions mutated during build")
    if _sha_file(parent / "campaign.ready.json") != parent_ready_sha:
        raise SystemExit("parent ready mutated during build")

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

    parent_counts = parent_ready.get("counts") or {}
    parent_pad = int(parent_counts.get("residualTerminalPadding") or 0)
    parent_data = int(parent_counts.get("residualTerminalData") or 0)
    parent_ambig = int(parent_counts.get("residualTerminalBoundedAmbiguity") or 0)
    parent_dark = int(parent_counts.get("residualOpenDark") or 0)
    parent_adj = int(parent_counts.get("adjudications") or len(adjudications) - n_proofs)
    parent_sup = int(parent_counts.get("supersessions") or len(supersessions) - n_proofs)

    if term_pad != parent_pad + EXPECTED_PAD_ADDED:
        raise SystemExit(
            f"padding terminals: got {term_pad}, expected parent {parent_pad}+{EXPECTED_PAD_ADDED}"
        )
    if term_data != parent_data + EXPECTED_DATA_ADDED:
        raise SystemExit(
            f"data terminals: got {term_data}, expected parent {parent_data}+{EXPECTED_DATA_ADDED}"
        )
    if term_ambig != parent_ambig:
        raise SystemExit(f"bounded ambiguity drifted: {term_ambig} vs parent {parent_ambig}")
    if open_dark != parent_dark - n_proofs:
        raise SystemExit(
            f"open dark: got {open_dark}, expected parent {parent_dark}-{n_proofs}"
        )
    if open_exec != 108:
        raise SystemExit(f"executed residual count drifted: {open_exec}")
    if term_pad + term_data + term_ambig + open_dark + open_exec != 6117:
        raise SystemExit(
            f"residual partition incomplete: pad={term_pad} data={term_data} "
            f"ambig={term_ambig} dark={open_dark} exec={open_exec}"
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
        "terminalPaddingAddedThisGeneration": term_pad_added,
        "terminalDataAddedThisGeneration": term_data_added,
    }

    if counts["adjudications"] != parent_adj + n_proofs and parent_adj > 0:
        # soft check — parent_counts adjudications should match
        expected_adj = int(parent_counts.get("adjudications") or 0) + n_proofs
        if counts["adjudications"] != expected_adj:
            raise SystemExit(
                f"adjudications {counts['adjudications']} != expected {expected_adj}"
            )
    expected_sup = int(parent_counts.get("supersessions") or 0) + n_proofs
    if counts["supersessions"] != expected_sup:
        raise SystemExit(
            f"supersessions {counts['supersessions']} != expected {expected_sup}"
        )

    ready = {
        "schema": SCHEMA,
        "reducer": {
            "id": "residual-terminal-open-dark-pad-data-bulk-v1",
            "note": (
                "Generation 13 residual-terminal OPEN DARK pad/data bulk; "
                "verify via tools/re_open_dark_pad_data_generation.py verify"
            ),
        },
        "generatedAtUtc": measured_at,
        "generation": 13,
        "parentCampaign": {
            "path": str(parent.resolve()),
            "ready": _file_stamp(parent / "campaign.ready.json"),
            "generation": 12,
            "advanceKind": parent_advance.get("kind"),
            "residualsSha256": parent_res_sha,
            "functionsSha256": parent_fn_sha,
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
                "residualTerminalPaddingAdded": term_pad_added,
                "residualTerminalDataAdded": term_data_added,
                "residualTerminalsAdded": len(updated_entities),
                "questionsClosedSurvived": len(set(closed_qids)),
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
                "TERMINAL_PADDING is pure PE pad only; not behavior.",
                "TERMINAL_DATA is shape/data-structure only; not live jump-table proof.",
                "CODE envelopes excluded by construction.",
                "REBUILD_READY not claimed.",
                "EXECUTED residuals unchanged.",
                "Gen12 MIXED terminals preserved.",
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
        "schema": "bea.re.open-dark-pad-data-generation-receipt.v1",
        "status": "APPLIED",
        "generation": 13,
        "out": str(out.resolve()),
        "parent": str(parent.resolve()),
        "formalPackSha256": pack_sha,
        "parentResidualsSha256": parent_res_sha,
        "counts": counts,
        "readySha256": _sha_file(out / "campaign.ready.json"),
        "measuredAtUtc": measured_at,
    }
    (out / "generation-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )

    # Parent immutability re-check after write
    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated after child write")
    if _sha_file(parent / "campaign.ready.json") != parent_ready_sha:
        raise SystemExit("parent ready mutated after child write")

    return receipt


def _verify_parent_gen12(
    parent: Path,
    mixed_pack: Path,
    pad_pack: Path,
    gen11: Path,
    gen10: Path,
) -> None:
    script = Path("tools/re_residual_mixed_shape_generation.py")
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(script),
            "verify",
            "--campaign",
            str(parent),
            "--formal-pack",
            str(mixed_pack),
            "--parent",
            str(gen11),
            "--pad-pack",
            str(pad_pack),
            "--gen10",
            str(gen10),
        ],
        cwd=str(Path.cwd()),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**dict(os.environ), "BEA_REPO_ROOT": str(Path.cwd())},
    )
    out = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode != 0 or "RESIDUAL_MIXED_SHAPE_GENERATION_VERIFIED" not in out:
        raise SystemExit(f"parent Gen12 verify failed:\n{out}")


def verify_generation(
    campaign: Path,
    formal_pack: Path,
    parent: Path,
    *,
    mixed_pack: Path = DEFAULT_MIXED_PACK,
    pad_pack: Path = DEFAULT_PAD_PACK,
    gen11: Path = PARENT_GEN11,
    gen10: Path = PARENT_GEN10,
    verify_parent: bool = True,
) -> dict:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation", -1)) != 13:
        raise SystemExit(f"expected generation 13, got {ready.get('generation')}")
    advance = ready.get("advance") or {}
    if advance.get("kind") != ADVANCE_KIND:
        raise SystemExit(f"unexpected advance kind {advance.get('kind')}")

    if verify_parent:
        _verify_parent_gen12(parent, mixed_pack, pad_pack, gen11, gen10)

    # Parent still unmutated vs receipt stamps
    parent_stamp = (ready.get("parentCampaign") or {}).get("residualsSha256")
    if parent_stamp:
        live = _sha_file(parent / "campaign-residuals.tsv")
        if live != parent_stamp:
            raise SystemExit(
                f"parent Gen12 residuals mutated after Gen13 build: "
                f"ready={parent_stamp} live={live}"
            )

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    questions = _read_tsv(campaign / "campaign-questions.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    pack = json.loads(formal_pack.read_text(encoding="utf-8"))

    if len(functions) != 8124 or len(residuals) != 6117:
        raise SystemExit("function/residual cardinality drifted")
    if len(pack["proofs"]) != EXPECTED_PROOFS:
        raise SystemExit(f"pack proofs {len(pack['proofs'])} != {EXPECTED_PROOFS}")

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_ek = {c["entityKey"]: c for c in contracts}
    q_by_id = {q["questionId"]: q for q in questions}

    for proof in pack["proofs"]:
        proposed = proof.get("proposed") or {}
        terminal_state = proposed.get("terminalState")
        classification = proposed.get("classification")
        kind = proof.get("kind") or ""
        if kind in FORBIDDEN_KINDS:
            raise SystemExit(f"forbidden kind in verified pack: {kind}")
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
    if closed != EXPECTED_PROOFS:
        raise SystemExit(f"expected {EXPECTED_PROOFS} closed pack questions, got {closed}")

    states = Counter(r.get("campaignState") for r in residuals)
    term_pad = states.get("TERMINAL_PADDING", 0)
    term_data = states.get("TERMINAL_DATA", 0)
    term_ambig = states.get("TERMINAL_BOUNDED_AMBIGUITY", 0)
    open_dark = states.get("OPEN_DARK_RESIDUAL", 0)
    open_exec = states.get("OPEN_EXECUTED_RESIDUAL", 0)

    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    parent_pad = int((parent_ready.get("counts") or {}).get("residualTerminalPadding") or 0)
    parent_data = int((parent_ready.get("counts") or {}).get("residualTerminalData") or 0)
    parent_ambig = int(
        (parent_ready.get("counts") or {}).get("residualTerminalBoundedAmbiguity") or 0
    )
    parent_dark = int((parent_ready.get("counts") or {}).get("residualOpenDark") or 0)

    if term_pad != parent_pad + EXPECTED_PAD_ADDED:
        raise SystemExit(f"padding terminals {term_pad} != parent {parent_pad}+10")
    if term_data != parent_data + EXPECTED_DATA_ADDED:
        raise SystemExit(f"data terminals {term_data} != parent {parent_data}+2")
    if term_ambig != parent_ambig:
        raise SystemExit(f"ambig terminals drifted {term_ambig} vs {parent_ambig}")
    if open_dark != parent_dark - EXPECTED_PROOFS:
        raise SystemExit(f"open dark {open_dark} != parent {parent_dark}-12")
    if open_exec != 108:
        raise SystemExit(f"executed residual count drifted: {open_exec}")
    if term_pad + term_data + term_ambig + open_dark + open_exec != 6117:
        raise SystemExit(f"residual partition incomplete: {dict(states)}")

    rc = ready.get("counts") or {}
    if int(rc.get("residualTerminalsAddedThisGeneration", -1)) != EXPECTED_PROOFS:
        raise SystemExit(
            f"ready residualTerminalsAddedThisGeneration "
            f"{rc.get('residualTerminalsAddedThisGeneration')} != {EXPECTED_PROOFS}"
        )
    if int(rc.get("questionsClosedThisGeneration", -1)) != EXPECTED_PROOFS:
        raise SystemExit(
            f"ready questionsClosedThisGeneration "
            f"{rc.get('questionsClosedThisGeneration')} != {EXPECTED_PROOFS}"
        )

    result = {
        "status": "CAMPAIGN_VERIFIED",
        "generation": 13,
        "counts": ready.get("counts"),
        "residualStates": dict(states),
        "parentVerified": verify_parent,
        "formalPackSha256": _sha_file(formal_pack),
        "readySha256": _sha_file(campaign / "campaign.ready.json"),
        "nProofs": EXPECTED_PROOFS,
        "nQuestionsClosed": closed,
        "parentGen12Unmutated": True,
    }
    print("CAMPAIGN_VERIFIED", json.dumps(result["counts"]))
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build generation 13 from Gen12 + pad/data formal pack")
    b.add_argument("--parent", type=Path, default=PARENT_GEN12)
    b.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)

    v = sub.add_parser("verify", help="verify generation 13 pad/data residual-terminal campaign")
    v.add_argument("--campaign", type=Path, default=DEFAULT_OUT)
    v.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    v.add_argument("--parent", type=Path, default=PARENT_GEN12)
    v.add_argument("--mixed-pack", type=Path, default=DEFAULT_MIXED_PACK)
    v.add_argument("--pad-pack", type=Path, default=DEFAULT_PAD_PACK)
    v.add_argument("--gen11", type=Path, default=PARENT_GEN11)
    v.add_argument("--gen10", type=Path, default=PARENT_GEN10)
    v.add_argument(
        "--skip-parent-verify",
        action="store_true",
        help="skip nested Gen12 verify (faster; still checks parent residual hash)",
    )

    args = p.parse_args(argv)
    if args.cmd == "build":
        receipt = build_generation(
            parent=args.parent, formal_pack=args.formal_pack, out=args.out
        )
        print(json.dumps(receipt, indent=2))
        print("OPEN_DARK_PAD_DATA_GENERATION_APPLIED")
        return 0
    if args.cmd == "verify":
        verify_generation(
            args.campaign,
            args.formal_pack,
            args.parent,
            mixed_pack=args.mixed_pack,
            pad_pack=args.pad_pack,
            gen11=args.gen11,
            gen10=args.gen10,
            verify_parent=not args.skip_parent_verify,
        )
        print("OPEN_DARK_PAD_DATA_GENERATION_VERIFIED")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
