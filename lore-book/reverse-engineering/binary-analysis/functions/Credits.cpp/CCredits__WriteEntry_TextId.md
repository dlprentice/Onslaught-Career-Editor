# CCredits__WriteEntry_TextId

- **Address:** `0x00519ff0`
- **Status:** Mapped (rename/signature/comment present; read-back verified)
- **Signature (current read-back):** `void __thiscall CCredits__WriteEntry_TextId(void *this, int section, int text_id, int style)`
- **Confidence:** Medium-high

## Summary

Small credits-table row writer used by `CCredits__BuildDefaultEntries`. It stores a 4-field row shaped like `{section, text_id, 0, style}` into the destination row pointer.

## Behavioral Notes

- Decompiled body writes:
  - `[this + 0x00] = section`
  - `[this + 0x04] = text_id`
  - `[this + 0x08] = 0`
  - `[this + 0x0c] = style`
- Callsite pattern in `CCredits__BuildDefaultEntries` is effectively `CCredits__WriteEntry_TextId(section, text_id, style)` with destination row pointer in `ECX`.

## Recovery Note

- This address did roll back once during a deadlock/crash-recovery cycle, but was successfully restored in a later lock-step pass (single write + read-back + save checkpoints).
