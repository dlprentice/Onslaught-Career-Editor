# Wave1219 Final Score16 Current-Risk Review

Wave1219 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1219; wave1219-final-score16-current-risk-review; 1179/1179 = 100.00%; 16 final score16 current-risk rows; CLine__ctor_copy; CBoat__Init; CBoatGuide__ctor; CFrameTimer__ctor; CDebugMarker__ctor; CEndLevelData__IsAllSecondaryObjectivesComplete; CCollisionSeekingThing__ctor_base; CHLCollisionDetector__ctor_base; COggLoader__readerSubobject_dtor_body; COggLoader__ctor_base; CPlane__Hit_CheckFatalDamageAndDie; CSentinel__Init; SharedUnitAnimation__FindAnimationIndexOrZero; SharedUnitAnimation__PlayAnimationByNameIfPresent; PCLTShell__ctor; COggFileRead__scalar_deleting_dtor; 6411/6411 = 100.00%; 0 / 0 / 0; 44 xref rows; 539 instruction rows; 16 decompile rows; current focused candidates: 1117; live regenerated current focused candidates: 1117; remaining active focused work: 0; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=16 skipped=0; tags_added=84; final dry updated=0 skipped=16; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1210/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; continuity denominator; [maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Wave1219 closed the remaining active `wave1108-current-risk-rank` continuity denominator rows with fresh read-only exports and a tag-only Ghidra normalization. The 16-row tail is heterogeneous by subsystem, but coherent by risk type: prior static corrections already carried bounded names/signatures/comments, while the current-risk/read-back/rebuild-grade tags were missing or incomplete.

| Address | Function | Static boundary |
| --- | --- | --- |
| `0x004098e0` | `CLine__ctor_copy` | CGeneralVolume/CLine copy-constructor evidence; exact concrete layout and runtime collision behavior remain separate proof. |
| `0x00414e50` | `CBoat__Init` | Boat init delegates through `CGroundUnit__Init`, seeds boat fields, and allocates guide/Warspite-adjacent helpers; runtime boat behavior remains separate proof. |
| `0x00415d70` | `CBoatGuide__ctor` | Constructor wrapper calls `CGuide__ctor_base`, writes vtable `0x005d8d5c`, and returns `this`; exact guide layout remains separate proof. |
| `0x00423650` | `CFrameTimer__ctor` | Platform timer constructor records performance-counter frequency/fallback state; runtime timing behavior remains separate proof. |
| `0x004422d0` | `CDebugMarker__ctor` | Debug marker constructor inserts the marker into global list state and seeds defaults; runtime marker/debug behavior remains separate proof. |
| `0x004496e0` | `CEndLevelData__IsAllSecondaryObjectivesComplete` | Secondary-objective status scanner with source-parity log string behavior; runtime progression behavior remains separate proof. |
| `0x00488ef0` / `0x00488f00` | `CCollisionSeekingThing__ctor_base`, `CHLCollisionDetector__ctor_base` | Collision constructor-base helpers zero a field and install their vtables; exact layouts remain separate proof. |
| `0x004b6cd0` / `0x004b6d30` | `COggLoader__readerSubobject_dtor_body`, `COggLoader__ctor_base` | Ogg loader reader/waiting-thread construction and cleanup evidence; runtime streaming behavior remains separate proof. |
| `0x004d1f10` | `CPlane__Hit_CheckFatalDamageAndDie` | Plane vtable slot-39 fatal-hit path before the common hit/death tail; runtime hit/death behavior remains separate proof. |
| `0x004dea50` | `CSentinel__Init` | Sentinel init delegates through GroundUnit, attaches motion/control helpers, and registers state; runtime Sentinel behavior remains separate proof. |
| `0x004f4530` / `0x004f4560` | `SharedUnitAnimation__FindAnimationIndexOrZero`, `SharedUnitAnimation__PlayAnimationByNameIfPresent` | Shared animation lookup/playback helpers used by GillMHead and BattleEngine paths; runtime animation behavior remains separate proof. |
| `0x00512670` | `PCLTShell__ctor` | Platform shell constructor installs PCLTShell vtable and title/input state; runtime launch behavior remains separate proof. |
| `0x005245e0` | `COggFileRead__scalar_deleting_dtor` | Scalar-deleting destructor wrapper for COggFileRead; runtime Ogg/audio behavior remains separate proof. |

Read-back evidence:

- `ApplyWave1219FinalScore16CurrentRisk.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=84 tags_removed=0 missing=0 bad=0`
- `ApplyWave1219FinalScore16CurrentRisk.java apply`: `updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=84 tags_removed=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyWave1219FinalScore16CurrentRisk.java final dry`: `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 tags_removed=0 missing=0 bad=0`.
- Post exports: 16 metadata rows, 16 tag rows, 44 xref rows, 539 instruction rows, and 16 decompile rows.
- Queue after Wave1219: `6411/6411 = 100.00%`, with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`, 19 files, 176458631 bytes, `DiffCount=0`, `HashDiffCount=0`.

Boundary: Wave1219 closes the active current-risk focused static denominator and strengthens rebuild-grade static contracts. Runtime behavior, exact concrete layouts, exact source identity where not separately proven, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
