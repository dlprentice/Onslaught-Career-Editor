#!/usr/bin/env python3
"""Validate Wave618 CDXTrees head Ghidra artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave618-cdxtrees-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtrees_head_wave618_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTREES_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTrees.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x0055a350": (
        "CDXTrees__CDXTrees",
        "void * __thiscall CDXTrees__CDXTrees(void * this)",
        ("0x009cc148", "0x005e59d8", "constructor"),
        ("cdxtrees-wave618", "constructor", "vtable-005e59d8"),
    ),
    "0x0055a360": (
        "CDXTrees__scalar_deleting_dtor",
        "void * __thiscall CDXTrees__scalar_deleting_dtor(void * this, byte delete_flags)",
        ("vtable 0x005e59d8 slot 0", "RET 0x4", "delete_flags"),
        ("cdxtrees-wave618", "scalar-deleting-dtor", "ret-0x4"),
    ),
    "0x0055a380": (
        "CDXTrees__dtor",
        "void __thiscall CDXTrees__dtor(void * this)",
        ("0x00512d50", "tail-jumps", "vtable 0x005e59d8"),
        ("cdxtrees-wave618", "destructor", "device-object-tail"),
    ),
    "0x0055a390": (
        "CDXTrees__Init",
        "void __thiscall CDXTrees__Init(void * this)",
        ("CEngine__Init", "CShaderBase__Init", "this+0x08"),
        ("cdxtrees-wave618", "init", "shader-base"),
    ),
    "0x0055a3b0": (
        "CDXTrees__ReleaseBuffers",
        "int __thiscall CDXTrees__ReleaseBuffers(void * this)",
        ("vtable 0x005e59d8 slot 4", "CVBufTexture", "returns 0"),
        ("cdxtrees-wave618", "release-buffers", "vtable-slot-4"),
    ),
    "0x0055a400": (
        "CDXTrees__Reset",
        "void __thiscall CDXTrees__Reset(void * this)",
        ("CGame__ShutdownRestartLoop", "CEngine__Shutdown", "CShaderBase"),
        ("cdxtrees-wave618", "reset", "render-list-unlink"),
    ),
    "0x0055a420": (
        "CDXTrees__BuildTreeGeometry",
        "void __thiscall CDXTrees__BuildTreeGeometry(void * this)",
        ("CGame__LoadLevel", "0x68-byte CVBufTexture", "0x02000000"),
        ("cdxtrees-wave618", "build-tree-geometry", "tree-flag-02000000"),
    ),
    "0x0055aa10": (
        "CDXTrees__Render",
        "void __thiscall CDXTrees__Render(void * this)",
        ("CDXEngine__Render", "CDXTrees__BuildTreeGeometry", "CVBufTexture__RenderIndexedNoValidate"),
        ("cdxtrees-wave618", "render", "billboard-render"),
    ),
    "0x0055ae40": (
        "CDXTrees__HideTree",
        "void __thiscall CDXTrees__HideTree(void * this, void * tree_object)",
        ("CRTTree__Destructor", "RET 0x4", "tree_object+0x30"),
        ("cdxtrees-wave618", "hide-tree", "vertex-stride-0x24"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime vegetation proven",
    "runtime tree rendering proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        token = token.replace("\\\\", "\\")
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_clean_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back signature mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    clean_expectations = {
        "apply-wave618-dry.log": {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave618-apply.log": {"updated": 9, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave618-final-dry.log": {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    }
    for name, expected in clean_expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=9 found=9 missing=0",),
        "post-context-tags.log": ("rows=9 missing=0",),
        "post-context-xrefs.log": ("Wrote 12 rows",),
        "post-context-instructions.log": ("Wrote 333 instruction rows", "targets=9 missing=0"),
        "post-callsite-instructions.log": ("Wrote 378 instruction rows", "targets=18 missing=0"),
        "post-hidetree-tail-instructions.log": ("Wrote 61 instruction rows", "targets=1 missing=0"),
        "post-context-decompile.log": ("targets=9 dumped=9 missing=0 failed=0",),
        "post-vtable-slots.log": ("targets=1 rows=16",),
        "post-function-quality.log": ("total_functions=6093 commented_functions=3185",),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 9:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 9")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, tag_tokens) in TARGETS.items():
        row = by_address.get(address)
        if not row:
            failures.append(f"post-context-metadata missing {address}")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} status mismatch: {row['status']}")
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in tag_tokens:
            if token not in tags:
                failures.append(f"{address} missing tag {token}")


def check_xrefs_and_callsites(failures: list[str]) -> None:
    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "0055a350\tCDXTrees__CDXTrees\t0055a325",
        "0055a360\tCDXTrees__scalar_deleting_dtor\t005e59d8",
        "0055a390\tCDXTrees__Init\t00449d0f\t004499d0\tCEngine__Init",
        "0055a400\tCDXTrees__Reset\t0046cc20\t0046ca70\tCGame__ShutdownRestartLoop",
        "0055a400\tCDXTrees__Reset\t004498ae\t00449890\tCEngine__Shutdown",
        "0055a420\tCDXTrees__BuildTreeGeometry\t0046cfe2\t0046cdf0\tCGame__LoadLevel",
        "0055aa10\tCDXTrees__Render\t0053e7c1\t0053e2e0\tCDXEngine__Render",
        "0055ae40\tCDXTrees__HideTree\t004de001\t004ddfd0\tCRTTree__Destructor",
    ):
        require_tokens("post-context-xrefs.tsv", xrefs, (token,), failures)

    callsites = read_text(BASE / "post-callsite-instructions.tsv")
    for token in (
        "0x0055a325\t0x0055a325\tTARGET\t0\t0x0055a325\t<none>\t<no_function>\tCALL\t0x0055a350",
        "0x00449d0f\t0x00449d0f\tTARGET\t0\t0x00449d0f\t0x004499d0\tCEngine__Init\tCALL\t0x0055a390",
        "0x0046cfe2\t0x0046cfe2\tTARGET\t0\t0x0046cfe2\t0x0046cdf0\tCGame__LoadLevel\tCALL\t0x0055a420",
        "0x0053e7c1\t0x0053e7c1\tTARGET\t0\t0x0053e7c1\t0x0053e2e0\tCDXEngine__Render\tCALL\t0x0055aa10",
        "0x004de001\t0x004de001\tTARGET\t0\t0x004de001\t0x004ddfd0\tCRTTree__Destructor\tCALL\t0x0055ae40",
        "0x0055a37d\t0x0055a37d\tTARGET\t0\t0x0055a37d\t0x0055a360\tCDXTrees__scalar_deleting_dtor\tRET\t0x4",
        "0x0055aa00\t0x0055aa00\tTARGET\t0\t0x0055aa00\t0x0055a420\tCDXTrees__BuildTreeGeometry\tRET",
    ):
        require_tokens("post-callsite-instructions.tsv", callsites, (token,), failures)

    hidetree_tail = read_text(BASE / "post-hidetree-tail-instructions.tsv")
    require_tokens(
        "post-hidetree-tail-instructions.tsv",
        hidetree_tail,
        ("0x0055af84\t0x0055af84\tAFTER\t3\t0x0055af87\t0x0055ae40\tCDXTrees__HideTree\tRET\t0x4",),
        failures,
    )

    vtable_slots = read_text(BASE / "post-vtable-slots.tsv")
    for token in (
        "005e59d8\t0\t005e59d8\t0x0055a360\t0055a360\t0055a360\tCDXTrees__scalar_deleting_dtor",
        "005e59d8\t1\t005e59dc\t0x005019c0\t005019c0\t005019c0\tVFuncSlot_09_005019c0",
        "005e59d8\t4\t005e59e8\t0x0055a3b0\t0055a3b0\t0055a3b0\tCDXTrees__ReleaseBuffers",
        "005e59d8\t5\t005e59ec\t0x3f000000\t3f000000\t<none>\t<no_function>",
    ):
        require_tokens("post-vtable-slots.tsv", vtable_slots, (token,), failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    expected_backup = {
        "BackupPath": "G:\\GhidraBackups\\BEA_20260520-025200_post_wave618_cdxtrees_head_verified",
        "SourceFileCount": 19,
        "BackupFileCount": 19,
        "SourceBytes": 161680263,
        "BackupBytes": 161680263,
        "DiffCount": 0,
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")

    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    expected_signals = {
        "commentlessFunctionCount": 2908,
        "undefinedSignatureCount": 1247,
        "paramSignatureCount": 1056,
        "legacyWeakNameCount": 0,
        "uncertainOwnerNameCount": 0,
        "helperAddressNameCount": 0,
        "wrapperAddressNameCount": 0,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0055d5e0" or head.get("name") != "DirectSoundCreate8":
        failures.append(f"queue head mismatch: {head}")


def check_docs(failures: list[str]) -> None:
    doc_tokens = {
        PUBLIC_NOTE: ("Wave618", "0x0055d5e0 DirectSoundCreate8", "3185/6093 = 52.27%"),
        FUNCTION_INDEX: ("Latest saved-correction note: Wave618", "DXTrees.cpp", "3140/6093 = 51.53%"),
        DXTREES_DOC: ("## Wave618 Static Read-Back Note", "void __thiscall CDXTrees__HideTree", "0x0055d5e0 DirectSoundCreate8"),
        CAMPAIGN: ("after Wave618", "Current CDXTrees head follow-up", "2908"),
        BACKLOG: ("Ghidra CDXTrees head Wave618", "ApplyCDXTreesHeadWave618.java", "DiffCount=0"),
        LEDGER: ("Ghidra CDXTrees head Wave618", "0x0055d5e0 DirectSoundCreate8", "Runtime vegetation rendering"),
        ATTEMPT_LOG: ("\"attempt_id\":20273", "Ghidra CDXTrees head Wave618", "\"readback\":\"verified\""),
        PACKAGE_JSON: ("test:ghidra-cdxtrees-head-wave618", "tools\\\\ghidra_cdxtrees_head_wave618_probe.py --check"),
    }
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20274:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    if tracking.get("counters", {}).get("ledger_rows") != 1014:
        failures.append("tracking ledger_rows mismatch")
    if tracking.get("counters", {}).get("attempt_rows") != 20274:
        failures.append("tracking attempt_rows mismatch")
    if "Wave618 CDXTrees head hardening" not in tracking.get("current_focus", ""):
        failures.append("tracking current_focus missing Wave618")

    for path, tokens in doc_tokens.items():
        text = read_text(path)
        require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.relative_to(ROOT)} overclaims: {token}")


def run_check() -> list[str]:
    failures: list[str] = []
    for step in (
        check_logs,
        check_metadata_and_tags,
        check_xrefs_and_callsites,
        check_backup_and_queue,
        check_docs,
    ):
        try:
            step(failures)
        except Exception as exc:  # pragma: no cover - command-line probe reports all hard failures.
            failures.append(f"{step.__name__} raised {exc.__class__.__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave618 CDXTrees head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave618 CDXTrees head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
