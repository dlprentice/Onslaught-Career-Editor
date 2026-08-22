#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generation 32 authority builder: bulk reseat of the sealed static receipts.

Admits the 7,885 still-opaque ``SEALED_STATIC_RECEIPT`` rows of
``reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv``
(seal SHA-256 ``cfe90af3…``, byte-identical requirement) into the campaign
ledger in ONE Generation 32, carrying the literal-pinned Generation 31 v2
authority through the no-replay bridge.

Row application follows the Generation 11 C1 precedent
(``tools/re_gen73_reseal.py`` ~1010-1100) in every graded field: each
function's evidence states gain a ``CAMPAIGN_C1_STATIC_RECEIPT`` token,
``resolutionState=CANDIDATE_CONTRACT``, ``semanticGrade=C1_CANDIDATE_PARTIAL``;
the entity's existing OPEN contract row takes
``contractState=CANDIDATE_NEEDS_REFUTER``, ``semanticGrade=C1_CANDIDATE_PARTIAL``,
the seven bounded-static semantic fields from the receipt,
``refuterVerdict=UNSCORED``, its questionIds kept, and the receipt file appended
to ``evidenceRefs``.  One fresh adjudication row
(``refuterVerdict=UNSCORED``, ``terminalState=FUNCTION_BOUNDARY_C1_STATIC``) is
recorded per admitted row.

Deliberate divergence from the Gen 11 precedent: names are NOT written.  The
sealed closure carries dated 2026-08-10 inventory names; the live ledger holds
later corrections (measured 2026-08-22: 1,133 of the 7,885 admit rows differ —
see ``name-divergence.tsv`` beside the prep artifacts), and campaign policy
holds that coverage is execution evidence, never naming authority.  The reseat
admits the bounded static CONTRACT; name reconciliation stays a separate gated
lane.  Rows whose live grade is already C1 or stronger are skip-and-recorded in
the prep artifacts (Gen 11 precedent: never demote), so no terminal
rebuild-ready or runtime-measured row can move.

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
from pathlib import Path

import re_campaign as campaign  # noqa: E402


ADVANCE_KIND = "GENERATION32_STATIC_RECEIPT_RESEAT"
ADVANCE_SCHEMA = "bea.re.generation32-static-receipt-reseat-advance.v1"

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

PREP_RELATIVE = Path("local-lab/gen32-reseat-prep-20260821")
SNAPSHOT_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-31-prep-2026-08-17/snapshot-a"
)

CLOSURE_RELATIVE = (
    "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv"
)
CLOSURE_SHA256 = (
    "cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974"
)

SPECIMEN_SHA = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

SEALED_CLASS = "SEALED_STATIC_RECEIPT"
C1_OR_STRONGER = {"C1", "C1_CANDIDATE_PARTIAL", "C2_BOUNDED_RUNTIME"}

FUNCTION_EVIDENCE_TOKEN = "CAMPAIGN_C1_STATIC_RECEIPT"
CONTRACT_STATE_AFTER = "CANDIDATE_NEEDS_REFUTER"
GRADE_AFTER = "C1_CANDIDATE_PARTIAL"
ADJUDICATION_TERMINAL_STATE = "FUNCTION_BOUNDARY_C1_STATIC"

# The 51 newer standard receipts share the 15-column contracts.tsv shape;
# cgame51 is the older 16-column variant (calls_and_order,
# unresolved_and_cheapest_falsifier, metadata_action, proposed_comment);
# Weapon41 is the separately shaped comments.tsv receipt (closure report:
# "Standard contracts.tsv receipts / rows | 52 / 7,904" and "Separately
# shaped Weapon41 receipt rows | 41").
STANDARD_RECEIPT_COLUMNS = {
    "entry",
    "current_name",
    "body_bytes",
    "execution_state",
    "inputs",
    "returns",
    "state_writes",
    "calls_order",
    "bounded_static_contract",
    "confidence",
    "uncertainty_cheapest_falsifier",
    "grade_before",
    "grade_after",
    "name_or_comment_correction",
    "evidence_refs",
}
CGAME51_RECEIPT_COLUMNS = {
    "entry",
    "current_name",
    "body_bytes",
    "execution_state",
    "inputs",
    "returns",
    "state_writes",
    "calls_and_order",
    "bounded_static_contract",
    "confidence",
    "unresolved_and_cheapest_falsifier",
    "grade_before",
    "grade_after",
    "metadata_action",
    "proposed_comment",
    "evidence_refs",
}
WEAPON41_RECEIPT_NAME = "ghidra-weapon41-static-20260809-v1/comments.tsv"


def _load_receipt_rows(
    order_rows: list[dict[str, str]],
) -> dict[str, dict[str, dict[str, str]]]:
    """Load each referenced receipt file once, keyed by entry address.

    Every admit row must reproduce its receipt row's sealed content; the
    builder refuses any file whose columns do not match its known shape or
    whose row for an ordered entry is missing.
    """
    sources_seen = sorted({row["receiptSources"] for row in order_rows})
    loaded: dict[str, dict[str, dict[str, str]]] = {}
    for sources in sources_seen:
        path = _repo_root() / sources
        if not path.is_file():
            raise campaign.CampaignError(f"receipt file is absent: {sources}")
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            columns = set(reader.fieldnames or ())
            if columns in (STANDARD_RECEIPT_COLUMNS, CGAME51_RECEIPT_COLUMNS):
                rows = list(reader)
                by_entry = {
                    row["entry"].upper(): row for row in rows
                }
            elif sources.endswith(WEAPON41_RECEIPT_NAME):
                rows = list(reader)
                by_entry = {
                    row["address"].upper(): row for row in rows
                }
            else:
                raise campaign.CampaignError(
                    f"receipt file has an unknown column shape: {sources}"
                )
        if len(by_entry) != len(rows):
            raise campaign.CampaignError(
                f"receipt file repeats an entry address: {sources}"
            )
        loaded[sources] = by_entry
    return loaded


def _repo_root() -> Path:
    return campaign.REPO_ROOT


def _prep_default() -> Path:
    return _repo_root() / PREP_RELATIVE


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_tsv_rows(path: Path) -> list[dict[str, str]]:
    return campaign._read_tsv(path)


def _read_closure_sealed_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = [
            row
            for row in csv.DictReader(stream, delimiter="\t")
            if row.get("closureClass") == SEALED_CLASS
        ]
    seen: set[str] = set()
    for row in rows:
        va = row["entryVa"]
        if va in seen:
            raise campaign.CampaignError(
                f"closure TSV repeats SEALED_STATIC_RECEIPT entryVa: {va}"
            )
        seen.add(va)
    return rows


def _verify_closure_seal(path: Path) -> None:
    stamp = campaign.coverage.file_stamp(path)
    if stamp["sha256"] != CLOSURE_SHA256:
        raise campaign.CampaignError(
            "function-c1-closure-2026-08-11.tsv is not the sealed "
            f"cfe90af3… artifact: {stamp['sha256']}"
        )


def _load_order(prep: Path) -> list[dict[str, str]]:
    """Load the admit order joined to live Gen 31 entities (step-2 artifact)."""
    for name in (
        "gen32-order.tsv",
        "gen32-skipped-already-c1.tsv",
        "receipt-manifest.tsv",
    ):
        if not (prep / name).is_file():
            raise campaign.CampaignError(
                f"Generation 32 prep artifact {name} is absent from {prep}: "
                "run build_prep_artifacts.py first"
            )
    with (prep / "gen32-order.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows:
        raise campaign.CampaignError("gen32-order.tsv is empty")
    return rows


def _load_receipt_manifest(prep: Path) -> dict[str, dict[str, str]]:
    with (prep / "receipt-manifest.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return {row["receiptSources"]: row for row in rows}


def _receipt_ref(sources: str) -> str:
    return sources


def sources_is_weapon41(sources: str) -> bool:
    return sources.endswith(WEAPON41_RECEIPT_NAME)


def _adjudication_id(
    parent_ready_sha: str,
    order_row: dict[str, str],
    receipt_stamp: dict,
    overlay_identity: str,
) -> str:
    evidence_identity = "|".join(
        (
            order_row["entityKey"],
            order_row["contractId"],
            order_row["receiptSources"],
            order_row["receiptSha256"],
            overlay_identity,
        )
    )
    return "A-" + _sha256_text(
        "|".join((parent_ready_sha, evidence_identity, receipt_stamp["sha256"]))
    )[:16]


def _validate_order_against_sealed_closure(
    order_rows: list[dict[str, str]], closure_path: Path
) -> tuple[dict[str, dict[str, str]], int]:
    """Every admit row must reproduce a sealed closure row byte-for-byte."""
    _verify_closure_seal(closure_path)
    sealed_by_va = {
        row["entryVa"]: row
        for row in _read_closure_sealed_rows(closure_path)
    }
    resolved: dict[str, dict[str, str]] = {}
    for order_row in order_rows:
        va = order_row["entryVa"]
        sealed = sealed_by_va.get(va)
        if sealed is None:
            raise campaign.CampaignError(
                f"order row {order_row['order']} is not a sealed closure address: {va}"
            )
        if (
            order_row["closureClass"] != sealed["closureClass"]
            or order_row["currentName"] != sealed["trackedName"]
            or order_row["bodyBytes"] != sealed["bodyBytes"]
            or order_row["bodyDigest"] != sealed["bodyDigest"]
            or order_row["confidence"] != sealed["confidence"]
            or order_row["receiptSources"] != sealed["receiptSources"]
            or order_row["receiptSha256"] != sealed["receiptSha256"]
        ):
            raise campaign.CampaignError(
                f"order row {order_row['order']} drifted from the sealed closure row"
            )
        if va in resolved:
            raise campaign.CampaignError(f"duplicate order row for {va}")
        resolved[va] = sealed
    return resolved, len(sealed_by_va)


def _validate_receipts_on_disk(
    order_rows: list[dict[str, str]], manifest: dict[str, dict[str, str]]
) -> dict[str, dict]:
    stamps: dict[str, dict] = {}
    checked: dict[str, bool] = {}
    for order_row in order_rows:
        sources = order_row["receiptSources"]
        if sources in checked:
            continue
        pinned = manifest.get(sources)
        if pinned is None:
            raise campaign.CampaignError(
                f"receipt file absent from the step-2 manifest: {sources}"
            )
        if pinned["pinnedReceiptSha256"] != order_row["receiptSha256"]:
            raise campaign.CampaignError(
                f"manifest pin disagrees with the closure pin: {sources}"
            )
        path = _repo_root() / sources
        if not path.is_file():
            raise campaign.CampaignError(f"receipt file is absent: {sources}")
        stamp = campaign.coverage.file_stamp(path)
        if stamp["sha256"] != order_row["receiptSha256"]:
            raise campaign.CampaignError(
                f"receipt file changed on disk: {sources}"
            )
        stamps[sources] = stamp
        checked[sources] = True
    return stamps


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
                f"unexpected row change outside the reseat: {key_column}={row_id}"
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
                f"Generation 32 moved rows outside the reseat: {name}"
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


def _apply_reseat_rows(
    rows: dict[str, list[dict[str, str]]],
    order_rows: list[dict[str, str]],
    sealed_by_va: dict[str, dict[str, str]],
    receipt_rows: dict[str, dict[str, dict[str, str]]],
    parent_ready_sha: str,
    measured_date: str,
) -> dict:
    """Apply the Gen-11-C1-shaped row layer to the seeded ledgers."""
    functions = rows["campaign-functions.tsv"]
    contracts = rows["campaign-contracts.tsv"]
    adjudications = rows["campaign-adjudications.tsv"]

    before = {name: _snapshot_ids(value) for name, value in rows.items()}

    function_by_entity = {row["entityKey"]: row for row in functions}
    contract_by_id = {row["contractId"]: row for row in contracts}
    question_ids_by_entity: dict[str, set[str]] = {}
    for row in rows["campaign-questions.tsv"]:
        question_ids_by_entity.setdefault(row["entityKey"], set()).add(
            row["questionId"]
        )

    grade_movements: list[dict] = []
    adjudication_rows: list[dict] = []
    receipt_name_divergences: list[dict] = []
    changed_functions: set[str] = set()
    changed_contracts: set[str] = set()

    for order_row in sorted(order_rows, key=lambda item: int(item["order"])):
        entity_key = order_row["entityKey"]
        contract_id = order_row["contractId"]
        function = function_by_entity.get(entity_key)
        if function is None:
            raise campaign.CampaignError(
                f"order {order_row['order']}: entity is absent from the "
                "seeded function ledger"
            )
        contract = contract_by_id.get(contract_id)
        if contract is None or contract["entityKey"] != entity_key:
            raise campaign.CampaignError(
                f"order {order_row['order']}: base contract is absent or "
                "names another entity"
            )
        if function["semanticGrade"] in C1_OR_STRONGER:
            raise campaign.CampaignError(
                f"order {order_row['order']}: live grade moved past OPAQUE "
                "since the step-2 join; re-run the prep artifacts"
            )
        if contract["contractState"] != "OPEN":
            raise campaign.CampaignError(
                f"order {order_row['order']}: base contract is not OPEN"
            )
        if contract["semanticGrade"] not in {"", "C0_OPAQUE"}:
            raise campaign.CampaignError(
                f"order {order_row['order']}: base contract is already graded"
            )

        sealed = sealed_by_va[order_row["entryVa"]]
        receipt_sources = order_row["receiptSources"]
        # The row's own sealed-receipt stamp, measured against the on-disk
        # receipt by the step-2 manifest join and re-verified by
        # _validate_receipts_on_disk above — never hand-typed.
        receipt_stamp = {"sha256": order_row["receiptSha256"]}
        entry_key = order_row["entryVa"].upper()
        if sources_is_weapon41(receipt_sources):
            weapon41 = receipt_rows[receipt_sources][entry_key]
            comment = str(weapon41.get("comment", ""))
            if "HYPOTHESIS ONLY" not in comment:
                raise campaign.CampaignError(
                    f"order {order_row['order']}: Weapon41 comment is not the "
                    "sealed hypothesis envelope"
                )
            expected_name = str(weapon41.get("expectedName", ""))
            if not expected_name.startswith("HYP__"):
                raise campaign.CampaignError(
                    f"order {order_row['order']}: Weapon41 expectedName is not "
                    "the HYP__ disposable provenance name"
                )
            execution_state = "COVERED"
            inputs = (
                "displayed prototype arguments only; hidden register/"
                "caller-stack values remain open"
            )
            returns = (
                "displayed direct return only; exact status/error state "
                "remains bounded by the pinned comment"
            )
            state_writes = (
                "visible explicit memory-destination sites are not enumerated "
                "by this receipt shape; the pinned comment bounds the claim"
            )
            calls_order = (
                "static transfer sites are not enumerated by this receipt "
                "shape; the pinned comment bounds the claim"
            )
            bounded_static_contract = comment
            confidence = "MEDIUM_STATIC"
            falsifier = (
                "Exact original source ownership, complete heap/object/event "
                "layouts and aliases, allocation provenance/lifetime/failure "
                "semantics, callback and virtual targets, synchronization, "
                "hidden ABI, runtime causality, source equivalence, patch "
                "behavior, and Godot parity remain open. Cheapest falsifier: "
                "one copied-runtime call with pinned receiver and exact "
                "inputs, recording transfer targets/order, exact return bits, "
                "and before/after hashes of named global ranges."
            )
        else:
            standard = receipt_rows[receipt_sources][entry_key]
            # The dated receipts may carry the closure's disposable-project
            # label (HYP__..., slot-style) instead of the reviewed tracked
            # name; the closure report records both columns and states the
            # HYP__ names "are kept as provenance only". Receipt identity is
            # already enforced byte-for-byte by the per-row SHA-256 join, and
            # no receipt name ever enters the ledger (naming authority stays
            # untouched), so a name divergence is recorded, not refused.
            if standard["current_name"] != sealed["trackedName"]:
                receipt_name_divergences.append(
                    {
                        "order": order_row["order"],
                        "entryVa": order_row["entryVa"],
                        "receiptName": standard["current_name"],
                        "closureTrackedName": sealed["trackedName"],
                    }
                )
            execution_state = standard["execution_state"]
            inputs = standard["inputs"]
            returns = standard["returns"]
            state_writes = standard["state_writes"]
            calls_order = standard.get(
                "calls_order", standard.get("calls_and_order", "")
            )
            bounded_static_contract = standard["bounded_static_contract"]
            confidence = standard["confidence"]
            falsifier = standard.get(
                "uncertainty_cheapest_falsifier",
                standard.get("unresolved_and_cheapest_falsifier", ""),
            )

        # Naming authority is deliberately NOT touched: measured 2026-08-22,
        # 1,133 of the 7,885 admit rows carry a closure-era name that differs
        # from the live ledger (local-lab/gen32-reseat-prep-20260821/
        # name-divergence.tsv), including later proven corrections the dated
        # closure name would regress.  Campaign policy: coverage is execution
        # evidence, never naming authority.  The reseat admits the bounded
        # static CONTRACT; name reconciliation stays a separate gated lane.

        # --- function row (Gen 11 C1 shape, tools/re_gen73_reseal.py ~1055,
        # minus the name writes for the reason recorded above) ---
        if FUNCTION_EVIDENCE_TOKEN not in [
            token
            for token in function.get("evidenceStates", "").split(";")
            if token
        ]:
            function["evidenceStates"] = campaign._append_state(
                function.get("evidenceStates", ""), FUNCTION_EVIDENCE_TOKEN
            )
        function["resolutionState"] = "CANDIDATE_CONTRACT"
        grade_before_function = function["semanticGrade"]
        function["semanticGrade"] = GRADE_AFTER
        # The Gen 11 precedent keeps the entity's existing structural
        # cheapestFalsifier on the function row; the receipt's own can-fail
        # falsifier lands on the contract row below.
        function["lastMeasurementDate"] = measured_date
        changed_functions.add(entity_key)
        if grade_before_function != GRADE_AFTER:
            grade_movements.append(
                {
                    "entityKey": entity_key,
                    "ledger": "functions",
                    "semanticGradeBefore": grade_before_function,
                    "semanticGradeAfter": GRADE_AFTER,
                }
            )

        # --- contract row (existing OPEN row per entity) ---
        grade_before_contract = contract["semanticGrade"]
        contract["contractState"] = CONTRACT_STATE_AFTER
        contract["semanticGrade"] = GRADE_AFTER
        contract["receiver"] = (
            "displayed prototype receiver; hidden register/caller-stack "
            f"values remain open ({execution_state} execution state)"
        )
        contract["inputs"] = inputs
        contract["returns"] = returns
        contract["writes"] = state_writes
        contract["sideEffects"] = calls_order
        contract["preconditions"] = bounded_static_contract
        contract["failureModes"] = (
            f"confidence {confidence}; exact runtime causality, "
            "allocation/lifetime semantics, and source equivalence remain open"
        )
        contract["refuterVerdict"] = "UNSCORED"
        contract["cheapestFalsifier"] = falsifier
        question_ids_sorted = sorted(
            question_ids_by_entity.get(entity_key, set())
        )
        contract["questionIds"] = ";".join(question_ids_sorted)
        contract["evidenceRefs"] = campaign._append_state(
            contract.get("evidenceRefs", ""),
            _receipt_ref(receipt_sources),
        )
        contract["lastMeasurementDate"] = measured_date
        changed_contracts.add(contract_id)
        if grade_before_contract != GRADE_AFTER:
            grade_movements.append(
                {
                    "entityKey": entity_key,
                    "contractId": contract_id,
                    "ledger": "contracts",
                    "semanticGradeBefore": grade_before_contract,
                    "semanticGradeAfter": GRADE_AFTER,
                }
            )

        # --- one fresh adjudication per row ---
        overlay_identity = "|".join(
            (
                function["currentName"],
                function["resolutionState"],
                function["semanticGrade"],
                contract["contractState"],
                contract["semanticGrade"],
            )
        )
        adjudication_id = _adjudication_id(
            parent_ready_sha,
            order_row,
            receipt_stamp,
            overlay_identity,
        )
        if any(
            row.get("adjudicationId") == adjudication_id
            for row in adjudications
        ):
            raise campaign.CampaignError(
                f"order {order_row['order']}: adjudication already exists"
            )
        adjudications.append(
            {
                "adjudicationId": adjudication_id,
                "baseContractId": contract_id,
                "entityKey": entity_key,
                "overlaySchema": ADVANCE_SCHEMA,
                "overlayReadySha256": receipt_stamp["sha256"],
                "questionIdsAddressed": contract["questionIds"],
                "refuterVerdict": "UNSCORED",
                "refuterEvidenceSha256": receipt_stamp["sha256"],
                "semanticPromotionApplied": "true",
                "terminalState": ADJUDICATION_TERMINAL_STATE,
                "successorQuestionIds": contract["questionIds"],
                "remainingUncertainty": contract["failureModes"],
                "measuredAtUtc": measured_date,
            }
        )
        adjudication_rows.append(adjudications[-1])

    after = {name: _snapshot_ids(value) for name, value in rows.items()}
    receipt_name_divergences.sort(key=lambda item: int(item["order"]))
    return {
        "gradeMovements": grade_movements,
        "adjudicationRows": adjudication_rows,
        "receiptNameDivergences": receipt_name_divergences,
        "changedFunctions": changed_functions,
        "changedContracts": changed_contracts,
        "before": before,
        "after": after,
    }


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
            f"refusing existing Generation 32 destination: {out}"
        )
    if _verified_parent_receipt is None:
        parent_receipt = campaign._verify_generation31_campaign_carry(parent)
    else:
        parent_receipt = _verified_parent_receipt
    if parent_receipt.get("generation") != 31:
        raise campaign.CampaignError(
            "Generation 32 requires the canonical Generation 31 parent"
        )
    if (
        parent_receipt.get("_carryBridge")
        != "LITERAL_PINNED_SEALED_AUTHORITY_GENERATION31_NO_REPLAY"
    ):
        raise campaign.CampaignError(
            "Generation 32 requires the literal-pinned Generation 31 bridge"
        )
    parent_ready = campaign.coverage.file_stamp(parent / "campaign.ready.json")

    closure_path = _repo_root() / CLOSURE_RELATIVE
    order_rows = _load_order(prep_root)
    manifest = _load_receipt_manifest(prep_root)
    sealed_by_va, sealed_total = _validate_order_against_sealed_closure(
        order_rows, closure_path
    )
    # The skip set is a step-2 artifact joined against the live Gen 31 ledger;
    # refuse any drift rather than silently re-deciding which rows are admit
    # and which are already C1-or-stronger (Gen 11 precedent).
    with (prep_root / "gen32-skipped-already-c1.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        skipped_rows = list(csv.DictReader(stream, delimiter="\t"))
    if len(order_rows) + len(skipped_rows) != 7945:
        raise campaign.CampaignError(
            "order rows plus skip-and-record rows do not reproduce the "
            f"sealed 7,945-row population: {len(order_rows)} + {len(skipped_rows)}"
        )
    if sealed_total != 7945:
        raise campaign.CampaignError(
            f"closure TSV carries an unexpected sealed population: {sealed_total}"
        )
    for skip_row in skipped_rows:
        va = skip_row["entryVa"]
        if va in sealed_by_va:
            raise campaign.CampaignError(
                f"an entry appears in both the admit order and the skips: {va}"
            )
    _validate_receipts_on_disk(order_rows, manifest)
    receipt_rows = _load_receipt_rows(order_rows)

    seeded_stage = Path(
        tempfile.mkdtemp(prefix=".gen32-seeded-", dir=out.parent or Path.cwd())
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

    # The step-2 join bound every order row to a live entity; re-check that
    # binding against the freshly seeded ledgers before applying anything.
    seeded_functions = {row["entityKey"]: row for row in rows["campaign-functions.tsv"]}
    seeded_contracts = {row["contractId"]: row for row in rows["campaign-contracts.tsv"]}
    for order_row in order_rows:
        function = seeded_functions.get(order_row["entityKey"])
        contract = seeded_contracts.get(order_row["contractId"])
        if function is None or function["entryVa"] != order_row["entryVa"]:
            raise campaign.CampaignError(
                f"order {order_row['order']}: seeded entity drifted from the join"
            )
        if contract is None or contract["entityKey"] != order_row["entityKey"]:
            raise campaign.CampaignError(
                f"order {order_row['order']}: seeded contract drifted from the join"
            )

    # Measured-date provenance: the sealed closure's own date, deterministic.
    measured_date = "2026-08-11"

    accounting = _apply_reseat_rows(
        rows,
        order_rows,
        sealed_by_va,
        receipt_rows,
        parent_ready["sha256"],
        measured_date,
    )

    changed_ids = {
        "campaign-functions.tsv": set(accounting["changedFunctions"]),
        "campaign-residuals.tsv": set(),
        "campaign-questions.tsv": set(),
        "campaign-contracts.tsv": set(accounting["changedContracts"]),
        "campaign-scenarios.tsv": set(),
        "campaign-levers.tsv": set(),
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
            "generatedAtUtc": datetime_now_iso(),
            "generation": 32,
            "parentCampaign": {
                "path": str(parent.resolve()),
                "ready": {**parent_ready, "path": "campaign.ready.json"},
            },
            "sourceSnapshot": seeded_receipt["sourceSnapshot"],
            "advance": {
                "kind": ADVANCE_KIND,
                "schema": ADVANCE_SCHEMA,
                "parentSchema": campaign.SCHEMA,
                "carryVerification": parent_receipt.get("_carryBridge"),
                "snapshot": {
                    "path": str(snapshot_path.resolve()),
                    "schema": seeded_receipt["sourceSnapshot"]["schema"],
                    "coverageSetSha256": seeded_receipt["sourceSnapshot"][
                        "coverageSetSha256"
                    ],
                },
                "prepRoot": {"path": str(prep_root.resolve())},
                "reseed": seeded_receipt["advance"],
                "sealedClosure": {
                    "path": CLOSURE_RELATIVE,
                    "sha256": CLOSURE_SHA256,
                    "sealedStaticReceiptRows": 7945,
                    "skippedAlreadyC1OrStronger": 60,
                    "admittedRows": len(order_rows),
                },
                "rows": [
                    {
                        "order": order_row["order"],
                        "entityKey": order_row["entityKey"],
                        "contractId": order_row["contractId"],
                        "entryVa": order_row["entryVa"],
                        "receiptSources": order_row["receiptSources"],
                        "receiptSha256": order_row["receiptSha256"],
                        "refuterVerdict": "UNSCORED",
                        "terminalState": ADJUDICATION_TERMINAL_STATE,
                    }
                    for order_row in sorted(
                        order_rows, key=lambda item: int(item["order"])
                    )
                ],
                "gradeMovements": accounting["gradeMovements"],
                "receiptNameDivergences": accounting["receiptNameDivergences"],
                "zeroCollateral": collateral,
                "semanticGradePolicy": (
                    "Every admitted row raises OPAQUE/C0_OPAQUE to "
                    "C1_CANDIDATE_PARTIAL behind an UNSCORED refuter, exactly "
                    "the Generation 11 C1 candidate boundary; the 60 rows "
                    "already at C1_CANDIDATE_PARTIAL or stronger were "
                    "skip-and-recorded in the step-2 prep and no terminal "
                    "rebuild-ready or runtime-measured row moved"
                ),
                "namingPolicy": (
                    "Names are deliberately untouched: coverage is execution "
                    "evidence, never naming authority. The sealed closure's "
                    "dated 2026-08-10 inventory names differ from later live "
                    "corrections on 1,133 of the 7,885 admit rows (measured, "
                    "name-divergence.tsv in the prep root); writing them "
                    "would regress proven identities. Name reconciliation is "
                    "a separate gated lane."
                ),
            },
            "counts": counts,
            "questionTypes": dict(
                Counter(
                    row["questionType"] for row in rows["campaign-questions.tsv"]
                )
            ),
            "policies": [
                "Coverage is execution evidence, never naming authority.",
                "Every open semantic row remains OPAQUE until a reviewed contract earns a higher grade.",
                "UNSCORED and INSTRUMENT_NEEDED are valid accounting outcomes.",
                "This campaign never mutates Ghidra or the pristine specimen.",
                "Every function has one contract row; UNKNOWN and C0_OPAQUE are required until evidence closes them.",
                "Every nonterminal function and exact .text residual has at least one explicit open question.",
                "Rebuild mappings remain UNMAPPED until evidence and a focused parity test make them REBUILD_READY.",
                "Fresh snapshot rows remain structural truth; progress carries only across exact specimen-bound entity identities.",
                "Verified closed questions, successor lineage, adjudications, and supersessions cannot silently reopen on reseed.",
                "Function, residual, contract, question, adjudication, and supersession progress requires campaign provenance; stale identities are counted and skipped rather than transferred.",
                "The sealed static receipts enter once as bounded C1 candidates with their own cheapest falsifiers; static closure claims no runtime causality, source identity, or rebuild parity.",
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


def datetime_now_iso() -> str:
    """Wall clock goes ONLY into the staging READY; the frozen replay
    normalizes it away (see _normalized_campaign_field)."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def verify_campaign(campaign_path: Path) -> dict:
    return campaign.verify(campaign_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser(
        "build", help="build Generation 32 from the Gen 31 parent and staged inputs"
    )
    build_parser.add_argument("--campaign", type=Path, required=True)
    build_parser.add_argument("--out", type=Path, required=True)
    build_parser.add_argument("--snapshot", type=Path)
    build_parser.add_argument("--prep", type=Path)
    build_parser.add_argument("--no-self-check", action="store_true")
    verify_parser = commands.add_parser(
        "verify", help="verify a built Generation 32 campaign"
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
