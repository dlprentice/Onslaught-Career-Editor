# Ghidra BattleEngine/JetPart Movement Review Wave925

Status: complete read-only static review
Date: 2026-05-27
Scope: `battleengine-jetpart-movement-review-wave925`

Wave925 re-reviewed the BattleEngine/JetPart input and zoom mini-cluster selected from the Wave911 focused queue. The pass was read-only: no Ghidra mutation, no rename, no saved signature/comment/tag change, no function-boundary change, and no executable-byte change.

Targets:

| Address | Saved row | Static read-back evidence |
| --- | --- | --- |
| `0x00409e80` | `CBattleEngine__AutoZoomOut` | Writes `1.0` / `0x3f800000` to BattleEngine `+0x2cc`; xrefs from `CBattleEngineJetPart__ChangeWeapon` and `CBattleEngineWalkerPart__ChangeWeapon`. |
| `0x00410310` | `CBattleEngineJetPart__Thrust` | `RET 0x4` one-float input helper; source-aligned thrust / loop-start timing body. |
| `0x00410490` | `CBattleEngineJetPart__Turn` | `RET 0x4` one-float input helper; yaw/roll velocity path remains source-aligned, with known local decompiler artifact debt. |
| `0x00410670` | `CBattleEngineJetPart__Pitch` | `RET 0x4` one-float input helper; pitch velocity path remains source-aligned, with known local decompiler artifact debt. |
| `0x00410740` | `CBattleEngineJetPart__YawLeft` | `RET 0x4` one-float input helper; left hard-turn / loop-break / roll-start path remains source-aligned. |
| `0x004109d0` | `CBattleEngineJetPart__YawRight` | `RET 0x4` one-float input helper; right hard-turn / loop-break / roll-start path remains source-aligned. |
| `0x00411b70` | `CBattleEngineJetPart__IsStateMachineActive` | Called by `CBattleEngine__Morph`; returns whether local JetPart state at `+0x2c` or `+0x48` is active. |

Read-back evidence:

- Metadata export: `7` rows, `7` OK.
- Tag export: `7` rows, `7` OK.
- Xref export: `9` rows.
- Instruction export: `697` function-body instruction rows.
- Decompile export: `7` rows, `7` OK.
- Focused Wave911 re-audit progress after Wave925: `96/1408 = 6.82%`.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260527-223000_post_wave925_battleengine_jetpart_movement_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

Consult note:

- A Codex read-only consult and Cursor Composer 2.5 ask-mode consult both recommended keeping the five JetPart input helpers plus `CBattleEngine__AutoZoomOut` context, excluding the WalkerPart-only `0x004135d0` predicate from this wave, and optionally including `0x00411b70 CBattleEngineJetPart__IsStateMachineActive`. The final Wave925 target set follows that shape.

What this proves:

- The seven saved function rows still exist in the loaded Ghidra database with the expected names and signatures.
- The fresh xrefs connect `AutoZoomOut` to JetPart/WalkerPart change-weapon callers, the five JetPart input helpers to the same input-dispatch region, and `IsStateMachineActive` to `CBattleEngine__Morph`.
- The old Wave304/Wave308 source-parity correction boundaries still hold under fresh read-back.

What remains unproven:

- Runtime jet input behavior.
- Runtime zoom behavior.
- Runtime morph/controller dispatch behavior.
- Concrete `CBattleEngine` / `CBattleEngineJetPart` / `CBattleEngineWalkerPart` layouts.
- BEA patching behavior.
- Rebuild parity.
