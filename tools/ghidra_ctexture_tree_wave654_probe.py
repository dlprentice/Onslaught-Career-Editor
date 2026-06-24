#!/usr/bin/env python3
"""Validate Wave654 CTexture/RB-tree helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave654-ctexture-tree"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_tree_wave654_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "ctexture-rbtree-wave654",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00572e40": {
        "name": "CTexture__DestroyNodeTreeAndStorage",
        "signature": "void __fastcall CTexture__DestroyNodeTreeAndStorage(void * tree_state)",
        "tags": {"ctexture", "red-black-tree", "tree-destruction", "shared-sentinel"},
        "comment_tokens": ("tree/list state", "DAT_009d0c44", "owner/template identity"),
        "decompile": "00572e40_CTexture__DestroyNodeTreeAndStorage.c",
        "decompile_tokens": ("tree_state", "CTexture__DestroySubtreeRecursive", "OID__FreeObject_Callback"),
    },
    "0x005738e0": {
        "name": "CTexture__EraseNodeFromTree",
        "signature": "void __thiscall CTexture__EraseNodeFromTree(void * this, void * unused_out_slot, void * node, void * unused_context)",
        "tags": {"ctexture", "red-black-tree", "erase-node", "delete-fixup", "shared-sentinel", "ret-0xc"},
        "comment_tokens": ("delete fixup", "CFastVB tree range erase", "static Ghidra naming evidence"),
        "decompile": "005738e0_CTexture__EraseNodeFromTree.c",
        "decompile_tokens": ("node", "DAT_009d0c44", "unused_context"),
    },
    "0x00573cc0": {
        "name": "CTexture__DestroySubtreeRecursive",
        "signature": "void __stdcall CTexture__DestroySubtreeRecursive(void * node)",
        "tags": {"ctexture", "red-black-tree", "subtree-destruction", "shared-sentinel", "ret-0x4"},
        "comment_tokens": ("recursive subtree destructor", "right children", "DAT_009d0c44"),
        "decompile": "00573cc0_CTexture__DestroySubtreeRecursive.c",
        "decompile_tokens": ("node", "OID__FreeObject_Callback", "DAT_009d0c44"),
    },
    "0x00574080": {
        "name": "CTexture__WalkNodeListUntilSentinel",
        "signature": "void __cdecl CTexture__WalkNodeListUntilSentinel(void * node_slot)",
        "tags": {"ctexture", "red-black-tree", "sentinel-walk", "shared-sentinel", "narrow-static-claim"},
        "comment_tokens": ("no visible side effect", "narrow static observation", "concrete iterator semantics"),
        "decompile": "00574080_CTexture__WalkNodeListUntilSentinel.c",
        "decompile_tokens": ("node_slot", "DAT_009d0c44", "return"),
    },
    "0x005740a0": {
        "name": "CTexture__RotateTreeLeft",
        "signature": "void __thiscall CTexture__RotateTreeLeft(void * this, void * pivot_node)",
        "tags": {"ctexture", "red-black-tree", "left-rotate", "insert-delete-fixup", "shared-sentinel", "ret-0x4"},
        "comment_tokens": ("left-rotation helper", "pivot_node", "DAT_009d0c44"),
        "decompile": "005740a0_CTexture__RotateTreeLeft.c",
        "decompile_tokens": ("pivot_node", "DAT_009d0c44", "+ 8"),
    },
    "0x00574100": {
        "name": "CTexture__InitTreeNodeParentAndKey",
        "signature": "void * __stdcall CTexture__InitTreeNodeParentAndKey(void * parent_node, int node_color)",
        "tags": {"ctexture", "red-black-tree", "node-allocation", "parent-link", "node-color", "ret-0x8"},
        "comment_tokens": ("0x14-byte node", "parent_node", "returns the new node in EAX"),
        "decompile": "00574100_CTexture__InitTreeNodeParentAndKey.c",
        "decompile_tokens": ("parent_node", "node_color", "return pvVar1"),
    },
    "0x00574120": {
        "name": "CTexture__TreeIteratorNext",
        "signature": "void __fastcall CTexture__TreeIteratorNext(void * iterator_slot)",
        "tags": {"ctexture", "red-black-tree", "iterator-next", "shared-sentinel"},
        "comment_tokens": ("in-order successor", "iterator_slot", "DAT_009d0c44"),
        "decompile": "00574120_CTexture__TreeIteratorNext.c",
        "decompile_tokens": ("iterator_slot", "DAT_009d0c44", "+ 8"),
    },
    "0x00574180": {
        "name": "CTexture__TreeIteratorPrev",
        "signature": "void __fastcall CTexture__TreeIteratorPrev(void * iterator_slot)",
        "tags": {"ctexture", "red-black-tree", "iterator-prev", "shared-sentinel"},
        "comment_tokens": ("in-order predecessor", "iterator_slot", "DAT_009d0c44"),
        "decompile": "00574180_CTexture__TreeIteratorPrev.c",
        "decompile_tokens": ("iterator_slot", "DAT_009d0c44", "+ 8"),
    },
}

DOC_TOKENS = (
    "Wave654 CTexture/RB-tree helper hardening",
    "3551",
    "2542",
    "757",
    "0x00572f00 CFastVB__InitDwordSpanBuilderState_00572f00",
    "G:\\GhidraBackups\\BEA_20260520-195520_post_wave654_ctexture_tree_verified",
)

OVERCLAIM_TOKENS = (
    "runtime texture behavior proven",
    "concrete node layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
    "fully recovered",
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


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "BAD:", "BADNAME:", "MISSING:", "Save blocked", "Read-back"):
        if bad_token in text:
            failures.append(f"{path.name} contains bad token: {bad_token}")


def check_metadata(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-metadata.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-metadata target set mismatch: {sorted(set(rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        require_tokens(f"{address} comment", row.get("comment", ""), spec["comment_tokens"], failures)


def check_tags(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-tags.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-tags target set mismatch: {sorted(set(rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        missing = sorted((COMMON_TAGS | spec["tags"]) - tags)
        if missing:
            failures.append(f"{address} missing tags: {missing}")


def check_decompiles(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "decompile-post" / "index.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"decompile index target set mismatch: {sorted(set(rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row and row.get("status") != "OK":
            failures.append(f"{address} decompile status mismatch: {row.get('status')}")
        text = read_text(BASE / "decompile-post" / spec["decompile"])
        require_tokens(f"{address} decompile", text, spec["decompile_tokens"], failures)


def check_counts_and_logs(failures: list[str]) -> None:
    for path, expected in (
        (BASE / "apply-wave654-dry.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "signature_updated": 8, "missing": 0, "bad": 0}),
        (BASE / "apply-wave654-apply.log", {"updated": 8, "skipped": 0, "renamed": 0, "would_rename": 0, "signature_updated": 8, "missing": 0, "bad": 0}),
        (BASE / "apply-wave654-final-dry.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0}),
    ):
        require_log_summary(path, expected, failures)

    counts = {
        "post-metadata": len(read_tsv_rows(BASE / "post-metadata.tsv")),
        "post-tags": len(read_tsv_rows(BASE / "post-tags.tsv")),
        "post-xrefs": len(read_tsv_rows(BASE / "post-xrefs.tsv")),
        "post-instructions": len(read_tsv_rows(BASE / "post-instructions.tsv")),
        "post-decompile": len(read_tsv_rows(BASE / "decompile-post" / "index.tsv")),
    }
    expected_counts = {
        "post-metadata": 8,
        "post-tags": 8,
        "post-xrefs": 13,
        "post-instructions": 392,
        "post-decompile": 8,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            failures.append(f"{key} count mismatch: {counts.get(key)} != {expected}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    expected_signals = {
        "commentlessFunctionCount": 2542,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 757,
    }
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    first = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if first.get("address") != "0x00572f00" or first.get("name") != "CFastVB__InitDwordSpanBuilderState_00572f00":
        failures.append(f"queue head mismatch: {first}")

    backup = read_json(BACKUP_SUMMARY)
    destination = backup.get("BackupPath", backup.get("backupPath", ""))
    if "post_wave654_ctexture_tree_verified" not in destination:
        failures.append(f"backup destination mismatch: {destination}")
    if backup.get("DiffCount", backup.get("diffCount")) != 0:
        failures.append(f"backup DiffCount mismatch: {backup.get('DiffCount', backup.get('diffCount'))}")
    if int(backup.get("FileCount", backup.get("fileCount", 0))) != 19:
        failures.append(f"backup FileCount mismatch: {backup.get('FileCount', backup.get('fileCount'))}")


def check_docs(failures: list[str]) -> None:
    docs = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "texture doc": read_text(TEXTURE_DOC),
        "fastvb doc": read_text(FASTVB_DOC),
        "ghidra reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
        "tracking": read_text(TRACKING),
    }
    for label, text in docs.items():
        require_tokens(label, text, DOC_TOKENS, failures)
        for bad in OVERCLAIM_TOKENS:
            if bad in text:
                failures.append(f"{label} contains overclaim token: {bad}")
    package_json = read_text(PACKAGE_JSON)
    if "test:ghidra-ctexture-tree-wave654" not in package_json:
        failures.append("package.json missing Wave654 npm script")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Run validation checks.")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    failures: list[str] = []
    check_metadata(failures)
    check_tags(failures)
    check_decompiles(failures)
    check_counts_and_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave654 CTexture/RB-tree probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave654 CTexture/RB-tree probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
