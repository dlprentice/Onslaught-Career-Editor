# Wave1186 CUnitAI Init / Entry Dispatch Current-Risk Readiness Note

Status: complete static current-risk comment/tag normalization; artifact commit `ff689ddf098e0ec97f655d0f901c3257fb050cba`; state closeout commit `abb5074838313596034cc28c99531aecd24a2450`; handoff pointer `82beb6b3ecc75287b0b331f3729b55b49c11e513`; pushed to origin/main
Date: 2026-06-06
Scope: `wave1186-cunitai-init-entry-dispatch-current-risk-review`

Wave1186 accounts for `4 CUnitAI init/indexed-entry dispatch current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator:

- `0x004239f0 CUnitAI__InitDefaults_AutoConfigTestPath`
- `0x00444f00 CUnitAI__CallIndexedEntryVFunc10`
- `0x0044cd20 CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200`
- `0x0044d1f0 CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4`

The saved Ghidra names/signatures were already bounded. The pass normalized saved comments and tags only; it made no rename, no signature change, no function-boundary change, and no executable-byte change.

Evidence:

- Ghidra dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=42 missing=0 bad=0`, then `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=42 missing=0 bad=0`, then `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Fresh exports after apply: `4` metadata rows, `4` tag rows, `8 xref rows`, `161 instruction rows`, and `4` decompile rows.
- Queue refresh after apply: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-143218_post_wave1186_cunitai_init_entry_dispatch_current_risk_review_verified`, `19` files, `176130951` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `787/1179 = 66.75%`, current focused candidates: 1176, live regenerated current focused candidates: 1176, remaining active focused work: 392, current risk candidates: 6166.

Static contract:

`CUnitAI__InitDefaults_AutoConfigTestPath` is reached from no-function caller `0x004239c5`, writes CUnitAI default fields, copies `c:\beaautoconfigtest\` into `this+0x44`, copies `DAT_00624484` into `this+0x2d4`, and gates `this+0x318` against `DAT_0066e94e`. `CUnitAI__CallIndexedEntryVFunc10` is called by `SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10` and dispatches indexed entry vfunc slot `+0x10`. `CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200` decays `this+0xe0`, compares against `DAT_005d856c`, conditionally dispatches byte offset `+0xc8`, and clamps to profile field `+0x18`. `CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4` calls `CUnitAI__SetStateTimestampCCToNow` and conditionally dispatches byte offset `+0x38`.

One Codex read-only consult was used and recommended this residual CUnitAI init/indexed-entry dispatch slice. No Cursor/Composer was used.

Mutation boundary:

- Comment/tag normalization only.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Static clean-room target: rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference.

Not proven here: concrete CUnitAI/profile/entry-table layouts, exact source-body identity, runtime AI/defaulting/dispatch behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1186; wave1186-cunitai-init-entry-dispatch-current-risk-review; 787/1179 = 66.75%; 4 CUnitAI init/indexed-entry dispatch current-risk rows; current focused candidates: 1176; live regenerated current focused candidates: 1176; remaining active focused work: 392; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=42; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CUnitAI__InitDefaults_AutoConfigTestPath; CUnitAI__CallIndexedEntryVFunc10; CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200; CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4; SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10; c:\beaautoconfigtest\; DAT_00624484; DAT_0066e94e; DAT_005d856c; CUnitAI__SetStateTimestampCCToNow; 0 / 0 / 0; 6411/6411 = 100.00%; 8 xref rows; 161 instruction rows; 4 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-143218_post_wave1186_cunitai_init_entry_dispatch_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
