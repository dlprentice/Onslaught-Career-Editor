# CUMTexture__InvalidateDeviceObjects

Status: active static function note
Last updated: 2026-09-27 (interface identity rederived; earlier body notes retain their stated limits)
Summary: retail device-lifecycle identity with retained, separately bounded August body analysis.
Source File: UMTexture.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened for that August review. At that date,
the table name was a research label. The `[vtable+8]` callee is **not** this proof.

> Address: `0x004f7bd0`

## September 27 interface correction

The former label `CUMTexture__VFunc_03_ReleaseTextureResource` is retained by this filename for stable links.
Fresh complete-body decoding, both typed list callers and all known RTTI holder
occurrences establish `CUMTexture__InvalidateDeviceObjects`; see the
[platform evidence](../../../source-code/core/platform-system.md#retail-device-lifecycle--september-27-correction).
The new name identifies its lifecycle interface. It does not establish the full
resource algorithm, source return type, callback lifetime or retail graphics
behavior. The August evidence statements below describe that earlier review;
its separate specimen twin was not reverified for this correction.

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x004f7bea`. Body `0x004f7bd0`–`0x004f7bea` is 27 bytes,
SHA-256
`a5fe000f2b8ee504daaf82c2c21deaece2c5dbeba481a00bc2336a1ea7c4092c`.
Zero `E8` / zero `E9`. If `[this+8]` is live, `call [[eax]+8]`
then store 0 at `+8`. `EAX` is forced 0.

The August direct-call scan reported zero inbound `.text` `E8`/`E9`.
The September raw-pointer/RTTI census corrects its unique-copy claim:
this entry occurs in both CUMTexture slot 3 at `0x005df914` and
CLandscapeTexture slot 3 at `0x005dc1fc`. Recreate already zeros `+8` after
the same shape of `[vtable+8]` call. That sibling body is **not**
re-derived here.

Cheapest falsifier: file `0x000f7bd0` is not
`56 8b f1 8b 46 08 85 c0`, **or** `0x000f7bea` is not `c3`,
**or** body SHA-256 is not `a5fe000f…092c`, **or**
`tools/call_xref_scan.py` on `0x004f7bd0` is not empty, **or**
`0x001dc1fc` is not `d0 7b 4f 00`, **or** `0x000f7be0` is not
`c7 46 08 00 00 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004f7bd0` | `CUMTexture__InvalidateDeviceObjects` | `568bf1 8b4608 85c0 740d 8b08 50 ff5108 c74608 00000000 33c0 5e c3` | thiscall; bare ret; 27 B; 0 E8/E9; 0 inbound; vtable slot 3; zeros `[+8]`. HIGH on ABI, inbound-empty, that slot, that store. **Not** on the `[vtable+8]` body. |
