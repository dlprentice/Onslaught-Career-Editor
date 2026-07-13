# Ghidra Round Wave493 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004d8410` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-17

## Scope

Wave493 saved static Ghidra name/signature/comment/tag hardening for five CRound/Round-core functions:

| Address | Saved state |
| --- | --- |
| `0x004d81e0` | `void * __thiscall CRound__ctor(void * this, void * init)` |
| `0x004d82a0` | `double __fastcall VFuncSlot_15_004d82a0(void * this)` |
| `0x004d8350` | `void * __thiscall CRound__scalar_deleting_dtor(void * this, int flags)` |
| `0x004d8370` | `void __fastcall CRound__ShutdownAndDetachReaders(void * this)` |
| `0x004d8410` | `void __thiscall CRound__Init(void * this, void * init)` |

## Evidence

- Apply script: `tools/ApplyRoundWave493.java`
- Probe: `tools/ghidra_round_wave493_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave493-round-core-004d81e0/`
- Dry/apply/verify:
  - Dry: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0`
  - Apply: `updated=5 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `9` context metadata rows, `9` tag rows, decompile/xref/instruction/vtable exports, CRound vtable `0x005de82c` slots 1, 9, and 15, and CMissile-style vtable `0x005e3ba4` slot 15.
- Focused probe: `py -3 tools\ghidra_round_wave493_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-round-wave493` PASS.
- Queue refresh: `6068` total functions, `2223` commented, `3845` commentless, `1673` undefined signatures, `1531` `param_N`; strict comment-plus-clean-signature proxy `2167/6068 = 35.71%`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-090622_post_wave493_round_verified` with `19` files, `157584263` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Public Boundary

This note is public-safe static RE accounting. It does not include private game assets, installed-game mutation, runtime launch proof, raw decompile bodies, or private media.

## Not Proven

- Exact source virtual names and full `Round.cpp` source-body identity.
- Concrete `CRound`, `CRoundInitThing`, and `CRoundData` layouts.
- Meaning of the slot-15 scalar return.
- Runtime projectile collision/effect behavior, BEA launch behavior, game patching, and rebuild parity.
