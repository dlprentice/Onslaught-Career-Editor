#!/usr/bin/env python3
"""Validate the saved CCutscene Ghidra signature/boundary tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "cutscene-wave345" / "current"

COMMON_TAGS = [
    "static-reaudit",
    "cutscene-wave345",
    "cutscene",
    "retail-binary-evidence",
]


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0043e8e0": target(
        "CCutscene__dtor_base",
        "void __fastcall CCutscene__dtor_base(void * this)",
        ["Destructor body", "Stop", "animation-name table", "CGenericActiveReader", "CComplexThing__dtor_base", "remain unproven"],
        ["CCutscene__Stop", "OID__FreeObject", "CSPtrSet__Remove", "CComplexThing__dtor_base"],
        ["destructor", "name-correction"],
    ),
    "0x0043ea90": target(
        "CCutscene__scalar_deleting_dtor",
        "void * __thiscall CCutscene__scalar_deleting_dtor(void * this, int flags)",
        ["scalar-deleting destructor wrapper", "CCutscene__dtor_base", "OID__FreeObject", "flags bit 0", "remain unproven"],
        ["CCutscene__dtor_base", "OID__FreeObject", "flags"],
        ["destructor", "vtable-slot"],
    ),
    "0x0043eab0": target(
        "CCutscene__Init",
        "void __thiscall CCutscene__Init(void * this, void * initThing)",
        ["Initializes CCutscene", "copies initThing names", "Load", "CComplexThing__Init", "remain unproven"],
        ["CCutscene__Load", "CComplexThing__Init", "initThing"],
        ["init", "vtable-slot", "name-correction"],
    ),
    "0x0043eca0": target(
        "CCutscene__ClearAnimationsAndStop",
        "void __fastcall CCutscene__ClearAnimationsAndStop(void * this)",
        ["Recovered function boundary", "calls the Stop slot", "clears 30 animation-slot lists", "DestroyRecursive", "remain unproven"],
        ["CCutsceneAnimNode__DestroyRecursive", "0x7c", "0x1e"],
        ["function-boundary", "animation-cleanup"],
    ),
    "0x0043ed20": target(
        "CCutsceneAnimNode__DestroyRecursive",
        "void * __thiscall CCutsceneAnimNode__DestroyRecursive(void * this, int flags)",
        ["animation-node recursive destructor", "owned RT object", "next pointer", "frees this", "remain unproven"],
        ["0x244", "0x248", "OID__FreeObject", "flags"],
        ["destructor", "animation-node", "name-correction"],
    ),
    "0x0043ed80": target(
        "CCutscene__Load",
        "int __thiscall CCutscene__Load(void * this)",
        ["Loads data cutscenes cut", "ChunkReader", "AddAnimation", "marks the cutscene dirty", "remain unproven"],
        ["CChunkReader__OpenFile", "data_cutscenes", "CCutscene__AddAnimation", "0x841"],
        ["loader", "signature-correction"],
    ),
    "0x0043f210": target(
        "CCutscene__AddAnimation",
        "void * __thiscall CCutscene__AddAnimation(void * this, int trackSlot, char * animationName, char * meshName, int startFrame, int durationFrames)",
        ["Allocates and links", "trackSlot", "copies animationName", "meshName", "remain unproven"],
        ["trackSlot", "animationName", "meshName", "durationFrames"],
        ["animation-node", "signature-correction"],
    ),
    "0x0043f340": target(
        "CCutscene__Start",
        "void __fastcall CCutscene__Start(void * this)",
        ["Starts cutscene playback", "current cutscene global", "active reader", "HUD", "EVENT_MANAGER", "remain unproven"],
        ["CWorld__FindThingByName", "CGenericActiveReader__SetReader", "DAT_0066ea20", "CEventManager__AddEvent_AtTime"],
        ["playback", "signature-correction"],
    ),
    "0x0043f420": target(
        "CCutscene__Stop",
        "void __fastcall CCutscene__Stop(void * this)",
        ["Stops cutscene playback", "restores camera", "ResetLandscape", "HUD", "clears the current cutscene global", "remain unproven"],
        ["CGame__SetCamera", "CCutscene__ResetLandscape", "DAT_0066ea20", "CHud__SetHudComponent"],
        ["playback", "signature-correction"],
    ),
    "0x0043f510": target(
        "CCutscene__InitAnimations",
        "void __fastcall CCutscene__InitAnimations(void * this)",
        ["Initializes animation name index table", "deduplicates animation names", "allocates", "CRTCutscene object", "remain unproven"],
        ["OID__AllocObject", "PCRTID__CreateObject", "0xd6c", "0xd70"],
        ["animation-index", "signature-correction"],
    ),
    "0x0043f690": target(
        "CCutscene__Update",
        "void __fastcall CCutscene__Update(void * this)",
        ["Updates cutscene frame playback", "prepares animations", "MovieCamera", "sound samples", "requeues an EVENT_MANAGER tick", "remain unproven"],
        ["CCutscene__PrepareAnimations", "CMovieCamera__ctor", "CSoundManager__PlaySample", "CEventManager__AddEvent_AtTime"],
        ["playback", "signature-correction"],
    ),
    "0x0043fa70": target(
        "CCutscene__PrepareAnimations",
        "void __fastcall CCutscene__PrepareAnimations(void * this)",
        ["Prepares animation timings", "resolves animation indices", "sample durations", "total frame count", "remain unproven"],
        ["FindAnimationIndex", "CSoundManager__GetOrCreateSample", "CSoundManager__GetSampleDurationSeconds", "0x848"],
        ["animation-timing", "signature-correction"],
    ),
    "0x0043fcb0": target(
        "CCutscene__EventDispatchUpdate",
        "void __thiscall CCutscene__EventDispatchUpdate(void * this, void * eventRecord)",
        ["Recovered event callback boundary", "event code 3000", "forwarding to CCutscene__Update", "fallback CComplexThing event handler", "remain unproven"],
        ["eventRecord", "0xbb8", "CCutscene__Update", "CComplexThing__HandleEvent"],
        ["function-boundary", "event-callback"],
    ),
    "0x0043fcd0": target(
        "CCutscene__ForceEnd",
        "void __cdecl CCutscene__ForceEnd(void)",
        ["Global force-end helper", "current cutscene global", "dispatches its vtable +0x100 Stop slot", "otherwise returns", "remain unproven"],
        ["DAT_0066ea20", "0x100"],
        ["playback", "global-helper", "signature-correction"],
    ),
}

STALE_NAMES = [
    "CCutscene__scalar_deleting_dtor_0043e8e0",
    "CCutscene__VFunc_01_0043ea90",
    "CCutscene__VFunc_09_0043eab0",
    "CCutscene__DestroyRecursive",
]

EXPECTED_VTABLE_SLOTS = [
    ("0x005dad88", "0", "CCutscene__EventDispatchUpdate"),
    ("0x005dad88", "1", "CCutscene__scalar_deleting_dtor"),
    ("0x005dad88", "2", "CCutscene__ClearAnimationsAndStop"),
    ("0x005dad88", "9", "CCutscene__Init"),
    ("0x005dae00", "4", "CCutscene__InitAnimations"),
    ("0x005dae80", "2", "CCutscene__Stop"),
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact class layout proven",
    "rebuild parity proven",
]


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)", log_text)
    if not match:
        return {"targets": -1, "changed": -1, "failed": -1}
    return {"targets": int(match.group(1)), "changed": int(match.group(2)), "failed": int(match.group(3))}


def build_report(
    *,
    dry_log_path: Path = BASE / "cutscene_dry.log",
    apply_log_path: Path = BASE / "cutscene_apply.log",
    metadata_path: Path = BASE / "metadata_final.tsv",
    tags_path: Path = BASE / "tags_final.tsv",
    xrefs_path: Path = BASE / "xrefs_final.tsv",
    vtable_slots_path: Path = BASE / "vtable_slots_final.tsv",
    instructions_path: Path = BASE / "instructions_final.tsv",
    decompile_dir: Path = BASE / "decompile_final",
) -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(metadata_path)
    tags = read_tsv(tags_path)
    xrefs = read_tsv(xrefs_path)
    vtable_slots = read_tsv(vtable_slots_path)
    instructions = read_tsv(instructions_path)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))

    if dry_summary["targets"] != len(TARGETS) or dry_summary["failed"] != 0:
        failures.append(f"dry-run summary unexpected: {dry_summary}")
    if apply_summary["targets"] != len(TARGETS) or apply_summary["failed"] != 0:
        failures.append(f"apply summary unexpected: {apply_summary}")

    metadata_by_addr = {normalize_address(row.get("address", "")): row for row in metadata}
    tags_by_addr = {normalize_address(row.get("address", "")): row for row in tags}
    names = {row.get("name", "") for row in metadata}

    decompile_hits = 0
    ret_evidence_hits = 0
    comment_overclaims = 0
    for address, spec in TARGETS.items():
        row = metadata_by_addr.get(normalize_address(address))
        if not row:
            failures.append(f"missing metadata row for {address}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name {row.get('name')} != {spec['name']}")
        if not token_present(row.get("signature", ""), str(spec["signature"])):
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        if "param_" in row.get("signature", ""):
            failures.append(f"{address} generic param_ remains in signature")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(row.get("comment", ""), str(token)):
                failures.append(f"{address} comment missing token {token!r}")
        lowered_comment = row.get("comment", "").lower()
        if any(token in lowered_comment for token in OVERCLAIM_TOKENS):
            failures.append(f"{address} comment overclaim")
            comment_overclaims += 1

        tag_row = tags_by_addr.get(normalize_address(address))
        tag_text = tag_row.get("tags", "") if tag_row else ""
        for token in COMMON_TAGS + list(spec["tags"]):  # type: ignore[arg-type]
            if not token_present(tag_text, str(token)):
                failures.append(f"{address} tags missing token {token!r}")

        decompile_path = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_path) if decompile_path else ""
        if not decompile_path:
            failures.append(f"{address} missing decompile file")
        elif all(token_present(decompile_text, str(token)) for token in spec["decompileTokens"]):  # type: ignore[index]
            decompile_hits += 1
        else:
            failures.append(f"{address} decompile missing expected evidence token")

    for stale_name in STALE_NAMES:
        if stale_name in names:
            failures.append(f"stale name remains: {stale_name}")

    vtable_hits = 0
    for vtable, slot_index, expected_name in EXPECTED_VTABLE_SLOTS:
        row = next(
            (
                slot
                for slot in vtable_slots
                if normalize_address(slot.get("vtable", "")) == normalize_address(vtable)
                and slot.get("slot_index", "") == slot_index
            ),
            None,
        )
        if row and row.get("function_name") == expected_name:
            vtable_hits += 1
        else:
            failures.append(f"vtable {vtable} slot {slot_index} missing {expected_name}")

    xref_names = {row.get("target_name", "") for row in xrefs}
    for expected in ["CCutscene__Init", "CCutscene__InitAnimations", "CCutscene__Stop"]:
        if expected not in xref_names:
            failures.append(f"xref evidence missing {expected}")

    for address in ["0x0043eab0", "0x0043ed20", "0x0043fcb0"]:
        wanted = normalize_address(address)
        if any(normalize_address(row.get("target_addr", "")) == wanted and row.get("mnemonic", "").upper() == "RET" for row in instructions):
            ret_evidence_hits += 1
        else:
            failures.append(f"ret evidence missing for {address}")

    summary = {
        "targets": len(TARGETS),
        "metadataRows": len(metadata),
        "tagRows": len(tags),
        "xrefRows": len(xrefs),
        "vtableRows": len(vtable_slots),
        "instructionRows": len(instructions),
        "decompileHits": decompile_hits,
        "vtableEvidenceHits": vtable_hits,
        "retEvidenceHits": ret_evidence_hits,
        "commentOverclaims": comment_overclaims,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
    }
    return {"status": "PASS" if not failures else "FAIL", "summary": summary, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json-out", type=Path, default=BASE / "cutscene-signature-boundary-tranche.json")
    args = parser.parse_args()

    report = build_report()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
