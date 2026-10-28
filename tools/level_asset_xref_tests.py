#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Selected-level asset cross-references using authored data only."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import content_catalog_tests as fixtures
import level_asset_xref as xref


def sample_archive(*, bad_text: bool = False, duplicate_mesh: bool = False,
                   wdat: bytes | None = None) -> bytes:
    """One authored level resource with distinct matching and excluded records."""
    header = fixtures.chunk(b"LVLR", bytes(4))
    selected = fixtures.named_mesh_record("authored.msh")
    if duplicate_mesh:
        selected += fixtures.named_mesh_record("AUTHORED.msh")
    matching = fixtures.text_record("MESHTEX\\skin.tga", requested=1, levels=-1)
    matching += fixtures.text_record("meshtex\\Skin.tga", requested=1, levels=-1)
    excluded = fixtures.text_record("meshtex\\skin.tga", requested=2, levels=-1)
    excluded += fixtures.text_record("meshtex\\skin.tga", requested=1, levels=0)
    if bad_text:
        excluded += fixtures.chunk(b"TEXT", b"malformed-secret-payload")
    if wdat is None:
        wdat = (123).to_bytes(4, "little", signed=True) + (456).to_bytes(4, "little", signed=True)
    world = fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", fixtures.chunk(b"WDAT", wdat)))
    return fixtures.aya(header + selected + matching + excluded + world)


class SelectedArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="level-xref-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "100_res_PC.aya"
        self.mesh = self.root / "m_authored.msh.aya"
        self.archive.write_bytes(sample_archive())
        self.mesh.write_bytes(fixtures.aya(fixtures.mesh_stream()))

    def run_cli(self, args: list[str]) -> tuple[int, str, str]:
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            try:
                rc = xref.main(args)
            except SystemExit as exc:
                rc = exc.code
        return rc, output.getvalue(), error.getvalue()

    def test_independent_archive_occurrences_and_format_filters(self) -> None:
        before = self.archive.read_bytes(), self.mesh.read_bytes()
        report = xref.report_for(self.archive, [self.mesh])
        self.assertEqual(xref.SCHEMA, report["schema"])
        self.assertTrue(report["generatedRetailDerived"])
        self.assertEqual(100, report["archive"]["filenameLevelHint"])
        self.assertEqual((123, 456), (report["archive"]["worldHeader"]["baseLevel"],
                                      report["archive"]["worldHeader"]["realLevel"]))
        [mesh_occurrence] = report["archiveMeshOccurrences"]
        self.assertEqual((mesh_occurrence["name"], mesh_occurrence["selectedFilenameCandidates"]),
                         ("authored.msh", [0]))
        self.assertEqual(mesh_occurrence["filenameCandidateStatus"], "evaluated-filename-only")
        [mesh] = report["selectedMeshes"]
        self.assertEqual(mesh["archiveMeshFilenameCandidates"], [mesh_occurrence["chunk"]])
        self.assertEqual(mesh["archiveMeshFilenameCandidateStatus"], "evaluated-comparable-named-meshes")
        [slot] = mesh["textures"]
        self.assertEqual(slot["name"], "meshtex\\Skin.tga")
        self.assertEqual(slot["requestedFormat"], 1)
        self.assertEqual(slot["sameArchiveTextCandidates"], [2, 3])
        self.assertEqual(slot["candidateStatus"], "known-candidates-top-level-text-only")
        self.assertEqual([1, 1, 2, 1], [r["requestedFormat"] for r in report["archiveTopLevelTextOccurrences"]])
        self.assertEqual(report["coverage"]["unparsedTopLevelTextOccurrences"], 0)
        self.assertEqual(before, (self.archive.read_bytes(), self.mesh.read_bytes()))
        encoded = xref.report_bytes(self.archive, [self.mesh])
        self.assertEqual(json.loads(encoded), report)
        self.assertEqual(encoded, xref.report_bytes(self.archive, [self.mesh]))
        self.assertNotIn(b"malformed-secret-payload", encoded)

    def test_partial_text_coverage_never_claims_no_possible_match(self) -> None:
        self.archive.write_bytes(sample_archive(bad_text=True))
        report = xref.report_for(self.archive, [self.mesh])
        self.assertEqual(report["coverage"]["unparsedTopLevelTextOccurrences"], 1)
        self.assertIsNone(report["archiveTopLevelTextOccurrences"][-1]["name"])
        [slot] = report["selectedMeshes"][0]["textures"]
        self.assertEqual(slot["sameArchiveTextCandidates"], [2, 3])
        self.assertEqual(slot["candidateStatus"], "known-candidates-partial-text-coverage")
        self.assertNotIn("malformed-secret-payload", json.dumps(report))

    def test_no_match_distinguishes_complete_top_level_from_partial(self) -> None:
        mesh = fixtures.named_mesh_record("authored.msh")
        wrong = fixtures.text_record("meshtex\\Skin.tga", requested=4, levels=-1)
        for extra, expected in ((b"", "no-candidate-known-top-level-text-only"),
                                (fixtures.chunk(b"TEXT", b"bad"), "no-known-candidate-partial-text-coverage")):
            with self.subTest(expected=expected):
                self.archive.write_bytes(fixtures.aya(mesh + wrong + extra))
                slot = xref.report_for(self.archive, [self.mesh])["selectedMeshes"][0]["textures"][0]
                self.assertEqual(slot["sameArchiveTextCandidates"], [])
                self.assertEqual(slot["candidateStatus"], expected)

    def test_parsed_uncomparable_text_marks_coverage_partial(self) -> None:
        mesh = fixtures.named_mesh_record("authored.msh")
        # This record is structurally valid, but DEL is outside the supported
        # printable-ASCII comparison profile.
        unsupported = fixtures.text_record("meshtex\\Skin.tg\x7f", requested=1, levels=-1)
        self.archive.write_bytes(fixtures.aya(mesh + unsupported))
        report = xref.report_for(self.archive, [self.mesh])
        self.assertEqual(report["coverage"]["unparsedTopLevelTextOccurrences"], 0)
        self.assertEqual(report["coverage"]["uncomparableTopLevelTextOccurrences"], 1)
        [text] = report["archiveTopLevelTextOccurrences"]
        self.assertEqual(text["status"], "parsed-name-uncomparable")
        self.assertIsNone(text["name"])
        [slot] = report["selectedMeshes"][0]["textures"]
        self.assertEqual(slot["sameArchiveTextCandidates"], [])
        self.assertEqual(slot["candidateStatus"], "no-known-candidate-partial-text-coverage")

    def test_duplicate_mesh_and_filename_candidates_stay_distinct(self) -> None:
        self.archive.write_bytes(sample_archive(duplicate_mesh=True))
        other = self.root / "M_AUTHORED.MSH.AYA"
        other.write_bytes(self.mesh.read_bytes())
        report = xref.report_for(self.archive, [self.mesh, other])
        self.assertEqual([r["selectedFilenameCandidates"] for r in report["archiveMeshOccurrences"]], [[0, 1], [0, 1]])
        self.assertEqual([r["archiveMeshFilenameCandidates"] for r in report["selectedMeshes"]], [[1, 2], [1, 2]])

    def test_empty_selection_and_missing_candidate_are_not_missing_files(self) -> None:
        empty = xref.report_for(self.archive, [])
        self.assertEqual(empty["selectedMeshes"], [])
        self.assertEqual(empty["archiveMeshOccurrences"][0]["selectedFilenameCandidates"], [])
        unmatched = self.root / "m_unrelated.msh.aya"
        unmatched.write_bytes(self.mesh.read_bytes())
        report = xref.report_for(self.archive, [unmatched])
        self.assertEqual(report["selectedMeshes"][0]["archiveMeshFilenameCandidates"], [])
        self.assertEqual(report["selectedMeshes"][0]["textures"][0]["sameArchiveTextCandidates"], [2, 3])
        self.assertIn("not verified source paths or runtime use", report["coverage"]["limits"])

    def test_unparsed_mesh_and_unknown_slot_names_are_not_empty_counts(self) -> None:
        malformed = self.root / "m_broken.msh.aya"
        malformed.write_bytes(fixtures.aya(b"opaque-author-data"))
        row = xref.report_for(self.archive, [malformed])["selectedMeshes"][0]
        self.assertEqual(row["status"], "unparsed")
        self.assertIsNone(row["textures"])
        original = fixtures.mesh_stream()
        old = b"meshtex\\Skin.tga".ljust(128, b"\0")
        for raw in (b"X" * 128, b"meshtex\\\xff.tga".ljust(128, b"\0"), b"short\0".ljust(128, b"\0")):
            with self.subTest(raw=raw):
                self.mesh.write_bytes(fixtures.aya(original.replace(old, raw, 1)))
                slot = xref.report_for(self.archive, [self.mesh])["selectedMeshes"][0]["textures"][0]
                self.assertIsNone(slot["sameArchiveTextCandidates"])
                self.assertEqual(slot["candidateStatus"], "unknown")

    def test_selected_internal_name_is_bounded_and_never_invented(self) -> None:
        original = fixtures.mesh_stream()
        start = 8 + 0x24  # CMSH header plus the source-backed name offset.
        end = start + 300
        cases = (
            (b"A" * 299 + b"\0", "A" * 299),
            (b"A" * 300, None),  # The next pointer's NUL is not a name terminator.
            (bytes(300), None),
            (b"bad\xff\0".ljust(300, b"\0"), None),
            (b"control\x7f\0".ljust(300, b"\0"), None),
            ("é".encode().ljust(300, b"\0"), None),  # The xref only reports ASCII names.
        )
        for field, expected in cases:
            with self.subTest(field=field[:12]):
                changed = bytearray(original)
                changed[start:end] = field
                changed[end:end + 4] = b"\0PTR"  # Non-name bytes immediately after the field.
                packed = fixtures.aya(bytes(changed))
                self.mesh.write_bytes(packed)
                row = xref.report_for(self.archive, [self.mesh])["selectedMeshes"][0]
                self.assertEqual(row["status"], "parsed")
                self.assertEqual(row["internalName"], expected)
                self.assertEqual(row["archiveMeshFilenameCandidates"], [1])
                self.assertEqual(row["textures"][0]["name"], "meshtex\\Skin.tga")
                self.assertEqual(self.mesh.read_bytes(), packed)
                if field == b"A" * 300:
                    rc, output, _ = self.run_cli(["--archive", str(self.archive), "--mesh", str(self.mesh), "--stdout"])
                    self.assertEqual(rc, 0)
                    self.assertIsNone(json.loads(output)["selectedMeshes"][0]["internalName"])

    def test_unknown_mesh_record_and_wdat_limits_are_explicit(self) -> None:
        self.archive.write_bytes(fixtures.aya(fixtures.chunk(b"MESH", b"bad")
                                 + fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", fixtures.chunk(b"WDAT", b"x")))))
        report = xref.report_for(self.archive, [])
        self.assertEqual(report["coverage"]["unparsedMeshOccurrences"], 1)
        self.assertEqual(report["archiveMeshOccurrences"][0]["status"], "unparsed")
        self.assertIsNone(report["archiveMeshOccurrences"][0]["name"])
        self.assertIsNone(report["archiveMeshOccurrences"][0]["selectedFilenameCandidates"])
        self.assertEqual(report["archive"]["worldHeader"]["status"], "unparsed")
        self.assertIsNone(report["archive"]["worldHeader"]["realLevel"])

    def test_uncomparable_and_embedded_mesh_names_have_unknown_candidates(self) -> None:
        unknown = [fixtures.named_mesh_record("dir/authored.msh"),
                   fixtures.named_mesh_record("authored\x7f.msh"),
                   fixtures.named_mesh_record("")]
        self.archive.write_bytes(fixtures.aya(fixtures.named_mesh_record("authored.msh") + b"".join(unknown)))
        report = xref.report_for(self.archive, [self.mesh])
        rows = report["archiveMeshOccurrences"]
        self.assertEqual(report["coverage"]["uncomparableMeshFilenameOccurrences"], 3)
        self.assertEqual([r["filenameCandidateStatus"] for r in rows[1:]], ["unknown-not-comparable"] * 3)
        self.assertEqual([r["selectedFilenameCandidates"] for r in rows[1:]], [None] * 3)
        self.assertEqual(rows[2]["status"], "named-uncomparable")
        self.assertIsNone(rows[2]["name"])
        self.assertEqual(rows[3]["status"], "embedded-not-inspected")
        self.assertEqual(report["selectedMeshes"][0]["archiveMeshFilenameCandidates"], [0])
        self.assertEqual(report["selectedMeshes"][0]["archiveMeshFilenameCandidateStatus"],
                         "partial-uncomparable-archive-meshes")

    def test_uncomparable_selected_filename_has_unknown_reverse_candidates(self) -> None:
        unsupported = self.root / "m_é.msh.aya"
        unsupported.write_bytes(self.mesh.read_bytes())
        [row] = xref.report_for(self.archive, [unsupported])["selectedMeshes"]
        self.assertIsNone(row["filename"])
        self.assertIsNone(row["archiveMeshFilenameCandidates"])
        self.assertEqual(row["archiveMeshFilenameCandidateStatus"], "unknown-selected-filename")

    def test_ambiguous_wdat_is_not_silently_overwritten(self) -> None:
        wdat = fixtures.chunk(b"WDAT", bytes(8))
        world = fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", wdat + wdat))
        self.archive.write_bytes(fixtures.aya(world))
        self.assertEqual(xref.report_for(self.archive, [])["archive"]["worldHeader"]["status"], "ambiguous")

    def test_absent_world_is_unknown_and_nested_count_is_bounded(self) -> None:
        self.archive.write_bytes(fixtures.aya(fixtures.chunk(b"LVLR", bytes(4))))
        self.assertEqual(xref.report_for(self.archive, [])["archive"]["worldHeader"]["status"], "absent")
        world = fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", fixtures.chunk(b"SKIP", b"")
                                                       + fixtures.chunk(b"WDAT", bytes(8))))
        self.archive.write_bytes(fixtures.aya(world))
        with mock.patch.object(xref, "MAX_NESTED_CHUNKS", 1):
            self.assertEqual(xref.report_for(self.archive, [])["archive"]["worldHeader"]["status"], "unparsed")

    def test_input_and_candidate_resource_bounds_fail_closed(self) -> None:
        with mock.patch.object(xref, "MAX_MESH_INPUTS", 0):
            with self.assertRaisesRegex(ValueError, "at most"):
                xref.report_for(self.archive, [self.mesh])
        with mock.patch.object(xref, "MAX_COMPRESSED_TOTAL", 1):
            with self.assertRaisesRegex(ValueError, "compressed-byte"):
                xref.report_for(self.archive, [])
        with mock.patch.object(xref, "MAX_MESH_INFLATED_TOTAL", 1):
            with self.assertRaisesRegex(ValueError, "inflated-byte"):
                xref.report_for(self.archive, [self.mesh])
        with mock.patch.object(xref, "MAX_ARCHIVE_ASSET_ROWS", 1):
            with self.assertRaisesRegex(ValueError, "occurrence limit"):
                xref.report_for(self.archive, [])
        with mock.patch.object(xref, "MAX_CANDIDATE_LINKS", 1):
            with self.assertRaisesRegex(ValueError, "candidate link limit"):
                xref.report_for(self.archive, [self.mesh])

    def test_bad_mesh_still_counts_its_inflated_bytes_toward_budget(self) -> None:
        malformed = self.root / "m_broken.msh.aya"
        malformed.write_bytes(fixtures.aya(b"opaque-author-data"))
        with mock.patch.object(xref, "MAX_MESH_INFLATED_TOTAL", 1):
            with self.assertRaisesRegex(ValueError, "inflated-byte"):
                xref.report_for(self.archive, [malformed])

    def test_filename_aliases_hardlinks_and_parent_traversal_refuse(self) -> None:
        with self.assertRaisesRegex(ValueError, "more than once"):
            xref.report_for(self.archive, [self.mesh, self.mesh])
        hardlink = self.root / "m_second.msh.aya"
        os.link(self.mesh, hardlink)
        with self.assertRaisesRegex(ValueError, "hard link"):
            xref.report_for(self.archive, [self.mesh])
        hardlink.unlink()
        link = self.root / "alias.aya"
        link.symlink_to(self.mesh.name)
        with self.assertRaises((ValueError, OSError)):
            xref.report_for(self.archive, [link])
        with self.assertRaisesRegex(ValueError, "parent path"):
            xref.report_for(self.archive, [self.root / ".." / self.root.name / self.mesh.name])

    def test_replacement_after_analysis_refuses_callable_and_cli(self) -> None:
        original = xref._report_for
        old = self.mesh.with_name("before-replacement.aya")
        def replace(*args):
            result = original(*args)
            self.mesh.rename(old)
            self.mesh.write_bytes(fixtures.aya(b"different"))
            return result
        with mock.patch.object(xref, "_report_for", side_effect=replace):
            rc, output, _ = self.run_cli(["--archive", str(self.archive), "--mesh", str(self.mesh), "--stdout"])
        self.assertNotEqual(rc, 0)
        self.assertEqual(output, "")
        self.mesh.unlink()
        old.rename(self.mesh)
        with mock.patch.object(xref, "_report_for", side_effect=replace):
            with self.assertRaisesRegex(ValueError, "changed before report emission"):
                xref.report_bytes(self.archive, [self.mesh])

    def test_real_cli_stdout_and_legacy_out_refusal(self) -> None:
        script = Path(xref.__file__)
        command = [sys.executable, str(script), "--archive", str(self.archive), "--mesh", str(self.mesh), "--stdout"]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.encode(), xref.report_bytes(self.archive, [self.mesh]))
        target = self.root / "report.json"
        result = subprocess.run(command + ["--out", str(target)], capture_output=True, text=True, timeout=10, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertFalse(target.exists())

    def test_real_cli_opens_no_write_file_and_audit_negative_fires(self) -> None:
        wrapper = """
import os, runpy, sys
def audit(event, args):
    if event == "open":
        _path, mode, flags = args
        if ((isinstance(mode, str) and any(c in mode for c in "wax+")) or
            (isinstance(flags, int) and
             ((flags & os.O_ACCMODE) != os.O_RDONLY or flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND)))):
            raise RuntimeError("unexpected write-open by CLI")
sys.addaudithook(audit)
if os.environ.get("XREF_AUDIT_NEGATIVE"):
    os.open(os.environ["XREF_AUDIT_NEGATIVE"], os.O_WRONLY | os.O_CREAT, 0o600)
script, archive, mesh = sys.argv[1:]
sys.argv = [script, "--archive", archive, "--mesh", mesh, "--stdout"]
sys.path.insert(0, os.path.dirname(script))
runpy.run_path(script, run_name="__main__")
"""
        script = str(Path(xref.__file__))
        command = [sys.executable, "-c", wrapper, script, str(self.archive), str(self.mesh)]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        env.pop("XREF_AUDIT_NEGATIVE", None)
        before = {path.relative_to(self.root) for path in self.root.rglob("*")}
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.encode(), xref.report_bytes(self.archive, [self.mesh]))
        self.assertEqual(before, {path.relative_to(self.root) for path in self.root.rglob("*")})
        target = self.root / "not-created"
        env["XREF_AUDIT_NEGATIVE"] = str(target)
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected write-open by CLI", result.stderr)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
