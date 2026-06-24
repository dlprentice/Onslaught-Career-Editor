# Depth4 Lane03 Skills Sync Plan (Final Synthesis)

## Inputs Synthesized
- `subagents/depth2/lane03_skill_drift_findings.md`
- `subagents/depth3/lane03_skill_fixcards.md`
- `subagents/depth3/lane10_master_fix_queue.tsv` (FX linkage)

## Scope and Target
- Primary target file: `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`
- In-scope fix cards: `SD-01`, `SD-02`, `SD-03`, `SD-04`, `SD-05`
- Existing queue IDs: `FX-001`, `FX-002`, `FX-012`, `FX-013`
- Queue gap to close: `SD-05` (medium) is not represented in lane10 TSV and should be added before closure sign-off.

## Closure Outcome Required
Bring `documentation-standards/SKILL.md` into full alignment with repo-canonical policy in `AGENTS.md` by removing stale `CLAUDE.md` anchoring, fixing true-view offset examples, making canonical indexes explicit, aligning README compatibility wording, and replacing obsolete god-mode sample status text.

## Exact Edits (Apply in Order)

### Edit 1: Canonical top-level index language (SD-03, FX-012)
File: `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`

1. In `## Directory Structure` code block, replace this line:
```text
  RE-INDEX.md              # Optional root landing page (project may keep one)
```
with:
```text
  RE-INDEX.md              # Canonical reverse-engineering top-level index
```

2. In `## Index File Naming`, replace the current table rows:
```markdown
| `_index.md` | Canonical index for any documentation folder/subfolder |
| `RE-INDEX.md` | Optional reverse-engineering root landing page (if present) |
| `README.md` | Repo-root only (avoid per-folder README duplicates when `_index.md` exists) |
```
with:
```markdown
| `_index.md` | Canonical index for any documentation folder/subfolder |
| `reverse-engineering/RE-INDEX.md` | Canonical reverse-engineering top-level index |
| `lore/LORE-INDEX.md` | Canonical lore top-level index |
| `roadmap/ROADMAP-INDEX.md` | Canonical roadmap top-level index |
| `README.md` | May exist in folders for compatibility; keep content non-divergent from canonical `_index.md` |
```

### Edit 2: Replace stale `CLAUDE.md` anchor with `AGENTS.md` (SD-01, FX-001)
File: `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`

1. In `## What Belongs Where`, replace row:
```markdown
| `CLAUDE.md` | Critical info for 24/7 awareness: current status, key patterns, gotchas. Keep concise. |
```
with:
```markdown
| `AGENTS.md` | Repo-wide assistant policy context and canonical documentation navigation rules. Keep concise and policy-focused. |
```

2. Replace sentence:
```markdown
**CLAUDE.md is NOT for detailed analysis.** Move details to scoped files.
```
with:
```markdown
**AGENTS.md is not for deep technical analysis.** Keep details in scoped docs under `reverse-engineering/`, `lore/`, and `roadmap/`.
```

### Edit 3: Correct kill-counter example to true-view mapping (SD-02, FX-002)
File: `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`

In `## Discovery Documentation` example, replace line:
```markdown
- Real kill counts at 0x23F4 (verified via hex dump of gold save)
```
with:
```markdown
- Real kill counts at file 0x23F6 (CCareer 0x23F4, true dword view; aligned-view 0x23F4 references are legacy/non-authoritative)
```

### Edit 4: Cross-linking must point to canonical indexes, not `CLAUDE.md` (SD-01, FX-001)
File: `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`

In `## Cross-Linking`, replace bullet:
```markdown
- Link from specialized docs back to CLAUDE.md for context
```
with:
```markdown
- Link specialized docs to canonical indexes for navigation context: `reverse-engineering/RE-INDEX.md`, `lore/LORE-INDEX.md`, and `roadmap/ROADMAP-INDEX.md`
```

### Edit 5: Replace obsolete god-mode status example with conservative wording (SD-05, queue gap)
File: `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`

In `### Status Tables` example, replace row:
```markdown
| God mode | Partial | P2 works in multiplayer |
```
with:
```markdown
| God mode | Unverified (Steam) | Runtime cheat-gated; Maladim had no visible effect in Dec 2025 user testing |
```

## Validation Checklist (Command + Expected Result)

1. `CLAUDE.md` anchor removed from required guidance:
```bash
rg -n "CLAUDE\.md" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md
```
Expected: no matches.

2. Canonical repo policy/index anchors present:
```bash
rg -n "AGENTS\.md|reverse-engineering/RE-INDEX\.md|lore/LORE-INDEX\.md|roadmap/ROADMAP-INDEX\.md" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md
```
Expected: matches for all 4 tokens.

3. True-view kill mapping explicit and aligned-view marked legacy:
```bash
rg -n "file 0x23F6|CCareer 0x23F4|legacy/non-authoritative" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md
```
Expected: all phrases present in discovery example.

4. Optional framing removed for top-level indexes:
```bash
rg -n "Optional reverse-engineering root landing page|if present" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md
```
Expected: no matches.

5. README compatibility posture aligned (not repo-root-only):
```bash
rg -n "Repo-root only|compatibility|non-divergent|_index\.md" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md
```
Expected: no `Repo-root only`; positive matches for compatibility/non-divergent and `_index.md`.

6. God-mode example conservative and evidence-aligned:
```bash
rg -n "God mode \| Unverified \(Steam\)|Runtime cheat-gated|Maladim had no visible effect" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md
```
Expected: all phrases present in status table row.

7. Queue reconciliation for full lane closure:
- Ensure lane10 master queue includes a medium entry for `SD-05` (current gap).
- If queue update is required, add a new `FX` row referencing `subagents/depth2/lane03_skill_drift_findings.md` + `subagents/depth3/lane03_skill_fixcards.md` and use the same validation command as checklist item 6.

## No-Change Confirmation
No edits required for these skill files (remain aligned per depth2 audit):
- `/home/dlprentice/.codex/skills/bes-file-format/SKILL.md`
- `/home/dlprentice/.codex/skills/binary-patching/SKILL.md`
- `/home/dlprentice/.codex/skills/cheat-codes/SKILL.md`
- `/home/dlprentice/.codex/skills/onslaught-controls/SKILL.md`
- `/home/dlprentice/.codex/skills/career-file-format/SKILL.md`
- `/home/dlprentice/.codex/skills/critical-patterns/SKILL.md`
