# Goodies Scalar Candidate Classification - 2026-05-08

Status: GREEN read-only focused-candidate classification

## Objective

Classify the `41` focused literal-immediate candidates from `release/readiness/goodies_scalar_reference_scan_2026-05-08.md` before treating any small scalar value as a possible Goodies 71-73 selector.

## Public-Safe Result

The focused candidates do not currently provide evidence for a hidden Goodies 71-73 selector.

| Candidate family | Rows | Classification |
| --- | ---: | --- |
| `CPhysicsScriptStatements__CreateStatementType2` | 3 | Object-allocation metadata/source-line constants in physics-script statement construction, not Goodies ids. |
| `CFEPMain__Render` | 2 | Frontend page/icon render state constants used as indices, not Goodies ids. |
| `CFrontEnd__LoadSharedResources` | 27 | Repeated `ADD ESP, 0x48` stack cleanup around resource loads, not Goodies ids. |
| `CFEPMultiplayerStart__Init` | 1 | Object-allocation metadata/source-line constant in multiplayer frontend setup, not a Goodies selector. |
| `CFEPVirtualKeyboard__InitKeyboardLayout` | 3 | Virtual keyboard character/layout constants (`G`, `H`, `I` range), not Goodies ids. |
| `CFEPVirtualKeyboard__HandleKeyToken` | 1 | Virtual keyboard key-token handling constant, not a Goodies selector. |
| `CFEPVirtualKeyboard__DrawPanel` | 1 | Virtual keyboard panel rendering constant, not a Goodies selector. |
| `IScript__CallEvent0AndRegisterNestedListeners` | 1 | Script runtime structure offset/stride, not a Goodies state index. |
| `CRT__InitializeFileDescriptorTable` | 1 | CRT allocation/stack-size noise, not game logic. |
| `CTexture__ParseScriptTokensAndBuildNodes` | 1 | Texture parser stride/offset noise, not Goodies state logic. |

## Commands Run

| Command | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `node -e "<build focused candidate address lists from ignored scalar JSON>"` | PASS | `instructionAddrs=41 functionAddrs=10` | Produces private input lists for candidate context export. |
| `analyzeHeadless ... -postScript ExportInstructionsAroundAddresses.java <focused-addresses> <ignored-output> 6 10 -noanalysis` | PASS | `targets=41 missing=0`; `697` instruction-context rows. | Exports bounded instruction context for every focused scalar candidate. |
| `analyzeHeadless ... -postScript ExportFunctionsByAddressDecompile.java <focused-functions> <ignored-output> 60 -noanalysis` | PASS | `targets=10 dumped=10 missing=0 failed=0`. | Exports private decompile context for every focused candidate function. |
| Private output inspection | PASS | The categories above were classified from instruction mnemonics/operands and decompile context. | Narrows the scalar path without publishing raw decompile or private Ghidra artifacts. |
| `cmd.exe /c npm run test:goodies-scalar-reference` | PASS | Parser tests `2/2`. | Confirms the scalar-reference summarizer remains covered. |
| `py -3 tools\goodies_scalar_reference_probe.py --tsv <ignored-output> --check` | PASS | `rows=1698`, `knownSupport=11`, `literalImmediateCandidates=169`, `focusedCandidates=41`. | Confirms the focused candidate input set still matches the public classification. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new note and updated links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1031`. | Confirms documented command references remain synchronized. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Hygiene unit tests `29/29`; live repo hygiene PASS. | Confirms the public-safe wording avoids stale/private term violations. |
| `py -3 tools\release_curated_manifest.py` and `--check` | PASS | Selected files `1394`. | Regenerates and verifies public release allowlist accounting for the new note. |
| `py -3 tools\release_profile_snapshot.py` and `--check` | PASS | Counts `R0=1451 R2=0 R3=2 R4=18187`. | Regenerates and verifies release profile outputs after manifest changes. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1394`. | Confirms public allowlist safety still excludes private runtime and asset families. |
| `node -e "<parse state and manifest JSON>"` | PASS | `json ok`. | Confirms state and manifest JSON are valid. |
| `git diff --check` | PASS | No whitespace errors. | Confirms the tracked diff is whitespace-clean. |
| Process check for `BEA`, `cdb`, `ghidra`, and `analyzeHeadless` | PASS | No matching processes. | Confirms the read-only wave did not leave game, debugger, or Ghidra processes running. |

Ghidra headless printed the known local GhydraMCP extension manifest warnings before processing. Both scripts are read-only, but headless reported normal project save after processing.

## Updated Classification

The scalar-reference path now rules out the current focused candidate set as direct Goodies 71-73 selector evidence. This strengthens the current model:

- normal wall navigation skips 71-73;
- shipped/source/catalog support for 71-73 exists;
- direct source/script/xref selectors are not currently proven;
- broad scalar search did not reveal a hidden selector after focused candidate classification.

## Not Claimed

- This does not prove there is no indirect runtime-only path.
- This does not prove cheat/developer/direct-selection behavior impossible.
- This does not replace copied-profile runtime proof if a later hypothesis identifies an actual selector.
- This does not launch BEA, attach CDB, mutate Ghidra intentionally, patch saves, or patch executables.
