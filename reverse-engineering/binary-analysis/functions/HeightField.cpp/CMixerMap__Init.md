# CMixerMap__Init

Status: active static function note
Last updated: 2026-08-19
Source File: MixerMap.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_b56783b2`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee bodies and shade-plane algebra are **not** this proof.

> Address: `0x005232b0`

## Contract

`thiscall`. `ECX`→`EDI`. One stack dword (`ret 4` at
`0x005233bb`). Body `0x005232b0`–`0x005233bd` is 270 bytes,
SHA-256
`5cc6bc9ac86a5919012b24073be7a76847793a4144f1fd4230bbd497ed72411d`.
Nine instruction-aligned `E8`, zero `E9`. A raw `E9` at
`0x00523390` is the `rel8` of `jl 0x0052337a` (`7c e9`); Capstone
does not agree it is a jmp.

One inbound `.text` `E8`, zero `E9`: already-pinned Deserialize
`0x004910e1`. The site is:

```
push edi
mov  ecx, 0x0089bd80
call 0x005232b0
```

File `0x000910dc` is `b9 80 bd 89 00 e8 ca 21 09 00`. `EAX` after
return is not tested. Caller body is **not** claimed.

If entry `[this+0]` is live: `push 0x00523210` / `[ptr-4]` /
`0x14` / `ptr` into `0x0055db0a`, Free `esi`, then `[this+0] = 0`.
Then Alloc size `0x14004` (string `C:\dev\ONSLAUGHT2\mixermap.cpp`
at `0x00640030`); if live, vector-ctor `0x00523210`/`0x00523200`
over `0x1000` slots of stride `0x14` and `[this+0] = esi`. Second
Alloc size `0x40000` then `[this+4] = eax`. Loop
`esi += 0x14` until `0x14000` calling `0x00523190` at
`[this+0]+esi` (first gates:
[`CMixerMap__InitSlot.md`](CMixerMap__InitSlot.md)). Then `GetNext` / `Read([this+4], 1, 0x40000)`
through the inbound stack arg in `EBX`. Callee bodies are **not**
claimed. `0x00523200` has no table name.

Cheapest falsifier: file `0x001232b0` is not
`6a ff 68 09 69 5d 00 64`, **or** `0x001233bb` is not `c2 04 00`,
**or** body SHA-256 is not `5cc6bc9a…411d`, **or**
`tools/call_xref_scan.py` on `0x005232b0` is not exactly `E8` at
`0x004910e1`, **or** `0x000910dc` is not
`b9 80 bd 89 00 e8 ca 21 09 00`, **or** `0x001232c9` is not
`8b f9`, **or** `0x0012336e` is not `89 47 04`, **or**
`0x00123389` is not `81 fe 00 40 01 00 7c e9`, **or**
`0x00240030` is not `C:\dev\ONSLAUGHT2\mixermap.cpp\0`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005232b0` | `CMixerMap__Init` | `6aff6809695d00 … 8bf9 … 894704 … 81fe00400100 7ce9 … c20400` | thiscall; ret 4; inbound `mov ecx,0x0089bd80`; 9 E8 / 0 aligned E9; writes `[+0]`/`[+4]`; walk `0x14` to `0x14000`; Read `0x40000` at `[+4]`. HIGH on ABI, inbound, those slots, those immediates. **Not** on callee bodies, `0x00523200`, or authored names. |
