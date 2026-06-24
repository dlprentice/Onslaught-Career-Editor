# Lane03 Skill Drift Findings

## Scope Audited
- `/home/dlprentice/.codex/skills/bes-file-format/SKILL.md`
- `/home/dlprentice/.codex/skills/binary-patching/SKILL.md`
- `/home/dlprentice/.codex/skills/cheat-codes/SKILL.md`
- `/home/dlprentice/.codex/skills/onslaught-controls/SKILL.md`
- `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`
- `/home/dlprentice/.codex/skills/career-file-format/SKILL.md`
- `/home/dlprentice/.codex/skills/critical-patterns/SKILL.md`

## Severity-Ranked Findings

### Critical
1. **Stale canonical anchor to `CLAUDE.md` (non-canonical/non-existent in this repo)**
- Skill refs:
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:63`
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:69`
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:164`
- Canonical truth:
  - `AGENTS.md:360` defines top-level canonical indexes.
  - `AGENTS.md:361` allows README compatibility but keeps `_index.md` canonical in subfolders.
  - Repo root has `AGENTS.md` and no `CLAUDE.md`.
- Drift impact:
  - Directs documentation contributors to a non-canonical control file and broken/irrelevant cross-links.
- Recommended correction:
  - Replace `CLAUDE.md` references with `AGENTS.md` for repo-wide assistant policy context.
  - For doc navigation guidance, point to `reverse-engineering/RE-INDEX.md`, `lore/LORE-INDEX.md`, and `roadmap/ROADMAP-INDEX.md`.

2. **Example encodes kill-counter offset in legacy aligned view as if it were authoritative**
- Skill ref:
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:158`
- Canonical truth:
  - `AGENTS.md:266` and `AGENTS.md:184` set true-view file offset to `0x23F6` (CCareer `0x23F4`).
  - `reverse-engineering/save-file/save-format.md:147` and `:170` reinforce true-view authoritative offset.
- Drift impact:
  - Reintroduces the exact aligned-view confusion the repo explicitly corrected, increasing risk of bad docs and bad patch guidance.
- Recommended correction:
  - Update example to: “Real kill counts at file `0x23F6` (CCareer `0x23F4`, true dword view).”
  - Optionally annotate `0x23F4` as legacy aligned-view reference only.

### High
3. **Top-level index guidance is downgraded to optional/incomplete**
- Skill refs:
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:32`
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:56`
- Canonical truth:
  - `AGENTS.md:360` explicitly declares canonical top-level indexes: `RE-INDEX.md`, `LORE-INDEX.md`, `ROADMAP-INDEX.md`.
- Drift impact:
  - Encourages inconsistent navigation standards and misses two required top-level canonical indexes.
- Recommended correction:
  - Update index section to treat those three top-level indexes as canonical (not optional) and include all three explicitly.

4. **README policy conflicts with current compatibility posture**
- Skill ref:
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:57`
- Canonical truth:
  - `AGENTS.md:361`: README files may exist for compatibility; avoid divergent duplicate content.
- Drift impact:
  - “Repo-root only” guidance conflicts with existing repo structure (many folder-level README files retained for compatibility).
- Recommended correction:
  - Replace with: “`_index.md` is canonical; folder `README.md` may exist for compatibility but must remain content-synced / non-divergent.”

### Medium
5. **Status-table example carries obsolete god-mode claim**
- Skill ref:
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:93`
- Canonical truth:
  - `AGENTS.md:286` marks Maladim/god mode as “No visible effect - needs investigation.”
  - `reverse-engineering/game-mechanics/god-mode.md:7` and `:148` treat Steam behavior as unconfirmed.
- Drift impact:
  - Example text can propagate disproven/insufficiently evidenced claims in new docs.
- Recommended correction:
  - Replace with an explicitly conservative example status, e.g. “God mode | Unverified (Steam) | Runtime cheat-gated; no visible effect in Dec 2025 user testing.”

## No Material Drift Found In Other Audited Skills
- `/home/dlprentice/.codex/skills/bes-file-format/SKILL.md`
- `/home/dlprentice/.codex/skills/binary-patching/SKILL.md`
- `/home/dlprentice/.codex/skills/cheat-codes/SKILL.md`
- `/home/dlprentice/.codex/skills/onslaught-controls/SKILL.md`
- `/home/dlprentice/.codex/skills/career-file-format/SKILL.md`
- `/home/dlprentice/.codex/skills/critical-patterns/SKILL.md`

These six are currently consistent with repo-canonical truths for save-format mapping, binary patch caveats, cheat behavior, and controls context.
