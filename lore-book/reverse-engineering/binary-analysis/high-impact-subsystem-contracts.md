# High-Impact Subsystem Contracts (Phase 5 Pass 2)

> Scope: baseline ownership/type/behavior contracts for remaining high-impact subsystems from the static RE completion plan.
> Last updated: 2026-03-01

## Contract Schema

Each subsystem contract row captures:

1. `name` (symbol-level anchor)
2. `owner proof` (class/debug-path/xref evidence)
3. `typed signature` (current best typed shape)
4. `behavior summary` (inputs/outputs/side effects)
5. `confidence` (`high`/`medium`/`low` + rationale)
6. `evidence links`

## Subsystem Contracts

| Subsystem | Function Contract(s) | Owner Proof | Typed Signature | Behavior Summary | Confidence | Evidence |
|---|---|---|---|---|---|---|
| AirUnit | `CAirUnit__Init` (`0x00402ad0`) | AirUnit debug path (`0x00622cf4`) + inheritance notes (`CUnit -> CAirUnit`) in index | `void __thiscall CAirUnit__Init(void * this, int param_1)` | Initializes air-unit runtime, creates trail/engine effects, then continues base-unit init flow | high (post-run read-back verified) | `functions/AirUnit.cpp/_index.md`, `functions/AirUnit.cpp/CAirUnit__Init.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| Carrier | `CCarrier__Init` (`0x00421a80`) | Carrier debug path (`0x006243bc`) + class-specific allocation/unwind ownership | `void __thiscall CCarrier__Init(void * this, int param_1)` | Constructor/init path that allocates carrier child objects and sets runtime state | high (post-run read-back verified) | `functions/Carrier.cpp/_index.md`, `functions/Carrier.cpp/CCarrier__Init.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| DiveBomber | `CDiveBomber__SelectTarget` (`0x00445070`) | DiveBomber debug path (`0x006289c0`) + class ownership notes in index | `void * __thiscall CDiveBomber__SelectTarget(void * this)` | AI target-selection routine for dive-bombing run decisions | high (post-run read-back verified) | `functions/DiveBomber.cpp/_index.md`, `functions/DiveBomber.cpp/CDiveBomber__SelectTarget.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| FEPDebriefing | `CFEPDebriefing__Initialize` (`0x00456780`) | Source-file/class ownership in dedicated frontend index | `int __fastcall CFEPDebriefing__Initialize(void * this)` | Seeds mission debrief page state and prepares kill/goodie presentation flow | medium-high (live signature verified; caller-side chain still sparse) | `functions/FEPDebriefing.cpp/_index.md`, `functions/FEPDebriefing.cpp/CFEPDebriefing__Initialize.md`, `high-impact-call-chain-appendix.md` |
| HeightField | `CHeightField__Load` (`0x0047f750`), `CHeightField__InitColorGradient` (`0x0047e8e0`) | HeightField debug path string + structured member-offset map in index | `void CHeightField::Load(int* pSizePtr)`, `void CHeightField::InitColorGradient(void)` | Loads terrain height data buffers and initializes color-gradient tables used by terrain rendering | high (typed shapes + data-layout context are explicit in docs) | `functions/HeightField.cpp/_index.md`, `functions/HeightField.cpp/CHeightField__Load.md`, `functions/HeightField.cpp/CHeightField__InitColorGradient.md` |
| Infantry | `CInfantry__Init` (`0x00488bb0`), `CInfantryGuide__SelectNearestTargetReader` (`0x0048ace0`) | Infantry debug path + infantry-guide class ownership in index | `void __thiscall CInfantry__Init(void * this, int param_1)` | Initializes infantry + guide subobjects and provides nearest-target selection helper for guide AI | high (post-run read-back verified for init signature) | `functions/Infantry.cpp/_index.md`, `functions/Infantry.cpp/CInfantry__Init.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| Mech | `CMech__InitLegMotion` (`0x0049f940`) | Mech class ownership in source-file index + leg-motion asset linkage | `void __thiscall CMech__InitLegMotion(void * this)` | Sets up mech leg-motion animation system and related movement state | high (post-run read-back verified) | `functions/Mech.cpp/_index.md`, `functions/Mech.cpp/CMech__InitLegMotion.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| PauseMenu | `PauseMenu__Init` (`0x004cde60`), `CPauseMenu__ResumeGameAndPersistOptions` (`0x004d06e0`) | PauseMenu source ownership + decompiled option-persistence behavior in index | `void __thiscall PauseMenu__Init(void * this)`, `void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * param_1)` | Initializes pause UI state and cheat-gated toggles; resume helper persists options/defaultoptions path | high (both signatures read-back verified; persistence chain documented) | `functions/PauseMenu.cpp/_index.md`, `functions/PauseMenu.cpp/PauseMenu__Init.md`, `functions/PauseMenu.cpp/CPauseMenu__ResumeGameAndPersistOptions.md`, `high-impact-call-chain-appendix.md` |
| ThunderHead | `CThunderHead__CreateLegMotion` (`0x004f4730`) | ThunderHead debug path (`0x00633240`) + owned subobject offset map in index | `void __thiscall CThunderHead__CreateLegMotion(void * this, void * param_1)` | Allocates/attaches thunderhead leg-motion controller object during boss setup | high (post-run read-back verified) | `functions/ThunderHead.cpp/_index.md`, `functions/ThunderHead.cpp/CThunderHead__CreateLegMotion.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| Unit | `CUnit__Init` (`0x004f86d0`), `CUnit__ApplyDamage` (`0x004f9a90`) | Unit source-file index + class-central behavior map | `void __thiscall CUnit__Init(void * this)`, `void __thiscall CUnit__ApplyDamage(void * this, float damageAmount, int damageType)` | Core unit spawn/equipment init and damage-processing contract (shield/armor/effects paths) | high (post-run read-back verified for both signatures) | `functions/Unit.cpp/_index.md`, `functions/Unit.cpp/CUnit__Init.md`, `functions/Unit.cpp/CUnit__ApplyDamage.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| world | `CWorld__LoadWorld` (`0x0050b9c0`), `CWorld__ShutdownAndClear` (`0x0050ada0`) | world debug path (`C:\dev\ONSLAUGHT2\world.cpp`) + lifecycle function cluster in index | `bool __thiscall CWorld__LoadWorld(void * this, void * levelName)` | World lifecycle contract: load/deserialize world resources, initialize world state, and teardown/reset path | high (post-run read-back verified; call-chain anchors expanded) | `functions/World.cpp/_index.md`, `functions/World.cpp/CWorld__LoadWorld.md`, `high-impact-call-chain-appendix.md`, `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |
| text | `CText__Init` (`0x004f21f0`), `CText__GetStringById` (`0x004f2580`) | text debug path + full CText structure mapping in index | `void CText::Init(uint languageId)`, `const wchar_t* CText::GetStringById(int text_id)` | Initializes localized text tables and resolves runtime string lookups by text id | high (typed signatures and structure context are explicit in docs) | `functions/text.cpp/_index.md`, `functions/text.cpp/CText__Init.md`, `functions/text.cpp/CText__GetStringById.md` |

## Residual Contract Gaps (Pass 2)

| Subsystem | Gap | Next Action |
|---|---|---|
| Signature hardening queue | 9-address queue executed with post-run read-back `9/9 OK` | Keep queue and read-back artifacts as gate evidence; update if any future signature refinements are applied |
| FEPDebriefing | Caller anchor is now documented via dedicated xref export (`0x005db9c0` data dispatch reference) | Monitoring only; no blocking action unless additional direct caller evidence is required |
| PauseMenu / text | Call-chain depth and fallback behavior contracts are now explicit and evidence-backed | Monitoring only (non-blocking) |

## Phase-5 Use

This file is the canonical pass-2 contract tracker for the high-impact subsystem bucket listed in `deep-validation-status.md`.
