#!/usr/bin/env python3
"""Focused tests for the executable validation inventory."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validation_inventory.py"


def load_inventory_module():
    assert SCRIPT.is_file(), "validation_inventory.py must exist"
    spec = importlib.util.spec_from_file_location("validation_inventory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_inventory_module()
    assert hasattr(module, "build_inventory")
    assert hasattr(module, "validate_repository_contracts")

    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp)
        (root / "tools").mkdir()
        (root / "src").mkdir()
        package = {
            "scripts": {
                "check:quick": "npm run test:docs",
                "test:docs": "py -3 tools/docs.py",
                "test:runtime-tooling-safety": (
                    "npm run test:runtime-profile-helper-safety && "
                    "npm run test:runtime-cdb-helper-safety && "
                    "npm run test:runtime-input-helper-safety && "
                    "npm run test:winui-safe-copy-live-runtime-smoke-helper"
                ),
                "test:runtime-profile-helper-safety": "py -3 tools/profile.py",
                "test:runtime-cdb-helper-safety": "py -3 tools/cdb.py",
                "test:runtime-input-helper-safety": "py -3 tools/input.py",
                "test:winui-safe-copy-live-runtime-smoke-helper": "py -3 tools/smoke.py",
                "test:ghidra-wave1": "py -3 tools/wave.py --check",
                "test:winui-copied-profile-runtime": (
                    "npm run test:proof-child && npm run test:runtime-cdb-helper-safety && "
                    "npm run test:runtime-input-helper-safety"
                ),
                "test:proof-child": "py -3 tools/proof.py",
                "broken": "npm run missing-script",
                "alias:a": "echo same",
                "alias:b": "echo same",
            }
        }
        (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
        (root / "ACTIVE.md").write_text("npm run test:docs\n", encoding="utf-8")
        (root / "HISTORY.md").write_text("npm run test:ghidra-wave1\n", encoding="utf-8")
        (root / "src" / "Commands.cs").write_text(
            'const string Command = "npm run test:runtime-cdb-helper-safety";\n',
            encoding="utf-8",
        )
        (root / "tools" / "wave.py").write_text(
            'EXPECTED = "test:ghidra-wave1"\n', encoding="utf-8"
        )

        inventory = module.build_inventory(
            root,
            root / "package.json",
            active_docs=("ACTIVE.md",),
            tracked_paths=(
                "ACTIVE.md",
                "HISTORY.md",
                "src/Commands.cs",
                "tools/wave.py",
            ),
        )
        scripts = {item["name"]: item for item in inventory["scripts"]}

        assert inventory["summary"]["scriptCount"] == 13
        assert inventory["summary"]["edgeCount"] == 8
        assert inventory["summary"]["unknownDependencyCount"] == 1
        assert scripts["broken"]["unknownDependencies"] == ["missing-script"]
        assert scripts["test:ghidra-wave1"]["family"] == "historical-proof"
        assert scripts["test:proof-child"]["family"] == "runtime-proof"
        assert scripts["test:proof-child"]["status"] == "historical-retained"
        assert scripts["test:docs"]["activeDocReferences"] == ["ACTIVE.md:1"]
        assert scripts["test:ghidra-wave1"]["historicalDocReferenceCount"] == 1
        assert scripts["test:runtime-cdb-helper-safety"]["sourceReferences"] == [
            "src/Commands.cs:1"
        ]
        assert scripts["test:ghidra-wave1"]["selfBinding"] is True
        assert scripts["alias:a"]["duplicateCommandPeers"] == ["alias:b"]
        assert scripts["check:quick"]["npmDependencies"] == ["test:docs"]

        bad_package = json.loads(json.dumps(package))
        bad_package["scripts"]["check:quick"] = (
            "npm run test:winui-copied-profile-runtime"
        )
        (root / "package.json").write_text(json.dumps(bad_package), encoding="utf-8")
        bad_inventory = module.build_inventory(
            root,
            root / "package.json",
            active_docs=("ACTIVE.md",),
            tracked_paths=("ACTIVE.md",),
        )
        forbidden = module.quick_profile_forbidden(bad_inventory)
        assert "test:proof-child" in forbidden
        assert "test:winui-copied-profile-runtime" in forbidden

    print("Validation inventory tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
