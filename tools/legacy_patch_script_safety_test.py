#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import json
import hashlib
import importlib.util
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_SCHEMA_VERSION = "winui-copied-game-profile.v1"
PROFILE_MANIFEST_NAME = "onslaught-profile-manifest.json"
REQUIRED_PROFILE_ENTRIES = [
    "BEA.exe",
    "data",
    "defaultoptions.bea",
    "binkw32.dll",
    "ogg.dll",
    "vorbis.dll",
    "zlib.dll",
]
KNOWN_RETAIL_STEAM_SIZE = 2_506_752


def seed_exe(path: Path, patches: dict[int, bytes], *, size: int | None = None) -> bytes:
    minimum_size = max(offset + len(data) for offset, data in patches.items()) + 0x100
    size = max(size or minimum_size, minimum_size)
    blob = bytearray([0x90] * size)
    for offset, data in patches.items():
        blob[offset : offset + len(data)] = data
    path.write_bytes(blob)
    return bytes(blob)


def run_script(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module_from_path(script: str):
    module_path = REPO_ROOT / script
    module_name = "archive_patch_guard_" + module_path.stem
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load module spec for {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_minimal_profile_manifest(root: Path) -> None:
    manifest = {
        "schemaVersion": PROFILE_SCHEMA_VERSION,
        "targetGameRoot": ".",
        "executablePath": "BEA.exe",
        "patchResult": {
            "requested": True,
            "success": True,
            "patchKeys": [],
        },
    }
    (root / PROFILE_MANIFEST_NAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_profile_manifest(root: Path, exe_path: Path, patch_keys: list[str]) -> None:
    manifest = {
        "schemaVersion": PROFILE_SCHEMA_VERSION,
        "generatedAt": "2026-06-17T00:00:00Z",
        "mutation": True,
        "sourceGameRoot": "selected-game-root",
        "targetGameRoot": ".",
        "executablePath": "BEA.exe",
        "executableSize": exe_path.stat().st_size,
        "executableSha256": sha256_file(exe_path),
        "entries": [
            {
                "name": name,
                "targetPath": name,
                "directory": name == "data",
            }
            for name in REQUIRED_PROFILE_ENTRIES
        ],
        "patchResult": {
            "requested": True,
            "success": True,
            "patchKeys": patch_keys,
        },
        "launchPlan": {
            "executablePath": "BEA.exe",
            "workingDirectory": ".",
            "arguments": [],
        },
    }
    (root / PROFILE_MANIFEST_NAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def assert_refused_without_allowed_root(script_args: list[str], exe_path: Path, original: bytes) -> None:
    result = run_script(script_args)
    if result.returncode == 0:
        raise AssertionError(f"Expected mutation to be refused without --allowed-root.\n{result.stdout}")
    if "--allowed-root" not in result.stdout and "allowed root" not in result.stdout.lower():
        raise AssertionError(f"Expected refusal to mention allowed root.\n{result.stdout}")
    if exe_path.read_bytes() != original:
        raise AssertionError("Script mutated BEA.exe even though no allowed root was supplied.")


def assert_refused_without_manifest(script_args: list[str], exe_path: Path, original: bytes) -> None:
    result = run_script(script_args)
    if result.returncode == 0:
        raise AssertionError(f"Expected mutation to be refused without generated manifest.\n{result.stdout}")
    if "manifest" not in result.stdout.lower():
        raise AssertionError(f"Expected refusal to mention generated manifest.\n{result.stdout}")
    if exe_path.read_bytes() != original:
        raise AssertionError("Script mutated BEA.exe even though no generated manifest was present.")


def assert_refused_with_minimal_manifest(script_args: list[str], exe_path: Path, original: bytes) -> None:
    result = run_script(script_args)
    if result.returncode == 0:
        raise AssertionError(f"Expected mutation to be refused with a minimal/forgeable manifest.\n{result.stdout}")
    if "manifest" not in result.stdout.lower():
        raise AssertionError(f"Expected refusal to mention generated manifest.\n{result.stdout}")
    if exe_path.read_bytes() != original:
        raise AssertionError("Script mutated BEA.exe even though the generated manifest was incomplete.")


def test_display_script_requires_allowed_root() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-display-script-safety-") as temp:
        exe_path = Path(temp) / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
            size=KNOWN_RETAIL_STEAM_SIZE,
        )

        assert_refused_without_allowed_root(
            [
                "patches/patch_display_mode_flow.py",
                "--path",
                str(exe_path),
                "--apply",
                "--windowed-only",
            ],
            exe_path,
            original,
        )

        allowed_root_args = [
            "patches/patch_display_mode_flow.py",
            "--path",
            str(exe_path),
            "--allowed-root",
            temp,
            "--apply",
            "--windowed-only",
        ]
        assert_refused_without_manifest(allowed_root_args, exe_path, original)
        write_minimal_profile_manifest(Path(temp))
        assert_refused_with_minimal_manifest(allowed_root_args, exe_path, original)
        write_profile_manifest(Path(temp), exe_path, ["force_windowed"])

        result = run_script(
            allowed_root_args
        )
        if result.returncode != 0:
            raise AssertionError(f"Expected display script to patch under --allowed-root.\n{result.stdout}")
        patched = exe_path.read_bytes()
        if patched[0x12A644 : 0x12A649] != bytes([0xB8, 0x01, 0x00, 0x00, 0x00]):
            raise AssertionError("Display script did not apply the force-windowed bytes under --allowed-root.")
        if not Path(str(exe_path) + ".original.backup.sha256").is_file():
            raise AssertionError("Display script did not create a backup hash sidecar.")


def test_display_script_rejects_steam_library_shape_even_with_manifest() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-display-steam-shape-") as temp:
        root = Path(temp) / "steamapps" / "common" / "Battle Engine Aquila"
        root.mkdir(parents=True)
        exe_path = root / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
            size=KNOWN_RETAIL_STEAM_SIZE,
        )
        write_profile_manifest(root, exe_path, ["force_windowed"])
        result = run_script(
            [
                "patches/patch_display_mode_flow.py",
                "--path",
                str(exe_path),
                "--allowed-root",
                str(root),
                "--apply",
                "--windowed-only",
            ]
        )
        if result.returncode == 0:
            raise AssertionError(f"Expected Steam-library-shaped root to be refused.\n{result.stdout}")
        if "steamapps/common/battle engine aquila" not in result.stdout.lower():
            raise AssertionError(f"Expected refusal to mention Steam install root shape.\n{result.stdout}")
        if exe_path.read_bytes() != original:
            raise AssertionError("Script mutated BEA.exe under a Steam-library-shaped root.")


def test_goodies_script_requires_allowed_root() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-goodies-script-safety-") as temp:
        exe_path = Path(temp) / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x5D819: bytes([0xF7, 0xD8]),
            },
        )

        assert_refused_without_allowed_root(
            [
                "patches/patch_devmode_goodies_logic_fix.py",
                str(exe_path),
            ],
            exe_path,
            original,
        )

        allowed_root_args = [
            "patches/patch_devmode_goodies_logic_fix.py",
            str(exe_path),
            "--allowed-root",
            temp,
        ]
        assert_refused_without_manifest(allowed_root_args, exe_path, original)
        write_minimal_profile_manifest(Path(temp))
        assert_refused_with_minimal_manifest(allowed_root_args, exe_path, original)
        write_profile_manifest(Path(temp), exe_path, ["devmode_goodies_logic_fix"])

        result = run_script(
            allowed_root_args
        )
        if result.returncode != 0:
            raise AssertionError(f"Expected goodies script to patch under --allowed-root.\n{result.stdout}")
        patched = exe_path.read_bytes()
        if patched[0x5D819 : 0x5D81B] != bytes([0x33, 0xC0]):
            raise AssertionError("Goodies script did not apply the expected bytes under --allowed-root.")
        if not Path(str(exe_path.with_suffix(".exe.backup")) + ".sha256").is_file():
            raise AssertionError("Goodies script did not create a backup hash sidecar.")


def test_catalog_patch_helper_requires_allowed_root_and_manifest() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-catalog-helper-safety-") as temp:
        exe_path = Path(temp) / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
            size=KNOWN_RETAIL_STEAM_SIZE,
        )

        base_args = [
            "tools/apply_bea_catalog_patch.py",
            "--exe",
            str(exe_path),
            "--patch-id",
            "force_windowed",
            "--apply",
        ]
        assert_refused_without_allowed_root(base_args, exe_path, original)

        allowed_root_args = [
            *base_args,
            "--allowed-root",
            temp,
        ]
        assert_refused_without_manifest(allowed_root_args, exe_path, original)
        write_minimal_profile_manifest(Path(temp))
        assert_refused_with_minimal_manifest(allowed_root_args, exe_path, original)
        write_profile_manifest(Path(temp), exe_path, ["force_windowed"])

        result = run_script(allowed_root_args)
        if result.returncode == 0:
            raise AssertionError("Catalog helper accepted a synthetic byte-layout target without explicit test-only opt-in.")
        if "canonical clean specimen" not in result.stdout.lower():
            raise AssertionError(f"Expected canonical specimen refusal.\n{result.stdout}")
        if exe_path.read_bytes() != original:
            raise AssertionError("Catalog helper changed bytes while refusing a non-canonical target.")

        result = run_script([*allowed_root_args, "--allow-byte-layout-only-target"])
        if result.returncode != 0:
            raise AssertionError(f"Expected explicit byte-layout test mode to patch the synthetic target.\n{result.stdout}")
        patched = exe_path.read_bytes()
        if patched[0x12A644 : 0x12A649] != bytes([0xB8, 0x01, 0x00, 0x00, 0x00]):
            raise AssertionError("Catalog helper did not apply the force-windowed bytes under --allowed-root.")
        if not Path(str(exe_path) + ".original.backup.sha256").is_file():
            raise AssertionError("Catalog helper did not create a backup hash sidecar.")


def test_catalog_patch_helper_rejects_untrusted_catalog_for_apply() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-catalog-helper-untrusted-") as temp:
        root = Path(temp)
        exe_path = root / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
        )
        write_profile_manifest(root, exe_path, ["force_windowed"])

        catalog = json.loads((REPO_ROOT / "patches" / "catalog" / "patches.v2.json").read_text(encoding="utf-8"))
        for row in catalog["patches"]:
            if row.get("id") == "force_windowed":
                row["patched_bytes"] = "90 90 90 90 90"
                break
        forged_catalog = root / "forged-patches.v2.json"
        forged_catalog.write_text(json.dumps(catalog, indent=2), encoding="utf-8")

        result = run_script(
            [
                "tools/apply_bea_catalog_patch.py",
                "--exe",
                str(exe_path),
                "--patch-id",
                "force_windowed",
                "--apply",
                "--allowed-root",
                str(root),
                "--catalog",
                str(forged_catalog),
            ]
        )
        if result.returncode == 0:
            raise AssertionError(f"Expected forged catalog to be refused.\n{result.stdout}")
        if "supported patch catalog hash" not in result.stdout.lower():
            raise AssertionError(f"Expected refusal to mention supported catalog hash.\n{result.stdout}")
        if exe_path.read_bytes() != original:
            raise AssertionError("Catalog helper mutated BEA.exe with an untrusted catalog.")


def test_catalog_patch_helper_rejects_unrelated_drift_with_verified_backup() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-catalog-helper-backup-drift-") as temp:
        root = Path(temp)
        exe_path = root / "BEA.exe"
        seed_exe(
            exe_path,
            {
                0x129696: bytes([0xCC]),
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
            size=KNOWN_RETAIL_STEAM_SIZE,
        )
        write_profile_manifest(root, exe_path, ["force_windowed", "resolution_gate"])

        common_args = [
            "tools/apply_bea_catalog_patch.py",
            "--exe",
            str(exe_path),
            "--apply",
            "--allowed-root",
            str(root),
            "--allow-byte-layout-only-target",
        ]
        first = run_script([*common_args, "--patch-id", "force_windowed"])
        if first.returncode != 0:
            raise AssertionError(f"Expected first catalog mutation to create a verified backup.\n{first.stdout}")

        drifted = bytearray(exe_path.read_bytes())
        drifted[0x20] = 0x42
        exe_path.write_bytes(drifted)
        write_profile_manifest(root, exe_path, ["force_windowed", "resolution_gate"])

        second = run_script([*common_args, "--patch-id", "resolution_gate"])
        if second.returncode == 0:
            raise AssertionError("Catalog helper accepted unrelated executable drift beside a verified backup.")
        if "outside known catalog patch spans" not in second.stdout.lower():
            raise AssertionError(f"Expected unrelated-drift refusal.\n{second.stdout}")
        if exe_path.read_bytes() != bytes(drifted):
            raise AssertionError("Catalog helper changed bytes while refusing unrelated executable drift.")


def test_catalog_patch_helper_rejects_preexisting_backup_hash_link() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-catalog-helper-sidecar-link-") as temp:
        root = Path(temp)
        exe_path = root / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
            size=KNOWN_RETAIL_STEAM_SIZE,
        )
        write_profile_manifest(root, exe_path, ["force_windowed"])

        sentinel = root / "sentinel.txt"
        sentinel.write_text("do not overwrite", encoding="utf-8")
        hash_path = Path(str(exe_path) + ".original.backup.sha256")
        os.link(sentinel, hash_path)

        result = run_script(
            [
                "tools/apply_bea_catalog_patch.py",
                "--exe",
                str(exe_path),
                "--patch-id",
                "force_windowed",
                "--apply",
                "--allowed-root",
                str(root),
                "--allow-byte-layout-only-target",
            ]
        )
        if result.returncode == 0:
            raise AssertionError("Catalog helper accepted a pre-existing hardlinked backup hash sidecar.")
        if "backup hash sidecar" not in result.stdout.lower():
            raise AssertionError(f"Expected sidecar-link refusal.\n{result.stdout}")
        if sentinel.read_text(encoding="utf-8") != "do not overwrite":
            raise AssertionError("Catalog helper overwrote the hardlink source through the backup hash sidecar.")
        if exe_path.read_bytes() != original:
            raise AssertionError("Catalog helper mutated BEA.exe while refusing the backup hash sidecar.")


def test_catalog_patch_helper_manifest_patch_ids_are_case_insensitive() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-catalog-helper-manifest-case-") as temp:
        root = Path(temp)
        exe_path = root / "BEA.exe"
        seed_exe(
            exe_path,
            {
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
            size=KNOWN_RETAIL_STEAM_SIZE,
        )
        write_profile_manifest(root, exe_path, ["FORCE_WINDOWED"])

        result = run_script(
            [
                "tools/apply_bea_catalog_patch.py",
                "--exe",
                str(exe_path),
                "--patch-id",
                "force_windowed",
                "--apply",
                "--allowed-root",
                str(root),
                "--allow-byte-layout-only-target",
            ]
        )
        if result.returncode != 0:
            raise AssertionError(f"Catalog helper rejected a case-equivalent manifest patch ID.\n{result.stdout}")


def test_catalog_patch_helper_rejects_steam_library_shape_even_with_manifest() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-catalog-steam-shape-") as temp:
        root = Path(temp) / "steamapps" / "common" / "Battle Engine Aquila"
        root.mkdir(parents=True)
        exe_path = root / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x12A644: bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
            },
        )
        write_profile_manifest(root, exe_path, ["force_windowed"])
        result = run_script(
            [
                "tools/apply_bea_catalog_patch.py",
                "--exe",
                str(exe_path),
                "--patch-id",
                "force_windowed",
                "--apply",
                "--allowed-root",
                str(root),
            ]
        )
        if result.returncode == 0:
            raise AssertionError(f"Expected Steam-library-shaped root to be refused.\n{result.stdout}")
        if "steamapps/common/battle engine aquila" not in result.stdout.lower():
            raise AssertionError(f"Expected refusal to mention Steam install root shape.\n{result.stdout}")
        if exe_path.read_bytes() != original:
            raise AssertionError("Catalog helper mutated BEA.exe under a Steam-library-shaped root.")


def test_archival_cheat_patch_scripts_are_disabled() -> None:
    with tempfile.TemporaryDirectory(prefix="onslaught-archive-patch-disabled-") as temp:
        exe_path = Path(temp) / "BEA.exe"
        original = seed_exe(
            exe_path,
            {
                0x65490: bytes([0xA1, 0xF4, 0x2D, 0x66, 0x00, 0x81, 0xEC, 0x00, 0x01, 0x00, 0x00]),
                0x654A0: bytes([0x75, 0x7A]),
            },
        )
        for script in (
            "patches/archive/patch_ischeatactive_always_true_BROKEN.py",
            "patches/archive/patch_ischeatactive_return_path_bypass.py",
        ):
            result = run_script([script, str(exe_path)])
            if result.returncode == 0:
                raise AssertionError(f"Expected archival script to be disabled: {script}\n{result.stdout}")
            if "disabled" not in result.stdout.lower():
                raise AssertionError(f"Expected archival script refusal to mention disabled: {script}\n{result.stdout}")
            if exe_path.read_bytes() != original:
                raise AssertionError(f"Archival script mutated BEA.exe despite disabled guard: {script}")

            module = load_module_from_path(script)
            for function_name in ("apply_patch", "restore_backup"):
                try:
                    getattr(module, function_name)(exe_path)
                except RuntimeError as ex:
                    if "disabled" not in str(ex).lower():
                        raise AssertionError(
                            f"Expected disabled RuntimeError from {script}::{function_name}; got {ex}"
                        ) from ex
                else:
                    raise AssertionError(f"{script}::{function_name} did not raise the disabled guard.")
                if exe_path.read_bytes() != original:
                    raise AssertionError(f"{script}::{function_name} mutated BEA.exe despite disabled guard.")


def main() -> int:
    test_display_script_requires_allowed_root()
    test_display_script_rejects_steam_library_shape_even_with_manifest()
    test_goodies_script_requires_allowed_root()
    test_catalog_patch_helper_requires_allowed_root_and_manifest()
    test_catalog_patch_helper_rejects_untrusted_catalog_for_apply()
    test_catalog_patch_helper_rejects_unrelated_drift_with_verified_backup()
    test_catalog_patch_helper_rejects_preexisting_backup_hash_link()
    test_catalog_patch_helper_manifest_patch_ids_are_case_insensitive()
    test_catalog_patch_helper_rejects_steam_library_shape_even_with_manifest()
    test_archival_cheat_patch_scripts_are_disabled()
    print("legacy patch script safety checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
