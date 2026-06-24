# Lane 03 - AGENTS + Skills Policy Audit (2026-03-04)

Scope:
- `AGENTS.md`
- Skills: `bes-file-format`, `critical-patterns`, `binary-patching`, `stuart-source-code`, `documentation-standards`
- Reality checks against current repo implementation/docs (`README.MD`, `patches/README.md`, `BinaryPatchEngine.cs`, `onslaught/core/binary_patches.py`, patch scripts)

## High-Severity Contradictions

1. **Backup contract mismatch in `binary-patching` skill can break restore expectations across tools.**
   - Skill states: "All create `.backup` before modifying" (`/home/dlprentice/.codex/skills/binary-patching/SKILL.md:135`).
   - Actual repo reality is split:
     - App/primary binary patch engine uses `.original.backup` (`BinaryPatchEngine.cs:33`, `BinaryPatchEngine.cs:63`, `BinaryPatchEngine.cs:164`; `onslaught/core/binary_patches.py:14`, `onslaught/core/binary_patches.py:62`, `onslaught/core/binary_patches.py:148`; `README.MD:65`; `patches/README.md:220`, `patches/README.md:222`).
     - Dev-mode script uses `.exe.backup` (`patches/patch_devmode_goodies_logic_fix.py:64`, `patches/patch_devmode_goodies_logic_fix.py:132`; `patches/README.md:221`).
   - Why this is high severity:
     - Cross-tool restore can fail if operators assume one backup convention.
     - The app UI restore path is keyed to `.original.backup`; `.exe.backup` is not equivalent in that flow.

2. **`binary-patching` skill “key patch locations” drifts from the canonical app-supported patch model.**
   - Skill lists `-forcewindowed` guard normalization (`0x00662F3E` / file `0x262F3E`) as a key patch location (`/home/dlprentice/.codex/skills/binary-patching/SKILL.md:102-108`).
   - Current canonical patch model implemented in app/parity modules and patch docs is the 3-patch display-flow set only:
     - `0x129696`, `0x12A644`, optional `0x12BB97` (`BinaryPatchEngine.cs:35-59`; `onslaught/core/binary_patches.py:33-59`; `patches/README.md:46-50`).
   - Why this is high severity:
     - Agents can apply unsupported extra mutations outside the app’s byte-verified set, creating executable states not represented by current UI/tested workflows.

## Medium/Low (Optional)

- `binary-patching` includes MALLOY JNZ/JZ inversion as a live example (`/home/dlprentice/.codex/skills/binary-patching/SKILL.md:70-72`) while repo policy says MALLOY needs no binary patch and old cheat patches are archival (`patches/README.md:9`, `patches/README.md:85-95`, `patches/README.md:119`).
- Risk: guidance confusion, but less severe than backup/patch-model drift because it is partly framed as historical/example content.

## Alignment Check (No High-Severity Contradictions Found)

- **App-delivery focus:** AGENTS app-first delivery policy is clear and current (`AGENTS.md:15-22`), and none of the audited skills directly contradict it.
- **Retail-target rules:** `bes-file-format`, `critical-patterns`, and `stuart-source-code` remain aligned with retail/Steam true-view rules (`/home/dlprentice/.codex/skills/bes-file-format/SKILL.md:12-17`, `/home/dlprentice/.codex/skills/critical-patterns/SKILL.md:22-30`, `/home/dlprentice/.codex/skills/stuart-source-code/SKILL.md:10-19`).
- **Docs conventions:** `documentation-standards` matches current index naming/location conventions (`AGENTS.md:358-362`; `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:51-60`).
