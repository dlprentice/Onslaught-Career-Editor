# Goodies Scalar Reference Scan - 2026-05-08

Status: GREEN read-only Ghidra scalar scan; focused candidates require review

## Objective

Search the current Ghidra project for instruction scalar values `0x47`, `0x48`, and `0x49` after the focused Goodies wall observer and hidden-path static refresh. These are the decimal Goodie ids 71, 72, and 73, but they are also common small constants, stack/member offsets, UI dimensions, and parser values.

This pass adds a reusable read-only exporter plus a public-safe summarizer so future RE work can distinguish expected Goodies support from noisy scalar hits.

## Public-Safe Result

The full scalar search is intentionally broad and noisy:

```text
ExportScalarReferences.java rows: 1698
goodies_scalar_reference_probe.py rows: 1698
known support rows: 11
all candidate rows: 1687
literal-immediate candidate rows: 169
focused Goodies/frontend/script/career-adjacent literal candidates: 41
```

Focused candidate functions currently reported by the summarizer:

| Function | Count | Review note |
| --- | ---: | --- |
| `CFEPMain__Render` | 2 | Frontend render literal candidates; not Goodies proof by itself. |
| `CFEPMultiplayerStart__Init` | 1 | Frontend initialization literal candidate. |
| `CFEPVirtualKeyboard__DrawPanel` | 1 | Virtual-keyboard UI candidate. |
| `CFEPVirtualKeyboard__HandleKeyToken` | 1 | Virtual-keyboard token candidate. |
| `CFEPVirtualKeyboard__InitKeyboardLayout` | 3 | Virtual-keyboard layout candidates. |
| `CFrontEnd__LoadSharedResources` | 27 | Repeated `0x48` stride/resource-load candidates. |
| `CPhysicsScriptStatements__CreateStatementType2` | 3 | Script-statement construction candidates worth classifying before any reachability claim. |
| `CRT__InitializeFileDescriptorTable` | 1 | Runtime-library noise candidate. |
| `CTexture__ParseScriptTokensAndBuildNodes` | 1 | Texture/parser candidate; not Goodies proof by itself. |
| `IScript__CallEvent0AndRegisterNestedListeners` | 1 | Script runtime candidate worth classifying with surrounding instructions/decompile if Goodies script work continues. |

The scan did not produce an immediate, self-evident Goodies 71-73 selector. It produced a bounded review list for the next static step.

Follow-up classification: `release/readiness/goodies_scalar_candidate_classification_2026-05-08.md` exports instruction/decompile context for the `41` focused candidates and classifies them as source-line/object-allocation metadata, stack cleanup/stride offsets, frontend page/icon state constants, virtual-keyboard layout/token constants, script runtime offsets, CRT noise, or texture parser offsets rather than Goodies selectors.

## Commands Run

| Command | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `npm run test:goodies-scalar-reference` | PASS | Parser tests `2/2` pass. | Proves the public-safe TSV summarizer handles known support rows, focused candidate rows, and missing input. |
| `analyzeHeadless ... -postScript ExportScalarReferences.java <ignored-output> 0x47 0x48 0x49 -noanalysis` | PASS | Wrote `1698` scalar rows under ignored `subagents/`. | Exports instruction scalar references from the existing Ghidra project without launching BEA or patching the executable. |
| `py -3 tools\goodies_scalar_reference_probe.py --tsv <ignored-output> --check` | PASS | `knownSupport=11`, `literalImmediateCandidates=169`, `focusedCandidates=41`. | Summarizes broad scalar noise into a smaller focused review queue. |

Ghidra headless printed the known local GhydraMCP extension manifest warnings before processing. The script itself is read-only, but headless still reported `Save succeeded` for the processed project file as part of normal headless processing.

## Not Claimed

- This does not prove focused candidate functions are hidden Goodies selectors.
- This does not prove Goodies 71-73 are reachable or unreachable in every runtime state.
- This does not launch BEA, attach CDB, patch saves, patch executables, or commit raw Ghidra output.
- This does not replace decompile/instruction-context review of the focused candidates.

## Next Step

Classify the focused scalar candidates before another runtime run. The highest-value candidates are script/front-end-adjacent entries: `CPhysicsScriptStatements__CreateStatementType2`, `IScript__CallEvent0AndRegisterNestedListeners`, `CFEPMain__Render`, and the `CFEPVirtualKeyboard__*` rows.
