#!/usr/bin/env python3
"""Validate Wave678 CDXTexture dispatch-prelude read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave678-cdxtexture-dispatch-prelude"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_dispatch_prelude_wave678_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BASE_TAGS = {
    "static-reaudit",
    "cdxtexture-dispatch-prelude-wave678",
    "wave678-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00588cc6": (
        "CDXTexture__ProjectPointToPlaneAndScale",
        "void __stdcall CDXTexture__ProjectPointToPlaneAndScale(float * source_point, float * plane_point, float * plane_normal, float scale, float * out_point)",
        BASE_TAGS | {"cdxtexture", "vector-math", "plane-projection", "scale-about-plane-point", "dispatch-prelude"},
    ),
    "0x00589094": (
        "CDXTexture__RegistryValueEqualsDword",
        "int __stdcall CDXTexture__RegistryValueEqualsDword(int expected_registry_type, void * value_name, void * out_value_buffer, int value_byte_count)",
        BASE_TAGS | {"cdxtexture", "registry-query", "direct3d-config", "registry-type-check", "dispatch-prelude"},
    ),
    "0x005890f1": (
        "CDXTexture__CpuHasMmxFeature",
        "int __cdecl CDXTexture__CpuHasMmxFeature(void)",
        BASE_TAGS | {"cdxtexture", "cpu-feature", "cpuid", "mmx-feature", "dispatch-prelude"},
    ),
    "0x0058926b": (
        "CFastVB__InitDispatchTableByCpuFeature",
        "int __stdcall CFastVB__InitDispatchTableByCpuFeature(int requested_mode)",
        BASE_TAGS | {"cfastvb", "dispatch-table", "cpu-feature-dispatch", "direct3d-registry-override", "simd-dispatch", "dispatch-prelude"},
    ),
}

DOC_TOKENS = (
    "Wave678 CDXTexture dispatch prelude",
    "cdxtexture-dispatch-prelude-wave678",
    "0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale",
    "0x0058926b CFastVB__InitDispatchTableByCpuFeature",
    "0x00589200 Catch@00589200",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime CPU dispatch proven",
    "exact dispatch ABI proven",
    "registry policy proven",
    "SIMD feature policy proven",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    require(len(metadata) == len(TARGETS), f"metadata row count is {len(metadata)}", failures)
    require(len(tags) == len(TARGETS), f"tag row count is {len(tags)}", failures)
    require(len(decompile_index) == len(TARGETS), f"decompile index row count is {len(decompile_index)}", failures)
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 71, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 148, "instruction row count mismatch", failures)

    for address, (name, expected_signature, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave678 static read-back" in comment, f"missing Wave678 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}: {tag_row.get('status')}", failures)

        decompile_row = decompile_index.get(address)
        require(decompile_row is not None, f"missing decompile index for {address}", failures)
        if decompile_row is not None:
            require(decompile_row.get("signature") == expected_signature, f"decompile signature mismatch at {address}", failures)
            require(decompile_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected_exact = {
        "apply-wave678-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0",
        "apply-wave678-apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0",
        "apply-wave678-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-instructions.log": "targets=4 missing=0",
        "post-xrefs.log": "Wrote 71 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)
    require("Wrote 148 instruction rows" in read_text(BASE / "post-instructions.log"), "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-cdxtexture-dispatch-prelude-wave678" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyCDXTextureDispatchPreludeWave678.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave678 CDXTexture dispatch prelude" in text, f"Wave678 missing from {path.relative_to(ROOT)}", failures)
        require("cdxtexture-dispatch-prelude-wave678" in text, f"Wave678 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 164367239, "backup byteCount mismatch", failures)
    require("post_wave678_cdxtexture_dispatch_prelude_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2259, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 478, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00589200", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "Catch@00589200", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave678 CDXTexture dispatch prelude", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave678 CDXTexture dispatch prelude", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20333, "attempt id mismatch", failures)
    require(len(ledger) == 1074, "ledger row count mismatch", failures)
    require(len(attempts) == 20334, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave678 CDXTexture dispatch prelude"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1074, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20334, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1065, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20334, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave678 CDXTexture dispatch prelude" in text, f"Wave678 missing from {path.name}", failures)
        require("cdxtexture-dispatch-prelude-wave678" in text, f"Wave678 tag missing from {path.name}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return non-zero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_logs(failures)
        check_docs(failures)
        check_state(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{type(exc).__name__}: {exc}")

    status = "PASS" if not failures else "FAIL"
    print("Ghidra CDXTexture dispatch prelude Wave678 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
