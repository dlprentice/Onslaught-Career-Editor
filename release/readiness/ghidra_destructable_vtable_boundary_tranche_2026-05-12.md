# Ghidra Destructable Vtable Boundary Tranche - 2026-05-12

Status: GREEN public-safe static Ghidra correction evidence.

This wave continued the saved-Ghidra static re-audit on destructable segment vtable slots exposed by the prior bridge tranche. It recovered three missing function starts and saved behavior-bounded names, signatures, comments, and tags after serialized dry/apply/read-back. Stuart's checked source snapshot does not currently include the full `DestructableSegmentsController.cpp` body, so these labels are behavior-backed static retail names, not exact source-body closure.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00443460` | `CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch` | Shared slot-0 dispatcher used by base/component/core/variant vtables; checks event code `3000` / `0x0bb8` before dispatching vfunc slot `+0x20`. |
| `0x00443830` | `CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex` | Standard/swap slot-4 helper deriving a clamped damage-stage index from fields `+0x0c`, `+0x10`, and `+0x40`. |
| `0x00443890` | `CDestroyableSegmentVariant__VFunc_03_ApplyDamage` | Shared leaf/end slot-3 damage body; subtracts damage, records last damage time/amount context, derives a source-facing break vector, marks break state, and dispatches slot `+0x20` when the segment breaks. |

Evidence:

- `tools/ApplyDestructableVtableBoundaryTranche.java` dry/apply passed with `targets=3 changed_or_would_change=3 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `3` metadata rows, `3` decompile exports, `8` xref rows, `591` instruction rows, `3` tag rows, `40` vtable-slot rows, `8` vtable evidence hits, `8` xref evidence hits, `11` instruction evidence hits, and no stale-token or comment-overclaim failures.
- Focused validation passed: `py -3 tools\ghidra_destructable_vtable_boundary_tranche_probe_test.py`, `py -3 -m py_compile tools\ghidra_destructable_vtable_boundary_tranche_probe.py tools\ghidra_destructable_vtable_boundary_tranche_probe_test.py`, and `cmd.exe /c npm run test:ghidra-destructable-vtable-boundary-tranche`.
- The refreshed all-functions baseline reports `5982` total functions, `0` legacy weak names, `1951` undefined signatures, and `2075` `param_N` signatures.
- The refreshed quality queue reports `5982` functions, `1151` commented functions, `4831` commentless functions, `1951` undefined signatures, and `2075` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1151/5982 = 19.24%`, strict clean-signature `1088/5982 = 18.19%`. The `20%` value is not a milestone or acceptance gate.
- The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_215540_post_wave352_destructable_vtable_verified` with `19` files, `152931207` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/destructable-vtable-boundary-wave352/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects saved function boundaries, names, signatures, comments, and tags for three destructable vtable targets, but it does not prove exact source identity, concrete class layout, local/type recovery, runtime destruction/cascade/random-damage/rubble/mesh behavior, BEA launch, game patching, or rebuild parity.
