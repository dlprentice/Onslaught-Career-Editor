# MissionScript Vector/Range Command-Effect Static Proof

Status: static vector/range command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-vector-range-command-effect-static`
Artifact: `missionscript-vector-range-command-effect-static-proof.md`; schema: `missionscript-vector-range-command-effect.v1.json`

This proof converts saved retail Ghidra evidence from Wave581, the completed MissionScript descriptor schema, and a copied loose-MSL token scan into a machine-checkable vector/range helper map. It is the next narrow MissionScript command-effect child lane after the completed slot, objective/outcome, message/audio, Goodie-state, selected `SpawnThing`, selected `GetThingRef`, and cutscene pan-camera/position static proofs.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Vector length handler | Wave581 saved `0x005345d0 IScript__GetVectorLength` as `void __stdcall IScript__GetVectorLength(void * script_args, void * unused_state, void * out_result)`. The body reads a vector through datatype getter slot `+0x44`, computes `sqrt(x*x+y*y+z*z)`, and returns a float object through vtable `0x005e4ea4`. |
| Range handler | Wave581 saved `0x005347b0 IScript__CheckValueInRange` with the same three-stack-argument command ABI. The body reads value/min/max through float getter slot `+0x34`, accepts ascending and descending bounds as in-range, and returns a boolean-byte result with bool vtable context `0x005e4d50`. |
| Component handlers | Wave581 saved `0x00534b80 IScript__GetVectorX`, `0x00534c10 IScript__GetVectorY`, and `0x00534ca0 IScript__GetVectorZ`. Each reads a vector through datatype getter slot `+0x44`, copies component offset `+0`, `+4`, or `+8`, and returns a float object via `0x005e4ea4`. |
| Descriptor context | The descriptor schema preserves raw rows `0x0064dc50`, `0x0064dc90`, `0x0064dcd0`, `0x0064dd10`, `0x0064dd50`, `0x0064dd90`, `0x0064e850`, `0x0064e890`, and `0x0064e950`. The proof records these as raw static descriptor context only, because the observed name/handler fields do not justify an exact descriptor-layout or exact command-arity claim. |
| Loose corpus scan | A copied loose-MSL non-comment token scan found no direct non-comment loose-MSL rows for `GetVectorLength`, `CheckValueInRange`, `GetVectorX`, `GetVectorY`, `GetVectorZ`, or `Magnitude`. This means the slice is a static VM/helper proof, not a script-corpus usage proof. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave581 metadata/tag/xref/decompile rows | `5` / `5` / `5` / `5` |
| Wave581 instruction rows and vtable rows | `3545` / `24` |

Backups already verified by their original waves:

- Wave581: `[maintainer-local-ghidra-backup-root]\BEA_20260519-075959_post_wave581_iscript_vector_range_verified`
- Latest static closeout backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`

## Why This Matters

This gives clean-room MissionScript planning a bounded value-helper bridge: vector getter slot `+0x44`, float getter slot `+0x34`, float result vtable `0x005e4ea4`, bool result vtable context `0x005e4d50`, component offsets `+0`, `+4`, and `+8`, and a range comparison helper that tolerates reversed bounds.

The proof intentionally treats descriptor rows around `Magnitude`, `LevelLostString`, and `SetSegmentVulnerable` as raw static table evidence only. It does not turn those rows into exact descriptor-field semantics or live command names. The loose corpus scan absence is also evidence: this family is useful for clean-room VM/value behavior planning, but not yet tied to a selected mission script usage path.

## Claim Boundary

This proves static vector/range command-effect accounting from saved retail Ghidra evidence, raw descriptor context, datatype-vtable context, and a copied loose-MSL absence scan. It does not prove runtime MissionScript execution, runtime command effects, runtime vector behavior, runtime range behavior, live loose-MSL loading, packed-vs-loose script selection, exact command descriptor layout, exact arity, exact datatype layout, exact vector layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
