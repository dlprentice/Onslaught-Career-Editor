# Wave1171 D3D Device Profile Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1171-d3d-device-profile-current-risk-review`

Wave1171 accounts for two D3D device profile current-risk rows from the `wave1108-current-risk-rank` denominator with fresh Ghidra export evidence. The pass is read-only: no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. A Codex read-only consult returned a different message/particle candidate that is deferred as a likely Wave1172 cluster; Codex root selected this D3D slice locally.

| Address | Saved function | Static read-back evidence |
| --- | --- | --- |
| `0x00420cd0` | `D3DDeviceProfileTable__GetAdapterRecord` | Called by `0x00420b10 OptionsTail_Write`; indexes the `DAT_00855bb0` display/profile table base with a `0x516c` stride and falls back to the active adapter index at `+0x32e40` when `adapterIndex == -1`. |
| `0x00420d10` | `D3DDeviceProfile__PackDeviceIndexKey` | Called by `0x00420b10 OptionsTail_Write` and `0x00420d70 OptionsTail_Read`; packs a display mode/profile record into the persisted `g_D3DDeviceIndex`-style key using low 16 record bits, masked mode bits in bits 16-30, and a high-bit format marker for formats `0x14`, `0x15`, or `0x16`. |

Evidence counts:

- Fresh Ghidra exports verified `2` metadata rows, `2` tag rows, `3` xref rows, `54` instruction rows, and `2` decompile rows.
- Queue/static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`.
- Wave1108 current focused accounting advances to `668/1179 = 56.66%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 511.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-064430_post_wave1171_d3d_device_profile_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The two selected D3D profile rows still read back with saved names, signatures, comments, xrefs, instructions, and decompile exports.
- The profile-table accessor remains tied to options-tail write persistence.
- The device-index packing helper remains tied to both options-tail write and read paths.

What remains unproven:

- Runtime Direct3D device/profile selection behavior.
- Exact display/profile table layout beyond observed static offsets and bit packing.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1171; wave1171-d3d-device-profile-current-risk-review; 668/1179 = 56.66%; 2 D3D device profile current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 511; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult deferred; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 54 instruction rows; D3DDeviceProfileTable__GetAdapterRecord; D3DDeviceProfile__PackDeviceIndexKey; OptionsTail_Write; OptionsTail_Read; [maintainer-local-ghidra-backup-root]\BEA_20260606-064430_post_wave1171_d3d_device_profile_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
