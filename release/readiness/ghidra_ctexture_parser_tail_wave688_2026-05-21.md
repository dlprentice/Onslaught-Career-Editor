# Ghidra CTexture Parser Tail Wave688 Readiness Note

Date: 2026-05-21

Wave688 CTexture parser tail saved five parser-terminal, register-node parser, node/binding cleanup, compile-context cleanup, and parser-reduction rows after serialized Ghidra dry/apply/final-dry read-back.

Tag anchors:

- `ctexture-parser-tail-wave688`
- `wave688-readback-verified`

Function anchors:

- `0x0058f593 CTexture__ReadParserTerminalToken`
- `0x0058fbc5 CTexture__ApplyParserReductionAction`
- Next queue head: `0x005907d9 CTexture__LoadScriptAndDispatchByVersion`

## Saved Scope

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0058f593` | `uint __fastcall CTexture__ReadParserTerminalToken(void * parser_compile_context)` | Reads preprocessed tokens through `CTexture__GetNextTokenWithPreprocessor`, maps token classes to observed parser terminal ids, recognizes `entrypoint`, `true`, and `false`, calls `CTexture__ParseShaderSemanticToken` when semantic parsing is enabled, and sets parser error flags on lexer failure. |
| `0x0058f66f` | `int __thiscall CTexture__ParseScriptTokensAndBuildNodes(void * this, void * token_descriptor, int relative_register_node, int unused_context)` | Parses underscore-delimited register/expression token text, consults the observed 0x48-byte descriptor table, derives register classes/modifiers, handles relative register offsets, allocates 0x2c-byte node payloads, and emits diagnostic `0x7d5` for invalid register forms. |
| `0x0058fb70` | `void __fastcall CTexture__DestroyNodeAndBindingsRecord(void * node_payload_record)` | Frees the object/callback slot at `+0x00` and releases a linked binding record at `+0x20` through the Wave687 binding-record destructor wrapper. |
| `0x0058fb8b` | `void __fastcall CTexture__DestroyParserCompileContext(void * parser_compile_context)` | Releases the object at `+0x08`, the owner/list at `+0x34`, callback storage at `+0x58`, and parser state at `+0x78` through the Wave687 parser-state destructor wrapper. |
| `0x0058fbc5` | `void __thiscall CTexture__ApplyParserReductionAction(void * this, uint reduction_rule_id, uint rhs_count, uint unused_context)` | Pops right-hand-side nodes from the parser stack, switches on reduction ids, links node lists, validates instruction nodes, applies masks/swizzles, builds relative-address and literal nodes, emits observed diagnostics, cleans unused stack entries, and pushes the reduction result through a 0x14-byte parser-stack record. |

## Evidence

`ApplyCTextureParserTailWave688.java` dry/apply/final dry reported:

- Dry: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 varargs=0 missing=0 bad=0`
- Apply: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 varargs=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`

All three passes reported `REPORT: Save succeeded`. Post exports verified `5` metadata rows, `5` tag rows, `7` xref rows, `185` instruction rows, and `5` clean decompile rows. Pre-state exports covered the same five rows, and candidate exports covered `8` adjacent parser-tail/script-loader/query-stub rows with `10` xref rows, `296` instruction rows, and `8` clean decompile rows before tranche selection.

Post-Wave688 queue telemetry is `6098` total functions, `3939` commented, `2159` commentless, `1216` exact-undefined signatures, and `382` `param_N` signatures. Comment-backed proxy is `3939/6098 = 64.60%`; strict clean-signature proxy is `3889/6098 = 63.78%`.

Verified backup: `G:\GhidraBackups\BEA_20260521-114344_post_wave688_ctexture_parser_tail_verified`, `19` files, `164760455` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static Ghidra name/signature/comment/tag evidence only. Exact token enum, yacc grammar/rule mapping, descriptor-table schema, register enum, node layout, parser stack/compile-context layouts, instruction ABI, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe: `cmd.exe /c npm run test:ghidra-ctexture-parser-tail-wave688`
