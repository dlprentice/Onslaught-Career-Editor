#!/usr/bin/env python3
"""Validate the saved Ghidra correction for CBattleEngineJetPart functions."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-jetpart-signature-correction" / "current"

TARGETS = {
    "0x00410210": {
        "name": "CBattleEngineJetPart__ctor",
        "previous": ["CBattleEngine__InitTargetSetBucketState", "CBattleEngine__Helper_00410210"],
        "signature": ["void *", "__thiscall", "CBattleEngineJetPart__ctor", "void * this", "void * mainPart"],
        "comment": ["Source/decompile correction", "constructor", "mainPart", "ResetConfiguration", "runtime jet behavior", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__ctor", "mainPart", "CBattleEngineJetPart__ResetConfiguration"],
        "from": ["0x00404ff1"],
        "ret": "0x4",
        "scope": "JetPart constructor and main-part binding.",
    },
    "0x004102a0": {
        "name": "CBattleEngineJetPart__dtor_base",
        "previous": ["CBattleEngine__DestroySPtrSetElementsAndClear"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__dtor_base", "void * this"],
        "comment": ["Source/decompile correction", "destructor-base", "SPtrSet", "runtime weapon ownership", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__dtor_base", "CSPtrSet__Remove", "CSPtrSet__Clear"],
        "from": ["0x00405bde"],
        "ret": "",
        "scope": "JetPart destructor-base weapon set cleanup.",
    },
    "0x00410310": {
        "name": "CBattleEngineJetPart__Thrust",
        "previous": ["CGeneralVolume__HandleBoostWindowInput"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__Thrust", "void * this", "float moveY"],
        "comment": ["CBattleEngineJetPart::Thrust", "thruster", "hard-forward", "loop state", "Runtime input behavior", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__Thrust", "moveY", "+0x20", "+0x44", "+0x24"],
        "from": ["0x004d3415", "0x004d342a"],
        "ret": "0x4",
        "scope": "Jet thrust and loop-trigger input path.",
    },
    "0x00410490": {
        "name": "CBattleEngineJetPart__Turn",
        "previous": ["CGeneralVolume__ApplyInputDampingToVelocity"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__Turn", "void * this", "float moveX"],
        "comment": ["CBattleEngineJetPart::Turn", "yaw", "roll", "configuration turn rate", "Runtime input behavior", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__Turn", "moveX", "CGeneralVolume__ToDoubleIdentity", "+0x278", "+0x27c"],
        "from": ["0x004d33c1"],
        "ret": "0x4",
        "scope": "Jet turn yaw/roll input path.",
    },
    "0x00410670": {
        "name": "CBattleEngineJetPart__Pitch",
        "previous": ["CGeneralVolume__DrainLinkedObjectFromVelocity"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__Pitch", "void * this", "float moveY"],
        "comment": ["CBattleEngineJetPart::Pitch", "pitch velocity", "zoom", "transform-start", "Runtime input behavior", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__Pitch", "moveY", "CGeneralVolume__ToDoubleIdentity", "+0x280"],
        "from": ["0x004d33d6"],
        "ret": "0x4",
        "scope": "Jet pitch input path.",
    },
    "0x00410740": {
        "name": "CBattleEngineJetPart__YawLeft",
        "previous": ["CGeneralVolume__HandleAxisPositiveThresholdCross"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__YawLeft", "void * this", "float moveX"],
        "comment": ["CBattleEngineJetPart::YawLeft", "hard-left", "left barrel roll", "strafing acceleration", "Runtime input behavior"],
        "decompile": ["CBattleEngineJetPart__YawLeft", "moveX", "CSquadNormal__BuildOrientationMatrixFromEuler", "+0x3c", "+0x4c"],
        "from": ["0x004d33eb"],
        "ret": "0x4",
        "scope": "Jet left yaw/barrel-roll input path.",
    },
    "0x004109d0": {
        "name": "CBattleEngineJetPart__YawRight",
        "previous": ["CGeneralVolume__HandleAxisNegativeThresholdCross"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__YawRight", "void * this", "float moveX"],
        "comment": ["CBattleEngineJetPart::YawRight", "hard-right", "right barrel roll", "strafing acceleration", "Runtime input behavior"],
        "decompile": ["CBattleEngineJetPart__YawRight", "moveX", "CSquadNormal__BuildOrientationMatrixFromEuler", "+0x40"],
        "from": ["0x004d3400"],
        "ret": "0x4",
        "scope": "Jet right yaw/barrel-roll input path.",
    },
    "0x004114d0": {
        "name": "CBattleEngineJetPart__Gravity",
        "previous": ["CGeneralVolume__GetFlagFCScalar"],
        "signature": ["float", "__thiscall", "CBattleEngineJetPart__Gravity", "void * this"],
        "comment": ["CBattleEngineJetPart::Gravity", "energy", "0.0", "runtime flight physics", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__Gravity", "+0xfc"],
        "from": ["0x004074ee", "0x00407513"],
        "ret": "",
        "scope": "Jet gravity accessor.",
    },
    "0x00411500": {
        "name": "CBattleEngineJetPart__HandleSkimming",
        "previous": ["CMonitor__ApplyHostileEnvironmentPenalty"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__HandleSkimming", "void * this"],
        "comment": ["CBattleEngineJetPart::HandleSkimming", "terrain", "skimming", "CBattleEngine__HostileEnvironment", "runtime skimming behavior", "remain unproven"],
        "decompile": ["CBattleEngineJetPart__HandleSkimming", "CBattleEngine__HostileEnvironment"],
        "from": ["0x004114bd"],
        "ret": "",
        "scope": "Jet low-altitude skimming helper.",
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_CALLSITES = BASE / "callsite_instructions_final.tsv"
DEFAULT_OUT = BASE / "battleengine-jetpart-signature-correction.json"

OVERCLAIMS = [
    "runtime behavior proven",
    "concrete layout proven",
    "rebuild parity proven",
    "tagged in ghidra",
    "all jetpart functions complete",
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
    callsites_path: Path = DEFAULT_CALLSITES,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    callsites_path = resolve(callsites_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata", metadata_path),
        ("decompile index", decompile_index_path),
        ("xrefs", xrefs_path),
        ("instructions", instructions_path),
        ("callsite instructions", callsites_path),
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
    callsites = read_tsv(callsites_path)

    function_reports: list[dict[str, object]] = []
    stale_name_hits = 0
    stale_signature_hits = 0
    comment_overclaims = 0
    ret_evidence_hits = 0
    xref_hits = 0
    callsite_57c_hits = 0

    all_metadata_text = "\n".join(
        f"{row.get('name', '')} {row.get('signature', '')} {row.get('comment', '')}"
        for row in metadata.values()
    )

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
        if not index_row:
            failures.append(f"{address}: missing decompile index row")
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
        for old_name in rule["previous"]:
            if has_token(name, old_name) or has_token(signature, old_name):
                stale_name_hits += 1
                failures.append(f"{address}: stale name/signature token survived: {old_name}")
        if "param_" in signature:
            stale_signature_hits += 1
            failures.append(f"{address}: param_N token survived in signature")
        for token in OVERCLAIMS:
            if has_token(comment, token):
                comment_overclaims += 1
                failures.append(f"{address}: comment overclaims {token!r}")

        matched_xrefs = [
            row for row in xrefs
            if normalize_address(row.get("target_addr", "")) == normalize_address(address)
            and normalize_address(row.get("from_addr", "")) in {normalize_address(v) for v in rule["from"]}
        ]
        xref_hits += len(matched_xrefs)
        if not matched_xrefs:
            failures.append(f"{address}: missing expected xref from {', '.join(rule['from'])}")

        if rule["ret"]:
            matched_rets = [
                row for row in instructions
                if normalize_address(row.get("target_addr", "")) == normalize_address(address)
                and normalize_address(row.get("function_entry", "")) == normalize_address(address)
                and row.get("mnemonic", "").upper() == "RET"
                and row.get("operands", "") == rule["ret"]
            ]
            if matched_rets:
                ret_evidence_hits += 1
            else:
                failures.append(f"{address}: missing RET {rule['ret']} instruction evidence")

        matched_57c = [
            row for row in callsites
            if normalize_address(row.get("instruction_addr", "")) in {normalize_address(v) for v in rule["from"]}
            and has_token(row.get("operands", ""), "0x004114d0") is False
        ]
        if address not in {"0x00410210", "0x004102a0", "0x004114d0", "0x00411500"} and not any("+ 0x57c" in row.get("operands", "").lower() or "+0x57c" in row.get("operands", "").lower() for row in callsites):
            failures.append("raw callsite export does not show +0x57c jet-part dispatch context")
        if matched_57c:
            callsite_57c_hits += len(matched_57c)

        function_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "scope": rule["scope"],
                "xrefs": len(matched_xrefs),
                "decompile": relative(decomp_file),
            }
        )

    for address, rule in TARGETS.items():
        for old_name in rule["previous"]:
            if has_token(all_metadata_text, old_name):
                failures.append(f"stale metadata token remains in tranche: {old_name}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-battleengine-jetpart-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "callsiteInstructions": relative(callsites_path),
        },
        "summary": {
            "targets": len(TARGETS),
            "dry": dry_summary,
            "apply": apply_summary,
            "staleNameHits": stale_name_hits,
            "staleSignatureHits": stale_signature_hits,
            "commentOverclaims": comment_overclaims,
            "retEvidenceHits": ret_evidence_hits,
            "xrefHits": xref_hits,
            "callsiteRowsChecked": len(callsites),
            "callsiteMatchHits": callsite_57c_hits,
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
    parser.add_argument("--callsites", type=Path, default=DEFAULT_CALLSITES)
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
        callsites_path=args.callsites,
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
