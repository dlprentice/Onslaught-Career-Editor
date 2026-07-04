#!/usr/bin/env python3
"""Validate Wave953 CFEPMain menu read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave953-cfepmain-menu-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfepmain_menu_review_wave953_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FEPMAIN_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMain.cpp.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-093826_post_wave953_cfepmain_menu_review_verified"

PRIMARY_TARGETS = {
    "0x004621b0": ("CFEPMain__Init", "int __fastcall CFEPMain__Init(void * this)"),
    "0x004621d0": ("CFEPMain__GetMenuType", "int __cdecl CFEPMain__GetMenuType(void)"),
    "0x004621e0": ("CFEPMain__GetActionCount", "int __stdcall CFEPMain__GetActionCount(int menu_state)"),
    "0x00462250": ("CFEPMain__ButtonPressed", "void __thiscall CFEPMain__ButtonPressed(void * this, int button, float val)"),
    "0x004623e0": ("CFEPMain__DoAction", "void __fastcall CFEPMain__DoAction(void * this)"),
    "0x00462640": ("CFEPMain__Process", "void __thiscall CFEPMain__Process(void * this, int state)"),
    "0x00462b70": ("CFEPMain__RenderPreCommon", "void __stdcall CFEPMain__RenderPreCommon(float transition, int dest)"),
    "0x00462c90": ("CFEPMain__Update", "void __stdcall CFEPMain__Update(int menu_state)"),
    "0x00462d40": ("CFEPMain__Render", "void __thiscall CFEPMain__Render(void * this, float transition, int dest)"),
    "0x004644d0": ("CFEPMain__TransitionNotification", "void __fastcall CFEPMain__TransitionNotification(void * this, int from)"),
    "0x00464520": ("CFEPMain__ActiveNotification", "void __fastcall CFEPMain__ActiveNotification(void * this, int from_page)"),
}

CONTEXT_TARGETS = {
    "0x004662a0": "CFrontEnd__Init",
    "0x00466ae0": "CFrontEnd__SetPage",
    "0x004679e0": "CFrontEnd__RenderPreCommonFade",
    "0x00468770": "CFrontEnd__PlaySound",
    "0x0044d390": "FEMessBox__Create",
    "0x00457ee0": "CFEPDemoMain__DoAction",
}

COMMENT_TOKENS = {
    "0x004621b0": ("selection/timer", "+0x14", "+0x20"),
    "0x004621d0": ("no-argument", "constant 7"),
    "0x004621e0": ("stack-only menu_state", "career-in-progress", "controller-count"),
    "0x00462250": ("0x2a/0x2b/0x2c/0x36/0x37", "frontend sounds"),
    "0x004623e0": ("New Game/Continue/Load/Options/Multiplayer/Goodies/Credits/Return", "FrontEnd pages"),
    "0x00462640": ("FEPMain.cpp", "CCareer__Save", "CFEPOptions__WriteDefaultOptionsFile"),
    "0x00462b70": ("stack-only transition/dest", "dest 0x0c"),
    "0x00462c90": ("FrontEndText token", "fallback 8"),
    "0x00462d40": ("selection state", "language arrows"),
    "0x004644d0": ("+0x14", "CAREER_mCareerInProgress"),
    "0x00464520": ("clears +0x14", "ignored page argument"),
}

COMMON_TAGS = {"static-reaudit", "fepmain-wave401", "fepmain", "frontend", "retail-binary-evidence", "comment-hardened"}

DECOMPILE_TOKENS = {
    "0x004621d0": ("return 7;",),
    "0x004621e0": ("case 8:", "return CAREER_mCareerInProgress;", "CFrontEnd__NumControllersPresent"),
    "0x00462250": ("case 0x2a:", "case 0x36:", "case 0x37:", "CFrontEnd__PlaySound(0)"),
    "0x004623e0": ("CFrontEnd__SetPage(&DAT_0089d758,7,0x46)", "CFrontEnd__SetPage(&DAT_0089d758,0xb,0)", "FrontEndText__GetLocalizedOrFallbackTextByToken(0x18)"),
    "0x00462640": ("CCareer__Save(&CAREER", "CFEPOptions__WriteDefaultOptionsFile", "CFrontEnd__SetPage(&DAT_0089d758,0xc,0)"),
    "0x00462b70": ("CFrontEnd__RenderVideoQuadScaledToWindow",),
    "0x00462c90": ("FrontEndText__GetLocalizedOrFallbackTextByToken(0)", "FrontEndText__GetLocalizedOrFallbackTextByToken(8)"),
    "0x00462d40": ("(**(code **)(*(int *)this + 0xc))(0x36,0x3f800000)", "(**(code **)(*(int *)this + 0xc))(0x37,0x3f800000)"),
    "0x004644d0": ("CAREER_mCareerInProgress",),
    "0x00464520": ("*(undefined4 *)((int)this + 0x14) = 0",),
}

VTABLE_TOKENS = {
    ("005dbae4", "0", "CFEPMain__Init"),
    ("005dbae4", "3", "CFEPMain__ButtonPressed"),
    ("005dbae4", "4", "CFEPMain__RenderPreCommon"),
    ("005dbae4", "5", "CFEPMain__Render"),
    ("005dbae4", "7", "CFEPMain__ActiveNotification"),
    ("005dbae4", "9", "CFEPMain__GetActionCount"),
    ("005dbae4", "10", "CFEPMain__GetMenuType"),
    ("005dbae4", "11", "CFEPMain__DoAction"),
    ("005dbae4", "12", "CFEPMain__Update"),
    ("005dbaf0", "0", "CFEPMain__ButtonPressed"),
    ("005dbb00", "0", "CFEPMain__ActiveNotification"),
    ("005dbb1c", "0", "CGenericCamera__GetPos"),
}

CORE_TOKENS = (
    "Wave953",
    "cfepmain-menu-review-wave953",
    "0x004621d0 CFEPMain__GetMenuType",
    "0x004621e0 CFEPMain__GetActionCount",
    "0x00462b70 CFEPMain__RenderPreCommon",
    "0x00462c90 CFEPMain__Update",
    "0x005dbae4",
    "0x005dbaf0",
    "0x005dbb00",
    "[maintainer-local-source-export-root]\\FEPMain.cpp",
    "280/1408 = 19.89%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime main-menu behavior proven",
    "runtime frontend behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return (
        token in text
        or token in stripped
        or token.replace("\\", "\\\\") in text
        or token.replace("\\", "\\\\") in stripped
    )


def decompile_path(address: str, name: str) -> Path:
    return BASE / "pre-decompile" / f"{address[2:]}_{name}.c"


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 17,
        "pre-tags.tsv": 17,
        "pre-xrefs.tsv": 257,
        "pre-instructions.tsv": 2935,
        "pre-decompile/index.tsv": 17,
        "pre-vtables.tsv": 56,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    string_rows = read_tsv(BASE / "string-00629414.tsv")
    require(string_rows and string_rows[0].get("cstring") == r"[maintainer-local-source-export-root]\FEPMain.cpp", "FEPMain debug string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    for address, (name, signature) in PRIMARY_TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile_index.get(address)
        require(dec is not None and dec.get("status") == "OK", f"decompile index missing/failed at {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        for token in DECOMPILE_TOKENS.get(address, ()):
            require(token in read_text(decompile_path(address, name)), f"missing decompile token in {name}: {token}", failures)

    for address, expected_name in CONTEXT_TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row:
            require(row.get("name") == expected_name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)

    vtable_hits = {
        (row["vtable"].lower(), row["slot_index"], row["function_name"])
        for row in read_tsv(BASE / "pre-vtables.tsv")
        if row.get("status") == "OK"
    }
    for token in VTABLE_TOKENS:
        require(token in vtable_hits, f"missing vtable token {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=17 found=17 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "pre-xrefs.log": "Wrote 257 rows",
        "pre-instructions.log": "Wrote 2935 function-body instruction rows",
        "pre-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
        "pre-vtables.log": "ExportVtableSlots complete: targets=4 rows=56",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Input file not found", "BADADDR", "MISSING", "FAIL:", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_backup_and_wave401(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6151, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    result = subprocess.run(
        ["py", "-3", str(ROOT / "tools" / "ghidra_fepmain_wave401_probe.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(result.returncode == 0, f"Wave401 probe failed: {result.stdout} {result.stderr}", failures)
    require("status=PASS targets=11 failures=0" in result.stdout, "Wave401 probe PASS token missing", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-cfepmain-menu-review-wave953")
        == r"py -3 tools\ghidra_cfepmain_menu_review_wave953_probe.py --check",
        "missing package script",
        failures,
    )

    docs = [NOTE, CAMPAIGN, FEPMAIN_DOC, FRONTEND_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_and_wave401(failures)
    check_docs(failures)

    if failures:
        print("Wave953 CFEPMain menu review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave953 CFEPMain menu review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
