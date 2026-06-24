# CCredits__WriteEntry_String

- **Address:** `0x0051a010`
- **Status:** Mapped
- **Signature (current):** `void CCredits__WriteEntry_String(void * this, int section, char * text, int style)`
- **Confidence:** High

## Summary

Writes one direct-string credits row into the global credits table consumed by `CCredits__RenderCredits`.

## Behavioral Notes

- Companion helper to `CCredits__WriteEntry_TextId` (`0x00519ff0`).
- Used heavily by `CCredits__BuildDefaultEntries` to emit rows where text comes from static string pointers rather than localized numeric text IDs.
- Row shape is consistent with `{section, text_ptr, 0, style}` packing pattern used by the credits table builder.

## Evidence

- Direct caller: `CCredits__BuildDefaultEntries` (`0x00518bf0`).
- Same table region consumed by `CCredits__RenderCredits` (`0x0051a030`).
