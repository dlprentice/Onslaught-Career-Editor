#!/usr/bin/env python3
"""Validate the saved early-function Ghidra comment/signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "early-comment-signature-tranche" / "current"

TARGETS = {
    "0x00401000": {
        "name": "CGenericActiveReader__SetReader",
        "signatureTokens": ["void", "__thiscall", "CGenericActiveReader__SetReader", "void * this", "void * readerCell"],
        "forbiddenSignatureTokens": ["param_", "to_read"],
        "commentTokens": ["Signature/comment hardening", "rebinds", "CSPtrSet__Remove", "CMonitor__AddDeletionEvent", "runtime behavior", "remain unproven"],
        "decompileTokens": ["readerCell", "CSPtrSet__Remove", "CMonitor__AddDeletionEvent"],
        "xrefs": ["CEventManager__Flush", "CBattleEngine__Init", "ProjectileBurst__SpawnFromCurrentPreset"],
        "instructionRet": "0x4",
    },
    "0x00401040": {
        "name": "CMonitor__AddDeletionEvent",
        "signatureTokens": ["void", "__thiscall", "CMonitor__AddDeletionEvent", "void * this", "void * readerCell"],
        "forbiddenSignatureTokens": ["param_", "reader_cell"],
        "commentTokens": ["Signature/comment hardening", "deletion-event", "+0x4", "CSPtrSet__Init", "CSPtrSet__AddToHead", "runtime behavior", "remain unproven"],
        "decompileTokens": ["readerCell", "OID__AllocObject", "CSPtrSet__Init", "CSPtrSet__AddToHead"],
        "xrefs": ["CGenericActiveReader__SetReader", "CScriptEventNB__RegisterEventListener"],
        "instructionRet": "0x4",
    },
    "0x004011b0": {
        "name": "vector_constructor_iterator_nothrow",
        "signatureTokens": ["void", "__stdcall", "vector_constructor_iterator_nothrow", "void * base", "int elemSize", "int count", "void * ctorFn"],
        "forbiddenSignatureTokens": ["param_", "elem_size", "ctor_fn"],
        "commentTokens": ["Signature/comment hardening", "vector-constructor", "ret 0x10", "computed call", "CRT", "runtime behavior", "remain unproven"],
        "decompileTokens": ["base", "elemSize", "count", "ctorFn"],
        "xrefs": ["CMesh__Load", "CMeshPart__LoadFromStream", "CMeshRenderer__RenderMeshCore"],
        "instructionRet": "0x10",
    },
    "0x004014c0": {
        "name": "CFrontEndPage__ActiveNotification_NoOp",
        "signatureTokens": ["void", "__thiscall", "CFrontEndPage__ActiveNotification_NoOp", "void * this", "int fromPage"],
        "forbiddenSignatureTokens": ["__stdcall", "from_page", "param_"],
        "commentTokens": ["Signature/comment hardening", "no-op", "ret 0x4", "frontend page", "runtime behavior", "remain unproven"],
        "decompileTokens": ["fromPage"],
        "xrefs": ["DATA"],
        "instructionRet": "0x4",
    },
    "0x00403650": {
        "name": "CMeshRenderer__CopyBasisAndRefreshTime",
        "signatureTokens": ["void", "__thiscall", "CMeshRenderer__CopyBasisAndRefreshTime", "void * this", "void * srcBasis"],
        "forbiddenSignatureTokens": ["dst_basis", "dstBasis", "param_"],
        "commentTokens": ["Signature/comment hardening", "this as destination", "srcBasis", "+0xac", "DAT_00672fd0", "runtime behavior", "remain unproven"],
        "decompileTokens": ["srcBasis", "+0xac", "DAT_00672fd0"],
        "xrefs": ["CMeshRenderer__RenderMesh", "CMonitor__UpdateTrackedList_620"],
        "instructionRet": "0x4",
    },
    "0x00403f40": {
        "name": "CResourceDescriptor__ctor",
        "signatureTokens": ["void", "__fastcall", "CResourceDescriptor__ctor", "void * this"],
        "forbiddenSignatureTokens": ["param_"],
        "commentTokens": ["Signature/comment hardening", "zeros", "+0x400", "+0x414", "+0x418", "runtime behavior", "remain unproven"],
        "decompileTokens": ["+0x400", "+0x414", "+0x418"],
        "xrefs": ["CResourceDescriptorTable__ctor", "CBattleEngine__Init", "CUnit__Init"],
        "instructionRet": "",
    },
    "0x00403f80": {
        "name": "CResourceDescriptor__dtor",
        "signatureTokens": ["void", "__fastcall", "CResourceDescriptor__dtor", "void * this"],
        "forbiddenSignatureTokens": ["param_"],
        "commentTokens": ["Signature/comment hardening", "frees", "+0x414", "+0x418", "OID__FreeObject", "runtime behavior", "remain unproven"],
        "decompileTokens": ["+0x414", "+0x418", "OID__FreeObject"],
        "xrefs": ["CDXLandscape__DestroyResourceDescriptorArray_Thunk", "CResourceDescriptorTable__ctor", "CUnit__Init"],
        "instructionRet": "",
    },
    "0x004048f0": {
        "name": "CMesh__IsValidProfileIndex_1to10",
        "signatureTokens": ["int", "__cdecl", "CMesh__IsValidProfileIndex_1to10", "int profileIndex"],
        "forbiddenSignatureTokens": ["profile_index", "param_"],
        "commentTokens": ["Signature/comment hardening", "profileIndex", "1..10", "CMesh__Load", "runtime behavior", "remain unproven"],
        "decompileTokens": ["profileIndex", "0xb"],
        "xrefs": ["CMesh__Load"],
        "instructionRet": "",
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "early-comment-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
    "rebuild parity proven",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = (value or "").strip().lower()
    if value in {"", "<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join((value or "").lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_update_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def matching_ret_rows(instruction_rows: list[dict[str, str]], address: str, operand: str | None) -> list[dict[str, str]]:
    if operand is None:
        return []
    wanted = normalize_address(address)
    return [
        row
        for row in instruction_rows
        if normalize_address(row.get("target_addr", "")) == wanted
        and row.get("mnemonic", "").upper() == "RET"
        and row.get("operands", "") == operand
    ]


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata", metadata_path),
        ("decompile index", decompile_index_path),
        ("xrefs", xrefs_path),
        ("instructions", instructions_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_update_summary(read_text(dry_log_path))
    apply_summary = parse_update_summary(read_text(apply_log_path))
    if not (
        dry_summary.get("updated") == 0
        and dry_summary.get("skipped") == len(TARGETS)
        and dry_summary.get("missing") == 0
        and dry_summary.get("bad") == 0
    ):
        failures.append("dry summary is not clean")
    if not (
        apply_summary.get("updated") == len(TARGETS)
        and apply_summary.get("skipped") == 0
        and apply_summary.get("missing") == 0
        and apply_summary.get("bad") == 0
    ):
        failures.append("apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    target_reports: list[dict[str, object]] = []
    stale_signature_hits = 0
    comment_overclaims = 0
    ret_evidence_hits = 0
    xref_evidence_hits = 0

    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        if index_row is None:
            failures.append(f"decompile index missing {address}")

        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("name") != expected["name"] or row.get("status") != "OK":
            failures.append(f"name/status mismatch for {address}")
        if not comment.strip():
            failures.append(f"comment remains blank at {address}")
        for forbidden in expected["forbiddenSignatureTokens"]:
            if token_present(signature, forbidden):
                stale_signature_hits += 1
                failures.append(f"forbidden signature token remains at {address}: {forbidden}")

        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"signature tokens missing at {address}: {missing_signature_tokens}")

        missing_comment_tokens = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment_tokens:
            failures.append(f"comment tokens missing at {address}: {missing_comment_tokens}")

        lowered_comment = comment.lower()
        if any(token in lowered_comment for token in OVERCLAIM_TOKENS):
            comment_overclaims += 1
            failures.append(f"runtime/source overclaim in comment at {address}")

        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile_tokens:
            failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")

        ret_rows = matching_ret_rows(instruction_rows, address, expected.get("instructionRet"))
        if ret_rows:
            ret_evidence_hits += 1
        elif expected.get("instructionRet") is not None:
            failures.append(f"missing ret evidence at {address}: {expected.get('instructionRet')!r}")

        xref_hits = [
            row
            for row in xref_rows
            if normalize_address(row.get("target_addr", "")) == normalize_address(address)
            and any(token_present(" ".join(row.values()), token) for token in expected["xrefs"])
        ]
        if xref_hits:
            xref_evidence_hits += 1
        else:
            failures.append(f"missing xref/data evidence at {address}")

        target_reports.append(
            {
                "address": address,
                "name": expected["name"],
                "signature": signature,
                "commentLength": len(comment),
                "retEvidenceRows": len(ret_rows),
                "xrefEvidenceRows": len(xref_hits),
                "decompile": relative(decompile_file),
            }
        )

    return {
        "schema": "ghidra.early_comment_signature_tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": len(TARGETS),
            "dry": dry_summary,
            "apply": apply_summary,
            "staleSignatureHits": stale_signature_hits,
            "commentOverclaims": comment_overclaims,
            "retEvidenceHits": ret_evidence_hits,
            "xrefEvidenceHits": xref_evidence_hits,
        },
        "targets": target_reports,
        "files": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="write JSON and return non-zero on failure")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    report = build_report()
    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(out)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
