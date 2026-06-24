#!/usr/bin/env python3
"""Self-tests for the BattleEngineData/config signature tranche probe."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import ghidra_battleengine_data_config_signature_tranche_probe as probe


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_tsv(path: Path, rows: list[dict[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return path


def metadata_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for address, expected in probe.TARGETS.items():
        signature = " ".join(expected["signatureTokens"])
        comment = " ".join(expected["commentTokens"]) + " remain unproven"
        rows.append({
            "address": address,
            "name": expected["name"],
            "signature": signature,
            "comment": comment,
            "status": "OK",
        })
    return rows


def build_fixture(root: Path, *, bad_signature: bool = False) -> dict[str, Path]:
    dry = write(root / "signature_dry.log", "--- SUMMARY ---\nupdated=0 skipped=7 missing=0 bad=0\n")
    apply = write(root / "signature_apply.log", "--- SUMMARY ---\nupdated=7 skipped=0 missing=0 bad=0\n")

    rows = metadata_rows()
    if bad_signature:
        rows[1]["signature"] = "undefined BattleEngineConfigurations__Load(void)"
    metadata = write_tsv(root / "metadata_final.tsv", rows)

    index_rows = [
        {"address": address, "name": expected["name"], "signature": "ok", "status": "OK"}
        for address, expected in probe.TARGETS.items()
    ]
    index = write_tsv(root / "decompile_final" / "index.tsv", index_rows)
    decompile_dir = root / "decompile_final"
    for address, expected in probe.TARGETS.items():
        write(
            decompile_dir / f"{probe.normalize_address(address)[2:]}_{expected['name']}.c",
            " ".join(expected["decompileTokens"]),
        )

    xrefs = write_tsv(root / "xrefs_final.tsv", [
        {"target_addr": address, "target_name": expected["name"], "from_addr": "00400000", "from_function_addr": "00400000", "from_function": "Caller", "ref_type": "UNCONDITIONAL_CALL"}
        for address, expected in probe.TARGETS.items()
    ])
    instructions = write_tsv(root / "instructions_final.tsv", [
        {"target_raw": address, "target_addr": address, "role": "TARGET", "ordinal": "0", "instruction_addr": address, "function_entry": address, "function_name": expected["name"], "mnemonic": "PUSH", "operands": "EBX", "bytes": "53", "flow_type": ""}
        for address, expected in probe.TARGETS.items()
    ])
    callsites = write_tsv(root / "callsite_instructions.tsv", [
        {"target_raw": "0x0050d506", "target_addr": "0x0050d506", "role": "TARGET", "ordinal": "0", "instruction_addr": "0x0050d506", "function_entry": "0x0050d4c0", "function_name": "CWorld__LoadWorldHeader", "mnemonic": "CALL", "operands": "0x0040f180", "bytes": "", "flow_type": ""},
        {"target_raw": "0x0050d506", "target_addr": "0x0050d506", "role": "AFTER", "ordinal": "2", "instruction_addr": "0x0050d50f", "function_entry": "0x0050d4c0", "function_name": "CWorld__LoadWorldHeader", "mnemonic": "ADD", "operands": "ESP, 0x4", "bytes": "", "flow_type": ""},
        {"target_raw": "0x0050d4ff", "target_addr": "0x0050d4ff", "role": "TARGET", "ordinal": "0", "instruction_addr": "0x0050d4ff", "function_entry": "0x0050d4c0", "function_name": "CWorld__LoadWorldHeader", "mnemonic": "CALL", "operands": "0x0040f260", "bytes": "", "flow_type": ""},
        {"target_raw": "0x0050d4ff", "target_addr": "0x0050d4ff", "role": "AFTER", "ordinal": "4", "instruction_addr": "0x0050d50f", "function_entry": "0x0050d4c0", "function_name": "CWorld__LoadWorldHeader", "mnemonic": "ADD", "operands": "ESP, 0x4", "bytes": "", "flow_type": ""},
    ])
    load_full = write_tsv(root / "instructions_load_full.tsv", [
        {"target_raw": "0x0040f980", "target_addr": "0x0040f980", "role": "AFTER", "ordinal": "671", "instruction_addr": "0x004100fb", "function_entry": "0x0040f980", "function_name": "CBattleEngineData__LoadFromMemBuffer", "mnemonic": "RET", "operands": "0x4", "bytes": "", "flow_type": ""},
        {"target_raw": "0x0040f980", "target_addr": "0x0040f980", "role": "AFTER", "ordinal": "676", "instruction_addr": "0x00410110", "function_entry": "0x0040f980", "function_name": "CBattleEngineData__LoadFromMemBuffer", "mnemonic": "RET", "operands": "0x4", "bytes": "", "flow_type": ""},
    ])
    return {
        "dry_log_path": dry,
        "apply_log_path": apply,
        "metadata_path": metadata,
        "decompile_index_path": index,
        "decompile_dir": decompile_dir,
        "xrefs_path": xrefs,
        "instructions_path": instructions,
        "callsites_path": callsites,
        "load_full_path": load_full,
    }


def test_valid_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report = probe.build_report(**build_fixture(Path(tmp)))
    assert report["status"] == "PASS", report["failures"]
    assert report["target_count"] == 7
    assert report["param_signature_hits"] == 0
    assert report["undefined_signature_hits"] == 0
    assert report["load_ret_0x4_hits"] == 2


def test_undefined_signature_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report = probe.build_report(**build_fixture(Path(tmp), bad_signature=True))
    assert report["status"] == "FAIL"
    assert report["undefined_signature_hits"] == 1
    assert any("undefined signature remains" in failure for failure in report["failures"])


def main() -> int:
    tests = [test_valid_fixture_passes, test_undefined_signature_fails]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:  # pragma: no cover - script-style self-test output
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"Result: {len(tests) - failed}/{len(tests)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
