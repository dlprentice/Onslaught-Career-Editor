#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generation-31 residual-terminal SEH + segment-resolve bulk advance.

Parent: Generation 30 MSVC table-mix tip (unmutated).
Advance: apply SEH/segment-resolve formal pack (4 TERMINAL_BOUNDED_AMBIGUITY).

Does not invent function names or claim REBUILD_READY / CALL entry.
Does not mutate Gen10/Gen30 in place. Does not close police-reopened rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.campaign.v5"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_SEH_SEGMENT_RESOLVE"
ADVANCE_SCHEMA = "bea.re.residual-terminal-open-seh-segment-resolve-bulk-advance.v1"
OVERLAY_SCHEMA = "bea.re.open-residual-gen30-seh-segment-resolve-formal-pack.v1"
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_PROOFS = 4
EXPECTED_DARK = 4
EXPECTED_EXEC = 0
EXPECTED_AMBIG_ADDED = 4
EXPECTED_PAD = 5062
EXPECTED_DATA = 29
EXPECTED_AMBIG = 1000  # 996 + 4
EXPECTED_OPEN_DARK = 26  # 30 - 4
EXPECTED_OPEN_EXEC = 0

PARENT_GEN30 = Path(
    "local-lab/residual-terminal-generation30-msvc-table-mix-20260805-v1/"
    "generation-30-residual-terminal-msvc-table-mix"
)
DEFAULT_PACK = Path(
    "local-lab/open-residual-gen30-seh-segment-resolve-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_OUT = Path(
    "local-lab/residual-terminal-generation31-seh-segment-resolve-20260805-v1/"
    "generation-31-residual-terminal-seh-segment-resolve"
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

ALLOWED_TERMINAL = {"TERMINAL_BOUNDED_AMBIGUITY"}
ALLOWED_LANES = {
    "SEH_FILTER_STUB",
    "SEH_PLUS_EXACT_INSN",
    "SEH_PLUS_MULTI",
    "SEH_PLUS_ENVELOPE",
    "SEH_PLUS_BODY_CT",
    "MULTI_SEH_LEAD",
    "SEGMENT_RESOLVE",
}
DEFAULT_FALSIFIER = (
    "PE re-decode SEH/segment-resolve fails; residual membership of a named body; "
    "REBUILD_READY claim"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _short_id(prefix: str, material: str) -> str:
    return f"{prefix}-{hashlib.sha256(material.encode()).hexdigest()[:14]}"


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(
            handle, fieldnames=columns, delimiter="\t",
            lineterminator="\n", extrasaction="ignore",
        )
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


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
    return [c.strip() for c in raw.replace(",", ";").split(";") if c.strip()]


def _uncertainty(lane: str, shape: str) -> str:
    return (
        f"Shape-terminal ({shape}; lane={lane}); static SEH filter and/or "
        "segment-resolve compose only; not CALL entry; not REBUILD_READY."
    )


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
        raise SystemExit(f"formal pack not READY: {pack.get('status')}")
    if pack.get("specimen_sha256") != PRISTINE_SHA256:
        raise SystemExit("specimen mismatch in pack")
    if int(pack.get("n_hard_mismatches", 1)) != 0:
        raise SystemExit("pack hard mismatches")
    if pack.get("advance_kind_proposed") not in {
        ADVANCE_KIND + ".v1",
        "RESIDUAL_TERMINAL_OPEN_SEH_SEGMENT_RESOLVE.v1",
    }:
        raise SystemExit(f"unexpected advance_kind {pack.get('advance_kind_proposed')}")
    proofs = pack["proofs"]
    if len(proofs) != EXPECTED_PROOFS:
        raise SystemExit(f"proofs {len(proofs)} != {EXPECTED_PROOFS}")
    for p in proofs:
        term = (p.get("proposed") or {}).get("terminalState")
        if term not in ALLOWED_TERMINAL:
            raise SystemExit(f"bad terminal {term} at {p.get('startVa')}")
        if p.get("sourceState") != "OPEN_DARK_RESIDUAL":
            raise SystemExit(f"non-dark {p.get('startVa')}")
        lane = (p.get("proposed") or {}).get("recoveryLane") or p.get("recoveryLane")
        if lane not in ALLOWED_LANES:
            raise SystemExit(f"bad lane {lane}")

    n_need_q = sum(
        1 for p in proofs if p.get("proposed", {}).get("requiresQuestionSupersession")
    )
    if n_need_q != EXPECTED_PROOFS:
        raise SystemExit(f"need_q {n_need_q}")

    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(parent_ready.get("generation", -1)) != 30:
        raise SystemExit(f"parent must be Gen30, got {parent_ready.get('generation')}")
    parent_advance = parent_ready.get("advance") or {}
    if parent_advance.get("kind") != "RESIDUAL_TERMINAL_OPEN_MSVC_TABLE_MIX":
        raise SystemExit(f"parent advance {parent_advance.get('kind')}")

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
        raise SystemExit("cardinality drift")

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_entity = {c["entityKey"]: c for c in contracts}
    q_by_id = {q["questionId"]: q for q in questions}

    pack_sha = _sha_file(formal_pack)
    evidence_refs_common = [f"{formal_pack.resolve()}#sha256={pack_sha}"]

    closed_qids: list[str] = []
    updated: list[str] = []
    ambig_added = 0
    dark_closed = 0

    for proof in proofs:
        proposed = proof["proposed"]
        terminal_state = proposed["terminalState"]
        start = proof["startVa"].lower()
        residual = res_by_start.get(start)
        if residual is None:
            raise SystemExit(f"missing residual {proof['startVa']}")
        if residual.get("campaignState") != "OPEN_DARK_RESIDUAL":
            raise SystemExit(
                f"{proof['startVa']} expected OPEN_DARK_RESIDUAL got "
                f"{residual.get('campaignState')}"
            )
        dark_closed += 1
        ek = residual["entityKey"]
        if ek != proof.get("entityKey"):
            raise SystemExit(f"entityKey mismatch {proof['startVa']}")

        qids = _split_qids(residual.get("questionIds") or "") or _split_qids(
            proof.get("questionIds") or ""
        )
        if not qids:
            raise SystemExit(f"no qids {proof['startVa']}")

        shape_kind = proposed.get("shapeKind") or proof.get("subspanKinds") or ""
        lane = proposed.get("recoveryLane") or proof.get("recoveryLane") or ""
        residual["classification"] = proposed["classification"]
        residual["classificationVerdict"] = proposed["classificationVerdict"]
        residual["terminalState"] = terminal_state
        residual["campaignState"] = proposed["campaignState"]
        residual["bytePattern"] = proposed.get("bytePattern") or "MIXED_OR_CODE_LIKE_BYTES"
        residual["lever"] = "NONE"
        residual["cheapestFalsifier"] = (
            proposed.get("cheapestFalsifier") or DEFAULT_FALSIFIER
        )
        residual["questionIds"] = ""
        residual["lastMeasurementDate"] = measured_at[:10]
        updated.append(ek)
        ambig_added += 1

        contract = con_by_entity.get(ek)
        if contract is None or contract.get("entityKind") != "TEXT_RESIDUAL":
            raise SystemExit(f"bad contract {ek}")
        contract["contractState"] = proposed["contractState"]
        contract["semanticGrade"] = "C0_OPAQUE"
        contract["authorVerdict"] = proposed.get("classificationVerdict") or "STATIC_SEH_SEGMENT"
        contract["runtimeVerdict"] = "UNSCORED"
        contract["refuterVerdict"] = "SURVIVED"
        contract["questionIds"] = ""
        contract["evidenceRefs"] = ";".join(
            evidence_refs_common
            + [
                f"pe-shape#seh-segment#sha256={proof['peBytesSha256']}",
                f"shapeKind#{shape_kind}",
                f"recoveryLane#{lane}",
            ]
        )
        contract["cheapestFalsifier"] = residual["cheapestFalsifier"]
        contract["rebuildOwner"] = "UNASSIGNED"
        contract["rebuildImplementation"] = "UNMAPPED"
        contract["parityTests"] = "UNMAPPED"
        contract["rebuildState"] = "NOT_READY"
        contract["remainingUncertainty"] = _uncertainty(lane, shape_kind)
        contract["lastMeasurementDate"] = measured_at[:10]

        for qid in qids:
            q = q_by_id.get(qid)
            if q is None:
                raise SystemExit(f"missing question {qid}")
            if not (
                q.get("state") == "CLOSED_SURVIVED"
                and q.get("lastOutcome") == "SURVIVED"
            ):
                q["state"] = "CLOSED_SURVIVED"
                q["lastOutcome"] = "SURVIVED"
                q["lastMeasurementDate"] = measured_at[:10]
                q["attemptCount"] = str(int(q.get("attemptCount") or "0") + 1)
            closed_qids.append(qid)

        adjudications.append(
            {
                "adjudicationId": _short_id(
                    "A", f"ssr|{ek}|{proof['peBytesSha256']}"
                ),
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
                "remainingUncertainty": _uncertainty(lane, shape_kind),
                "measuredAtUtc": measured_at,
            }
        )
        supersessions.append(
            {
                "supersessionId": _short_id(
                    "S", f"ssr|{ek}|{proof['peBytesSha256']}"
                ),
                "oldEntityKey": ek,
                "newEntityKey": ek,
                "kind": ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": f"pe-shape#sha256={proof['peBytesSha256']};lane#{lane}",
                "measuredAtUtc": measured_at,
            }
        )

    if len(updated) != EXPECTED_PROOFS:
        raise SystemExit(f"updated {len(updated)}")
    if ambig_added != EXPECTED_AMBIG_ADDED:
        raise SystemExit(f"ambig {ambig_added}")
    if dark_closed != EXPECTED_DARK:
        raise SystemExit(f"dark closed {dark_closed}")
    if len(set(closed_qids)) != EXPECTED_PROOFS:
        raise SystemExit(f"closed unique {len(set(closed_qids))}")

    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated during build")
    if _sha_file(parent / "campaign.ready.json") != parent_ready_sha:
        raise SystemExit("parent ready mutated during build")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    if (parent / "_reducer").is_dir():
        shutil.copytree(parent / "_reducer", out / "_reducer")

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

    pc = parent_ready.get("counts") or {}
    parent_pad = int(pc.get("residualTerminalPadding") or 0)
    parent_data = int(pc.get("residualTerminalData") or 0)
    parent_ambig = int(pc.get("residualTerminalBoundedAmbiguity") or 0)
    parent_dark = int(pc.get("residualOpenDark") or 0)
    parent_exec = int(pc.get("residualOpenExecuted") or 0)

    if term_pad != parent_pad:
        raise SystemExit(f"pad drifted {term_pad}")
    if term_data != parent_data:
        raise SystemExit(f"data drifted {term_data}")
    if term_ambig != parent_ambig + EXPECTED_AMBIG_ADDED:
        raise SystemExit(f"ambig {term_ambig}")
    if open_dark != parent_dark - EXPECTED_DARK:
        raise SystemExit(f"dark {open_dark}")
    if open_exec != parent_exec:
        raise SystemExit(f"exec {open_exec}")
    if term_pad + term_data + term_ambig + open_dark + open_exec != 6117:
        raise SystemExit("partition incomplete")
    if (
        term_pad != EXPECTED_PAD
        or term_data != EXPECTED_DATA
        or term_ambig != EXPECTED_AMBIG
        or open_dark != EXPECTED_OPEN_DARK
        or open_exec != EXPECTED_OPEN_EXEC
    ):
        raise SystemExit(
            f"absolute partition "
            f"{term_pad}/{term_data}/{term_ambig}/{open_dark}/{open_exec}"
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
        "residualTerminalsAddedThisGeneration": len(updated),
        "questionsClosedThisGeneration": len(set(closed_qids)),
        "terminalPaddingAddedThisGeneration": 0,
        "terminalDataAddedThisGeneration": 0,
        "terminalBoundedAmbiguityAddedThisGeneration": ambig_added,
        "openDarkClosedThisGeneration": dark_closed,
        "openExecutedClosedThisGeneration": 0,
    }

    expected_adj = int(pc.get("adjudications") or 0) + EXPECTED_PROOFS
    expected_sup = int(pc.get("supersessions") or 0) + EXPECTED_PROOFS
    if counts["adjudications"] != expected_adj:
        raise SystemExit(f"adj {counts['adjudications']}")
    if counts["supersessions"] != expected_sup:
        raise SystemExit(f"sup {counts['supersessions']}")

    ready = {
        "schema": SCHEMA,
        "reducer": {
            "id": "residual-terminal-open-seh-segment-resolve-bulk-v1",
            "note": (
                "Generation 31 residual-terminal SEH + segment-resolve bulk; "
                "verify via tools/re_open_residual_gen31_seh_segment_resolve_generation.py verify"
            ),
        },
        "generatedAtUtc": measured_at,
        "generation": 31,
        "parentCampaign": {
            "path": str(parent.resolve()),
            "ready": _file_stamp(parent / "campaign.ready.json"),
            "generation": 30,
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
                "residualTerminalPaddingAdded": 0,
                "residualTerminalDataAdded": 0,
                "residualTerminalBoundedAmbiguityAdded": ambig_added,
                "residualTerminalsAdded": len(updated),
                "questionsClosedSurvived": len(set(closed_qids)),
                "openDarkClosed": dark_closed,
                "openExecutedClosed": 0,
            },
            "delta": {
                "namesChanged": 0,
                "writesProved": 0,
                "rebuildParityProved": 0,
                "ghidraMutated": False,
                "functionsChanged": 0,
                "residualsTerminalized": len(updated),
            },
            "semanticLimitations": [
                "SEH filter stubs are static MSVC exception-filter shape only.",
                "SEGMENT_RESOLVE re-resolves open subspans via table-mix/pad/multi.",
                "Police OFFSET_ENVELOPE reopens not closed.",
                "Not CALL entry; not REBUILD_READY; no invented function names.",
                "Gen30 parent unmutated; prior terminals preserved.",
                "26 OPEN_DARK + 0 OPEN_EXECUTED remain.",
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
        "schema": "bea.re.open-residual-gen31-seh-segment-resolve-generation-receipt.v1",
        "status": "APPLIED",
        "generation": 31,
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
    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated after child write")
    return receipt


def verify_generation(
    campaign: Path,
    formal_pack: Path,
    parent: Path,
    *,
    verify_parent: bool = True,
) -> dict:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation", -1)) != 31:
        raise SystemExit(f"expected Gen31, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != ADVANCE_KIND:
        raise SystemExit(f"bad advance {(ready.get('advance') or {}).get('kind')}")

    if verify_parent:
        parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
        if int(parent_ready.get("generation", -1)) != 30:
            raise SystemExit("parent not Gen30")
        parent_res = _read_tsv(parent / "campaign-residuals.tsv")
        pst = Counter(r.get("campaignState") for r in parent_res)
        if pst.get("OPEN_DARK_RESIDUAL") != 30:
            raise SystemExit(f"parent dark {pst.get('OPEN_DARK_RESIDUAL')}")

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    states = Counter(r.get("campaignState") for r in residuals)
    if len(residuals) != 6117:
        raise SystemExit("residuals")
    if states.get("TERMINAL_PADDING", 0) != EXPECTED_PAD:
        raise SystemExit(f"pad {states.get('TERMINAL_PADDING')}")
    if states.get("TERMINAL_DATA", 0) != EXPECTED_DATA:
        raise SystemExit(f"data {states.get('TERMINAL_DATA')}")
    if states.get("TERMINAL_BOUNDED_AMBIGUITY", 0) != EXPECTED_AMBIG:
        raise SystemExit(f"ambig {states.get('TERMINAL_BOUNDED_AMBIGUITY')}")
    if states.get("OPEN_DARK_RESIDUAL", 0) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"dark {states.get('OPEN_DARK_RESIDUAL')}")
    if states.get("OPEN_EXECUTED_RESIDUAL", 0) != EXPECTED_OPEN_EXEC:
        raise SystemExit(f"exec {states.get('OPEN_EXECUTED_RESIDUAL')}")

    pack = json.loads(formal_pack.read_text(encoding="utf-8"))
    if pack.get("n_proofs") != EXPECTED_PROOFS:
        raise SystemExit("pack proofs")
    parent_res_sha = _sha_file(parent / "campaign-residuals.tsv")
    child_parent_sha = (ready.get("parentCampaign") or {}).get("residualsSha256")
    if child_parent_sha != parent_res_sha:
        raise SystemExit("parent residuals sha drift")

    rc = ready.get("counts") or {}
    if int(rc.get("residualTerminalsAddedThisGeneration", -1)) != EXPECTED_PROOFS:
        raise SystemExit("added count")
    if int(rc.get("openDarkClosedThisGeneration", -1)) != EXPECTED_DARK:
        raise SystemExit("dark closed")

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    for proof in pack.get("proofs") or []:
        start = (proof.get("startVa") or "").lower()
        residual = res_by_start.get(start)
        if residual is None:
            raise SystemExit(f"pack proof missing residual {proof.get('startVa')}")
        if residual.get("entityKey") != proof.get("entityKey"):
            raise SystemExit(f"entityKey drift {proof.get('startVa')}")
        term = (proof.get("proposed") or {}).get("terminalState") or proof.get(
            "proposedTerminalState"
        )
        if residual.get("campaignState") != term:
            raise SystemExit(
                f"terminal drift {proof.get('startVa')}: "
                f"{residual.get('campaignState')} != {term}"
            )

    result = {
        "status": "CAMPAIGN_VERIFIED",
        "generation": 31,
        "counts": ready.get("counts"),
        "residualStates": dict(states),
        "parentVerified": verify_parent,
        "formalPackSha256": _sha_file(formal_pack),
        "readySha256": _sha_file(campaign / "campaign.ready.json"),
        "nProofs": EXPECTED_PROOFS,
        "packRowJoinVerified": True,
        "parentGen30Unmutated": True,
    }
    print(json.dumps(result, indent=2))
    print("CAMPAIGN_VERIFIED")
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply", help="Apply Gen31 SEH/segment-resolve advance")
    a.add_argument("--parent", type=Path, default=PARENT_GEN30)
    a.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    a.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify Gen31 campaign")
    v.add_argument("--campaign", type=Path, default=DEFAULT_OUT)
    v.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    v.add_argument("--parent", type=Path, default=PARENT_GEN30)
    v.add_argument("--skip-parent-verify", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "apply":
        receipt = build_generation(
            parent=args.parent, formal_pack=args.formal_pack, out=args.out
        )
        print(json.dumps(receipt, indent=2))
        print("GEN31_APPLIED")
        return 0
    if args.cmd == "verify":
        verify_generation(
            args.campaign,
            args.formal_pack,
            args.parent,
            verify_parent=not args.skip_parent_verify,
        )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
