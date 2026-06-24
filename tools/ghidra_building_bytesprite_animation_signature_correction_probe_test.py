#!/usr/bin/env python3
"""Self-tests for the Wave 314 Building / ByteSprite probe."""

from __future__ import annotations

import csv
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_building_bytesprite_animation_signature_correction_probe.py"


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
    dry.write_text("updated=0 skipped=14 renamed=0 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("updated=14 skipped=0 renamed=6 missing=0 bad=0\n", encoding="utf-8")

    metadata_rows = []
    index_rows = []
    instruction_rows = []
    xref_rows = []
    decompile_dir = base / "decompile"
    decompile_dir.mkdir()
    for index, (address, expected) in enumerate(probe.TARGETS.items()):
        signature = " ".join(expected["signature"])
        comment = " ".join(expected["comment"])
        metadata_rows.append({"address": address, "name": expected["name"], "signature": signature, "comment": comment, "status": "OK"})
        index_rows.append({"address": address, "name": expected["name"], "signature": signature, "status": "OK"})
        (decompile_dir / f"{address[2:]}_{expected['name']}.c").write_text(f"{expected['name']}\n", encoding="utf-8")
        for i in range(100):
            instruction_rows.append({"target_addr": address, "instruction_addr": f"0x{0x401000 + index * 0x100 + i:08x}"})
        xref_rows.append({"target_addr": address, "from_addr": f"0x{0x500000 + index:08x}"})
    for i in range(6):
        xref_rows.append({"target_addr": "0x00418920", "from_addr": f"0x0060{i:04x}"})

    write_tsv(base / "metadata.tsv", ["address", "name", "signature", "comment", "status"], metadata_rows)
    write_tsv(base / "index.tsv", ["address", "name", "signature", "status"], index_rows)
    write_tsv(base / "instructions.tsv", ["target_addr", "instruction_addr"], instruction_rows)
    write_tsv(base / "xrefs.tsv", ["target_addr", "from_addr"], xref_rows)
    write_tsv(base / "vtables.tsv", ["vtable", "demangled_type_name"], [
        {"vtable": "005d8eb4", "demangled_type_name": "CBuilding"},
        {"vtable": "005dfd3c", "demangled_type_name": "CSimpleBuilding"},
        {"vtable": "005d910c", "demangled_type_name": "CBuildingNamedMesh"},
    ])
    caller_dir = base / "caller"
    caller_dir.mkdir()
    write_tsv(base / "caller_index.tsv", ["address", "name", "signature", "status"], [
        {"address": "0x0053be40", "name": "CDXCompass__Init", "signature": "void CDXCompass__Init(void)", "status": "OK"}
    ])
    (caller_dir / "0053be40_CDXCompass__Init.c").write_text(
        "CByteSprite__Init CByteSprite__Load CByteSprite__SetTarget compass 0x10 0x14 0x200",
        encoding="utf-8",
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
        "caller_index_path": base / "caller_index.tsv",
        "caller_dir": caller_dir,
    }


def test_accepts_expected_fixture() -> None:
    probe = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        paths = make_fixture(Path(tmp), probe)
        report = probe.build_report(**paths)
        assert report["status"] == "PASS", report["failures"]


def test_rejects_stale_owner_name() -> None:
    probe = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        paths = make_fixture(base, probe)
        rows = list(csv.DictReader((base / "metadata.tsv").open("r", encoding="utf-8"), delimiter="\t"))
        rows[0]["name"] = "VFuncSlot_02_00417870"
        write_tsv(base / "metadata.tsv", ["address", "name", "signature", "comment", "status"], rows)
        report = probe.build_report(**paths)
        assert report["status"] == "FAIL"
        assert any("name mismatch" in failure or "stale names" in failure for failure in report["failures"])


def main() -> int:
    test_accepts_expected_fixture()
    test_rejects_stale_owner_name()
    print("ghidra_building_bytesprite_animation_signature_correction_probe_test: PASS (2/2)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
