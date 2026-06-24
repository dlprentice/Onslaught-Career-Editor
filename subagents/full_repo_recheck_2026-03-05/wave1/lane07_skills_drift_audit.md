# Lane 07 Skills Drift Audit

- Date: 2026-03-05
- Scope: `bes-file-format`, `career-file-format`, `binary-patching`, `critical-patterns`, `onslaught-controls`, `onslaught-architecture`, `stuart-source-code`, `documentation-standards`
- Method: compared each skill's `SKILL.md` against current repo truth in `AGENTS.md`, active RE docs, and patch docs.
- Constraint check: read-only audit; no tracked repo file edited other than this report output.

## Summary

| Skill | Status | Notes |
|------|--------|-------|
| `bes-file-format` | OK | No material factual drift found. |
| `career-file-format` | OK | Still correctly framed as internal/source-build guidance with retail handoff. |
| `binary-patching` | DRIFT | Canonical patch-set guidance is stale/incomplete. |
| `critical-patterns` | DRIFT | Still implies a persisted "pending extras" fixed-region field that repo docs now reject. |
| `onslaught-controls` | OK | No hard factual drift found in the skill body. |
| `onslaught-architecture` | DRIFT | GPU override flag name is stale. |
| `stuart-source-code` | MINOR DRIFT | Retail cheat-string rendering for index 5 is over-normalized. |
| `documentation-standards` | DRIFT | Contains stale god-mode example; 1000-line rule no longer matches repo reality. |

## Findings

### 1. Medium: `binary-patching` no longer reflects the canonical display/window patch set

- Skill refs:
  - `/home/dlprentice/.codex/skills/binary-patching/SKILL.md:99-108`
  - `/home/dlprentice/.codex/skills/binary-patching/SKILL.md:141-153`
- Problem:
  - The skill's `Key Patch Locations` only surfaces three addresses (`0x129696`, `0x12A644`, optional `0x12BB97`) and does not mention the repo's current canonical v2 patch catalog or the other stable display-flow patches.
- Repo truth:
  - `patches/README.md:22-38` says the canonical source is `patches/catalog/patches.v2.json`.
  - `patches/README.md:60-68` lists the current supported patch set, including `0x0CDD40`, `0x12AF3F`, `0x06416F`, and `0x1AA444` in addition to the three addresses above.
- Impact:
  - An agent using the skill as-is can recommend an incomplete patch plan and miss the catalog-driven app workflow.
- Recommended skill update:
  - Point agents at `patches/catalog/patches.v2.json` / `patches/README.md` as canonical, and treat the three-address table as a subset, not the full active patch set.

### 2. Medium: `binary-patching` still presents the guard-byte `00 -> 01` edit as a validated baseline patch

- Skill refs:
  - `/home/dlprentice/.codex/skills/binary-patching/SKILL.md:157-178`
  - `/home/dlprentice/.codex/skills/binary-patching/SKILL.md:51-60`
- Problem:
  - The skill still frames `0x262F3E: 00 -> 01` as the concrete validated `-forcewindowed` patch path.
- Repo truth:
  - `reverse-engineering/binary-analysis/windowed-mode-analysis.md:10-14` says the current canonical Steam hash already has the guard byte at `0x01`.
  - `reverse-engineering/binary-analysis/windowed-mode-analysis.md:108` and `:142-147` make startup-flow patches the primary repo guidance, with guard-byte normalization only as an optional baseline tweak.
- Impact:
  - The skill can push agents toward an outdated fix-first narrative for current repo binaries.
- Recommended skill update:
  - Reword the guard-byte patch as variant-only normalization, not the main current-repo fix.

### 3. Medium: `critical-patterns` still implies a persisted fixed-region "pending extras" field in retail `.bes`

- Skill refs:
  - `/home/dlprentice/.codex/skills/critical-patterns/SKILL.md:85-90`
- Problem:
  - The skill says the fixed end-of-file settings region includes "pending extras".
- Repo truth:
  - `reverse-engineering/source-code/gameplay/career-system.md:183-188` says the internal source has `mPendingExtraGoodies`, but the Steam build does not currently have a confirmed standalone persisted dword for it; earlier `0x24BA` labeling was wrong and is now Player 2 controller config.
  - `AGENTS.md:195-199` identifies `0x24AE..0x24BA` as vibration/config fields and starts options entries at `0x24BE`.
- Impact:
  - This keeps an old false-positive alive around the fixed CCareer tail.
- Recommended skill update:
  - Remove "pending extras" from the retail fixed-region summary or mark it explicitly as unconfirmed/non-persisted in Steam.

### 4. Medium: `onslaught-architecture` uses a stale GPU override flag name

- Skill refs:
  - `/home/dlprentice/.codex/skills/onslaught-architecture/SKILL.md:205`
- Problem:
  - The skill says the GeForce 3 requirement can be overridden with `-nonforcegf3`.
- Repo truth:
  - `reverse-engineering/source-code/_index.md:100-106` lists `-geforce2` / `-geforce3` as the current documented GPU compatibility flags.
  - `reverse-engineering/source-code/core/platform-system.md:218-220` ties the override path to `CLIPARAMS.mGeforce3` and those `-geforce2` / `-geforce3` flags.
- Impact:
  - An agent can recommend a flag name that is not the repo's current authoritative CLI guidance.
- Recommended skill update:
  - Replace `-nonforcegf3` with `-geforce2` / `-geforce3` unless fresh source evidence is added.

### 5. Low: `documentation-standards` includes a stale god-mode example

- Skill refs:
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:90-96`
- Problem:
  - The example status table still uses `God mode | Partial | P2 works in multiplayer`.
- Repo truth:
  - `roadmap/ROADMAP-INDEX.md:18-25` now describes god mode as cheat-gated with persisted `g_bGodModeEnabled`, but says `Maladim` shows no visible effect and per-player persisted flags are not mapped in Steam.
  - `AGENTS.md:271-288` says god mode is runtime-only/cheat-gated and treats `Maladim` as unresolved.
- Impact:
  - The example reintroduces a claim the repo now treats as non-canonical.
- Recommended skill update:
  - Swap the example note to the current unresolved wording or use a different feature example.

### 6. Low: `documentation-standards` still asserts a hard 1000-line markdown ceiling, but repo reality has already drifted

- Skill refs:
  - `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md:21-26`
- Problem:
  - The skill states a strict `Maximum 1000 LOC per .md file` rule.
- Repo reality:
  - `wc -l reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` currently reports `3335` lines.
- Impact:
  - Agents get an inaccurate picture of the current corpus shape and may over-trust the rule as something the repo consistently enforces.
- Recommended skill update:
  - Either reframe this as an aspirational guideline or note that older docs exceed it and may need future splitting.

### 7. Low: `stuart-source-code` over-normalizes the retail index-5 cheat string as `latête`

- Skill refs:
  - `/home/dlprentice/.codex/skills/stuart-source-code/SKILL.md:36`
- Problem:
  - The skill presents the extra retail string as `latête` without the encoding caveat.
- Repo truth:
  - `reverse-engineering/game-mechanics/cheat-codes.md:19-22` records the decoded value as `lat\xEAte` and explicitly says rendering as `latête` depends on encoding/font.
- Impact:
  - Minor, but it weakens exactness in a repo that now tracks the encoding nuance explicitly.
- Recommended skill update:
  - Use `lat\xEAte` with a note that it may render as `latête`.

## No Material Drift Found

- `bes-file-format`
  - Current offsets, kill-meta handling, control-field mapping, and true-dword guidance match `AGENTS.md:177-205` and the save docs.
- `career-file-format`
  - Still correctly framed as internal/source-build structure, with explicit retail handoff to `bes-file-format` and `cheat-codes`.
- `onslaught-controls`
  - Current button ranges, debug-key caveats, config mapping summary, and retail cheat-name framing are consistent with `reverse-engineering/source-code/frontend/controller-system.md:65-86` and `:153-166`.

## Net

The highest-value fixes are in `binary-patching`, `critical-patterns`, `onslaught-architecture`, and `documentation-standards`. The save-format skills are in comparatively good shape.
