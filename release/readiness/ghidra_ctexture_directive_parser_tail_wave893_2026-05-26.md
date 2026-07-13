# Ghidra CTexture Directive Parser Tail Wave893 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x0058c396` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `ctexture-directive-parser-tail-wave893`

Wave893 CTexture directive parser tail saved comments/tags for eight raw commentless CTexture preprocessor, directive parser, shader parser, diagnostic, register-reference, and parser work-queue rows after serialized headless dry/apply/read-back/final dry with the `ctexture-directive-parser-tail-wave893` and `wave893-readback-verified` tags. Existing names and signature displays were preserved. The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0058aacf CTexture__HandleDirective_If` | Called by `CTexture__GetNextTokenWithPreprocessor` at `0x0058bf56`; expands queued/lexed token descriptors, handles macro actual parameters, stringize/charize-like markers `#` / `#@`, token paste marker `##`, and re-lexes synthesized token text through `CTexture__InitBufferCursorRange` plus `CTexture__ReadNextLexToken`. |
| `0x0058b812 CTexture__RunDirectiveParser` | YACC-style directive parser driver using globals `DAT_009d1430` / `DAT_009d0c60`, parser tables around `DAT_00657b48` / `DAT_00658050`, `CTexture__MapLexTokenToPreprocessorToken`, and `CTexture__ExecuteDirectiveParserAction`. |
| `0x0058bd25 CTexture__InitializePreprocessorStateFromMemorySpan` | Called by `CVertexShader__CompileScriptWithDirectiveParser`; allocates a `0x70`-byte preprocessor context, runs `CTexture__PreprocessorContextCtor`, initializes the source span, and seeds default defines. |
| `0x0058c396 CTexture__InitBufferCursorRange` | Shared source-buffer cursor initializer called by `CTexture__InitBufferFromMemorySpan`, `CTexture__InitPreprocessorDefaultDefines`, `CTexture__HandleDirective_If`, and `CTexture__OpenIncludeSourceAndInitBuffer`; returns `-0x7fffbffb` on invalid input. |
| `0x0058d821 CTexture__EmitParserMessageBySeverity` | DATA callback from `CTexture__LoadScriptAndDispatchByVersion`; severity values `1/5` use `CTexture__AppendDiagnosticMessageDedup`, `2/6` use `CTexture__AppendDiagnosticMessage`, and message ids are offset by `5000`. |
| `0x0058f34c CTexture__ResolveOrCreateRegisterReference` | Called by `CTexture__ParseScriptTokensAndBuildNodes`; resolves input/temp/constant register references through hash tables, prefix globals, vertex semantic parsing, symbol insertion, and `0x7d5` diagnostics. |
| `0x0059020b CTexture__ParseScriptWithYaccTables` | YACC-style shader/script parser called by `CTexture__LoadScriptAndDispatchByVersion`; uses globals `DAT_009d2010` / `DAT_009d1840`, parser table `DAT_00658438`, terminal reader `CTexture__ReadParserTerminalToken`, and `CTexture__ApplyParserReductionAction`. |
| `0x00590da0 CTexture__DrainParserWorkQueue` | Called twice by `CDXTexture__ProcessInputControllerState`; uses hidden ESI state, state marker `0xcc`, callback slot `0x6a`, queue count at `*(state[0x6a]+8)`, node mark `0x30`, and final state markers `0xcd/0xce`. |

Read-back evidence:

- `ApplyCTextureDirectiveParserTailWave893.java dry`: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCTextureDirectiveParserTailWave893.java apply`: `updated=8 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCTextureDirectiveParserTailWave893.java final dry`: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 8 metadata rows, 8 tag rows, 13 xref rows, 1696 instruction rows, and 8 decompile rows.
- Queue after Wave893: 6113 total, 6073 commented, 40 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `6073/6113 = 99.35%`.
- Next raw commentless row: `0x005913b0 CFastVB__JpegParser_ResetFrameState`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-055039_post_wave893_ctexture_directive_parser_tail_verified`, 19 files, 173149063 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project.
- The saved comments and tags include `ctexture-directive-parser-tail-wave893` and `wave893-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to metadata, tags, xrefs, instruction exports, decompile exports, and the refreshed queue.

What remains unproven:

- Exact preprocessor/parser/register/work-queue layouts.
- Exact token/action/diagnostic enum meanings.
- Exact grammar/source identity.
- Runtime macro expansion, shader parsing, or decode scheduling behavior.
- BEA patching behavior.
- Rebuild parity.
