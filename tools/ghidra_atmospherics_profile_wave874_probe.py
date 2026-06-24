#!/usr/bin/env python3
"""Validate Wave874 atmospherics-profile read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave874-atmospherics-profile"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_atmospherics_profile_wave874_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ATMOS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Atmospherics.cpp" / "_index.md"
DXSNOW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXSnow.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave874 atmospherics profile"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-201600_post_wave874_atmospherics_profile_verified"
NEXT_HEAD = "0x00555be0 CVBufTexture__DrawSpriteEx"
STRICT_PROXY = "5872/6113 = 96.06%"

TARGETS = {
    "0x00554e80": {
        "name": "DXSnow__StaticInitPrimaryTransformGlobals",
        "signature": "void __cdecl DXSnow__StaticInitPrimaryTransformGlobals(void)",
        "tokens": ("0x00622ab8", "0x009c7f88", "high-importance weather-renderer setup"),
        "tags": {"function-boundary-created", "pointer-table-00622ab8", "static-initializer", "transform-globals"},
    },
    "0x00554f50": {
        "name": "DXSnow__StaticInitDisableSnowConfig",
        "signature": "void __cdecl DXSnow__StaticInitDisableSnowConfig(void)",
        "tokens": ("0x00622abc", "DISABLE_SNOW", "CVar__Init", "0x00554f70"),
        "tags": {"function-boundary-created", "pointer-table-00622ab8", "static-initializer", "disable-snow-config"},
    },
    "0x00554f70": {
        "name": "DXSnow__StaticDestroyDisableSnowConfig",
        "signature": "void __cdecl DXSnow__StaticDestroyDisableSnowConfig(void)",
        "tokens": ("0x00554f61", "CTweak__dtor_base_thunk_004530a0", "DISABLE_SNOW"),
        "tags": {"function-boundary-created", "static-cleanup", "disable-snow-config"},
    },
    "0x00554f80": {
        "name": "CAtmosphericsProfile__ctor",
        "signature": "void * __fastcall CAtmosphericsProfile__ctor(void * this)",
        "tokens": ("0x00404a98", "0x005e5974", "+0x388=9.0", "+0x3a0=10.0"),
        "tags": {"raw-commentless-head", "constructor", "vtable-005e5974"},
    },
    "0x00555010": {
        "name": "CAtmosphericsProfile__VFunc00_GetNameString",
        "signature": "char * __fastcall CAtmosphericsProfile__VFunc00_GetNameString(void * this)",
        "tokens": ("0x005e5974", "0x0065246c", "Snow"),
        "tags": {"function-boundary-created", "vtable-slot", "vtable-005e5974", "snow-name"},
    },
    "0x00555410": {
        "name": "CAtmosphericsProfile__ReleaseResources",
        "signature": "void __fastcall CAtmosphericsProfile__ReleaseResources(void * this)",
        "tokens": ("0x005e5984", "CTexture__DecrementRefCountFromNameField", "CVBufTexture__dtor", "CVertexShader__DecrementLiveReferenceCount"),
        "tags": {"vtable-slot", "resource-release", "vtable-005e5974"},
    },
    "0x00555460": {
        "name": "CAtmosphericsProfile__RenderOverlay",
        "signature": "void __fastcall CAtmosphericsProfile__RenderOverlay(void * this)",
        "tokens": ("0x00555a09", "0x009c6914", "0x0066018c", "this+0x08"),
        "tags": {"overlay-renderer", "snow-density", "matrix-copy"},
    },
    "0x00555600": {
        "name": "CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay",
        "signature": "void __fastcall CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay(void * this)",
        "tokens": ("0x005e5974", "Atmospherics__UpdateAll", "CDXTexture__GetAnimatedFrame", "CAtmosphericsProfile__RenderOverlay"),
        "tags": {"function-boundary-created", "vtable-slot", "vtable-005e5974", "snow-update", "overlay-renderer"},
    },
    "0x00555af0": {
        "name": "DXSnow__StaticZeroOverlayVectorGlobals",
        "signature": "void __cdecl DXSnow__StaticZeroOverlayVectorGlobals(void)",
        "tokens": ("0x00622ac0", "0x009c8000", "0x009c8008"),
        "tags": {"function-boundary-created", "pointer-table-00622ab8", "static-initializer", "overlay-vector-globals"},
    },
    "0x00555b10": {
        "name": "DXSnow__StaticInitOverlayTransformGlobals",
        "signature": "void __cdecl DXSnow__StaticInitOverlayTransformGlobals(void)",
        "tokens": ("0x00622ac4", "0x009c7fd0", "important renderer setup evidence"),
        "tags": {"function-boundary-created", "pointer-table-00622ab8", "static-initializer", "overlay-transform-globals"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "atmospherics-profile-wave874",
    "wave874-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-corrected",
    "important-weather-renderer-infrastructure",
    "high-importance-low-local-evidence-density",
    "atmospherics",
    "dxsnow",
}

CORE_ANCHORS = (
    TASK,
    "atmospherics-profile-wave874",
    "0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals",
    "0x00554f50 DXSnow__StaticInitDisableSnowConfig",
    "0x00554f70 DXSnow__StaticDestroyDisableSnowConfig",
    "0x00554f80 CAtmosphericsProfile__ctor",
    "0x00555010 CAtmosphericsProfile__VFunc00_GetNameString",
    "0x00555410 CAtmosphericsProfile__ReleaseResources",
    "0x00555460 CAtmosphericsProfile__RenderOverlay",
    "0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay",
    "0x00555af0 DXSnow__StaticZeroOverlayVectorGlobals",
    "0x00555b10 DXSnow__StaticInitOverlayTransformGlobals",
    "DISABLE_SNOW",
    "high-importance weather-renderer infrastructure with low local-evidence density, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime snow/weather visual behavior proven",
    "runtime console/cvar behavior proven",
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
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 173,
        "pre-decompile/index.tsv": 3,
        "pre-vtable.tsv": 8,
        "pre-helper-metadata.tsv": 16,
        "pre-pointer-table-code-instructions.tsv": 735,
        "pre-pointer-table-code-xrefs.tsv": 7,
        "post-create-metadata.tsv": 10,
        "post-create-decompile/index.tsv": 10,
        "post-create-vtable.tsv": 8,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 10,
        "post-instructions.tsv": 601,
        "post-decompile/index.tsv": 10,
        "post-vtable.tsv": 8,
        "post-pointer-table.tsv": 6,
        "post-helper-metadata.tsv": 16,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"metadata name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"metadata signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave874 static read-back", *expected["tokens"]):
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | set(expected["tags"])
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}: {dec.get('signature')}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for relative, expected in {
        "string-00652444.tsv": "DISABLE_SNOW",
        "string-0065246c.tsv": "Snow",
    }.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    vtable = read_text(BASE / "post-vtable.tsv")
    for token in (
        "CAtmosphericsProfile__VFunc00_GetNameString",
        "CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay",
        "CAtmosphericsProfile__ResetAndInitSnowResources",
        "CAtmosphericsProfile__ReleaseResources",
        "0x40f00000",
    ):
        require(token in vtable, f"missing vtable token: {token}", failures)

    pointer_table = read_text(BASE / "post-pointer-table.tsv")
    for token in (
        "DXSnow__StaticInitPrimaryTransformGlobals",
        "DXSnow__StaticInitDisableSnowConfig",
        "DXSnow__StaticZeroOverlayVectorGlobals",
        "DXSnow__StaticInitOverlayTransformGlobals",
        "00556420\t<none>",
        "00556b80\t<none>",
    ):
        require(token in pointer_table, f"missing pointer-table token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "create-dry.log": "created=0 would_create=7 already_exists=0 renamed=0 would_rename=0 failed=0",
        "create-apply.log": "created=7 would_create=0 already_exists=0 renamed=7 would_rename=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 10 rows",
        "post-instructions.log": "Wrote 601 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-helper-metadata.log": "targets=16 found=16 missing=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5872",
        "queue-probe.log": "Commentless functions: 241",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave874.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave874_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "FAIL:", "BADADDR:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 241, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5872, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5872, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00555be0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CVBufTexture__DrawSpriteEx", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (172592007, 172592007.0), "backup byte count mismatch", failures)
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
        ATMOS_DOC,
        DXSNOW_DOC,
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
        scripts.get("test:ghidra-atmospherics-profile-wave874") == r"py -3 tools\ghidra_atmospherics_profile_wave874_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave874 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20529 for row in attempts), "missing Wave874 attempt row", failures)


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
        print("Wave874 atmospherics-profile probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave874 atmospherics-profile probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
