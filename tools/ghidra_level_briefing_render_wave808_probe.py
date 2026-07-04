#!/usr/bin/env python3
"""Validate Wave808 level-briefing render read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave808-engine-postmission-overlay"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_level_briefing_render_wave808_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEVEL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "LevelBriefingLog.cpp" / "_index.md"
DXENGINE_SOURCE = ROOT / "references" / "Onslaught" / "DXEngine.cpp"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

ADDRESS = "0x0048f620"
OLD_NAME = "CDXEngine__RenderPostMissionOverlayAndMenu"
NAME = "CLevelBriefingLog__Render"
SIGNATURE = "void __thiscall CLevelBriefingLog__Render(void * this, void * viewport)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-113054_post_wave808_level_briefing_render_verified"
NEXT_HEAD = "0x004901e0 MathMatrix3x4__AssignFromEightScalars"

COMMON_TAGS = {
    "static-reaudit",
    "level-briefing-render-wave808",
    "wave808-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "level-briefing-log",
    "owner-corrected",
    "post-render-ui",
    "overlay-render",
    "renamed",
    "tranche-head",
}

DOC_TOKENS = (
    "Wave808 level-briefing render",
    "level-briefing-render-wave808",
    "0x0048f620 CLevelBriefingLog__Render",
    "CDXEngine__RenderPostMissionOverlayAndMenu",
    "0x0053ee19",
    "DAT_008a9d94",
    "5583/6098 = 91.55%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime ui behavior proven",
    "runtime level briefing behavior proven",
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
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 251,
        "pre-full-instructions.tsv": 1201,
        "pre-decompile/index.tsv": 1,
        "pre-caller-metadata.tsv": 1,
        "pre-caller-instructions.tsv": 261,
        "pre-caller-decompile/index.tsv": 1,
        "pre-callsite-instructions.tsv": 86,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 1201,
        "post-decompile/index.tsv": 1,
        "post-caller-decompile/index.tsv": 1,
        "post-callsite-instructions.tsv": 86,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    post = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(pre["address"]) == ADDRESS, "pre address mismatch", failures)
    require(pre["name"] == OLD_NAME, "pre name mismatch", failures)
    require(pre["signature"] == f"void {OLD_NAME}(void)", "pre signature mismatch", failures)
    require(normalize_address(post["address"]) == ADDRESS, "post address mismatch", failures)
    require(post["name"] == NAME, "post name mismatch", failures)
    require(post["signature"] == SIGNATURE, "post signature mismatch", failures)
    for token in ("Wave808 static read-back correction", "0x0053ee19", "DAT_008a9d94", "RET 0x4", "GAME.GetLevelBriefingLog()->Render(viewport)"):
        require(token in post.get("comment", ""), f"missing post comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"missing tags: {COMMON_TAGS - tags}", failures)

    decomp = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decomp["name"] == NAME, "post decompile name mismatch", failures)
    require(decomp["signature"] == SIGNATURE, "post decompile signature mismatch", failures)
    require(decomp["status"] == "OK", "post decompile status mismatch", failures)

    xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(normalize_address(xref["target_addr"]) == ADDRESS, "post xref target mismatch", failures)
    require(normalize_address(xref["from_addr"]) == "0x0053ee19", "post xref source mismatch", failures)
    require(xref["from_function"] == "CDXEngine__PostRender", "post xref caller mismatch", failures)

    caller_text = read_text(BASE / "post-caller-decompile" / "0053ecc0_CDXEngine__PostRender.c")
    require("CMessageLog__Render(DAT_008a9d88" in caller_text, "caller missing message-log render", failures)
    require("CLevelBriefingLog__Render(DAT_008a9d94,pvVar5)" in caller_text, "caller missing level-briefing render", failures)
    require("CPauseMenu__Render(DAT_008a9d8c)" in caller_text, "caller missing pause-menu render", failures)

    callsite_rows = read_tsv(BASE / "post-callsite-instructions.tsv")
    callsite = {row["instruction_addr"]: row for row in callsite_rows}
    require(callsite.get("0x0053ee12", {}).get("operands") == "ECX, dword ptr [0x008a9d94]", "callsite ECX load mismatch", failures)
    require(callsite.get("0x0053ee18", {}).get("mnemonic") == "PUSH", "callsite viewport push mismatch", failures)
    require(callsite.get("0x0053ee19", {}).get("operands") == "0x0048f620", "callsite call target mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 1201 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-caller-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 86 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5583",
        "queue-probe.log": "Commentless functions: 515",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave808.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave808_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 515, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5583, "commented count mismatch", failures)
    require(strict == 5583, "strict count mismatch", failures)
    require(raw is not None and raw.get("address") == "0x004901e0", "raw head address mismatch", failures)
    require(raw is not None and raw.get("name") == "MathMatrix3x4__AssignFromEightScalars", "raw head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (171314055, 171314055.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, LEVEL_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    source = read_text(DXENGINE_SOURCE)
    require("GAME.GetMessageLog()->Render(viewport)" in source, "source missing message-log call", failures)
    require("GAME.GetLevelBriefingLog()->Render(viewport)" in source, "source missing level-briefing call", failures)
    require("GAME.GetPauseMenu()->Render()" in source, "source missing pause-menu call", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-level-briefing-render-wave808") == r"py -3 tools\ghidra_level_briefing_render_wave808_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave808 level briefing render" for row in read_jsonl(LEDGER)), "missing Wave808 ledger row", failures)
    require(any(row.get("task") == "Wave808 level briefing render" and row.get("attempt_id") == 20463 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave808 attempt row", failures)


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
        print("Wave808 level-briefing render probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave808 level-briefing render probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
