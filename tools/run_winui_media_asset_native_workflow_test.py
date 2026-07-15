#!/usr/bin/env python3
"""Tests for the fail-closed native WinUI Media/Asset workflow runner."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import struct
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib
from collections.abc import Callable
from pathlib import Path
from unittest import mock

import run_winui_media_asset_native_workflow as harness


RUN_ID = "a" * 32
OTHER_ID = "b" * 32
INTERACTION_MODE = (
    "UIA Value/SelectionItem/ScrollItem/Scroll/Focus/Invoke; no keyboard, pointer, "
    "playback, reveal, browse, clipboard, export, or package actions"
)
EMPTY_SHA256 = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
FIXTURE_SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "OnslaughtCareerEditor.UiTests"
    / "MediaAssetNativeFixture.cs"
)


def fixture_catalog_bytes() -> bytes:
    source = FIXTURE_SOURCE_PATH.read_text(encoding="utf-8")
    match = re.search(
        r'private const string CatalogJson = """\n(?P<body>.*?)\n        """;',
        source,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Media/Asset fixture catalog source shape changed")
    lines = match.group("body").split("\n")
    if any(not line.startswith("        ") for line in lines):
        raise AssertionError("Media/Asset fixture catalog indentation changed")
    return "\n".join(line[8:] for line in lines).encode("utf-8")


def fixture_texture_bytes() -> bytes:
    source = FIXTURE_SOURCE_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"private static readonly byte\[\] FixturePng\s*=\s*\[(?P<body>.*?)\];",
        source,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Media/Asset fixture PNG source shape changed")
    values = [int(value) for value in re.findall(r"\b\d+\b", match.group("body"))]
    return bytes(values)


def build_minimal_binary_fbx(texture_file_name: str) -> bytes:
    data = bytearray(b"Kaydara FBX Binary  \x00\x1a\x00")
    data.extend(struct.pack("<I", 7400))

    def long_property(value: int) -> bytes:
        return b"L" + struct.pack("<q", value)

    def string_property(value: str) -> bytes:
        encoded = value.encode("utf-8")
        return b"S" + struct.pack("<I", len(encoded)) + encoded

    def double_array_property(values: tuple[float, ...]) -> bytes:
        encoded = struct.pack(f"<{len(values)}d", *values)
        return b"d" + struct.pack("<III", len(values), 0, len(encoded)) + encoded

    def int_array_property(values: tuple[int, ...]) -> bytes:
        encoded = struct.pack(f"<{len(values)}i", *values)
        return b"i" + struct.pack("<III", len(values), 0, len(encoded)) + encoded

    def write_node(
        name: str,
        properties: tuple[bytes, ...],
        children: tuple[Callable[[], None], ...],
    ) -> None:
        header_position = len(data)
        encoded_name = name.encode("ascii")
        data.extend(bytes(13))
        data.extend(encoded_name)
        property_start = len(data)
        for value in properties:
            data.extend(value)
        property_end = len(data)
        for child in children:
            child()
        if children:
            data.extend(bytes(13))
        end_position = len(data)
        struct.pack_into(
            "<III",
            data,
            header_position,
            end_position,
            len(properties),
            property_end - property_start,
        )
        data[header_position + 12] = len(encoded_name)

    def geometry() -> None:
        write_node(
            "Geometry",
            (
                long_property(1),
                string_property("Fixture\0\x01Geometry"),
                string_property("Mesh"),
            ),
            (
                lambda: write_node(
                    "Vertices",
                    (double_array_property((0, 0, 0, 1, 0, 0, 0, 1, 0)),),
                    (),
                ),
                lambda: write_node(
                    "PolygonVertexIndex",
                    (int_array_property((0, 1, -3)),),
                    (),
                ),
            ),
        )

    write_node(
        "Objects",
        (),
        (
            geometry,
            lambda: write_node(
                "Model",
                (long_property(2), string_property("Fixture\0\x01Model"), string_property("Mesh")),
                (),
            ),
            lambda: write_node(
                "Material",
                (long_property(3), string_property("Material1\0\x01Material"), string_property("")),
                (),
            ),
            lambda: write_node(
                "Texture",
                (
                    long_property(4),
                    string_property("base_color_texture\0\x01Texture"),
                    string_property(""),
                    string_property(texture_file_name),
                ),
                (),
            ),
        ),
    )
    data.extend(bytes(13))
    return bytes(data)


CATALOG_BYTES = fixture_catalog_bytes()
FBX_BYTES = build_minimal_binary_fbx("texture_one.tga")
TEXTURE_BYTES = fixture_texture_bytes()

FIXTURE_BYTES = {
    "asset-bundle/asset_catalog/catalog.json": CATALOG_BYTES,
    "asset-bundle/exports/body00_binary.fbx": FBX_BYTES,
    "asset-bundle/exports/fixture_mesh_binary.fbx": FBX_BYTES,
    "asset-bundle/exports/fixture_texture.png": TEXTURE_BYTES,
    "media-game/BEA.exe": b"",
    "media-game/data/Music/battle_theme (Master).ogg": b"",
    "media-game/data/sounds/english/MessageBox/110_arrival.ogg": b"",
    "media-game/data/sounds/english/MessageBox/HEALTH_low.ogg": b"",
    "media-game/data/sounds/english/MessageBox/TUTORIAL_intro.ogg": b"",
    "media-game/data/video/OpeningFMV.vid": b"",
    "media-game/data/video/UsTheMovie.vid": b"",
    "media-game/data/video/briefings/PC_101_exact.vid": b"",
    "media-game/data/video/cutscenes/02.vid": b"",
}

CAPTURE_SPEC = {
    "media-audio-selected-normal.png": (
        "media-audio", "audio-selected", "MediaAudioSearchBox", 1100, 900,
        ("MediaAudioSearchBox", "MediaAudioTreeView", "MediaAudioNowPlaying", "MediaAudioSourceSummary"),
    ),
    "media-audio-selected-760.png": (
        "media-audio", "audio-selected", "MediaAudioSearchBox", 760, 820,
        ("MediaAudioSearchBox", "MediaAudioTreeView", "MediaAudioNowPlaying", "MediaAudioSourceSummary"),
    ),
    "media-video-selected-normal.png": (
        "media-video", "video-selected", "MediaVideoSearchBox", 1100, 900,
        ("MediaVideoSearchBox", "MediaVideoTreeView", "MediaVideoPlayerStatus", "MediaVideoSelected", "MediaVideoSourceSummary"),
    ),
    "media-video-selected-760.png": (
        "media-video", "video-selected", "MediaVideoSearchBox", 760, 820,
        ("MediaVideoSearchBox", "MediaVideoTreeView", "MediaVideoPlayerStatus", "MediaVideoSelected", "MediaVideoSourceSummary"),
    ),
    "asset-texture-selected-normal.png": (
        "asset-library", "texture-selected", "AssetSearchBox", 1100, 900,
        ("AssetCatalogSummary", "AssetItemsList", "AssetSelectedTitle", "AssetTexturePreviewImage"),
    ),
    "asset-texture-selected-760.png": (
        "asset-library", "texture-selected", "AssetSearchBox", 760, 820,
        ("AssetCatalogSummary", "AssetItemsList", "AssetSelectedTitle", "AssetTexturePreviewImage"),
    ),
    "asset-model-wireframe-normal.png": (
        "asset-library", "model-wireframe", "AssetMeshesTabButton", 1100, 900,
        ("AssetItemsList", "AssetPreviewTitle", "AssetModelWireframeStatus", "AssetModelWireframePanel"),
    ),
    "asset-model-wireframe-760.png": (
        "asset-library", "model-wireframe", "AssetMeshesTabButton", 760, 820,
        ("AssetItemsList", "AssetPreviewTitle", "AssetModelWireframeStatus", "AssetModelWireframePanel"),
    ),
}

SELECTIONS = {
    "media-audio": [
        {
            "Phase": "audio-selected",
            "Title": "TUTORIAL_intro",
            "Summary": "Tutorial • TUTORIAL_intro.ogg",
            "Detail": "play-enabled-no-playback",
        }
    ],
    "media-video": [
        {
            "Phase": "video-selected",
            "Title": "Credits Video",
            "Summary": "Main Videos • UsTheMovie.vid",
            "Detail": "play-enabled-deferred-no-playback",
        }
    ],
    "asset-library": [
        {
            "Phase": "texture-selected",
            "Title": "Texture One",
            "Summary": "fixture; 1 packed references; export available.",
            "Detail": "texture:fixture/texture_one.tga",
        },
        {
            "Phase": "model-wireframe",
            "Title": "fixture_mesh.msh",
            "Summary": "1 packed references; FBX export available. Use the in-app wireframe for a quick geometry check, then open the FBX for full material review.",
            "Detail": "Binary FBX 7400; 3 vertices; 3 polygon index entries; UV mapping: no coordinate data recorded.",
        },
    ],
}

APPLICATION_PAYLOAD_PATHS = (
    "App.xbf",
    "MainWindow.xbf",
    "OnslaughtCareerEditor.AppCore.dll",
    "OnslaughtCareerEditor.WinUI.deps.json",
    "OnslaughtCareerEditor.WinUI.dll",
    "OnslaughtCareerEditor.WinUI.exe",
    "OnslaughtCareerEditor.WinUI.pri",
    "OnslaughtCareerEditor.WinUI.runtimeconfig.json",
    "Pages/AboutPage.xbf",
    "Pages/AssetLibraryPage.xbf",
    "Pages/BinaryPatchesPage.xbf",
    "Pages/HomePage.xbf",
    "Pages/LorePage.xbf",
    "Pages/MediaPage.xbf",
    "Pages/SavesPage.xbf",
    "Pages/SettingsPage.xbf",
    "patches/catalog/patches.v2.json",
    "patches/catalog/safe-copy-profiles.v1.json",
)


def write_trx(path: Path, *, passed: int = 1, not_executed: int = 0, outcome: str = "Passed") -> None:
    root = ET.Element("TestRun")
    results = ET.SubElement(root, "Results")
    ET.SubElement(results, "UnitTestResult", {"testName": harness.TEST_METHOD_NAME, "outcome": outcome})
    summary = ET.SubElement(root, "ResultSummary", {"outcome": "Completed"})
    ET.SubElement(
        summary,
        "Counters",
        {
            "total": "1",
            "executed": str(1 - not_executed),
            "passed": str(passed),
            "failed": "0",
            "error": "0",
            "timeout": "0",
            "aborted": "0",
            "inconclusive": "0",
            "notExecuted": str(not_executed),
        },
    )
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def write_rgba_png(path: Path, width: int, height: int, *, flat: bool = False) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            if flat:
                rgba = (245, 245, 245, 255)
            elif 40 <= y <= 115:
                rgba = (32, 52, 154, 255)
            else:
                shade = ((x // 8) + (y // 8)) % 10
                rgba = (250 - shade * 18, 250 - shade * 16, 250 - shade * 13, 255)
            row.extend(rgba)
        rows.append(b"\x00" + bytes(row))
    path.write_bytes(
        harness.native_support.PNG_SIGNATURE
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"".join(rows)))
        + chunk(b"IEND", b"")
    )


class MediaAssetNativeWorkflowRunnerTests(unittest.TestCase):
    def test_commands_pin_debug_win_x64_and_exact_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            test_command = harness.native_test_command(root, root / "result.trx")
        for command in (harness.WINUI_BUILD_COMMAND, test_command):
            self.assertEqual("Debug", command[command.index("--configuration") + 1])
            self.assertEqual("win-x64", command[command.index("--runtime") + 1])
        self.assertIn(f"FullyQualifiedName={harness.TEST_FQN}", test_command)
        self.assertEqual(APPLICATION_PAYLOAD_PATHS, harness.APPLICATION_PAYLOAD_PATHS)

    def test_interaction_contract_excludes_side_effecting_actions(self) -> None:
        self.assertEqual(INTERACTION_MODE, harness.INTERACTION_MODE)

    def test_validate_manifest_accepts_exact_generated_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            summary = harness.validate_manifest(manifest, repo, expected_harness_run_id=RUN_ID)
        self.assertEqual(13, summary["fixtureFileCount"])
        self.assertEqual(8, summary["captureCount"])
        self.assertEqual(3, summary["workflowCount"])

    def test_validate_manifest_rejects_another_runner_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "another runner invocation"):
                harness.validate_manifest(manifest, repo, expected_harness_run_id=OTHER_ID)

    def test_validate_manifest_rejects_consistently_rehashed_fixture_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            catalog = manifest.parent / "fixtures" / "asset-bundle" / "asset_catalog" / "catalog.json"
            catalog.write_bytes(catalog.read_bytes() + b" ")
            receipt = payload["Fixture"]["Files"][0]
            receipt["Length"] = catalog.stat().st_size
            receipt["Sha256"] = harness.sha256(catalog)
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "canonical fixture receipt"):
                harness.validate_manifest(manifest, repo)

    def test_validate_manifest_rejects_toolkit_owned_payload_sibling_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            app_core = (
                repo
                / "OnslaughtCareerEditor.WinUI"
                / "bin"
                / "Debug"
                / "net10.0-windows10.0.19041.0"
                / "win-x64"
                / "OnslaughtCareerEditor.AppCore.dll"
            )
            app_core.write_bytes(b"tampered")

            with self.assertRaisesRegex(harness.NativeAcceptanceError, "application payload"):
                harness.validate_manifest(manifest, repo)

    def test_catalog_fbx_and_texture_are_independently_reparsed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            catalog = root / "catalog.json"
            fbx = root / "fixture.fbx"
            texture = root / "texture.png"
            catalog.write_bytes(CATALOG_BYTES)
            fbx.write_bytes(FBX_BYTES)
            texture.write_bytes(TEXTURE_BYTES)
            harness.validate_catalog_fixture(catalog)
            harness.validate_fbx_fixture(fbx)
            harness.validate_fixture_texture_png(texture)

            changed = json.loads(catalog.read_text(encoding="utf-8"))
            changed["summary"]["total_catalog_entries"] = 5
            catalog.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "catalog summary"):
                harness.validate_catalog_fixture(catalog)

            damaged_fbx = bytearray(FBX_BYTES)
            damaged_fbx[damaged_fbx.index(b"Vertices") + len(b"Vertices") + 2] = 8
            fbx.write_bytes(damaged_fbx)
            with self.assertRaises(harness.NativeAcceptanceError):
                harness.validate_fbx_fixture(fbx)

            write_rgba_png(texture, 8, 8, flat=True)
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "contrast"):
                harness.validate_fixture_texture_png(texture)

    def test_validate_manifest_rejects_capture_matrix_hash_or_visual_forgery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["Captures"].append(copy.deepcopy(payload["Captures"][0]))
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "exactly eight captures"):
                harness.validate_manifest(manifest, repo)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            capture = payload["Captures"][0]
            image = manifest.parent / capture["RelativeFileName"]
            write_rgba_png(image, capture["Width"], capture["Height"], flat=True)
            capture["Sha256"] = harness.sha256(image)
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "visual coverage"):
                harness.validate_manifest(manifest, repo)

    def test_validate_manifest_rejects_marker_focus_identity_or_selection_forgery(self) -> None:
        mutations = (
            (lambda payload: payload["Captures"][0]["Markers"].pop(), "marker set"),
            (lambda payload: payload["Captures"][0]["FocusAfterCapture"].update({"X": 1100}), "focus"),
            (
                lambda payload: payload["Workflows"][1].update(
                    {"Identity": copy.deepcopy(payload["Workflows"][0]["Identity"])}
                ),
                "distinct process launch identities",
            ),
            (lambda payload: payload["Workflows"][1].update({"PlaybackModulesLoaded": True}), "playback"),
            (lambda payload: payload["Workflows"][0]["Selections"][0].update({"Title": "forged"}), "selection"),
        )
        for mutate, message in mutations:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as temp_dir:
                repo = Path(temp_dir) / "repo"
                manifest = self._write_valid_manifest(repo)
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                mutate(payload)
                manifest.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(harness.NativeAcceptanceError, message):
                    harness.validate_manifest(manifest, repo)

    def test_validate_manifest_rejects_one_process_with_distinct_window_handles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            audio_identity = payload["Workflows"][0]["Identity"]
            video_identity = payload["Workflows"][1]["Identity"]
            video_identity["ProcessId"] = audio_identity["ProcessId"]
            video_identity["ProcessStartTimeUtc"] = audio_identity["ProcessStartTimeUtc"]
            video_identity["WindowOwnerProcessId"] = audio_identity["ProcessId"]
            for capture in payload["Captures"]:
                if capture["Workflow"] != "media-video":
                    continue
                capture["Identity"] = copy.deepcopy(video_identity)
                capture["FocusBeforeCapture"]["ProcessId"] = audio_identity["ProcessId"]
                capture["FocusAfterCapture"]["ProcessId"] = audio_identity["ProcessId"]
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(harness.NativeAcceptanceError, "distinct process launch identities"):
                harness.validate_manifest(manifest, repo)

    def test_validate_manifest_rejects_path_escape_and_reordered_fixture_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["Fixture"]["RootRelativePath"] = "../fixtures"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "fixture root"):
                harness.validate_manifest(manifest, repo)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["Fixture"]["Files"].reverse()
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "canonical fixture receipt"):
                harness.validate_manifest(manifest, repo)

    def test_validate_trx_rejects_skipped_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trx = Path(temp_dir) / "result.trx"
            write_trx(trx, passed=0, not_executed=1, outcome="NotExecuted")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "exactly one executed passing test"):
                harness.validate_trx(trx)

    def test_partial_scan_and_failed_cleanup_are_invocation_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            evidence = repo / "local-lab" / "winui-media-asset-native-workflow"
            evidence.mkdir(parents=True)
            owned = evidence / f"media-asset-x-{RUN_ID}"
            partial = evidence / f".media-asset-x-{RUN_ID}.partial"
            other = evidence / f"media-asset-x-{OTHER_ID}"
            owned.mkdir()
            partial.mkdir()
            other.mkdir()
            self.assertEqual([partial], harness.partial_evidence_directories(evidence))
            harness.remove_failed_invocation_evidence(RUN_ID, evidence, repo_root=repo)
            self.assertFalse(owned.exists())
            self.assertFalse(partial.exists())
            self.assertTrue(other.is_dir())

    def test_owned_roots_reject_junction_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            local_lab = repo / "local-lab"
            local_lab.mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            evidence = local_lab / "winui-media-asset-native-workflow"
            self._create_junction(evidence, outside)
            try:
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                    harness.verify_evidence_root(evidence, repo_root=repo)
            finally:
                evidence.rmdir()

    def test_build_output_preflight_rejects_junction_before_dotnet_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            for project in harness.BUILD_PROJECT_DIRECTORIES:
                (repo / project).mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            linked_bin = repo / "OnslaughtCareerEditor.WinUI" / "bin"
            self._create_junction(linked_bin, outside)
            try:
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                    harness.preflight_build_output_roots(repo)
                self.assertEqual([], list(outside.iterdir()))
            finally:
                linked_bin.rmdir()

    def test_owned_manifest_receipt_rechecks_hash_after_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            evidence = repo / "local-lab" / "winui-media-asset-native-workflow"
            original = harness.validate_manifest

            def validate_then_mutate(*args: object, **kwargs: object) -> dict[str, object]:
                summary = original(*args, **kwargs)
                manifest.write_text(manifest.read_text(encoding="utf-8") + " ", encoding="utf-8")
                return summary

            with mock.patch.object(harness, "validate_manifest", side_effect=validate_then_mutate):
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "changed during manifest reconciliation"):
                    harness.validate_owned_manifest_receipt(
                        manifest,
                        evidence_root=evidence,
                        repo_root=repo,
                        expected_harness_run_id=RUN_ID,
                    )

    def test_owned_manifest_receipt_validates_the_exact_hashed_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            evidence = repo / "local-lab" / "winui-media-asset-native-workflow"
            original_bytes = manifest.read_bytes()
            forged = json.loads(original_bytes.decode("utf-8"))
            forged["Workflows"][0]["Identity"]["ProcessId"] = 999
            forged_bytes = json.dumps(forged).encode("utf-8")
            original_validate = harness.validate_manifest

            def validate_during_aba(*args: object, **kwargs: object) -> dict[str, object]:
                self.assertEqual(original_bytes, kwargs["manifest_bytes"])
                manifest.write_bytes(forged_bytes)
                try:
                    return original_validate(*args, **kwargs)
                finally:
                    manifest.write_bytes(original_bytes)

            with mock.patch.object(harness, "validate_manifest", side_effect=validate_during_aba):
                summary = harness.validate_owned_manifest_receipt(
                    manifest,
                    evidence_root=evidence,
                    repo_root=repo,
                    expected_harness_run_id=RUN_ID,
                )

            self.assertEqual(101, summary["ownedProcessIdentities"][0]["processId"])

    def test_validate_manifest_rejects_capture_path_swap_during_snapshot_decode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            target = manifest.parent / "media-audio-selected-normal.png"
            flat = manifest.parent / "flat.png"
            write_rgba_png(flat, 1100, 900, flat=True)
            flat_bytes = flat.read_bytes()
            flat.unlink()
            original_decode = harness.native_support.decode_png_rgba_bytes
            swapped = False

            def decode_then_swap(data: bytes, *, name: str) -> object:
                nonlocal swapped
                if name == target.name and not swapped:
                    target.write_bytes(flat_bytes)
                    swapped = True
                return original_decode(data, name=name)

            with mock.patch.object(
                harness.native_support,
                "decode_png_rgba_bytes",
                side_effect=decode_then_swap,
            ):
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "changed during reconciliation"):
                    harness.validate_manifest(manifest, repo)

    def test_cleanup_receipt_recovery_requires_post_build_hash_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            evidence = manifest.parent.parent
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "post-build hash authority"):
                harness.recover_validated_owned_process_receipt(
                    RUN_ID,
                    evidence_root=evidence,
                    repo_root=repo,
                )

    def test_receipt_bound_forced_cleanup_is_never_converted_to_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            evidence = manifest.parent.parent
            summary = harness.validate_owned_manifest_receipt(
                manifest,
                evidence_root=evidence,
                repo_root=repo,
                expected_harness_run_id=RUN_ID,
            )
            owned = harness.owned_process_identity_set(summary)
            first = summary["ownedProcessIdentities"][0]
            census = {
                first["processId"]: {
                    "Id": first["processId"],
                    "ProcessName": "OnslaughtCareerEditor.WinUI",
                    "Path": first["executablePath"],
                    "StartTimeUtcTicks": first["startTimeUtcTicks"],
                }
            }
            with mock.patch.object(harness, "terminate_exact_owned_winui_process") as terminate, mock.patch.object(
                harness,
                "process_census",
                return_value={},
            ), mock.patch.object(harness.time, "sleep"):
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "forced cleanup was required"):
                    harness.remediate_final_process_census(
                        census,
                        owned,
                        receipt_path=manifest,
                        receipt_sha256=summary["_validatedReceiptSha256"],
                        evidence_root=evidence,
                        repo_root=repo,
                    )
            terminate.assert_called_once()

    def test_changed_receipt_denies_survivor_termination_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            manifest = self._write_valid_manifest(repo)
            evidence = manifest.parent.parent
            summary = harness.validate_owned_manifest_receipt(
                manifest,
                evidence_root=evidence,
                repo_root=repo,
                expected_harness_run_id=RUN_ID,
            )
            owned = harness.owned_process_identity_set(summary)
            first = summary["ownedProcessIdentities"][0]
            census = {
                first["processId"]: {
                    "Id": first["processId"],
                    "ProcessName": "OnslaughtCareerEditor.WinUI",
                    "Path": first["executablePath"],
                    "StartTimeUtcTicks": first["startTimeUtcTicks"],
                }
            }
            manifest.write_bytes(manifest.read_bytes() + b" ")
            with mock.patch.object(harness, "terminate_exact_owned_winui_process") as terminate:
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "changed before process cleanup"):
                    harness.remediate_final_process_census(
                        census,
                        owned,
                        receipt_path=manifest,
                        receipt_sha256=summary["_validatedReceiptSha256"],
                        evidence_root=evidence,
                        repo_root=repo,
                    )
            terminate.assert_not_called()

    def test_run_acceptance_binds_post_build_hashes_and_returns_zero_census(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            evidence = repo / "local-lab" / "winui-media-asset-native-workflow"
            runner = repo / "local-lab" / "winui-media-asset-native-workflow-runner"
            built = repo / "OnslaughtCareerEditor.WinUI" / "bin" / "Debug" / "net10.0-windows10.0.19041.0" / "win-x64"
            evidence.mkdir(parents=True)
            runner.mkdir(parents=True)
            for project in harness.BUILD_PROJECT_DIRECTORIES:
                (repo / project).mkdir(parents=True, exist_ok=True)
            captured_environment: dict[str, str] = {}

            def fake_run(command: list[str], timeout: int, env_overrides: dict[str, str] | None = None) -> None:
                if command == harness.WINUI_BUILD_COMMAND:
                    built.mkdir(parents=True, exist_ok=True)
                    for relative_path in APPLICATION_PAYLOAD_PATHS:
                        payload_file = built / Path(relative_path)
                        payload_file.parent.mkdir(parents=True, exist_ok=True)
                        payload_file.write_bytes(f"payload:{relative_path}".encode("utf-8"))
                    (built / "OnslaughtCareerEditor.WinUI.exe").write_bytes(b"fixture-exe")
                    (built / "OnslaughtCareerEditor.WinUI.dll").write_bytes(b"fixture-dll")
                    return
                captured_environment.update(env_overrides or {})
                self._write_valid_manifest(repo)
                trx = Path(command[command.index("--results-directory") + 1]) / "media-asset-native-workflow.trx"
                write_trx(trx)

            with mock.patch.multiple(
                harness,
                REPO_ROOT=repo,
                EVIDENCE_ROOT=evidence,
                RUNNER_ROOT=runner,
                BUILT_APP_ROOT=built,
            ), mock.patch.object(harness.uuid, "uuid4", return_value=mock.Mock(hex=RUN_ID)), mock.patch.object(
                harness,
                "run_command",
                side_effect=fake_run,
            ), mock.patch.object(harness, "process_census", return_value={}), mock.patch.object(
                harness,
                "shutdown_build_servers",
            ), mock.patch.object(harness.time, "sleep"):
                result = harness.run_acceptance()

            self.assertEqual("zero", result["processCensus"])
            self.assertEqual(
                harness.sha256(built / "OnslaughtCareerEditor.WinUI.exe"),
                captured_environment["ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_EXE_SHA256"],
            )
            self.assertEqual(
                harness.sha256(built / "OnslaughtCareerEditor.WinUI.dll"),
                captured_environment["ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_DLL_SHA256"],
            )
            self.assertEqual(
                self._application_payload_sha256(built),
                captured_environment["ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_PAYLOAD_SHA256"],
            )

    @staticmethod
    def _write_valid_manifest(repo: Path) -> Path:
        evidence = repo / "local-lab" / "winui-media-asset-native-workflow" / f"media-asset-x-{RUN_ID}"
        fixture_root = evidence / "fixtures"
        fixture_root.mkdir(parents=True)
        for relative_path, contents in FIXTURE_BYTES.items():
            path = fixture_root / Path(relative_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)

        built = repo / "OnslaughtCareerEditor.WinUI" / "bin" / "Debug" / "net10.0-windows10.0.19041.0" / "win-x64"
        built.mkdir(parents=True, exist_ok=True)
        executable = built / "OnslaughtCareerEditor.WinUI.exe"
        product = built / "OnslaughtCareerEditor.WinUI.dll"
        for relative_path in APPLICATION_PAYLOAD_PATHS:
            payload_file = built / Path(relative_path)
            payload_file.parent.mkdir(parents=True, exist_ok=True)
            payload_file.write_bytes(f"payload:{relative_path}".encode("utf-8"))
        executable.write_bytes(b"fixture-exe")
        product.write_bytes(b"fixture-dll")
        application_payload_hash = MediaAssetNativeWorkflowRunnerTests._application_payload_sha256(built)

        identities = {
            name: {
                "ProcessId": 101 + index,
                "ProcessStartTimeUtc": f"2026-07-15T03:00:0{index + 1}.1234567Z",
                "ExecutablePath": str(executable.resolve()),
                "ExecutableSha256": harness.sha256(executable),
                "ProductAssemblyPath": str(product.resolve()),
                "ProductAssemblySha256": harness.sha256(product),
                "ApplicationPayloadSha256": application_payload_hash,
                "MainWindowHandle": 1001 + index,
                "UiaNativeWindowHandle": 1001 + index,
                "WindowOwnerProcessId": 101 + index,
            }
            for index, name in enumerate(("media-audio", "media-video", "asset-library"))
        }

        captures = []
        for file_name, (workflow, phase, focus_id, width, height, marker_names) in CAPTURE_SPEC.items():
            image = evidence / file_name
            write_rgba_png(image, width, height)
            markers = [
                {
                    "Name": marker,
                    "Bounds": {"X": 40 + index * 18, "Y": 180 + index * 24, "Width": 150, "Height": 48},
                }
                for index, marker in enumerate(marker_names)
            ]
            focus = {
                "AutomationId": focus_id,
                "ProcessId": identities[workflow]["ProcessId"],
                "MainWindowHandle": identities[workflow]["MainWindowHandle"],
                "X": 40,
                "Y": 180,
                "Width": 150,
                "Height": 48,
                "HasKeyboardFocus": True,
            }
            captures.append(
                {
                    "Workflow": workflow,
                    "Phase": phase,
                    "FocusAutomationId": focus_id,
                    "RelativeFileName": file_name,
                    "Sha256": harness.sha256(image),
                    "Width": width,
                    "Height": height,
                    "Identity": identities[workflow],
                    "Markers": markers,
                    "FocusBeforeCapture": focus,
                    "FocusAfterCapture": focus,
                }
            )

        workflows = [
            {
                "Workflow": name,
                "Identity": identities[name],
                "PlaybackModulesLoaded": False,
                "Selections": SELECTIONS[name],
            }
            for name in ("media-audio", "media-video", "asset-library")
        ]
        manifest = {
            "SchemaVersion": 1,
            "HarnessRunId": RUN_ID,
            "InteractionMode": INTERACTION_MODE,
            "Fixture": {
                "RootRelativePath": "fixtures",
                "Files": [
                    {
                        "RelativePath": relative_path,
                        "Length": len(contents),
                        "Sha256": harness.sha256(fixture_root / Path(relative_path)),
                    }
                    for relative_path, contents in FIXTURE_BYTES.items()
                ],
            },
            "Captures": captures,
            "Workflows": workflows,
        }
        path = evidence / "media-asset-acceptance-manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _application_payload_sha256(root: Path) -> str:
        receipt = bytearray()
        for relative_path in APPLICATION_PAYLOAD_PATHS:
            path = root / Path(relative_path)
            digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
            receipt.extend(f"{relative_path}\0{path.stat().st_size}\0{digest}\n".encode("utf-8"))
        return hashlib.sha256(receipt).hexdigest().upper()

    @staticmethod
    def _create_junction(link: Path, target: Path) -> None:
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            text=True,
            capture_output=True,
            timeout=10,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
