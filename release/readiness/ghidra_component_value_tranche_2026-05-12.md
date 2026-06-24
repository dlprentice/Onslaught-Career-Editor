# Ghidra Component Value Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 343 continued the `CPhysicsScriptStatements.cpp` static re-audit after the hazard-value tranche. It saved names, signatures, comments, and tags for thirty-two component-value targets.

The pass recovered twenty-five missing function boundaries in the type-10/component-value family, hardened the type-10 component-value factory, and corrected stale component constructor/vfunc labels to destructor, scalar/flag apply, owned-string apply, indexed-scalar, based-on, and compound value evidence.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0043c500` | `CPhysicsScriptStatements__CreateStatementType10` | Hardened the type-10/component-value factory over value ids `0x1..0x19` except `0x5`; vtable evidence spans `0x005da908` through `0x005daad4`. |
| `0x0043ca70..0x0043d460` / `0x0043ce60..0x0043d3a0` | component scalar and flag apply helpers | Recovered offset-backed scalar helpers for component record fields `+0xd8`, `+0xdc`, `+0xc0`, `+0x158`, `+0xb8`, `+0xbc`, and `+0x160`, plus flag helpers for `+0x124`, `+0x128`, `+0x12c`, `+0x198`, `+0x114`, `+0x19c`, `+0x134`, and `+0x108`; field semantics remain unproven. |
| `0x0043d760` / `0x0043d8f0` / `0x0043da90` / `0x0043db90` | owned-string and based-on apply helpers | Hardened mesh, vent, noise, and based-on component apply helpers. The based-on helper resolves the source name at `this+0x8` and calls `CComponentBasedOn__CopyFrom(destination, source/null)`. |
| `0x004175b0` / `0x00433170` / `0x004331e0` / `0x00433220` / `0x0043d500` / `0x0043d5c0` / `0x0043d670` / `0x0043d6b0` / `0x0043d850` / `0x0043d9f0` | compound, indexed, and two-scalar helpers | Hardened two-scalar size/load, value-id `02` and `13` load/size/apply helpers, indexed scalar `+0x164`, and conservative `CComponentValue04` / `CComponentValue0E` apply labels. |
| `0x0043d5a0` / `0x0043dcc0` | component-value destructor family | Recovered the shared leaf scalar-deleting destructor wrapper and base destructor body, correcting stale constructor/vfunc evidence. |

## Evidence

- Initial read-only metadata, decompile, xref, instruction, tag, and vtable-slot exports selected the type-10/component-value targets and recovered twenty-five missing vtable-target function boundaries.
- `tools/ApplyComponentValueTranche.java` dry/apply reported `targets=32`, `failed=0`, and apply reported `changed_or_would_change=32` with `REPORT: Save succeeded`.
- Final read-back verified `32/32` metadata rows, `32/32` decompile exports, `95` xref rows, `2976` instruction rows, `32/32` tag rows, and `120` vtable-slot rows for the checked vtable targets.
- `py -3 tools\ghidra_component_value_tranche_probe_test.py` passed `3/3`; `py -3 -m py_compile tools\ghidra_component_value_tranche_probe.py tools\ghidra_component_value_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-component-value-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5966` functions and `0` weak functions. The refreshed quality queue reports `1054` commented functions, `4912` commentless functions, `1974` undefined signatures, and `2129` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `G:\GhidraBackups\BEA_20260512_164714_post_wave343_verified` with `19` files, `152636295` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It improves the current type-10/component-value family labels, but it does not prove exact source identities for every helper, concrete component or value class layouts, scalar/flag/string field semantics, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/component-values-wave343/current/`.
