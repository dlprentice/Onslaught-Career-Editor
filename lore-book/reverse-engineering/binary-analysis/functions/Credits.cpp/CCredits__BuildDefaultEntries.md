# CCredits__BuildDefaultEntries

- **Address:** `0x00518bf0`
- **Status:** Mapped (rename/signature/comment present; read-back verified)
- **Signature (current):** `void CCredits__BuildDefaultEntries(void)`
- **Confidence:** High

## Summary

Builds the static credits-entry table used by the renderer. The function writes a long sequence of rows into global storage (`DAT_00896ca8..DAT_0089754c`) containing section/type values, localized text IDs, raw string pointers, and style fields.

## Behavioral Notes

- Uses two tiny row-writer helpers repeatedly:
  - `CCredits__WriteEntry_TextId` (`0x00519ff0`) for numeric text-ID rows.
  - `CCredits__WriteEntry_String` (`0x0051a010`) for direct string-pointer rows.
- Final row appears to be a terminator-like entry (`FUN_00519ff0(3, 0, 3)` at the end of the builder stream).

## Evidence

- Startup thunk at `0x00518be0` is `JMP 0x00518bf0`, with data reference at `0x00622878`.
- `CCredits__RenderCredits` (`0x0051a030`) consumes the same global table region while drawing.

## Recovery Note

- This address did roll back once during a deadlock/crash-recovery cycle, but was successfully restored in a later lock-step pass (single write + read-back + save checkpoints).
