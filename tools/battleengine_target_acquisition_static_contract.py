#!/usr/bin/env python3
"""Validate the public BattleEngine target-acquisition static contract.

The gate consumes tracked public-safe JSON/Markdown and current correction
records. It does not launch BEA, invoke Ghidra, read process memory, or write an
evidence artifact.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "reverse-engineering"
    / "game-mechanics"
    / "battleengine-target-acquisition-static-contract-v1.json"
)
DOC_PATH = CONTRACT_PATH.with_suffix(".md")

CORRECTION_PLAN_PATH = "reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json"
CORRECTION_DECISIONS_PATH = "reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl"
HANDLE_LOCKS_DOC_PATH = "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.md"
NEAREST_HELPER_DOC_PATH = "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__SelectNearestForwardTargetFromGlobalSet.md"
LOCK_ENTRY_DOC_PATH = "reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__AddProjectile.md"
UNIT_STATIC_CONTRACT_PATH = "reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-contract.md"
SOURCE_AUDIT_PATH = "reverse-engineering/source-code/reference-submodule-audit-2026-07-12.md"
SOURCE_PATH = "references/Onslaught/BattleEngine.cpp"

REQUIRED_EVIDENCE_PATHS = (
    CORRECTION_PLAN_PATH,
    CORRECTION_DECISIONS_PATH,
    HANDLE_LOCKS_DOC_PATH,
    NEAREST_HELPER_DOC_PATH,
    LOCK_ENTRY_DOC_PATH,
    UNIT_STATIC_CONTRACT_PATH,
    SOURCE_AUDIT_PATH,
)

SCHEMA_VERSION = "battleengine-target-acquisition-static-contract.v1"
CONTRACT_ID = "M2.3-target-acquisition-static-contract"
STATUS = "accepted-static-contract-not-runtime-proof"
SOURCE_PIN = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"

EVIDENCE_HIERARCHY = (
    "reviewed-retail-static",
    "saved-retail-structure",
    "pinned-source-hypothesis",
    "runtime-required",
)

CANONICAL_ANCHORS = (
    {
        "address": "0x00406560",
        "currentRetailName": "CBattleEngine__HandleLocks",
        "retailNameStatus": "reviewed-current",
        "sourceCandidate": "CBattleEngine::HandleLocks",
        "sourceCandidateStatus": "reviewed-source-aligned-retail-static",
    },
    {
        "address": "0x00406da0",
        "currentRetailName": "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
        "retailNameStatus": "saved-descriptive",
        "sourceCandidate": "CBattleEngine::GetClosestLockableUnit",
        "sourceCandidateStatus": "hypothesis-only",
    },
    {
        "address": "0x00406fc0",
        "currentRetailName": "CBattleEngine__AddProjectile",
        "retailNameStatus": "saved-dependent-name-semantic-role-superseded",
        "sourceCandidate": "CBattleEngine::StartLock",
        "sourceCandidateStatus": "hypothesis-only",
    },
)

LOCK_PATH_ROWS = (
    ("move-calls-handle-locks", "reviewed-retail-static"),
    ("active-part-weapon-selection", "reviewed-retail-static"),
    ("existing-lock-pruning", "reviewed-retail-static"),
    ("maximum-lock-and-readiness-gates", "reviewed-retail-static"),
    ("direct-proximity-sequence-modes", "reviewed-retail-static"),
    ("lock-entry-creation-call-shape", "saved-retail-structure"),
)

LOCK_PATH_CLAIMS = (
    "The sole reviewed caller is CBattleEngine__Move, which enters 0x00406560 with the BattleEngine pointer and no explicit stack arguments.",
    "The helper selects the current JetPart or WalkerPart weapon from the BattleEngine state before maintaining or acquiring locks.",
    "The helper removes null, dying, or out-of-deflection entries from the tracked lock set at BattleEngine +0x294.",
    "New acquisition is bounded by current-weapon fire readiness and maximum-lock gates; numeric thresholds and runtime timing remain unproven.",
    "The body contains distinct direct, proximity, and sequence lock-mode paths without establishing their live selection or gameplay outcomes.",
    "Four calls from HandleLocks pass a target, lock-time value, and direct-lock flag to 0x00406fc0; this is lock-entry creation structure, not projectile emission proof.",
)

CANDIDATE_ORDER_ROWS = (
    ("global-candidate-set-traversal", "saved-retail-structure"),
    ("side-compatibility-gate", "saved-retail-structure"),
    ("weapon-profile-eligibility-gate", "saved-retail-structure"),
    ("distance-and-nearest-so-far-gate", "saved-retail-structure"),
    ("forward-deflection-gate", "saved-retail-structure"),
    ("existing-lock-exclusion", "saved-retail-structure"),
    ("candidate-return-or-null", "saved-retail-structure"),
)

CANDIDATE_ORDER_CLAIMS = (
    "0x00406da0 traverses the global candidate set rooted at DAT_008550d0.",
    "Each candidate first passes an address-bound side/team compatibility helper.",
    "The candidate then passes the saved weapon/profile target-mask eligibility helper.",
    "Squared distance from the caller-supplied origin is checked against a scaled range and the current nearest-so-far value.",
    "A BattleEngine-relative normalized direction is compared with a cosine-derived deflection threshold.",
    "The candidate is excluded when it already appears in the tracked set at BattleEngine +0x294.",
    "The helper returns the best retained candidate pointer or null when none survives.",
)

SOURCE_HYPOTHESES = (
    "stealth-adjusted-effective-lock-range",
    "helper-00406da0-is-get-closest-lockable-unit",
    "helper-00406fc0-is-start-lock",
)

PROVES_CLAIMS = (
    "the reviewed retail-static identity and bounded lock-maintenance phases of CBattleEngine__HandleLocks at 0x00406560",
    "the address-bound candidate-filter ordering retained by the saved 0x00406da0 helper body",
    "the target, lock-time, and direct-lock call shape of the saved 0x00406fc0 dependent helper",
)

DOES_NOT_PROVE_CLAIMS = (
    "runtime target choice",
    "lock timing",
    "Core behavior",
    "exact helper source identity",
    "the retail semantic meaning of the source stealth expression",
    "projectile emission or weapon firing",
    "exact object or field layouts",
    "gameplay outcomes",
    "visual behavior",
    "rebuild parity",
)

FALSE_GUARDS = (
    "runtimeObservation",
    "beaLaunch",
    "debuggerAttachment",
    "ghidraMutation",
    "executablePatching",
    "targetChoiceCausalityProven",
    "lockTimingProven",
    "exactLayoutProven",
    "exactHelperSourceIdentityProven",
    "coreImplementation",
    "godotImplementation",
    "visualProof",
    "rebuildParityProven",
    "releasePublicationOccurred",
)
ZERO_GUARDS = ("runtimeObservationRows", "coreImplementationRows")

FORBIDDEN_MARKDOWN_CLAIMS = (
    "accepted runtime contract",
    "runtime target choice is proven",
    "runtime target choice proven",
    "lock timing is proven",
    "core behavior is proven",
    "core behavior accepted",
    "exact helper source identity is proven",
    "exact helper source identity proven",
    "rebuild parity is proven",
    "rebuild parity proven",
)

DOCUMENT_TOKEN_REQUIREMENTS = {
    HANDLE_LOCKS_DOC_PATH: ("CBattleEngine__HandleLocks", "lock-entry creation"),
    NEAREST_HELPER_DOC_PATH: ("CBattleEngine::GetClosestLockableUnit", "hypothesis-only"),
    LOCK_ENTRY_DOC_PATH: ("saved Ghidra", "lock-entry creation", "CBattleEngine::StartLock"),
    UNIT_STATIC_CONTRACT_PATH: (
        "battleengine-target-acquisition-static-contract-v1.json",
        "CBattleEngine__HandleLocks",
    ),
    SOURCE_AUDIT_PATH: (SOURCE_PIN, "Stuart source suggests architecture"),
}

DOCUMENT_FORBIDDEN_CLAIMS = {
    HANDLE_LOCKS_DOC_PATH: (
        "current live-ghidra name: `cbattleengine__updateautotargetsetandfireprojectiles`",
        "runtime target acquisition is proven",
        "projectile emission is proven",
    ),
    NEAREST_HELPER_DOC_PATH: (
        "runtime target-choice behavior is proven",
        "source candidate status: `accepted",
        "saved retail name: `cbattleengine::getclosestlockableunit`",
    ),
    LOCK_ENTRY_DOC_PATH: (
        "runtime projectile emission is proven",
        "projectile emission is proven",
        "current static semantic role: projectile",
        "source candidate status: `accepted",
    ),
}

SOURCE_TOKEN_REQUIREMENTS = (
    "CBattleEngine::HandleLocks()",
    "CBattleEngine::GetClosestLockableUnit(",
    "CBattleEngine::StartLock(",
)


class ContractError(ValueError):
    """Raised when the static contract or its tracked authority is incoherent."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ContractError(f"{label} keys mismatch: expected {sorted(expected)}, got {sorted(value)}")


def _safe_relative(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{label} must be a non-empty relative path")
    posix = Path(value)
    windows = PureWindowsPath(value)
    has_uri_or_drive_prefix = bool(windows.drive) or bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value))
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or has_uri_or_drive_prefix
        or ".." in posix.parts
        or ".." in windows.parts
    ):
        raise ContractError(f"{label} contains an absolute or escaping path: {value}")
    return value


def _source_revision(source_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError(f"cannot resolve initialized source revision: {exc}") from exc
    revision = result.stdout.strip().lower()
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ContractError("cannot resolve initialized source revision")
    return revision


def _source_text_at_revision(source_root: Path, revision: str, relative_path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_root), "show", f"{revision}:{relative_path}"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError(f"cannot read pinned source commit: {exc}") from exc
    if result.returncode != 0:
        raise ContractError("cannot read pinned source commit")
    return result.stdout


def _validate_rows(
    value: Any,
    expected: Sequence[tuple[str, str]],
    expected_claims: Sequence[str],
    label: str,
) -> list[Mapping[str, Any]]:
    if not isinstance(value, list) or len(value) != len(expected):
        raise ContractError(f"{label} must contain exactly {len(expected)} rows")
    rows: list[Mapping[str, Any]] = []
    for ordinal, (raw, (expected_id, expected_tier)) in enumerate(zip(value, expected), start=1):
        row = _mapping(raw, f"{label}[{ordinal}]")
        _exact_keys(row, {"ordinal", "id", "evidenceTier", "claim"}, f"{label}[{ordinal}]")
        if row["ordinal"] != ordinal or row["id"] != expected_id or row["evidenceTier"] != expected_tier:
            raise ContractError(f"{label} canonical order/tier mismatch at ordinal {ordinal}")
        if row["claim"] != expected_claims[ordinal - 1]:
            raise ContractError(f"{label} canonical claim mismatch at ordinal {ordinal}")
        rows.append(row)
    return rows


def _load_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        return _mapping(json.loads(path.read_text(encoding="utf-8")), label)
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read {label}: {path}: {exc}") from exc


def _validate_authority(root: Path) -> bool:
    for relative in REQUIRED_EVIDENCE_PATHS:
        path = root / _safe_relative(relative, "evidencePaths")
        if not path.is_file():
            raise ContractError(f"missing evidence path: {relative}")

    plan = _load_json(root / CORRECTION_PLAN_PATH, "correction plan")
    records = plan.get("records")
    if not isinstance(records, list):
        raise ContractError("correction plan records must be a list")
    address_records = [
        row for row in records if isinstance(row, dict) and row.get("address") == "0x00406560"
    ]
    if len(address_records) != 1:
        raise ContractError("correction plan must contain exactly one 0x00406560 record")
    accepted = address_records[0]
    if not (
        accepted.get("classification") == "confirmed-apply"
        and accepted.get("correctedName") == "CBattleEngine__HandleLocks"
        and accepted.get("correctedSignature") == "void __fastcall CBattleEngine__HandleLocks(void * this)"
    ):
        raise ContractError("correction plan lacks the exact accepted 0x00406560 HandleLocks record")

    decision_rows: list[Mapping[str, Any]] = []
    try:
        for line in (root / CORRECTION_DECISIONS_PATH).read_text(encoding="utf-8").splitlines():
            if line.strip():
                decision_rows.append(_mapping(json.loads(line), "correction decision row"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read correction decisions: {exc}") from exc
    address_decisions = [row for row in decision_rows if row.get("address") == "0x00406560"]
    if len(address_decisions) != 1 or address_decisions[0].get("classification") != "confirmed-apply":
        raise ContractError("correction decisions lack one accepted 0x00406560 row")

    for relative, tokens in DOCUMENT_TOKEN_REQUIREMENTS.items():
        text = (root / relative).read_text(encoding="utf-8", errors="replace")
        missing = [token for token in tokens if token not in text]
        if missing:
            raise ContractError(f"authority document {relative} missing tokens: {missing}")
        normalized_text = re.sub(r"\s+", " ", text.casefold())
        forbidden = [
            phrase
            for phrase in DOCUMENT_FORBIDDEN_CLAIMS.get(relative, ())
            if phrase in normalized_text
        ]
        if forbidden:
            raise ContractError(
                f"authority document {relative} contains forbidden claim text: {forbidden}"
            )

    source_path = root / SOURCE_PATH
    if not source_path.is_file():
        return False
    revision = _source_revision(source_path.parent)
    if revision != SOURCE_PIN:
        raise ContractError(
            f"initialized pinned source revision mismatch: expected {SOURCE_PIN}, got {revision}"
        )
    source_text = _source_text_at_revision(source_path.parent, SOURCE_PIN, "BattleEngine.cpp")
    missing_source = [token for token in SOURCE_TOKEN_REQUIREMENTS if token not in source_text]
    if missing_source:
        raise ContractError(f"pinned source commit is missing expected function tokens: {missing_source}")
    return True


def _markdown_tokens(payload: Mapping[str, Any]) -> list[str]:
    anchors = payload["anchors"]
    lock_rows = payload["lockPathRows"]
    candidate_rows = payload["candidateOrder"]
    hypotheses = payload["sourceHypotheses"]
    boundary = payload["claimBoundary"]
    return [
        str(payload["schemaVersion"]),
        str(payload["contractId"]),
        SOURCE_PIN,
        *(str(row["address"]) for row in anchors),
        *(str(row["currentRetailName"]) for row in anchors),
        *(str(row["sourceCandidate"]) for row in anchors),
        *(str(row["id"]) for row in lock_rows),
        *(str(row["claim"]) for row in lock_rows),
        *(str(row["id"]) for row in candidate_rows),
        *(str(row["claim"]) for row in candidate_rows),
        *(str(row["id"]) for row in hypotheses),
        *EVIDENCE_HIERARCHY,
        *(str(item) for item in boundary["proves"]),
        *(str(item) for item in boundary["doesNotProve"]),
    ]


def validate_contract(
    payload: Mapping[str, Any],
    markdown: str,
    *,
    root: Path = ROOT,
) -> dict[str, object]:
    root_map = _mapping(payload, "contract")
    _exact_keys(
        root_map,
        {
            "schemaVersion",
            "contractId",
            "status",
            "evidenceHierarchy",
            "sourceReference",
            "anchors",
            "lockPathRows",
            "candidateOrder",
            "sourceHypotheses",
            "evidencePaths",
            "guardSummary",
            "claimBoundary",
        },
        "contract",
    )
    if root_map["schemaVersion"] != SCHEMA_VERSION:
        raise ContractError("schemaVersion mismatch")
    if root_map["contractId"] != CONTRACT_ID:
        raise ContractError("contractId mismatch")
    if root_map["status"] != STATUS:
        raise ContractError("status mismatch")
    if root_map["evidenceHierarchy"] != list(EVIDENCE_HIERARCHY):
        raise ContractError("evidenceHierarchy mismatch")

    source = _mapping(root_map["sourceReference"], "sourceReference")
    if source != {
        "repository": "dlprentice/Onslaught",
        "commit": SOURCE_PIN,
        "path": "BattleEngine.cpp",
        "role": "pinned-source-hypothesis-only",
    }:
        raise ContractError("sourceReference mismatch")

    anchors = root_map["anchors"]
    if anchors != [dict(item) for item in CANONICAL_ANCHORS]:
        raise ContractError("canonical anchors mismatch")

    lock_rows = _validate_rows(
        root_map["lockPathRows"], LOCK_PATH_ROWS, LOCK_PATH_CLAIMS, "lockPathRows"
    )
    candidate_rows = _validate_rows(
        root_map["candidateOrder"],
        CANDIDATE_ORDER_ROWS,
        CANDIDATE_ORDER_CLAIMS,
        "candidateOrder",
    )

    hypotheses = root_map["sourceHypotheses"]
    if not isinstance(hypotheses, list) or len(hypotheses) != len(SOURCE_HYPOTHESES):
        raise ContractError("sourceHypotheses count mismatch")
    for expected_id, raw in zip(SOURCE_HYPOTHESES, hypotheses):
        row = _mapping(raw, "sourceHypotheses row")
        _exact_keys(row, {"id", "evidenceTier", "retailRuntimeAccepted"}, "sourceHypotheses row")
        if row != {
            "id": expected_id,
            "evidenceTier": "pinned-source-hypothesis",
            "retailRuntimeAccepted": False,
        }:
            raise ContractError(f"sourceHypotheses mismatch for {expected_id}")

    paths = root_map["evidencePaths"]
    if paths != list(REQUIRED_EVIDENCE_PATHS):
        raise ContractError("evidencePaths must equal the canonical public-safe evidence list")
    for index, value in enumerate(paths):
        _safe_relative(value, f"evidencePaths[{index}]")

    guards = _mapping(root_map["guardSummary"], "guardSummary")
    _exact_keys(guards, set(FALSE_GUARDS + ZERO_GUARDS), "guardSummary")
    if any(guards[key] is not False for key in FALSE_GUARDS):
        raise ContractError("guardSummary false guards must remain exactly false")
    if any(type(guards[key]) is not int or guards[key] != 0 for key in ZERO_GUARDS):
        raise ContractError("guardSummary zero counters must remain numeric zero")

    boundary = _mapping(root_map["claimBoundary"], "claimBoundary")
    _exact_keys(boundary, {"proves", "doesNotProve"}, "claimBoundary")
    if boundary != {
        "proves": list(PROVES_CLAIMS),
        "doesNotProve": list(DOES_NOT_PROVE_CLAIMS),
    }:
        raise ContractError("claimBoundary must equal the canonical bounded claims")

    if not isinstance(markdown, str) or not markdown.strip():
        raise ContractError("Markdown contract must be non-empty")
    normalized_markdown = re.sub(r"\s+", " ", markdown)
    missing_markdown = [
        token
        for token in _markdown_tokens(root_map)
        if re.sub(r"\s+", " ", token) not in normalized_markdown
    ]
    if missing_markdown:
        raise ContractError(f"Markdown contract missing tokens: {missing_markdown}")
    lowered_markdown = re.sub(r"\s+", " ", markdown.casefold())
    forbidden_markdown = [
        phrase for phrase in FORBIDDEN_MARKDOWN_CLAIMS if phrase in lowered_markdown
    ]
    if forbidden_markdown:
        raise ContractError(f"Markdown contract contains forbidden claim text: {forbidden_markdown}")

    source_body_checked = _validate_authority(root)
    return {
        "passed": True,
        "schemaVersion": SCHEMA_VERSION,
        "contractId": CONTRACT_ID,
        "anchorCount": len(anchors),
        "lockPathRowCount": len(lock_rows),
        "candidateOrderCount": len(candidate_rows),
        "sourceHypothesisCount": len(hypotheses),
        "sourceBodyChecked": source_body_checked,
        "runtimeObservationRows": 0,
        "coreImplementationRows": 0,
    }


def validate_tracked_contract(
    contract_path: Path = CONTRACT_PATH,
    doc_path: Path = DOC_PATH,
) -> dict[str, object]:
    payload = _load_json(contract_path, "tracked contract")
    try:
        markdown = doc_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"cannot read tracked Markdown contract: {doc_path}: {exc}") from exc
    return validate_contract(payload, markdown, root=ROOT)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--check", action="store_true", help="validate the tracked contract")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")
    try:
        report = validate_tracked_contract()
    except ContractError as exc:
        print(f"BattleEngine target-acquisition static contract: FAIL: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine target-acquisition static contract: PASS")
        print(f"Anchors: {report['anchorCount']}/3")
        print(f"Lock path rows: {report['lockPathRowCount']}/6")
        print(f"Candidate order rows: {report['candidateOrderCount']}/7")
        print(f"Source hypotheses: {report['sourceHypothesisCount']}/3")
        print(f"Pinned source body checked: {str(report['sourceBodyChecked']).lower()}")
        print("Runtime observations: 0; Core implementation rows: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
