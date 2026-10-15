# CFrontEnd__ResolveLevelNameTextByCode

- Address: 0x00469550
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `short * __cdecl CFrontEnd__ResolveLevelNameTextByCode(int level_code)`

## Purpose

Resolves a level/world numeric code to localized wide text, with an `Unnamed Level` fallback when the code is unmapped.

## Notes

Wave 377 hardened the return type and argument name for the already named helper. Static decompile evidence shows mapping to localized text through the text database and a wide scratch-string fallback.

This is static evidence only. Runtime localization behavior remains unproven by this page.
