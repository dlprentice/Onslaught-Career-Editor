# Full Source Parse Refresh (2026-02-11)

> Complete inventory-level parse of the public source-reference repositories used in this appendix.
> This refresh supersedes older partial-count notes.

## Scope and Method

Repositories parsed:

- `references/Onslaught`
- `references/AYAResourceExtractor`

Method:

1. Enumerated every file recursively.
2. Calculated file size, line count, and SHA-1 for each file.
3. Ran lexical extraction passes for:
   - includes
   - class declarations
   - scoped method names (`Class::Method`) for C/C++
   - namespace/class/method candidates for C#

This is a full-corpus parse for inventory and navigation grounding. It is not a claim that every method is semantically decompiled/mapped in retail `BEA.exe`.

## Output Artifacts

- `reverse-engineering/source-code/stuart-source-file-manifest-2026-02-11.tsv`
- `reverse-engineering/source-code/aya-resourceextractor-file-manifest-2026-02-11.tsv`

Each manifest row contains:

- relative path
- byte size
- line count
- SHA-1

## Parsed Corpus Metrics

### Stuart Source (`references/Onslaught`)

| Metric | Value |
|--------|------:|
| Total files | 111 |
| `.cpp` files | 52 |
| `.h` files | 53 |
| Other files | 6 |
| Unique include targets | 334 |
| Unique class declarations found | 145 |
| Unique scoped classes with method defs | 111 |
| Unique scoped methods (`Class::Method`) | 1097 |

Top `.cpp` files by scoped-method density:

| File | Scoped methods detected |
|------|------------------------:|
| `FEPGoodies.cpp` | 286 |
| `BattleEngine.cpp` | 145 |
| `game.cpp` | 100 |
| `FrontEnd.cpp` | 60 |
| `thing.cpp` | 57 |
| `SoundManager.cpp` | 51 |
| `Camera.cpp` | 48 |
| `DXEngine.cpp` | 47 |

Most frequent include targets:

| Include | Count |
|---------|------:|
| `common.h` | 30 |
| `debuglog.h` | 25 |
| `Common.h` | 22 |
| `console.h` | 15 |
| `Game.h` | 14 |
| `stdio.h` | 14 |
| `EventManager.h` | 12 |
| `Platform.h` | 12 |

### AYA Extractor Source (`references/AYAResourceExtractor`)

| Metric | Value |
|--------|------:|
| Total files | 75 |
| Source files parsed (`.cs/.cpp/.c/.h`) | 54 |
| C# files | 24 |
| C/C++ files | 30 |
| Unique include targets (C/C++) | 22 |
| Unique C# namespaces | 3 |
| Unique C# classes | 22 |
| Unique C# method candidates | 57 |

Top C# files by method-candidate count:

| File | Method candidates |
|------|------------------:|
| `Code/AyaResourceExtractor/AyaModelImporter.cs` | 14 |
| `Code/AyaResourceExtractor/MainForm.cs` | 9 |
| `Code/Fbx/FbxBinary.cs` | 7 |
| `Code/Fbx/FbxAsciiReader.cs` | 6 |
| `Code/AyaResourceExtractor/Log.cs` | 4 |
| `Code/Fbx/FbxIO.cs` | 4 |

## Practical RE Impact

1. The Stuart corpus is now fully indexed at file level with reproducible fingerprints.
2. Source-to-binary mapping can reference manifests for coverage accounting and drift detection.
3. AYA extractor knowledge now has parity-level inventory grounding (UI, parser, exporter, zlib/DDS wrapper layers).
4. Future “what changed in source references” checks can diff manifest hashes instead of re-scanning manually.

## Caveats

- Stuart source remains an internal PC build; Steam retail binary is console-port lineage and differs in on-disk layout and some runtime logic.
- Function-name similarity and code-structure hints are useful but must still be validated against retail binary behavior (`BEA.exe` + real saves).

## See Also

- `reverse-engineering/source-code/_index.md`
- `reverse-engineering/binary-analysis/functions/_index.md`
- `reverse-engineering/binary-analysis/functions/FUNCTION_COVERAGE_STATE.md`

---

*Generated: 2026-02-11*
