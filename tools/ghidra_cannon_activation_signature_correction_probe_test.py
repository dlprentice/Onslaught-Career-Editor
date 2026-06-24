#!/usr/bin/env python3
"""Self-tests for the Cannon activation Ghidra correction probe."""

from __future__ import annotations

import csv
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_cannon_activation_signature_correction_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_fixture(base: Path, probe) -> dict[str, Path]:
    dry = base / "dry.log"
    apply = base / "apply.log"
    dry.write_text("updated=0 skipped=9 renamed=0 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("updated=9 skipped=0 renamed=3 missing=0 bad=0\n", encoding="utf-8")

    metadata_rows = []
    index_rows = []
    xref_rows = []
    instruction_rows = []
    decompile_dir = base / "decompile"
    decompile_dir.mkdir()

    for index, (address, expected) in enumerate(probe.TARGETS.items()):
        signature = " ".join(expected["signature"])
        comment = " ".join(expected["comment"])
        decompile = " ".join(expected["decompile"]) + f" {expected['name']}"
        metadata_rows.append({"address": address, "name": expected["name"], "signature": signature, "comment": comment, "status": "OK"})
        index_rows.append({"address": address, "name": expected["name"], "signature": signature, "status": "OK"})
        (decompile_dir / f"{address[2:]}_{expected['name']}.c").write_text(decompile, encoding="utf-8")
        xref_rows.append(
            {
                "target_addr": address,
                "target_name": expected["name"],
                "from_addr": f"0x{0x005e0000 + index * 4:08x}",
                "from_function_addr": "<none>",
                "from_function": "<no_function>",
                "ref_type": "DATA",
            }
        )
        instruction_rows.append(
            {
                "target_raw": address,
                "target_addr": address,
                "role": "TARGET",
                "ordinal": "0",
                "instruction_addr": address,
                "function_entry": address,
                "function_name": expected["name"],
                "mnemonic": "PUSH",
                "operands": "ESI",
                "bytes": "56",
                "flow_type": "FALL_THROUGH",
            }
        )

    write_tsv(base / "metadata.tsv", ["address", "name", "signature", "comment", "status"], metadata_rows)
    write_tsv(base / "index.tsv", ["address", "name", "signature", "status"], index_rows)
    write_tsv(
        base / "xrefs.tsv",
        ["target_addr", "target_name", "from_addr", "from_function_addr", "from_function", "ref_type"],
        xref_rows,
    )
    write_tsv(
        base / "instructions.tsv",
        ["target_raw", "target_addr", "role", "ordinal", "instruction_addr", "function_entry", "function_name", "mnemonic", "operands", "bytes", "flow_type"],
        instruction_rows,
    )
    write_tsv(
        base / "vtables.tsv",
        ["vtable", "demangled_type_name"],
        [
            {"vtable": "005e24dc", "demangled_type_name": "CCannon"},
            {"vtable": "005e08e0", "demangled_type_name": "CSentinel"},
            {"vtable": "005e01dc", "demangled_type_name": "CWarspiteDome"},
            {"vtable": "005e297c", "demangled_type_name": "CGroundVehicle"},
        ],
    )

    return {
        "dry_log_path": dry,
        "apply_log_path": apply,
        "metadata_path": base / "metadata.tsv",
        "decompile_index_path": base / "index.tsv",
        "decompile_dir": decompile_dir,
        "xrefs_path": base / "xrefs.tsv",
        "instructions_path": base / "instructions.tsv",
        "vtable_path": base / "vtables.tsv",
    }


def test_accepts_expected_fixture() -> None:
    probe = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        paths = make_fixture(Path(tmp), probe)
        report = probe.build_report(**paths)
        assert report["status"] == "PASS", report["failures"]


def test_rejects_stale_destructor_name() -> None:
    probe = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        paths = make_fixture(base, probe)
        rows = list(csv.DictReader((base / "metadata.tsv").open("r", encoding="utf-8"), delimiter="\t"))
        rows[2]["name"] = "CCannon__Destructor"
        write_tsv(base / "metadata.tsv", ["address", "name", "signature", "comment", "status"], rows)
        report = probe.build_report(**paths)
        assert report["status"] == "FAIL"
        assert any("stale" in failure or "name mismatch" in failure for failure in report["failures"])


def test_rejects_missing_vtable_type() -> None:
    probe = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        paths = make_fixture(base, probe)
        write_tsv(base / "vtables.tsv", ["vtable", "demangled_type_name"], [{"vtable": "005e24dc", "demangled_type_name": "CCannon"}])
        report = probe.build_report(**paths)
        assert report["status"] == "FAIL"
        assert any("missing vtable type" in failure for failure in report["failures"])


def main() -> int:
    test_accepts_expected_fixture()
    test_rejects_stale_destructor_name()
    test_rejects_missing_vtable_type()
    print("ghidra_cannon_activation_signature_correction_probe_test: PASS (3/3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
