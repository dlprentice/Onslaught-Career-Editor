#!/usr/bin/env python3
"""Validate Wave1071 texel-unpack head/middle read-only review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1071-texel-unpack-head-mid-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_unpack_head_mid_review_wave1071_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1071_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

CORE_DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

OWNER_DOC_TOKENS = {
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md": (
        "Wave1071",
        "texel-unpack-head-mid-review-wave1071",
        "0x00584d78 CFastVB__UnpackTexels_Bits565ToFloat4",
        "0x00585bd3 CFastVB__TexelUnpackProfile_scalar_deleting_dtor",
        "0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4",
        "1319/1560 = 84.55%",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md": (
        "Wave1071",
        "texel-unpack-head-mid-review-wave1071",
        "0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4",
        "0x0058579b CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne",
        "0x00585cb0 CTexture__UnpackTexels_Signed8_8_ToFloat4_RG",
        "1319/1560 = 84.55%",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md": (
        "Wave1071",
        "texel-unpack-head-mid-review-wave1071",
        "0x00585576 CDXTexture__UnpackTexels_Bits332ToFloat4",
        "0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4",
        "0x00585e9f CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG",
        "1319/1560 = 84.55%",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md": (
        "Wave1071",
        "texel-unpack-head-mid-review-wave1071",
        "0x0058546f CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4",
        "owner/layout identity remains unproven",
        BACKUP_PATH,
    ),
}

TARGETS = [
    "0x00584b5f",
    "0x00584c04",
    "0x00584cc3",
    "0x00584d78",
    "0x00584e32",
    "0x00584ee9",
    "0x00584fae",
    "0x00585072",
    "0x00585161",
    "0x00585220",
    "0x005852d5",
    "0x00585380",
    "0x0058546f",
    "0x00585576",
    "0x0058562d",
    "0x005856b8",
    "0x0058577f",
    "0x0058579b",
    "0x0058584f",
    "0x0058586b",
    "0x00585908",
    "0x00585924",
    "0x005859bc",
    "0x005859d8",
    "0x00585a5f",
    "0x00585a7b",
    "0x00585b19",
    "0x00585b35",
    "0x00585bd3",
    "0x00585bef",
    "0x00585c0b",
    "0x00585c94",
    "0x00585cb0",
    "0x00585d6b",
    "0x00585d87",
    "0x00585da3",
    "0x00585e83",
    "0x00585e9f",
    "0x00585f6b",
    "0x00585f87",
    "0x00585fa3",
]

CONTEXT_TARGETS = {
    "0x0058609e": "CFastVB__TexelUnpackProfile_005ea020__ctor",
    "0x00586994": "CFastVB__InitTexelUnpackVTable_005ea118",
    "0x005869b0": "CTexture__UnpackTexels_Bits16_16_16_ToFloat4",
    "0x00586a71": "CFastVB__TexelUnpackProfileRegistry_005ea138__ctor",
    "0x00586ec7": "CFastVB__InitTexelUnpackVTable_005ea198",
    "0x00587dd6": "CFastVB__TexelUnpackProfileRegistry_005ea254__ctor",
    "0x00587e82": "CFastVB__CreateTexelUnpackProfileByFormat",
}

DOC_TOKENS = (
    "Wave1071",
    "texel-unpack-head-mid-review-wave1071",
    "0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4",
    "0x0058546f CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4",
    "0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4",
    "0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor",
    "0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4",
    "812/1408 = 57.67%",
    "1319/1560 = 84.55%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime texture output behavior proven",
    "runtime codec behavior proven",
    "exact source identity proven",
    "rebuild parity proven",
)


def norm(address: str) -> str:
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 41,
        "primary-tags.tsv": 41,
        "primary-xrefs.tsv": 83,
        "primary-instructions.tsv": 1856,
        "primary-decompile/index.tsv": 41,
        "context-metadata.tsv": 7,
        "context-xrefs.tsv": 11,
        "context-instructions.tsv": 707,
        "context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    quality = {norm(row["address"]): row for row in read_tsv(QUEUE_TSV)}
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "primary-xrefs.tsv")

    for address in TARGETS:
        qrow = quality.get(address)
        row = metadata.get(address)
        require(qrow is not None, f"missing queue row for {address}", failures)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None or qrow is None:
            continue

        require(row.get("name") == qrow.get("name"), f"name mismatch at {address}", failures)
        require(row.get("signature") == qrow.get("signature"), f"signature mismatch at {address}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        expected_wave = "Wave672" if TARGETS.index(address) < 16 else "Wave673"
        require(expected_wave in comment, f"missing historical wave token at {address}: {expected_wave}", failures)
        require("Static metadata only" in comment, f"missing bounded static token at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = {"static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-hardened"}
            if expected_wave == "Wave672":
                required.update({"texel-unpack-head-wave672", "wave672-readback-verified"})
            else:
                required.update({"texel-unpack-continuation-wave673", "wave673-readback-verified"})
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec is not None:
            require(dec.get("name") == row.get("name"), f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == row.get("signature"), f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    require(any(norm(row["target_addr"]) == "0x0058546f" and row["ref_type"] == "DATA" for row in xrefs), "missing 0x0058546f DATA xref", failures)
    require(any(norm(row["target_addr"]) == "0x00584b5f" and norm(row["from_addr"]) == "0x005e9f40" for row in xrefs), "missing head table xref", failures)
    require(any(norm(row["target_addr"]) == "0x00585fa3" and row["ref_type"] == "DATA" for row in xrefs), "missing tail table xref", failures)

    context = {norm(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=41 found=41 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=41 missing=0",
        "primary-xrefs.log": "Wrote 83 rows",
        "primary-instructions.log": "Wrote 1856 function-body instruction rows",
        "primary-decompile.log": "targets=41 dumped=41 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-xrefs.log": "Wrote 11 rows",
        "context-instructions.log": "Wrote 707 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(float(backup.get("totalBytes")) == 174721927.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    for path in CORE_DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-texel-unpack-head-mid-review-wave1071")
        == r"py -3 tools\ghidra_texel_unpack_head_mid_review_wave1071_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1071-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1071 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1071 texel unpack head/mid review" for row in ledger), "missing ledger row", failures)
    require(any(row.get("task") == "Wave1071 texel unpack head/mid review" and row.get("attempt_id") == 20653 for row in attempts), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave1071 texel-unpack head/middle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1071 texel-unpack head/middle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
