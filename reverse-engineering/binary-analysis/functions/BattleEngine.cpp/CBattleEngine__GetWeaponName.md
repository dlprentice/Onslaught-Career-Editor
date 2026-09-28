# CBattleEngine__GetWeaponName

Status: active static function note
Last updated: 2026-09-27
Summary: complete main dispatcher rechecked; its Jet callee now has a verified source identity.
Source File: `references/Onslaught/BattleEngine.cpp:2819-2825` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. | Binary: BEA.exe.original.backup, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0040c550`

Complete body `[0x0040c550,0x0040c56e]`: 31 bytes, six instructions;
raw-byte SHA-256 `1ced8b7a2f1990b1041a2ac6d17316b1130a8e92859e9a2ec10b20e83232a828`. The ECX member takes no stack argument and
returns by tail jump through the selected part:

- Main state `+0x260 == 3`: load Jet from `+0x57c`, jump to
  `CBattleEngineJetPart__GetWeaponName` at `0x00412420`.
- Every other state: load Walker from `+0x578`, jump to
  `CBattleEngineWalkerPart__GetWeaponName` at `0x004145a0`.

The Jet helper returns null when there is no selected weapon. Otherwise it
forwards the profile language identifier at `+0x3c` to lookup `0x004f2580`,
receiver `0x0083d960`. This is distinct from the physics name, icon name and
attachment index. Its existing `short *` result annotation is retained; this
pass does not prove the full text representation, ownership or lifetime.

The August note's restriction on identifying the Jet callee is superseded by
its complete-body/source/caller audit; frozen evidence is unchanged. This
recheck does not certify all callers, pointer validity, corrupt state or runtime
presentation. It does not change this dispatcher's Ghidra record.

Evidence: MEASURED — fresh complete decode in `local-data/test-runs/re-audit-20260926/jet/doc-recheck-v1.json`,
the [Jet helper manifest](../../../../tools/cohort-specs/jet-helper-identities-20260927.manifest.tsv),
and the [weapon-store contract](../../../game-mechanics/battle-engine-weapon-stores.md#september-27-jet-recheck).
Cheapest falsifier: compare the pinned body and its two receiver loads/tail targets
against the selected pristine specimen. No runtime rerun is claimed here.
