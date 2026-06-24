# Ghidra Options / Platform Input Comment Tranche - 2026-05-13

Status: GREEN public-safe saved-Ghidra evidence

## Summary

Serialized headless Ghidra dry/apply/read-back hardened comments and tags for `7` options-entry and platform-input targets after focused metadata, decompile, xref, instruction, tag, and source-context review.

The saved names and signatures were already aligned with the current evidence. This pass added proof-boundary comments/tags, refreshed the whole-database quality queue, and backed up the actual live Ghidra project to `G:`.

## Targets

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0042d260` | `OptionsEntries__InitSingleBindingEntry` | Records the active byte, entry id, slot-0 device/scan/virtual-key fields, slot-1 defaults, and `RET 0x14` context. |
| `0x0042d2b0` | `OptionsEntries__InitDualBindingEntry` | Records the active byte, entry id, slot-0 and slot-1 metadata fields, and `RET 0x20` context. |
| `0x0042d300` | `OptionsEntries__InitSentinelEntry` | Records the cleared active byte and `-1` sentinel entry id used by the options-entry tables. |
| `0x0042d310` | `PlatformInput__InitMouse` | Records DirectInput mouse-device creation, data-format/cooperative-level setup, zeroed state, profiler reset, cursor centering, and enabled global input state. |
| `0x0042d3b0` | `PlatformInput__ShutdownMouse` | Records mouse-device unacquire/release, disabled global state, non-dev-mode cursor-position snapshot, and profiler reset. |
| `0x0042d420` | `PlatformInput__PollMouseMotion` | Records DIMOUSESTATE-style global zeroing, device-state read, reacquire on `0x8007001e`, and non-dev-mode delta/wheel accumulation. |
| `0x0042d4d0` | `PlatformInput__PollMouseState` | Records the shared state/reacquire path, delta/wheel update, and left/right/middle held/edge masks `0x80`, `0x8000`, and `0x800000`. |

## Validation

- Headless dry run: `targets=7 updated=0 skipped=7 failed=0`.
- Headless apply: `targets=7 updated=7 skipped=0 failed=0`, with `REPORT: Save succeeded`.
- Read-back exports: `7` metadata rows, `7` decompile exports, `99` xref rows, `847` focused instruction rows, and `7` tag rows.
- Focused probe: `PASS`; `7` xref evidence hits, `7` instruction evidence hits, `0` stale signature hits, and `0` overclaim hits.
- Whole-database refresh: `6008` functions, `1250` commented functions, `4758` commentless functions, `1948` `undefined` signatures, and `2019` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1250/6008 = 20.81%`; strict clean-signature `1188/6008 = 19.77%`. The `20%` value is not a milestone.
- Actual live Ghidra backup: `G:\GhidraBackups\BEA_20260513_051500_post_wave363_options_platform_input_verified`, verified at `19` files, `153127815` bytes, and `HashDiffCount=0`.

## Claim Boundary

This proves saved static retail Ghidra names, signatures, comments, tags, selected xrefs, and selected instruction/decompile read-back for the `7` listed targets.

It does not prove exact Stuart-source method identity, concrete global layouts/types, local variables, runtime input behavior, BEA launch behavior, game patching, or rebuild parity.
