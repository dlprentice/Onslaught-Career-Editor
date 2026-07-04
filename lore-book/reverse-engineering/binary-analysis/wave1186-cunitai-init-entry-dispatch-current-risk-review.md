# Wave1186 CUnitAI Init / Entry Dispatch Current-Risk Review

Status: complete static current-risk comment/tag normalization; artifact commit `ff689ddf098e0ec97f655d0f901c3257fb050cba`; state closeout commit `abb5074838313596034cc28c99531aecd24a2450`; handoff pointer `82beb6b3ecc75287b0b331f3729b55b49c11e513`; pushed to origin/main
Date: 2026-06-06
Scope tag: `wave1186-cunitai-init-entry-dispatch-current-risk-review`

Wave1186 accounts for `4 CUnitAI init/indexed-entry dispatch current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra evidence:

- `0x004239f0 CUnitAI__InitDefaults_AutoConfigTestPath`
- `0x00444f00 CUnitAI__CallIndexedEntryVFunc10`
- `0x0044cd20 CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200`
- `0x0044d1f0 CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4`

The saved Ghidra names and signatures were already bounded. This wave normalized saved comments and tags only, adding rebuild-grade static-contract anchors and preserving the runtime/rebuild/no-noticeable-difference boundary.

One Codex read-only consult was used and recommended this residual CUnitAI init/indexed-entry dispatch slice. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `787/1179 = 66.75%`; current risk candidates: 6166; current focused candidates: 1176; live regenerated current focused candidates: 1176; remaining active focused work: 392; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `4` metadata rows, `4` tag rows, `8 xref rows`, `161 instruction rows`, and `4` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-143218_post_wave1186_cunitai_init_entry_dispatch_current_risk_review_verified`.

## Reviewed Rows

| Address | Name | Evidence |
| --- | --- | --- |
| `0x004239f0` | `CUnitAI__InitDefaults_AutoConfigTestPath` | Call xref from no-function caller `0x004239c5`; writes CUnitAI default flags/timers/state fields, copies `c:\beaautoconfigtest\` into `this+0x44`, copies `DAT_00624484` into `this+0x2d4`, and sets `this+0x318` to `0xffffffff` or `120000` based on `DAT_0066e94e`. |
| `0x00444f00` | `CUnitAI__CallIndexedEntryVFunc10` | Call xref from `0x0049500d SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10`; loads `(*(this+4))[entryIndex]`, returns `0` when absent, otherwise dispatches indexed-entry vfunc slot `+0x10`. |
| `0x0044cd20` | `CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200` | DATA vtable ref `0x005e4680`; `RET 0x10` confirms four stack dwords, subtracts `delta` from `this+0xe0`, compares against `DAT_005d856c`, dispatches vfunc byte offset `+0xc8` when flag bit 4 at `this+0x2c` is clear, and clamps to profile field `+0x18`. |
| `0x0044d1f0` | `CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4` | DATA vtable refs `0x005e239c`, `0x005e3e50`, `0x005e40ac`, `0x005e4308`, and `0x005e46f0`; calls `CUnitAI__SetStateTimestampCCToNow`, then dispatches vfunc byte offset `+0x38` when flag bit 4 at `unitAi+0x2c` is set. |

## Mutation Summary

The wave saved comment/tag normalization only: dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=42 missing=0 bad=0`, then `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=42 missing=0 bad=0`, then `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.

No rename, signature change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation occurred.

## Boundary

This wave strengthens the CUnitAI static contract needed for rebuild-grade static contracts and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove concrete CUnitAI/profile/entry-table layouts, exact source-body identity, runtime AI/defaulting/dispatch behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1186; wave1186-cunitai-init-entry-dispatch-current-risk-review; 787/1179 = 66.75%; 4 CUnitAI init/indexed-entry dispatch current-risk rows; current focused candidates: 1176; live regenerated current focused candidates: 1176; remaining active focused work: 392; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=42; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CUnitAI__InitDefaults_AutoConfigTestPath; CUnitAI__CallIndexedEntryVFunc10; CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200; CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4; SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10; c:\beaautoconfigtest\; DAT_00624484; DAT_0066e94e; DAT_005d856c; CUnitAI__SetStateTimestampCCToNow; 0 / 0 / 0; 6411/6411 = 100.00%; 8 xref rows; 161 instruction rows; 4 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-143218_post_wave1186_cunitai_init_entry_dispatch_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
