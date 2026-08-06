#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generation-21 residual-terminal code+pad / soft multi-unit bulk advance.

Parent: Generation 20 residual-terminal multi-unit (unmutated).
Advance: apply code-pad formal pack (6 TERMINAL_BOUNDED_AMBIGUITY:
5 OPEN_DARK envelope/multi+pad + 1 OPEN_EXECUTED soft multi-unit) with
question supersession.

Does not invent function names or claim REBUILD_READY.
Does not mutate Gen10/Gen20 in place.
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
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_CODE_PAD"
ADVANCE_SCHEMA = "bea.re.residual-terminal-open-code-pad-bulk-advance.v1"
OVERLAY_SCHEMA = "bea.re.open-residual-gen20-code-pad-formal-pack.v1"
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_PROOFS = 6
EXPECTED_DARK = 5
EXPECTED_EXEC = 1
EXPECTED_AMBIG_ADDED = 6

PARENT_GEN20 = Path(
    "local-lab/residual-terminal-generation20-multi-unit-20260805-v1/"
    "generation-20-residual-terminal-multi-unit"
)
DEFAULT_PACK = Path(
    "local-lab/open-residual-gen20-code-pad-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_OUT = Path(
    "local-lab/residual-terminal-generation21-code-pad-20260805-v1/"
    "generation-21-residual-terminal-code-pad"
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
DEFAULT_FALSIFIER = (
    "PE byte change; pad strip + re-decode fails; soft multi-unit loses ret-first "
    "unit; residual membership of a named body; REBUILD_READY claim"
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


def _uncertainty(lane: str, shape: str, src: str) -> str:
    return (
        f"Shape-terminal bounded ambiguity ({shape}; lane={lane}; src={src}); "
        "static code+pad or EXECUTED soft multi-unit only; not full contract; "
        "not REBUILD_READY; no invented function name."
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
        "RESIDUAL_TERMINAL_OPEN_CODE_PAD.v1",
    }:
        raise SystemExit(f"unexpected advance_kind {pack.get('advance_kind_proposed')}")
    proofs = pack["proofs"]
    if len(proofs) != EXPECTED_PROOFS:
        raise SystemExit(f"proofs {len(proofs)} != {EXPECTED_PROOFS}")
    n_dark = sum(1 for p in proofs if p.get("sourceState") == "OPEN_DARK_RESIDUAL")
    n_exec = sum(1 for p in proofs if p.get("sourceState") == "OPEN_EXECUTED_RESIDUAL")
    if n_dark != EXPECTED_DARK or n_exec != EXPECTED_EXEC:
        raise SystemExit(f"source split {n_dark}/{n_exec}")
    for p in proofs:
        term = (p.get("proposed") or {}).get("terminalState")
        if term not in ALLOWED_TERMINAL:
            raise SystemExit(f"bad terminal {term} at {p.get('startVa')}")
        if p.get("recoveryLane") == "SOFT_MULTI_UNIT_EXECUTED":
            if p.get("sourceState") != "OPEN_EXECUTED_RESIDUAL":
                raise SystemExit(f"soft on non-exec {p.get('startVa')}")

    n_need_q = sum(
        1 for p in proofs if p.get("proposed", {}).get("requiresQuestionSupersession")
    )
    if n_need_q != EXPECTED_PROOFS:
        raise SystemExit(f"need_q {n_need_q}")

    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(parent_ready.get("generation", -1)) != 20:
        raise SystemExit(f"parent must be Gen20, got {parent_ready.get('generation')}")
    parent_advance = parent_ready.get("advance") or {}
    if parent_advance.get("kind") != "RESIDUAL_TERMINAL_OPEN_MULTI_UNIT":
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
    summary_path = formal_pack.resolve().parent / "SUMMARY.json"
    if summary_path.is_file():
        evidence_refs_common.append(
            f"{summary_path.resolve()}#sha256={_sha_file(summary_path)}"
        )

    closed_qids: list[str] = []
    updated: list[str] = []
    ambig_added = 0
    dark_closed = 0
    exec_closed = 0

    for proof in proofs:
        proposed = proof["proposed"]
        terminal_state = proposed["terminalState"]
        start = proof["startVa"].lower()
        residual = res_by_start.get(start)
        if residual is None:
            raise SystemExit(f"missing residual {proof['startVa']}")
        src = proof.get("sourceState") or residual.get("campaignState")
        if residual.get("campaignState") != src:
            raise SystemExit(
                f"{proof['startVa']} expected {src} got {residual.get('campaignState')}"
            )
        if src == "OPEN_DARK_RESIDUAL":
            dark_closed += 1
        elif src == "OPEN_EXECUTED_RESIDUAL":
            if residual.get("observationState") != "EXECUTED":
                raise SystemExit(f"exec not EXECUTED {proof['startVa']}")
            exec_closed += 1
        else:
            raise SystemExit(f"bad source {src}")

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
        residual["bytePattern"] = proposed["bytePattern"]
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
        contract["authorVerdict"] = proposed.get("classificationVerdict") or "STATIC_CODE_PLUS_PAD"
        contract["runtimeVerdict"] = (
            "EXECUTED_OBSERVED" if src == "OPEN_EXECUTED_RESIDUAL" else "UNSCORED"
        )
        contract["refuterVerdict"] = "SURVIVED"
        contract["questionIds"] = ""
        contract["evidenceRefs"] = ";".join(
            evidence_refs_common
            + [
                f"pe-shape#code-pad#sha256={proof['peBytesSha256']}",
                f"shapeKind#{shape_kind}",
                f"recoveryLane#{lane}",
                f"sourceState#{src}",
            ]
        )
        contract["cheapestFalsifier"] = residual["cheapestFalsifier"]
        contract["rebuildOwner"] = "UNASSIGNED"
        contract["rebuildImplementation"] = "UNMAPPED"
        contract["parityTests"] = "UNMAPPED"
        contract["rebuildState"] = "NOT_READY"
        contract["remainingUncertainty"] = _uncertainty(lane, shape_kind, src)
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
                    "A", f"code-pad|{ek}|{proof['peBytesSha256']}"
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
                "remainingUncertainty": _uncertainty(lane, shape_kind, src),
                "measuredAtUtc": measured_at,
            }
        )
        supersessions.append(
            {
                "supersessionId": _short_id(
                    "S", f"code-pad|{ek}|{proof['peBytesSha256']}"
                ),
                "oldEntityKey": ek,
                "newEntityKey": ek,
                "kind": ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": (
                    f"pe-shape#sha256={proof['peBytesSha256']};lane#{lane};src#{src}"
                ),
                "measuredAtUtc": measured_at,
            }
        )

    if len(updated) != EXPECTED_PROOFS:
        raise SystemExit(f"updated {len(updated)}")
    if ambig_added != EXPECTED_AMBIG_ADDED:
        raise SystemExit(f"ambig {ambig_added}")
    if dark_closed != EXPECTED_DARK or exec_closed != EXPECTED_EXEC:
        raise SystemExit(f"closed split {dark_closed}/{exec_closed}")
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
        raise SystemExit(f"padding drifted {term_pad}")
    if term_data != parent_data:
        raise SystemExit(f"data drifted {term_data}")
    if term_ambig != parent_ambig + EXPECTED_AMBIG_ADDED:
        raise SystemExit(f"ambig {term_ambig}")
    if open_dark != parent_dark - EXPECTED_DARK:
        raise SystemExit(f"dark {open_dark}")
    if open_exec != parent_exec - EXPECTED_EXEC:
        raise SystemExit(f"exec {open_exec}")
    if term_pad + term_data + term_ambig + open_dark + open_exec != 6117:
        raise SystemExit("partition incomplete")

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
        "terminalBoundedAmbiguityAddedThisGeneration": ambig_added,
        "openDarkClosedThisGeneration": dark_closed,
        "openExecutedClosedThisGeneration": exec_closed,
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
            "id": "residual-terminal-open-code-pad-bulk-v1",
            "note": (
                "Generation 21 residual-terminal code+pad / soft multi-unit bulk; "
                "verify via tools/re_open_residual_gen20_code_pad_generation.py verify"
            ),
        },
        "generatedAtUtc": measured_at,
        "generation": 21,
        "parentCampaign": {
            "path": str(parent.resolve()),
            "ready": _file_stamp(parent / "campaign.ready.json"),
            "generation": 20,
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
                "residualTerminalBoundedAmbiguityAdded": ambig_added,
                "residualTerminalsAdded": len(updated),
                "questionsClosedSurvived": len(set(closed_qids)),
                "openDarkClosed": dark_closed,
                "openExecutedClosed": exec_closed,
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
                "TERMINAL_BOUNDED_AMBIGUITY code+pad is residual-row static shape only.",
                "SOFT_MULTI_UNIT_EXECUTED is EXECUTED residual shape only.",
                "Not REBUILD_READY; no invented function names.",
                "Gen20 parent unmutated; prior terminals preserved.",
                "166 OPEN_DARK + 4 OPEN_EXECUTED remain.",
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
        "schema": "bea.re.open-residual-gen20-code-pad-generation-receipt.v1",
        "status": "APPLIED",
        "generation": 21,
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
    if int(ready.get("generation", -1)) != 21:
        raise SystemExit(f"expected Gen21, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != ADVANCE_KIND:
        raise SystemExit(f"bad advance {(ready.get('advance') or {}).get('kind')}")

    if verify_parent:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "tools/re_open_residual_gen19_multi_unit_generation.py",
                "verify",
                "--campaign",
                str(parent),
                "--skip-parent-verify",
            ],
            cwd=str(Path(__file__).resolve().parents[1]),
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise SystemExit(
                f"parent Gen20 verify failed: {completed.stderr or completed.stdout}"
            )

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    states = Counter(r.get("campaignState") for r in residuals)
    if len(residuals) != 6117:
        raise SystemExit("residuals")
    if states.get("TERMINAL_PADDING") != 5062:
        raise SystemExit(f"pad {states.get('TERMINAL_PADDING')}")
    if states.get("TERMINAL_DATA") != 23:
        raise SystemExit("data")
    if states.get("TERMINAL_BOUNDED_AMBIGUITY") != 862:
        raise SystemExit(f"ambig {states.get('TERMINAL_BOUNDED_AMBIGUITY')}")
    if states.get("OPEN_DARK_RESIDUAL") != 166:
        raise SystemExit(f"dark {states.get('OPEN_DARK_RESIDUAL')}")
    if states.get("OPEN_EXECUTED_RESIDUAL") != 4:
        raise SystemExit(f"exec {states.get('OPEN_EXECUTED_RESIDUAL')}")

    pack = json.loads(formal_pack.read_text(encoding="utf-8"))
    if pack.get("n_proofs") != EXPECTED_PROOFS:
        raise SystemExit("pack proofs")
    parent_res = _sha_file(parent / "campaign-residuals.tsv")
    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if parent_ready.get("generation") != 20:
        raise SystemExit("parent gen")
    child_parent_sha = (ready.get("parentCampaign") or {}).get("residualsSha256")
    if child_parent_sha != parent_res:
        raise SystemExit("parent residuals sha drift")

    rc = ready.get("counts") or {}
    if int(rc.get("residualTerminalsAddedThisGeneration", -1)) != EXPECTED_PROOFS:
        raise SystemExit("added count")
    if int(rc.get("openDarkClosedThisGeneration", -1)) != EXPECTED_DARK:
        raise SystemExit("dark closed")
    if int(rc.get("openExecutedClosedThisGeneration", -1)) != EXPECTED_EXEC:
        raise SystemExit("exec closed")

    result = {
        "status": "CAMPAIGN_VERIFIED",
        "generation": 21,
        "counts": ready.get("counts"),
        "residualStates": dict(states),
        "parentVerified": verify_parent,
        "formalPackSha256": _sha_file(formal_pack),
        "readySha256": _sha_file(campaign / "campaign.ready.json"),
        "nProofs": EXPECTED_PROOFS,
        "parentGen20Unmutated": True,
    }
    print("CAMPAIGN_VERIFIED", json.dumps(result["counts"]))
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--parent", type=Path, default=PARENT_GEN20)
    b.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--campaign", type=Path, default=DEFAULT_OUT)
    v.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    v.add_argument("--parent", type=Path, default=PARENT_GEN20)
    v.add_argument("--skip-parent-verify", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "build":
        receipt = build_generation(
            parent=args.parent, formal_pack=args.formal_pack, out=args.out
        )
        print(json.dumps(receipt, indent=2))
        print("OPEN_RESIDUAL_GEN20_CODE_PAD_GENERATION_APPLIED")
        return 0
    if args.cmd == "verify":
        verify_generation(
            args.campaign,
            args.formal_pack,
            args.parent,
            verify_parent=not args.skip_parent_verify,
        )
        print("OPEN_RESIDUAL_GEN20_CODE_PAD_GENERATION_VERIFIED")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
