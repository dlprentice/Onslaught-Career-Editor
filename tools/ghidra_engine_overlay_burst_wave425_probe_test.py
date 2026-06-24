#!/usr/bin/env python3
"""Self-tests for ghidra_engine_overlay_burst_wave425_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_engine_overlay_burst_wave425_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=6 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0\n",
    )

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    xref_lines = ["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"]
    instruction_lines = [
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type"
    ]
    caller_texts: dict[str, str] = {}

    for address, expected in probe.TARGETS.items():
        comment = " ".join(str(token) for token in expected["commentTokens"])
        metadata_lines.append(
            "\t".join([address, str(expected["name"]), str(expected["signature"]), comment, "OK"])
        )
        tags = sorted(probe.COMMON_TAGS | set(expected["tags"]))  # type: ignore[arg-type]
        tags_lines.append("\t".join([address, str(expected["name"]), ";".join(tags), "OK"]))
        from_addr, from_function = expected["xref"]  # type: ignore[misc]
        xref_lines.append(
            "\t".join([address, str(expected["name"]), "0x00000000", str(from_addr), str(from_function), "UNCONDITIONAL_CALL"])
        )
        mnemonic, operand = probe.INSTRUCTION_RETURNS[address]
        instruction_lines.append(
            "\t".join([address, address, "AFTER", "1", address, address, str(expected["name"]), mnemonic, operand, "", "TERMINATOR"])
        )
        clean = probe.normalize_address(address)[2:]
        decompile = " ".join(str(token) for token in expected["decompileTokens"])
        write(base / "decompile_after" / f"{clean}_{expected['name']}.c", decompile)

    for filename, expectation in probe.CALLER_EXPECTATIONS.items():
        caller_texts[filename] = " ".join(expectation["required"])

    write(base / "metadata_after.tsv", "\n".join(metadata_lines) + "\n")
    write(base / "tags_after.tsv", "\n".join(tags_lines) + "\n")
    write(base / "xrefs_after.tsv", "\n".join(xref_lines) + "\n")
    write(base / "instructions_after.tsv", "\n".join(instruction_lines) + "\n")
    for filename, text in caller_texts.items():
        write(base / "decompile_callers_after" / filename, text)


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_signature_regression_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("int slot_index, int candidate_index", "int param_1, int param_2, int param_3")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("signature mismatch" in failure for failure in failures)


def test_stale_decompile_param_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        path = base / "decompile_after" / "004903a0_CDXEngine__BuildOverlaySlotFromSortedEntry.c"
        path.write_text(path.read_text(encoding="utf-8") + " param_3\n", encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("stale decompile token" in failure for failure in failures)


def test_caller_artifact_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        path = base / "decompile_callers_after" / "0044a640_CDXEngine__SetOverlaySlotVisibilityByPlayerView.c"
        path.write_text(path.read_text(encoding="utf-8") + " unaff_retaddr\n", encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("stale caller token" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("runtime render behavior and rebuild parity remain unproven", "runtime render behavior proven")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [
        test_good_fixture_passes,
        test_signature_regression_fails,
        test_stale_decompile_param_fails,
        test_caller_artifact_fails,
        test_runtime_overclaim_fails,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
