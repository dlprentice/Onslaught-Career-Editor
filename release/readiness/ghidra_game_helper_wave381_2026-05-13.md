# Ghidra Game Helper Wave381 Readiness Note

Status: public-safe static RE evidence
Date: 2026-05-13

## Summary

Wave381 serialized a focused headless dry/apply/read-back pass over `9` saved Ghidra targets in the game, EndLevelData, console/status, and frontend text helper area. The pass corrected four stale owner/name labels, corrected two generic objective-count labels, and hardened three existing CGame helper signatures/comments/tags. This is saved static retail Ghidra evidence only.

## Saved Targets

| Address | Saved signature | Evidence summary |
| --- | --- | --- |
| `0x004496e0` | `bool __fastcall CEndLevelData__IsAllSecondaryObjectivesComplete(void * this)` | Corrects older `CCareer__AreSecondaryObjectivesComplete` owner label; source-parity secondary-objective status scan at `this+0x4d0`, with no-secondary-objective error context. |
| `0x00470650` | `void __fastcall CGame__DrawDebugStuff(void * this)` | Corrects older debug-memory label to source-parity `CGame::DrawDebugStuff` debug overlay behavior. |
| `0x00472240` | `void __cdecl CConsole__AppendToStatusBufferV(void * console, char * format)` | Corrects older CGame owner label; appends formatted status/debug overlay text through `vsprintf` using `console+0x2710`. |
| `0x00472270` | `short * __cdecl Frontend__XorWideTextBlock100BytesToScratch(short * encoded_text, short * xor_mask)` | Corrects older CGame owner and block-size wording; XORs a `0x64` byte wide-text block into `DAT_00679e18`. |
| `0x00472570` | `bool __thiscall CGame__DoWeWantMesh(void * this, char * mesh)` | Source-parity mesh filter for player cockpit and wingman mesh strings. |
| `0x004725f0` | `int __thiscall CGame__GetPlayerLives(void * this, int player_index)` | Source-parity player-lives selector for player index `1` or `2`. |
| `0x00472650` | `bool __fastcall CGame__IsRunningResources(void * this)` | Source-parity current-level versus last resource-loaded level comparison. |
| `0x00472670` | `int __fastcall CGame__GetNumPrimaryObjectives(void * this)` | Corrects older `CGame__CountActiveSlots_A` label; counts defined primary objective rows at `this+0x4c`. |
| `0x00472690` | `int __fastcall CGame__GetNumSecondaryObjectives(void * this)` | Corrects older `CGame__CountActiveSlots_B` label; counts defined secondary objective rows at `this+0x9c`. |

## Validation

- `py -3 tools\ghidra_game_helper_wave381_probe_test.py` initially failed red before implementation with `ModuleNotFoundError`.
- `py -3 tools\ghidra_game_helper_wave381_probe_test.py` passed with `2/2` tests.
- `cmd.exe /c npm run test:ghidra-game-helper-wave381` passed with status `PASS`, `9` targets, `12` xref evidence hits, and `18` instruction evidence hits.
- `py -3 -m py_compile tools\ghidra_game_helper_wave381_probe.py tools\ghidra_game_helper_wave381_probe_test.py` passed.
- Headless dry/apply reported dry `updated=0 skipped=9 renamed=0 would_rename=6 missing=0 bad=0` and apply `updated=9 skipped=0 renamed=6 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back verified `9` metadata rows, `9` decompile exports, `22` xref rows, `405` instruction rows, and `9` tag rows.
- The refreshed live queue reports `6026` functions, `1393` commented functions, `4633` commentless functions, `1939` undefined signatures, and `1934` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1393/6026 = 23.12%`, strict clean-signature `1328/6026 = 22.04%`.
- The live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_160255_post_wave381_game_helper_verified` with `19` files, `153652103` bytes, and `HashDiffCount=0`.

## Not Proven

- Runtime objective, debug overlay, console/status, frontend text, resource-loading, or lives behavior is not proven by this static pass.
- Exact class layouts, local variable names, and structure types remain open.
- Complete EndLevelData source-file coverage is not proven.
- BEA launch behavior, executable patching, packaged-app behavior, and rebuild parity remain unproven.
