from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PATCH_ID = "pause_o_scan_initializer_experiment"
EXPECTED_HASH = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_SIZE = 2_506_752
EXPECTED_OFFSET = "0x1144CD"
EXPECTED_ORIGINAL = "01"
EXPECTED_PATCHED = "18"
EXPECTED_PROOF = "experimental_copied_runtime_cdb_ordered_o_window_proof"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_catalog(root: Path) -> dict:
    path = root / "patches" / "catalog" / "patches.v2.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _find_row(catalog: dict) -> dict:
    rows = [row for row in catalog.get("patches", []) if row.get("id") == PATCH_ID]
    if len(rows) != 1:
        raise AssertionError(f"expected exactly one {PATCH_ID} row, found {len(rows)}")
    return rows[0]


def _assert_row(row: dict, root: Path) -> None:
    assert row["title"] == "Experimental: O scan for default pause initializer"
    assert row["track"] == "experimental"
    assert row["target_binary_hashes"] == [EXPECTED_HASH]
    assert row["target_binary_size"] == EXPECTED_SIZE
    assert row["file_offset"] == EXPECTED_OFFSET
    assert row["expected_original_bytes"] == EXPECTED_ORIGINAL
    assert row["patched_bytes"] == EXPECTED_PATCHED
    assert row["optional"] is True
    assert row["dependencies"] == []
    assert row["conflicts"] == []
    assert row["exclusive_group"] == ""
    assert row["proof_level"] == EXPECTED_PROOF
    assert row["selectability"] == "experimental_visible"
    assert row["preset_eligibility"] == ["custom"]
    assert row["requires_windowed_pair"] is True

    purpose = row.get("purpose", "")
    if "ordered same-window O-query" not in purpose:
        raise AssertionError("purpose must cite the accepted ordered same-window runtime proof")

    evidence_refs = row.get("evidence_refs", [])
    required_refs = {
        "reverse-engineering/binary-analysis/pause-key-default-row-patch.md",
        "release/readiness/winui_pause_o_scan_initializer_runtime_2026-06-18.md",
        "release/readiness/winui_controller_mapping_table_diagnostic_2026-06-18.md",
        "release/readiness/winui_free_camera_pause_context_diagnostic_2026-06-18.md",
        "patches/README.md",
    }
    missing = sorted(required_refs.difference(evidence_refs))
    if missing:
        raise AssertionError(f"missing evidence refs: {missing}")
    for ref in evidence_refs:
        if ref.startswith("reverse-engineering/") or ref.startswith("release/") or ref.startswith("patches/"):
            if not (root / ref).exists():
                raise AssertionError(f"evidence ref does not exist: {ref}")


def _assert_no_preset_inclusion(root: Path) -> None:
    source = (root / "OnslaughtCareerEditor.AppCore" / "BinaryPatchPlanBuilder.cs").read_text(encoding="utf-8")
    forbidden_blocks = [
        "s_windowedCompatibilityKeys",
        "s_recommendedSafeCopyKeys",
        "s_enhancedPreviewKeys",
    ]
    for block_name in forbidden_blocks:
        block_start = source.find(block_name)
        if block_start < 0:
            raise AssertionError(f"missing preset block {block_name}")
        block_end = source.find("};", block_start)
        block = source[block_start:block_end]
        if PATCH_ID in block:
            raise AssertionError(f"{PATCH_ID} must not be included in {block_name}")


def _assert_clean_exe(clean_exe: Path) -> None:
    data = clean_exe.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_HASH:
        raise AssertionError(f"clean exe hash mismatch: {digest}")
    if len(data) != EXPECTED_SIZE:
        raise AssertionError(f"clean exe size mismatch: {len(data)}")
    offset = int(EXPECTED_OFFSET, 16)
    if data[offset : offset + 1].hex().upper() != EXPECTED_ORIGINAL:
        raise AssertionError(f"clean exe byte mismatch at {EXPECTED_OFFSET}")
    context = data[offset - 3 : offset + 10].hex(" ").upper()
    expected_context = "6A 00 6A 01 6A 08 6A 38 6A 00 B9 18 97"
    if context != expected_context:
        raise AssertionError(f"clean exe context mismatch: {context}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate the catalog row and repo evidence refs.")
    parser.add_argument("--clean-exe", type=Path, help="Optional clean BEA.exe specimen to byte-check.")
    args = parser.parse_args()

    if not args.check:
        parser.error("--check is required")

    root = _repo_root()
    row = _find_row(_load_catalog(root))
    _assert_row(row, root)
    _assert_no_preset_inclusion(root)
    if args.clean_exe:
        _assert_clean_exe(args.clean_exe)

    print(
        json.dumps(
            {
                "patchId": PATCH_ID,
                "fileOffset": EXPECTED_OFFSET,
                "expectedOriginalBytes": EXPECTED_ORIGINAL,
                "patchedBytes": EXPECTED_PATCHED,
                "proofLevel": EXPECTED_PROOF,
                "status": "PASS",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
