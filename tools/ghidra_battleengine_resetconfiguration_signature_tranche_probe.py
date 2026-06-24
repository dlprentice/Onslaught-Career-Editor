#!/usr/bin/env python3
"""Validate the saved Ghidra signature tranche for BattleEngine reset-configuration helpers."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-resetconfiguration-signature-tranche" / "current"

TARGETS = {
    "0x00412650": {
        "name": "CBattleEngineJetPart__ResetConfiguration",
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__ResetConfiguration", "void * this"],
        "comment": ["signature hardening", "jet-part weapon", "config +0x50", "from param_1 to this", "runtime weapon behavior", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__ResetConfiguration", "CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "CSPtrSet__AddToTail", "+ 0x50"],
        "from": ["0x0040c695", "0x00410268"],
        "from_functions": ["CBattleEngine__UpdateConfiguration", "CBattleEngineJetPart__ctor"],
        "ret": "",
        "scope": "JetPart weapon-list reset from configuration jet weapons.",
    },
    "0x004146b0": {
        "name": "CBattleEngineWalkerPart__ResetConfiguration",
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__ResetConfiguration", "void * this"],
        "comment": ["signature hardening", "walker weapon", "config +0x40", "config +0x60", "+0x64", "from param_1 to this", "runtime weapon behavior", "remain unproven"],
        "decompile": ["CBattleEngineWalkerPart__ResetConfiguration", "CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "CSPtrSet__AddToTail", "+ 0x40", "+ 0x60"],
        "from": ["0x0040c6a4", "0x00412c06"],
        "from_functions": ["CBattleEngine__UpdateConfiguration", "CBattleEngine__InitDashMoveParams"],
        "ret": "",
        "scope": "WalkerPart weapon-list, primary weapon, and augmented weapon reset.",
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "battleengine-resetconfiguration-signature-tranche.json"

OVERCLAIMS = [
    "runtime behavior proven",
    "concrete layout proven",
    "rebuild parity proven",
    "tagged in ghidra",
    "all resetconfiguration functions complete",
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
    value = value.strip().lower()
    if not value or value in {"<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
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


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def metadata_map(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    out = {}
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
        out[row["address"]] = row
    return out


def index_map(path: Path) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get("address", "")): row for row in read_tsv(path)}


def decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


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

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary.get("updated") != 0 or dry_summary.get("skipped") < len(TARGETS) or dry_summary.get("missing") != 0 or dry_summary.get("bad") != 0:
        failures.append("dry summary is not clean")
    if apply_summary.get("updated") + apply_summary.get("skipped") < len(TARGETS) or apply_summary.get("missing") != 0 or apply_summary.get("bad") != 0:
        failures.append("apply summary is not clean")

    metadata = metadata_map(metadata_path)
    indexes = index_map(decompile_index_path)
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)

    function_reports: list[dict[str, object]] = []
    stale_signature_hits = 0
    comment_overclaims = 0
    xref_hits = 0
    ret_hits = 0

    for address, rule in TARGETS.items():
        row = metadata.get(normalize_address(address))
        index_row = indexes.get(normalize_address(address))
        if not row:
            failures.append(f"{address}: missing metadata row")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        decomp_file = decompile_file(decompile_dir, address)
        decomp_text = read_text(decomp_file)

        if name != rule["name"]:
            failures.append(f"{address}: expected name {rule['name']}, got {name or '<blank>'}")
        if not index_row or index_row.get("status") != "OK":
            failures.append(f"{address}: missing OK decompile index row")
        if not decomp_text:
            failures.append(f"{address}: missing decompile text")
        for token in rule["signature"]:
            if not has_token(signature, token):
                failures.append(f"{address}: signature missing {token!r}")
        for token in rule["comment"]:
            if not has_token(comment, token):
                failures.append(f"{address}: comment missing {token!r}")
        for token in rule["decompile"]:
            if not has_token(decomp_text, token):
                failures.append(f"{address}: decompile missing {token!r}")
        if "param_" in signature:
            stale_signature_hits += 1
            failures.append(f"{address}: param_N token survived in signature")
        for token in OVERCLAIMS:
            if has_token(comment, token):
                comment_overclaims += 1
                failures.append(f"{address}: comment overclaims {token!r}")

        expected_from = {normalize_address(v) for v in rule["from"]}
        expected_functions = set(rule["from_functions"])
        matched_xrefs = [
            xref for xref in xrefs
            if normalize_address(xref.get("target_addr", "")) == normalize_address(address)
            and normalize_address(xref.get("from_addr", "")) in expected_from
        ]
        xref_hits += len(matched_xrefs)
        observed_functions = {xref.get("from_function", "") for xref in matched_xrefs}
        missing_functions = sorted(expected_functions - observed_functions)
        if missing_functions:
            failures.append(f"{address}: missing expected xref function context: {', '.join(missing_functions)}")

        matched_rets = [
            ins for ins in instructions
            if normalize_address(ins.get("function_entry", "")) == normalize_address(address)
            and ins.get("mnemonic", "").upper() == "RET"
        ]
        if matched_rets:
            ret_hits += len(matched_rets)
        else:
            failures.append(f"{address}: missing RET instruction evidence")

        function_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "scope": rule["scope"],
                "xrefs": len(matched_xrefs),
                "retRows": len(matched_rets),
                "decompile": relative(decomp_file),
            }
        )

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-battleengine-resetconfiguration-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "summary": {
            "targets": len(TARGETS),
            "dry": dry_summary,
            "apply": apply_summary,
            "staleSignatureHits": stale_signature_hits,
            "commentOverclaims": comment_overclaims,
            "xrefHits": xref_hits,
            "retEvidenceHits": ret_hits,
        },
        "functions": function_reports,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
    )
    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(out)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
    return 0 if report["status"] == "PASS" or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
