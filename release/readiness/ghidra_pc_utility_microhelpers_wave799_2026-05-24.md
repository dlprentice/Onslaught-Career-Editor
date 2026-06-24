# Ghidra PC Utility Microhelpers Wave799 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `pc-utility-microhelpers-wave799`

Wave799 PC utility microhelpers saved comments/tags for six raw commentless PC/game/front-end utility rows from `0x00441730 CLIParams__SetField04` through `0x00441e40 CGame__ClearDwordValue`. The pass also corrected one narrow phantom-parameter signature on `0x00441730 CLIParams__SetField04`. It made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00441730 CLIParams__SetField04` | `void __thiscall CLIParams__SetField04(void * this, int field04_value)` | Called from `CLIParams__ParseCommandLine` at `0x004240a0`; instruction evidence loads `[ESP+4]`, stores to `[ECX+4]`, and returns with `RET 0x4`, proving the older `unused_flags` parameter was phantom. Stuart source layout suggests field `+4` aligns with `CCLIParams::mNoStaticShadows`, but retail field identity and runtime CLI effects remain unproven. |
| `0x00441b10 CGame__SetGlobalSelectionSnapshot` | Existing `void __cdecl` signature plus comment/tags | Called by `CFrontEnd__Render`, `CGame__Update`, and `CGame__DrawGameStuff`; copies optional four-dword snapshot into `0x0066eb80` through `0x0066eb8c`, or writes sentinel `0xffffffff` at `0x0066eb84`; sets pending flag `0x0066ff74` and mode byte `0x0066ff75`. |
| `0x00441b80 Platform__ProcessPendingScreenDump` | Existing no-arg signature plus comment/tags | Called by `PCPlatform__DeviceFlip`; checks `0x0066ff74`, formats numbered DDS/BMP dump paths from `0x0066ff78`, uses the snapshot around `0x0066eb80`, calls Direct3D surface/save helper paths, prints CConsole status/error messages, increments the counter, and clears the pending flag. |
| `0x00441e20 CDXFrontEndVideo__ClearByteFlag` | Existing `void __thiscall` signature plus comment/tags | Called by `CDXFrontEndVideo__Render`; writes zero to the byte pointed to by `ECX`. Exact owning field offset remains unproven. |
| `0x00441e30 CDXFrontEndVideo__SetByteFlagAndReturnOld` | Existing `int __thiscall` signature plus comment/tags | Called by `CDXFrontEndVideo__Render`; reads old low byte at `[ECX]`, writes `1`, and returns old byte in `AL`; upper `EAX` bits are not semantically proven. |
| `0x00441e40 CGame__ClearDwordValue` | Existing `void __thiscall` signature plus comment/tags | Called by `CGame__InitRestartLoop`; clears the dword pointed to by `ECX`. Exact owning `CGame` field identity remains unproven. |

Read-back evidence:

- `ApplyPcUtilityMicrohelpersWave799.java dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=5 missing=0 bad=0`
- `ApplyPcUtilityMicrohelpersWave799.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=5 missing=0 bad=0`
- `ApplyPcUtilityMicrohelpersWave799.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 6 metadata rows, 6 tag rows, 9 xref rows, 222 instruction rows, and 6 decompile rows.
- Queue after Wave799: 6098 total, 5552 commented, 546 commentless, 0 exact-undefined signatures, 0 param_N signatures, comment-backed proxy `5552/6098 = 91.05%`, strict clean-signature proxy `5552/6098 = 91.05%`.
- The commentless high-signal, signature, and name-confidence queues are empty.
- Next raw commentless row: `0x00445010 CMCBuggy__GetTargetValueOrFallback`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-063302_post_wave799_pc_utility_microhelpers_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The six target rows exist in the saved Ghidra project.
- The saved comments and tags include `pc-utility-microhelpers-wave799` and `wave799-readback-verified`.
- `0x00441730 CLIParams__SetField04` now has the saved one-argument `RET 0x4` signature without the phantom `unused_flags` parameter.
- The observed helper bodies are static retail Ghidra evidence tied to instruction, xref, decompile, metadata, tag, queue, and backup read-back artifacts.

What remains unproven:

- Exact source-body identity.
- Exact object/global field ownership beyond the stated bounded evidence.
- Runtime command-line, screenshot, Direct3D/filesystem, restart-loop, or Bink/video behavior.
- BEA patching behavior.
- Rebuild parity.
