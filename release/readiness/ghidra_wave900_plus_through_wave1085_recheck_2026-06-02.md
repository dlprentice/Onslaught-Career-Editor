# Ghidra Wave900+ Through Wave1085 Recheck Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00401910` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1085-recheck`

This note extends the post-Wave900 recheck chain through Wave1085 and records the Wave1085 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1085-recheck
```

Wave1085 (`shared-unit-residual-vtable-boundary-review-wave1085`) recovered twenty-four residual shared unit-family vtable-boundary function starts that were previously `INSTRUCTION_NO_FUNCTION` code pointers. Representative rows are `0x00401550 SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550`, `0x004fd440 SharedUnitVFunc__TestField17c19cReadiness_004fd440`, `0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0`, `0x004f9220 SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220`, `0x004fe4a0 SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0`, `0x00401900 SharedUnitVFunc__ForwardArgToThingBridge_00401900`, `0x00401910 SharedUnitVFunc__CopyTransformAndNotify_00401910`, and `0x004fce00 SharedUnitVFunc__ForwardField208Slot10_004fce00`. The focused readiness note is [`ghidra_shared_unit_residual_vtable_boundary_wave1085_2026-06-02.md`](ghidra_shared_unit_residual_vtable_boundary_wave1085_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `188`
- Covered waves: `186`
- Package probe scripts: `184`
- Evidence bases: `184`
- Backup references: `186`
- Apply scripts: `64`
- Wave982-Wave1085 direct probes: `resultCount=104`, `passCount=1`, `failCount=103`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6331`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`
- Wave1085 evidence: `24` metadata rows, `24` tag rows, `790` xref rows, `431` function-body instruction rows, `24` decompile rows, and `1600` post vtable-slot rows.
- Sampled vtable-slot improvement: pre `1244` OK / `356` `NO_FUNCTION_AT_POINTER`; post `1480` OK / `120` `NO_FUNCTION_AT_POINTER`; selected Wave1085 targets account for `236` slot occurrences changing from no-function to OK.

Coverage anchors:

- Static function-quality closure is `6331/6331 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1448/1560 = 92.82%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-125900_post_wave1085_shared_unit_residual_vtable_boundary_verified`, `19` files, `174918535` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual names, concrete unit-family layout semantics, runtime targeting, movement, render, event, name-propagation, transform, and field-forwarding behavior, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1085; shared-unit-residual-vtable-boundary-review-wave1085; 0x00401550 SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550; 0x004fd440 SharedUnitVFunc__TestField17c19cReadiness_004fd440; 0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0; 0x004f9220 SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220; 0x004fe4a0 SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0; 0x00401900 SharedUnitVFunc__ForwardArgToThingBridge_00401900; 0x00401910 SharedUnitVFunc__CopyTransformAndNotify_00401910; 0x004fce00 SharedUnitVFunc__ForwardField208Slot10_004fce00; 1448/1560 = 92.82%; 812/1408 = 57.67%; 500/500 = 100.00%; 6331/6331 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-125900_post_wave1085_shared_unit_residual_vtable_boundary_verified; boundary recovery.
