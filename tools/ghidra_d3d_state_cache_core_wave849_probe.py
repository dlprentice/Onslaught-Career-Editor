#!/usr/bin/env python3
"""Validate Wave849 D3D state/cache core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave849-d3d-state-cache-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_d3d_state_cache_core_wave849_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LTSHELL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ltshell.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
CUMTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CUMTexture.cpp" / "_index.md"
DXMESHTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-073710_post_wave849_d3d_state_cache_core_verified"
NEXT_HEAD = "0x00513a80 PlatformInput__GetKeyState3Core"
TASK = "Wave849 D3D state/cache core"

TARGETS = {
    "0x00513640": {
        "name": "CEngine__GetConstant32",
        "signature": "int __cdecl CEngine__GetConstant32(void)",
        "tokens": ("Wave849 static read-back", "constant helper returning 0x20", "CDXTexture__Deserialize"),
        "tags": {"engine-constant", "texture-resource"},
    },
    "0x00513650": {
        "name": "CEngine__PrintGraphicsCardInfo",
        "signature": "void __cdecl CEngine__PrintGraphicsCardInfo(void)",
        "tokens": ("Wave849 static read-back", "con_whatami", "Graphics card info", "Using pure device"),
        "tags": {"graphics-card-info", "console-command", "source-con-whatami"},
    },
    "0x00513730": {
        "name": "CEngine__MarkDeviceResetPending",
        "signature": "void __cdecl CEngine__MarkDeviceResetPending(void)",
        "tokens": ("Wave849 static read-back", "CD3DApplication__MsgProc", "0x008a9acc", "D3DERR_DEVICELOST"),
        "tags": {"device-reset", "lost-device", "state-machine"},
    },
    "0x00513760": {
        "name": "CEngine__TextureFormatField32FD4ToIndex",
        "signature": "int __fastcall CEngine__TextureFormatField32FD4ToIndex(void * this)",
        "tokens": ("Wave849 static read-back", "this+0x32fd4", "CEngine__TextureFormatD3DToIndex", "old ReleaseField32FD4 name was misleading"),
        "tags": {"name-corrected", "texture-format", "texture-resource"},
    },
    "0x00513770": {
        "name": "CEngine__DeviceCall68_CheckError",
        "signature": "int __thiscall CEngine__DeviceCall68_CheckError(void * this, int arg2, int arg3, int arg4, int arg5, int arg6)",
        "tokens": ("Wave849 static read-back", "vtable slot 0x68", "D3D Error!", "HResultToString"),
        "tags": {"device-vtable-0x68", "error-logging", "hresult", "mesh-vbuffer"},
    },
    "0x005137d0": {
        "name": "CEngine__DeviceCall6C",
        "signature": "int __thiscall CEngine__DeviceCall6C(void * this, int arg2, int arg3, int arg4, int arg5, int arg6)",
        "tokens": ("Wave849 static read-back", "vtable slot 0x6c", "CIBuffer__CreateDynamic", "test EAX"),
        "tags": {"device-vtable-0x6c", "hresult", "buffer-create", "signature-corrected"},
    },
    "0x00513800": {
        "name": "IUnknown__ReleaseIfNonNull_ReturnZero",
        "signature": "int __stdcall IUnknown__ReleaseIfNonNull_ReturnZero(void * obj)",
        "tokens": ("Wave849 static read-back", "vtable[8]", "returns zero", "CDXMeshVB__ReleaseResources"),
        "tags": {"com-release", "resource-lifetime", "returns-zero"},
    },
    "0x00513820": {
        "name": "D3DStateCache__SetStateCached",
        "signature": "void __stdcall D3DStateCache__SetStateCached(int state_slot, int state_id, int value)",
        "tokens": ("Wave849 static read-back", "DAT_008557f0", "vtable slot 0x10c", "419 xref rows"),
        "tags": {"render-state", "state-cache", "vtable-0x10c"},
    },
    "0x00513870": {
        "name": "D3DStateCache__SetStateRaw",
        "signature": "void __stdcall D3DStateCache__SetStateRaw(int state_slot, int state_id, int value)",
        "tokens": ("Wave849 static read-back", "raw state helper", "DAT_008557f0", "slot 0x10c"),
        "tags": {"raw-state", "state-cache", "vtable-0x10c"},
    },
    "0x005138b0": {
        "name": "D3DStateCache__SetState114Cached",
        "signature": "void __stdcall D3DStateCache__SetState114Cached(int state_slot, int state_id, uint value)",
        "tokens": ("Wave849 static read-back", "slot 0x114", "state_id 6 value 3", "SetTextureStageState"),
        "tags": {"state-cache", "texture-stage-policy", "vtable-0x114"},
    },
    "0x00513930": {
        "name": "D3DStateCache__SetState114Raw",
        "signature": "void __stdcall D3DStateCache__SetState114Raw(int state_slot, int state_id, uint value)",
        "tokens": ("Wave849 static read-back", "raw policy-gated", "slot 0x114", "192 xref rows"),
        "tags": {"raw-policy-state", "state-cache", "vtable-0x114"},
    },
    "0x005139a0": {
        "name": "CEngine__CreateTextureOrFatal",
        "signature": "int __thiscall CEngine__CreateTextureOrFatal(void * this, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8)",
        "tokens": ("Wave849 static read-back", "vtable slot 0x5c", "Create texture failed: %s", "FatalError_LocalizedStringId"),
        "tags": {"device-vtable-0x5c", "fatal-on-failure", "texture-create"},
    },
    "0x00513a10": {
        "name": "CEngine__CreateTextureUnchecked",
        "signature": "int __thiscall CEngine__CreateTextureUnchecked(void * this, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8)",
        "tokens": ("Wave849 static read-back", "vtable slot 0x5c", "CDXTexture__Deserialize", "test EAX"),
        "tags": {"device-vtable-0x5c", "hresult", "signature-corrected", "texture-create"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "d3d-state-cache-core-wave849",
    "wave849-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "source-reference-ltshell",
    "direct3d-device",
}

EXPECTED_XREFS = {
    "0x00513640": {("0x00559f60", "CDXTexture__Deserialize"), ("0x005582cc", "CDXTexture__LoadTextureFromFile_Core")},
    "0x00513650": {("0x00512465", "<no_function>")},
    "0x00513730": {("0x0052ab8f", "CD3DApplication__MsgProc")},
    "0x00513760": {("0x004f7b73", "CUMTexture__RecreateTextureResource"), ("0x00557ad6", "CDXTexture__LoadTextureFromFile_Core")},
    "0x00513770": {("0x0054e3ee", "CDXMeshVB__Load"), ("0x0054c6e1", "CDXMeshVB__BuildStaticVB")},
    "0x005137d0": {("0x00488482", "CIBuffer__CreateDynamic"), ("0x0054d0d3", "CDXMeshVB__BuildSkeletalVB")},
    "0x00513800": {("0x004fffd7", "CVBuffer__dtor_base"), ("0x0054d40c", "CDXMeshVB__ReleaseResources")},
    "0x00513820": {("0x0042c8fe", "CConsole__RenderLoadingScreen"), ("0x0053e6d3", "CDXEngine__Render")},
    "0x00513870": {("0x004eb5e5", "D3DStateCache__UseDefaultRenderState")},
    "0x005138b0": {("0x004eb58b", "D3DStateCache__UseDefaultRenderState")},
    "0x00513930": {("0x0042c946", "CConsole__RenderLoadingScreen"), ("0x0046701b", "CFrontEnd__DrawPanel")},
    "0x005139a0": {("0x00557ca1", "CDXTexture__LoadTextureFromFile_Core"), ("0x0055711f", "CTextureSequence__EnsureLoaded")},
    "0x00513a10": {("0x00559d88", "CDXTexture__Deserialize"), ("0x004f7bb5", "CUMTexture__RecreateTextureResource")},
}

STRING_EXPECTATIONS = {
    "string-0063de64.tsv": r"Using impure device\x0a",
    "string-0063de7c.tsv": r"Using pure device\x0a",
    "string-0063de90.tsv": r"Driver version : %d\x0a",
    "string-0063dea8.tsv": r"Driver         : %s\x0a",
    "string-0063dec0.tsv": r"Description    : %s\x0a",
    "string-0063ded8.tsv": r"Graphics card info\x0a",
    "string-0063deec.tsv": r"------------------\x0a",
    "string-0063df00.tsv": "D3D Error! ",
    "string-0063df0c.tsv": "Create texture failed: %s",
}

CORE_DOC_TOKENS = (
    TASK,
    "d3d-state-cache-core-wave849",
    "0x00513640 CEngine__GetConstant32",
    "0x00513650 CEngine__PrintGraphicsCardInfo",
    "0x00513730 CEngine__MarkDeviceResetPending",
    "0x00513760 CEngine__TextureFormatField32FD4ToIndex",
    "0x00513770 CEngine__DeviceCall68_CheckError",
    "0x005137d0 CEngine__DeviceCall6C",
    "0x00513800 IUnknown__ReleaseIfNonNull_ReturnZero",
    "0x00513820 D3DStateCache__SetStateCached",
    "0x005138b0 D3DStateCache__SetState114Cached",
    "0x005139a0 CEngine__CreateTextureOrFatal",
    "0x00513a10 CEngine__CreateTextureUnchecked",
    "5691/6098 = 93.33%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime d3d behavior proven",
    "runtime texture behavior proven",
    "runtime device behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact d3d enum names proven",
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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 765,
        "pre-instructions.tsv": 637,
        "pre-decompile/index.tsv": 13,
        "pre-context-metadata.tsv": 19,
        "pre-context-decompile/index.tsv": 19,
        "pre-release-field-xref-instructions.tsv": 76,
        "pre-return-use-xref-instructions.tsv": 208,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 765,
        "post-instructions.tsv": 637,
        "post-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    xrefs: dict[str, set[tuple[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        target = normalize_address(row["target_addr"])
        xrefs.setdefault(target, set()).add((normalize_address(row.get("from_addr", "")), row.get("from_function", "")))

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == spec["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in spec["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | set(spec["tags"])
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == spec["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == spec["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(EXPECTED_XREFS[address].issubset(xrefs.get(address, set())), f"xref set mismatch for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=1 signature_updated=6 comment_only_updated=13 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=13 skipped=0 renamed=1 would_rename=1 signature_updated=6 comment_only_updated=13 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 765 rows",
        "post-instructions.log": "Wrote 637 instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5691",
        "queue-probe.log": "Commentless functions: 407",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave849.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave849_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "READBACK_BAD", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_log = read_text(BASE / "apply.log")
    for address, spec in TARGETS.items():
        require(f"APPLY_OK: {address} {spec['name']} {spec['signature']}" in apply_log, f"missing APPLY_OK for {address}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 407, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5691, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5691, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00513a80", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "PlatformInput__GetKeyState3Core", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171936647 or backup.get("totalBytes") == 171936647.0, "backup byte count mismatch", failures)
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
        TRACKING_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        ENGINE_DOC: (
            TASK,
            "0x00513760 CEngine__TextureFormatField32FD4ToIndex",
            "0x00513820 D3DStateCache__SetStateCached",
            "0x005139a0 CEngine__CreateTextureOrFatal",
            BACKUP_PATH,
        ),
        LTSHELL_DOC: (
            TASK,
            "0x00513650 CEngine__PrintGraphicsCardInfo",
            "cg_whatami",
            "Graphics card info",
            BACKUP_PATH,
        ),
        DXTEXTURE_DOC: (
            TASK,
            "0x00513640 CEngine__GetConstant32",
            "0x00513a10 CEngine__CreateTextureUnchecked",
            "CDXTexture__LoadTextureFromFile_Core",
            BACKUP_PATH,
        ),
        CUMTEXTURE_DOC: (
            TASK,
            "0x00513760 CEngine__TextureFormatField32FD4ToIndex",
            "0x00513a10 CEngine__CreateTextureUnchecked",
            "CUMTexture__RecreateTextureResource",
            BACKUP_PATH,
        ),
        DXMESHTVB_DOC: (
            TASK,
            "0x00513770 CEngine__DeviceCall68_CheckError",
            "0x005137d0 CEngine__DeviceCall6C",
            "CDXMeshVB__BuildStaticVB",
            BACKUP_PATH,
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-d3d-state-cache-core-wave849")
        == r"py -3 tools\ghidra_d3d_state_cache_core_wave849_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave849 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20504 for row in attempts), "missing Wave849 attempt row", failures)


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
        print("Wave849 D3D state/cache core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave849 D3D state/cache core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
