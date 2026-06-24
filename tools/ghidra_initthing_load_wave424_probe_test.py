#!/usr/bin/env python3
"""Self-tests for ghidra_initthing_load_wave424_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_initthing_load_wave424_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
    )
    write(
        base / "metadata_after.tsv",
        "\n".join(
            [
                "address\tname\tsignature\tcomment\tstatus",
                "\t".join(
                    [
                        probe.ADDRESS,
                        probe.NAME,
                        probe.SIGNATURE,
                        " ".join(probe.COMMENT_TOKENS),
                        "OK",
                    ]
                ),
            ]
        )
        + "\n",
    )
    tags = sorted(probe.COMMON_TAGS | probe.TARGET_TAGS)
    write(base / "tags_after.tsv", f"address\tname\ttags\tstatus\n{probe.ADDRESS}\t{probe.NAME}\t{';'.join(tags)}\tOK\n")
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        f"{probe.ADDRESS}\t{probe.NAME}\t0x0048d8df\t0x0048d8d0\t"
        "CSquadInitThing__LoadFromMemBuffer\tUNCONDITIONAL_CALL\n",
    )
    clean = probe.ADDRESS.replace("0x", "")
    write(base / "decompile_after" / f"{clean}_{probe.NAME}.c", " ".join(probe.DECOMPILE_TOKENS))


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_param_name_regression_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("int version, void * mem_buffer", "int param_1, int param_2")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("signature mismatch" in failure for failure in failures)


def test_missing_tag_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "tags_after.tsv").read_text(encoding="utf-8")
        text = text.replace(";signature-corrected", "")
        (base / "tags_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("missing tags" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace(
            "runtime level-load behavior and rebuild parity remain unproven",
            "runtime level-load behavior proven",
        )
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [
        test_good_fixture_passes,
        test_param_name_regression_fails,
        test_missing_tag_fails,
        test_runtime_overclaim_fails,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
