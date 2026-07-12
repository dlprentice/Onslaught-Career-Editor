#!/usr/bin/env python3
"""Lock the small active validation profiles and retained safety commands."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from validation_inventory import build_inventory


ROOT = Path(__file__).resolve().parents[1]
NPM_RUN = re.compile(r"npm\s+run\s+([A-Za-z0-9:_-]+)")
REMOVED_ALIASES = {
    "test:winui-copied-game-preflight",
    "test:winui-copied-game-runtime",
    "test:winui-copied-game-music-replacement",
}
RUNTIME_HELPERS = {
    "test:runtime-profile-helper-safety",
    "test:runtime-cdb-helper-safety",
    "test:winui-safe-copy-live-runtime-smoke-helper",
}
READINESS_COMMANDS = {
    "test:winui-original-binary-second-host-live-readiness",
    "test:winui-original-binary-second-host-live-run-kit",
    "test:winui-original-binary-second-host-command-source",
    "test:winui-original-binary-host-join-enablement",
}


def dependencies(command: str) -> set[str]:
    return set(NPM_RUN.findall(command))


def main() -> int:
    root_scripts = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
    public_scripts = json.loads(
        (ROOT / "release" / "readiness" / "public_package.json").read_text(encoding="utf-8")
    )["scripts"]

    quick = dependencies(root_scripts["check:quick"])
    assert quick == {
        "test:validation-inventory",
        "test:docsync",
        "test:doc-commands",
        "test:md-links:public-core",
        "test:generated-output-safety",
        "test:winui-primary-lane",
        "test:rebuild",
    }
    assert not {"build:winui", "test:appcore", "test:winui"} & quick
    assert not {"test:hard-payload-safety", "test:repo-hygiene"} & quick

    public_quick = dependencies(public_scripts["check:quick"])
    assert "test:winui-primary-lane" in public_quick
    assert not {"build:winui", "test:appcore", "test:winui"} & public_quick

    assert dependencies(root_scripts["test:runtime-tooling-safety"]) == RUNTIME_HELPERS
    proof_sweep = dependencies(root_scripts["test:winui-copied-profile-runtime"])
    assert RUNTIME_HELPERS <= proof_sweep

    allowlist = root_scripts["test:public-allowlist"]
    assert allowlist.count("public_allowlist_safety_check.py") == 2
    assert "--self-test" in allowlist and "--include-submodules" in allowlist
    assert dependencies(allowlist) == {"test:public-primary-migration-inventory"}

    assert REMOVED_ALIASES.isdisjoint(root_scripts)
    for alias in sorted(REMOVED_ALIASES):
        result = subprocess.run(
            ["git", "grep", "-I", "-n", "-F", f"npm run {alias}", "--"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert result.returncode == 1, result.stdout
    assert "--scope active" in root_scripts["test:doc-commands"]
    assert "--scope all" in root_scripts["test:doc-commands-all"]
    assert "--scope public-core" in root_scripts["test:md-links:public-core"]
    assert "--check-only" in root_scripts["test:md-links:public-core"]

    readiness_source = (
        ROOT / "OnslaughtCareerEditor.AppCore" / "OnlineMultiplayerReadinessService.cs"
    ).read_text(encoding="utf-8")
    emitted = set(NPM_RUN.findall(readiness_source))
    assert READINESS_COMMANDS <= emitted
    assert READINESS_COMMANDS <= set(root_scripts)
    inventory = build_inventory(ROOT, ROOT / "package.json")
    inventory_scripts = {item["name"]: item for item in inventory["scripts"]}
    for command in READINESS_COMMANDS:
        assert inventory_scripts[command]["status"] == "active-runtime-proof"

    print("Validation profile tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
