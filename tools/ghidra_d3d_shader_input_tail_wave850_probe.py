#!/usr/bin/env python3
"""Validate Wave850 D3D shader/input tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave850-d3d-shader-input-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_d3d_shader_input_tail_wave850_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LTSHELL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ltshell.cpp" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
VERTEX_SHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-081702_post_wave850_d3d_shader_input_tail_verified"
NEXT_HEAD = "0x005140e0 CDXEngine__CaptureAviFrame"
TASK = "Wave850 D3D shader/input tail"

TARGETS = {
    "0x00513a80": {
        "name": "PlatformInput__GetKeyState3Core",
        "signature": "bool __thiscall PlatformInput__GetKeyState3Core(void * this, int key)",
        "tokens": ("Wave850 static read-back", "source PCController/PCPlatform KeyOn", "this+0x332e4+key"),
        "tags": {"controller", "input", "source-keyon"},
    },
    "0x00513a90": {
        "name": "PlatformInput__GetKeyOnceCore",
        "signature": "bool __thiscall PlatformInput__GetKeyOnceCore(void * this, int key)",
        "tokens": ("Wave850 static read-back", "source PCController/PCPlatform KeyOnce", "0x00855424"),
        "tags": {"controller", "input", "source-keyonce", "consumed-key-queue"},
    },
    "0x00513b60": {
        "name": "D3DStateCache__ForceSlotMode4or5",
        "signature": "void __stdcall D3DStateCache__ForceSlotMode4or5(int state_slot)",
        "tokens": ("Wave850 static read-back", "DAT_008557f4", "vtable slot 0x10c"),
        "tags": {"direct3d-device", "force-mode", "state-cache", "vtable-0x10c"},
    },
    "0x00513c70": {
        "name": "CEngine__DrawIndexedPrimitives",
        "signature": "void __thiscall CEngine__DrawIndexedPrimitives(void * this, int primitive_type, int arg2, int arg3, int arg4, int arg5)",
        "tokens": ("Wave850 static read-back", "vtable slot 0x148", "MinIndex forced to 0"),
        "tags": {"direct3d-device", "draw-indexed", "source-reference-ltshell", "vtable-0x148"},
    },
    "0x00513ca0": {
        "name": "CEngine__SetVertexShadersEnabled",
        "signature": "int __thiscall CEngine__SetVertexShadersEnabled(void * this, uchar enabled)",
        "tokens": ("Wave850 static read-back", "vtable slot 0x134", "DAT_00889070"),
        "tags": {"direct3d-device", "hresult", "shader-path-toggle", "vertex-shader"},
    },
    "0x00513d20": {
        "name": "D3DBufferRegistry__MoveToFreeList",
        "signature": "void __stdcall D3DBufferRegistry__MoveToFreeList(int buffer_node)",
        "tokens": ("Wave850 static read-back", "DAT_00889074", "DAT_00889078"),
        "tags": {"buffer-registry", "direct3d-device", "free-list", "resource-lifetime"},
    },
    "0x00513e00": {
        "name": "CEngine__DeviceCall118_WithZeroOut",
        "signature": "void __fastcall CEngine__DeviceCall118_WithZeroOut(void * this)",
        "tokens": ("Wave850 static read-back", "vtable slot 0x118", "zeroed stack dword"),
        "tags": {"device-vtable-0x118", "direct3d-device", "stack-output"},
    },
    "0x00513e20": {
        "name": "CEngine__SetShaderObject",
        "signature": "void __thiscall CEngine__SetShaderObject(void * this, void * shader_obj)",
        "tokens": ("Wave850 static read-back", "CVertexShader__GetVertexDeclarationToken", "shader_obj+0x28"),
        "tags": {"direct3d-device", "shader-object", "state-cache", "vertex-shader"},
    },
    "0x00513e90": {
        "name": "CEngine__SetVertexShaderHandleCached",
        "signature": "void __thiscall CEngine__SetVertexShaderHandleCached(void * this, int shader_handle)",
        "tokens": ("Wave850 static read-back", "DAT_00889068", "slot 0x164"),
        "tags": {"direct3d-device", "source-reference-ltshell", "state-cache", "vertex-shader"},
    },
    "0x00513ec0": {
        "name": "CEngine__SetVertexShaderHandleRaw",
        "signature": "void __thiscall CEngine__SetVertexShaderHandleRaw(void * this, int shader_handle)",
        "tokens": ("Wave850 static read-back", "clears DAT_0088906c", "slot 0x170"),
        "tags": {"direct3d-device", "raw-state", "source-reference-ltshell", "vertex-shader"},
    },
    "0x00513f20": {
        "name": "CEngine__CreatePixelShaderFromText",
        "signature": "int __thiscall CEngine__CreatePixelShaderFromText(void * this, char * shader_text, void * release_after_create)",
        "tokens": ("Wave850 static read-back", "CVertexShader__CompileScriptWithDirectiveParser", "slot 0x1a8"),
        "tags": {"direct3d-device", "hresult", "pixel-shader", "shader-compile", "source-reference-ltshell"},
    },
    "0x00513ff0": {
        "name": "CEngine__DeviceCall16C_CreateVertexShaderLike",
        "signature": "int __thiscall CEngine__DeviceCall16C_CreateVertexShaderLike(void * this, int unused_arg1, int arg2, int arg3, int unused_arg4)",
        "tokens": ("Wave850 static read-back", "RET 0x10", "slot 0x16c", "CreateVertexShaderLike"),
        "tags": {"device-vtable-0x16c", "direct3d-device", "hresult", "name-corrected", "vertex-shader"},
    },
    "0x00514010": {
        "name": "IUnknown__ReleaseAndNull",
        "signature": "void __stdcall IUnknown__ReleaseAndNull(void * * object_ptr)",
        "tokens": ("Wave850 static read-back", "vtable slot 8 Release", "writes null"),
        "tags": {"com-release", "release-and-null", "resource-lifetime"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "d3d-shader-input-tail-wave850",
    "wave850-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

CORE_DOC_TOKENS = (
    TASK,
    "d3d-shader-input-tail-wave850",
    "0x00513a80 PlatformInput__GetKeyState3Core",
    "0x00513a90 PlatformInput__GetKeyOnceCore",
    "0x00513b60 D3DStateCache__ForceSlotMode4or5",
    "0x00513c70 CEngine__DrawIndexedPrimitives",
    "0x00513ca0 CEngine__SetVertexShadersEnabled",
    "0x00513d20 D3DBufferRegistry__MoveToFreeList",
    "0x00513e20 CEngine__SetShaderObject",
    "0x00513f20 CEngine__CreatePixelShaderFromText",
    "0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike",
    "0x00514010 IUnknown__ReleaseAndNull",
    "5704/6098 = 93.54%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime input behavior proven",
    "runtime rendering behavior proven",
    "runtime shader behavior proven",
    "runtime shader compilation behavior proven",
    "runtime resource lifetime behavior proven",
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
        "pre-xrefs.tsv": 74,
        "pre-instructions.tsv": 637,
        "pre-decompile/index.tsv": 13,
        "pre-context-metadata.tsv": 18,
        "pre-context-decompile/index.tsv": 18,
        "pre-xref-site-instructions.tsv": 1998,
        "pre-target-long-instructions.tsv": 1937,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 74,
        "post-instructions.tsv": 637,
        "post-decompile/index.tsv": 13,
        "post-context-metadata.tsv": 18,
        "post-context-decompile/index.tsv": 18,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=13 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=13 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=13 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 74 rows",
        "post-instructions.log": "Wrote 637 instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-context-metadata.log": "targets=18 found=18 missing=0",
        "post-context-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5704",
        "queue-probe.log": "Commentless functions: 394",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave850.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave850_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 394, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5704, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5704, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005140e0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXEngine__CaptureAviFrame", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171969415 or backup.get("totalBytes") == 171969415.0, "backup byte count mismatch", failures)
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
            "0x00513c70 CEngine__DrawIndexedPrimitives",
            "0x00513e20 CEngine__SetShaderObject",
            "0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike",
            BACKUP_PATH,
        ),
        LTSHELL_DOC: (
            TASK,
            "D3D_DrawIndexedPrimitive",
            "D3D_SetVertexShader",
            "D3D_CreatePixelShader",
            BACKUP_PATH,
        ),
        PCPLATFORM_DOC: (
            TASK,
            "PlatformInput__GetKeyState3Core",
            "PlatformInput__GetKeyOnceCore",
            "PCPlatform KeyOn/KeyOnce",
            BACKUP_PATH,
        ),
        CONTROLLER_DOC: (
            TASK,
            "0x00513a80 PlatformInput__GetKeyState3Core",
            "0x00513a90 PlatformInput__GetKeyOnceCore",
            "CPCController__GetKeyOnce",
            BACKUP_PATH,
        ),
        VERTEX_SHADER_DOC: (
            TASK,
            "0x00513e20 CEngine__SetShaderObject",
            "0x00513f20 CEngine__CreatePixelShaderFromText",
            "0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike",
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
        scripts.get("test:ghidra-d3d-shader-input-tail-wave850")
        == r"py -3 tools\ghidra_d3d_shader_input_tail_wave850_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave850 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20505 for row in attempts), "missing Wave850 attempt row", failures)


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
        print("Wave850 D3D shader/input tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave850 D3D shader/input tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
