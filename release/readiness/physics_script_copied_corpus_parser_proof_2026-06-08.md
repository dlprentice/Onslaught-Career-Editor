# PhysicsScript Copied-Corpus Parser Proof Readiness Note

Status: copied-corpus parser/census proof complete, not runtime proof
Date: 2026-06-08
Scope: Public-safe PhysicsScript corpus parser/census proof

This readiness note records the first copied-corpus parser/census result for PhysicsScript. It is not a new static re-audit wave, not a Ghidra mutation, not a runtime launch, not mission outcome proof, not serialized completeness proof, and not rebuild parity.

Static closeout remains unchanged:

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |

Remaining active focused work remains `0`.

Generated ignored evidence:

- `subagents/physics_script_schema_parser_proof_2026-06-08/physics-script-copied-corpus-summary.json`
- Parser schema: `physics-script-copied-corpus-parser.v1`

Public-safe aggregate result:

| Metric | Result |
| --- | --- |
| Copied input | `data/default physics.dat` |
| Parsed files / bytes | `1` / `175603` |
| Header | `0x12` |
| Top-level statements | `777` |
| Type counts `1..9` | `160 / 139 / 145 / 91 / 38 / 118 / 39 / 43 / 4` |
| Unknown top-level ids | `0` |
| Value-list nodes | `6803` |
| Unique statement/value id pairs | `185` |
| Raw value payload bytes preserved | `73796` |
| Continuation markers | `6026` zero/continue markers and `777` terminating `-1` markers |
| Stop reason | terminating `-1` marker at EOF |

The parser consumes copied/app-owned input only, excludes `MissionScripts/*.msl`, keeps raw bytes and private hashes in ignored evidence, and publishes only aggregate counts.

The aggregate includes `0` unknown top-level ids.

What this proves:

- The copied `data/default physics.dat` corpus candidate matches the saved `CPhysicsScript__Load` shallow framing.
- The copied corpus uses top-level statement ids within the saved `1..9` factory range.
- The parser/census reaches a clean top-level terminator at EOF.
- Value-list records are counted and raw-preserved without semantic field decoding.

What remains separate proof:

- Runtime PhysicsScript behavior.
- Mission outcomes.
- Resource-script outcomes.
- Serialized physics-script file-format completeness.
- Exact statement/value-list/concrete record layouts.
- Complete nested enum semantics.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

This is a shallow framed parser/census proof only.
