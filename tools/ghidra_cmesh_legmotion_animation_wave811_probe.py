#!/usr/bin/env python3
"""Validate Wave811 CMesh LegMotion animation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave811-cmeshpart-animation-token"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cmesh_legmotion_animation_wave811_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
MESHPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

ADDRESS = "0x0049c2d0"
OLD_NAME = "CMeshPart__HasAnimationToken_623074"
NAME = "CMesh__HasLegMotionAnimation"
SIGNATURE = "bool __cdecl CMesh__HasLegMotionAnimation(void * mesh)"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-125806_post_wave811_cmesh_legmotion_animation_verified"
NEXT_HEAD = "0x004a25c0 CLTShell__ValidateAndRollHeapDeltas"

COMMON_TAGS = {
    "static-reaudit",
    "cmesh-legmotion-animation-wave811",
    "wave811-readback-verified",
    "retail-binary-evidence",
    "renamed",
    "signature-corrected",
    "comment-hardened",
    "raw-commentless-tail",
    "mesh-optimization",
    "legmotion-animation",
}

DOC_TOKENS = (
    "Wave811 CMesh LegMotion animation",
    "cmesh-legmotion-animation-wave811",
    f"{ADDRESS} {NAME}",
    OLD_NAME,
    "0x00623074",
    "LegMotion",
    "part+0x128",
    "CMesh__FindAnimationIndexByName",
    "5586/6098 = 91.60%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime mesh optimization behavior proven",
    "runtime animation behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 181,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 9,
        "pre-context-decompile/index.tsv": 9,
        "pre-context-xrefs.tsv": 28,
        "pre-token-predicate-instructions.tsv": 564,
        "pre-caller-metadata.tsv": 4,
        "pre-caller-decompile/index.tsv": 4,
        "pre-caller-instructions.tsv": 884,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 181,
        "post-decompile/index.tsv": 1,
        "post-caller-metadata.tsv": 4,
        "post-caller-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    post = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(pre["address"]) == ADDRESS, "pre address mismatch", failures)
    require(pre["name"] == OLD_NAME, "pre name mismatch", failures)
    require(pre["signature"] == "bool CMeshPart__HasAnimationToken_623074(void)", "pre signature mismatch", failures)
    require(not pre.get("comment", "").strip(), "pre row should be commentless", failures)
    require(normalize_address(post["address"]) == ADDRESS, "post address mismatch", failures)
    require(post["name"] == NAME, "post name mismatch", failures)
    require(post["signature"] == SIGNATURE, "post signature mismatch", failures)

    comment = post.get("comment", "")
    for token in (
        "Wave811 static read-back hardening",
        "0x00623074",
        "LegMotion",
        "CMesh__FindAnimationIndexByName",
        "part+0x128",
        "CMesh rather than CMeshPart",
        "runtime mesh optimization behavior",
        "runtime animation behavior",
        "rebuild parity remain deferred",
    ):
        require(token in comment, f"missing post comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"missing tags: {COMMON_TAGS - tags}", failures)

    decomp = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decomp["name"] == NAME, "post decompile name mismatch", failures)
    require(decomp["signature"] == SIGNATURE, "post decompile signature mismatch", failures)
    require(decomp["status"] == "OK", "post decompile status mismatch", failures)
    decomp_text = read_text(BASE / "post-decompile" / "0049c2d0_CMesh__HasLegMotionAnimation.c")
    for token in (
        "CMesh__HasLegMotionAnimation(void *mesh)",
        "CMesh__FindAnimationIndexByName(mesh,s_LegMotion_00623074)",
        "return iVar1 != -1;",
    ):
        require(token in decomp_text, f"missing decompile token: {token}", failures)

    instruction_rows = read_tsv(BASE / "post-instructions.tsv")
    by_addr = {normalize_address(row["instruction_addr"]): row for row in instruction_rows}
    require(by_addr.get("0x0049c2d0", {}).get("operands") == "ECX, dword ptr [ESP + 0x4]", "missing mesh load", failures)
    require(by_addr.get("0x0049c2d4", {}).get("operands") == "0x623074", "missing LegMotion string push", failures)
    require(by_addr.get("0x0049c2d9", {}).get("operands") == "0x004aa630", "missing animation lookup call", failures)
    require(by_addr.get("0x0049c2e0", {}).get("operands") == "EAX, -0x1", "missing -1 compare", failures)
    require(by_addr.get("0x0049c2e8", {}).get("mnemonic") == "RET", "missing cdecl RET", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_from = {normalize_address(row["from_addr"]) for row in xrefs}
    for addr in ("0x004baf26", "0x004bafae", "0x004baff2", "0x004bb0f6", "0x004bb17e", "0x004bb1c2", "0x004bb22a", "0x004bb23e", "0x004bb27a"):
        require(addr in xref_from, f"missing xref from {addr}", failures)

    caller_text = "\n".join(
        read_text(path)
        for path in (BASE / "post-caller-decompile").glob("*.c")
    )
    for token in (
        "CMesh__HasLegMotionAnimation(*(void **)((int)part + 0x128))",
        "CMesh__HasLegMotionAnimation(mesh)",
        "CMesh__FindAnimationIndexByName",
    ):
        require(token in caller_text, f"missing caller decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-instructions.log": "Wrote 181 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-caller-metadata.log": "targets=4 found=4 missing=0",
        "post-caller-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5586",
        "queue-probe.log": "Commentless functions: 512",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave811.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave811_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1", "Input file not found", "SCRIPT ERROR"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 512, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5586, "commented count mismatch", failures)
    require(strict == 5586, "strict count mismatch", failures)
    require(raw is not None and raw.get("address") == "0x004a25c0", "raw head address mismatch", failures)
    require(raw is not None and raw.get("name") == "CLTShell__ValidateAndRollHeapDeltas", "raw head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 171314055, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        MESH_DOC,
        MESHPART_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cmesh-legmotion-animation-wave811")
        == r"py -3 tools\ghidra_cmesh_legmotion_animation_wave811_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave811 CMesh LegMotion animation" for row in ledger_rows), "missing Wave811 ledger row", failures)
    require(any(row.get("task") == "Wave811 CMesh LegMotion animation" and row.get("attempt_id") == 20466 for row in attempts), "missing Wave811 attempt row", failures)


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
        print("Wave811 CMesh LegMotion animation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave811 CMesh LegMotion animation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
