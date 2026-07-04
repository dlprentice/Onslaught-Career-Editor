# Ghidra Wave900+ Through Wave1006 Recheck

Status: PASS
Date: 2026-05-31

This note extends the current Wave900+ recheck scope through Wave1006 after `air-unit-crash-support-vfunc-review-wave1006`.

Anchor tokens: Wave1006; `air-unit-crash-support-vfunc-review-wave1006`; `0x00402fa0 CUnit__UpdateMotionAndTrailEffects`; `0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport`; `0x00403760 CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes`; `0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear`; `0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes`; `0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport`; progress `485/1408 = 34.45%`, `662/1478 = 44.79%`, `384/500 = 76.80%`; queue closure `6223/6223 = 100.00%`; backup `[maintainer-local-ghidra-backup-root]\BEA_20260531-135619_post_wave1006_airunit_crash_support_vfunc_review_verified`.

Validation command:

```powershell
cmd.exe /c npm run test:ghidra-wave900-plus-through-wave1006-recheck
```

Result: PASS with 109 readiness notes, 107 covered waves, 105 package probe scripts, 105 evidence bases, 107 backup references, 33 apply scripts, and Wave982-Wave1006 direct probes 25 total / 1 pass / 24 classified stale-current failures / 0 disallowed evidence or unclassified failures. Current queue remains 6223 total, 0 commentless, 0 exact-undefined signatures, and 0 `param_N` signatures.

This recheck is static evidence structure only. It does not prove runtime air-unit crash/support behavior, exact source virtual names, concrete `CUnit`/`CAirUnit`/`CPlane` layout identity, BEA patching, or rebuild parity.
