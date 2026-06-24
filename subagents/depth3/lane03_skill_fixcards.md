# Lane03 Skill Update Fix Cards

Source findings: `subagents/depth2/lane03_skill_drift_findings.md`.
Target skill file: `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`.

## Card SD-01 (Critical)

- Title: Replace non-canonical `CLAUDE.md` anchors with repo-canonical references.
- Sections to rewrite (exact):
  - `## What Belongs Where` table row at `SKILL.md:63` (`CLAUDE.md` row).
  - Statement at `SKILL.md:69` (`CLAUDE.md is NOT for detailed analysis.`).
  - `## Cross-Linking` bullet at `SKILL.md:164` (`Link ... back to CLAUDE.md`).
- Rewrite instructions:
  - Remove `CLAUDE.md` as a canonical documentation anchor.
  - Replace with `AGENTS.md` for repo-wide assistant policy context.
  - In cross-link guidance, point to canonical top-level indexes: `reverse-engineering/RE-INDEX.md`, `lore/LORE-INDEX.md`, `roadmap/ROADMAP-INDEX.md`.
- Expected truth statements (must be true after update):
  - `AGENTS.md` is the repo-canonical assistant policy file.
  - Canonical top-level documentation indexes are `reverse-engineering/RE-INDEX.md`, `lore/LORE-INDEX.md`, and `roadmap/ROADMAP-INDEX.md`.
  - `CLAUDE.md` is not required as a canonical doc anchor in this repo.
- Acceptance checks:
  - `documentation-standards/SKILL.md` contains no required-action guidance pointing to `CLAUDE.md`.
  - `AGENTS.md` and all three top-level canonical indexes are explicitly named where global navigation context is described.

## Card SD-02 (Critical)

- Title: Correct kill-counter example to true-dword-view authoritative offsets.
- Sections to rewrite (exact):
  - `## Discovery Documentation` example block at `SKILL.md:156-159`.
- Rewrite instructions:
  - Replace the example claim `Real kill counts at 0x23F4` with true-view authoritative mapping.
  - Recommended wording: `Real kill counts at file 0x23F6 (CCareer 0x23F4, true dword view).`
  - If legacy aligned view is mentioned, mark it explicitly as non-authoritative.
- Expected truth statements (must be true after update):
  - Kill counters are stored at file offset `0x23F6` in Steam/retail `.bes` true view.
  - `CCareer` offset for the kill-counter block is `0x23F4`.
  - `0x23A4` is in the goodies array region and is not a kill-counter location.
- Acceptance checks:
  - No example text in this skill treats `0x23F4` as the direct on-disk file offset.
  - At least one example line explicitly pairs `file 0x23F6` with `CCareer 0x23F4`.

## Card SD-03 (High)

- Title: Make top-level canonical index guidance mandatory and complete.
- Sections to rewrite (exact):
  - `## Directory Structure` comment at `SKILL.md:32` (`RE-INDEX.md # Optional root landing page`).
  - `## Index File Naming` table row at `SKILL.md:56` (`RE-INDEX.md | Optional ...`).
- Rewrite instructions:
  - Remove optional framing for top-level canonical index files.
  - Expand guidance to explicitly include all three top-level canonical indexes: `RE-INDEX.md`, `LORE-INDEX.md`, `ROADMAP-INDEX.md`.
  - Keep `_index.md` canonical for subfolders.
- Expected truth statements (must be true after update):
  - Top-level canonical indexes are exactly: `reverse-engineering/RE-INDEX.md`, `lore/LORE-INDEX.md`, `roadmap/ROADMAP-INDEX.md`.
  - `_index.md` is canonical within subfolders.
- Acceptance checks:
  - The skill no longer labels top-level canonical indexes as optional.
  - The index naming guidance includes all three top-level canonical index files.

## Card SD-04 (High)

- Title: Align README guidance with compatibility policy.
- Sections to rewrite (exact):
  - `## Index File Naming` table row at `SKILL.md:57` (`README.md | Repo-root only ...`).
- Rewrite instructions:
  - Replace repo-root-only prohibition with compatibility posture.
  - Required stance: folder-level `README.md` files may exist for compatibility, but `_index.md` remains canonical and README content must not diverge.
- Expected truth statements (must be true after update):
  - `_index.md` is canonical in subfolders.
  - `README.md` can exist in folders for compatibility.
  - Duplicate README/_index content must remain non-divergent.
- Acceptance checks:
  - No text in this skill says folder README files are disallowed when `_index.md` exists.
  - Compatibility/non-divergence language is explicit.

## Card SD-05 (Medium)

- Title: Replace obsolete god-mode status-table example with conservative verified wording.
- Sections to rewrite (exact):
  - `## Standard Table Formats` -> `### Status Tables` example row at `SKILL.md:93` (`God mode | Partial | P2 works in multiplayer`).
- Rewrite instructions:
  - Remove gameplay claim implying partially confirmed Steam god mode behavior.
  - Replace with conservative verified wording, e.g. `God mode | Unverified (Steam) | Runtime cheat-gated; Maladim had no visible effect in Dec 2025 user testing.`
- Expected truth statements (must be true after update):
  - Steam-build god mode remains unconfirmed.
  - `Maladim` is documented as no visible effect in limited Dec 2025 user testing.
  - God mode behavior is runtime cheat-gated rather than a confirmed save-persistence outcome.
- Acceptance checks:
  - No sample table row in this skill asserts confirmed Steam god mode behavior.
  - Example wording is explicitly conservative (`Unverified`/equivalent) and references runtime gating.

## No-Change Note

- No skill-update cards are required for:
  - `/home/dlprentice/.codex/skills/bes-file-format/SKILL.md`
  - `/home/dlprentice/.codex/skills/binary-patching/SKILL.md`
  - `/home/dlprentice/.codex/skills/cheat-codes/SKILL.md`
  - `/home/dlprentice/.codex/skills/onslaught-controls/SKILL.md`
  - `/home/dlprentice/.codex/skills/career-file-format/SKILL.md`
  - `/home/dlprentice/.codex/skills/critical-patterns/SKILL.md`
