# Ghidra UnitAI / DiveBomber / Dropship Signature Tranche - 2026-05-13

Status: GREEN public-safe static Ghidra signature evidence.

This wave continued the saved-Ghidra static re-audit in the UnitAI / DiveBomber / Dropship neighborhood. It corrected stale destructor-style labels, hardened names/signatures/comments/tags for adjacent door-wing and dropship helpers, and preserved a narrow claim boundary after serialized dry/apply/read-back.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00445380` | `CDiveBomberAI__scalar_deleting_dtor` | Scalar-deleting destructor wrapper over `CDiveBomberAI__dtor_base`, with conditional object free and `RET 0x4`. |
| `0x004453a0` | `CDiveBomberAI__dtor_base` | Destructor-base cleanup: tracked-set removals plus `CMonitor__Shutdown`. |
| `0x00445440` | `CDiveBomberGuide__scalar_deleting_dtor` | Scalar-deleting destructor wrapper over `CDiveBomberGuide__dtor_base`, with conditional object free and `RET 0x4`. |
| `0x00445460` | `CDiveBomberGuide__dtor_base` | Guide destructor-base cleanup for the tracked-set entry and monitor shutdown. |
| `0x00445570` | `CUnitAI__PlayOpenAnimationIfState1Or3` | Door-wing helper checks state `+0x280`, resolves the open animation, and dispatches animation vfunc `+0xf0`. |
| `0x004455c0` | `CUnitAI__PlayCloseAnimationIfState0Or2` | Door-wing helper checks state `+0x280`, resolves the close animation, and dispatches animation vfunc `+0xf0`. |
| `0x00445610` | `CUnitAI__AdvanceOpenCloseShootAnimationState` | Door-wing animation-state helper resolves shoot/close/open-style animation names and updates state `+0x280`. |
| `0x00445ad0` | `CUnitAI__UpdateDoorWingEngagement_CloseRange` | Close-range engagement helper updates door-wing tracking fields, calls open/close animation helpers, and dispatches movement vfunc context. |
| `0x00445f40` | `CUnitAI__UpdateDoorWingEngagement_MidRange` | Mid-range engagement helper samples target/weapon context and can dispatch vfunc `+0xf4`. |
| `0x00446150` | `CUnitAI__UpdateDoorWingEngagement_LongRange` | Long-range engagement helper toggles tracking fields and can call open-tracking or close-animation paths. |
| `0x00446400` | `CUnitAI__EnterDoorWingOpenTrackingState` | Door-wing helper enters open tracking and calls `CUnitAI__PlayOpenAnimationIfState1Or3`. |
| `0x00446d70` | `CDropship__Init` | Dropship initializer selects `wingflat` / `doorclosed` animation context, creates CMCDropship component context, enumerates thruster nodes, and resolves `Thruster Dust Effect`. |
| `0x00447040` | `CDropshipAI__scalar_deleting_dtor` | Scalar-deleting destructor wrapper over `CDropshipAI__dtor_base`, with conditional object free and `RET 0x4`. |
| `0x00447060` | `CDropshipAI__dtor_base` | Dropship AI destructor-base cleanup: tracked-set removals plus `CMonitor__Shutdown`. |
| `0x00447100` | `CDropship__dtor_base` | Dropship cleanup removes the unit from the occupancy grid and delegates to `CAirUnit__dtor_base`. |
| `0x00447120` | `CDropship__ProcessDoorThrustersAndChildUnits` | Dropship vtable body processes dooropening/doorclosing state, thruster/child-unit linked lists, shadow-height helpers, and pickup/effect context. |
| `0x00447a40` | `CUnitAI__SetDoorWingState2AndClampYawDelta` | Door-wing helper validates cached anchor fields, sets state `+0x27c` to `2`, and clamps yaw delta into `+0x2a0`. |
| `0x00447ac0` | `CUnitAI__PlayWingFoldedAnimationAndSetState3` | Door-wing helper sets state `+0x27c` to `3`, clears `+0x290`, updates occupancy/shadow context, resolves `wingfolded`, and dispatches animation vfunc `+0xf0`. |

Evidence:

- `tools/ApplyUnitAiDiveDropshipSignatureTranche.java` dry/apply passed with dry `targets=18 updated=0 skipped=18 failed=0` and apply `targets=18 updated=18 skipped=0 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `18` metadata rows, `18` decompile exports, `20` xref rows, `18` tag rows, `64` vtable-slot rows, `9` focused xref evidence hits, and `18` focused instruction evidence hits.
- Focused validation passed: `py -3 tools\ghidra_unitai_dive_dropship_signature_probe_test.py`, `py -3 -m py_compile tools\ghidra_unitai_dive_dropship_signature_probe.py tools\ghidra_unitai_dive_dropship_signature_probe_test.py`, and `cmd.exe /c npm run test:ghidra-unitai-dive-dropship-signature`.
- The focused probe reports `0` stale target-name hits, `0` stale target-signature hits, `2` external stale-reference hits, and `0` overclaim hits. The external stale references are follow-up debt in called helpers outside this tranche, not failed Wave358 target corrections.
- The refreshed all-functions baseline reports `6008` total functions, `0` legacy weak names, `1949` undefined signatures, and `2040` `param_N` signatures.
- The refreshed quality queue reports `6008` functions, `1214` commented functions, `4794` commentless functions, `1949` undefined signatures, and `2040` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1214/6008 = 20.21%`, strict clean-signature `1148/6008 = 19.11%`. The `20%` value is not a milestone or acceptance gate; the objective remains as close to `100%` evidence-grade static RE as possible.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_014424_post_wave358_unitai_dive_dropship_verified` with `19` files, `153029511` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/unitai-dive-dropship-wave358/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects and hardens eighteen UnitAI / DiveBomber / Dropship-adjacent saved functions, but it does not prove exact Stuart-source method identities, concrete UnitAI/DiveBomber/Dropship layouts, local/type recovery, runtime AI/door/wing/thruster/child-unit behavior, BEA launch, game patching, or rebuild parity.
