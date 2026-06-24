#!/usr/bin/env python3
"""Self-tests for the BattleEngine reset-configuration signature tranche probe."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import ghidra_battleengine_resetconfiguration_signature_tranche_probe as probe


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_fixture(root: Path, *, stale_param: bool = False) -> dict[str, Path]:
    decomp = root / "decompile_final"
    metadata_rows = []
    index_rows = []
    xref_rows = []
    instruction_rows = []

    for address, rule in probe.TARGETS.items():
        name = rule["name"]
        signature = " ".join(rule["signature"])
        if stale_param and address == "0x00412650":
            signature = f"void __fastcall {name}(void * param_1)"
        comment = " ".join(rule["comment"])
        metadata_rows.append({"address": address, "name": name, "signature": signature, "comment": comment, "status": "OK"})
        index_rows.append({"address": address, "name": name, "signature": signature, "status": "OK"})
        for from_addr, from_function in zip(rule["from"], rule["from_functions"]):
            xref_rows.append({
                "target_addr": address,
                "target_name": name,
                "from_addr": from_addr,
                "from_function_addr": "<none>",
                "from_function": from_function,
                "ref_type": "UNCONDITIONAL_CALL",
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
    }


def test_pass_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report = probe.build_report(**make_fixture(Path(tmp)))
        assert report["status"] == "PASS", report["failures"]
        assert report["summary"]["targets"] == len(probe.TARGETS)
        assert report["summary"]["staleSignatureHits"] == 0


def test_stale_param_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report = probe.build_report(**make_fixture(Path(tmp), stale_param=True))
        assert report["status"] == "FAIL"
        assert any("0x00412650" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_pass_fixture()
    test_stale_param_fails()
    print("PASS: ghidra_battleengine_resetconfiguration_signature_tranche_probe_test (2/2)")
