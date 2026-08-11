# Localization__GetStringById

> Source File: retail debug owner `text.cpp` (source file not retained) | Binary: pristine PC retail `BEA.exe`, SHA-256 `74154bfa…`; paired PC demo `BEA.exe`, SHA-256 `d8637dd7…`
> Address: `0x00524830`
> PC demo address: `0x00524b40`
> Status: hard-coded dispatch and complete cross-build logical table recovered
> Last updated: 2026-08-11

## Status

- **Named/signature set:** Yes
- **Signature:** `wchar_t* __cdecl Localization__GetStringById(int id)`
- **Confidence:** High for hard-coded dispatch and returned strings

## Purpose

Returns the PC-specific hard-coded wide string for an integer ID. It selects
one of five language tables from `g_LanguageIndex`, bounds the ID to 0–248, and
dispatches to a small return stub. Several undefined/local-control slots fall
through a common secondary dispatch table; six control-label IDs return one
runtime-populated shared wide buffer.

This is separate from `CText__GetStringById`, which resolves hashed IDs from the
loaded `data/LANGUAGE/<language>.DAT` file.

## Recovered contract

- Primary hard-coded surface: five languages × 249 IDs = 1,245 mappings.
- Languages represented by the five tables are English, French, German,
  Spanish, and Italian.
- IDs `58`, `63`, `68`, `71`, `77`, and `80` route through the common fallback
  and return runtime storage (`0x00677d78` in retail).
- All other resolved entries return a file-backed wide literal or null.
- Out-of-range IDs and unsupported language values retain their dedicated
  fallback paths; their exact caller-visible policy is not generalized here.

## PC demo comparison

The complete
[credits/localization lineage report](../../pc-demo-retail-credits-localization-lineage-2026-08-11.md)
resolves the initially changed demo body:

- ID 183 is the only changed primary mapping. Retail says DirectX 8 in all five
  localized diagnostics; demo says DirectX 9.
- The other 1,240 primary mappings return the same text or paired runtime
  buffer.
- Demo adds an American-English selector and a second 249-entry table, but its
  target list is exactly identical to ordinary demo English. External
  `american.DAT` behavior remains separate.

## Evidence boundary

The body, jump tables, return stubs, literal contents, and paired runtime buffer
are statically measured. This does not prove that every ID is reached, the
runtime contents of the shared buffer, which graphics failure selects ID 183,
or equality of external language data.
