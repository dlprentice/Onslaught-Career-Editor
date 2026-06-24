# Lane 10/10 Unresolved Uncertainty Tracker Audit (2026-03-04)

## Scope
- Audited docs under:
  - `reverse-engineering/`
  - `lore-book/reverse-engineering/`
  - `roadmap/`
  - app docs: `README.MD`, `CURRENT_CAPABILITIES.md`, `MAPPED_SYSTEMS.md`, `WHAT_WE_CAN_DO_NOW.md`, `USER_SANITY_CHECK.md`, `MCP_LIMITATIONS.md`, `MCP_DEBUGGING_OPTIONS.md`, `STUART_SOURCE_REQUIREMENTS_FOR_FULL_CLARITY.md`
- Read-only audit intent; only this report file was written.
- `developer_agent_state.json` / `documentation_agent_state.json` were not edited per request.

## Triage Method
- Keyword sweep for `TBD/TODO/unverified/unresolved/unknown/pending`.
- Deep-read of high-impact hits (save patch correctness + user-facing behavior).
- Deduplicated mirror copies in `lore-book/reverse-engineering/` where content matches canonical files.

## Should-Be-Resolved-Now Queue

| Priority | Claim | Why this should be resolved now | Evidence |
|---|---|---|---|
| P0 | **`Maladim` god-mode behavior remains unresolved/inconsistently framed** (`no visible effect`, `SP unverified`, historical MP notes) | Direct user-facing behavior ambiguity; docs currently mix “historical/pre-correction” and open-state wording across multiple pages. | `reverse-engineering/game-mechanics/god-mode.md:292`, `reverse-engineering/game-mechanics/god-mode.md:315`, `reverse-engineering/game-mechanics/cheat-codes.md:18`, `reverse-engineering/game-mechanics/_index.md:50`, `roadmap/status-current.md:52`, `reverse-engineering/binary-analysis/functions/FEPSaveGame.cpp/_index.md:36` |
| P0 | **`--experimental-pending-extra-goodies` remains unresolved/no-op in retail Steam** | User-facing CLI/UI expectation risk: feature appears exposed/documented but intentionally ignored. Either finalize persistence mapping or hard-disable/de-emphasize user-facing surface. | `CURRENT_CAPABILITIES.md:38`, `CURRENT_CAPABILITIES.md:55`, `README.MD:172`, `reverse-engineering/save-file/save-format.md:339`, `roadmap/status-current.md:83`, `roadmap/csharp-python-parity.md:187` |
| P1 | **Walker invert-Y semantics still listed as pending verification** | Save editor patches these per-player settings; final runtime-path verification would close remaining uncertainty on user-visible controls behavior. | `roadmap/status-current.md:80`, `roadmap/status-current.md:81`, `reverse-engineering/source-code/core/engine-system.md:203` |
| P1 | **Stale uncertainty backlog items in `roadmap/re-investigation.md` conflict with newer canonical status** (e.g., `File Offset TBD` for cheat patch path; broad unresolved language in archival sections) | Documentation consistency issue can mislead implementation/RE lanes and re-open already-closed questions. | `roadmap/re-investigation.md:120`, `roadmap/re-investigation.md:129`, `roadmap/re-investigation.md:158` |
| P2 | **`V3R5IOF` effect still “no call sites / needs in-game confirmation”** | User-facing cheat behavior remains unknown; lower impact than save correctness but still externally visible behavior ambiguity. | `reverse-engineering/game-mechanics/_index.md:49`, `reverse-engineering/game-mechanics/cheat-codes.md:17`, `reverse-engineering/binary-analysis/functions/FEPSaveGame.cpp/_index.md:35` |

## Acceptable Residual Queue (Keep Preserving / Non-Blocking)

| Area | Residual claim | Why acceptable for now | Evidence |
|---|---|---|---|
| Save patch safety | `0x249A` remains unknown/unused | Patchers preserve this dword; no write required for core workflows. | `reverse-engineering/save-file/struct-layouts.md:22`, `reverse-engineering/save-file/struct-layouts.md:292`, `reverse-engineering/save-file/save-format.md:281` |
| Save patch safety | Kill-counter top-byte metadata UI meaning unknown | Core patch rule is already safe (`preserve top byte`), so correctness is protected while UI meaning stays unknown. | `reverse-engineering/save-file/kill-tracking.md:131`, `reverse-engineering/save-file/kill-tracking.md:146`, `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/_index.md:11` |
| Save progression details | Tech-slot unknown bit semantics | Core editor does not require full semantic map to patch rank/kills/goodies safely. | `roadmap/tech-slots.md:42`, `roadmap/tech-slots.md:54` |
| Save progression details | `mBaseThingsExists` bit semantics incomplete | Non-blocking for current rank/kills/goodies/options patch goals; affects deeper objective-state tooling only. | `roadmap/re-investigation.md:26` |
| Goodie catalog naming | Goodie 78 display/name unresolved | Unlock rule is known (43 S-grades), so core unlock logic is unaffected. | `reverse-engineering/save-file/goodies-system.md:155` |
| Frontend/control RE depth | `CPCController__GetKeyState3` semantics TBD | Not required for current save patch correctness path. | `reverse-engineering/source-code/frontend/controller-system.md:47`, `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:895` |
| Frontend UX RE depth | `CFrontEnd__SetPage(..., 0, 0x32)` exact UX meaning TBD | Does not affect save-data patch correctness. | `reverse-engineering/binary-analysis/functions/FEPDirectory.cpp/_index.md:57`, `reverse-engineering/binary-analysis/functions/FEPDirectory.cpp/_index.md:118` |
| Localization RE depth | `g_UseAmericanEnglish` setter path TBD | Non-blocking for save patch behavior. | `reverse-engineering/binary-analysis/functions/text.cpp/CText__Init.md:137` |
| Docs backlog | Many function-level TODO/TBD stubs in binary-analysis docs | Acceptable as long as marked as stub/provisional and not used as canonical save-format authority. | `reverse-engineering` + `lore-book/reverse-engineering` contain **126** `TODO/TBD` hits (mostly function docs/stubs) |
| Historical/community lore | Unknown contributor identities / unknown causes in community bug notes | Not save-editor correctness blockers. | `reverse-engineering/project-meta/attribution.md:28`, `reverse-engineering/project-meta/known-bugs.md:69` |

## Mirror Parity Note (`lore-book/reverse-engineering/`)
- High-impact unresolved claims above are mirrored in corresponding lore-book files (notably `game-mechanics/*`, `save-file/*`, `project-meta/*`).
- No additional unique high-impact uncertainty was found in the mirrored tree beyond canonical `reverse-engineering/` sources.

## Recommended Immediate Doc-Close Order
1. Normalize `Maladim` status wording across all canonical + mirrored docs (single source-of-truth statement + test matrix outcome).
2. Decide policy for `--experimental-pending-extra-goodies`: either implement verified retail persistence path or explicitly hide/deprecate from user-facing docs/CLI help.
3. Close walker invert-Y verification gap and update confidence/status rows to final values.
4. Clean stale `roadmap/re-investigation.md` entries that contradict newer resolved evidence.
