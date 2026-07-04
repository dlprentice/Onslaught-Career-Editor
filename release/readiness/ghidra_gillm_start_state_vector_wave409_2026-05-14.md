# Ghidra CGillM State-Vector Owner Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave409 corrected saved Ghidra metadata for `0x0047a160` from the older `CExplosionInitThing__StartState1WithStoredMotionVector` owner label to `CGillM__StartState1WithStoredMotionVector`. This is serialized static Ghidra name/signature/comment/tag read-back only.

| Address | Prior saved state | Saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x0047a160` | `void __fastcall CExplosionInitThing__StartState1WithStoredMotionVector(void * param_1)` | `void __thiscall CGillM__StartState1WithStoredMotionVector(void * this)` | CGillM RTTI vtable `0x005e0b30` slot 100 at `0x005e0cc0` points here. Neighboring checked CGillM slots include slot 66 `CGillM__UpdateGroundedVerticalDrift`, slot 117 `CGillM__InitLegMotion`, slot 118 `CGillM__InitGillMAIComponent`, and slot 119 `CGillM__InitTerrainGuideComponent`. The body skips when state field `+0x244` is already `1` or `2`, copies the stored four-dword motion vector at `+0x278` into a virtual dispatch at vtable +0xf4 with a zero flag, then sets `+0x244` to `1`. |

## Correction Boundary

The vtable evidence supersedes the older CExplosionInitThing label. Stuart's source tree is useful architecture context, but the current submodule does not contain a matching `GillM.cpp` source body, so the exact source virtual name stays open.

## Validation

- Headless dry run: `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`; `REPORT: Save succeeded`.
- Headless apply: `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`; `REPORT: Save succeeded`.
- Read-back verified `1` metadata row, `1` tag row, `1` DATA xref row from `0x005e0cc0`, `121` instruction rows, post-apply decompile text, and `128` CGillM vtable-slot rows.
- Focused unit tests passed `3/3`, Python compile passed, and the direct/package-script probes passed.
- Refreshed queue telemetry reports `6028` functions, `1562` commented functions, `4466` commentless functions, `1909` undefined signatures, and `1854` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1562/6028 = 25.91%`; strict clean-signature `1500/6028 = 24.88%`.
- The live Ghidra project backup was verified on `[maintainer-local-backup-volume]` at `[maintainer-local-ghidra-backup-root]\BEA_20260514_083210_post_wave409_gillm_state_vector_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove exact source virtual name, does not prove concrete CGillM layout, does not prove runtime movement behavior, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
