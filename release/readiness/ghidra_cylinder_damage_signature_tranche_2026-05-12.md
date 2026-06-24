# Ghidra Cylinder / Damage Signature Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 346 continued the saved-Ghidra static re-audit at the adjacent `CCylinder` and `CDamage` cluster around `0x0043fde0..0x00441000`. It saved signatures, comments, and tags for nine already named targets after fresh metadata, decompile, xref, instruction, tag, vtable, and caller review.

The pass corrected one important calling-convention nuance: for Ghidra `__thiscall` signatures, the ECX parameter must be named `this` or Ghidra inserts an extra hidden `this` and shifts the intended first semantic parameter onto the stack. The final saved signatures use `this` for the ECX receiver and put the semantic object/record details in function comments.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0043fde0` | `CCylinder__ctor` | Copy/constructor helper for cylinder radius/basis context. |
| `0x0043fe20` | `CCylinder__ResolveCollisionVFunc02` | Vtable slot `2` target; caller `CSphere__VFunc_02_004e4d70` pushes four stack arguments and passes ECX as the cylinder context. |
| `0x00440b90` | `CDamage__Init` | Initializes the damage-system table/texture context. |
| `0x00440c00` | `CDamage__FreeOwnedDamageObjects` | Releases nested owned damage-object pointers and nulls them. |
| `0x00440c40` | `CDamage__ResetDamageTables` | Clears damage lookup/work tables and restores default runtime flags. |
| `0x00440c70` | `CDamage__LoadDamageTexture` | Loads/processes the damage texture through a 12-byte texture-info record; ECX/`this` is that texture-info record, not the full `CDamage` object. |
| `0x00440eb0` | `CDamage__InsertCellEntry` | Saved as four stack arguments plus ECX receiver, backed by `ret 0x10` evidence. |
| `0x00440f80` | `CDamage__RemoveCellEntryByCoords` | Saved as three stack arguments plus ECX receiver, backed by `ret 0x0c` evidence; the older fourth stack argument was stale. |
| `0x00441000` | `CDamage__CreateTextureBuffer` | Creates/allows the texture-buffer context from chunk-reader input. |

## Evidence

- Initial read-only exports covered `9` targets with metadata, decompile, xrefs, instructions, and tag state.
- Extra caller and vtable review covered `CSphere__VFunc_02_004e4d70` and `0x005d88cc` slot `2`, which points to `CCylinder__ResolveCollisionVFunc02`.
- `tools/ApplyCylinderDamageSignatureTranche.java` dry/apply was rerun after correcting the Ghidra hidden-`this` nuance; final apply printed `REPORT: Save succeeded`.
- Final read-back verified `9/9` metadata rows, `9/9` decompile exports, `10` xref rows, `1665` instruction rows, `9/9` tag rows, and `8` checked `CCylinder` vtable-slot rows.
- `py -3 tools\ghidra_cylinder_damage_signature_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_cylinder_damage_signature_tranche_probe.py tools\ghidra_cylinder_damage_signature_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-cylinder-damage-signature-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5974` functions and `0` weak functions. The refreshed quality queue reports `1098` commented functions, `4876` commentless functions, `1958` undefined signatures, and `2110` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `G:\GhidraBackups\BEA_20260512_183034_post_wave346_cylinder_damage_verified` with `19` files, `152734599` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra signature/comment/tag evidence only. It improves the current `CCylinder` and `CDamage` labels and signatures, but it does not prove runtime collision behavior, damage texture/decal rendering parity, exact source identities beyond the recorded static evidence, concrete `CCylinder` or `CDamage` layouts, local variable recovery, structure typing, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/cylinder-damage-wave346/current/`.
