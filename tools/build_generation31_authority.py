#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generation 31 authority builder: the 16 mutation-killed REBUILD_READY rows.

The single-row ``advance-runtime`` reducer admits exactly one overlay contract
per call and one generation per call.  Criterion 3 requires all 16
mutation-killed rebuild-parity rows in ONE Generation 31, and rows 1 and 2 are
two contract rows for the one ``CBattleEngineJetPart__GetFriction`` entity, so
this bespoke builder seeds the db.18624 coverage snapshot with the literal-pinned
Generation 30 carry bridge and then applies all sixteen rows in one cut.

Determinism: every input is a staged, hash-bound artifact; the advance record
carries no wall-clock stamp, so the frozen reducer replays this builder and the
campaign verifier requires the eight ledgers and the normalized READY to
reproduce byte-for-byte from the parent and the staged inputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import re_campaign as campaign  # noqa: E402


ADVANCE_KIND = "GENERATION31_REBUILD_READY_SIXTEEN"
ADVANCE_SCHEMA = "bea.re.generation31-rebuild-ready-advance.v1"

COLUMNS_BY_OUTPUT = {
    "campaign-functions.tsv": campaign.FUNCTION_COLUMNS,
    "campaign-residuals.tsv": campaign.RESIDUAL_COLUMNS,
    "campaign-questions.tsv": campaign.QUESTION_COLUMNS,
    "campaign-scenarios.tsv": campaign.SCENARIO_COLUMNS,
    "campaign-levers.tsv": campaign.LEVER_COLUMNS,
    "campaign-contracts.tsv": campaign.CONTRACT_COLUMNS,
    "campaign-adjudications.tsv": campaign.ADJUDICATION_COLUMNS,
    "campaign-supersessions.tsv": campaign.SUPERSESSION_COLUMNS,
}

PREP_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-31-prep-2026-08-17"
)
SNAPSHOT_RELATIVE = PREP_RELATIVE / "snapshot-a"
GATE_RELATIVE = PREP_RELATIVE / "gate-results"
REFUTER_RELATIVE = PREP_RELATIVE / "refuter-findings"
ADJUDICATION_RELATIVE = PREP_RELATIVE / "adjudications"
MUTATION_RESULTS_RELATIVE = Path(
    "local-lab/rebuild-parity-mutation-kills-2026-08-17/mutation-results.json"
)

SPECIMEN_SHA = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

# One sentence per mutation record, mirroring the measured 2026-08-17 criterion
# (_CRITERION_3_SIXTEEN_KILLS_20260817) and the staged refuter findings.  The
# builder fails closed if this text is not carried by the staged finding.
LAWS = {
    "01-jetfriction-coregate": (
        "the integer slow-flight friction ladder gates the interpolated arm at retail 1.0"
    ),
    "01b-jetfriction-floatgate": (
        "GetFriction loads 1.5f (0x3FC00000) from 0x005D8BD8"
    ),
    "02-careerslots-guard": (
        "SetSlot compares the slot against 0x100 while the store holds 1024 bits"
    ),
    "03-careernodes-mask": (
        "SetBaseThingExistTo builds its bit from bit 0 (mov edx,1 then shl edx,cl)"
    ),
    "04-killcounters-normalise": (
        "NormaliseOnLoad clamps exactly two counter words and leaves the other three alone"
    ),
    "05-scheduler-int16": (
        "AddEvent stores the event number as signed sixteen bits (movsx word)"
    ),
    "06-analogue-divide": (
        "NormalizeLeftX multiplies by 0.001f (0x3A83126F at 0x005DC6E4), and 0.36f occurs zero times imagewide"
    ),
    "07-interpolation-narrow": (
        "AdjustedOldAngle keeps the wrapped angle on the x87 stack (wide) instead of rounding it back to float"
    ),
    "08-hostile-narrow": (
        "ShouldWarn compares the unrounded elapsed-time difference against 5.0f"
    ),
    "09-ammocount-truncate": (
        "AmmoCount rounds to nearest even via the bare fistp qword under QIfist"
    ),
    "10-camerazoom-divide": (
        "MovieCameraZoom multiplies by the rounded reciprocal 1/90 (0x3C360B61 at 0x005D9338), unique in the image"
    ),
    "11-gravity-tableorder": (
        "the gravity jump tables walk the walker/jet arms in the order the parity expectedBits pins (index 0 takes 0.002f)"
    ),
    "12-walkerfire-shared": (
        "the walker CanWeaponFire body carries the active gate the jet body does not (the jet displacement occurs zero times in the jet body)"
    ),
    "13-waterentry-arm": (
        "GoingIntoWater's arm selector at 0x00413ABF is non-inclusive: the low arm is taken only strictly above the 0.3f margin"
    ),
    "14-autolevel-constant": (
        "AutoLevel gates on 0.1f squared (the folded 0x3C23D70B), which is not plain 0.01f"
    ),
    "15-chunkreader-clamp": (
        "Skip leaves the over-read charge unclamped so it wraps unsigned (a silent no-op)"
    ),
}


def _repo_root() -> Path:
    return campaign.REPO_ROOT


def _prep_default() -> Path:
    return _repo_root() / PREP_RELATIVE


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _mint_second_contract_id(entity_key: str, owner_posix: str) -> str:
    return "C-" + _sha256_text(f"{entity_key}|{owner_posix}")[:16]


def _stamp3(relative: str, stamp: dict) -> dict:
    return {
        "path": relative,
        "bytes": stamp["bytes"],
        "sha256": stamp["sha256"],
    }


def _read_tsv_rows(path: Path) -> list[dict[str, str]]:
    return campaign._read_tsv(path)


def _load_contracts_sixteen(prep: Path) -> list[dict[str, str]]:
    with (prep / "contracts-16.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(
            csv.DictReader(
                (line for line in stream if not line.startswith("#")),
                delimiter="\t",
            )
        )
    if len(rows) != 16:
        raise campaign.CampaignError(
            f"Generation 31 prep expects 16 contract rows, found {len(rows)}"
        )
    return rows


def _load_mutation_records(prep: Path) -> dict[str, dict]:
    path = _repo_root() / MUTATION_RESULTS_RELATIVE
    records = json.loads(path.read_text(encoding="utf-8"))
    return {record["id"]: record for record in records}


def _subject_row(order_row: dict[str, str]) -> dict[str, str]:
    base_contract_id = order_row["baseContractId"]
    if base_contract_id == "SECOND-ROW":
        base_contract_id = _mint_second_contract_id(
            order_row["entityKey"], order_row["owner"]
        )
    return {
        "baseContractId": base_contract_id,
        "entityKey": order_row["entityKey"],
        "questionIdsAddressed": order_row["questionId"],
    }


def _decision_json(
    order_row: dict[str, str],
    parent_ready_sha: str,
    overlay_sha: str,
    finding_stamp: dict,
    result_stamp: dict,
    result_stamp_gate: dict,
    measured_at_utc: str,
    parent_contract: dict[str, str],
    law: str,
) -> dict:
    owner = (campaign.REPO_ROOT / order_row["owner"]).resolve()
    test_file = (campaign.REPO_ROOT / order_row["testFile"]).resolve()
    project = (campaign.REPO_ROOT / order_row["project"]).resolve()
    owner_stamp = campaign.coverage.file_stamp(owner)
    test_stamp = campaign.coverage.file_stamp(test_file)
    project_stamp = campaign.coverage.file_stamp(project)
    base_contract_id = order_row["baseContractId"]
    if base_contract_id == "SECOND-ROW":
        base_contract_id = _mint_second_contract_id(
            order_row["entityKey"], order_row["owner"]
        )
    rebuild_mapping = {
        "rebuildOwner": order_row["owner"].replace("\\", "/"),
        "rebuildImplementation": order_row["implementation"],
        "parityTests": order_row["testName"],
        "rebuildState": "REBUILD_READY",
    }
    gate = {
        "schema": campaign.REBUILD_GATE_SCHEMA,
        "runner": "dotnet-test-v1",
        "owner": _stamp3(order_row["owner"], owner_stamp),
        "implementation": order_row["implementation"],
        "test": _stamp3(order_row["testFile"], test_stamp),
        "testName": order_row["testName"],
        "project": _stamp3(order_row["project"], project_stamp),
        "expectedTests": int(order_row["expectedTests"]),
        "result": {
            **_stamp3(
                f"../../gate-results/{order_row['order']}/rebuild-result.json",
                result_stamp_gate,
            )
        },
    }
    decision = {
        "refuterVerdict": "SURVIVED",
        "baseContractId": base_contract_id,
        "questionIdsAddressed": [order_row["questionId"]],
        "measuredAtUtc": measured_at_utc,
        "terminalState": "TERMINAL_REBUILD_READY",
        "remainingUncertainty": parent_contract.get("remainingUncertainty", ""),
        "semanticGradeBefore": parent_contract.get("semanticGrade", ""),
        "semanticGradeAfter": "C1_CANDIDATE_PARTIAL",
        "authorVerdict": "SUPPORTED_BY_PRISTINE_BYTES_AND_MEASURED_MUTATION_KILL",
        "law": law,
        "semanticGradeDisposition": (
            "C0_OPAQUE_RAISED_TO_C1_CANDIDATE_PARTIAL"
            if parent_contract.get("semanticGrade", "") == "C0_OPAQUE"
            else "C1_CANDIDATE_PARTIAL_UNCHANGED"
        ),
        "refuterEvidence": [
            {
                "role": "refuter-finding",
                "path": (
                    f"../../refuter-findings/{order_row['order']}/"
                    "refuter-finding.json"
                ),
                "sha256": finding_stamp["sha256"],
            },
            {
                "role": "refuter-result",
                "path": (
                    f"../../refuter-findings/{order_row['order']}/"
                    "refuter-result.json"
                ),
                "sha256": result_stamp["sha256"],
            },
        ],
        "rebuildMapping": rebuild_mapping,
        "rebuildGate": gate,
    }
    return {
        "schema": campaign.RUNTIME_ADJUDICATION_SCHEMA,
        "baseCampaignReadySha256": parent_ready_sha,
        "overlayReadySha256": overlay_sha,
        "decision": decision,
    }


def _adjudication_id(
    parent_ready_sha: str,
    overlay_ready_sha: str,
    adjudication_stamp: dict,
    evidence_stamps: list[dict],
    verdict: str,
) -> str:
    evidence_identity = "|".join(
        f"{row['role']}:{row['sha256']}" for row in evidence_stamps
    )
    return "A-" + _sha256_text(
        "|".join(
            (
                parent_ready_sha,
                overlay_ready_sha,
                adjudication_stamp["sha256"],
                evidence_identity,
                verdict,
            )
        )
    )[:16]


def _write_adjudications(
    prep: Path,
    parent_ready_sha: str,
    contracts_by_id: dict[str, dict[str, str]],
) -> list[dict]:
    """Materialize the 16 deterministic adjudication JSONs once, then pin them."""
    order_rows = _load_contracts_sixteen(prep)
    mutations = _load_mutation_records(prep)
    adjudication_dir = prep / "adjudications"
    adjudication_dir.mkdir(parents=True, exist_ok=True)
    refuter_manifest = json.loads(
        (prep / "refuter-findings" / "refuters-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    gate_manifest = json.loads(
        (prep / "gate-results" / "results-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    refuter_by_order = {
        row["order"]: row for row in refuter_manifest["rows"]
    }
    gate_by_order = {row["order"]: row for row in gate_manifest["rows"]}
    rows_out = []
    for order_row in order_rows:
        order = order_row["order"]
        mutation = mutations[order_row["mutationId"]]
        law = LAWS[order_row["mutationId"]]
        refuter_row = refuter_by_order[order]
        gate_row = gate_by_order[order]
        finding_path = (
            prep / "refuter-findings" / order / "refuter-finding.json"
        )
        result_path = prep / "refuter-findings" / order / "refuter-result.json"
        gate_result_path = prep / "gate-results" / order / "rebuild-result.json"
        overlay_path = prep / "gate-results" / order / "overlay.json"
        finding_stamp = campaign.coverage.file_stamp(finding_path)
        result_stamp = campaign.coverage.file_stamp(result_path)
        gate_result_stamp = campaign.coverage.file_stamp(gate_result_path)
        overlay_sha = hashlib.sha256(overlay_path.read_bytes()).hexdigest()
        if overlay_sha != gate_row["overlaySha256"]:
            raise campaign.CampaignError(
                f"order {order}: overlay SHA drifted from the gate manifest"
            )
        measured_at = refuter_row["result"]["lastWriteUtc"]
        subject_row = _subject_row(order_row)
        parent_contract = contracts_by_id.get(subject_row["baseContractId"])
        if parent_contract is None:
            first_id = _subject_row(
                next(
                    row
                    for row in order_rows
                    if row["order"] == "1"
                )
            )["baseContractId"]
            parent_contract = dict(contracts_by_id[first_id])
            parent_contract["contractId"] = subject_row["baseContractId"]
        row_dir = adjudication_dir / order
        row_dir.mkdir(parents=True, exist_ok=True)
        decision = _decision_json(
            order_row,
            parent_ready_sha,
            overlay_sha,
            finding_stamp,
            result_stamp,
            gate_result_stamp,
            measured_at,
            parent_contract,
            law,
        )
        path = row_dir / "adjudication.json"
        content = json.dumps(decision, indent=2) + "\n"
        if path.is_file():
            if path.read_text(encoding="utf-8") != content:
                raise campaign.CampaignError(
                    f"order {order}: adjudication JSON drifted; re-derive it"
                )
        else:
            path.write_text(content, encoding="utf-8")
        rows_out.append(
            {
                "order": order,
                "mutationId": order_row["mutationId"],
                "adjudicationPath": str(
                    path.relative_to(campaign.REPO_ROOT).as_posix()
                ),
                "adjudicationStamp": campaign.coverage.file_stamp(path),
                "measuredAtUtc": measured_at,
                "overlayReadySha256": overlay_sha,
            }
        )
    return rows_out


def _validate_one_row(
    order_row: dict[str, str],
    adjudication: dict,
    adjudication_path: Path,
    overlay_sha: str,
    parent_contract: dict[str, str],
) -> dict:
    subject_row = _subject_row(order_row)
    decision = campaign._runtime_mapping(
        adjudication.get("decision"), "Generation 31 decision"
    )
    if decision.get("refuterVerdict") != "SURVIVED":
        raise campaign.CampaignError(
            f"order {order_row['order']}: only SURVIVED rows may terminate"
        )
    if decision.get("terminalState") != "TERMINAL_REBUILD_READY":
        raise campaign.CampaignError(
            f"order {order_row['order']}: terminal state is not REBUILD_READY"
        )
    if (
        decision.get("baseContractId") != subject_row["baseContractId"]
        or set(decision.get("questionIdsAddressed", []))
        != {order_row["questionId"]}
    ):
        raise campaign.CampaignError(
            f"order {order_row['order']}: decision does not reproduce its subject"
        )
    campaign._validate_rebuild_ready_gate(
        decision, adjudication_path, subject_row, overlay_sha
    )

    evidence_specs = campaign._runtime_list(
        decision.get("refuterEvidence"), "Generation 31 refuter evidence"
    )
    evidence_stamps: list[dict] = []
    evidence_paths: dict[str, Path] = {}
    for item in evidence_specs:
        role = str(item.get("role", "")).strip()
        if not role or role in evidence_paths:
            raise campaign.CampaignError(
                "Generation 31 refuter evidence has duplicate/missing roles"
            )
        path = campaign._runtime_artifact_path(
            adjudication_path, item.get("path"), f"refuter:{role}"
        )
        stamp = campaign._runtime_artifact_stamp(
            adjudication_path,
            item.get("path"),
            item.get("sha256"),
            f"refuter:{role}",
        )
        evidence_paths[role] = path
        evidence_stamps.append(stamp)
    if len(set(evidence_paths.values())) != len(evidence_paths):
        raise campaign.CampaignError(
            "Generation 31 refuter evidence aliases artifacts"
        )
    result_path = evidence_paths["refuter-result"]
    finding_path = evidence_paths["refuter-finding"]
    refuter_result = campaign._runtime_json(result_path, "refuter result")
    finding = campaign._runtime_json(finding_path, "refuter finding")
    expected_subject = campaign._runtime_refuter_subject(subject_row, overlay_sha)
    if (
        not campaign._same_json(finding.get("subject"), expected_subject)
        or not campaign._same_json(
            refuter_result.get("subject"), expected_subject
        )
    ):
        raise campaign.CampaignError(
            f"order {order_row['order']}: refuter is not bound to the candidate"
        )
    min_sample = refuter_result.get("minSampleN")
    if not isinstance(min_sample, int) or min_sample < 1:
        raise campaign.CampaignError(
            f"order {order_row['order']}: refuter has invalid minSampleN"
        )
    reproduced = campaign.probe_refute.adjudicate(finding, min_sample_n=min_sample)
    observed_without_source = {
        key: value for key, value in refuter_result.items() if key != "source"
    }
    if reproduced != observed_without_source:
        raise campaign.CampaignError(
            f"order {order_row['order']}: refuter result does not reproduce"
        )
    if refuter_result.get("verdict") != "SURVIVED":
        raise campaign.CampaignError(
            f"order {order_row['order']}: refuter verdict is not SURVIVED"
        )
    if (
        parent_contract.get("entityKey") != subject_row["entityKey"]
        or parent_contract.get("contractId") != subject_row["baseContractId"]
    ):
        raise campaign.CampaignError(
            f"order {order_row['order']}: base contract does not match the parent"
        )
    if parent_contract.get("semanticGrade") not in {
        "C0_OPAQUE",
        "C1",
        "C1_CANDIDATE_PARTIAL",
    }:
        raise campaign.CampaignError(
            f"order {order_row['order']}: parent grade is not a static grade"
        )
    law = str(decision.get("law", "")).strip()
    claim_statement = str(finding.get("claim", {}).get("statement", ""))
    if not law or law not in claim_statement:
        raise campaign.CampaignError(
            f"order {order_row['order']}: decision law is not carried by the finding"
        )
    return {
        "order": order_row["order"],
        "baseContractId": subject_row["baseContractId"],
        "entityKey": subject_row["entityKey"],
        "questionId": order_row["questionId"],
        "overlayReadySha256": overlay_sha,
        "adjudicationPath": adjudication_path,
        "adjudicationStamp": campaign.coverage.file_stamp(adjudication_path),
        "evidenceStamps": evidence_stamps,
        "verdict": "SURVIVED",
        "expectedTests": int(order_row["expectedTests"]),
        "mutationId": order_row["mutationId"],
        "law": law,
        "semanticGradeAfter": str(decision.get("semanticGradeAfter", "")),
        "authorVerdict": str(decision.get("authorVerdict", "")),
    }


def _apply_rows(
    rows: dict[str, list[dict[str, str]]],
    validated: list[dict],
    order_rows: list[dict[str, str]],
    parent_ready_sha: str,
) -> dict:
    functions = rows["campaign-functions.tsv"]
    residuals = rows["campaign-residuals.tsv"]
    questions = rows["campaign-questions.tsv"]
    contracts = rows["campaign-contracts.tsv"]
    adjudications = rows["campaign-adjudications.tsv"]

    before = {name: _snapshot_ids(value) for name, value in rows.items()}

    contract_by_id = {row["contractId"]: row for row in contracts}
    question_by_id = {row["questionId"]: row for row in questions}
    entity_rows = {
        row["entityKey"]: row for row in functions + residuals
    }

    closed_questions: set[str] = set()
    updated_entities: set[str] = set()
    grade_movements: list[dict] = []
    adjudication_rows: list[dict] = []
    second_row_contract_id: str | None = None

    for item in validated:
        order = item["order"]
        decision = campaign._runtime_json(
            item["adjudicationPath"], "Generation 31 adjudication"
        )["decision"]
        contract = contract_by_id.get(item["baseContractId"])
        if contract is None and order == "2":
            first = contract_by_id[
                _subject_row(
                    next(row for row in order_rows if row["order"] == "1")
                )["baseContractId"]
            ]
            contract = dict(first)
            contract["contractId"] = item["baseContractId"]
            second_row_contract_id = item["baseContractId"]
            contracts.append(contract)
            contract_by_id[contract["contractId"]] = contract
        if contract is None or contract["entityKey"] != item["entityKey"]:
            raise campaign.CampaignError(
                f"order {order}: base contract is absent or names another entity"
            )

        question = question_by_id.get(item["questionId"])
        if question is None or question["entityKey"] != item["entityKey"]:
            raise campaign.CampaignError(
                f"order {order}: addressed question is absent or misbound"
            )
        if item["questionId"] in closed_questions:
            if question["state"] != "CLOSED_SURVIVED":
                raise campaign.CampaignError(
                    f"order {order}: shared question was not closed by its first row"
                )
        else:
            if question["state"] != "OPEN":
                raise campaign.CampaignError(
                    f"order {order}: addressed question is not OPEN"
                )
            question["state"] = "CLOSED_SURVIVED"
            question["lastOutcome"] = "SURVIVED"
            question["attemptCount"] = str(
                campaign._integer(question.get("attemptCount"), 0) + 1
            )
            question["lastMeasurementDate"] = decision["measuredAtUtc"][:10]
            closed_questions.add(item["questionId"])

        other_open = [
            row["questionId"]
            for row in questions
            if row["entityKey"] == item["entityKey"]
            and row["state"] == "OPEN"
        ]
        if other_open:
            raise campaign.CampaignError(
                f"order {order}: terminal row leaves other entity questions open"
            )

        grade_before = contract.get("semanticGrade", "")
        contract["semanticGrade"] = "C1_CANDIDATE_PARTIAL"
        if order == "13":
            contract["authorVerdict"] = contract.get(
                "authorVerdict", item["authorVerdict"]
            )
        else:
            contract["authorVerdict"] = item["authorVerdict"]
            contract["inputs"] = f"static byte law: {item['law']}"
        prior_refs = contract.get("evidenceRefs", "")
        for ref in (
            f"local-lab/rebuild-parity-mutation-kills-2026-08-17/"
            f"mutation-results.json#id={item['mutationId']}",
            (
                "local-lab/re-campaign-incident-recovery-20260808-v1/"
                "generation-31-prep-2026-08-17/refuter-findings/"
                f"{order}/refuter-finding.json"
            ),
        ):
            prior_refs = campaign._append_state(prior_refs, ref)
        contract["evidenceRefs"] = prior_refs
        contract["refuterVerdict"] = "SURVIVED"
        contract["contractState"] = "TERMINAL_REBUILD_READY"
        contract["lastMeasurementDate"] = decision["measuredAtUtc"][:10]
        grade_movements.append(
            {
                "entityKey": item["entityKey"],
                "contractId": contract["contractId"],
                "semanticGradeBefore": grade_before,
                "semanticGradeAfter": contract["semanticGrade"],
            }
        )
        mapping = campaign._runtime_mapping(
            decision.get("rebuildMapping"), "Generation 31 rebuildMapping"
        )
        for field in (
            "rebuildOwner",
            "rebuildImplementation",
            "parityTests",
            "rebuildState",
        ):
            value = mapping.get(field)
            if not isinstance(value, str) or not value.strip():
                raise campaign.CampaignError(
                    f"order {order}: rebuildMapping.{field} is empty"
                )
            contract[field] = value.strip()
        if (
            contract["rebuildState"] != "REBUILD_READY"
            or contract["rebuildOwner"] == "UNASSIGNED"
            or contract["parityTests"] == "UNMAPPED"
        ):
            raise campaign.CampaignError(
                f"order {order}: REBUILD_READY termination lacks its mapping"
            )

        entity = entity_rows.get(item["entityKey"])
        if entity is None:
            raise campaign.CampaignError(
                f"order {order}: entity is absent from function/residual ledgers"
            )
        if item["entityKey"] not in updated_entities:
            entity_grade_before = entity.get("semanticGrade", "")
            entity["campaignState"] = "TERMINAL_REBUILD_READY"
            entity["resolutionState"] = "TERMINAL_REBUILD_READY"
            entity["lastMeasurementDate"] = decision["measuredAtUtc"][:10]
            if entity.get("entityKey", "").startswith("CODE:"):
                entity["semanticGrade"] = "C1_CANDIDATE_PARTIAL"
            entity["evidenceStates"] = campaign._append_state(
                entity.get("evidenceStates", ""),
                "RUNTIME_CONTRACT_REFUTER_SURVIVED",
            )
            updated_entities.add(item["entityKey"])
            if entity.get("entityKey", "").startswith("CODE:"):
                grade_movements.append(
                    {
                        "entityKey": item["entityKey"],
                        "semanticGradeBefore": entity_grade_before,
                        "semanticGradeAfter": entity.get("semanticGrade", ""),
                    }
                )

        adjudication_id = _adjudication_id(
            parent_ready_sha,
            item["overlayReadySha256"],
            item["adjudicationStamp"],
            item["evidenceStamps"],
            "SURVIVED",
        )
        if any(
            row.get("adjudicationId") == adjudication_id for row in adjudications
        ):
            raise campaign.CampaignError(
                f"order {order}: adjudication already exists in the lineage"
            )
        adjudications.append(
            {
                "adjudicationId": adjudication_id,
                "baseContractId": contract["contractId"],
                "entityKey": contract["entityKey"],
                "overlaySchema": "bea.re.runtime-contract-overlay.v1",
                "overlayReadySha256": item["overlayReadySha256"],
                "questionIdsAddressed": item["questionId"],
                "refuterVerdict": "SURVIVED",
                "refuterEvidenceSha256": ";".join(
                    row["sha256"] for row in item["evidenceStamps"]
                ),
                "semanticPromotionApplied": "true",
                "terminalState": "TERMINAL_REBUILD_READY",
                "successorQuestionIds": "",
                "remainingUncertainty": contract.get("remainingUncertainty", ""),
                "measuredAtUtc": decision["measuredAtUtc"],
            }
        )
        adjudication_rows.append(adjudications[-1])

    after = {name: _snapshot_ids(value) for name, value in rows.items()}
    return {
        "closedQuestions": sorted(closed_questions),
        "gradeMovements": grade_movements,
        "secondRowContractId": second_row_contract_id,
        "adjudicationRows": adjudication_rows,
        "before": before,
        "after": after,
    }


def _snapshot_ids(rows: list[dict[str, str]]) -> dict[str, str]:
    key_column = next(
        (
            column
            for column in (
                "entityKey",
                "questionId",
                "contractId",
                "adjudicationId",
                "scenarioId",
                "leverId",
                "supersessionId",
            )
            if rows and rows[0].get(column)
        ),
        "",
    )
    if not key_column:
        return {"ids": "", "count": str(len(rows))}
    ids = sorted(row[key_column] for row in rows)
    return {
        "idColumn": key_column,
        "count": str(len(rows)),
        "idSetSha256": hashlib.sha256(
            "\n".join(ids).encode("utf-8")
        ).hexdigest(),
    }


def _compare_rows_except(
    before: list[dict[str, str]],
    after: list[dict[str, str]],
    changed_ids: set[str],
    key_column: str,
) -> tuple[int, int]:
    before_by_id = {row[key_column]: row for row in before}
    after_by_id = {row[key_column]: row for row in after}
    unchanged = 0
    changed = 0
    for row_id, before_row in before_by_id.items():
        after_row = after_by_id.get(row_id)
        if after_row is None:
            continue
        if row_id in changed_ids:
            changed += 1
            continue
        if before_row != after_row:
            raise campaign.CampaignError(
                f"unexpected row change outside the sixteen: {key_column}={row_id}"
            )
        unchanged += 1
    return unchanged, changed


def _zero_collateral_proof(
    seeded_rows: dict[str, list[dict[str, str]]],
    final_rows: dict[str, list[dict[str, str]]],
    changed: dict[str, set[str]],
) -> dict:
    proof: dict = {}
    for name, key_column in (
        ("campaign-functions.tsv", "entityKey"),
        ("campaign-residuals.tsv", "entityKey"),
        ("campaign-questions.tsv", "questionId"),
        ("campaign-contracts.tsv", "contractId"),
        ("campaign-scenarios.tsv", "scenarioId"),
        ("campaign-levers.tsv", "regionKey"),
        ("campaign-adjudications.tsv", "adjudicationId"),
        ("campaign-supersessions.tsv", "supersessionId"),
    ):
        before = seeded_rows[name]
        after = final_rows[name]
        before_ids = {row.get(key_column, "") for row in before}
        after_ids = {row.get(key_column, "") for row in after}
        removed = before_ids - after_ids
        added = after_ids - before_ids
        changed_ids = changed.get(name, set())
        if removed or added - changed_ids:
            raise campaign.CampaignError(
                f"Generation 31 moved rows outside the sixteen: {name}"
            )
        untouched, touched = _compare_rows_except(
            before, after, changed_ids, key_column
        )
        proof[name] = {
            "beforeRows": len(before),
            "afterRows": len(after),
            "changedRows": touched,
            "unchangedRows": untouched,
            "addedRows": len(added),
            "removedRows": len(removed),
        }
    return proof


def build(
    parent_path: Path,
    out: Path,
    *,
    snapshot: Path | None = None,
    prep: Path | None = None,
    _self_check: bool = True,
    _verified_parent_receipt: dict | None = None,
) -> dict:
    parent = Path(os.path.abspath(parent_path))
    snapshot_path = Path(os.path.abspath(snapshot)) if snapshot else (
        _repo_root() / SNAPSHOT_RELATIVE
    )
    prep_root = Path(os.path.abspath(prep)) if prep else _prep_default()
    if out.exists():
        raise campaign.CampaignError(
            f"refusing existing Generation 31 destination: {out}"
        )
    if _verified_parent_receipt is None:
        parent_receipt = campaign._verify_generation30_campaign_carry(parent)
    else:
        parent_receipt = _verified_parent_receipt
    if parent_receipt.get("generation") != 30:
        raise campaign.CampaignError(
            "Generation 31 requires the canonical Generation 30 parent"
        )
    parent_ready = campaign.coverage.file_stamp(parent / "campaign.ready.json")

    parent_contracts = {
        row["contractId"]: row
        for row in _read_tsv_rows(parent / "campaign-contracts.tsv")
    }
    adjudication_rows = _write_adjudications(
        prep_root, parent_ready["sha256"], parent_contracts
    )
    seeded_stage = Path(
        tempfile.mkdtemp(prefix=".gen31-seeded-", dir=out.parent or Path.cwd())
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        seeded_receipt = campaign.seed(
            snapshot_path,
            seeded_stage / "seeded",
            carry=parent,
            _self_check=False,
            _verified_carry_receipt=parent_receipt,
        )
    except Exception:
        shutil.rmtree(seeded_stage, ignore_errors=True)
        raise

    rows = {
        name: _read_tsv_rows(seeded_stage / "seeded" / name)
        for name in campaign.OUTPUTS
    }
    seeded_rows = {
        name: [dict(row) for row in value] for name, value in rows.items()
    }
    contracts_by_id = {
        row["contractId"]: row for row in rows["campaign-contracts.tsv"]
    }
    order_rows = _load_contracts_sixteen(prep_root)
    validated = []
    for order_row in order_rows:
        adjudication_path = (
            prep_root
            / "adjudications"
            / order_row["order"]
            / "adjudication.json"
        )
        adjudication = campaign._runtime_json(
            adjudication_path, "Generation 31 adjudication"
        )
        overlay_path = (
            prep_root / "gate-results" / order_row["order"] / "overlay.json"
        )
        overlay_sha = hashlib.sha256(overlay_path.read_bytes()).hexdigest()
        base_contract_id = _subject_row(order_row)["baseContractId"]
        parent_contract = contracts_by_id.get(base_contract_id)
        if parent_contract is None and order_row["order"] != "2":
            raise campaign.CampaignError(
                f"order {order_row['order']}: base contract is absent from the seeded campaign"
            )
        if order_row["order"] == "2":
            first_row = next(
                row for row in order_rows if row["order"] == "1"
            )
            first_id = _subject_row(first_row)["baseContractId"]
            first_contract = contracts_by_id[first_id]
            parent_contract = dict(first_contract)
            parent_contract["contractId"] = base_contract_id
        validated.append(
            _validate_one_row(
                order_row,
                adjudication,
                adjudication_path,
                overlay_sha,
                parent_contract,
            )
        )

    accounting = _apply_rows(
        rows, validated, order_rows, parent_ready["sha256"]
    )
    before_contract_ids = set(
        row["contractId"] for row in _read_tsv_rows(
            seeded_stage / "seeded" / "campaign-contracts.tsv"
        )
    )
    after_contract_ids = {row["contractId"] for row in rows["campaign-contracts.tsv"]}
    changed_contract_ids = {
        item["baseContractId"] for item in validated
    }
    new_contract_ids = after_contract_ids - before_contract_ids
    if new_contract_ids != {accounting["secondRowContractId"]}:
        raise campaign.CampaignError(
            "the second GetFriction contract row is not the only new contract"
        )
    changed_ids = {
        "campaign-functions.tsv": {item["entityKey"] for item in validated},
        "campaign-residuals.tsv": {item["entityKey"] for item in validated},
        "campaign-questions.tsv": set(accounting["closedQuestions"]),
        "campaign-contracts.tsv": changed_contract_ids,
        "campaign-adjudications.tsv": {
            row["adjudicationId"] for row in accounting["adjudicationRows"]
        },
        "campaign-supersessions.tsv": set(),
    }
    collateral = _zero_collateral_proof(seeded_rows, rows, changed_ids)

    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        for name, columns in COLUMNS_BY_OUTPUT.items():
            campaign._write_tsv(stage / name, columns, rows[name])
        reducer = campaign._publish_reducer(stage)
        counts = {
            "functions": len(rows["campaign-functions.tsv"]),
            "residuals": len(rows["campaign-residuals.tsv"]),
            "questions": len(rows["campaign-questions.tsv"]),
            "scenarios": len(rows["campaign-scenarios.tsv"]),
            "levers": len(rows["campaign-levers.tsv"]),
            "contracts": len(rows["campaign-contracts.tsv"]),
            "adjudications": len(rows["campaign-adjudications.tsv"]),
            "supersessions": len(rows["campaign-supersessions.tsv"]),
        }
        receipt = {
            "schema": campaign.SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "generation": 31,
            "parentCampaign": {
                "path": str(parent.resolve()),
                "ready": {**parent_ready, "path": "campaign.ready.json"},
            },
            "sourceSnapshot": seeded_receipt["sourceSnapshot"],
            "advance": {
                "kind": ADVANCE_KIND,
                "schema": ADVANCE_SCHEMA,
                "parentSchema": campaign.SCHEMA,
                "snapshot": {
                    "path": str(snapshot_path.resolve()),
                    "schema": seeded_receipt["sourceSnapshot"]["schema"],
                    "coverageSetSha256": seeded_receipt["sourceSnapshot"][
                        "coverageSetSha256"
                    ],
                },
                "prepRoot": {"path": str(prep_root.resolve())},
                "reseed": seeded_receipt["advance"],
                "rows": [
                    {
                        "order": item["order"],
                        "baseContractId": item["baseContractId"],
                        "entityKey": item["entityKey"],
                        "overlayReadySha256": item["overlayReadySha256"],
                        "verdict": item["verdict"],
                        "terminalState": "TERMINAL_REBUILD_READY",
                        "expectedTests": item["expectedTests"],
                    }
                    for item in validated
                ],
                "secondRowContractId": {
                    "contractId": accounting["secondRowContractId"],
                    "mintedFrom": "sha256(entityKey|ownerPosix)[:16]",
                    "ownerPosix": "rebuild/OnslaughtRebuild.Core/RetailJetFriction.cs",
                },
                "closedQuestions": accounting["closedQuestions"],
                "gradeMovements": accounting["gradeMovements"],
                "zeroCollateral": collateral,
                "semanticGradePolicy": (
                    "Fourteen rows raise C0_OPAQUE to C1_CANDIDATE_PARTIAL behind "
                    "a SURVIVED probe refuter; row 13 carries C1_CANDIDATE_PARTIAL "
                    "unchanged and the fresh second GetFriction row enters at "
                    "C1_CANDIDATE_PARTIAL; no C2 runtime grade is claimed for any row"
                ),
            },
            "counts": counts,
            "questionTypes": dict(
                Counter(row["questionType"] for row in rows["campaign-questions.tsv"])
            ),
            "policies": [
                "Every row is a measured mutation kill plus a MEASURED_STATIC pristine anchor and a focused parity test.",
                "REBUILD_READY requires an implementation owner and a focused parity test joined exactly to its campaign contract.",
                "Generation 31 raises only the fourteen measured C0_OPAQUE rows to C1_CANDIDATE_PARTIAL and never to a C2 runtime grade.",
                "The second GetFriction contract row is minted once as C-<sha256(entityKey|ownerPosix)[:16]>.",
            ],
            "outputs": {
                name: {**campaign.coverage.file_stamp(stage / name), "path": name}
                for name in campaign.OUTPUTS
            },
        }
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            campaign.verify(stage)
        os.replace(stage, out)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(seeded_stage, ignore_errors=True)
    return receipt


def verify_campaign(campaign_path: Path) -> dict:
    return campaign.verify(campaign_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser(
        "build", help="build Generation 31 from the Gen 30 parent and staged inputs"
    )
    build_parser.add_argument("--campaign", type=Path, required=True)
    build_parser.add_argument("--out", type=Path, required=True)
    build_parser.add_argument("--snapshot", type=Path)
    build_parser.add_argument("--prep", type=Path)
    build_parser.add_argument("--no-self-check", action="store_true")
    verify_parser = commands.add_parser(
        "verify", help="verify a built Generation 31 campaign"
    )
    verify_parser.add_argument("--campaign", type=Path, required=True)
    options = parser.parse_args(argv)
    if options.command == "build":
        build(
            options.campaign,
            options.out,
            snapshot=options.snapshot,
            prep=options.prep,
            _self_check=not options.no_self_check,
        )
        return 0
    verify_campaign(options.campaign)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
