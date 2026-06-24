#!/usr/bin/env python3
"""Self-tests for ghidra_mapwho_line_wave429_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_mapwho_line_wave429_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(base / "apply_dry.log", "SUMMARY updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0\n")
    write(base / "apply_apply.log", "SUMMARY updated=13 skipped=0 renamed=0 would_rename=0 missing=0 bad=0\n")

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    xref_lines = ["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"]
    instruction_lines = [
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type"
    ]

    for address, expected in probe.TARGETS.items():
        metadata_lines.append(
            "\t".join(
                [
                    address,
                    str(expected["name"]),
                    str(expected["signature"]),
                    " ".join(str(token) for token in expected["commentTokens"]),
                    "OK",
                ]
            )
        )
        tags = sorted(probe.COMMON_TAGS | set(expected["tags"]))  # type: ignore[arg-type]
        tags_lines.append("\t".join([address, str(expected["name"]), ";".join(tags), "OK"]))
        for from_function in expected["xrefTokens"]:  # type: ignore[assignment]
            xref_lines.append(
                "\t".join(
                    [address, str(expected["name"]), "0x00000000", "0x00000000", str(from_function), "UNCONDITIONAL_CALL"]
                )
            )
        mnemonic, operand = probe.INSTRUCTION_RETURNS[address]
        instruction_lines.append(
            "\t".join([address, address, "AFTER", "1", address, address, str(expected["name"]), mnemonic, operand, "", "TERMINATOR"])
        )
        clean = probe.normalize_address(address)[2:]
        write(
            base / "decompile_after" / f"{clean}_{expected['name']}.c",
            " ".join(str(token) for token in expected["decompileTokens"]),
        )

    write(base / "metadata_after.tsv", "\n".join(metadata_lines) + "\n")
    write(base / "tags_after.tsv", "\n".join(tags_lines) + "\n")
    write(base / "xrefs_after.tsv", "\n".join(xref_lines) + "\n")
    write(base / "instructions_after.tsv", "\n".join(instruction_lines) + "\n")


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_undefined_signature_regression_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("void * __thiscall CMapWho__GetFirstEntryWithinLine", "undefined CMapWho__GetFirstEntryWithinLine")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("signature mismatch" in failure for failure in failures)


def test_missing_line_iterator_tag_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "tags_after.tsv").read_text(encoding="utf-8")
        text = text.replace("line-iterator;", "")
        (base / "tags_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("missing tags" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("runtime line-query behavior", "runtime line-query behavior proven")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [
        test_good_fixture_passes,
        test_undefined_signature_regression_fails,
        test_missing_line_iterator_tag_fails,
        test_runtime_overclaim_fails,
    ]
    for test in tests:
        test()
    print(f"PASS ghidra_mapwho_line_wave429_probe_test: {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
