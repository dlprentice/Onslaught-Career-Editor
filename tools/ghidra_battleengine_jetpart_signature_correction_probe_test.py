#!/usr/bin/env python3
"""Self-tests for the CBattleEngineJetPart Ghidra correction probe."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import ghidra_battleengine_jetpart_signature_correction_probe as probe


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_fixture(root: Path, *, stale_pitch: bool = False) -> dict[str, Path]:
    decomp = root / "decompile_final"
    metadata_rows = []
    index_rows = []
    xref_rows = []
    instruction_rows = []
    callsite_rows = []

    signatures = {
        address: " ".join(rule["signature"])
        for address, rule in probe.TARGETS.items()
    }
    names = {address: rule["name"] for address, rule in probe.TARGETS.items()}
    if stale_pitch:
        names["0x00410670"] = "CGeneralVolume__DrainLinkedObjectFromVelocity"
        signatures["0x00410670"] = "void __fastcall CGeneralVolume__DrainLinkedObjectFromVelocity(int param_1)"

    for address, rule in probe.TARGETS.items():
        name = names[address]
        signature = signatures[address]
        comment = " ".join(rule["comment"])
        metadata_rows.append({"address": address, "name": name, "signature": signature, "comment": comment, "status": "OK"})
        index_rows.append({"address": address, "name": name, "signature": signature, "status": "OK"})
        for from_addr in rule["from"]:
            xref_rows.append({
                "target_addr": address,
                "target_name": name,
                "from_addr": from_addr,
                "from_function_addr": "<none>",
                "from_function": "<no_function>",
                "ref_type": "UNCONDITIONAL_CALL",
            })
            callsite_rows.append({
                "target_raw": from_addr,
                "target_addr": from_addr,
                "role": "TARGET",
                "ordinal": "0",
                "instruction_addr": from_addr,
                "function_entry": "<none>",
                "function_name": "<no_function>",
                "mnemonic": "CALL",
                "operands": address,
                "bytes": "",
                "flow_type": "UNCONDITIONAL_CALL",
            })
            callsite_rows.append({
                "target_raw": from_addr,
                "target_addr": from_addr,
                "role": "BEFORE",
                "ordinal": "-1",
                "instruction_addr": "0x004d33bb",
                "function_entry": "<none>",
                "function_name": "<no_function>",
                "mnemonic": "MOV",
                "operands": "ECX, dword ptr [EAX + 0x57c]",
                "bytes": "",
                "flow_type": "FALL_THROUGH",
            })
        instruction_rows.append({
            "target_raw": address,
            "target_addr": address,
            "role": "AFTER",
            "ordinal": "1",
            "instruction_addr": address,
            "function_entry": address,
            "function_name": name,
            "mnemonic": "RET",
            "operands": rule["ret"],
            "bytes": "",
            "flow_type": "TERMINATOR",
        })
        write_text(decomp / f"{address[2:]}_{name}.c", f"{name} {' '.join(rule['decompile'])}")

    write_tsv(root / "metadata_final.tsv", metadata_rows, ["address", "name", "signature", "comment", "status"])
    write_tsv(root / "decompile_final" / "index.tsv", index_rows, ["address", "name", "signature", "status"])
    write_tsv(root / "xrefs_final.tsv", xref_rows, ["target_addr", "target_name", "from_addr", "from_function_addr", "from_function", "ref_type"])
    write_tsv(root / "instructions_final.tsv", instruction_rows, ["target_raw", "target_addr", "role", "ordinal", "instruction_addr", "function_entry", "function_name", "mnemonic", "operands", "bytes", "flow_type"])
    write_tsv(root / "callsite_instructions_final.tsv", callsite_rows, ["target_raw", "target_addr", "role", "ordinal", "instruction_addr", "function_entry", "function_name", "mnemonic", "operands", "bytes", "flow_type"])
    write_text(root / "signature_dry.log", f"--- SUMMARY ---\nupdated=0 skipped={len(probe.TARGETS)} missing=0 bad=0\n")
    write_text(root / "signature_apply.log", f"--- SUMMARY ---\nupdated={len(probe.TARGETS)} skipped=0 missing=0 bad=0\n")
    return {
        "dry_log_path": root / "signature_dry.log",
        "apply_log_path": root / "signature_apply.log",
        "metadata_path": root / "metadata_final.tsv",
        "decompile_index_path": root / "decompile_final" / "index.tsv",
        "decompile_dir": decomp,
        "xrefs_path": root / "xrefs_final.tsv",
        "instructions_path": root / "instructions_final.tsv",
        "callsites_path": root / "callsite_instructions_final.tsv",
    }


def test_pass_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report = probe.build_report(**make_fixture(Path(tmp)))
        assert report["status"] == "PASS", report["failures"]
        assert report["summary"]["targets"] == len(probe.TARGETS)
        assert report["summary"]["staleSignatureHits"] == 0


def test_stale_pitch_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report = probe.build_report(**make_fixture(Path(tmp), stale_pitch=True))
        assert report["status"] == "FAIL"
        assert any("0x00410670" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_pass_fixture()
    test_stale_pitch_fails()
    print("PASS: ghidra_battleengine_jetpart_signature_correction_probe_test (2/2)")
