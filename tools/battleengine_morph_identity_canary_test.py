#!/usr/bin/env python3
"""Focused synthetic tests for the morph identity canary protocol."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import tempfile
import unittest
from unittest import mock

import battleengine_morph_identity_canary as canary


TEMPLATE = (
    Path(__file__).parent
    / "runtime-probes"
    / "battleengine-morph-identity-canary.cdb.tmpl"
)


def build_pe32_fixture(
    path: Path,
    *,
    executable_rvas: tuple[int, ...] = tuple(canary.PROBE_RVAS.values()),
    relocation_rvas: tuple[int, ...] = (0x000081D0,),
    image_base: int = 0x00400000,
    optional_magic: int = 0x010B,
    executable: bool = True,
    truncate_at: int | None = None,
) -> Path:
    pe_offset = 0x80
    optional_size = 0xE0
    section_table = pe_offset + 4 + 20 + optional_size
    text_rva = 0x1000
    text_raw = 0x400
    text_size = 0xE0000
    reloc_rva = 0xE1000
    reloc_raw = text_raw + text_size
    reloc_size = 0x400
    data = bytearray(reloc_raw + reloc_size)

    data[0:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, pe_offset)
    data[pe_offset : pe_offset + 4] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, pe_offset + 4, 0x014C, 2, 0, 0, 0, optional_size, 0x010F)
    optional = pe_offset + 24
    struct.pack_into("<H", data, optional, optional_magic)
    struct.pack_into("<I", data, optional + 28, image_base)
    struct.pack_into("<I", data, optional + 32, 0x1000)
    struct.pack_into("<I", data, optional + 36, 0x200)
    struct.pack_into("<I", data, optional + 56, 0xF0000)
    struct.pack_into("<I", data, optional + 60, 0x400)
    struct.pack_into("<I", data, optional + 92, 16)

    reloc_blob = bytearray()
    for page_rva in sorted({rva & ~0xFFF for rva in relocation_rvas}):
        entries = [rva for rva in relocation_rvas if (rva & ~0xFFF) == page_rva]
        block_size = 8 + 2 * len(entries)
        if block_size % 4:
            block_size += 2
        block = bytearray(block_size)
        struct.pack_into("<II", block, 0, page_rva, block_size)
        for index, rva in enumerate(entries):
            struct.pack_into("<H", block, 8 + index * 2, (3 << 12) | (rva & 0xFFF))
        reloc_blob.extend(block)
    data[reloc_raw : reloc_raw + len(reloc_blob)] = reloc_blob
    struct.pack_into(
        "<II", data, optional + 96 + 5 * 8, reloc_rva if reloc_blob else 0, len(reloc_blob)
    )

    text_characteristics = 0x60000020 if executable else 0x40000040
    struct.pack_into(
        "<8sIIIIIIHHI",
        data,
        section_table,
        b".text\0\0\0",
        text_size,
        text_rva,
        text_size,
        text_raw,
        0,
        0,
        0,
        0,
        text_characteristics,
    )
    struct.pack_into(
        "<8sIIIIIIHHI",
        data,
        section_table + 40,
        b".reloc\0\0",
        reloc_size,
        reloc_rva,
        reloc_size,
        reloc_raw,
        0,
        0,
        0,
        0,
        0x42000040,
    )
    for index, rva in enumerate(executable_rvas):
        raw = text_raw + (rva - text_rva)
        data[raw : raw + 8] = bytes((index * 17 + offset + 1) & 0xFF for offset in range(8))
    if truncate_at is not None:
        data = data[:truncate_at]
    path.write_bytes(data)
    return path


def render_fixture(exe: Path, template: Path = TEMPLATE) -> canary.RenderedCommand:
    payload = exe.read_bytes()
    with mock.patch.object(canary, "CANONICAL_SIZE", len(payload)), mock.patch.object(
        canary, "CANONICAL_SHA256", hashlib.sha256(payload).hexdigest()
    ):
        return canary.render_private_command(exe, template)


def private_artifact(rendered: canary.RenderedCommand, executable: Path, path: Path) -> Path:
    command = path.with_suffix(".cdb")
    command.write_bytes(rendered.text.encode("ascii"))
    payload = {
        "schema": canary.PRIVATE_RUN_SCHEMA,
        "executablePath": str(executable),
        "templatePath": str(TEMPLATE),
        "commandPath": str(command),
        "receiptSha256": "1" * 64,
        "commandSha256": rendered.sha256,
        "templateSha256": rendered.template_sha256,
        "executableSha256": canary.CANONICAL_SHA256,
        "fingerprints": [
            {
                "event": target.event,
                "rva": target.rva,
                "length": target.size,
                "sha256": target.sha256,
            }
            for target in rendered.targets
        ],
        "sourceUnchanged": True,
        "copyUnchanged": True,
        "cleanup": {
            "keysReleased": True,
            "cdbDetached": True,
            "managedProcessStopped": True,
            "ownedProcessCount": 0,
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def event_log(path: Path, *, include_events: bool = True, state_seed: int = 0) -> Path:
    lines = ["MORPH_CANARY_BEGIN", "MORPH_CANARY_READY"]
    if include_events:
        for index, event in enumerate(canary.EXPECTED_EVENTS):
            lines.append(
                f"MORPH_CANARY_EVENT event={event} identityEqual=1 "
                f"rawStateU32=0x{state_seed + index + 1:08x}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return path


class Pe32AndRenderingTests(unittest.TestCase):
    def test_render_uses_rvas_and_private_relocation_free_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            exe = build_pe32_fixture(Path(temp) / "BEA.exe")
            rendered = render_fixture(exe)

        self.assertIn("BEA+0x000081c0", rendered.text)
        self.assertIn("BEA+0x0000a580", rendered.text)
        self.assertNotIn("0x004081c0", rendered.text)
        self.assertEqual(8, rendered.fingerprint_size)
        self.assertTrue(all(not target.relocation_overlap for target in rendered.targets))
        self.assertNotIn(rendered.targets[0].sha256, rendered.text)
        self.assertNotRegex(rendered.text, r"(?i)\b(?:pid|hwnd|0x004081c0)\b")
        hardware_slots = re.findall(
            r"(?<!\S)ba(\d+) e1(?: /1)? BEA\+0x[0-9a-f]{8}", rendered.text
        )
        self.assertEqual(["0", "1", "2", "3"], hardware_slots)
        self.assertEqual(3, rendered.text.count(" e1 /1 "))
        self.assertIn('ba0 e1 /1 BEA+0x0000a580 ".printf', rendered.text)
        self.assertIn("bd 0", rendered.text)
        self.assertIn("bd 1", rendered.text)
        self.assertIn("bd 2", rendered.text)
        self.assertIn('ba3 e1 BEA+0x000d3110 ".if', rendered.text)
        self.assertNotIn("ba3 e1 /1", rendered.text)
        self.assertNotRegex(rendered.text, r"(?<![A-Za-z0-9_$])bp\d*\s")
        self.assertEqual(1, rendered.text.count("bc 3"))
        self.assertIn("bc 3; r @$t3=poi(@ecx+0x1c)", rendered.text)
        self.assertIn("be 0 1 2", rendered.text)
        self.assertNotIn("$bpnum", rendered.text)
        self.assertEqual(4, rendered.text.count("poi(@$t3+0x260)"))
        self.assertNotIn("poi(@ecx+0x260)", rendered.text)
        self.assertIn("poi(@esp+0x4)==0x21", rendered.text)
        self.assertIn("@ecx==poi(BEA+0x004a9d3c)", rendered.text)
        self.assertIn("r @$t3=poi(@ecx+0x1c)", rendered.text)
        self.assertGreaterEqual(rendered.text.count("@ecx==@$t3"), 2)
        self.assertIn("poi(@ecx+0x18)==@$t3", rendered.text)
        self.assertRegex(rendered.text, r"by\(BEA\+0x000081c0\)==0x[0-9a-f]{2}")
        self.assertEqual(
            hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(), canary.TEMPLATE_SHA256
        )
        self.assertEqual(rendered.text.count("{"), rendered.text.count("}"))
        self.assertEqual(0, rendered.text.count('\\"') % 2)

    def test_rejects_invalid_pe_headers_and_non_pe32_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bad_dos = root / "bad-dos.exe"
            bad_dos.write_bytes(b"not a PE")
            with self.assertRaisesRegex(ValueError, "DOS"):
                render_fixture(bad_dos)

            bad_pe = build_pe32_fixture(root / "bad-pe.exe")
            payload = bytearray(bad_pe.read_bytes())
            payload[0x80:0x84] = b"NOPE"
            bad_pe.write_bytes(payload)
            with self.assertRaisesRegex(ValueError, "PE signature"):
                render_fixture(bad_pe)

            pe32_plus = build_pe32_fixture(root / "pe32-plus.exe", optional_magic=0x020B)
            with self.assertRaisesRegex(ValueError, "PE32"):
                render_fixture(pe32_plus)

    def test_rejects_unmapped_nonexecutable_truncated_and_relocated_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            unmapped = build_pe32_fixture(root / "unmapped.exe")
            outside = dict(canary.PROBE_RVAS)
            outside["jetPartMove"] = 0x000F1000
            with mock.patch.object(canary, "PROBE_RVAS", outside), self.assertRaisesRegex(
                ValueError, "executable section"
            ):
                render_fixture(unmapped)

            nonexec = build_pe32_fixture(root / "nonexec.exe", executable=False)
            with self.assertRaisesRegex(ValueError, "executable section"):
                render_fixture(nonexec)

            truncated = build_pe32_fixture(
                root / "truncated.exe", relocation_rvas=(), truncate_at=0xD2514
            )
            with self.assertRaisesRegex(ValueError, "truncated file data"):
                render_fixture(truncated)

            relocated = build_pe32_fixture(root / "relocated.exe", relocation_rvas=(0x81C4,))
            with self.assertRaisesRegex(ValueError, "relocation"):
                render_fixture(relocated)

    def test_rejects_wrong_specimen_size_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            exe = build_pe32_fixture(Path(temp) / "BEA.exe")
            with self.assertRaisesRegex(ValueError, "size"):
                canary.render_private_command(exe, TEMPLATE)
            payload = exe.read_bytes()
            with mock.patch.object(canary, "CANONICAL_SIZE", len(payload)), mock.patch.object(
                canary, "CANONICAL_SHA256", "0" * 64
            ):
                with self.assertRaisesRegex(ValueError, "SHA-256"):
                    canary.render_private_command(exe, TEMPLATE)

    def test_rejects_template_and_generated_command_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            exe = build_pe32_fixture(root / "BEA.exe")
            drifted_template = root / "drifted.cdb.tmpl"
            drifted_template.write_text(TEMPLATE.read_text(encoding="ascii") + ".echo DRIFT\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "template"):
                render_fixture(exe, drifted_template)

            rendered = render_fixture(exe)
            command = root / "generated.cdb"
            command.write_bytes(rendered.text.encode("ascii"))
            payload = exe.read_bytes()
            with mock.patch.object(canary, "CANONICAL_SIZE", len(payload)), mock.patch.object(
                canary, "CANONICAL_SHA256", hashlib.sha256(payload).hexdigest()
            ):
                self.assertEqual(rendered, canary.validate_private_command(command, exe, TEMPLATE))
                command.write_bytes((rendered.text + ".echo DRIFT\n").encode("ascii"))
                with self.assertRaisesRegex(ValueError, "generated command"):
                    canary.validate_private_command(command, exe, TEMPLATE)


class MaterializerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.exe = build_pe32_fixture(self.root / "BEA.exe")
        payload = self.exe.read_bytes()
        self.canonical_patches = (
            mock.patch.object(canary, "CANONICAL_SIZE", len(payload)),
            mock.patch.object(canary, "CANONICAL_SHA256", hashlib.sha256(payload).hexdigest()),
        )
        for patcher in self.canonical_patches:
            patcher.start()
        self.rendered = canary.render_private_command(self.exe, TEMPLATE)

    def tearDown(self) -> None:
        for patcher in reversed(self.canonical_patches):
            patcher.stop()
        self.temp.cleanup()

    def test_materializes_strict_run_without_private_values(self) -> None:
        artifact = private_artifact(self.rendered, self.exe, self.root / "live.json")
        log = event_log(self.root / "cdb.log")
        result = canary.materialize_run(artifact, log, "positiveTransform")

        self.assertEqual("positiveTransform", result["role"])
        self.assertEqual(list(canary.EXPECTED_EVENTS), [event["event"] for event in result["events"]])
        self.assertEqual("0x00000001", result["events"][0]["rawStateU32"])
        self.assertEqual(hashlib.sha256(log.read_bytes()).hexdigest(), result["rawCaptureSha256"])
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(str(artifact), serialized)
        self.assertNotIn("MORPH_CANARY_EVENT", serialized)

    def test_rejects_private_artifact_and_log_drift(self) -> None:
        artifact = private_artifact(self.rendered, self.exe, self.root / "live.json")
        log = event_log(self.root / "cdb.log")
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        payload["pid"] = 1234
        artifact.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "keys"):
            canary.materialize_run(artifact, log, "positiveTransform")

        artifact = private_artifact(self.rendered, self.exe, self.root / "live.json")
        log.write_text(
            "MORPH_CANARY_BEGIN\nMORPH_CANARY_READY\n"
            "MORPH_CANARY_EVENT event=unknown identityEqual=1 rawStateU32=0x00000001\n",
            encoding="ascii",
        )
        with self.assertRaisesRegex(ValueError, "event"):
            canary.materialize_run(artifact, log, "positiveTransform")

        payload = json.loads(artifact.read_text(encoding="utf-8"))
        payload["templateSha256"] = "0" * 64
        artifact.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "template"):
            canary.materialize_run(artifact, event_log(log), "positiveTransform")

        artifact = private_artifact(self.rendered, self.exe, self.root / "live.json")
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        payload["fingerprints"][0]["sha256"] = "0" * 64
        artifact.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            canary.materialize_run(artifact, event_log(log), "positiveTransform")

        artifact = private_artifact(self.rendered, self.exe, self.root / "live.json")
        with self.assertRaisesRegex(ValueError, "positive"):
            canary.materialize_run(
                artifact, event_log(log, include_events=False), "positiveTransform"
            )

        pre_ready = self.root / "pre-ready.log"
        pre_ready.write_text(
            "MORPH_CANARY_BEGIN\n"
            "MORPH_CANARY_EVENT event=playerTransformAction identityEqual=1 rawStateU32=0x00000001\n"
            "MORPH_CANARY_READY\n",
            encoding="ascii",
        )
        with self.assertRaisesRegex(ValueError, "before.*READY"):
            canary.materialize_run(artifact, pre_ready, "noInputControl")

    def test_rejects_inconsistent_gate_markers(self) -> None:
        artifact = private_artifact(self.rendered, self.exe, self.root / "gate-live.json")
        reversed_markers = self.root / "reversed-markers.log"
        reversed_markers.write_text(
            "MORPH_CANARY_READY\nMORPH_CANARY_BEGIN\n",
            encoding="ascii",
        )
        with self.assertRaisesRegex(ValueError, "BEGIN.*before.*READY"):
            canary.materialize_run(artifact, reversed_markers, "noInputControl")

        contradictory = self.root / "contradictory-gate.log"
        contradictory.write_text(
            "MORPH_CANARY_BEGIN\n"
            "MORPH_CANARY_CODE_MISMATCH\n"
            "MORPH_CANARY_READY\n",
            encoding="ascii",
        )
        with self.assertRaisesRegex(ValueError, "CODE_MISMATCH"):
            canary.materialize_run(artifact, contradictory, "noInputControl")

        echoed_command = self.root / "echoed-command.log"
        echoed_command.write_text(
            "0:000> .if (fingerprints) { .echo MORPH_CANARY_READY; g } "
            ".else { .echo MORPH_CANARY_CODE_MISMATCH; qd }\n"
            "MORPH_CANARY_BEGIN\n"
            "MORPH_CANARY_READY\n",
            encoding="ascii",
        )
        try:
            control = canary.materialize_run(artifact, echoed_command, "noInputControl")
        except ValueError as exc:
            self.fail(f"echoed mismatch command must not fail the control: {exc}")
        self.assertEqual("noInputControl", control["role"])
        self.assertEqual([], control["events"])

    def test_matrix_enforces_roles_outcomes_and_exact_public_keys(self) -> None:
        runs = []
        for index, role in enumerate(canary.RUN_ROLES):
            artifact = private_artifact(self.rendered, self.exe, self.root / f"live-{index}.json")
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["receiptSha256"] = f"{index + 1:x}" * 64
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            log = event_log(
                self.root / f"cdb-{index}.log",
                include_events=role != "noInputControl",
                state_seed=index * 10,
            )
            runs.append(canary.materialize_run(artifact, log, role))

        matrix = canary.materialize_matrix(runs)
        canary.validate_public_matrix(matrix)
        self.assertEqual(canary.PUBLIC_SCHEMA, matrix["schema"])
        self.assertEqual(list(canary.RUN_ROLES), [run["role"] for run in matrix["runs"]])

        leaked = copy.deepcopy(matrix)
        leaked["runs"][0]["codeBytes"] = "90cc"
        with self.assertRaisesRegex(ValueError, "keys"):
            canary.validate_public_matrix(leaked)

        bad_control = copy.deepcopy(matrix)
        bad_control["runs"][0]["events"] = copy.deepcopy(matrix["runs"][1]["events"])
        bad_control["runs"][0]["eventCounts"] = copy.deepcopy(matrix["runs"][1]["eventCounts"])
        with self.assertRaisesRegex(ValueError, "control"):
            canary.validate_public_matrix(bad_control)

        bad_positive = copy.deepcopy(matrix)
        bad_positive["runs"][1]["events"][1]["identityEqual"] = False
        with self.assertRaisesRegex(ValueError, "identity"):
            canary.validate_public_matrix(bad_positive)

        reordered = copy.deepcopy(matrix)
        reordered["runs"][1]["events"][1:3] = reversed(reordered["runs"][1]["events"][1:3])
        with self.assertRaisesRegex(ValueError, "ordinal|order"):
            canary.validate_public_matrix(reordered)

        duplicate_receipt = copy.deepcopy(matrix)
        duplicate_receipt["runs"][2]["receiptSha256"] = duplicate_receipt["runs"][1]["receiptSha256"]
        with self.assertRaisesRegex(ValueError, "distinct"):
            canary.validate_public_matrix(duplicate_receipt)

        failed_cleanup = copy.deepcopy(matrix)
        failed_cleanup["runs"][2]["cleanup"]["cdbDetached"] = False
        with self.assertRaisesRegex(ValueError, "cleanup"):
            canary.validate_public_matrix(failed_cleanup)

        drifted_template = copy.deepcopy(matrix)
        drifted_template["runs"][2]["templateSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "template"):
            canary.validate_public_matrix(drifted_template)

        inconsistent_fingerprint = copy.deepcopy(matrix)
        inconsistent_fingerprint["runs"][2]["fingerprints"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            canary.validate_public_matrix(inconsistent_fingerprint)

        replayed_capture = copy.deepcopy(matrix)
        replayed_capture["runs"][2]["rawCaptureSha256"] = replayed_capture["runs"][1]["rawCaptureSha256"]
        with self.assertRaisesRegex(ValueError, "capture"):
            canary.validate_public_matrix(replayed_capture)

    def test_public_validator_rejects_nested_raw_bytes_and_pointer_comparisons(self) -> None:
        runs = []
        for index, role in enumerate(canary.RUN_ROLES):
            artifact = private_artifact(
                self.rendered, self.exe, self.root / f"artifact-{index}.json"
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["receiptSha256"] = str(index + 1) * 64
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            log = event_log(
                self.root / f"raw-{index}.log",
                include_events=role != "noInputControl",
                state_seed=index * 10,
            )
            runs.append(canary.materialize_run(artifact, log, role))
        matrix = canary.materialize_matrix(runs)

        for key, value in (
            ("path", "C:/private/BEA.exe"),
            ("moduleBase", "0x76000000"),
            ("pointer", "0x12345678"),
            ("crossRunPointerEqual", True),
            ("screenshot", "capture.png"),
        ):
            leaked = copy.deepcopy(matrix)
            leaked["runs"][1]["events"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "keys"):
                canary.validate_public_matrix(leaked)


if __name__ == "__main__":
    unittest.main(verbosity=2)
