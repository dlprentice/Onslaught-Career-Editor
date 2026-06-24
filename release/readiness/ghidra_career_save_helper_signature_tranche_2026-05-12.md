# Ghidra Career Save Helper Signature Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

This wave revisited a coherent `Career.cpp` / save / Goodies helper cluster after fresh saved-project read-back. It updated saved Ghidra signatures, comments, and tags for 21 already named functions:

- `0x0041b770` `CCareerNode__SetBaseThingExistTo`
- `0x0041b7b0` `CCareer__GetLevelStructure`
- `0x0041b940` `CCareerNode__GetChildLinks`
- `0x0041b9f0` `CCareerNode__GetParentLinks`
- `0x0041bb20` `CCareer__DoesBaseThingExist`
- `0x0041bbb0` `CCareer__IsWorldLater`
- `0x0041bc60` `CCareer__Later`
- `0x0041bdf0` `CCareer__ReCalcLinks`
- `0x0041c240` `TOTAL_S_GRADES`
- `0x0041c330` `CCareer__GetGradeForWorld`
- `0x0041c450` `CCareer__CountGoodies`
- `0x00420ab0` `CGrade__ctor_char`
- `0x00420ac0` `CGrade__operator_gte`
- `0x00420af0` `CCareer__GetNode`
- `0x004213c0` `CCareer__SaveWithFlag`
- `0x00421430` `CCareer__GetSaveSize`
- `0x00421550` `CCareer__GetAndResetGoodieNewCount`
- `0x00421560` `CCareer__GetAndResetFirstGoodie`
- `0x00421570` `CCareer__IsEpisodeAvailable`
- `0x004218f0` `CCareer__GetKillCounterTopByte_23F4`
- `0x00421970` `CCareer__NodeArrayAt`

No function names were changed. The main correction was replacing stale wording on `CCareer__ReCalcLinks`: the saved comment now identifies the world-500 `mSlots` branch at career `+0x240c` bits `29/30` for source slots `61/62`, and explicitly says those checks are not god-mode flags.

## Evidence

- `tools/ApplyCareerSaveHelperSignatureTranche.java` dry run: `updated=0 skipped=21 renamed=0 missing=0 bad=0`.
- `tools/ApplyCareerSaveHelperSignatureTranche.java` apply: `updated=21 skipped=0 renamed=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `21/21` metadata rows, `21/21` decompile exports, `452` xref rows, `1953` instruction rows, and `21/21` tag rows.
- `cmd.exe /c npm run test:ghidra-career-save-helper-signature-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5884` functions, `818` commented functions, `5066` commentless functions, `1988` undefined signatures, and `2269` `param_N` signatures.

## Claim Boundary

This is saved static Ghidra signature/comment/tag evidence only. It does not prove runtime save/load behavior, runtime Goodies unlock behavior, exact source identity for every selected helper body, concrete `CCareer` / `SPtrSet` / grade / options-tail layouts, local variable recovery, structure typing, BEA launch, game patching, copied-save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/career-save-wave329/current/`.
