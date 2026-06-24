# Ghidra CUnit ApplyDamage Wave835 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cunit-apply-damage-wave835`

Wave835 CUnit ApplyDamage saved a bounded signature/comment/tag correction for `0x004f9a90 CUnit__ApplyDamage`. This is important shared CUnit damage/lifetime infrastructure, not throwaway tail code. The pass made no rename, no function-boundary change, and no executable-byte change.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004f9a90 CUnit__ApplyDamage` | `void __thiscall CUnit__ApplyDamage(void * this, float damage_amount, void * damage_source, int apply_shields, int mesh_part_index)` | Deep instruction export shows `RET 0x10` at `0x004fa4a7`; direct callsite windows at `0x004037be`, `0x00417a16`, `0x0048006d`, and `0x004898b0` show four pushed stack arguments before `ECX` receiver setup and call. |
| DATA slot refs | 19 slot pointers to `0x004f9a90` | DATA refs at `0x005dd828`, `0x005dfa38`, `0x005dfddc`, `0x005e002c`, `0x005e027c`, `0x005e0724`, `0x005e0980`, `0x005e0bd0`, `0x005e1080`, `0x005e1530`, `0x005e1c24`, `0x005e232c`, `0x005e257c`, `0x005e2a1c`, `0x005e3114`, `0x005e3374`, `0x005e3de0`, `0x005e403c`, and `0x005e4298` all read back as pointers to `CUnit__ApplyDamage`. |
| Damage flow anchors | Static body evidence | Observed behavior resets `CUnit__ResetDamageCooldownTimer` through `this+0x148`, scales damage by profile/state fields, repairs health-like `this+0xf8` for non-positive damage, gates nexus/weakpoint mesh-part cases using `s_nexus_00633af4` and `s_weakpoint_00633ae8`, forwards segment damage to `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` when `this+0x178` exists, otherwise applies shield-like `this+0x100` before life-like `this+0xf8`, dispatches death/cleanup vfuncs, emits a particle effect when the profile effect pointer is present, and queues profile/Tara/Billy damage text through `CMessageBox` with Unit.cpp debug allocation path `0x00633b6c`, line `0x44d`. |

Read-back evidence:

- `ApplyCUnitApplyDamageWave835.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitApplyDamageWave835.java apply`: `READBACK_OK`, `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitApplyDamageWave835.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 23 xref rows, 261 instruction-window rows, 901 deep instruction rows, 164 xref-site instruction rows, 19 DATA slot rows, and 1 decompile row.
- Queue after Wave835: 6098 total functions, 5657 commented, 441 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5657/6098 = 92.77%`, strict clean-signature proxy `5657/6098 = 92.77%`.
- Next raw commentless row: `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-003658_post_wave835_cunit_apply_damage_verified`, 19 files, 171838343 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row exists at `0x004f9a90`.
- The saved signature, function comment, and tags include `cunit-apply-damage-wave835` and `wave835-readback-verified`.
- The four explicit stack arguments are supported by `RET 0x10` and direct callsite push evidence.
- The observed damage/shield/life/segment/message behavior is static retail Ghidra evidence tied to decompile, instruction, xref, and DATA-slot exports.

What remains unproven:

- Exact Unit.cpp source body identity.
- Concrete `CUnit`, profile, damage-source, segment, message, or effect layouts beyond observed offsets.
- Exact player/god-mode, shield, death, particle, or message runtime behavior.
- BEA patching behavior.
- Rebuild parity.
