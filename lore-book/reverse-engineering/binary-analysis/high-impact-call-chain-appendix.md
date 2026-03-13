# High-Impact Call-Chain Appendix (Phase 5)

> Scope: side-effect call-chain depth for frontend/world/text contracts in the static RE completion gate.
> Last updated: 2026-03-01

## Frontend Save/Options Persistence Chains

| Chain | Anchors | Side Effect |
|---|---|---|
| Load-game path | `CFEPLoadGame__DoLoad` (`0x00461e20`) -> `CCareer__Load(..., flag=1)` -> conditional `CFEPOptions__WriteDefaultOptionsFile(out_buf, size)` when `DAT_0082b5b0 == 0` | Loaded save buffer can overwrite `defaultoptions.bea` for next boot |
| Main-menu save path | `CFEPMain__Process` (`0x00462640`) callsites `0x00462893` (`CCareer__Save`) and `0x004628df` (`CFEPOptions__WriteDefaultOptionsFile`) with optional `PCPlatform__WriteSaveFile` in same branch | Menu transition/save flow can persist both slot data and global options snapshot |
| Pause resume/exit path | `CPauseMenu__ResumeGameAndPersistOptions` (`0x004d06e0`) -> `CCareer__Save` -> optional `PCPlatform__WriteSaveFile` -> `CFEPOptions__WriteDefaultOptionsFile` | Resume/exit can also update `defaultoptions.bea` |
| Debriefing path boundary | `CFEPDebriefing__Initialize` (`0x00456780`) populates debrief runtime state; dedicated xref export shows `from_addr=0x005db9c0` (`DATA`, indirect dispatch anchor) | Debriefing is upstream of save/options persistence paths above |

Primary evidence docs:
- `functions/FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md`
- `functions/FEPMain.cpp.md`
- `functions/Career.cpp/CCareer__Save.md`
- `functions/PauseMenu.cpp/CPauseMenu__ResumeGameAndPersistOptions.md`

## World Lifecycle Call-Chain Anchors

| Chain | Evidence |
|---|---|
| `CWorld__LoadWorldFile` (`0x0050b520`) -> `CWorld__LoadWorld` (`0x0050b9c0`) | `functions/World.cpp/_index.md` |
| `CWorld__LoadWorld` -> `CWorld__LoadWorldHeader` / `CWorld__InitLODLists` / `CWorld__SpawnInitialThings` | `functions/World.cpp/_index.md` function details |
| `CWorld__LoadWorld` -> `CWaypointManager__LoadWaypoints` | `functions/WaypointManager.cpp/_index.md` caller map |
| Caller anchor into `CWorld__LoadWorld` | `scratch/deep_semantic_tail_2026-02-27/pass2_semantic_wave145_prep/xrefs.tsv` line 21 (`CDXEngine__Unk_005475d0` call at `0x0050d11e`) |

## Text Lookup and Fallback Chain

| Function | Contracted Behavior |
|---|---|
| `CText__Init` (`0x004f21f0`) | Loads language DAT and seeds `mVersion`, `mCount`, `mTextPool`, `mAudioPool` |
| `CText__GetStringById` (`0x004f2580`) | v1/v2/v3 entry-table lookup by `text_id`; on miss logs error and returns `mTextPool` fallback |
| `CText__GetStringByIdAfter` (`0x004f2500`) | grouped-string lookup by offset from a matched id; on miss logs error and returns `mTextPool` fallback |

Primary evidence docs:
- `functions/text.cpp/CText__Init.md`
- `functions/text.cpp/CText__GetStringById.md`
- `functions/text.cpp/CText__GetStringByIdAfter.md`

## Signature Verification Snapshot (High-Impact Set, Post-Run Read-Back)

Pre-run baseline snapshot:
- `scratch/deep_semantic_tail_2026-02-27/all_after_wave217.tsv`

Post-run authoritative read-back:
- `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`9/9 status=OK`)

| Address | Function | Live Export Signature | Status |
|---|---|---|---|
| `0x00456780` | `CFEPDebriefing__Initialize` | `int __fastcall CFEPDebriefing__Initialize(void * this)` | verified typed |
| `0x004cde60` | `PauseMenu__Init` | `void __thiscall PauseMenu__Init(void * this)` | verified typed |
| `0x00402ad0` | `CAirUnit__Init` | `void __thiscall CAirUnit__Init(void * this, int param_1)` | verified typed |
| `0x00421a80` | `CCarrier__Init` | `void __thiscall CCarrier__Init(void * this, int param_1)` | verified typed |
| `0x00445070` | `CDiveBomber__SelectTarget` | `void * __thiscall CDiveBomber__SelectTarget(void * this)` | verified typed |
| `0x00488bb0` | `CInfantry__Init` | `void __thiscall CInfantry__Init(void * this, int param_1)` | verified typed |
| `0x0049f940` | `CMech__InitLegMotion` | `void __thiscall CMech__InitLegMotion(void * this)` | verified typed |
| `0x004f4730` | `CThunderHead__CreateLegMotion` | `void __thiscall CThunderHead__CreateLegMotion(void * this, void * param_1)` | verified typed |
| `0x004f86d0` | `CUnit__Init` | `void __thiscall CUnit__Init(void * this)` | verified typed |
| `0x004f9a90` | `CUnit__ApplyDamage` | `void __thiscall CUnit__ApplyDamage(void * this, float damageAmount, int damageType)` | verified typed |
| `0x0050b9c0` | `CWorld__LoadWorld` | `bool __thiscall CWorld__LoadWorld(void * this, void * levelName)` | verified typed |

Execution queue artifact (completed):
- `scratch/program_2026-03-01/phase5_signature_hardening_queue.tsv`
- Prepared headless postscript for this queue: `tools/ApplyPhase5HighImpactSignatureQueue.java`
