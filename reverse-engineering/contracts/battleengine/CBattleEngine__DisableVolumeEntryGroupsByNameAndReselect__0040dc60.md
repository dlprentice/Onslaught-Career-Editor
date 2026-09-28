# CBattleEngine__DisableWeapon

Status: active static contract
Last updated: 2026-09-27
Summary: source identity and ordered Walker/Jet byte-string forwarding re-derived from pristine instructions; failure and runtime limits remain open.
Source File: `references/Onslaught/BattleEngine.cpp:3237-3242` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. | Binary: BEA.exe.original.backup, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — complete pristine bodies and actual caller/argument transport, compared with the pinned source; static identity and structure only.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0040dc60`

## Identity and interface

The complete 37-byte body has raw-byte SHA-256
`d666fc300ce2dd4d230642cfc49d39d32ce7acf1be8823c909c284d35d2b38b5`. Its live name is now `CBattleEngine__DisableWeapon`.
The old `CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect` name and note remain qualified leads in Ghidra;
the historical filename is retained to preserve links.

```c
void __thiscall CBattleEngine__DisableWeapon(void * this, char * inWeaponName)
```

The receiver is ECX; the single pointer occupies the first four-byte stack slot;
`RET 4` balances that argument. The former `void *` parameter annotation is
now `char *`, supported by the byte comparisons in the complete callees. The
annotation does not establish an arbitrary character encoding or ownership.

## Behavior and limits

Always call Walker `0x00414a40` using main `+0x578`, then Jet
`0x00412830` using main `+0x57c`, forwarding the same name pointer.
There is no mode gate. The Jet helper uses a local list iterator, compares the byte-string name
case-sensitively and clears matching active DWORDs at `+0x9c`. It tests whether
the matched weapon is selected and invokes ChangeWeapon when so. The local
iterator survives that helper's changes to the shared cursor; re-selection is
not an unconditional action on every list entry.

The wrapper adds no pointer validation, transaction or rollback. No claim is made
about corrupt strings/lists, concurrent mutations or failure recovery. The
September recheck is static; the earlier empty TTD result is neither execution
proof nor evidence that the function is dormant. The former factory draft's
unknown component/identity claims are superseded; its numerical confidence cap
based only on missing TTD is not an evidence standard.

## Evidence and falsifier

Complete body/source/caller packets: `local-data/test-runs/re-audit-20260926/jet/`.
Exact [manifest](../../../tools/cohort-specs/jet-helper-identities-20260927.manifest.tsv)
and readbacks: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/jet-helper-identities/`.
See the [weapon-store contract](../../game-mechanics/battle-engine-weapon-stores.md#september-27-jet-recheck).
The previous frozen packet receipts remain historical. Compare the complete body,
call order, forwarded stack slot and both callees' byte-string comparisons to
falsify this contract. Runtime failure behavior needs a controlled experiment on
owned copies; no game or save was written for this recheck.
