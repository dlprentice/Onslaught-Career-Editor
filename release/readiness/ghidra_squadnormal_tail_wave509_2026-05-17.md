# Ghidra CSquadNormal Tail Wave509 Readiness Note

Date: 2026-05-17

## Summary

Wave509 saved static Ghidra names, signatures, comments, and tags for 15 adjacent CSquad/CSquadNormal tail helpers. The tranche includes 4 renames and focuses on CSquad base init, CSquadNormal process/formation/iterator/merge/spawn/faction helpers, plus two owner-neutral stale-owner corrections and one active-reader helper correction.

This is static retail Ghidra evidence only. It does not prove exact CSquad, CSquadNormal, CGenericActiveReader, shared-vfunc, member-list, reader-node, global-list, faction enum, event, or formation layouts. It also does not prove runtime AI behavior, runtime formation/merge/spawn behavior, BEA launch behavior, game patching, or rebuild parity.

## Targets

| Address | Saved signature |
| --- | --- |
| `0x004e5e70` | `void __thiscall CSquad__Init(void * this, void * init)` |
| `0x004e6610` | `bool __fastcall SharedState__IsTimer88PendingAndState7CZero(void * this)` |
| `0x004e66d0` | `void __thiscall SharedVFunc__ForwardProcessNoOp(void * this, void * process_arg)` |
| `0x004e7110` | `int __thiscall CSquadNormal__Process(void * this, void * process_arg)` |
| `0x004e81d0` | `int __fastcall CSquadNormal__EvaluateLeaderTargetPursuitMode(void * this)` |
| `0x004e83b0` | `void __thiscall CSquadNormal__PruneDeadMembersAndReschedule(void * this, int schedule_event)` |
| `0x004e84e0` | `bool __fastcall CSquadNormal__ResolveFormationSlotConflicts(void * this)` |
| `0x004e8730` | `void __fastcall CSquadNormal__BuildColumnFormation(void * this)` |
| `0x004e8930` | `void __fastcall CSquadNormal__BuildAttackFormation(void * this)` |
| `0x004e8dd0` | `bool __fastcall CSquadNormal__ShouldSwitchToAttackFormation(void * this)` |
| `0x004e8ed0` | `void * __fastcall CSquadNormal__CreateIterator(void * this)` |
| `0x004e8f80` | `void __thiscall CSquadNormal__TryMergeWithNearbySquad(void * this, int force_merge)` |
| `0x004e91f0` | `void __fastcall CSquadNormal__SpawnMembers(void * this)` |
| `0x004e9570` | `void __thiscall CSquadNormal__SetFactionAndRefreshGlobalLists(void * this, int faction_state)` |
| `0x004e97e0` | `bool __thiscall CGenericActiveReader__SwapWithCandidateIfFormationCloser(void * this, void * candidate_reader)` |

## Evidence

- `CSquad__Init` corrects the generic `CSquad__VFunc_09_004e5e70` label. Vtable read-back places it at CSquad table `0x005def1c` slot 9, and `CSquadNormal__Init` calls it while initializing the derived squad.
- `SharedState__IsTimer88PendingAndState7CZero` corrects stale `CExplosionInitThing` ownership. The ECX-only body tests `DAT_00672fd0`, `this+0x88`, and `this+0x7c`; exact owner and timer semantics remain open.
- `SharedVFunc__ForwardProcessNoOp` corrects stale `CWaypoint` ownership. `RET 0x4` proves one stack argument while ECX is passed through to the delegated process/no-op helper at `0x00452b60`.
- `CSquadNormal__Process` now has a one-argument thiscall signature matching the observed raw caller and process_arg forwarding. It connects leader sync, pursuit mode, path/reader refresh, column/attack formation, spawn/split, merge, and member-position averaging.
- `CSquadNormal__CreateIterator` and `CSquadNormal__SpawnMembers` no longer have undefined signatures; both are ECX-only helpers with static behavior read-back.
- `CGenericActiveReader__SwapWithCandidateIfFormationCloser` corrects the old CSquadNormal-owner label. The function operates on active-reader nodes and is called by `CSquadNormal__ResolveFormationSlotConflicts`.
- `CSquadNormal__SetFactionAndRefreshGlobalLists` propagates the new state to member units, removes the squad from `DAT_008550c0` / `DAT_008550b0`, and re-adds it for observed values `0`, `1`, and `6`.

Artifacts are under `subagents/ghidra-static-reaudit/wave509-squadnormal-tail-004e5e70/`.

## Verification

- `ApplySquadNormalTailWave509.java` dry: `updated=0 skipped=15 renamed=0 would_rename=4 missing=0 bad=0`.
- `ApplySquadNormalTailWave509.java` apply: `updated=15 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`.
- `ApplySquadNormalTailWave509.java` verify dry: `updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0`.
- All three mutation passes reported `REPORT: Save succeeded`.
- Post-readback exports verified `15` metadata rows, `15` tag rows, `27` xref rows, `4815` instruction rows, `15` decompile exports, and `384` vtable-slot rows.
- `py -3 tools\ghidra_squadnormal_tail_wave509_probe.py --check` passed.
- `cmd.exe /c npm run test:ghidra-squadnormal-tail-wave509` passed.
- Queue refresh passed and reports `6078` functions, `2363` commented, `3715` commentless, `1629` exact-undefined signatures, and `1450` `param_N` signatures.
- Current telemetry proxies are comment-backed `2363/6078 = 38.88%` and strict comment-plus-clean-signature `2309/6078 = 37.99%`; these are progress telemetry only, not completion certification.
- Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260517-173706_post_wave509_squadnormal_tail_verified` with `19` files, `158206855` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

- Runtime squad AI, formation, merge, spawn/split, faction propagation, or event behavior.
- Exact source-body identity for the checked helpers.
- Concrete CSquad/CSquadNormal/member-reader/global-list/faction/event layouts.
- BEA launch behavior, game patching behavior, or rebuild parity.
