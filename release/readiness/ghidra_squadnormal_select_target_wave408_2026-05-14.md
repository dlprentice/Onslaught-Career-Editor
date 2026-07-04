# Ghidra SquadNormal Select-Target Hardening - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave408 hardened the saved Ghidra metadata for `0x00477cb0` / `CSquadNormal__SelectBestEngagementTarget`. This is a serialized static Ghidra signature/comment/tag read-back wave only; the saved name was preserved.

| Address | Prior saved state | Saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x00477cb0` | `int * __stdcall CSquadNormal__SelectBestEngagementTarget(void * param_1)` | `void * __stdcall CSquadNormal__SelectBestEngagementTarget(void * squad)` | Fresh instruction read-back shows one explicit stack argument and `RET 0x4`, with no ECX thiscall setup. The body selects one of `DAT_00855090`, `DAT_008550b0`, or `DAT_008550c0` based on squad state at `+0x7c`, reads squad position/support context through vtable slots `+0x120` and `+0x124`, walks candidate-list entries, applies flag/range/faction/support filters, scores candidates from squad config weights under `squad+0xa0`, calls support/escort helpers, and falls back through `candidate+0x148` before returning. |

## Correction Boundary

The current retail body supports the `CSquadNormal__SelectBestEngagementTarget` behavior label and a one-argument stack-call signature. It does not support a hidden ECX `thiscall` receiver, and the old `param_1` / `int *` metadata was under-specified for the queue.

## Validation

- `ApplySquadNormalSelectTargetWave408.java` dry run passed with `updated=0 skipped=1 would_update=1 missing=0 bad=0`.
- `ApplySquadNormalSelectTargetWave408.java` apply run passed with `updated=1 skipped=0 would_update=0 missing=0 bad=0` and `REPORT: Save succeeded`.
- Read-back verified `1` metadata row, `1` tag row, `2` xref rows, `321` instruction rows, and the post-apply decompile text.
- Direct xrefs are `CSquadNormal__ScheduleTargetReaderRefresh` at callsite `0x004e815a` and a no-function callsite at `0x004ea584`; the latter remains boundary follow-up context, not a named function claim.
- Refreshed queue telemetry reports `6028` functions, `1561` commented functions, `4467` commentless functions, `1909` undefined signatures, and `1855` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1561/6028 = 25.90%`, strict clean-signature `1499/6028 = 24.87%`.
- The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_075916_post_wave408_squadnormal_select_target_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove exact CSquadNormal/source identity, does not prove candidate struct layout, does not prove global list semantics, does not prove runtime AI behavior, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
