#!/usr/bin/env python3
"""Validate Wave789 signature-debt read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave789-signature-debt-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_signature_debt_wave789_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-021024_post_wave789_signature_debt_verified"

TARGETS = {
    "0x00410c50": {
        "name": "CMonitor__UpdateMovementTransitionAndEffects",
        "signature": "void __fastcall CMonitor__UpdateMovementTransitionAndEffects(void * monitor)",
        "xrefs": {"0x00408d61": "UNCONDITIONAL_CALL"},
        "tokens": ("Wave789 signature-debt hardening", "CMonitor__Process", "monitor", "CMonitor__ApplyHostileEnvironmentPenalty"),
        "tags": {"monitor", "movement-transition", "param-name"},
    },
    "0x00412ad0": {
        "name": "CMonitor__UpdateSurfaceAlignmentAngle",
        "signature": "void __fastcall CMonitor__UpdateSurfaceAlignmentAngle(void * monitor)",
        "xrefs": {"0x00413a5a": "UNCONDITIONAL_CALL"},
        "tokens": ("Wave789 signature-debt hardening", "CBattleEngineWalkerPart__Move", "monitor", "+0x20", "+0x24", "+0x28"),
        "tags": {"monitor", "surface-alignment", "param-name"},
    },
    "0x00414b30": {
        "name": "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
        "signature": "int __fastcall TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit(void * target_set)",
        "xrefs": {"0x0040657e": "UNCONDITIONAL_CALL", "0x0040658b": "UNCONDITIONAL_CALL"},
        "tokens": ("Wave789 signature-debt hardening", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "target_set", "CUnit__IsTargetTimeoutBeforeProfileLimit"),
        "tags": {"target-set", "weapon-fire", "param-name"},
    },
    "0x00418090": {
        "name": "OpeningAnimationStateCallback__StartOpeningIfPending",
        "signature": "int __fastcall OpeningAnimationStateCallback__StartOpeningIfPending(void * state_record)",
        "xrefs": {"0x005d9080": "DATA"},
        "tokens": ("Wave789 signature-debt hardening", "state_record", "0x005d9080", "FindAnimationIndex", "unresolved table-owner boundary"),
        "tags": {"opening-animation", "callback", "param-name"},
    },
    "0x004879e0": {
        "name": "CHud__RenderOverlayForViewpoint",
        "signature": "void __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float unused_overlay_param)",
        "xrefs": {"0x00487c57": "UNCONDITIONAL_CALL"},
        "tokens": ("Wave789 signature-debt hardening", "unused_overlay_param", "viewpoint", "viewpoint_index", "per-viewpoint CHud overlay renderer"),
        "tags": {"hud", "overlay", "param-name"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "signature-debt-wave789",
    "wave789-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "param-name-hardened",
}

CORE_ANCHORS = (
    "Wave789 signature debt",
    "signature-debt-wave789",
    "0x00410c50 CMonitor__UpdateMovementTransitionAndEffects",
    "0x00412ad0 CMonitor__UpdateSurfaceAlignmentAngle",
    "0x00414b30 TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
    "0x00418090 OpeningAnimationStateCallback__StartOpeningIfPending",
    "0x004879e0 CHud__RenderOverlayForViewpoint",
    "commentless high-signal queue",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact source method identity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


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
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 185,
        "pre-decompile/index.tsv": 5,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 6,
        "post-instructions.tsv": 185,
        "post-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs_by_target: dict[str, dict[str, str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        target = normalize_address(row["target_addr"])
        xrefs_by_target.setdefault(target, {})[normalize_address(row["from_addr"])] = row.get("ref_type", "")

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == spec["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in spec["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | spec["tags"]
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == spec["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        actual_xrefs = xrefs_by_target.get(address, {})
        for from_addr, ref_type in spec["xrefs"].items():
            require(actual_xrefs.get(from_addr) == ref_type, f"xref mismatch for {address} from {from_addr}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 6 rows",
        "post-instructions.log": "Wrote 185 instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5544",
        "queue-probe.log": "Param signatures: 22",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave789.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave789_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 554, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 31, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 22, "param_N count mismatch", failures)
    require(not queue["priorityQueues"]["commentlessHighSignal"], "commentless high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5544, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5491, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (171215751, 171215751.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-signature-debt-wave789") == r"py -3 tools\ghidra_signature_debt_wave789_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave789 signature debt" for row in ledger_rows), "missing Wave789 ledger row", failures)
    require(any(row.get("task") == "Wave789 signature debt" and row.get("attempt_id") == 20444 for row in attempts), "missing Wave789 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave789 signature-debt probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave789 signature-debt probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
