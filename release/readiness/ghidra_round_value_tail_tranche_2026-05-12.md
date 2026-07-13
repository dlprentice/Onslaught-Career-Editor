# Ghidra Round Value Tail Tranche - 2026-05-12

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00437fe0` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 338 continued the `CPhysicsScriptStatements.cpp` static re-audit immediately after the round/sound value tranche. It saved names, signatures, comments, and tags for eighteen adjacent round-value tail functions and recovered three previously missing vtable-target function boundaries.

The pass also corrected the newly recovered `CRoundTreeCollision__ApplyToRoundByName` comment during the same wave: fresh decompile spot-check showed the nested child value is written to round record `+0xa4`, not `+0x48`.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x00437fe0` | `void __thiscall CPhysicsRoundValue__SetOwnedAuxStringAt0C(void * this, char * sourceString)` | Owned string copy helper for round/value records; frees `this+0xc` and allocates replacement storage with the observed `0x23c` tag. |
| `0x00438050` | `void __thiscall CPhysicsRoundValue__SetOwnedValueStringAt08(void * this, char * sourceString)` | Supersedes stale `CUnitAI` ownership; frees and replaces the owned value string at `this+0x8`. |
| `0x004380c0` | `void __fastcall CPhysicsRoundValue__dtor_base(void * this)` | Base destructor body with vtable `0x005da584`; that vtable slot 0 points at the recovered scalar-deleting destructor boundary. |
| `0x004380d0` | `void * __thiscall CPhysicsRoundValue__scalar_deleting_dtor(void * this, int flags)` | Recovered function boundary from vtable `0x005da584`; optionally frees `this` when flags bit 0 is set. |
| `0x00438400` | `void * __thiscall CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)` | Shared leaf scalar-deleting destructor wrapper that calls `0x004380c0` and optionally frees `this`. |
| `0x00438b40` | `void __thiscall CRoundGridOfFear__ApplyToRoundByName(void * this, char * roundName)` | Searches `DAT_008553f0` and writes the rounded value at `this+0x8` to round record `+0x58`. |
| `0x004394e0` | `void __thiscall CRoundSeek__ApplyToRoundByName(void * this, char * roundName)` | Recovered function boundary; writes the nested child value result from `this+0x8` to round record `+0x48`. |
| `0x00439580` | `void __thiscall CRoundSeek__LoadFromMemBuffer(void * this, void * memBuffer)` | Reads a nested value type id, dispatches `CPhysicsScriptStatements__CreateStatementType11`, and stores the child at `+0x8`. |
| `0x004395b0` | `void * __thiscall CRoundSeek__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting destructor wrapper around `CRoundSeek__dtor_base`. |
| `0x004395d0` | `void __fastcall CRoundSeek__dtor_base(void * this)` | Destructor body that destroys the owned child value at `+0x8` before restoring the base round-value vtable. |
| `0x00439620` | `void __thiscall CRoundMesh__ApplyToRoundByName(void * this, char * roundName)` | Replaces the owned mesh string at round record `+0xc`. |
| `0x00439710` | `void __thiscall CRoundEffect__ApplyToRoundByName(void * this, char * roundName)` | Replaces the owned effect string at round record `+0x10`. |
| `0x00439800` | `void __thiscall CRoundWaterEffect__ApplyToRoundByName(void * this, char * roundName)` | Replaces the owned water-effect string at round record `+0x14`. |
| `0x00439910` | `void __thiscall CRoundExplosion__ApplyToRoundByName(void * this, char * roundName)` | Replaces the owned explosion string at round record `+0x8`. |
| `0x00439a00` | `void __thiscall CRoundTreeCollision__ApplyToRoundByName(void * this, char * roundName)` | Recovered function boundary; writes the nested child value result from `this+0x8` to round record `+0xa4`. |
| `0x00439aa0` | `void __thiscall CRoundTreeCollision__LoadFromMemBuffer(void * this, void * memBuffer)` | Reads a nested value type id, dispatches `CPhysicsScriptStatements__CreateStatementType15`, and stores the child at `+0x8`. |
| `0x00439ad0` | `void * __thiscall CRoundTreeCollision__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting destructor wrapper around `CRoundTreeCollision__dtor_base`. |
| `0x00439af0` | `void __fastcall CRoundTreeCollision__dtor_base(void * this)` | Destructor body that destroys the owned child value at `+0x8` before restoring the base round-value vtable. |

## Evidence

- Initial read-only exports verified `15/15` metadata rows, `15/15` decompile exports, `52` xref rows, `555` instruction rows, and `15/15` tag rows.
- Vtable-context read-back found three uncreated function boundaries: `0x004380d0`, `0x004394e0`, and `0x00439a00`.
- `tools/ApplyRoundValueTailTranche.java` dry/apply recovered the three missing boundaries and saved all eighteen targets. The final apply reported `updated=18`, `skipped=0`, `renamed=0`, `missing=0`, and `bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `18/18` metadata rows, `18/18` decompile exports, `55` xref rows, `882` instruction rows, and `18/18` tag rows.
- `py -3 tools\ghidra_round_value_tail_tranche_probe_test.py` passed `3/3`; `py -3 -m py_compile tools\ghidra_round_value_tail_tranche_probe.py tools\ghidra_round_value_tail_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-round-value-tail-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5907` functions, `961` commented functions, `4946` commentless functions, `1979` undefined signatures, and `2158` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_121126_post_wave338_verified` with `19` files, `152275847` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It does not prove exact source identities, concrete round or value class layouts, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/round-values-tail-wave338/current/`.
