# Ghidra Wave900+ Through Wave1065 Recheck

Status: current structural static evidence gate
Date: 2026-06-01
Scope: Wave900-Wave1065

This note extends the Wave900+ recheck gate through Wave1065 after the destroyable-segment vfunc review. It is a structural validation gate over readiness notes, focused probes, ignored evidence bases, backup references, apply-script logs, and the current zero-debt queue. It is not runtime proof, exact source-layout proof, or rebuild parity.

Current extension:

- Wave1065 (`destroyable-segment-vfunc-review-wave1065`) re-read twenty existing destructable-segment vtable/vfunc rows plus thirty-eight context rows with no mutation.
- Representative anchors: `0x00442870 CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields`, `0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage`, `0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak`, `0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects`, `0x00443460 CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch`, `0x004436d0 CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch`, `0x00443890 CDestroyableSegmentVariant__VFunc_03_ApplyDamage`, and `0x00443ea0 CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak`.
- Fresh primary exports verified `20` metadata rows, `20` tag rows, `41` xref rows, `1253` function-body instruction rows, and `20` decompile rows.
- Fresh context exports verified `38` metadata rows, `38` tag rows, `73` xref rows, `1948` function-body instruction rows, and `38` decompile rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1219/1560 = 78.14%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Mutation status: no mutation.

Expected command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1065-recheck
```

Expected validation output should report:

- PASS status.
- Covered waves through Wave1065.
- Current live queue closure at `6246/6246 = 100.00%` with `0` commentless, `0` undefined signatures, and `0` `param_N`.
- Prior Wave900-Wave981 audit coverage preserved.
- Wave982-Wave1065 direct probe classifications with `0` disallowed evidence/unclassified failures.
- Backup references present, including `[maintainer-local-ghidra-backup-root]\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified`.

Boundary:

This recheck validates static evidence structure and current zero-debt queue state. It does not prove runtime destructable-segment behavior, runtime gameplay behavior, exact source-layout identity, BEA patching behavior, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1065; destroyable-segment-vfunc-review-wave1065; 0x00442870 CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields; 0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage; 0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak; 0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects; 0x00443460 CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch; 0x004436d0 CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch; 0x00443890 CDestroyableSegmentVariant__VFunc_03_ApplyDamage; 0x00443ea0 CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak; 812/1408 = 57.67%; 1219/1560 = 78.14%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified; no mutation.
