#!/usr/bin/env python3
"""Generated-fixture tests for the bounded AYA observation producer."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import stat
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

import aya_archive_inventory as inventory


def _chunk(tag: bytes, payload: bytes = b"") -> bytes:
    if len(tag) != 4:
        raise ValueError("fixture tags are exactly four bytes")
    return tag + struct.pack("<I", len(payload)) + payload


def _compressed_member(raw: bytes) -> bytes:
    compressed = zlib.compress(raw)
    return struct.pack("<I", len(compressed)) + compressed


def _archive(*members: bytes) -> bytes:
    return b"".join(_compressed_member(member) for member in members)


def _mesh_payload(*bodies: bytes) -> bytes:
    payload = bytearray(b"prefix")
    for index, body in enumerate(bodies):
        payload.extend(b"CMSH")
        payload.extend(body)
        if index + 1 < len(bodies):
            payload.extend(b"PMSH")
            payload.extend(struct.pack("<I", 4))
            payload.extend(b"PMS2")
    return bytes(payload)


class AyaArchiveInventoryObservationTests(unittest.TestCase):
    maxDiff = None

    def _api(self, name: str):
        value = getattr(inventory, name, None)
        self.assertIsNotNone(value, f"missing Sequence 1A API: {name}")
        return value

    def _error_type(self):
        return self._api("ArchiveObservationError")

    def _assert_category(self, category: str, callback) -> None:
        with self.assertRaises(self._error_type()) as caught:
            callback()
        self.assertEqual(category, caught.exception.category)

    def _observe(self, paths: list[Path]) -> dict[str, object]:
        return self._api("observe_archives")(paths)

    def _render(self, report: dict[str, object]) -> bytes:
        return self._api("render_observation_records")(report)

    def _body_candidates(self, chunk: dict[str, object]) -> list[dict[str, object]]:
        self.assertIn("bodyCandidateObservations", chunk)
        self.assertNotIn("bodyObservations", chunk)
        return chunk["bodyCandidateObservations"]

    def test_contract_surface_and_closed_rejection_categories(self) -> None:
        for name in (
            "read_held_archive",
            "inflate_aya_bytes",
            "observe_archives",
            "render_observation_records",
        ):
            self.assertTrue(callable(self._api(name)))
        categories = self._api("REJECTION_CATEGORIES")
        self.assertIsInstance(categories, frozenset)
        self.assertEqual(
            {
                "aggregate_body_limit",
                "body_count_limit",
                "body_framing",
                "body_length_limit",
                "changed_held_input",
                "chunk_count_limit",
                "chunk_length_limit",
                "chunk_overrun",
                "compressed_limit",
                "empty_archive",
                "hardlink_input",
                "incomplete_zlib_member",
                "inflate_limit",
                "internal_error",
                "invalid_member_length",
                "member_count_limit",
                "member_length_limit",
                "member_overrun",
                "not_regular_input",
                "reparse_input",
                "trailing_zlib_data",
                "truncated_chunk_header",
                "truncated_member_header",
                "unavailable_input",
                "zlib_member",
            },
            categories,
        )
        with self.assertRaises(ValueError):
            self._error_type()("not-a-closed-category")

    def test_deterministic_path_free_records_keep_duplicate_sources_distinct(self) -> None:
        fixture = _archive(_chunk(b"AYAD", b"same"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "private-alpha.aya"
            second = root / "private-beta.aya"
            first.write_bytes(fixture)
            second.write_bytes(fixture)

            forward = self._render(self._observe([second, first]))
            reverse = self._render(self._observe([first, second]))
            self.assertEqual(forward, reverse)
            self.assertTrue(forward.endswith(b"\n"))
            decoded = json.loads(forward)
            self.assertEqual("onslaught.aya-archive-observation.v1", decoded["schemaVersion"])
            self.assertEqual(
                {
                    "name": "aya_archive_inventory",
                    "profileVersion": "bounded-observation-v1",
                    "producerVersion": 1,
                },
                decoded["producer"],
            )
            records = decoded["archiveRecords"]
            self.assertEqual(["archive-0001", "archive-0002"], [item["archiveOrdinal"] for item in records])
            self.assertEqual(records[0]["sourceIdentity"], records[1]["sourceIdentity"])
            self.assertNotEqual(records[0]["archiveOrdinal"], records[1]["archiveOrdinal"])
            rendered = forward.decode("utf-8")
            self.assertNotIn(str(root), rendered)
            self.assertNotIn("private-alpha", rendered)
            self.assertNotIn("private-beta", rendered)

    def test_unequal_content_order_is_independent_of_private_names_and_locations(self) -> None:
        first_fixture = _archive(_chunk(b"AYAD", b"first-public-content"))
        second_fixture = _archive(_chunk(b"TARG", b"second-public-content"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_location = root / "first-private-location"
            second_location = root / "second-private-location"
            first_location.mkdir()
            second_location.mkdir()

            first_alpha = first_location / "alpha-private-name.aya"
            first_zulu = first_location / "zulu-private-name.aya"
            second_alpha = second_location / "alpha-renamed.aya"
            second_zulu = second_location / "zulu-renamed.aya"
            first_alpha.write_bytes(first_fixture)
            first_zulu.write_bytes(second_fixture)
            second_alpha.write_bytes(second_fixture)
            second_zulu.write_bytes(first_fixture)

            original = self._render(self._observe([first_zulu, first_alpha]))
            relocated = self._render(self._observe([second_zulu, second_alpha]))

        self.assertEqual(original, relocated)
        original_report = json.loads(original)
        relocated_report = json.loads(relocated)
        self.assertEqual(original_report["sourceUniverseId"], relocated_report["sourceUniverseId"])
        self.assertEqual(
            ["archive-0001", "archive-0002"],
            [record["archiveOrdinal"] for record in original_report["archiveRecords"]],
        )

    def test_multipart_cardinality_and_unknown_tag_bytes_are_preserved(self) -> None:
        raw_one = _chunk(b"AYAD", b"one")
        raw_two = _chunk(b"\x00A\xffZ", b"two")
        fixture = _archive(raw_one, raw_two)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "input.AYA"
            source.write_bytes(fixture)
            record = self._observe([source])["archiveRecords"][0]
        self.assertEqual("observed", record["observationStatus"])
        self.assertIsNone(record["rejectionCategory"])
        self.assertEqual(".aya", record["extension"])
        self.assertEqual(2, record["memberCount"])
        chunks = record["chunkObservations"]
        self.assertEqual(["chunk-0001", "chunk-0002"], [item["chunkOrdinal"] for item in chunks])
        self.assertEqual("AYAD", chunks[0]["tagAscii"])
        self.assertEqual("41594144", chunks[0]["tagHex"])
        self.assertEqual(".A.Z", chunks[1]["tagAscii"])
        self.assertEqual("0041ff5a", chunks[1]["tagHex"])

    def test_mesh_body_candidates_are_explicitly_candidate_only_and_one_to_one(self) -> None:
        fixture = _archive(_chunk(b"MESH", _mesh_payload(b"first", b"second")))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "mesh.aya"
            source.write_bytes(fixture)
            record = self._observe([source])["archiveRecords"][0]
        candidates = self._body_candidates(record["chunkObservations"][0])
        self.assertEqual(
            ["body-candidate-0001", "body-candidate-0002"],
            [item["candidateOrdinal"] for item in candidates],
        )
        self.assertTrue(all(item["tagAscii"] == "CMSH" for item in candidates))
        self.assertTrue(all(item["tagHex"] == "434d5348" for item in candidates))
        self.assertTrue(all(item["evidenceKind"] == "candidate-only" for item in candidates))
        self.assertTrue(
            all(
                item["boundaryRule"] == "cmsh-to-next-pmsh-pms2-or-mesh-end"
                for item in candidates
            )
        )
        self.assertTrue(
            all(
                set(item)
                == {
                    "boundaryRule",
                    "candidateOrdinal",
                    "evidenceKind",
                    "length",
                    "sha256",
                    "tagAscii",
                    "tagHex",
                }
                for item in candidates
            )
        )

    def test_repeated_body_marker_without_wrapper_is_rejected_as_ambiguous(self) -> None:
        self._assert_category(
            "body_framing",
            lambda: self._api("observe_embedded_bodies")(b"CMSHoneCMSHtwo"),
        )

    def test_rejected_record_is_terminal_closed_and_redacts_private_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "do-not-leak-this-name.aya"
            source.write_bytes(struct.pack("<I", 12) + b"short")
            rendered = self._render(self._observe([source]))
        record = json.loads(rendered)["archiveRecords"][0]
        self.assertEqual("rejected", record["observationStatus"])
        self.assertEqual("member_overrun", record["rejectionCategory"])
        self.assertEqual([], record["chunkObservations"])
        self.assertNotIn("do-not-leak", rendered.decode("utf-8"))
        self.assertNotIn(str(root), rendered.decode("utf-8"))

    def test_read_held_archive_accepts_regular_single_link_and_rejects_hardlink(self) -> None:
        fixture = _archive(_chunk(b"AYAD"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.aya"
            alias = root / "alias.aya"
            source.write_bytes(fixture)
            self.assertEqual(fixture, self._api("read_held_archive")(source))
            os.link(source, alias)
            self._assert_category("hardlink_input", lambda: self._api("read_held_archive")(alias))

    def test_read_held_archive_rejects_reparse_and_same_handle_change(self) -> None:
        fixture = _archive(_chunk(b"AYAD"))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.aya"
            source.write_bytes(fixture)
            with mock.patch.object(inventory, "_path_has_reparse", return_value=True):
                self._assert_category("reparse_input", lambda: self._api("read_held_archive")(source))

            real_fstat = os.fstat
            calls = 0

            def changed_fstat(descriptor: int):
                nonlocal calls
                calls += 1
                metadata = real_fstat(descriptor)
                if calls == 2:
                    values = list(metadata)
                    values[6] += 1
                    return os.stat_result(values)
                return metadata

            with mock.patch.object(inventory.os, "fstat", side_effect=changed_fstat):
                self._assert_category("changed_held_input", lambda: self._api("read_held_archive")(source))

    def test_read_held_archive_rechecks_reparse_components_after_read(self) -> None:
        fixture = _archive(_chunk(b"AYAD"))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.aya"
            source.write_bytes(fixture)
            with mock.patch.object(inventory, "_path_has_reparse", side_effect=[False, True]):
                self._assert_category("reparse_input", lambda: self._api("read_held_archive")(source))

    def test_read_held_archive_rejects_post_close_path_identity_change(self) -> None:
        fixture = _archive(_chunk(b"AYAD"))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.aya"
            source.write_bytes(fixture)
            real_lstat = os.lstat
            source_calls = 0

            def changed_lstat(path):
                nonlocal source_calls
                metadata = real_lstat(path)
                if os.path.normcase(os.fspath(path)) == os.path.normcase(os.fspath(source)):
                    source_calls += 1
                    if source_calls >= 3:
                        values = list(metadata)
                        values[6] += 1
                        return os.stat_result(values)
                return metadata

            with mock.patch.object(inventory.os, "lstat", side_effect=changed_lstat):
                self._assert_category("changed_held_input", lambda: self._api("read_held_archive")(source))

    def test_compressed_bytes_cap_accepts_cap_and_rejects_cap_plus_one(self) -> None:
        fixture = _archive(_chunk(b"AYAD", b"payload"))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.aya"
            source.write_bytes(fixture)
            with mock.patch.object(inventory, "MAX_COMPRESSED_BYTES", len(fixture), create=True):
                self.assertEqual(fixture, self._api("read_held_archive")(source))
            with mock.patch.object(inventory, "MAX_COMPRESSED_BYTES", len(fixture) - 1, create=True):
                self._assert_category("compressed_limit", lambda: self._api("read_held_archive")(source))

    def test_member_count_and_member_length_caps_are_independent(self) -> None:
        raw = _chunk(b"AYAD")
        one = _compressed_member(raw)
        two = one + one
        three = two + one
        compressed_length = struct.unpack_from("<I", one, 0)[0]
        with mock.patch.object(inventory, "MAX_MEMBERS", 2, create=True):
            self.assertEqual(raw + raw, self._api("inflate_aya_bytes")(two))
            self._assert_category("member_count_limit", lambda: self._api("inflate_aya_bytes")(three))
        with mock.patch.object(inventory, "MAX_MEMBER_COMPRESSED_BYTES", compressed_length, create=True):
            self.assertEqual(raw, self._api("inflate_aya_bytes")(one))
        with mock.patch.object(inventory, "MAX_MEMBER_COMPRESSED_BYTES", compressed_length - 1, create=True):
            self._assert_category("member_length_limit", lambda: self._api("inflate_aya_bytes")(one))

    def test_inflated_bytes_cap_accepts_cap_and_rejects_cap_plus_one(self) -> None:
        raw = _chunk(b"AYAD", b"bounded")
        fixture = _archive(raw)
        with mock.patch.object(inventory, "MAX_INFLATED_BYTES", len(raw), create=True):
            self.assertEqual(raw, self._api("inflate_aya_bytes")(fixture))
        with mock.patch.object(inventory, "MAX_INFLATED_BYTES", len(raw) - 1, create=True):
            self._assert_category("inflate_limit", lambda: self._api("inflate_aya_bytes")(fixture))

    def test_member_framing_and_decompressor_states_fail_closed(self) -> None:
        raw = _chunk(b"AYAD", b"payload")
        compressed = zlib.compress(raw)
        cases = {
            "empty_archive": b"",
            "truncated_member_header": b"\x01\x02\x03",
            "invalid_member_length": struct.pack("<I", 0),
            "member_overrun": struct.pack("<I", len(compressed) + 1) + compressed,
            "zlib_member": struct.pack("<I", 4) + b"nope",
            "incomplete_zlib_member": struct.pack("<I", len(compressed) - 2) + compressed[:-2],
            "trailing_zlib_data": struct.pack("<I", len(compressed) + 1) + compressed + b"x",
        }
        for category, fixture in cases.items():
            with self.subTest(category=category):
                self._assert_category(category, lambda fixture=fixture: self._api("inflate_aya_bytes")(fixture))

    def test_top_level_chunk_count_cap_accepts_cap_and_rejects_cap_plus_one(self) -> None:
        one = _chunk(b"AYAD")
        two = one + _chunk(b"TARG")
        with mock.patch.object(inventory, "MAX_TOP_LEVEL_CHUNKS", 1, create=True):
            self.assertEqual(1, len(self._api("parse_top_level_chunks_bounded")(one)))
            self._assert_category(
                "chunk_count_limit", lambda: self._api("parse_top_level_chunks_bounded")(two)
            )

    def test_per_chunk_length_cap_and_malformed_chunk_states(self) -> None:
        payload = b"12345"
        raw = _chunk(b"AYAD", payload)
        with mock.patch.object(inventory, "MAX_CHUNK_BYTES", len(payload), create=True):
            self.assertEqual(1, len(self._api("parse_top_level_chunks_bounded")(raw)))
        with mock.patch.object(inventory, "MAX_CHUNK_BYTES", len(payload) - 1, create=True):
            self._assert_category(
                "chunk_length_limit", lambda: self._api("parse_top_level_chunks_bounded")(raw)
            )
        self._assert_category(
            "truncated_chunk_header", lambda: self._api("parse_top_level_chunks_bounded")(b"AYAD\x00")
        )
        self._assert_category(
            "chunk_overrun",
            lambda: self._api("parse_top_level_chunks_bounded")(b"AYAD" + struct.pack("<I", 10) + b"x"),
        )

    def test_body_count_cap_accepts_cap_and_rejects_cap_plus_one(self) -> None:
        one = _mesh_payload(b"one")
        two = _mesh_payload(b"one", b"two")
        with mock.patch.object(inventory, "MAX_EMBEDDED_BODIES", 1, create=True):
            self.assertEqual(1, len(self._api("observe_embedded_bodies")(one)))
            self._assert_category("body_count_limit", lambda: self._api("observe_embedded_bodies")(two))

    def test_body_length_cap_accepts_cap_and_rejects_cap_plus_one(self) -> None:
        payload = _mesh_payload(b"12345")
        body_length = len(b"CMSH12345")
        with mock.patch.object(inventory, "MAX_BODY_BYTES", body_length, create=True):
            self.assertEqual(body_length, self._api("observe_embedded_bodies")(payload)[0]["length"])
        with mock.patch.object(inventory, "MAX_BODY_BYTES", body_length - 1, create=True):
            self._assert_category("body_length_limit", lambda: self._api("observe_embedded_bodies")(payload))

    def test_aggregate_body_cap_accepts_cap_and_rejects_cap_plus_one(self) -> None:
        payload = _mesh_payload(b"one", b"two")
        observed = self._api("observe_embedded_bodies")(payload)
        aggregate = sum(item["length"] for item in observed)
        with mock.patch.object(inventory, "MAX_AGGREGATE_BODY_BYTES", aggregate, create=True):
            self.assertEqual(2, len(self._api("observe_embedded_bodies")(payload)))
        with mock.patch.object(inventory, "MAX_AGGREGATE_BODY_BYTES", aggregate - 1, create=True):
            self._assert_category(
                "aggregate_body_limit", lambda: self._api("observe_embedded_bodies")(payload)
            )

    def test_internal_os_error_is_path_free_and_terminal(self) -> None:
        private = r"C:\private\retail\secret.aya"
        with mock.patch.object(inventory, "read_held_archive", side_effect=OSError(private)):
            report = self._observe([Path(private)])
        rendered = self._render(report).decode("utf-8")
        self.assertIn('"rejectionCategory":"internal_error"', rendered)
        self.assertNotIn("private", rendered.lower())
        self.assertNotIn("retail", rendered.lower())
        self.assertNotIn("secret", rendered.lower())

    def test_renderer_rejects_extra_fields_duplicate_ordinals_and_changed_universe(self) -> None:
        fixture = _archive(_chunk(b"AYAD"))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.aya"
            source.write_bytes(fixture)
            report = self._observe([source])

        injected = json.loads(json.dumps(report))
        injected["archiveRecords"][0]["machinePath"] = r"C:\private\source.aya"
        with self.assertRaises(ValueError):
            self._render(injected)

        duplicated = json.loads(json.dumps(report))
        duplicated["archiveRecords"].append(dict(duplicated["archiveRecords"][0]))
        with self.assertRaises(ValueError):
            self._render(duplicated)

        changed_universe = json.loads(json.dumps(report))
        changed_universe["sourceUniverseId"] = "0" * 64
        with self.assertRaises(ValueError):
            self._render(changed_universe)

    def test_renderer_rejects_reordered_unequal_records_with_recomputed_identity(self) -> None:
        first_fixture = _archive(_chunk(b"AYAD", b"first"))
        second_fixture = _archive(_chunk(b"TARG", b"second"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.aya"
            second = root / "second.aya"
            first.write_bytes(first_fixture)
            second.write_bytes(second_fixture)
            canonical = self._observe([first, second])

        canonical_bytes = self._render(canonical)
        reordered = json.loads(json.dumps(canonical))
        reordered["archiveRecords"].reverse()
        for ordinal, record in enumerate(reordered["archiveRecords"], 1):
            record["archiveOrdinal"] = f"archive-{ordinal:04d}"
        reordered["sourceUniverseId"] = inventory._source_universe_id(
            reordered["archiveRecords"]
        )

        with self.assertRaises(ValueError):
            self._render(reordered)
        self.assertEqual(canonical_bytes, self._render(canonical))

    def test_renderer_rejects_type_cap_arithmetic_tag_and_body_scope_mismatches(self) -> None:
        fixture = _archive(_chunk(b"MESH", _mesh_payload(b"body")))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.aya"
            source.write_bytes(fixture)
            report = self._observe([source])

        def changed(callback):
            candidate = json.loads(json.dumps(report))
            callback(candidate["archiveRecords"][0])
            candidate["sourceUniverseId"] = inventory._source_universe_id(candidate["archiveRecords"])
            return candidate

        cases = {
            "boolean source length": lambda record: record["sourceIdentity"].__setitem__("length", True),
            "source cap": lambda record: record["sourceIdentity"].__setitem__(
                "length", inventory.MAX_COMPRESSED_BYTES + 1
            ),
            "boolean inflated length": lambda record: record.__setitem__("inflatedLength", True),
            "inflated cap": lambda record: record.__setitem__(
                "inflatedLength", inventory.MAX_INFLATED_BYTES + 1
            ),
            "boolean member count": lambda record: record.__setitem__("memberCount", True),
            "inflated arithmetic": lambda record: record.__setitem__("inflatedLength", 0),
            "boolean chunk length": lambda record: record["chunkObservations"][0].__setitem__(
                "declaredLength", True
            ),
            "tag mismatch": lambda record: record["chunkObservations"][0].__setitem__(
                "tagAscii", "NOPE"
            ),
            "body candidate outside MESH": lambda record: (
                record["chunkObservations"][0].__setitem__("tagAscii", "AYAD"),
                record["chunkObservations"][0].__setitem__("tagHex", "41594144"),
            ),
            "body candidate shorter than CMSH marker": lambda record: self._body_candidates(
                record["chunkObservations"][0]
            )[0].__setitem__("length", 3),
            "body candidate aggregate exceeds MESH payload": lambda record: self._body_candidates(
                record["chunkObservations"][0]
            )[0].__setitem__(
                "length", record["chunkObservations"][0]["declaredLength"] + 1
            ),
            "body candidate evidence kind": lambda record: self._body_candidates(
                record["chunkObservations"][0]
            )[0].__setitem__("evidenceKind", "parsed"),
            "body candidate boundary rule": lambda record: self._body_candidates(
                record["chunkObservations"][0]
            )[0].__setitem__("boundaryRule", "unknown"),
        }
        for role, mutate in cases.items():
            with self.subTest(role=role), self.assertRaises(ValueError):
                self._render(changed(mutate))

        with mock.patch.object(inventory, "MAX_TOP_LEVEL_CHUNKS", 0), self.assertRaises(ValueError):
            self._render(report)
        with mock.patch.object(inventory, "MAX_EMBEDDED_BODIES", 0), self.assertRaises(ValueError):
            self._render(report)
        body_length = self._body_candidates(
            report["archiveRecords"][0]["chunkObservations"][0]
        )[0]["length"]
        with mock.patch.object(inventory, "MAX_AGGREGATE_BODY_BYTES", body_length - 1), self.assertRaises(ValueError):
            self._render(report)

    def test_unavailable_custom_suffix_is_reduced_to_closed_extension_token(self) -> None:
        private = Path(r"C:\private\name.private-client")
        with mock.patch.object(inventory, "read_held_archive", side_effect=OSError(str(private))):
            rendered = self._render(self._observe([private]))
        record = json.loads(rendered)["archiveRecords"][0]
        self.assertEqual("other", record["extension"])
        self.assertNotIn("private-client", rendered.decode("utf-8"))

    def test_legacy_summary_inflate_and_human_output_remain_compatible(self) -> None:
        raw = _chunk(b"AYAD", b"payload") + _chunk(b"TARG")
        fixture = _archive(raw)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "legacy.aya"
            source.write_bytes(fixture)
            self.assertEqual(raw, inventory.inflate_aya(source))
            summary, inflated, chunks = inventory.summarize_archive(source)
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                inventory.print_summary(summary)
        self.assertEqual(raw, inflated)
        self.assertEqual(2, len(chunks))
        self.assertEqual(str(source), summary.path)
        self.assertEqual(len(fixture), summary.compressed_size)
        self.assertEqual(hashlib.sha256(fixture).hexdigest(), summary.compressed_sha256)
        self.assertEqual({"AYAD": 1, "TARG": 1}, summary.tag_counts)
        self.assertIn(str(source), stream.getvalue())
        self.assertIn("AYAD:1", stream.getvalue())

    def test_cli_opt_in_writes_path_free_record_without_changing_normal_output(self) -> None:
        raw = _chunk(b"AYAD", b"payload")
        fixture = _archive(raw)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "private-source.aya"
            output = root / "records" / "observations.json"
            source.write_bytes(fixture)
            normal_stdout = io.StringIO()
            with contextlib.redirect_stdout(normal_stdout):
                result = inventory.main([str(source), "--observation-records-out", str(output)])
            rendered = output.read_text(encoding="utf-8")
        self.assertEqual(0, result)
        self.assertIn(str(source), normal_stdout.getvalue())
        self.assertNotIn("private-source", rendered)
        self.assertNotIn(str(root), rendered)
        self.assertEqual("observed", json.loads(rendered)["archiveRecords"][0]["observationStatus"])

    def test_legacy_dump_and_json_outputs_remain_available_without_opt_in(self) -> None:
        fixture = _archive(_chunk(b"TEXT", b"legacy-payload"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "legacy.aya"
            dump_root = root / "dump"
            manifest_path = root / "manifest" / "inventory.json"
            source.write_bytes(fixture)
            with contextlib.redirect_stdout(io.StringIO()):
                result = inventory.main(
                    [
                        str(source),
                        "--json-out",
                        str(manifest_path),
                        "--dump-dir",
                        str(dump_root),
                        "--dump-tag",
                        "TEXT",
                    ]
                )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            dumped_payloads = list(dump_root.rglob("*_payload.bin"))
            dumped_metadata = list(dump_root.rglob("*_payload.json"))
        self.assertEqual(0, result)
        self.assertEqual(str(source), manifest[0]["path"])
        self.assertEqual({"TEXT": 1}, manifest[0]["tag_counts"])
        self.assertEqual(1, len(dumped_payloads))
        self.assertEqual(1, len(dumped_metadata))


if __name__ == "__main__":
    unittest.main(verbosity=2)
