#!/usr/bin/env python3
"""Self-tests for the Wave431 destructable-segments probe."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_cmcbuggy_hiveboss_wave431_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_parse_summary() -> None:
    text = "SUMMARY: updated=2 skipped=0 renamed=2 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 2,
        "skipped": 0,
        "renamed": 2,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }


def test_token_and_address_helpers() -> None:
    assert probe.normalize_address("497140") == "0x00497140"
    assert probe.normalize_address("0x497130") == "0x00497130"
    assert probe.token_present("RET 0x4 confirms one stack argument", "ret 0x4")
    assert probe.unescape(r"one\ttwo\nthree\\four") == "one\ttwo\nthree\\four"


def test_apply_log_failure_detection() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        write(base / "apply.log", "SUMMARY: updated=1 skipped=0 renamed=2 would_rename=0 missing=0 bad=1\n")
        failures: list[str] = []
        probe.check_apply_log(base, "apply.log", probe.EXPECTED_APPLY, failures)
        assert failures
        assert "summary mismatch" in failures[0]


def test_minimal_success_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        write(base / "apply_dry.log", "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=2 missing=0 bad=0\n")
        write(base / "apply.log", "REPORT: Save succeeded\nSUMMARY: updated=2 skipped=0 renamed=2 would_rename=0 missing=0 bad=0\n")
        write(base / "apply_verify_dry.log", "REPORT: Save succeeded\nSUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0\n")

        metadata_rows = ["address\tname\tsignature\tcomment\tstatus"]
        tags_rows = ["address\tname\ttags\tstatus"]
        xrefs_rows = ["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"]
        instruction_rows = ["target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type"]
        full_rows = instruction_rows[:]

        for index, (address, spec) in enumerate(probe.TARGETS.items()):
            comment = " ".join(spec["commentTokens"])  # type: ignore[index]
            metadata_rows.append(f"{address}\t{spec['name']}\t{spec['signature']}\t{comment}\tOK")
            tags_rows.append(f"{address}\t{spec['name']}\t{','.join(spec['tags'])}\tOK")  # type: ignore[index]
            xref_tokens = " ".join(spec["xrefTokens"]) if spec["xrefTokens"] else "xref"  # type: ignore[index]
            xrefs_rows.append(f"{address}\t{spec['name']}\t0x004976f1\t<none>\t{xref_tokens}\tUNCONDITIONAL_CALL")
            decomp = " ".join(spec["decompileTokens"])  # type: ignore[index]
            write(base / "decompile_after" / f"{address[2:]}_{spec['name']}.c", decomp)
            for role, mnemonic, operand in probe.EXPECTED_INSTRUCTIONS[address]:
                row = f"{address}\t{address}\t{role}\t{index}\t{address}\t{address}\t{spec['name']}\t{mnemonic}\t{operand}\tc3\tTERMINATOR"
                if address == "0x00497140":
                    full_rows.append(row)
                else:
                    instruction_rows.append(row)

        write(base / "metadata_after.tsv", "\n".join(metadata_rows) + "\n")
        write(base / "tags_after.tsv", "\n".join(tags_rows) + "\n")
        write(base / "xrefs_after.tsv", "\n".join(xrefs_rows) + "\n")
        write(base / "instructions_after.tsv", "\n".join(instruction_rows) + "\n")
        write(base / "instructions_cylinders_full_after.tsv", "\n".join(full_rows) + "\n")

        result = probe.run(base)
        assert result["status"] == "PASS", result["failures"]


def main() -> int:
    tests = [
        test_parse_summary,
        test_token_and_address_helpers,
        test_apply_log_failure_detection,
        test_minimal_success_fixture,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
