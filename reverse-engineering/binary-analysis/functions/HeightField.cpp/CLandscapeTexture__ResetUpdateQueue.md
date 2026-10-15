# CLandscapeTexture__ResetUpdateQueue

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label.

> Address: `0x0048e7b0`

## Contract

Not incoming-`ECX` thiscall. Zero-arg. Bare `ret` at `0x0048e7ba`.
Body `0x0048e7b0`–`0x0048e7ba` is 11 bytes, SHA-256
`197836ff43e727f704e2628552cb3081e15c3cb80de8f013a3896c7ce8f35a5e`:

```
mov dword ptr [0x0062d868], 0x006fa7d8
ret
```

Zero `E8` / `E9`. That store is the cursor already walked by
`CLandscapeTexture__FlushUpdateQueue`. Three inbound `.text` `E8`,
zero `E9`. Caller bodies are **not** claimed.

Cheapest falsifier: file `0x0008e7b0` is not
`c7 05 68 d8 62 00 d8 a7 6f 00 c3`, **or** body SHA-256 is not
`197836ff…5a5e`, **or** `tools/call_xref_scan.py` on `0x0048e7b0`
is not exactly `E8` at `0x00544b0a` / `0x00544f24` / `0x005450bd`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e7b0` | `CLandscapeTexture__ResetUpdateQueue` | `c70568d86200 d8a76f00 c3` | not incoming-ECX; bare ret; 11 B; stores `[0x0062d868]=0x006fa7d8`; 3 inbound. HIGH. **Not** on callers. |
