#!/usr/bin/env python3
"""Tests for the second Ghidra name-confidence comment-pass probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche2_comment_pass_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_fixture(root: Path, *, omit_runtime_boundary: bool = False) -> dict[str, Path]:
    dry_log = root / "comments_dry.log"
    apply_log = root / "comments_apply.log"
    metadata = root / "metadata_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    decompile = root / "decompile_after"
    decompile.mkdir()

    dry_log.write_text(
        "\n".join(
            ["Mode: dry"]
            + [f"DRY: {target['address']} {target['name']}" for target in probe.TARGETS]
            + ["--- SUMMARY ---", "applied=0 skipped=9 missing=0 bad=0"]
        )
        + "\n",
        encoding="utf-8",
    )
    apply_log.write_text(
        "\n".join(
            ["Mode: apply"]
            + [f"OK: {target['address']} {target['name']}" for target in probe.TARGETS]
            + ["--- SUMMARY ---", "applied=9 skipped=0 missing=0 bad=0"]
        )
        + "\n",
        encoding="utf-8",
    )

    metadata_rows: list[str] = []
    index_rows: list[str] = []
    xref_rows: list[str] = []
    for index, target in enumerate(probe.TARGETS):
        comment = " ".join(target["commentTokens"])
        if index == 0 and omit_runtime_boundary:
            comment = comment.replace("runtime behavior remain", "runtime behavior proven")
        metadata_rows.append(
            "\t".join(
                [
                    target["address"],
                    target["name"],
                    f"void {target['name']}(void)",
                    comment,
                    "OK",
                ]
            )
            + "\n"
        )
        index_rows.append("\t".join([target["address"], target["name"], f"void {target['name']}(void)", "OK"]) + "\n")
        (decompile / f"{target['address'][2:]}_{target['name']}.c").write_text(
            " ".join(target["decompileTokens"]),
            encoding="utf-8",
        )
        expected_functions = list(target.get("expectedXrefFunctions", []))
        if expected_functions:
            for fn in expected_functions:
                xref_rows.append(f"{target['address'][2:]}\t{target['name']}\t00400000\t00400000\t{fn}\tUNCONDITIONAL_CALL\n")
        else:
            expected_rows = int(target.get("expectedXrefRows", 1))
            for row_index in range(expected_rows):
                xref_rows.append(
                    f"{target['address'][2:]}\t{target['name']}\t0040{row_index:04x}\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
                )

    metadata.write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    return {
        "dry_log": dry_log,
        "apply_log": apply_log,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
    }


class GhidraNameConfidenceTranche2CommentPassProbeTests(unittest.TestCase):
    def test_passes_for_clean_comment_context_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "tranche2-comment-candidates-commented")
        self.assertTrue(report["readback"]["allCommentsAndContextPresent"])

    def test_fails_when_comment_loses_runtime_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_runtime_boundary=True)
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x00411bf0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
