# Semantic Documentation Audit (2026-02-12)

This pass focuses on **semantic integrity** of RE notes (not link integrity): ensuring that claims about source alignment and verification are backed by consistent, parseable references to `references/Onslaught/`, and that doc headers clearly communicate whether a Stuart-source file exists in our snapshot.

## Scope

- Scanned all repo markdown (`802` files) for:
  - `Verified vs Source: Yes` claims without any `references/Onslaught/` citation
  - malformed `references/Onslaught/...` references (missing files, invalid line numbers, missing identifiers)
- Normalized function-doc header `Source:` fields where possible.
- Performed targeted content corrections where source-backed docs were misleading or stale.

Machine-readable artifact: `reverse-engineering/binary-analysis/semantic-audit-pass-2026-02-12.json`.

## Results (High-Level)

- `Verified vs Source: Yes` docs without any `references/Onslaught/` citation: **0**
- Function docs with a header `Source:` line: **171**
  - Header `Source:` pointing into `references/Onslaught/`: **155**
  - Header `Source:` explicitly marked as missing from the source snapshot: **16**

## Key Corrections Applied

- Career:
  - `CCareer__Blank` now explicitly maps to Stuart’s `CCareer::Blank()` and the placeholder signature reflects that name.
  - `CCareer__GetGradeFromRanking` now cites `references/Onslaught/Career.cpp` and uses `WCHAR` in the source-reference signature.
  - Removed the non-standard `Career.cpp::CCareer::...` formatting in favor of `references/Onslaught/Career.cpp` (`CCareer::...()`).

- Player:
  - `CPlayer__ctor` and `CPlayer__dtor` were rewritten to reflect Stuart’s actual constructor signature (`int number`) and empty destructor body, removing generic/hand-wavy claims.

- CLI Params:
  - `CLIParams__ParseCommandLine` now cites the correct Stuart-source entry point (`CCLIParams::GetParams(int, char**)`) and avoids presenting the retail signature as source-derived.

- HeightField:
  - Removed a misleading “Source: `references/Onslaught/HeightField.cpp`” note, since that file is not present in our Stuart-source snapshot; the mapping remains binary-only via debug-path xrefs.

## Remaining Work

This audit does **not** prove that every behavior summary matches retail decompilation. It ensures:
- source citations exist where “source-verified” is claimed, and
- citations are syntactically and filesystem-valid.

For deeper semantic verification, the next pass should focus on:
1. Docs marked “Partial” verification (confirm/downgrade specific claims and add evidence snippets).
2. Function docs that still contain `TODO` signatures (prioritize ones that drive save-file offsets/encoding rules).
3. Any “Unknown/likely/inference” docs that are referenced as foundations by other notes (tighten wording or add evidence).
