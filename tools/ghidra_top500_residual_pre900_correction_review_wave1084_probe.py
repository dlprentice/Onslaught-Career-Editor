#!/usr/bin/env python3
"""Validate Wave1084 top-500 residual pre-900 correction read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1084-top500-residual-pre900-correction-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_top500_residual_pre900_correction_review_wave1084_2026-06-02.md"
AGG_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1084_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-122026_post_wave1084_top500_residual_pre900_correction_review_verified"

TARGETS = {
    "0x004d1f10": {
        "name": "CPlane__Hit_CheckFatalDamageAndDie",
        "signature": "void __thiscall CPlane__Hit_CheckFatalDamageAndDie(void * this, void * hit_thing, void * hit_context)",
        "comment_tokens": ("Wave485", "CPlane vtable", "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000"),
        "tag_tokens": ("plane-wave485", "vtable-readback", "hit"),
        "xref_tokens": ("005e19cc", "DATA"),
    },
    "0x004de1d0": {
        "name": "CSafeSide__ShutdownAndUnlinkFactionAnchor",
        "signature": "void __fastcall CSafeSide__ShutdownAndUnlinkFactionAnchor(void * this)",
        "comment_tokens": ("Wave542", "DAT_00855160", "CComplexThing__Shutdown"),
        "tag_tokens": ("safeside-wave542", "owner-retained"),
        "xref_tokens": ("005dcce4", "DATA"),
    },
    "0x004ea8d0": {
        "name": "CRelaxedSquad__CreateIterator",
        "signature": "void * __fastcall CRelaxedSquad__CreateIterator(void * this)",
        "comment_tokens": ("Wave510", "CSPtrSet", "iterator"),
        "tag_tokens": ("start-respawn-wave510", "relaxed-squad", "iterator"),
        "xref_tokens": ("005e3b10", "DATA"),
    },
    "0x00505960": {
        "name": "CWaypoint__Load",
        "signature": "void __thiscall CWaypoint__Load(void * this, void * mem_buffer, int load_mode, void * object_table)",
        "comment_tokens": ("Wave538", "CWaypointManager__LoadWaypoints", "RET 0x0c"),
        "tag_tokens": ("waypoint-wave538", "mem-buffer", "object-link"),
        "xref_tokens": ("00505b64", "UNCONDITIONAL_CALL"),
    },
    "0x00523db0": {
        "name": "Input__ResetMouseTransientState",
        "signature": "void __cdecl Input__ResetMouseTransientState(void)",
        "comment_tokens": ("Wave567", "CProfiler__ResetAll", "mouse transient globals"),
        "tag_tokens": ("input-cursor-wave567", "mouse-state", "transient-reset"),
        "xref_tokens": ("0042d411", "00466ba5", "0046eee9"),
    },
    "0x005245e0": {
        "name": "COggFileRead__scalar_deleting_dtor",
        "signature": "void * __thiscall COggFileRead__scalar_deleting_dtor(void * this, byte flags)",
        "comment_tokens": ("Wave568", "scalar-deleting destructor", "RET 0x4"),
        "tag_tokens": ("ogg-vorbis-wave568", "scalar-deleting-dtor", "destructor"),
        "xref_tokens": ("005e4a44", "DATA"),
    },
}

DOC_TOKENS = (
    "Wave1084",
    "top500-residual-pre900-correction-review-wave1084",
    "0x004d1f10 CPlane__Hit_CheckFatalDamageAndDie",
    "0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor",
    "0x004ea8d0 CRelaxedSquad__CreateIterator",
    "0x00505960 CWaypoint__Load",
    "0x00523db0 Input__ResetMouseTransientState",
    "0x005245e0 COggFileRead__scalar_deleting_dtor",
    "1424/1560 = 91.28%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6307/6307 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof complete",
    "fully reverse-engineered",
    "rebuild parity proven",
    "gameplay outcomes proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "addresses.txt": 6,
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 11,
        "instructions.tsv": 249,
        "decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        path = BASE / relative
        if relative.endswith(".txt"):
            actual = len([line for line in read_text(path).splitlines() if line.strip() and not line.startswith("#")])
        else:
            actual = len(read_tsv(path))
        require(actual == expected, f"{relative} row count mismatch: {actual}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xref_text = read_text(BASE / "xrefs.tsv")

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch for {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch for {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch for {address}", failures)
            for token in expected["comment_tokens"]:
                require(token in row.get("comment", ""), f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            require(tag_row.get("status") == "OK", f"tag status mismatch for {address}", failures)
            for token in expected["tag_tokens"]:
                require(token in tag_text, f"missing tag token for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"decompile name mismatch for {address}", failures)
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch for {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch for {address}", failures)

        for token in expected["xref_tokens"]:
            require(token in xref_text, f"missing xref token for {address}: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "xrefs.log": "Wrote 11 rows",
        "instructions.log": "Wrote 249 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6307, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["legacyWeakNameCount"] == 0, "weak-name count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain-owner count mismatch", failures)
    require(quality["helperAddressNameCount"] == 0, "helper-address count mismatch", failures)
    require(quality["wrapperAddressNameCount"] == 0, "wrapper-address count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6307, "quality TSV row count mismatch", failures)
    require(commented == 6307, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6307, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174820231, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGG_NOTE,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-top500-residual-pre900-correction-review-wave1084")
        == r"py -3 tools\ghidra_top500_residual_pre900_correction_review_wave1084_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1084-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1084 --check",
        "missing aggregate package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave1084-top500-residual-pre900-correction-review.json")
    args = parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    report = {
        "schema": "ghidra-top500-residual-pre900-correction-review-wave1084.v1",
        "status": "PASS" if not failures else "FAIL",
        "targets": sorted(TARGETS),
        "mutatedTargets": 0,
        "metadataRows": 6,
        "tagRows": 6,
        "xrefRows": 11,
        "instructionRows": 249,
        "decompileRows": 6,
        "failures": failures,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Wave1084 top-500 residual pre-900 correction review probe:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in failures:
        print("-", failure)
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
