#!/usr/bin/env python3
"""Self-tests for ghidra_particle_token_landscape_wave420_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_particle_token_landscape_wave420_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=5 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
    )
    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tag_lines = ["address\tname\ttags\tstatus"]
    xref_lines = ["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"]
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
        tag_lines.append(f"{address}\t{expected['name']}\t{';'.join(tags)}\tOK")
        xref_lines.append(f"{address}\t{expected['name']}\t0x0\t0x0\tcaller\tUNCONDITIONAL_CALL")
        clean = address.replace("0x", "")
        write(
            base / "decompile_after" / f"{clean}_{expected['name']}.c",
            " ".join(str(token) for token in expected["decompileTokens"]),
        )
    write(base / "metadata_after.tsv", "\n".join(metadata_lines) + "\n")
    write(base / "tags_after.tsv", "\n".join(tag_lines) + "\n")
    write(base / "xrefs_after.tsv", "\n".join(xref_lines) + "\n")


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_stale_owner_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CDXMemBuffer__OpenReadMode11", "CParticleSet__OpenRead", 1)
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("stale names still present" in failure for failure in failures)


def test_cube_stale_signature_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace(
            "void __cdecl CDXEngine__FormatCubeTextureFilename(char * out_path, int cube_index, int suffix_index)",
            "void __cdecl CDXEngine__FormatCubeTextureFilename(void * param_1)",
        )
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("stale signature present" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("landscape render behavior remains unproven", "landscape render behavior proven")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [
        test_good_fixture_passes,
        test_stale_owner_name_fails,
        test_cube_stale_signature_fails,
        test_runtime_overclaim_fails,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
