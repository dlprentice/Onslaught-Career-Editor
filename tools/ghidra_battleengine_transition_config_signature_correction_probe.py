#!/usr/bin/env python3
"""Validate BattleEngine transition/config Ghidra name and signature corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-transition-config-signature-correction" / "current"

TARGETS = {
    "0x0040eeb0": {
        "name": "CBattleEngine__FinishedPlayingCurrentAnimation",
        "signatureTokens": [
            "int",
            "__thiscall",
            "CBattleEngine__FinishedPlayingCurrentAnimation",
            "void * this",
        ],
        "commentTokens": [
            "CBattleEngine::FinishedPlayingCurrentAnimation",
            "flytowalk/walktofly",
            "Corrects the prior CUnit owner label",
            "runtime animation behavior",
            "layout remain unproven",
        ],
        "decompileTokens": [
            "CBattleEngine__FinishedPlayingCurrentAnimation",
            "this",
            "flytowalk",
            "walktofly",
            "PlayAnimationByNameIfPresent",
        ],
    },
    "0x0040ef20": {
        "name": "CBattleEngine__GroundParticleEffect",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CBattleEngine__GroundParticleEffect",
            "void * this",
        ],
        "commentTokens": [
            "CBattleEngine::GroundParticleEffect",
            "water/terrain height",
            "land or water ground-effect particle",
            "Corrects the prior CMonitor helper/effect label",
            "runtime particle behavior",
        ],
        "decompileTokens": [
            "CBattleEngine__GroundParticleEffect",
            "this",
            "CStaticShadows__SampleShadowHeightBilinear",
            "CParticleManager__CreateEffect",
            "0x1c",
            "0x24",
        ],
    },
    "0x0040f110": {
        "name": "CEngine__ClampBurstStartTimeFloorNow",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CEngine__ClampBurstStartTimeFloorNow",
            "void * this",
        ],
        "commentTokens": [
            "Signature/comment hardening",
            "this+0x60c",
            "current event-time global",
            "Exact owner field layout",
            "remain unproven",
        ],
        "decompileTokens": [
            "CEngine__ClampBurstStartTimeFloorNow",
            "this",
            "0x60c",
            "005d85bc",
            "00672fd0",
        ],
    },
    "0x0040f2f0": {
        "name": "BattleEngineConfigurations__GetConfiguration",
        "signatureTokens": [
            "void *",
            "__cdecl",
            "BattleEngineConfigurations__GetConfiguration",
            "int configurationId",
        ],
        "commentTokens": [
            "UBattleEngineConfigurations::GetConfiguration",
            "configurationId",
            "global configuration count",
            "Corrects the prior CBattleEngine weapon-profile label",
            "layout and runtime configuration coverage remain unproven",
        ],
        "decompileTokens": [
            "BattleEngineConfigurations__GetConfiguration",
            "configurationId",
            "00660250",
            "00660200",
            "006602a0",
            "0xa8",
        ],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "battleengine-transition-config-signature-correction.json"

STALE_TOKENS = [
    "CUnit__FinishedPlayingCurrentAnimation",
    "CMonitor__SpawnGroundOrAirImpactEffect",
    "CBattleEngine__GetWeaponProfileByIndex",
    "void __fastcall CEngine__ClampBurstStartTimeFloorNow(int param_1)",
    "param_1",
    "param_2",
    "param_3",
]

OVERCLAIM_TOKENS = [
    "runtime animation behavior proven",
    "runtime particle behavior proven",
    "proves runtime particle behavior",
    "proves runtime configuration behavior",
    "concrete cbattleengine layout proven",
    "concrete cbattleenginedata layout proven",
    "exact retail class layout proven",
]


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
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


def build_report(
    *,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    failures: list[str] = []
    stale_hits: list[dict[str, str]] = []
    overclaim_hits: list[dict[str, str]] = []
    target_reports: dict[str, dict[str, object]] = {}

    signature_dry = parse_update_summary(read_text(signature_dry_log_path))
    signature_apply = parse_update_summary(read_text(signature_apply_log_path))

    if signature_dry != {"updated": 0, "skipped": len(TARGETS), "missing": 0, "bad": 0}:
        failures.append(f"unexpected signature dry summary {signature_dry}")
    if signature_apply != {"updated": len(TARGETS), "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected signature apply summary {signature_apply}")

    for address, expected in TARGETS.items():
        normalized = normalize_address(address)
        metadata = find_row(metadata_rows, "address", normalized)
        index = find_row(index_rows, "address", normalized)
        decompile_path = decompile_file_for(decompile_dir, normalized)
        decompile_text = read_text(decompile_path) if decompile_path else ""
        combined = "\n".join(
            [
                metadata.get("name", "") if metadata else "",
                metadata.get("signature", "") if metadata else "",
                metadata.get("comment", "") if metadata else "",
                index.get("name", "") if index else "",
                index.get("signature", "") if index else "",
                decompile_text,
            ]
        )

        if metadata is None:
            failures.append(f"{normalized}: missing metadata row")
        elif metadata.get("name") != expected["name"]:
            failures.append(f"{normalized}: name mismatch {metadata.get('name')} != {expected['name']}")
        if index is None:
            failures.append(f"{normalized}: missing decompile index row")
        elif index.get("name") != expected["name"]:
            failures.append(f"{normalized}: decompile index name mismatch {index.get('name')} != {expected['name']}")
        if decompile_path is None:
            failures.append(f"{normalized}: missing decompile file")

        signature = (metadata or {}).get("signature", "")
        missing_signature = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature:
            failures.append(f"{normalized}: signature tokens missing {missing_signature} from {signature!r}")

        comment = (metadata or {}).get("comment", "")
        missing_comment = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment:
            failures.append(f"{normalized}: comment tokens missing {missing_comment}")

        missing_decompile = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile:
            failures.append(f"{normalized}: decompile tokens missing {missing_decompile}")

        for token in STALE_TOKENS:
            if token_present(combined, token):
                stale_hits.append({"address": normalized, "token": token})
                failures.append(f"{normalized}: stale token {token!r} still present")

        for token in OVERCLAIM_TOKENS:
            if token_present(combined, token):
                overclaim_hits.append({"address": normalized, "token": token})
                failures.append(f"{normalized}: overclaim token {token!r} present")

        xrefs_for_target = [
            row
            for row in xref_rows
            if normalize_address(row.get("target_addr", "")) == normalized
            or normalize_address(row.get("target_addr", "")) == normalize_address(normalized[2:])
        ]
        instructions_for_target = [
            row for row in instruction_rows if normalize_address(row.get("target_addr", "")) == normalized
        ]

        target_reports[normalized] = {
            "name": (metadata or {}).get("name"),
            "signature": signature,
            "comment": comment,
            "decompilePath": relative(decompile_path),
            "xrefRows": len(xrefs_for_target),
            "instructionRows": len(instructions_for_target),
        }

    status = "PASS" if not failures else "FAIL"
    return {
        "status": status,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "targetCount": len(TARGETS),
            "correctedTargets": sum(
                1 for address, target in TARGETS.items()
                if (row := find_row(metadata_rows, "address", address)) is not None and row.get("name") == target["name"]
            ),
            "staleTokenHits": len(stale_hits),
            "overclaimHits": len(overclaim_hits),
            "signatureDry": signature_dry,
            "signatureApply": signature_apply,
        },
        "targets": target_reports,
        "staleHits": stale_hits,
        "overclaimHits": overclaim_hits,
        "artifacts": {
            "signatureDry": relative(signature_dry_log_path),
            "signatureApply": relative(signature_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="return non-zero when validation fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--signature-dry-log", type=Path, default=DEFAULT_SIGNATURE_DRY)
    parser.add_argument("--signature-apply-log", type=Path, default=DEFAULT_SIGNATURE_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    args = parser.parse_args(argv)

    report = build_report(
        signature_dry_log_path=resolve(args.signature_dry_log),
        signature_apply_log_path=resolve(args.signature_apply_log),
        metadata_path=resolve(args.metadata),
        decompile_index_path=resolve(args.decompile_index),
        decompile_dir=resolve(args.decompile_dir),
        xrefs_path=resolve(args.xrefs),
        instructions_path=resolve(args.instructions),
    )

    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
