#!/usr/bin/env python3
"""Tests for active versus historical documented-command validation."""

from __future__ import annotations

import tempfile
from pathlib import Path

import npm_script_doc_check as checker
import md_link_check


def main() -> int:
    assert hasattr(checker, "markdown_files_for_scope")
    assert hasattr(checker, "documented_command_errors")
    assert "LOCAL_LAB_OVERLAY.md" in checker.ACTIVE_MARKDOWN_FILES
    assert (
        "roadmap/original-binary-online-multiplayer-feasibility.md"
        in checker.ACTIVE_MARKDOWN_FILES
    )
    assert tuple(md_link_check.PUBLIC_CORE_MARKDOWN) == tuple(checker.ACTIVE_MARKDOWN_FILES)

    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp)
        (root / "release" / "readiness").mkdir(parents=True)
        (root / "AGENTS.md").write_text("npm run known\n", encoding="utf-8")
        (root / "VALIDATION.md").write_text("npm run known\n", encoding="utf-8")
        (root / "release" / "readiness" / "LOCAL_SIGNOFF_COMMANDS.md").write_text(
            "npm run missing-active\n", encoding="utf-8"
        )
        (root / "HISTORY.md").write_text("npm run missing-history\n", encoding="utf-8")
        tracked = (
            "AGENTS.md",
            "release/readiness/LOCAL_SIGNOFF_COMMANDS.md",
            "HISTORY.md",
        )

        active = checker.markdown_files_for_scope(root, "active", tracked)
        assert "release/readiness/LOCAL_SIGNOFF_COMMANDS.md" in active
        assert "VALIDATION.md" in active
        assert "HISTORY.md" not in active
        active_errors, active_count = checker.documented_command_errors(
            root, active, {"known"}, {}
        )
        assert active_count == 3
        assert len(active_errors) == 1 and "missing-active" in active_errors[0]

        all_files = checker.markdown_files_for_scope(root, "all", tracked)
        all_errors, all_count = checker.documented_command_errors(
            root, all_files, {"known"}, {}
        )
        assert all_count == 4
        assert any("missing-history" in error for error in all_errors)

    print("NPM documented-command scope tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
