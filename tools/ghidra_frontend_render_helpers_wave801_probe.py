#!/usr/bin/env python3
"""Validate Wave801 frontend/render helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave801-frontend-render-helpers"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_render_helpers_wave801_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
FEPDEBRIEFING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPDebriefing.cpp" / "_index.md"
FEPLEVELSELECT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPLevelSelect.cpp" / "_index.md"
DXFONT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFont.cpp" / "_index.md"
FEPVIRTUALKEYBOARD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPVirtualKeyboard.cpp" / "_index.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified"
NEXT_RAW_HEAD = "0x0044d390"

TARGETS = {
    "0x0044a0c0": {
        "name": "CDXMeshVB__GetGlobalZeroDouble",
        "signature": "double __cdecl CDXMeshVB__GetGlobalZeroDouble(void)",
        "comment": ("Wave801 static read-back", "DAT_00672fd0", "14 current xrefs"),
        "tags": {"dxmeshvb", "global-double-getter", "signature-corrected", "tranche-head"},
        "xrefs": 14,
    },
    "0x00456780": {
        "name": "CFEPDebriefing__Initialize",
        "signature": "int __fastcall CFEPDebriefing__Initialize(void * this)",
        "comment": ("Wave801 static read-back", "0x005db9c0", "FEPDebriefing.cpp", "0x324", "0x640"),
        "tags": {"fepdebriefing", "frontend-init", "allocation-init", "vtable-data-xref"},
        "xrefs": 1,
    },
    "0x0045d730": {
        "name": "CFEPLevelSelect__UpdateMouseEdgeSlide",
        "signature": "void __cdecl CFEPLevelSelect__UpdateMouseEdgeSlide(int state, float * value, float max_value)",
        "comment": ("Wave801 static read-back", "CFrontEnd__IsMouseInputReady", "DAT_0089bda8", "cubic"),
        "tags": {"feplevelselect", "mouse-edge-slide", "cubic-clamp", "frontend-process-helper"},
        "xrefs": 1,
    },
    "0x00465710": {
        "name": "CDXFont__DrawTextDynamic",
        "signature": "void __stdcall CDXFont__DrawTextDynamic(void * this, float x, float y, float z, float scale_x, float scale_y, int color, short * text, float transition, int fade_out, int flags)",
        "comment": ("Wave801 static read-back", "67 current xrefs", "per-character ARGB", "CDXFont__DrawTextScaled"),
        "tags": {"dxfont", "dynamic-text", "per-character-colors", "text-shadow"},
        "xrefs": 67,
    },
    "0x004659a0": {
        "name": "CDXFont__DrawTextScaledWithShadow",
        "signature": "int __thiscall CDXFont__DrawTextScaledWithShadow(void * this, float x, float y, uint packed_argb, short * text, uint flags, float depth_z, float x_scale, float y_scale)",
        "comment": ("Wave801 static read-back", "stale CDXEngine owner label", "x+1/y+1", "43 current xrefs"),
        "tags": {"dxfont", "drawtextscaled-shadow", "name-corrected", "signature-corrected", "text-shadow"},
        "xrefs": 43,
    },
    "0x00465c10": {
        "name": "CDXBitmapFont__BuildGlyphRemapTables",
        "signature": "void __cdecl CDXBitmapFont__BuildGlyphRemapTables(void)",
        "comment": ("Wave801 static read-back", "DAT_005db5fc", "DAT_00679af4", "DAT_006799f4"),
        "tags": {"dxbitmapfont", "glyph-remap", "charset-table", "font-init-helper"},
        "xrefs": 1,
    },
    "0x00465dd0": {
        "name": "CFEPVirtualKeyboard__IsInputAccepted",
        "signature": "int __thiscall CFEPVirtualKeyboard__IsInputAccepted(void * this, void * input_ctx, int key_code)",
        "comment": ("Wave801 static read-back", "this+0x15c", "input_ctx", "DAT_00679af4"),
        "tags": {"fepvirtualkeyboard", "input-predicate", "vtable-dispatch", "save-name-entry"},
        "xrefs": 1,
    },
    "0x00465f00": {
        "name": "CVBufTexture__GetGlobalEnableByte",
        "signature": "int __cdecl CVBufTexture__GetGlobalEnableByte(void)",
        "comment": ("Wave801 static read-back", "DAT_00679b40", "upper EAX", "six current xrefs"),
        "tags": {"vbuftexture", "global-enable-byte", "render-helper", "tranche-tail"},
        "xrefs": 6,
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "frontend-render-helpers-wave801",
    "wave801-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
}

CORE_ANCHORS = (
    "Wave801 frontend render helpers",
    "frontend-render-helpers-wave801",
    "0x0044a0c0 CDXMeshVB__GetGlobalZeroDouble",
    "0x00456780 CFEPDebriefing__Initialize",
    "0x0045d730 CFEPLevelSelect__UpdateMouseEdgeSlide",
    "0x00465710 CDXFont__DrawTextDynamic",
    "0x004659a0 CDXFont__DrawTextScaledWithShadow",
    "0x00465c10 CDXBitmapFont__BuildGlyphRemapTables",
    "0x00465dd0 CFEPVirtualKeyboard__IsInputAccepted",
    "0x00465f00 CVBufTexture__GetGlobalEnableByte",
    "0x0044d390 CFEPSaveGame__InitDialogAndLayoutState",
    "0x00465640 CLTShell__InvokeWithLoadingTransitionGate",
    "0 exact-undefined signatures",
    "0 param_N",
    "5564/6098 = 91.24%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime visual behavior proven",
    "runtime frontend behavior proven",
    "runtime rendering behavior proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 134,
        "pre-instructions.tsv": 296,
        "pre-decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 134,
        "post-instructions.tsv": 296,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata row: {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["comment"]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags row: {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | set(expected["tags"])
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row: {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_rows = read_tsv(BASE / "post-xrefs.tsv")
    for address, expected in TARGETS.items():
        actual_count = sum(1 for row in xref_rows if normalize_address(row["target_addr"]) == address)
        require(actual_count == expected["xrefs"], f"xref count mismatch at {address}: {actual_count}", failures)

    shadow_text = read_text(BASE / "post-decompile" / "004659a0_CDXFont__DrawTextScaledWithShadow.c")
    for token in ("CDXFont__DrawTextScaledWithShadow", "x + _DAT_005d8568", "packed_argb & 0xff000000"):
        require(token in shadow_text, f"missing shadow helper decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=1 would_rename=0 signature_updated=2 comment_only_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 134 rows",
        "post-instructions.log": "Wrote 296 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5564",
        "queue-probe.log": "Commentless functions: 534",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave801.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave801_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "Script not found", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 534, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5564, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5564, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and normalize_address(raw_commentless.get("address", "")) == NEXT_RAW_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFEPSaveGame__InitDialogAndLayoutState", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171314055, "backup byte count mismatch", failures)
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

    function_docs = {
        DXMESHVB_DOC: ("Wave801", "frontend-render-helpers-wave801", "0x0044a0c0 CDXMeshVB__GetGlobalZeroDouble", BACKUP_PATH),
        FEPDEBRIEFING_DOC: ("Wave801", "frontend-render-helpers-wave801", "0x00456780 CFEPDebriefing__Initialize", "0x0062913c", BACKUP_PATH),
        FEPLEVELSELECT_DOC: ("Wave801", "frontend-render-helpers-wave801", "0x0045d730 CFEPLevelSelect__UpdateMouseEdgeSlide", BACKUP_PATH),
        DXFONT_DOC: ("Wave801", "frontend-render-helpers-wave801", "0x00465710 CDXFont__DrawTextDynamic", "0x004659a0 CDXFont__DrawTextScaledWithShadow", BACKUP_PATH),
        FEPVIRTUALKEYBOARD_DOC: ("Wave801", "frontend-render-helpers-wave801", "0x00465dd0 CFEPVirtualKeyboard__IsInputAccepted", BACKUP_PATH),
        VBUFTEXTURE_DOC: ("Wave801", "frontend-render-helpers-wave801", "0x00465f00 CVBufTexture__GetGlobalEnableByte", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-frontend-render-helpers-wave801") == r"py -3 tools\ghidra_frontend_render_helpers_wave801_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave801 frontend render helpers" for row in ledger_rows), "missing Wave801 ledger row", failures)
    require(any(row.get("task") == "Wave801 frontend render helpers" and row.get("attempt_id") == 20456 for row in attempts), "missing Wave801 attempt row", failures)


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
        print("Wave801 frontend-render helper probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave801 frontend-render helper probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
