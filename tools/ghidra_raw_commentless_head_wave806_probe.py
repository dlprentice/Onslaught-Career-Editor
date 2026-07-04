#!/usr/bin/env python3
"""Validate Wave806 raw-commentless-head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave806-raw-commentless-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_raw_commentless_head_wave806_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXMEMBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMemBuffer.cpp.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
RESOURCE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ResourceAccumulator.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-102416_post_wave806_raw_commentless_head_verified"

TARGETS = {
    "0x0048ddf0": {
        "pre_name": "thunk_DXMemBuffer__Close",
        "name": "CDXMemBuffer__Close_Thunk",
        "signature": "bool __fastcall CDXMemBuffer__Close_Thunk(void * this)",
        "comment": ("Wave806 static read-back", "0x00548c00 CDXMemBuffer__Close", "CParticleSet__LoadParticleSetFile"),
        "tags": {"close-thunk", "dx-mem-buffer", "particle-file-context", "renamed", "signature-hardened", "tranche-head"},
        "xrefs": {("0x004cdb46", "CParticleSet__LoadParticleSetFile", "UNCONDITIONAL_CALL")},
    },
    "0x0048de90": {
        "pre_name": "CDXLandscape__ClearPendingHudMarkerHandle",
        "name": "CDXLandscape__ClearMixerDetailTextureHandle",
        "signature": "void * __thiscall CDXLandscape__ClearMixerDetailTextureHandle(void * this)",
        "comment": ("Wave806 static read-back correction", "0x0067a7d0", "older HUD-marker wording is superseded"),
        "tags": {"dx-landscape", "global-texture-handle", "mixer-detail-texture", "signature-corrected", "renamed"},
        "xrefs": {("0x00544a09", "CDXLandscape__Constructor", "UNCONDITIONAL_CALL")},
    },
    "0x0048dea0": {
        "pre_name": "CDXLandscape__ReleasePendingHudMarker",
        "name": "CDXLandscape__ReleaseMixerDetailTextureRef",
        "signature": "void __cdecl CDXLandscape__ReleaseMixerDetailTextureRef(void)",
        "comment": ("Wave806 static read-back", "0x0067a7d0", "CTexture__DecrementRefCountFromNameField", "CDXLandscape__Destructor"),
        "tags": {"dx-landscape", "mixer-detail-texture", "texture-refcount", "renamed", "signature-hardened"},
        "xrefs": {
            ("0x00544ad8", "CDXLandscape__Destructor", "UNCONDITIONAL_CALL"),
            ("0x005d79a2", "Unwind@005d7980", "UNCONDITIONAL_CALL"),
        },
    },
    "0x0048dec0": {
        "pre_name": "CResourceAccumulator__LoadMixerDetailTexture",
        "name": "CResourceAccumulator__LoadMixerDetailTexture",
        "signature": "void __cdecl CResourceAccumulator__LoadMixerDetailTexture(int detail_index)",
        "comment": ("Wave806 static read-back", "this+0x1094", "detail%.2d.tga", "0x0067a7d0"),
        "tags": {"resource-accumulator", "mixer-detail-texture", "texture-load", "signature-hardened"},
        "xrefs": {("0x00491124", "CHeightField__DeserializeMapAndInitResources", "UNCONDITIONAL_CALL")},
    },
    "0x004f27e0": {
        "pre_name": "CHud__DecrementCounter9C",
        "name": "CTexture__DecrementRefCountFromNameField",
        "signature": "void __thiscall CTexture__DecrementRefCountFromNameField(void * this)",
        "comment": ("Wave806 static read-back correction", "*(this+0x9c)", "115 callers", "superseding the older HUD-specific label"),
        "tags": {"texture", "refcount", "name-field-subobject", "renamed", "signature-hardened"},
        "xrefs": {("0x0048deac", "CDXLandscape__ReleaseMixerDetailTextureRef", "UNCONDITIONAL_CALL")},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "raw-commentless-head-wave806",
    "wave806-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
}

CORE_ANCHORS = (
    "Wave806 raw commentless head",
    "raw-commentless-head-wave806",
    "0x0048ddf0 CDXMemBuffer__Close_Thunk",
    "0x0048de90 CDXLandscape__ClearMixerDetailTextureHandle",
    "0x0048dea0 CDXLandscape__ReleaseMixerDetailTextureRef",
    "0x0048dec0 CResourceAccumulator__LoadMixerDetailTexture",
    "0x004f27e0 CTexture__DecrementRefCountFromNameField",
    "0x0048f2f0 CDXLandscape__SetUpdateBoundsAndRebuildVB",
    "5581/6098 = 91.52%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime texture lifetime proven",
    "runtime terrain rendering behavior proven",
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
        "pre-wave-metadata.tsv": 5,
        "pre-wave-tags.tsv": 5,
        "pre-wave-xrefs.tsv": 120,
        "pre-wave-instructions.tsv": 525,
        "pre-wave-decompile/index.tsv": 5,
        "pre-caller-helper-metadata.tsv": 3,
        "pre-caller-helper-instructions.tsv": 615,
        "pre-caller-helper-decompile/index.tsv": 3,
        "pre-refcount-xrefs.tsv": 115,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 120,
        "post-instructions.tsv": 525,
        "post-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    string_rows = read_tsv(BASE / "string-0062d80c.tsv")
    require(string_rows and string_rows[0].get("cstring") == r"mixers\detail%.2d.tga", "detail texture string mismatch", failures)

    pre = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-wave-metadata.tsv")}
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), []).append(row)

    for address, spec in TARGETS.items():
        pre_row = pre.get(address)
        require(pre_row is not None, f"missing pre metadata for {address}", failures)
        if pre_row is not None:
            require(pre_row.get("name") == spec["pre_name"], f"pre name mismatch at {address}", failures)

        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == spec["name"], f"post name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"post signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"post status mismatch at {address}", failures)
            for token in spec["comment"]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | set(spec["tags"])
            require(expected_tags.issubset(actual_tags), f"missing tags at {address}: {expected_tags - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == spec["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == spec["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        actual_xrefs = {
            (normalize_address(xref.get("from_addr", "")), xref.get("from_function", ""), xref.get("ref_type", ""))
            for xref in xrefs.get(address, [])
        }
        for expected in spec["xrefs"]:
            require(expected in actual_xrefs, f"missing xref at {address}: {expected}", failures)

    require(len(xrefs.get("0x004f27e0", [])) == 115, "refcount xref count mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=4 signature_updated=5 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "Read-back signature mismatch at 0x004f27e0",
        "apply-dry-after-readback-correction.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-readback-correction.log": "SUMMARY: updated=1 skipped=4 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 120 rows",
        "post-instructions.log": "Wrote 525 instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5581",
        "queue-probe.log": "Commentless functions: 517",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave806.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave806_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("LockException" not in text, f"LockException in {relative}", failures)
        if relative != "apply.log":
            for bad in ("BADNAME:", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1", "Input file not found"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        else:
            require("SUMMARY: updated=4 skipped=0 renamed=4 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=1" in text, "apply.log mismatch not preserved", failures)
            require("REPORT: Save succeeded" in text, "initial apply save report missing", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 517, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5581, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5581, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0048f2f0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXLandscape__SetUpdateBoundsAndRebuildVB", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171314055 or backup.get("totalBytes") == 171314055.0, "backup byte count mismatch", failures)
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
        DXMEMBUFFER_DOC: ("Wave806", "raw-commentless-head-wave806", "0x0048ddf0 CDXMemBuffer__Close_Thunk", "0x00548c00 CDXMemBuffer__Close", BACKUP_PATH),
        DXLANDSCAPE_DOC: ("Wave806", "raw-commentless-head-wave806", "0x0048de90 CDXLandscape__ClearMixerDetailTextureHandle", "0x0048dea0 CDXLandscape__ReleaseMixerDetailTextureRef", "0x0067a7d0", BACKUP_PATH),
        RESOURCE_DOC: ("Wave806", "raw-commentless-head-wave806", "0x0048dec0 CResourceAccumulator__LoadMixerDetailTexture", r"mixers\detail%.2d.tga", "0x00491060 CHeightField__DeserializeMapAndInitResources", BACKUP_PATH),
        TEXTURE_DOC: ("Wave806", "raw-commentless-head-wave806", "0x004f27e0 CTexture__DecrementRefCountFromNameField", "CHud__DecrementCounter9C", "115 callers", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-raw-commentless-head-wave806") == r"py -3 tools\ghidra_raw_commentless_head_wave806_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave806 raw commentless head" for row in ledger_rows), "missing Wave806 ledger row", failures)
    require(any(row.get("task") == "Wave806 raw commentless head" and row.get("attempt_id") == 20461 for row in attempts), "missing Wave806 attempt row", failures)


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
        print("Wave806 raw-commentless-head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave806 raw-commentless-head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
