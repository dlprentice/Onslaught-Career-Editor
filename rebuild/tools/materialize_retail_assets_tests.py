#!/usr/bin/env python3
"""Focused regressions for the local retail-asset materializer."""

from __future__ import annotations

import struct
import tempfile
import unittest
import zlib
import json
import subprocess
from pathlib import Path
from unittest import mock

import materialize_retail_assets as materializer


def _chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind)
    crc = zlib.crc32(payload, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _png(
    width: int,
    height: int,
    *,
    idat: bytes | None = None,
    last_pixel: int = 0,
) -> bytes:
    signature = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    pixels = bytearray(b"".join(b"\0" + bytes(width * 3) for _ in range(height)))
    pixels[-1] = last_pixel
    return (
        signature
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(pixels) if idat is None else idat)
        + _chunk(b"IEND", b"")
    )


def _physics_definition_record(
    record_type: int,
    name: str,
    fields: tuple[tuple[int, bytes], ...],
) -> bytes:
    result = bytearray(struct.pack("<II", record_type, 0))
    result.extend(name.encode("ascii") + b"\0")
    for index, (field_id, value) in enumerate(fields):
        result.extend(struct.pack("<II", field_id, len(value)))
        result.extend(value)
        result.extend(struct.pack("<i", -1 if index + 1 == len(fields) else 0))
    return bytes(result)


def _world_initial_object(
    thing_type: int,
    *,
    position_bits: tuple[int, int, int] = (0, 0, 0),
    orientation_bits: tuple[int, int, int] = (0, 0, 0),
    mesh_number: int = 0,
    allegiance: int = 0,
    target: int = -1,
    script: str = "",
    name: str = "",
    spawn_script: str = "",
    active: int = 1,
    attach_scripts: int = 0,
    definition_name: str = "X",
    trailer: int = -1,
    plane_mode: int = 0,
    player_number: int = 1,
    amount: int = 1,
    mode: int = 0,
    delay_bits: int = 0,
    squad_delay_bits: int = 0,
    initial_delay_bits: int = 0,
    squad_size: int = 1,
    spawn_unit: str = "",
    spawner_spawn_script: str = "",
    radius_bits: int = 0x3F800000,
) -> bytes:
    result = bytearray(struct.pack("<i", thing_type))
    for bits in (*position_bits, *orientation_bits):
        result.extend(struct.pack("<I", bits))
    result.extend(struct.pack("<iii", mesh_number, allegiance, target))
    for value in (script, name, spawn_script):
        result.extend(value.encode("ascii") + b"\0")
    result.extend(struct.pack("<ii", active, attach_scripts))
    if thing_type == 8:
        encoded = definition_name.encode("ascii")
        result.extend(bytes((len(encoded),)) + encoded + struct.pack("<i", trailer))
    elif thing_type == 15:
        result.extend(struct.pack("<ii", plane_mode, player_number))
    elif thing_type in (18, 27):
        pass
    elif thing_type == 19:
        result.extend(struct.pack("<iIIIi", amount, delay_bits, squad_delay_bits,
                                  initial_delay_bits, squad_size))
        result.extend(spawn_unit.encode("ascii") + b"\0")
        result.extend(spawner_spawn_script.encode("ascii") + b"\0")
    elif thing_type == 28:
        result.extend(struct.pack("<ii", amount, mode))
        encoded = definition_name.encode("ascii")
        result.extend(bytes((len(encoded),)) + encoded + struct.pack("<i", trailer))
    elif thing_type == 36:
        result.extend(struct.pack("<I", radius_bits))
    return bytes(result)


def _world110_initial_object_fixture(
    *,
    header: tuple[int, int, int] = (2, 0, 40),
    start_plane_mode: int = 0,
    start_player_number: int = 1,
    start_position_bits: tuple[int, int, int] = (0x43846000, 0x43816800, 0x80000000),
    start_orientation_bits: tuple[int, int, int] = (0xBF04FD8B, 0, 0),
    extra_start: bool = False,
    unsupported_type: bool = False,
    tree_header: tuple[int, int] = (0, 2),
) -> tuple[materializer._WorldReader, tuple[materializer._WorldInitialObject, ...]]:
    payload = bytearray(15_709)
    payload.extend(struct.pack("<iiH", *header))
    payload.extend(_world_initial_object(27, script="LevelScript"))
    payload.extend(
        _world_initial_object(
            15,
            position_bits=start_position_bits,
            orientation_bits=start_orientation_bits,
            plane_mode=start_plane_mode,
            player_number=start_player_number,
        )
    )
    remaining_types = [8] * 10 + [18] * 19 + [19] + [27] * 2 + [28] * 5 + [36]
    if extra_start:
        remaining_types[0] = 15
    if unsupported_type:
        remaining_types[0] = 99
    for thing_type in remaining_types:
        payload.extend(_world_initial_object(thing_type))
    payload.extend(struct.pack("<Hi", *tree_header))
    reader = materializer._WorldReader(bytes(payload))
    reader.position = 15_709
    objects = materializer._parse_world_initial_objects(
        reader,
        110,
        materializer.WORLD110_INITIAL_OBJECT_HEADER,
        materializer.WORLD110_INITIAL_OBJECT_TYPE_COUNTS,
    )
    return reader, objects


class PhysicsDefinitionTests(unittest.TestCase):
    def test_ordered_stream_preserves_duplicate_records_and_fields(self) -> None:
        records = [
            _physics_definition_record(
                1,
                f"Synthetic Unit {index}",
                ((8, struct.pack("<I", 1)),),
            )
            for index in range(775)
        ]
        records.extend(
            (
                _physics_definition_record(
                    5,
                    "Duplicate Spawner",
                    ((1, b"First Unit\0"), (1, b"Second Unit\0")),
                ),
                _physics_definition_record(
                    5,
                    "Duplicate Spawner",
                    ((1, b"Third Unit\0"),),
                ),
            )
        )
        data = struct.pack("<H", 0x12) + b"".join(records) + struct.pack("<i", -1)

        stream = materializer._physics_record_stream(data)
        index = materializer._physics_records(data)

        self.assertEqual(777, len(stream))
        self.assertEqual(
            ((1, b"First Unit\0"), (1, b"Second Unit\0")),
            stream[-2].fields,
        )
        self.assertEqual(2, len(index[(5, "Duplicate Spawner")]))
        with self.assertRaisesRegex(RuntimeError, "expected one physics record"):
            materializer._physics_record(index, 5, "Duplicate Spawner")
        with self.assertRaisesRegex(RuntimeError, "expected one physics field"):
            materializer._PhysicsFields(stream[-2].fields)[1]

    def test_unit_behavior_serialized_types_map_to_released_selectors(self) -> None:
        expected = (
            0, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13,
            14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
        )

        self.assertEqual(
            expected,
            materializer.UNIT_BEHAVIOR_SELECTOR_BY_SERIALIZED_TYPE,
        )
        for serialized_type, selector in enumerate(expected, start=1):
            self.assertEqual(
                selector,
                materializer._unit_behavior_selector(
                    {8: struct.pack("<I", serialized_type)}
                ),
            )

    def test_unit_behavior_selector_rejects_unreleased_values(self) -> None:
        for value in (0, 26):
            with self.assertRaisesRegex(RuntimeError, "unsupported Unit behaviour"):
                materializer._unit_behavior_selector({8: struct.pack("<I", value)})
        with self.assertRaisesRegex(RuntimeError, "not one dword"):
            materializer._unit_behavior_selector({8: b"\x01"})


class WorkRootRoutingTests(unittest.TestCase):
    @staticmethod
    def _canonical_lab(parent: Path) -> tuple[Path, Path]:
        repository = parent / "canonical"
        repository.mkdir()
        lab = repository / "local-lab"
        lab.mkdir()
        return repository, lab

    def test_canonical_root_is_derived_from_the_common_git_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "canonical"
            common = repository / ".git"
            common.mkdir(parents=True)
            result = mock.Mock(stdout=f"{common}\n")

            with mock.patch.object(
                materializer.subprocess,
                "run",
                return_value=result,
            ) as run:
                self.assertEqual(
                    repository.resolve(),
                    materializer._canonical_repository_root(),
                )

            run.assert_called_once_with(
                (
                    "git",
                    "-C",
                    str(materializer.ROOT),
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-common-dir",
                ),
                check=True,
                capture_output=True,
                text=True,
                env={
                    key: value
                    for key, value in materializer.os.environ.items()
                    if not key.startswith("GIT_")
                },
            )

    def test_canonical_root_ignores_ambient_git_routing_variables(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            canonical = parent / "canonical"
            foreign = parent / "foreign"
            for repository in (canonical, foreign):
                subprocess.run(
                    ("git", "init", "--quiet", str(repository)),
                    check=True,
                    capture_output=True,
                    text=True,
                )

            hostile = {
                "GIT_DIR": str(foreign / ".git"),
                "GIT_WORK_TREE": str(foreign),
                "GIT_COMMON_DIR": str(foreign / ".git"),
                "GIT_INDEX_FILE": str(foreign / ".git" / "index"),
            }
            with (
                mock.patch.object(materializer, "ROOT", canonical),
                mock.patch.dict(materializer.os.environ, hostile),
            ):
                self.assertEqual(
                    canonical.resolve(),
                    materializer._canonical_repository_root(),
                )

    def test_canonical_lab_root_owns_the_temporary_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            repository, lab = self._canonical_lab(parent)
            game_root = parent / "retail"
            game_root.mkdir()
            work_root = lab / "materializer-work"
            observed_stage_parents: list[Path] = []

            def materialize(
                _game_root: Path, stage: Path
            ) -> tuple[tuple[Path, str], ...]:
                observed_stage_parents.append(stage.parent)
                return ()

            with (
                mock.patch.object(
                    materializer.sys,
                    "argv",
                    [
                        "materialize_retail_assets.py",
                        "--force",
                        "--game-root",
                        str(game_root),
                        "--work-root",
                        str(work_root),
                    ],
                ),
                mock.patch.object(
                    materializer, "_resolve_game_root", return_value=game_root
                ),
                mock.patch.object(
                    materializer,
                    "_canonical_repository_root",
                    return_value=repository,
                ),
                mock.patch.object(
                    materializer, "_materialize", side_effect=materialize
                ),
                mock.patch.object(materializer, "_publish"),
                mock.patch.object(materializer, "_outputs_ready", return_value=True),
                mock.patch.object(materializer, "_all_outputs", return_value=()),
                mock.patch("builtins.print"),
            ):
                self.assertEqual(0, materializer.main())

            self.assertEqual([work_root.resolve()], observed_stage_parents)
            self.assertTrue(work_root.is_dir())

    def test_non_windows_requires_an_explicit_root(self) -> None:
        with mock.patch.object(materializer.os, "name", "posix"):
            with self.assertRaisesRegex(RuntimeError, "requires an explicit"):
                materializer._resolve_work_root(None)

    def test_windows_default_remains_the_historical_path(self) -> None:
        with mock.patch.object(materializer.os, "name", "nt"):
            self.assertEqual(
                materializer.WINDOWS_DEFAULT_WORK_ROOT,
                materializer._resolve_work_root(None),
            )

    def test_plain_canonical_lab_descendants_are_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository, lab = self._canonical_lab(Path(temporary))
            existing = lab / "existing"
            existing.mkdir()
            nested_parent = lab / "nested"
            nested_parent.mkdir()

            with mock.patch.object(
                materializer,
                "_canonical_repository_root",
                return_value=repository,
            ):
                self.assertEqual(
                    existing.resolve(),
                    materializer._resolve_work_root(existing),
                )
                self.assertEqual(
                    nested_parent / "new-work-root",
                    materializer._resolve_work_root(
                        nested_parent / "new-work-root"
                    ),
                )

    def test_repository_external_and_escape_spellings_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            repository, lab = self._canonical_lab(parent)
            arbitrary_repository_path = repository / "rebuild"
            arbitrary_repository_path.mkdir()
            external = parent / "external"
            external.mkdir()

            with mock.patch.object(
                materializer,
                "_canonical_repository_root",
                return_value=repository,
            ):
                for rejected in (
                    repository,
                    arbitrary_repository_path,
                    repository / "local-lab-sibling" / "work",
                    materializer.ROOT / "local-lab" / "work",
                ):
                    with self.subTest(rejected=rejected):
                        with self.assertRaisesRegex(RuntimeError, "repository"):
                            materializer._resolve_work_root(rejected)

                with self.assertRaisesRegex(RuntimeError, "descendant"):
                    materializer._resolve_work_root(lab)
                with self.assertRaisesRegex(RuntimeError, "exact.*local-lab"):
                    materializer._resolve_work_root(external / "work")

    def test_relative_parent_traversal_and_missing_ancestors_are_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "absolute"):
            materializer._resolve_work_root(Path("relative-work"))
        with tempfile.TemporaryDirectory() as temporary:
            repository, lab = self._canonical_lab(Path(temporary))
            with mock.patch.object(
                materializer,
                "_canonical_repository_root",
                return_value=repository,
            ):
                with self.assertRaisesRegex(RuntimeError, "parent traversal"):
                    materializer._resolve_work_root(lab / ".." / "escape")
                with self.assertRaisesRegex(RuntimeError, "parent.*absent"):
                    materializer._resolve_work_root(lab / "absent" / "work")

    def test_link_reparse_and_non_directory_ancestors_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            repository, lab = self._canonical_lab(parent)

            plain = lab / "plain"
            plain.mkdir()
            linked_parent = lab / "linked-parent"
            linked_parent.symlink_to(plain, target_is_directory=True)
            linked_work = lab / "linked-work"
            linked_work.symlink_to(plain, target_is_directory=True)
            non_directory = lab / "file-parent"
            non_directory.write_text("not a directory", encoding="utf-8")
            external_alias = parent / "lab-alias"
            external_alias.symlink_to(lab, target_is_directory=True)

            with mock.patch.object(
                materializer,
                "_canonical_repository_root",
                return_value=repository,
            ):
                for rejected in (
                    linked_parent / "work",
                    linked_work,
                ):
                    with self.subTest(rejected=rejected):
                        with self.assertRaisesRegex(RuntimeError, "link or reparse"):
                            materializer._resolve_work_root(rejected)
                with self.assertRaisesRegex(RuntimeError, "non-directory"):
                    materializer._resolve_work_root(non_directory / "work")
                with self.assertRaisesRegex(RuntimeError, "exact.*local-lab"):
                    materializer._resolve_work_root(external_alias / "work")

    def test_non_plain_or_missing_canonical_lab_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            repository = parent / "canonical"
            repository.mkdir()
            external = parent / "external-lab"
            external.mkdir()

            with mock.patch.object(
                materializer,
                "_canonical_repository_root",
                return_value=repository,
            ):
                with self.assertRaisesRegex(RuntimeError, "local-lab.*absent"):
                    materializer._resolve_work_root(repository / "local-lab" / "work")

                (repository / "local-lab").symlink_to(
                    external,
                    target_is_directory=True,
                )
                with self.assertRaisesRegex(RuntimeError, "link or reparse"):
                    materializer._resolve_work_root(repository / "local-lab" / "work")

    def test_retail_installation_overlap_is_rejected_inside_the_lab(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository, lab = self._canonical_lab(Path(temporary))
            retail = lab / "retail"
            retail.mkdir()

            with mock.patch.object(
                materializer,
                "_canonical_repository_root",
                return_value=repository,
            ):
                with self.assertRaisesRegex(RuntimeError, "retail installation"):
                    materializer._resolve_work_root(
                        retail / "materializer-work",
                        game_root=retail,
                    )


class World110PlayerStartTests(unittest.TestCase):
    def test_seed_wrapper_rewalks_the_exact_container_and_admits_all_rows(self) -> None:
        raw_world = b"world-container"
        wres = b"wres"
        wrld = b"wrld"
        rlwd = b"rlwd"
        objects = (mock.sentinel.object_row,)
        reader = mock.Mock()
        reader.position = materializer.WORLD110_INITIAL_OBJECT_HEADER_OFFSET
        reader.int32.side_effect = [0, 0, 0, 0, 0, 0, 0, 0, 0, 13]

        def parse_objects(*_args: object) -> tuple[object, ...]:
            reader.position = materializer.WORLD110_TREE_GROUP_HEADER_OFFSET + 6
            return objects

        def chunk_payload(data: bytes, kind: bytes) -> bytes:
            expected = {
                (raw_world, b"WRES"): wres,
                (wres, b"WRLD"): wrld,
                (wrld, b"RLWD"): rlwd,
            }
            return expected[(data, kind)]

        with (
            mock.patch.object(
                materializer,
                "_chunk_payload",
                side_effect=chunk_payload,
            ) as extract,
            mock.patch.object(
                materializer,
                "WORLD110_RLWD_SIZE",
                len(rlwd),
            ),
            mock.patch.object(
                materializer,
                "WORLD110_RLWD_SHA256",
                materializer._sha256(rlwd),
            ),
            mock.patch.object(materializer, "_parse_world_scripts") as scripts,
            mock.patch.object(
                materializer,
                "_WorldReader",
                return_value=reader,
            ),
            mock.patch.object(
                materializer,
                "_skip_level100_script_object",
            ) as skip_script,
            mock.patch.object(
                materializer,
                "_parse_world_initial_objects",
                side_effect=parse_objects,
            ) as parse_objects,
            mock.patch.object(
                materializer,
                "_admit_world110_player_start",
            ) as admit,
        ):
            self.assertEqual(
                objects,
                materializer._parse_world110_initial_object_seeds(raw_world),
            )

        self.assertEqual(3, extract.call_count)
        scripts.assert_called_once_with(
            raw_world,
            110,
            materializer.LEVEL110_SCRIPT_OBJECTS,
            materializer.COMMON_WORLD_LEVEL_HEADER,
        )
        self.assertEqual(len(materializer.LEVEL110_SCRIPT_OBJECTS), skip_script.call_count)
        parse_objects.assert_called_once_with(
            reader,
            110,
            materializer.WORLD110_INITIAL_OBJECT_HEADER,
            materializer.WORLD110_INITIAL_OBJECT_TYPE_COUNTS,
        )
        admit.assert_called_once_with(objects)

    def test_player_start_wrapper_filters_the_admitted_seed_table(self) -> None:
        objects = (mock.sentinel.object_row,)
        start = mock.sentinel.player_start
        with (
            mock.patch.object(
                materializer,
                "_parse_world110_initial_object_seeds",
                return_value=objects,
            ) as parse_seeds,
            mock.patch.object(
                materializer,
                "_admit_world110_player_start",
                return_value=start,
            ) as admit,
        ):
            self.assertIs(start, materializer._parse_world110_player_start(b"world"))

        parse_seeds.assert_called_once_with(b"world")
        admit.assert_called_once_with(objects)

    def test_wrapper_rejects_changed_rlwd_before_interpreting_it(self) -> None:
        with (
            mock.patch.object(
                materializer,
                "_chunk_payload",
                side_effect=(b"wres", b"wrld", b"changed-rlwd"),
            ),
            mock.patch.object(
                materializer,
                "WORLD110_RLWD_SIZE",
                len(b"changed-rlwd"),
            ),
            mock.patch.object(materializer, "_parse_world_scripts") as scripts,
        ):
            with self.assertRaisesRegex(RuntimeError, "RLWD identity changed"):
                materializer._parse_world110_player_start(b"world-container")

        scripts.assert_not_called()

    def test_exact_table_preserves_the_raw_authored_start(self) -> None:
        reader, objects = _world110_initial_object_fixture()
        start = materializer._admit_world110_player_start(objects)

        self.assertEqual(40, len(objects))
        self.assertEqual(len(reader.data), reader.position)
        self.assertEqual(1, start.ordinal)
        self.assertEqual(15_781, start.record_offset)
        self.assertEqual(59, start.record_bytes)
        self.assertEqual(
            "850de203b32b967064f3a9bacca24bebd783af68760a8b4c056ea242a2b47dfc",
            start.record_sha256,
        )
        self.assertEqual((0x43846000, 0x43816800, 0x80000000), start.position_bits)
        self.assertEqual((0xBF04FD8B, 0, 0), start.orientation_bits)
        self.assertEqual(0, start.plane_mode)
        self.assertEqual(1, start.player_number)

    def test_changed_header_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "header changed"):
            _world110_initial_object_fixture(header=(2, 1, 40))

    def test_changed_start_and_duplicate_type_census_are_rejected(self) -> None:
        _, objects = _world110_initial_object_fixture(start_player_number=2)
        with self.assertRaisesRegex(RuntimeError, "record changed"):
            materializer._admit_world110_player_start(objects)
        with self.assertRaisesRegex(RuntimeError, "type census changed"):
            _world110_initial_object_fixture(extra_start=True)

    def test_admission_rejects_zero_or_two_player_starts(self) -> None:
        _, objects = _world110_initial_object_fixture()
        start = next(item for item in objects if item.thing_type == 15)

        without_start = tuple(item for item in objects if item.thing_type != 15)
        with self.assertRaisesRegex(RuntimeError, "exactly one.*found 0"):
            materializer._admit_world110_player_start(without_start)

        with self.assertRaisesRegex(RuntimeError, "exactly one.*found 2"):
            materializer._admit_world110_player_start(objects + (start,))

    def test_changed_plane_or_raw_pose_bit_is_rejected(self) -> None:
        _, objects = _world110_initial_object_fixture(start_plane_mode=1)
        with self.assertRaisesRegex(RuntimeError, "record changed"):
            materializer._admit_world110_player_start(objects)
        _, objects = _world110_initial_object_fixture(
            start_position_bits=(0x43846001, 0x43816800, 0x80000000)
        )
        with self.assertRaisesRegex(RuntimeError, "record changed"):
            materializer._admit_world110_player_start(objects)

    def test_unsupported_type_and_tree_misalignment_are_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "unsupported thing type"):
            _world110_initial_object_fixture(unsupported_type=True)
        with self.assertRaisesRegex(RuntimeError, "tree groups"):
            _world110_initial_object_fixture(tree_header=(1, 2))

    def test_truncated_type_specific_tail_is_rejected(self) -> None:
        payload = struct.pack("<iiH", 2, 0, 1) + _world_initial_object(28)[:-2]
        reader = materializer._WorldReader(payload)
        with self.assertRaises(RuntimeError):
            materializer._parse_world_initial_objects(
                reader,
                110,
                (2, 0, 1),
                {28: 1},
            )


class World110InitialObjectSeedTests(unittest.TestCase):
    @staticmethod
    def _parse_rows(rows: list[bytes]) -> tuple[materializer._WorldInitialObject, ...]:
        payload = bytearray(struct.pack("<iiH", 2, 0, len(rows)))
        payload.extend(b"".join(rows))
        payload.extend(struct.pack("<Hi", 0, 2))
        return materializer._parse_world_initial_objects(
            materializer._WorldReader(bytes(payload)),
            110,
            (2, 0, len(rows)),
            {
                thing_type: sum(
                    struct.unpack_from("<i", row)[0] == thing_type for row in rows
                )
                for thing_type in sorted(
                    {struct.unpack_from("<i", row)[0] for row in rows}
                )
            },
        )

    def test_all_seven_closed_tails_retain_distinct_non_default_values(self) -> None:
        rows = self._parse_rows(
            [
                _world_initial_object(
                    8,
                    definition_name="Exact Unit",
                ),
                _world_initial_object(15, plane_mode=1, player_number=2),
                _world_initial_object(18),
                _world_initial_object(
                    19,
                    amount=7,
                    delay_bits=0x3F800001,
                    squad_delay_bits=0x40000002,
                    initial_delay_bits=0x40400003,
                    squad_size=4,
                    spawn_unit="Exact Spawn Unit",
                    spawner_spawn_script="SpawnerTailScript",
                    spawn_script="CommonSpawnScript",
                ),
                _world_initial_object(27, script="Carrier"),
                _world_initial_object(
                    28,
                    amount=9,
                    mode=2,
                    definition_name="Exact Squad",
                ),
                _world_initial_object(36, radius_bits=0x42480001),
            ]
        )

        self.assertEqual(
            materializer._WorldUnitSeedTail("Exact Unit", -1),
            rows[0].tail,
        )
        self.assertEqual(materializer._WorldStartSeedTail(1, 2), rows[1].tail)
        self.assertIsInstance(rows[2].tail, materializer._WorldWaypointSeedTail)
        self.assertEqual(
            materializer._WorldSpawnerSeedTail(
                7,
                0x3F800001,
                0x40000002,
                0x40400003,
                4,
                "Exact Spawn Unit",
                "SpawnerTailScript",
            ),
            rows[3].tail,
        )
        self.assertEqual("CommonSpawnScript", rows[3].spawn_script)
        self.assertIsInstance(rows[4].tail, materializer._WorldScriptSeedTail)
        self.assertEqual(
            materializer._WorldSquadSeedTail(9, 2, "Exact Squad", -1),
            rows[5].tail,
        )
        self.assertEqual(
            materializer._WorldVolumeSeedTail(0x42480001),
            rows[6].tail,
        )

    def test_non_finite_common_and_tail_words_fail_closed(self) -> None:
        cases = (
            _world_initial_object(18, position_bits=(0x7F800000, 0, 0)),
            _world_initial_object(19, delay_bits=0x7FC00000),
            _world_initial_object(36, radius_bits=0xFF800000),
        )
        for row in cases:
            with self.subTest(thing_type=struct.unpack_from("<i", row)[0]):
                with self.assertRaisesRegex(RuntimeError, "non-finite"):
                    self._parse_rows([row])

    def test_invalid_flags_sentinels_and_cardinalities_fail_closed(self) -> None:
        cases = (
            (_world_initial_object(18, active=2), "non-boolean"),
            (_world_initial_object(18, attach_scripts=-1), "non-boolean"),
            (_world_initial_object(8, trailer=0), "type-8.*trailer"),
            (_world_initial_object(28, trailer=0), "type-28.*trailer"),
            (_world_initial_object(19, amount=0), "cardinality"),
            (_world_initial_object(19, squad_size=-1), "cardinality"),
            (_world_initial_object(28, amount=-1), "configuration"),
            (_world_initial_object(28, mode=4), "configuration"),
        )
        for row, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(RuntimeError, message):
                    self._parse_rows([row])

    def test_canonical_seed_serialization_is_byte_deterministic(self) -> None:
        _, parsed = _world110_initial_object_fixture()
        exact_lengths = (
            62, 59, 56, 51, 51, 122, 51, 51, 89, 55,
            51, 51, 90, 90, 78, 51, 78, 87, 78, 92,
            89, 51, 51, 51, 51, 71, 51, 51, 51, 51,
            51, 51, 51, 51, 77, 77, 77, 77, 77, 58,
        )
        offset = materializer.WORLD110_INITIAL_OBJECT_FIRST_RECORD_OFFSET
        normalized: list[materializer._WorldInitialObject] = []
        for item, length in zip(parsed, exact_lengths, strict=True):
            normalized.append(
                item._replace(record_offset=offset, record_bytes=length)
            )
            offset += length
        rows = tuple(normalized)

        first = materializer._world110_initial_object_seed_bytes(rows)
        second = materializer._world110_initial_object_seed_bytes(rows)

        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertNotIn(b" ", first)
        self.assertEqual(
            materializer.WORLD110_INITIAL_OBJECT_SEEDS_SCHEMA,
            json.loads(first)["schema"],
        )
        self.assertRegex(
            materializer.WORLD110_INITIAL_OBJECT_SEEDS_SHA256,
            r"^[0-9a-f]{64}$",
        )


class StartupMediaCacheTests(unittest.TestCase):
    def test_complete_rgb_png_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "frame.png"
            path.write_bytes(_png(2, 3))
            self.assertEqual((2, 3), materializer._png_dimensions(path))

    def test_header_only_png_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "frame.png"
            path.write_bytes(_png(2, 3)[:33])
            self.assertIsNone(materializer._png_dimensions(path))

    def test_framed_but_invalid_idat_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "frame.png"
            path.write_bytes(_png(2, 3, idat=b"\x01"))
            self.assertIsNone(materializer._png_dimensions(path))

    def test_non_object_manifest_is_not_a_ready_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            (media / "startup-media.json").write_text("[]", encoding="utf-8")
            self.assertFalse(materializer._startup_media_ready(root, media))

    def test_legacy_v2_cache_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            (media / "startup-media.json").write_text(
                '{"schema":"onslaught-startup-media.v2","clips":{},"stills":{}}',
                encoding="utf-8",
            )
            self.assertFalse(materializer._startup_media_ready(root, media))

    def test_ready_cache_rejects_a_corrupt_middle_frame(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            frames = media / "clip"
            frames.mkdir(parents=True)
            source = root / "clip.vid"
            splash_source = root / "splash.tga"
            source.write_bytes(b"clip-source")
            splash_source.write_bytes(b"splash-source")
            frame_paths = []
            for frame in range(1, 4):
                path = frames / f"f{frame:05d}.png"
                path.write_bytes(_png(2, 3))
                frame_paths.append(path)
            (media / "splash.png").write_bytes(_png(512, 512))
            manifest = {
                "schema": materializer.STARTUP_MEDIA_SCHEMA,
                "clips": {
                    "Logo": {
                        "source": "clip.vid",
                        "sourceSha256": materializer._sha256(source.read_bytes()),
                        "width": 2,
                        "height": 3,
                        "fpsNumerator": 25,
                        "fpsDenominator": 1,
                        "frameCount": 3,
                        "framePathFormat": "clip/f{0:D5}.png",
                        "framesSha256": materializer._startup_frame_set_sha256(
                            frame_paths
                        ),
                    }
                },
                "stills": {
                    "Splash": {
                        "source": "splash.tga",
                        "sourceSha256": materializer._sha256(
                            splash_source.read_bytes()
                        ),
                        "path": "splash.png",
                        "outputSha256": materializer._sha256(
                            (media / "splash.png").read_bytes()
                        ),
                    }
                },
            }
            (media / "startup-media.json").write_text(
                __import__("json").dumps(manifest),
                encoding="utf-8",
            )
            with (
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_CLIPS",
                    (("Logo", "clip.vid", "clip", 2, 3, 25, 3),),
                ),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
            ):
                self.assertTrue(materializer._startup_media_ready(root, media))
                frame_paths[1].write_bytes(b"corrupt-middle-frame")
                self.assertFalse(materializer._startup_media_ready(root, media))

    def test_ready_cache_rejects_a_valid_but_different_splash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            splash_source = root / "splash.tga"
            splash_source.write_bytes(b"splash-source")
            splash_path = media / "splash.png"
            splash_path.write_bytes(_png(512, 512))
            manifest = {
                "schema": materializer.STARTUP_MEDIA_SCHEMA,
                "clips": {},
                "stills": {
                    "Splash": {
                        "source": "splash.tga",
                        "sourceSha256": materializer._sha256(
                            splash_source.read_bytes()
                        ),
                        "path": "splash.png",
                        "outputSha256": materializer._sha256(
                            splash_path.read_bytes()
                        ),
                    }
                },
            }
            (media / "startup-media.json").write_text(
                __import__("json").dumps(manifest),
                encoding="utf-8",
            )
            with (
                mock.patch.object(materializer, "STARTUP_MEDIA_CLIPS", ()),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
            ):
                self.assertTrue(materializer._startup_media_ready(root, media))
                del manifest["stills"]["Splash"]["outputSha256"]
                (media / "startup-media.json").write_text(
                    json.dumps(manifest),
                    encoding="utf-8",
                )
                self.assertFalse(materializer._startup_media_ready(root, media))
                manifest["stills"]["Splash"]["outputSha256"] = (
                    materializer._sha256(splash_path.read_bytes())
                )
                (media / "startup-media.json").write_text(
                    json.dumps(manifest),
                    encoding="utf-8",
                )
                splash_path.write_bytes(_png(512, 512, last_pixel=1))
                self.assertFalse(materializer._startup_media_ready(root, media))

    def test_generation_rejects_a_malformed_splash_before_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            (root / "splash.tga").write_bytes(b"splash-source")
            with (
                mock.patch.object(materializer, "STARTUP_MEDIA_CLIPS", ()),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
                mock.patch.object(materializer.subprocess, "run"),
                mock.patch.object(
                    materializer,
                    "_png_dimensions",
                    return_value=None,
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "invalid 512x512 PNG"):
                    materializer._materialize_startup_media(root, media)
            self.assertFalse((media / "startup-media.json").exists())

    def test_generation_receipts_exact_splash_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            source = root / "splash.tga"
            source.write_bytes(b"splash-source")

            def write_splash(arguments: list[str], **_kwargs: object) -> None:
                Path(arguments[-1]).write_bytes(_png(512, 512))

            with (
                mock.patch.object(materializer, "STARTUP_MEDIA_CLIPS", ()),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
                mock.patch.object(
                    materializer.subprocess,
                    "run",
                    side_effect=write_splash,
                ),
            ):
                manifest_path = materializer._materialize_startup_media(root, media)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            splash_path = media / "splash.png"
            self.assertEqual("onslaught-startup-media.v4", manifest["schema"])
            self.assertEqual(
                materializer._sha256(splash_path.read_bytes()),
                manifest["stills"]["Splash"]["outputSha256"],
            )


def _bink_header(track_ids: list[int], sample_rate: int = 44100) -> bytes:
    """A Bink header carrying only what _bink_audio_tracks reads."""
    count = len(track_ids)
    header = bytearray(b"BIKi")
    header += struct.pack("<I", 0)          # 0x04 file size
    header += struct.pack("<I", 3095)       # 0x08 frame count
    header += struct.pack("<I", 0)          # 0x0C largest frame
    header += struct.pack("<I", 3095)       # 0x10 frame count again
    header += struct.pack("<II", 480, 300)  # 0x14 width / 0x18 height
    header += struct.pack("<II", 25, 1)     # 0x1C fps num / 0x20 den
    header += struct.pack("<I", 0)          # 0x24 video flags
    header += struct.pack("<I", count)      # 0x28 audio track count
    header += b"".join(struct.pack("<I", 0) for _ in range(count))
    header += b"".join(struct.pack("<HH", sample_rate, 0xE000) for _ in range(count))
    header += b"".join(struct.pack("<I", track) for track in track_ids)
    return bytes(header)


def _pcm_wav(sample_frames: int, rate: int = 44100, channels: int = 2) -> bytes:
    block_align = channels * 2
    data = bytes(sample_frames * block_align)
    return (
        b"RIFF"
        + struct.pack("<I", 36 + len(data))
        + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, channels, rate, rate * block_align, block_align, 16)
        + b"data"
        + struct.pack("<I", len(data))
        + data
    )


class CutsceneVoiceTrackTests(unittest.TestCase):
    """The two laws that connect "English is Bink track 0" to bytes on disk.

    Everything else in that chain is a property of BEA.exe and was read out of
    the pristine specimen. These are the parts that are properties of the .vid
    and of the decode, so they are the parts this script can check on any
    machine and the parts a wrong edit here would silently break.
    """

    # Real numbers from cutscenes/01.vid: 3095 video frames at 25 fps is
    # 5,459,580 sample frames at 44.1 kHz, and the decode produces 5,460,480 —
    # an overhang of 900, well inside one 2048-sample binkaudio frame.
    VIDEO_FRAMES = 3095
    FPS = 25
    DECODED_SAMPLE_FRAMES = 5_460_480

    def _run(self, temporary: str, track_ids: list[int], sample_frames: int):
        root = Path(temporary)
        destination = root / "clip"
        destination.mkdir(parents=True, exist_ok=True)
        source = root / "01.vid"
        source.write_bytes(_bink_header(track_ids))

        def write_audio(arguments: list[str], **_kwargs: object) -> None:
            Path(arguments[-1]).write_bytes(_pcm_wav(sample_frames))

        with mock.patch.object(
            materializer.subprocess, "run", side_effect=write_audio
        ):
            return materializer._materialize_clip_audio(
                source,
                "data/video/cutscenes/01.vid",
                "clip",
                destination,
                self.VIDEO_FRAMES,
                self.FPS,
                (0, "voice-track00.wav", 44100, 2, 16),
            )

    def test_identity_track_table_and_measured_length_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            entry = self._run(temporary, [0, 1, 2, 3, 4], self.DECODED_SAMPLE_FRAMES)

        self.assertEqual(0, entry["track"])
        self.assertEqual("clip/voice-track00.wav", entry["path"])
        self.assertEqual(44100, entry["sampleRate"])
        self.assertEqual(2, entry["channels"])
        self.assertEqual(self.DECODED_SAMPLE_FRAMES, entry["sampleFrameCount"])
        self.assertEqual(64, len(entry["outputSha256"]))

    def test_a_non_identity_track_table_is_refused(self) -> None:
        # BinkSetSoundTrack takes a track ID; `-map 0:a:N` takes an ordinal.
        # They coincide only while the shipped table is the identity. If it ever
        # is not, ordinal 0 stops being the track the game would have played and
        # the decode must fail rather than quietly ship another language.
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "not the identity"):
                self._run(temporary, [4, 3, 2, 1, 0], self.DECODED_SAMPLE_FRAMES)

    def test_an_audio_track_that_does_not_match_the_video_length_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            # One binkaudio frame too long.
            with self.assertRaisesRegex(RuntimeError, r"sample frames"):
                self._run(
                    temporary,
                    [0, 1, 2, 3, 4],
                    self.DECODED_SAMPLE_FRAMES + materializer.BINK_AUDIO_FRAME_SAMPLES,
                )

        with tempfile.TemporaryDirectory() as temporary:
            # Short of the video: the movie would outlive its voice.
            with self.assertRaisesRegex(RuntimeError, r"sample frames"):
                self._run(temporary, [0, 1, 2, 3, 4], self.VIDEO_FRAMES * 44100 // self.FPS - 1)


class FrontendLoadingBarAssetsTests(unittest.TestCase):
    def test_barl_barc_barr_are_hash_pinned(self) -> None:
        rows = {
            destination.as_posix(): (source, expected)
            for destination, source, expected in materializer.FRONTEND_ASSETS
        }
        self.assertEqual(
            rows["rebuild/OnslaughtRebuild.Godot/Assets/Frontend/bar-l.texture.aya"],
            (
                "data/resources/dxtntextures/FrontEnd%BarL.tga(0)A8R8G8B8.aya",
                "fbd28ca720ebe91cb8f58a9f5be5e4e9ee5c013fc42052fd1bec6b41dfd094bd",
            ),
        )
        self.assertEqual(
            rows["rebuild/OnslaughtRebuild.Godot/Assets/Frontend/bar-c.texture.aya"],
            (
                "data/resources/dxtntextures/FrontEnd%BarC.tga(0)A8R8G8B8.aya",
                "347828edf9f97dd3463ce7374e167e57f8bd837113cbfad71cb8cbc6bcde68a5",
            ),
        )
        self.assertEqual(
            rows["rebuild/OnslaughtRebuild.Godot/Assets/Frontend/bar-r.texture.aya"],
            (
                "data/resources/dxtntextures/FrontEnd%BarR.tga(0)A8R8G8B8.aya",
                "9995d4a41ff140d3d33004086e82f940db946c0db45635b5c853662ace6c6199",
            ),
        )


class FrontendDebriefingAssetsTests(unittest.TestCase):
    def test_settled_ring_and_grade_surfaces_are_hash_pinned(self) -> None:
        rows = {
            destination.as_posix(): (source, expected)
            for destination, source, expected in materializer.FRONTEND_ASSETS
        }
        expected = {
            "metal-ring-transition": (
                "FrontEnd%v2%FE_metal_ring_trans_from_levsel2.tga(0)A8R8G8B8.aya",
                "8b9b79189981de706fc72de9552bdc398ada96d892c0e4e33706c77a907da869",
            ),
            "ranking-a": (
                "FrontEnd%RankingA.tga(0)A8R8G8B8.aya",
                "88765906f295b8002dc254f9805b05d5f5589d87a08f297b37d90953ba57d625",
            ),
            "ranking-b": (
                "FrontEnd%RankingB.tga(0)A8R8G8B8.aya",
                "5f03cdf1e79e679e706a0b6ab644ad6961447dace35695dc93d7c3928ebf3d50",
            ),
            "ranking-c": (
                "FrontEnd%RankingC.tga(0)A8R8G8B8.aya",
                "364b5140a18ebec99bdf4e4ce7c99e3619ff743d4cbe888c0fa5d84e96407a06",
            ),
            "ranking-d": (
                "FrontEnd%RankingD.tga(0)A8R8G8B8.aya",
                "894521839162a5d2d8d73feba39435cf0590b0863d65b67daa5c4a4420485bd0",
            ),
            "ranking-e": (
                "FrontEnd%RankingE.tga(0)A8R8G8B8.aya",
                "c844f938cfcf56a2f3908bb69313ec86153f97e6993f42172c2c8376897e911a",
            ),
            "ranking-s": (
                "FrontEnd%RankingS.tga(0)A8R8G8B8.aya",
                "aab0817f798ff8379cf6e9e0f86ae466832ad644170e8c14b6f7a50a6a12de9f",
            ),
        }

        for name, (source, expected_hash) in expected.items():
            self.assertEqual(
                rows[
                    "rebuild/OnslaughtRebuild.Godot/Assets/Frontend/"
                    f"Debriefing/{name}.texture.aya"
                ],
                (f"data/resources/dxtntextures/{source}", expected_hash),
            )


if __name__ == "__main__":
    unittest.main()
