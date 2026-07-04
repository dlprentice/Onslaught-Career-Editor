# Ghidra Seek / Behaviour / NavMap / State Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 344 continued the `CPhysicsScriptStatements.cpp` static re-audit after the component-value tranche. It saved names, signatures, comments, and tags for twenty-one type-11 through type-15 targets.

The pass recovered six missing function boundaries in the seek, behaviour, alligence, navmap, and state value families, hardened the five value factories, corrected stale constructor/vfunc labels to destructor evidence, and clarified the adjacent `CFlexArray__SkipBytesFromMemBuffer` serialization helper.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0043dcd0` / `0x0043ddc0` / `0x0043e310` / `0x0043e400` / `0x0043e540` | `CPhysicsScriptStatements__CreateStatementType11` through `CPhysicsScriptStatements__CreateStatementType15` | Hardened value factories for seek ids `1..3`, behaviour ids `0x1..0x19`, alligence ids `1..3`, navmap ids `1..4`, and state ids `1..3`. Exact value semantics and class layouts remain unproven. |
| `0x0043dd60` / `0x0043dd90` / `0x0043ddb0` | seek-value destructor family | Recovered the base scalar-deleting destructor boundary and corrected the shared leaf destructor/base destructor labels. |
| `0x0043e2b0` / `0x0043e2d0` / `0x0043e300` | behaviour-value destructor family | Recovered the base scalar-deleting destructor boundary and corrected stale constructor/vfunc evidence to destructor evidence. |
| `0x0043e3a0` / `0x0043e3c0` / `0x0043e3d0` | alligence-value destructor family | Recovered the base scalar-deleting destructor boundary and separated the shared leaf wrapper from the base destructor body. |
| `0x0043e4e0` / `0x0043e500` / `0x0043e530` | navmap-value destructor family | Recovered the base scalar-deleting destructor boundary and corrected stale constructor/vfunc evidence to destructor evidence. |
| `0x0043e5d0` / `0x0043e5f0` / `0x0043e620` | state-value destructor family | Recovered the base scalar-deleting destructor boundary and corrected stale constructor/vfunc evidence to destructor evidence. |
| `0x0043e630` | `CFlexArray__SkipBytesFromMemBuffer` | Hardened the adjacent shared serialization helper signature/comment as a byte-count skip loop over `CDXMemBuffer__Read`. |

## Evidence

- Initial read-only metadata, decompile, xref, instruction, tag, and vtable-slot exports selected the type-11 through type-15 targets and recovered six missing vtable-target function boundaries.
- `tools/ApplySeekBehaviourStateTranche.java` dry/apply reported `targets=21`, `failed=0`, and apply reported `changed_or_would_change=21` with `REPORT: Save succeeded`.
- Final read-back verified `21/21` metadata rows, `21/21` decompile exports, `54` xref rows, `2877` instruction rows, `21/21` tag rows, and `215` vtable-slot rows for the checked vtable targets.
- `py -3 tools\ghidra_seek_behaviour_state_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_seek_behaviour_state_tranche_probe.py tools\ghidra_seek_behaviour_state_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-seek-behaviour-state-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5972` functions and `0` weak functions. The refreshed quality queue reports `1075` commented functions, `4897` commentless functions, `1969` undefined signatures, and `2119` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_172227_post_wave344_verified` with `19` files, `152701831` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It improves the current type-11 through type-15 value-family labels, but it does not prove exact source identities for every helper, concrete value class layouts, seek/behaviour/alligence/navmap/state semantics, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/seek-behavior-state-wave344/current/`.
