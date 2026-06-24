#!/usr/bin/env python3
"""Validate Wave503 audio-tail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave503-audio-tail-004e1200"
)

COMMON_TAGS = {
    "audio",
    "audio-tail-wave503",
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "sound-manager",
    "static-reaudit",
}


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
    instruction_tokens: tuple[tuple[str, str, str], ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
        "instruction_tokens": instruction_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004e1200": target(
        "CSoundManager__KillAllInstancesOfSample",
        "void __thiscall CSoundManager__KillAllInstancesOfSample(void * this, void * sample)",
        (
            "CSoundManager::KillAllInstancesOfSample",
            "not a CMessageBox channel helper",
            "matches event+0x0c",
            "blocking stop",
            "runtime sample shutdown behavior",
            "rebuild parity remain unproven",
        ),
        {"event-stop", "name-corrected", "sample-lifecycle", "source-parity"},
        (
            "void __thiscall CSoundManager__KillAllInstancesOfSample",
            "CSoundManager__StopAndReleaseChannel",
            "CGenericActiveReader__SetReader",
            "sound_event[0x1d]",
        ),
        (
            ("0x004e1201", "MOV", "ESI, dword ptr [ECX + 0xc]"),
            ("0x004e120d", "CMP", "dword ptr [ESI + 0xc], EBP"),
            ("0x004e1233", "CALL", "0x005179b0"),
        ),
    ),
    "0x004e2bb0": target(
        "CSoundManager__BuildLanguageSampleBankPathIfChanged",
        "bool __thiscall CSoundManager__BuildLanguageSampleBankPathIfChanged(void * this, char * out_path)",
        (
            "retail PC language sample-bank path helper",
            "not a CUnit voice helper",
            "<root>/data/sounds/sounds_<language>_pc.xap",
            "this+0x88",
            "returns true only when the path changed",
            "runtime language switching behavior",
        ),
        {"language-audio", "name-corrected", "pc-sound", "sample-bank"},
        (
            "bool __thiscall CSoundManager__BuildLanguageSampleBankPathIfChanged",
            "CText__GetLanguageName",
            "PTR_s__s_data_sounds_sounds__s_pc_xap_0063e2a8",
            "stricmp",
        ),
        (
            ("0x004e2bb0", "SUB", "ESP, 0xc8"),
            ("0x004e2bb9", "MOV", "AL, byte ptr [ESI + 0x4]"),
            ("0x004e2bc9", "RET", "0x4"),
        ),
    ),
    "0x004e2e60": target(
        "CUnit__PlayImpactSoundForMaterials",
        "void __cdecl CUnit__PlayImpactSoundForMaterials(void * primary_unit, void * secondary_unit)",
        (
            "impact-material sound-effect dispatcher",
            "vtable slot +0xac",
            "impact_Wood",
            "hit_%d",
            "CSoundManager__PlayEffect",
            "runtime collision/impact sound behavior",
        ),
        {"effect-playback", "impact-sound", "material-sound"},
        (
            "void __cdecl CUnit__PlayImpactSoundForMaterials",
            "s_impact_Wood_00632640",
            "s_hit__d_00632638",
            "CSoundManager__GetEffectByName",
            "CSoundManager__PlayEffect",
        ),
        (
            ("0x004e2e60", "SUB", "ESP, 0xc"),
            ("0x004e2e82", "CALL", "dword ptr [EAX + 0xac]"),
            ("0x004e2e8e", "CALL", "dword ptr [EDX + 0xac]"),
        ),
    ),
}

EXPECTED_XREFS = {
    ("004e1200", "004b8829", "CMessageBox__StopVoicePlaybackIfNotInCutscene"),
    ("004e1200", "004b79d3", "CMessageBox__dtor_base"),
    ("004e1200", "004b7a58", "CMessageBox__dtor_base"),
    ("004e1200", "00516901", "CPCSoundManager__dtor"),
    ("004e2bb0", "00462ad5", "<no_function>"),
    ("004e2e60", "004d8d37", "<no_function>"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def norm_addr(value: str) -> str:
    text = value.lower()
    if text.startswith("0x"):
        text = text[2:]
    return f"0x{int(text, 16):08x}"


def file_for_decomp(base: Path, addr: str, name: str) -> Path:
    short = addr[2:]
    return base / "post-decomp" / f"{short}_{name}.c"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_log(path: Path, expected: str, errors: list[str]) -> None:
    text = read_text(path)
    require(expected in text, f"{path.name}: missing summary {expected!r}", errors)
    require("REPORT: Save succeeded" in text, f"{path.name}: missing save success", errors)
    for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}", errors)


def check_metadata(base: Path, errors: list[str]) -> None:
    rows = {norm_addr(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    require(set(rows) == set(TARGETS), f"metadata addresses mismatch: {sorted(rows)}", errors)
    for addr, spec in TARGETS.items():
        row = rows.get(addr, {})
        require(row.get("status") == "OK", f"{addr}: metadata status not OK", errors)
        require(row.get("name") == spec["name"], f"{addr}: name mismatch", errors)
        require(row.get("signature") == spec["signature"], f"{addr}: signature mismatch", errors)
        comment = row.get("comment", "")
        for token in spec["comment_tokens"]:
            require(str(token) in comment, f"{addr}: missing comment token {token!r}", errors)


def check_tags(base: Path, errors: list[str]) -> None:
    rows = {norm_addr(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    require(set(rows) == set(TARGETS), f"tag addresses mismatch: {sorted(rows)}", errors)
    for addr, spec in TARGETS.items():
        row = rows.get(addr, {})
        require(row.get("status") == "OK", f"{addr}: tag status not OK", errors)
        actual = set(filter(None, row.get("tags", "").split(";")))
        missing = set(spec["tags"]) - actual
        require(not missing, f"{addr}: missing tags {sorted(missing)}", errors)


def check_xrefs(base: Path, errors: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {
        (row["target_addr"].lower(), row["from_addr"].lower(), row["from_function"])
        for row in rows
    }
    require(
        actual == EXPECTED_XREFS,
        f"xrefs mismatch: expected {sorted(EXPECTED_XREFS)}, got {sorted(actual)}",
        errors,
    )


def check_decompile(base: Path, errors: list[str]) -> None:
    for addr, spec in TARGETS.items():
        path = file_for_decomp(base, addr, str(spec["name"]))
        require(path.exists(), f"{addr}: missing decompile {path}", errors)
        if not path.exists():
            continue
        text = read_text(path)
        for token in spec["decompile_tokens"]:
            require(str(token) in text, f"{addr}: missing decompile token {token!r}", errors)


def check_instructions(base: Path, errors: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {norm_addr(row["instruction_addr"]): row for row in rows}
    for addr, spec in TARGETS.items():
        for ins_addr, mnemonic, operands in spec["instruction_tokens"]:
            row = by_addr.get(norm_addr(ins_addr), {})
            require(row.get("function_name") == spec["name"], f"{addr}: wrong function at {ins_addr}", errors)
            require(row.get("mnemonic") == mnemonic, f"{addr}: wrong mnemonic at {ins_addr}", errors)
            require(row.get("operands") == operands, f"{addr}: wrong operands at {ins_addr}", errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base.resolve()
    errors: list[str] = []

    require(base.exists(), f"missing base directory: {base}", errors)
    if base.exists():
        check_log(
            base / "apply_audio_tail_wave503_dry.log",
            "SUMMARY: updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0",
            errors,
        )
        check_log(
            base / "apply_audio_tail_wave503_apply.log",
            "SUMMARY: updated=3 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0",
            errors,
        )
        check_log(
            base / "apply_audio_tail_wave503_final_verify_dry.log",
            "SUMMARY: updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0",
            errors,
        )
        check_metadata(base, errors)
        check_tags(base, errors)
        check_xrefs(base, errors)
        check_decompile(base, errors)
        check_instructions(base, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Wave503 audio-tail probe OK: 3 functions validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
