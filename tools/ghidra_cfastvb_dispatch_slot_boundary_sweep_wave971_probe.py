#!/usr/bin/env python3
"""Validate Wave971 CFastVB dispatch-slot boundary sweep artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave971-cfastvb-dispatch-final-sweep"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_dispatch_slot_boundary_sweep_wave971_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-181005_post_wave971_cfastvb_dispatch_slot_boundary_sweep_verified"

TARGETS = {
    "0x005a4fee": ("B0", "0x005985e0"),
    "0x005a50f9": ("E0", "0x00598630"),
    "0x005a5bd7": ("0C", "0x005984a4"),
    "0x005a5e09": ("2C", "0x005984d5"),
    "0x005a5ed8": ("68", "0x0059853e"),
    "0x005a5f28": ("6C", "0x00598545"),
    "0x005a6013": ("70", "0x0059854c"),
    "0x005a77bc": ("A4", "0x005985c2"),
    "0x005a923f": ("10", "0x00598658"),
    "0x005a996b": ("48", "0x00598506"),
    "0x005a9987": ("04", "0x00598496"),
    "0x005a9abe": ("CC", "0x005985f4"),
    "0x005a9b2f": ("C4", "0x0059861c"),
    "0x005a9c03": ("C8", "0x0059864e"),
    "0x005aa5c0": ("E4", "0x00598673"),
    "0x005aa82d": ("44", "0x005984ff"),
    "0x005aa8c5": ("C0", "0x005985fe"),
    "0x005aa90e": ("B8", "0x00598608"),
    "0x005aa951": ("BC", "0x00598644"),
    "0x005aa9fc": ("08", "0x0059849d"),
    "0x005aaa7e": ("20", "0x005984c0"),
    "0x005aaadd": ("40", "0x005984f8"),
    "0x005aac0f": ("D8", "0x005985ea"),
    "0x005aac80": ("D0", "0x00598612"),
    "0x005aad48": ("D4", "0x0059863a"),
    "0x005aae26": ("30", "0x005984dc"),
    "0x005aae69": ("34", "0x005984e3"),
    "0x005aaf4d": ("58", "0x00598522"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cfastvb-dispatch-slot-boundary-sweep-wave971",
    "wave971-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "dispatch-table-target",
    "cfastvb",
    "packed-math",
    "stack-locked",
    "comment-hardened",
    "signature-hardened",
}

CORE_TOKENS = (
    "Wave971",
    "cfastvb-dispatch-slot-boundary-sweep-wave971",
    "0x005a4fee CFastVB__DispatchOp_SlotB0_005a4fee",
    "0x005a77bc CFastVB__DispatchOp_SlotA4_005a77bc",
    "0x005aaadd CFastVB__DispatchOp_Slot40_005aaadd",
    "0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags",
    "390/1454 = 26.82%",
    "6198/6198 = 100.00%",
    BACKUP_PATH,
    "function-boundary recovery",
)

OVERCLAIMS = (
    "runtime CPU dispatch/math/render behavior proven",
    "rebuild parity proven",
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
        "init-body.tsv": 85,
        "dispatch-store-targets.txt": 72,
        "would-create-targets.txt": 28,
        "would-create-xrefs.tsv": 28,
        "post-metadata.tsv": 28,
        "post-tags.tsv": 28,
        "post-xrefs.tsv": 28,
        "post-body-instructions.tsv": 1821,
        "post-decompile/index.tsv": 28,
    }
    for relative, expected in expected_counts.items():
        path = BASE / relative
        if relative.endswith(".txt"):
            actual = len([line for line in read_text(path).splitlines() if line.strip()])
        else:
            actual = len(read_tsv(path))
        require(actual == expected, f"{relative} count mismatch: {actual} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, (slot, store) in TARGETS.items():
        name = f"CFastVB__DispatchOp_Slot{slot}_{address[2:]}"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == f"int {name}(void)", f"signature mismatch at {address}: {row.get('signature')}", failures)
            comment = row.get("comment", "")
            for token in ("Wave971", f"slot +0x{slot.lower()}", store, "stack-locked as int(void)"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)

        xref_row = xrefs.get(address)
        require(xref_row is not None, f"missing xref for {address}", failures)
        if xref_row is not None:
            require(normalize_address(xref_row.get("from_addr", "")) == store, f"xref store mismatch at {address}", failures)
            require(xref_row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


def check_logs_and_queue(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=28 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=28 skipped=0 created=28 would_create=0 renamed=0 would_rename=0 signature_updated=28 comment_only_updated=56 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=28 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=28 found=28 missing=0",
        "post-tags.log": "rows=28 missing=0",
        "post-xrefs.log": "Wrote 28 rows",
        "post-body-instructions.log": "targets=28 missing=0",
        "post-decompile.log": "targets=28 dumped=28 missing=0 failed=0",
        "export-functions-quality-wave971.log": "total_functions=6198 commented_functions=6198",
        "wave971_queue_probe.log": "Total functions: 6198",
    }
    aliases = {
        "export-functions-quality-wave971.log": QUEUE / "export-functions-quality-wave971.log",
        "wave971_queue_probe.log": QUEUE / "wave971_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue = read_json(QUEUE / "static-reaudit-queue.json")
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6198, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain owner count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173706119, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, FASTVB_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cfastvb-dispatch-slot-boundary-sweep-wave971")
        == r"py -3 tools\ghidra_cfastvb_dispatch_slot_boundary_sweep_wave971_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave971 CFastVB dispatch slot boundary sweep" for row in ledger_rows), "missing Wave971 ledger row", failures)
    require(any(row.get("task") == "Wave971 CFastVB dispatch slot boundary sweep" and row.get("attempt_id") == 20567 for row in attempts), "missing Wave971 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave971 CFastVB dispatch-slot boundary sweep probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave971 CFastVB dispatch-slot boundary sweep probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
