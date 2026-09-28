# CBattleEngine__GetWeaponAmmoCount

Status: active static function note
Last updated: 2026-09-27
Summary: complete main dispatcher rechecked; its Jet callee now has a verified source identity.
Source File: `references/Onslaught/BattleEngine.cpp:2777-2783` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. | Binary: BEA.exe.original.backup, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0040c460`

Complete body `[0x0040c460,0x0040c47e]`: 31 bytes, six instructions;
raw-byte SHA-256 `2c9f1fac5c5af72c9ea1218e1b4499c12fe8ea76c5bf46f027d5c43485a7373c`. The ECX member takes no stack argument and
returns by tail jump through the selected part:

- Main state `+0x260 == 3`: load Jet from `+0x57c`, jump to
  `CBattleEngineJetPart__GetWeaponAmmoCount` at `0x00412240`.
- Every other state: load Walker from `+0x578`, jump to
  `CBattleEngineWalkerPart__GetWeaponAmmoCount` at `0x00414470`.

The Jet helper returns zero without a selected non-heat store. Otherwise it uses
`FISTP QWORD` and returns the low DWORD. It does not change the x87 control word,
so this is not proof of a universal C# cast or nearest-even rule. Out-of-range
conversion and the retail ambient control word remain separate questions.

The August note's restriction on identifying the Jet callee is superseded by
its complete-body/source/caller audit; frozen evidence is unchanged. This
recheck does not certify all callers, pointer validity, corrupt state or runtime
presentation. It does not change this dispatcher's Ghidra record.

Evidence: MEASURED — fresh complete decode in `local-data/test-runs/re-audit-20260926/jet/doc-recheck-v1.json`,
the [Jet helper manifest](../../../../tools/cohort-specs/jet-helper-identities-20260927.manifest.tsv),
and the [weapon-store contract](../../../game-mechanics/battle-engine-weapon-stores.md#september-27-jet-recheck).
Cheapest falsifier: compare the pinned body and its two receiver loads/tail targets
against the selected pristine specimen. No runtime rerun is claimed here.
