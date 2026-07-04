# Ghidra Wave900+ Through Wave1041 Recheck

Status: structural static evidence recheck passed
Date: 2026-06-01
Scope: Wave900-Wave1041

This note extends the Wave900+ recheck gate after Wave1041. It is a structural evidence gate over saved readiness notes, focused probes, ignored evidence bases, backup references, apply-log coverage for mutation waves, direct focused-probe classifications for Wave982-Wave1041, and current queue closure.

Fresh validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1041-recheck
```

Expected scope:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1041 focused probes are rerun or classified by the current recheck gate.
- Wave910 and Wave911 remain queue/planning waves without per-wave Ghidra backup notes.
- Current live queue closure remains `6238/6238 = 100.00%`.

Wave1041 extension:

- Focused probe: `npm run test:ghidra-crt-fpu-runtime-tail-review-wave1041`
- Readiness note: `release/readiness/ghidra_crt_fpu_runtime_tail_review_wave1041_2026-06-01.md`
- Evidence base: `subagents/ghidra-static-reaudit/wave1041-crt-fpu-runtime-tail-review`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified`
- Mutation status: no mutation.

Boundary note: this recheck validates static evidence structure, backups, probe wiring, and current queue closure. It does not prove runtime behavior, exact source-layout identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1041; crt-fpu-runtime-tail-review-wave1041; 0x0055da76 CRT__InitRuntimeFromStoredFrameGlobals; 0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk; 0x00562a89 CRT__SetErrnoForFpSourceKind; 0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk; __cintrindisp2; __amsg_exit; DAT_009d08b8; 0x00653658; 727/1408 = 51.63%; 960/1493 = 64.30%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified; no mutation.
