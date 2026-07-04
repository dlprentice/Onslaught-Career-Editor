#!/usr/bin/env python3
"""Validate Wave861 render/HUD/platform-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave861-render-hud-platform-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_render_hud_platform_tail_wave861_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave861 render/HUD/platform tail"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-141443_post_wave861_render_hud_platform_tail_verified"
NEXT_HEAD = "0x0052a830 CD3DApplication__FindDepthStencilFormat"
STRICT_PROXY = "5802/6105 = 95.04%"

TARGET_SIGNATURES = {
    "0x00523a70": ("CDXEngine__RenderMouseCursorSprite", "void CDXEngine__RenderMouseCursorSprite(void)"),
    "0x00523b30": ("CVBufTexture__DestroyGlobalHudHandle89BD98", "void CVBufTexture__DestroyGlobalHudHandle89BD98(void)"),
    "0x00527990": ("CGame__DrawLocalCoopControllerPrompt", "void CGame__DrawLocalCoopControllerPrompt(void)"),
    "0x00527de0": (
        "CWaterRenderSystem__ResetAndMarkSourceFlag",
        "void __fastcall CWaterRenderSystem__ResetAndMarkSourceFlag(void * validation_record)",
    ),
    "0x00527f50": ("PCPlatform__AsyncMusicStreamWorkerMain", "int PCPlatform__AsyncMusicStreamWorkerMain(void)"),
    "0x005282b0": ("PCPlatform__InitAsyncMusicStream", "void PCPlatform__InitAsyncMusicStream(void)"),
    "0x00528460": ("PCPlatform__ShutdownAsyncMusicStream", "void PCPlatform__ShutdownAsyncMusicStream(void)"),
    "0x00528540": (
        "PCPlatform__KickAsyncMusicStreamRead",
        "void __cdecl PCPlatform__KickAsyncMusicStreamRead(char * track_path)",
    ),
    "0x005285b0": ("PCPlatform__ResetAsyncMusicStream", "void PCPlatform__ResetAsyncMusicStream(void)"),
    "0x005285e0": (
        "PCPlatform__UpdateAsyncMusicStreamVolume",
        "void __cdecl PCPlatform__UpdateAsyncMusicStreamVolume(float normalized_volume)",
    ),
}

COMMENT_TOKENS = {
    "0x00523a70": ("Wave861 static read-back", "mouse.tga", "meshtex\\default.tga", "CVBufTexture__DrawSpriteEx"),
    "0x00523b30": ("Wave861 static read-back", "DAT_0089bd98", "CTexture__DecrementRefCountFromNameField"),
    "0x00527990": ("Wave861 static read-back", "CFrontEnd__GetPlayer0ControllerPort", "CDXFont__DrawText", "DAT_009c690d"),
    "0x00527de0": ("Wave861 static read-back/signature correction", "validation_record+0x10", "DAT_00854dd9"),
    "0x00527f50": ("Wave861 static read-back", "CreateThread target", "44100 Hz stereo", "DAT_0089bed0"),
    "0x005282b0": ("Wave861 static read-back", "data\\music", "CreateThread", "0x22f0 COggFileRead-like"),
    "0x00528460": ("Wave861 static read-back", "signals the shutdown event", "closes the event handles"),
    "0x00528540": ("Wave861 static read-back/signature correction", "track_path", "CRT__MbsNcpy_LocaleLock", "DAT_0089beb8"),
    "0x005285b0": ("Wave861 static read-back", "ResetEvent", "symbol/address collision"),
    "0x005285e0": ("Wave861 static read-back/signature correction", "normalized_volume", "10000.0", "vtable slot 0x3c"),
}

COMMON_TAGS = {
    "static-reaudit",
    "render-hud-platform-tail-wave861",
    "wave861-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "important-connective-infrastructure",
}

EXPECTED_XREFS = {
    ("0x00523a70", "0x00473ad2", "UNCONDITIONAL_CALL"),
    ("0x00523a70", "0x0048ff7a", "UNCONDITIONAL_CALL"),
    ("0x00523a70", "0x004b9a66", "UNCONDITIONAL_CALL"),
    ("0x00523a70", "0x004d15ad", "UNCONDITIONAL_CALL"),
    ("0x00523a70", "0x00468700", "UNCONDITIONAL_CALL"),
    ("0x00523b30", "0x004f01a6", "UNCONDITIONAL_CALL"),
    ("0x00527990", "0x00468479", "UNCONDITIONAL_CALL"),
    ("0x00527990", "0x0046e8a9", "UNCONDITIONAL_CALL"),
    ("0x00527990", "0x0046e8c0", "UNCONDITIONAL_CALL"),
    ("0x00527990", "0x0051f2f7", "UNCONDITIONAL_CALL"),
    ("0x00527de0", "0x0055c1c0", "UNCONDITIONAL_CALL"),
    ("0x00527de0", "0x0055cf0a", "UNCONDITIONAL_CALL"),
    ("0x00527de0", "0x0055d255", "UNCONDITIONAL_CALL"),
    ("0x00527f50", "0x00528397", "DATA"),
    ("0x005282b0", "0x00515323", "UNCONDITIONAL_CALL"),
    ("0x00528540", "0x005285d7", "DATA"),
}

STRING_EXPECTATIONS = {
    "string-00640058.tsv": "mouse.tga",
    "string-00625498.tsv": r"meshtex\default.tga",
    "string-0063e03c.tsv": r"[maintainer-local-source-export-root]\PCPlatform.cpp",
    "string-0063dff0.tsv": r"data\music",
}

CORE_ANCHORS = (
    TASK,
    "render-hud-platform-tail-wave861",
    "0x00523a70 CDXEngine__RenderMouseCursorSprite",
    "0x00523b30 CVBufTexture__DestroyGlobalHudHandle89BD98",
    "0x00527990 CGame__DrawLocalCoopControllerPrompt",
    "0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag",
    "0x00527f50 PCPlatform__AsyncMusicStreamWorkerMain",
    "0x005282b0 PCPlatform__InitAsyncMusicStream",
    "0x00528540 PCPlatform__KickAsyncMusicStreamRead",
    "0x005285e0 PCPlatform__UpdateAsyncMusicStreamVolume",
    "important connective infrastructure",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime cursor behavior proven",
    "runtime controller prompt behavior proven",
    "runtime water behavior proven",
    "runtime async music behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 23,
        "pre-instructions.tsv": 1010,
        "pre-decompile/index.tsv": 10,
        "pre-context-metadata.tsv": 18,
        "pre-context-decompile/index.tsv": 18,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 23,
        "post-instructions.tsv": 1010,
        "post-decompile/index.tsv": 10,
        "post-context-metadata.tsv": 18,
        "post-context-decompile/index.tsv": 18,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }

    for address, (name, signature) in TARGET_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            if address in {"0x00527de0", "0x00528540", "0x005285e0"}:
                require("signature-hardened" in actual_tags, f"missing signature tag at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for expected in EXPECTED_XREFS:
        require(expected in xrefs, f"missing xref row: {expected}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=7 missing=0 bad=0",
        "apply-prototype-string-mismatch.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=7 missing=0 bad=3",
        "apply-dry-after-prototype-fix.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 23 rows",
        "post-instructions.log": "Wrote 1010 instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-context-metadata.log": "targets=18 found=18 missing=0",
        "post-context-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6105 commented_functions=5802",
        "queue-probe.log": "Commentless functions: 303",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave861.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave861_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative != "apply-prototype-string-mismatch.log":
            for bad in ("LockException", "MISSING:", "BADSIG:", "READBACK_BAD:", "missing=1", "bad=1", "failed=1"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 303, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for queue_name in ("commentlessHighSignal", "signature", "nameConfidence", "legacyWeakNames"):
        require(queue["priorityQueues"][queue_name] == [], f"{queue_name} should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5802, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5802, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0052a830", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CD3DApplication__FindDepthStencilFormat", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172264327 or backup.get("totalBytes") == 172264327.0, "backup byte count mismatch", failures)
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
        ENGINE_DOC,
        VBUFTEXTURE_DOC,
        GAME_DOC,
        PCPLATFORM_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-render-hud-platform-tail-wave861")
        == r"py -3 tools\ghidra_render_hud_platform_tail_wave861_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave861 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20516 for row in attempts), "missing Wave861 attempt row", failures)


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
        print("Wave861 render/HUD/platform-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave861 render/HUD/platform-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
