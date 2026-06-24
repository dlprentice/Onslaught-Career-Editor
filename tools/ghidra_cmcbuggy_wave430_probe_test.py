#!/usr/bin/env python3
"""Self-tests for the Wave430 CMCBuggy/wheel-motion probe."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_cmcbuggy_wave430_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_parse_summary() -> None:
    text = "SUMMARY: updated=15 skipped=0 renamed=9 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 15,
        "skipped": 0,
        "renamed": 9,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }


def test_token_and_address_helpers() -> None:
    assert probe.normalize_address("493020") == "0x00493020"
    assert probe.normalize_address("0x493020") == "0x00493020"
    assert probe.token_present("RET 0x50 confirms twenty stack arguments", "ret 0x50")
    assert probe.unescape(r"one\ttwo\nthree\\four") == "one\ttwo\nthree\\four"


def test_apply_log_failure_detection() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        write(base / "apply.log", "SUMMARY: updated=14 skipped=0 renamed=9 would_rename=0 missing=0 bad=1\n")
        failures: list[str] = []
        probe.check_apply_log(base, "apply.log", probe.EXPECTED_APPLY, failures)
        assert failures
        assert "summary mismatch" in failures[0]


def test_minimal_success_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        write(base / "apply_dry.log", "SUMMARY: updated=0 skipped=15 renamed=0 would_rename=9 missing=0 bad=0\n")
        write(base / "apply.log", "SUMMARY: updated=15 skipped=0 renamed=9 would_rename=0 missing=0 bad=0\n")
        write(base / "apply_fix_dry.log", "SUMMARY: updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0\n")
        write(base / "apply_fix.log", "SUMMARY: updated=15 skipped=0 renamed=0 would_rename=0 missing=0 bad=0\n")

        metadata_rows = ["address\tname\tsignature\tcomment\tstatus"]
        tags_rows = ["address\tname\ttags\tstatus"]
        xrefs_rows = ["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"]
        instruction_rows = ["target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type"]
        updatewheel_rows = instruction_rows[:]

        for index, (address, spec) in enumerate(probe.TARGETS.items()):
            comment = " ".join(spec["commentTokens"])  # type: ignore[index]
            metadata_rows.append(f"{address}\t{spec['name']}\t{spec['signature']}\t{comment}\tOK")
            tags_rows.append(f"{address}\t{spec['name']}\t{','.join(spec['tags'])}\tOK")  # type: ignore[index]
            xref_tokens = " ".join(spec["xrefTokens"]) if spec["xrefTokens"] else "xref"  # type: ignore[index]
            xrefs_rows.append(f"{address}\t{spec['name']}\t0x005000{index:02x}\t0x00500000\t{xref_tokens}\tUNCONDITIONAL_CALL")
            ret_operand = probe.INSTRUCTION_RETURNS.get(address)
            if ret_operand is not None:
                row = f"{address}\t{address}\tAFTER\t1\t0x005100{index:02x}\t{address}\t{spec['name']}\tRET\t{ret_operand}\tc3\tTERMINATOR"
                if address == "0x004934f0":
                    updatewheel_rows.append(row)
                else:
                    instruction_rows.append(row)

        for address, (mnemonic, operand) in probe.EXPECTED_TAIL_CALLS.items():
            instruction_rows.append(f"{address}\t{address}\tAFTER\t1\t0x00520000\t{address}\ttail\t{mnemonic}\t{operand}\te9\tCALL_TERMINATOR")

        for address, spec in probe.TARGETS.items():
            decomp = " ".join(spec["decompileTokens"])  # type: ignore[index]
            write(base / "decompile_after" / f"{address[2:]}_{spec['name']}.c", decomp)

        write(base / "metadata_after.tsv", "\n".join(metadata_rows) + "\n")
        write(base / "tags_after.tsv", "\n".join(tags_rows) + "\n")
        write(base / "xrefs_before.tsv", "\n".join(xrefs_rows) + "\n")
        write(base / "instructions_before.tsv", "\n".join(instruction_rows) + "\n")
        write(base / "instructions_updatewheel_full.tsv", "\n".join(updatewheel_rows) + "\n")

        for address, text in probe.EXPECTED_STRINGS.items():
            write(base / f"string_{address}.tsv", f"input_addr\tmode\tptr_raw\ttarget_addr\tcstring\n{address}\tdirect\t\t{address}\t{text}\n")

        vtable = [
            "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus",
            "005dc250\t1\t005dc254\t0x00493080\t00493080\t00493080\tfn\t00493080\tfn\tOK",
            "005dc250\t4\t005dc260\t0x004944d0\t004944d0\t<none>\t<no_function>\t<none>\t<no_function>\tNO_FUNCTION_AT_POINTER",
            "005dc250\t5\t005dc264\t0x00494940\t00494940\t<none>\t<no_function>\t<none>\t<no_function>\tNO_FUNCTION_AT_POINTER",
            "005dc27c\t1\t005dc280\t0x00494ca0\t00494ca0\t00494ca0\tfn\t00494ca0\tfn\tOK",
            "005dc27c\t4\t005dc28c\t0x00494ce0\t00494ce0\t00494ce0\tfn\t00494ce0\tfn\tOK",
            "005dc27c\t6\t005dc294\t0x00494fa0\t00494fa0\t00494fa0\tfn\t00494fa0\tfn\tOK",
            "005dc27c\t8\t005dc29c\t0x00495020\t00495020\t00495020\tfn\t00495020\tfn\tOK",
        ]
        write(base / "vtables_before.tsv", "\n".join(vtable) + "\n")

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
