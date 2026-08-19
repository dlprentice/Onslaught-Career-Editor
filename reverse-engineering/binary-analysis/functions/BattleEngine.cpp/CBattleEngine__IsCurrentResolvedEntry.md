# CBattleEngine__DisplayLock

> Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe (the Ghidra database's specimen, SHA-256 `74154bfa…`)
> Address: `0x00407310`
> Status: source identity promoted in Ghidra 2026-08-04; 2026-08-19 byte contract added
> Last updated: 2026-08-19
> The **filename** is retained at the withdrawn name so historical links resolve.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).

| Address | Superseded label | 2026-07-28 intermediate label (historical) | Correction |
| --- | --- | --- | --- |
| `0x00407310` | `CBattleEngine__IsCurrentResolvedEntry` | `CBattleEngine__IsExpectedCurrentWeapon` | same class; suffix re-read |

## Source-identity promotion — 2026-08-04

The later backed-up, scratch-reproduced, independently refuted and separately
read-back target-lock promotion proves this range as
`CBattleEngine__DisplayLock`. Its live promotion READY is
`local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/promotion.ready.json`,
SHA-256
`77f635e552b7a2dd8425af012204f8172eadcb1de8ecdb02a30e2c12ff9b9945`.
The July comparator interpretation below is retained as historical analysis and
is superseded; it is not the current function contract.

**The rename invalidates part of this note's own supporting argument, and that is
said here rather than left for a reader to notice.** The "Summary" section below
argues that the decompile read-back *supports the name*, and one of the four
signals it lists is the exported signature line, which quoted the withdrawn name
back to itself. That signal is circular now and was always weak. The remaining
three signals — the two neighbouring symbols and the `ret 0x4` evidence — are
untouched and still support a **one-stack-argument boolean comparator**; what
they never established is what the compared thing *is*.

- **MEASURED:** the current symbol is `CBattleEngine__DisplayLock`.

---

## Status

- Named in Ghidra: yes
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

Historical July interpretation: a small comparator helper. The August 4
source-identity promotion supersedes that description with the bounded
`CBattleEngine::DisplayLock` contract.

The current decompile read-back supports the name with these token-level signals:

- `CBattleEngine__GetIndexedEntry`
- `CGeneralVolume__ResolveCurrentOrFallbackEntry`
- `bool __thiscall CBattleEngine__IsCurrentResolvedEntry(void * this, void * expectedEntry)` in the exported index
- `ret 0x4` instruction evidence

## Interpretation

This helper supports the BattleEngine current/fallback entry-resolution cluster. It is useful context for weapon and target selection paths, but by itself it does not prove gameplay behavior.

The 2026-05-09 early-helper signature tranche hardened this helper from a stale two-argument `int` signature to a one-stack-argument boolean comparator. The exact entry type, concrete `CBattleEngine` layout, local names, tags, runtime target/weapon behavior, and rebuild parity remain open.

## Boundaries

- Does not launch the game.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map; the signature/comment update was a direct headless postscript dry/apply/read-back pass.
- Does not prove runtime target or weapon selection behavior.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake landed `9f66373e` `CBattleEngine__FireLock` — not redone.
Name-correction history above is not rewritten.

Incoming-ECX `thiscall`. First insn `cmp dword [ecx+0x260], 3`.
Two `ret 0x4` (`0x00407340` EAX=1, `0x00407345` EAX=0). Body
`0x00407310`–`0x00407347` is 56 bytes, SHA-256
`e502e3861de140d14213ca3aead3640f9c4a2b5e7bef298101627be374125931`.
Two `E8`, zero `E9`. Neighbour table `CBattleEngine__Hit` starts
at `0x00407350` and is not claimed.

The body:

1. `[this+0x260]==3` → `ecx=[this+0x57c]` / `E8`
   `CBattleEngineJetPart__GetCurrentWeapon` `0x00412610`.
2. Else `ecx=[this+0x578]` / `E8`
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
3. If EAX==0 or EAX != `[esp+4]`, return 0. Else return 1.

Source architecture (not a field-name promotion):
`CBattleEngine::DisplayLock` `BattleEngine.cpp:980-994` compares
`mState==BATTLE_ENGINE_STATE_JET` then
`GetCurrentWeapon()==inWeapon`. Enum order in
`BattleEngine.h:28-33` makes JET the fourth enumerator (3).
`+0x260==3` / flight polarity was already closed on this
campaign. Callee bodies are **not** this proof.

One inbound `.text` `E8`/`E9`: `CALL` at `0x005074bb` inside
`ProjectileBurst__SpawnFromCurrentPreset` — the nonzero gate
immediately before `FireLock` `0x005074c9`. Zero encodings of
imm `10 73 40 00` in the image.

Rebuild owner: **none**. Same gap as FireLock
(`Level100ActorWeaponRuntime` scatter only). Do not implement
rebuild here.

Cheapest falsifier: file `0x00007310` is not `83 b9 60 02 00 00 03`,
**or** `0x0000731f` is not `e8 ec b2 00 00`, **or** `0x0000732c`
is not `e8 ff cc 00 00`, **or** `0x00007340` is not `c2 04 00`,
**or** body SHA-256 is not `e502e386…5931`, **or**
`tools/call_xref_scan.py` on `0x00407310` is not exactly one
`CALL` at `0x005074bb`.

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00407310` | `CBattleEngine__DisplayLock` | `83b96002000003 750d … e8ecb20000 … e8ffcc0000 … b801000000 c20400` (56 B) | incoming-ECX thiscall; ret 0x4 ×2; 56 B; 2 E8 Jet/Walker `GetCurrentWeapon` / 0 E9; 1 inbound `0x005074bb`. HIGH on ABI, `+0x260==3` arm, EAX=1 iff current weapon equals stack arg. **Not** on part-pointer names or rebuild parity. |
