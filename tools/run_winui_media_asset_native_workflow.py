#!/usr/bin/env python3
"""Run fail-closed native WinUI Media and Asset Library acceptance.

The runner builds only the repository Debug/win-x64 WinUI app, executes one
explicit generated-fixture UIA test, independently reconciles its native
screenshots and semantic receipts, and requires zero relevant processes before
and after. It never launches BEA, initializes playback, or opens Explorer.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import struct
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import winui_native_acceptance_support as native_support


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = REPO_ROOT / "local-lab" / "winui-media-asset-native-workflow"
RUNNER_ROOT = REPO_ROOT / "local-lab" / "winui-media-asset-native-workflow-runner"
TEST_METHOD_NAME = "MediaAndAssetLibrary_PublishDeterministicNativeEvidence"
TEST_FQN = f"OnslaughtCareerEditor.UiTests.WinUiMediaAssetNativeWorkflowTests.{TEST_METHOD_NAME}"
BUILT_APP_ROOT = (
    REPO_ROOT
    / "OnslaughtCareerEditor.WinUI"
    / "bin"
    / "Debug"
    / "net10.0-windows10.0.19041.0"
    / "win-x64"
)
WINUI_BUILD_COMMAND = [
    "dotnet",
    "build",
    r".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj",
    "--nologo",
    "--configuration",
    "Debug",
    "--runtime",
    "win-x64",
]
INTERACTION_MODE = (
    "UIA Value/SelectionItem/ScrollItem/Scroll/Focus/Invoke; no keyboard, pointer, "
    "playback, reveal, browse, clipboard, export, or package actions"
)
DOTNET_TICKS_PER_SECOND = 10_000_000
EMPTY_SHA256 = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
MAX_MANIFEST_BYTES = 4 * 1024 * 1024

NativeAcceptanceError = native_support.NativeAcceptanceError
HarnessError = NativeAcceptanceError
require = native_support.require
sha256 = native_support.sha256
normalized = native_support.normalized
png_dimensions = native_support.png_dimensions


EXPECTED_FIXTURE_FILES: dict[str, tuple[int, str]] = {
    "asset-bundle/asset_catalog/catalog.json": (
        1913,
        "9BD4EE0A183E26370ADC351C1D7142A41EF8F6F9D4BF3F9FCF01A6236998F71F",
    ),
    "asset-bundle/exports/body00_binary.fbx": (
        509,
        "32D49C79250D425DABCD7C19B8D2411E20DA1DEF1F9BBA2D411A1785A73AB2CC",
    ),
    "asset-bundle/exports/fixture_mesh_binary.fbx": (
        509,
        "32D49C79250D425DABCD7C19B8D2411E20DA1DEF1F9BBA2D411A1785A73AB2CC",
    ),
    "asset-bundle/exports/fixture_texture.png": (
        158,
        "9546C1B8EAFD42B9074729F1275E69EA6763ADDA20AEDDCFE2BEC156E79CEA53",
    ),
    "media-game/BEA.exe": (0, EMPTY_SHA256),
    "media-game/data/Music/battle_theme (Master).ogg": (0, EMPTY_SHA256),
    "media-game/data/sounds/english/MessageBox/110_arrival.ogg": (0, EMPTY_SHA256),
    "media-game/data/sounds/english/MessageBox/HEALTH_low.ogg": (0, EMPTY_SHA256),
    "media-game/data/sounds/english/MessageBox/TUTORIAL_intro.ogg": (0, EMPTY_SHA256),
    "media-game/data/video/OpeningFMV.vid": (0, EMPTY_SHA256),
    "media-game/data/video/UsTheMovie.vid": (0, EMPTY_SHA256),
    "media-game/data/video/briefings/PC_101_exact.vid": (0, EMPTY_SHA256),
    "media-game/data/video/cutscenes/02.vid": (0, EMPTY_SHA256),
}

EXPECTED_CAPTURES: dict[str, tuple[str, str, str, int, int, tuple[str, ...]]] = {
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

EXPECTED_SELECTIONS: dict[str, list[dict[str, str]]] = {
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
BUILD_PROJECT_DIRECTORIES = (
    "OnslaughtCareerEditor.AppCore",
    "OnslaughtCareerEditor.UiTests",
    "OnslaughtCareerEditor.WinUI",
)


def validate_trx(path: Path) -> dict[str, int]:
    return native_support.validate_exact_trx(path, TEST_METHOD_NAME, "native Media/Asset")


def dotnet_utc_timestamp_ticks(value: Any) -> int:
    require(isinstance(value, str), "native Media/Asset process start UTC timestamp is invalid")
    match = re.fullmatch(
        r"(?P<base>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
        r"(?:\.(?P<fraction>\d{1,7}))?"
        r"(?P<offset>Z|[+-]\d{2}:\d{2})",
        value,
    )
    require(match is not None, "native Media/Asset process start UTC timestamp is invalid")
    offset = "+00:00" if match.group("offset") == "Z" else match.group("offset")
    try:
        parsed = datetime.fromisoformat(match.group("base") + offset).astimezone(timezone.utc)
    except ValueError as exc:
        raise NativeAcceptanceError("native Media/Asset process start UTC timestamp is invalid") from exc
    whole_seconds = (
        (parsed.toordinal() - 1) * 86_400
        + parsed.hour * 3_600
        + parsed.minute * 60
        + parsed.second
    )
    fractional_ticks = int((match.group("fraction") or "0").ljust(7, "0"))
    return whole_seconds * DOTNET_TICKS_PER_SECOND + fractional_ticks


def validate_catalog_fixture(path: Path) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NativeAcceptanceError("generated Asset catalog is malformed") from exc
    require(isinstance(payload, dict), "generated Asset catalog must be an object")
    require(payload.get("schema_version") == 2, "generated Asset catalog schema changed")
    require(payload.get("path_contract") == "bundle-root-relative", "generated Asset catalog path contract changed")
    require(
        payload.get("summary")
        == {
            "texture_catalog_entries": 1,
            "loose_mesh_catalog_entries": 1,
            "embedded_mesh_catalog_entries": 1,
            "video_catalog_entries": 0,
            "language_catalog_entries": 0,
            "goodie_catalog_entries": 1,
            "total_catalog_entries": 4,
        },
        "generated Asset catalog summary changed",
    )
    textures = payload.get("textures")
    loose_meshes = payload.get("loose_meshes")
    embedded_meshes = payload.get("embedded_meshes")
    goodies = payload.get("goodies")
    require(isinstance(textures, list) and len(textures) == 1, "generated Asset texture catalog changed")
    require(isinstance(loose_meshes, list) and len(loose_meshes) == 1, "generated Asset loose-mesh catalog changed")
    require(isinstance(embedded_meshes, list) and len(embedded_meshes) == 1, "generated Asset embedded-mesh catalog changed")
    require(isinstance(goodies, list) and len(goodies) == 1, "generated Asset goodie catalog changed")
    texture = textures[0]
    mesh = loose_meshes[0]
    embedded = embedded_meshes[0]
    goodie = goodies[0]
    require(
        isinstance(texture, dict)
        and texture.get("catalog_id") == "texture:fixture/texture_one.tga"
        and texture.get("canonical_ref") == "fixture/texture_one.tga"
        and texture.get("export_png_paths") == ["exports/fixture_texture.png"]
        and texture.get("source_aya_count") == 1
        and texture.get("export_png_count") == 1
        and texture.get("packed_text_ref_count") == 1,
        "generated Asset texture record changed",
    )
    require(
        isinstance(mesh, dict)
        and mesh.get("catalog_id") == "mesh:fixture_mesh.msh"
        and mesh.get("canonical_ref") == "fixture_mesh.msh"
        and mesh.get("export_fbx_paths") == ["exports/fixture_mesh_binary.fbx"]
        and mesh.get("source_aya_count") == 1
        and mesh.get("export_fbx_count") == 1
        and mesh.get("packed_reference_count") == 1,
        "generated Asset loose-mesh record changed",
    )
    require(
        isinstance(embedded, dict)
        and embedded.get("catalog_id") == "embedded_mesh:fixture/body00"
        and embedded.get("export_fbx_path") == "exports/body00_binary.fbx",
        "generated Asset embedded-mesh record changed",
    )
    require(
        isinstance(goodie, dict)
        and goodie.get("catalog_id") == "goodie:008"
        and goodie.get("index") == 8
        and goodie.get("texture_refs") == ["fixture/texture_one.tga"]
        and goodie.get("mesh_refs") == ["fixture_mesh.msh"],
        "generated Asset goodie record changed",
    )
    require(payload.get("videos") == [] and payload.get("language_rows") == [], "generated Asset empty catalog families changed")


def _fbx_array_property(data: bytes, node_name: bytes, property_type: bytes, element_format: str) -> tuple[Any, ...]:
    name_position = data.find(node_name)
    require(name_position >= 13, f"generated FBX lacks {node_name.decode('ascii')} node")
    header_position = name_position - 13
    end_offset, property_count, property_length = struct.unpack_from("<III", data, header_position)
    name_length = data[header_position + 12]
    require(
        name_length == len(node_name)
        and data[name_position : name_position + name_length] == node_name
        and end_offset <= len(data)
        and property_count == 1,
        f"generated FBX {node_name.decode('ascii')} node header changed",
    )
    property_position = name_position + name_length
    require(data[property_position : property_position + 1] == property_type, f"generated FBX {node_name.decode('ascii')} property type changed")
    count, encoding, encoded_length = struct.unpack_from("<III", data, property_position + 1)
    element_size = struct.calcsize(element_format)
    require(
        encoding == 0
        and encoded_length == count * element_size
        and property_length == 13 + encoded_length
        and property_position + 13 + encoded_length <= end_offset,
        f"generated FBX {node_name.decode('ascii')} array encoding changed",
    )
    return struct.unpack_from(f"<{count}{element_format}", data, property_position + 13)


def validate_fbx_fixture(path: Path) -> None:
    data = path.read_bytes()
    require(data.startswith(b"Kaydara FBX Binary  \x00\x1a\x00"), "generated FBX binary header changed")
    require(len(data) >= 27 and struct.unpack_from("<I", data, 23)[0] == 7400, "generated FBX version changed")
    vertices = _fbx_array_property(data, b"Vertices", b"d", "d")
    indices = _fbx_array_property(data, b"PolygonVertexIndex", b"i", "i")
    require(vertices == (0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0), "generated FBX triangle vertices changed")
    require(indices == (0, 1, -3), "generated FBX triangle polygon indices changed")
    require(b"texture_one.tga" in data, "generated FBX texture reference changed")


def validate_fixture_texture_png(path: Path) -> None:
    image = native_support.decode_png_rgba(path)
    require((image.width, image.height) == (8, 8), "generated fixture texture PNG dimensions changed")
    colors = {image.pixel(x, y)[:3] for y in range(image.height) for x in range(image.width)}
    luminances = {(red * 299 + green * 587 + blue * 114) // 1000 for red, green, blue in colors}
    require(len(colors) >= 4 and max(luminances) - min(luminances) >= 40, "generated fixture texture PNG contrast changed")


def _built_app_root(repo_root: Path) -> Path:
    return (
        repo_root
        / "OnslaughtCareerEditor.WinUI"
        / "bin"
        / "Debug"
        / "net10.0-windows10.0.19041.0"
        / "win-x64"
    )


def _read_bounded_snapshot(path: Path, *, maximum_bytes: int, label: str) -> bytes:
    size = path.stat().st_size
    require(0 < size <= maximum_bytes, f"{label} exceeds safety limits: {path.name}")
    data = path.read_bytes()
    require(len(data) == size, f"{label} changed while reading: {path.name}")
    return data


def application_payload_sha256(application_root: Path, *, repo_root: Path | None = None) -> str:
    """Hash the exact Toolkit-owned native application payload closure."""
    root = Path(os.path.abspath(application_root))
    require(root.is_dir(), "native Media/Asset application payload root is missing")
    _require_not_reparse_point(root, "native Media/Asset application payload root")
    if repo_root is not None:
        lexical_repo = Path(os.path.abspath(repo_root))
        require(
            os.path.normcase(str(root)) == os.path.normcase(str(_built_app_root(lexical_repo))),
            "native Media/Asset application payload root is not the pinned repo build",
        )
        current = lexical_repo
        for segment in root.relative_to(lexical_repo).parts:
            current /= segment
            require(current.exists(), f"native Media/Asset build path component is missing: {current}")
            _require_not_reparse_point(current, "native Media/Asset build path component")

    receipt = bytearray()
    retained: list[tuple[Path, int, str]] = []
    for relative_path in APPLICATION_PAYLOAD_PATHS:
        current = root
        for segment in relative_path.split("/"):
            current /= segment
            require(current.exists(), f"native Media/Asset application payload is missing: {relative_path}")
            _require_not_reparse_point(current, "native Media/Asset application payload")
        require(current.is_file(), f"native Media/Asset application payload is not a file: {relative_path}")
        require(stat.S_ISREG(os.lstat(current).st_mode), f"native Media/Asset application payload is not regular: {relative_path}")
        length = current.stat().st_size
        digest = sha256(current)
        require(current.stat().st_size == length, f"native Media/Asset application payload changed: {relative_path}")
        receipt.extend(f"{relative_path}\0{length}\0{digest}\n".encode("utf-8"))
        retained.append((current, length, digest))
    for current, length, digest in retained:
        require(
            current.stat().st_size == length and sha256(current) == digest,
            f"native Media/Asset application payload changed during reconciliation: {current.name}",
        )
    return hashlib.sha256(receipt).hexdigest().upper()


def _validate_identity(
    identity: Any,
    repo_root: Path,
    *,
    expected_executable_hash: str | None = None,
    expected_product_hash: str | None = None,
    expected_application_payload_hash: str | None = None,
) -> dict[str, Any]:
    require(isinstance(identity, dict), "native Media/Asset identity must be an object")
    process_id = identity.get("ProcessId")
    require(isinstance(process_id, int) and process_id > 0, "native Media/Asset process ID is invalid")
    start_time_ticks = dotnet_utc_timestamp_ticks(identity.get("ProcessStartTimeUtc"))
    expected_root = _built_app_root(repo_root).resolve()
    executable = expected_root / "OnslaughtCareerEditor.WinUI.exe"
    product = expected_root / "OnslaughtCareerEditor.WinUI.dll"
    require(executable.is_file() and product.is_file(), "native Media/Asset pinned build outputs are missing")
    require(
        normalized(identity.get("ExecutablePath", "")) == normalized(executable)
        and normalized(identity.get("ProductAssemblyPath", "")) == normalized(product),
        "native Media/Asset identity is not bound to the pinned repo build",
    )
    executable_hash = identity.get("ExecutableSha256")
    product_hash = identity.get("ProductAssemblySha256")
    application_payload_hash = identity.get("ApplicationPayloadSha256")
    require(
        isinstance(executable_hash, str)
        and re.fullmatch(r"[0-9A-F]{64}", executable_hash) is not None
        and executable_hash == sha256(executable),
        "native Media/Asset executable hash changed",
    )
    require(
        isinstance(product_hash, str)
        and re.fullmatch(r"[0-9A-F]{64}", product_hash) is not None
        and product_hash == sha256(product),
        "native Media/Asset product hash changed",
    )
    if expected_executable_hash is not None:
        require(executable_hash == expected_executable_hash, "native Media/Asset executable differs from post-build hash")
    if expected_product_hash is not None:
        require(product_hash == expected_product_hash, "native Media/Asset product differs from post-build hash")
    current_payload_hash = application_payload_sha256(expected_root, repo_root=repo_root)
    require(
        isinstance(application_payload_hash, str)
        and re.fullmatch(r"[0-9A-F]{64}", application_payload_hash) is not None
        and application_payload_hash == current_payload_hash,
        "native Media/Asset application payload changed",
    )
    if expected_application_payload_hash is not None:
        require(
            application_payload_hash == expected_application_payload_hash,
            "native Media/Asset application payload differs from post-build hash",
        )
    main_window = identity.get("MainWindowHandle")
    require(
        isinstance(main_window, int)
        and main_window > 0
        and identity.get("UiaNativeWindowHandle") == main_window
        and identity.get("WindowOwnerProcessId") == process_id,
        "native Media/Asset HWND ownership identity changed",
    )
    return {
        "processId": process_id,
        "startTimeUtcTicks": start_time_ticks,
        "executablePath": str(executable),
    }


def resolve_confined(root: Path, relative_value: Any, label: str) -> Path:
    require(isinstance(relative_value, str) and relative_value, f"{label} path must be relative")
    require("\\" not in relative_value, f"{label} path must use normalized separators")
    segments = relative_value.split("/")
    require(all(segment not in {"", ".", ".."} for segment in segments), f"{label} path is not confined")
    relative = Path(*segments)
    require(not relative.is_absolute(), f"{label} path is not confined")
    resolved_root = root.resolve()
    resolved = (resolved_root / relative).resolve()
    require(resolved != resolved_root and resolved_root in resolved.parents, f"{label} path is not confined")
    return resolved


def validate_bounds(bounds: Any, width: int, height: int, label: str) -> tuple[int, int, int, int]:
    require(isinstance(bounds, dict), f"{label} bounds must be an object")
    values = tuple(bounds.get(name) for name in ("X", "Y", "Width", "Height"))
    require(all(isinstance(value, int) for value in values), f"{label} bounds are invalid")
    x, y, bounds_width, bounds_height = values
    require(
        bounds_width > 0
        and bounds_height > 0
        and x >= 0
        and y >= 0
        and x + bounds_width <= width
        and y + bounds_height <= height,
        f"{label} bounds escape the capture",
    )
    return x, y, bounds_width, bounds_height


def validate_focus(
    focus: Any,
    identity: dict[str, Any],
    automation_id: str,
    width: int,
    height: int,
    label: str,
) -> None:
    require(isinstance(focus, dict), f"native Media/Asset focus receipt is missing: {label}")
    require(
        focus.get("AutomationId") == automation_id
        and focus.get("ProcessId") == identity.get("ProcessId")
        and focus.get("MainWindowHandle") == identity.get("MainWindowHandle")
        and focus.get("HasKeyboardFocus") is True,
        f"native Media/Asset focus identity changed: {label}",
    )
    validate_bounds(focus, width, height, f"native Media/Asset focus {label}")


def validate_manifest(
    path: Path,
    repo_root: Path | None = None,
    *,
    expected_harness_run_id: str | None = None,
    expected_executable_hash: str | None = None,
    expected_product_hash: str | None = None,
    expected_application_payload_hash: str | None = None,
    manifest_bytes: bytes | None = None,
) -> dict[str, Any]:
    repo_root = REPO_ROOT if repo_root is None else repo_root
    require(path.is_file(), f"native Media/Asset manifest is missing: {path}")
    evidence_directory = path.parent
    native_support.require_reparse_free_tree(evidence_directory, label="native Media/Asset receipt tree")
    snapshot = (
        _read_bounded_snapshot(path, maximum_bytes=MAX_MANIFEST_BYTES, label="native Media/Asset manifest")
        if manifest_bytes is None
        else manifest_bytes
    )
    require(0 < len(snapshot) <= MAX_MANIFEST_BYTES, "native Media/Asset manifest exceeds safety limits")
    try:
        payload = json.loads(snapshot.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NativeAcceptanceError("native Media/Asset manifest is malformed") from exc
    require(isinstance(payload, dict), "native Media/Asset manifest must be an object")
    require(payload.get("SchemaVersion") == 1, "native Media/Asset manifest schema changed")
    harness_run_id = payload.get("HarnessRunId")
    require(isinstance(harness_run_id, str), "native Media/Asset harness run ID is missing")
    native_support.validate_invocation_id(harness_run_id)
    if expected_harness_run_id is not None:
        require(harness_run_id == expected_harness_run_id, "native Media/Asset manifest belongs to another runner invocation")
    require(payload.get("InteractionMode") == INTERACTION_MODE, "native Media/Asset interaction contract changed")

    fixture = payload.get("Fixture")
    require(isinstance(fixture, dict), "native Media/Asset fixture receipt is missing")
    require(fixture.get("RootRelativePath") == "fixtures", "native Media/Asset fixture root is not exact")
    fixture_root = resolve_confined(evidence_directory, fixture.get("RootRelativePath"), "fixture root")
    require(fixture_root.is_dir(), "native Media/Asset fixture root is missing")
    native_support.require_reparse_free_tree(fixture_root, label="native Media/Asset fixture")
    receipts = fixture.get("Files")
    require(isinstance(receipts, list) and len(receipts) == 13, "native Media/Asset fixture must contain exactly thirteen receipts")
    require(
        [receipt.get("RelativePath") for receipt in receipts if isinstance(receipt, dict)]
        == list(EXPECTED_FIXTURE_FILES),
        "native Media/Asset canonical fixture receipt order changed",
    )
    actual_fixture_files = sorted(
        path.relative_to(fixture_root).as_posix()
        for path in fixture_root.rglob("*")
        if path.is_file()
    )
    require(actual_fixture_files == sorted(EXPECTED_FIXTURE_FILES), "native Media/Asset fixture file inventory is not exact")
    for receipt, (relative_path, (expected_length, expected_hash)) in zip(receipts, EXPECTED_FIXTURE_FILES.items(), strict=True):
        require(
            isinstance(receipt, dict)
            and receipt.get("RelativePath") == relative_path
            and receipt.get("Length") == expected_length
            and receipt.get("Sha256") == expected_hash,
            f"native Media/Asset canonical fixture receipt changed: {relative_path}",
        )
        fixture_file = resolve_confined(fixture_root, relative_path, f"fixture {relative_path}")
        require(
            fixture_file.is_file()
            and fixture_file.stat().st_size == expected_length
            and sha256(fixture_file) == expected_hash,
            f"native Media/Asset fixture file changed: {relative_path}",
        )

    validate_catalog_fixture(fixture_root / "asset-bundle" / "asset_catalog" / "catalog.json")
    validate_fbx_fixture(fixture_root / "asset-bundle" / "exports" / "body00_binary.fbx")
    validate_fbx_fixture(fixture_root / "asset-bundle" / "exports" / "fixture_mesh_binary.fbx")
    validate_fixture_texture_png(fixture_root / "asset-bundle" / "exports" / "fixture_texture.png")

    workflows = payload.get("Workflows")
    require(isinstance(workflows, list) and len(workflows) == 3, "native Media/Asset manifest must contain exactly three workflows")
    expected_workflow_names = list(EXPECTED_SELECTIONS)
    require(
        [row.get("Workflow") for row in workflows if isinstance(row, dict)] == expected_workflow_names,
        "native Media/Asset workflow set or order changed",
    )
    workflow_by_name: dict[str, dict[str, Any]] = {}
    owned_process_identities: list[dict[str, Any]] = []
    process_launch_keys: set[tuple[int, int]] = set()
    for workflow in workflows:
        require(isinstance(workflow, dict), "native Media/Asset workflow receipt must be an object")
        name = workflow["Workflow"]
        identity = workflow.get("Identity")
        owned = _validate_identity(
            identity,
            repo_root,
            expected_executable_hash=expected_executable_hash,
            expected_product_hash=expected_product_hash,
            expected_application_payload_hash=expected_application_payload_hash,
        )
        require(workflow.get("PlaybackModulesLoaded") is False, f"native Media/Asset {name} initialized playback modules")
        require(workflow.get("Selections") == EXPECTED_SELECTIONS[name], f"native Media/Asset {name} selection readback changed")
        process_launch_keys.add((identity["ProcessId"], owned["startTimeUtcTicks"]))
        owned_process_identities.append(owned)
        workflow_by_name[name] = workflow
    require(len(process_launch_keys) == 3, "native Media/Asset workflows must use distinct process launch identities")

    captures = payload.get("Captures")
    require(isinstance(captures, list) and len(captures) == 8, "native Media/Asset manifest must contain exactly eight captures")
    require(
        [capture.get("RelativeFileName") for capture in captures if isinstance(capture, dict)]
        == list(EXPECTED_CAPTURES),
        "native Media/Asset capture file set or order changed",
    )
    for capture in captures:
        require(isinstance(capture, dict), "native Media/Asset capture receipt must be an object")
        file_name = capture["RelativeFileName"]
        workflow, phase, focus_id, width, height, expected_markers = EXPECTED_CAPTURES[file_name]
        require(
            capture.get("Workflow") == workflow
            and capture.get("Phase") == phase
            and capture.get("FocusAutomationId") == focus_id
            and capture.get("Width") == width
            and capture.get("Height") == height,
            f"native Media/Asset capture mapping changed: {file_name}",
        )
        identity = capture.get("Identity")
        require(identity == workflow_by_name[workflow]["Identity"], f"native Media/Asset capture workflow identity changed: {file_name}")
        markers = capture.get("Markers")
        require(isinstance(markers, list), f"native Media/Asset capture markers are missing: {file_name}")
        marker_names = tuple(marker.get("Name") for marker in markers if isinstance(marker, dict))
        require(marker_names == expected_markers and len(markers) == len(expected_markers), f"native Media/Asset marker set changed: {file_name}")
        marker_bounds = [
            validate_bounds(marker.get("Bounds"), width, height, f"native Media/Asset marker {marker.get('Name')} in {file_name}")
            for marker in markers
        ]
        image = resolve_confined(evidence_directory, file_name, f"capture {file_name}")
        require(image.is_file(), f"native Media/Asset capture is missing: {file_name}")
        image_bytes = _read_bounded_snapshot(
            image,
            maximum_bytes=native_support.MAX_PNG_FILE_BYTES,
            label="native Media/Asset capture",
        )
        image_digest = hashlib.sha256(image_bytes).hexdigest().upper()
        require(capture.get("Sha256") == image_digest, f"native Media/Asset capture hash changed: {file_name}")
        decoded_image = native_support.decode_png_rgba_bytes(image_bytes, name=file_name)
        require((decoded_image.width, decoded_image.height) == (width, height), f"native Media/Asset PNG dimensions changed: {file_name}")
        native_support.require_toolkit_visual_evidence_image(
            decoded_image,
            marker_bounds,
            label="native Media/Asset capture",
            name=file_name,
        )
        require(sha256(image) == image_digest, f"native Media/Asset capture changed during reconciliation: {file_name}")
        validate_focus(capture.get("FocusBeforeCapture"), identity, focus_id, width, height, file_name)
        validate_focus(capture.get("FocusAfterCapture"), identity, focus_id, width, height, file_name)

    return {
        "manifest": str(path.resolve()),
        "harnessRunId": harness_run_id,
        "fixtureFileCount": len(receipts),
        "captureCount": len(captures),
        "workflowCount": len(workflows),
        "workflows": sorted(workflow_by_name),
        "ownedProcessIdentities": owned_process_identities,
    }


def process_census() -> dict[int, dict[str, Any]]:
    return native_support.process_census(REPO_ROOT)


def describe_processes(census: dict[int, dict[str, Any]]) -> str:
    return native_support.describe_processes(census)


def run_command(
    command: list[str],
    *,
    timeout: int,
    env_overrides: dict[str, str] | None = None,
) -> None:
    native_support.run_command(command, repo_root=REPO_ROOT, timeout=timeout, env_overrides=env_overrides)


def validate_invocation_id(invocation_id: str) -> None:
    native_support.validate_invocation_id(invocation_id)


def native_test_command(run_root: Path, trx: Path) -> list[str]:
    return [
        "dotnet",
        "test",
        r".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj",
        "--nologo",
        "--configuration",
        "Debug",
        "--runtime",
        "win-x64",
        "--filter",
        f"FullyQualifiedName={TEST_FQN}",
        "--logger",
        f"trx;LogFileName={trx.name}",
        "--results-directory",
        str(run_root),
    ]


def invocation_manifests(invocation_id: str, evidence_root: Path | None = None) -> set[Path]:
    validate_invocation_id(invocation_id)
    evidence_root = EVIDENCE_ROOT if evidence_root is None else evidence_root
    if not evidence_root.exists():
        return set()
    manifest = evidence_root / f"media-asset-x-{invocation_id}" / "media-asset-acceptance-manifest.json"
    return {manifest.absolute()} if manifest.is_file() else set()


def invocation_evidence_directories(invocation_id: str, evidence_root: Path | None = None) -> set[Path]:
    validate_invocation_id(invocation_id)
    evidence_root = EVIDENCE_ROOT if evidence_root is None else evidence_root
    if not evidence_root.exists():
        return set()
    candidates = (
        evidence_root / f"media-asset-x-{invocation_id}",
        evidence_root / f".media-asset-x-{invocation_id}.partial",
    )
    return {path.absolute() for path in candidates if path.is_dir()}


def partial_evidence_directories(evidence_root: Path | None = None) -> list[Path]:
    evidence_root = EVIDENCE_ROOT if evidence_root is None else evidence_root
    if not evidence_root.exists():
        return []
    return sorted(path for path in evidence_root.iterdir() if path.is_dir() and path.name.endswith(".partial"))


def _require_not_reparse_point(path: Path, label: str) -> None:
    if not os.path.lexists(path):
        return
    attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    require(not (attributes & reparse_flag), f"{label} must not be a reparse point: {path}")


def preflight_build_output_roots(repo_root: Path) -> None:
    """Reject pre-existing repo build-output junctions before dotnet can write."""
    lexical_repo = Path(os.path.abspath(repo_root))
    for project_name in BUILD_PROJECT_DIRECTORIES:
        project = lexical_repo / project_name
        require(project.is_dir(), f"native Media/Asset build project is missing: {project_name}")
        _require_not_reparse_point(project, "native Media/Asset build project")
        for output_name in ("bin", "obj"):
            output = project / output_name
            if not os.path.lexists(output):
                continue
            _require_not_reparse_point(output, "native Media/Asset build output root")
            require(output.is_dir(), f"native Media/Asset build output root is not a directory: {output}")
            native_support.require_reparse_free_tree(output, label="native Media/Asset build output")


def _resolve_owned_ignored_root(root: Path, expected_name: str, repo_root: Path) -> Path:
    resolved_repo = repo_root.resolve()
    lexical_local_lab = resolved_repo / "local-lab"
    lexical_expected = lexical_local_lab / expected_name
    require(
        os.path.normcase(os.path.abspath(root)) == os.path.normcase(os.path.abspath(lexical_expected)),
        f"{expected_name} ignored root is not the exact repository-owned path",
    )
    _require_not_reparse_point(lexical_local_lab, "repository local-lab")
    _require_not_reparse_point(lexical_expected, f"{expected_name} ignored root")
    resolved_local_lab = lexical_local_lab.resolve()
    resolved = root.resolve()
    require(
        resolved_local_lab != resolved_repo
        and resolved_repo in resolved_local_lab.parents
        and resolved != resolved_local_lab
        and resolved_repo in resolved.parents
        and resolved_local_lab in resolved.parents,
        f"{expected_name} ignored root escaped repository local-lab: {resolved}",
    )
    return resolved


def verify_evidence_root(
    evidence_root: Path | None = None,
    *,
    repo_root: Path | None = None,
) -> Path:
    evidence_root = EVIDENCE_ROOT if evidence_root is None else evidence_root
    repo_root = REPO_ROOT if repo_root is None else repo_root
    return _resolve_owned_ignored_root(evidence_root, "winui-media-asset-native-workflow", repo_root)


def verify_runner_path(
    path: Path,
    *,
    runner_root: Path | None = None,
    repo_root: Path | None = None,
) -> None:
    runner_root = RUNNER_ROOT if runner_root is None else runner_root
    repo_root = REPO_ROOT if repo_root is None else repo_root
    resolved = path.resolve()
    root = _resolve_owned_ignored_root(runner_root, "winui-media-asset-native-workflow-runner", repo_root)
    _require_not_reparse_point(path, "runner-owned child")
    require(resolved != root and resolved.parent == root, f"runner cleanup path escaped its ignored root: {resolved}")


def verify_owned_evidence_directory(path: Path, evidence_root: Path) -> Path:
    root = evidence_root.absolute()
    child = path.absolute()
    require(child.parent == root, f"Media/Asset evidence path is not a direct owned child: {child}")
    require(root.is_dir() and child.is_dir(), f"Media/Asset evidence receipt is missing: {child}")
    _require_not_reparse_point(root, "Media/Asset evidence root")
    _require_not_reparse_point(child, "Media/Asset evidence child")
    return child


def verify_owned_manifest_path(manifest_path: Path, evidence_root: Path) -> Path:
    manifest = manifest_path.absolute()
    parent = verify_owned_evidence_directory(manifest.parent, evidence_root)
    require(
        manifest.parent == parent and manifest.name == "media-asset-acceptance-manifest.json",
        f"Media/Asset manifest is not canonical: {manifest}",
    )
    require(manifest.is_file(), f"Media/Asset manifest is missing: {manifest}")
    _require_not_reparse_point(manifest, "Media/Asset manifest")
    require(stat.S_ISREG(os.lstat(manifest).st_mode), f"Media/Asset manifest is not a regular file: {manifest}")
    native_support.require_reparse_free_tree(parent, label="Media/Asset receipt tree")
    return manifest


def validate_owned_manifest_receipt(
    manifest_path: Path,
    *,
    evidence_root: Path,
    repo_root: Path,
    expected_harness_run_id: str,
    expected_executable_hash: str | None = None,
    expected_product_hash: str | None = None,
    expected_application_payload_hash: str | None = None,
) -> dict[str, Any]:
    root = verify_evidence_root(evidence_root, repo_root=repo_root)
    manifest = verify_owned_manifest_path(manifest_path, root)
    manifest_bytes = _read_bounded_snapshot(
        manifest,
        maximum_bytes=MAX_MANIFEST_BYTES,
        label="native Media/Asset manifest",
    )
    receipt_sha256 = hashlib.sha256(manifest_bytes).hexdigest().upper()
    summary = validate_manifest(
        manifest,
        repo_root,
        expected_harness_run_id=expected_harness_run_id,
        expected_executable_hash=expected_executable_hash,
        expected_product_hash=expected_product_hash,
        expected_application_payload_hash=expected_application_payload_hash,
        manifest_bytes=manifest_bytes,
    )
    root = verify_evidence_root(evidence_root, repo_root=repo_root)
    verify_owned_manifest_path(manifest, root)
    require(sha256(manifest) == receipt_sha256, "Media/Asset validated receipt hash changed during manifest reconciliation")
    return {**summary, "_validatedReceiptSha256": receipt_sha256}


def verify_validated_receipt_authority(
    receipt_path: Path,
    receipt_sha256: str,
    *,
    evidence_root: Path,
    repo_root: Path,
) -> None:
    root = verify_evidence_root(evidence_root, repo_root=repo_root)
    manifest = verify_owned_manifest_path(receipt_path, root)
    require(sha256(manifest) == receipt_sha256, "Media/Asset validated receipt hash changed before process cleanup")


def remove_failed_invocation_evidence(
    invocation_id: str,
    evidence_root: Path | None = None,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_invocation_id(invocation_id)
    evidence_root = EVIDENCE_ROOT if evidence_root is None else evidence_root
    repo_root = REPO_ROOT if repo_root is None else repo_root
    root = verify_evidence_root(evidence_root, repo_root=repo_root)
    for run_directory in invocation_evidence_directories(invocation_id, root):
        root = verify_evidence_root(evidence_root, repo_root=repo_root)
        run_directory = verify_owned_evidence_directory(run_directory, root)
        require(
            run_directory.name in {
                f"media-asset-x-{invocation_id}",
                f".media-asset-x-{invocation_id}.partial",
            },
            f"refusing to remove unowned failed Media/Asset evidence path: {run_directory}",
        )
        native_support.remove_reparse_free_tree(run_directory, label="Media/Asset invocation evidence")


def select_owned_repo_winui_survivors(
    census: dict[int, dict[str, Any]],
    expected_executable: Path,
    owned_process_identities: set[tuple[int, int, str]],
) -> list[tuple[int, dict[str, Any]]]:
    selected: list[tuple[int, dict[str, Any]]] = []
    for process_id, row in sorted(census.items()):
        if str(row.get("ProcessName", "")).lower() != "onslaughtcareereditor.winui":
            continue
        require(
            row.get("Id") == process_id and normalized(row.get("Path", "")) == normalized(expected_executable),
            f"surviving WinUI process {process_id} is not the exact repo build",
        )
        require(
            isinstance(row.get("StartTimeUtcTicks"), int) and row["StartTimeUtcTicks"] > 0,
            f"surviving WinUI process {process_id} lacks exact start identity",
        )
        identity = (process_id, row["StartTimeUtcTicks"], normalized(row["Path"]))
        require(identity in owned_process_identities, f"surviving WinUI process {process_id} is not receipt-bound")
        selected.append((process_id, row))
    return selected


def terminate_exact_owned_winui_process(process_id: int, row: dict[str, Any], expected_executable: Path) -> None:
    native_support.terminate_owned_process_tree(
        native_support.OwnedProcessIdentity(process_id, row["StartTimeUtcTicks"], expected_executable),
        repo_root=REPO_ROOT,
    )


def remediate_final_process_census(
    census: dict[int, dict[str, Any]],
    owned_process_identities: set[tuple[int, int, str]],
    *,
    receipt_path: Path | None = None,
    receipt_sha256: str | None = None,
    evidence_root: Path | None = None,
    repo_root: Path | None = None,
) -> None:
    evidence_root = EVIDENCE_ROOT if evidence_root is None else evidence_root
    repo_root = REPO_ROOT if repo_root is None else repo_root
    if owned_process_identities:
        require(receipt_path is not None and receipt_sha256 is not None, "owned WinUI cleanup identities lack a validated receipt")
        verify_validated_receipt_authority(
            receipt_path,
            receipt_sha256,
            evidence_root=evidence_root,
            repo_root=repo_root,
        )
    expected_executable = _built_app_root(repo_root) / "OnslaughtCareerEditor.WinUI.exe"
    survivors = select_owned_repo_winui_survivors(census, expected_executable, owned_process_identities)
    termination_errors: list[str] = []
    for process_id, row in survivors:
        try:
            verify_validated_receipt_authority(
                receipt_path,
                receipt_sha256,
                evidence_root=evidence_root,
                repo_root=repo_root,
            )
            terminate_exact_owned_winui_process(process_id, row, expected_executable)
        except Exception as exc:
            termination_errors.append(str(exc))
    if survivors:
        time.sleep(0.25)
    remaining = process_census()
    details = f"; termination errors: {termination_errors}" if termination_errors else ""
    raise NativeAcceptanceError(
        "final relevant-process census was nonzero and forced cleanup was required; "
        f"initial: {describe_processes(census)}; remaining: {describe_processes(remaining)}{details}"
    )


def shutdown_build_servers() -> None:
    native_support.shutdown_build_servers(REPO_ROOT)


def append_cleanup_error(error: Exception | None, phase: str, cleanup_error: Exception) -> NativeAcceptanceError:
    return native_support.append_cleanup_error(error, phase, cleanup_error)


def owned_process_identity_set(summary: dict[str, Any]) -> set[tuple[int, int, str]]:
    return {
        (row["processId"], row["startTimeUtcTicks"], normalized(row["executablePath"]))
        for row in summary["ownedProcessIdentities"]
    }


def recover_validated_owned_process_receipt(
    invocation_id: str,
    *,
    evidence_root: Path | None = None,
    repo_root: Path | None = None,
    expected_executable_hash: str | None = None,
    expected_product_hash: str | None = None,
    expected_application_payload_hash: str | None = None,
) -> tuple[set[tuple[int, int, str]], Path | None, str | None]:
    evidence_root = EVIDENCE_ROOT if evidence_root is None else evidence_root
    repo_root = REPO_ROOT if repo_root is None else repo_root
    require(
        expected_executable_hash is not None
        and expected_product_hash is not None
        and expected_application_payload_hash is not None,
        "post-build hash authority is required to recover Media/Asset cleanup identities",
    )
    root = verify_evidence_root(evidence_root, repo_root=repo_root)
    manifests = invocation_manifests(invocation_id, root)
    if len(manifests) != 1:
        return set(), None, None
    manifest = next(iter(manifests))
    summary = validate_owned_manifest_receipt(
        manifest,
        evidence_root=root,
        repo_root=repo_root,
        expected_harness_run_id=invocation_id,
        expected_executable_hash=expected_executable_hash,
        expected_product_hash=expected_product_hash,
        expected_application_payload_hash=expected_application_payload_hash,
    )
    return owned_process_identity_set(summary), manifest, summary["_validatedReceiptSha256"]


def run_acceptance() -> dict[str, Any]:
    evidence_root = verify_evidence_root()
    baseline = process_census()
    require(not baseline, f"pre-run relevant-process census must be zero, found: {describe_processes(baseline)}")
    partials = partial_evidence_directories()
    require(not partials, f"pre-run Media/Asset evidence contains partial directories: {[path.name for path in partials]}")
    invocation_id = uuid.uuid4().hex
    validate_invocation_id(invocation_id)
    require(not invocation_evidence_directories(invocation_id), "fresh Media/Asset invocation unexpectedly owns evidence")
    run_root = RUNNER_ROOT / f".{invocation_id}.partial"
    verify_runner_path(run_root)
    run_root.mkdir(parents=True, exist_ok=False)
    trx = run_root / "media-asset-native-workflow.trx"
    error: Exception | None = None
    result: dict[str, Any] | None = None
    owned_process_identities: set[tuple[int, int, str]] = set()
    owned_identity_receipt_path: Path | None = None
    owned_identity_receipt_sha256: str | None = None
    expected_executable_hash: str | None = None
    expected_product_hash: str | None = None
    expected_application_payload_hash: str | None = None
    try:
        preflight_build_output_roots(REPO_ROOT)
        run_command(WINUI_BUILD_COMMAND, timeout=180)
        executable = BUILT_APP_ROOT / "OnslaughtCareerEditor.WinUI.exe"
        product_dll = BUILT_APP_ROOT / "OnslaughtCareerEditor.WinUI.dll"
        require(executable.is_file() and product_dll.is_file(), "pinned Debug/win-x64 WinUI build outputs are missing")
        expected_executable_hash = sha256(executable)
        expected_product_hash = sha256(product_dll)
        expected_application_payload_hash = application_payload_sha256(BUILT_APP_ROOT, repo_root=REPO_ROOT)
        run_command(
            native_test_command(run_root, trx),
            timeout=300,
            env_overrides={
                "ONSLAUGHT_MEDIA_ASSET_NATIVE_ACCEPTANCE_RUN_ID": invocation_id,
                "ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_EXE_SHA256": expected_executable_hash,
                "ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_DLL_SHA256": expected_product_hash,
                "ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_PAYLOAD_SHA256": expected_application_payload_hash,
            },
        )
        trx_summary = validate_trx(trx)
        evidence_root = verify_evidence_root()
        manifests = invocation_manifests(invocation_id, evidence_root)
        require(len(manifests) == 1, f"native Media/Asset invocation must publish exactly one manifest, found {len(manifests)}")
        partials = partial_evidence_directories()
        require(not partials, f"native Media/Asset run left partial evidence: {[path.name for path in partials]}")
        manifest_path = next(iter(manifests))
        manifest_summary = validate_owned_manifest_receipt(
            manifest_path,
            evidence_root=evidence_root,
            repo_root=REPO_ROOT,
            expected_harness_run_id=invocation_id,
            expected_executable_hash=expected_executable_hash,
            expected_product_hash=expected_product_hash,
            expected_application_payload_hash=expected_application_payload_hash,
        )
        owned_process_identities = owned_process_identity_set(manifest_summary)
        owned_identity_receipt_path = manifest_path
        owned_identity_receipt_sha256 = manifest_summary.pop("_validatedReceiptSha256")
        time.sleep(0.5)
        post = process_census()
        require(not post, f"post-run relevant-process census must be zero, found: {describe_processes(post)}")
        result = {"trx": trx_summary, **manifest_summary, "processCensus": "zero"}
    except Exception as exc:
        error = exc
    finally:
        try:
            shutdown_build_servers()
        except Exception as cleanup_error:
            error = append_cleanup_error(error, "build-server shutdown", cleanup_error)
        if (
            not owned_process_identities
            and expected_executable_hash is not None
            and expected_product_hash is not None
            and expected_application_payload_hash is not None
        ):
            try:
                owned_process_identities, owned_identity_receipt_path, owned_identity_receipt_sha256 = (
                    recover_validated_owned_process_receipt(
                        invocation_id,
                        expected_executable_hash=expected_executable_hash,
                        expected_product_hash=expected_product_hash,
                        expected_application_payload_hash=expected_application_payload_hash,
                    )
                )
            except Exception:
                pass
        try:
            final_census = process_census()
            if final_census:
                remediate_final_process_census(
                    final_census,
                    owned_process_identities,
                    receipt_path=owned_identity_receipt_path,
                    receipt_sha256=owned_identity_receipt_sha256,
                )
        except Exception as cleanup_error:
            error = append_cleanup_error(error, "final relevant-process census", cleanup_error)
        try:
            if run_root.exists():
                verify_runner_path(run_root)
                native_support.remove_reparse_free_tree(run_root, label="Media/Asset runner scratch")
        except Exception as cleanup_error:
            error = append_cleanup_error(error, "runner-root cleanup", cleanup_error)
        if error is not None:
            try:
                remove_failed_invocation_evidence(invocation_id)
            except Exception as cleanup_error:
                error = append_cleanup_error(error, "owned evidence rollback", cleanup_error)

    if error is not None:
        if isinstance(error, NativeAcceptanceError):
            raise error
        raise NativeAcceptanceError(str(error)) from error
    require(result is not None, "native Media/Asset acceptance produced no result")
    return result


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print("usage: run_winui_media_asset_native_workflow.py", file=sys.stderr)
        return 2
    try:
        result = run_acceptance()
        print("\nWinUI Media/Asset native workflow acceptance: PASS", flush=True)
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
        return 0
    except (NativeAcceptanceError, subprocess.TimeoutExpired, OSError, json.JSONDecodeError) as exc:
        print(f"WinUI Media/Asset native workflow acceptance: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
