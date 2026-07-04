# Ghidra GeneralVolume Active Reader/Input Review Wave966

Status: read-only static review
Date: 2026-05-28
Scope: `generalvolume-active-reader-input-review-wave966`

Wave966 re-reviewed the CGeneralVolume active-reader, linked-entry reselect, and yaw/pitch input bridge. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary reviewed rows:

| Address | Saved name | Static read-back evidence |
| --- | --- | --- |
| `0x00402020` | `CGeneralVolume__ResetCooldownTimestamp` | Stores global time `DAT_00672fd0` into `this+0xd4`; the saved signature still models the ignored `activeReaderTarget` stack argument. |
| `0x0040b100` | `CGeneralVolume__ctor_base` | Installs CGeneralVolume vtable pointer `0x005d892c` and zeroes fields `+0x4`, `+0x8`, and `+0xc`. |
| `0x0040c720` | `CGeneralVolume__ResetAndSetActiveReader` | Calls `CBattleEngine__SwapPrimarySecondaryPartReadersForState`, binds `this+0x264` through `CGenericActiveReader__SetReader`, then calls `CGeneralVolume__ResetCooldownTimestamp` with the same target. |
| `0x00412830` | `CGeneralVolume__DisableLinkedEntriesByNameAndReselect` | Walks linked entries, compares `entry_name` against each entry-name pointer at `entry+0xa4`, clears matching `entry+0x9c`, and calls `CBattleEngineJetPart__ChangeWeapon` when the disabled entry was selected. |
| `0x00413660` | `CGeneralVolume__ApplyYawInputByWeaponClass` | Reads owner `this+0x20`, applies weapon-class token multiplier `0xb/0xc`, scales the axis input by owner slot data and `DAT_005d8cd8`, then subtracts into owner yaw field `+0x278`. |
| `0x004136e0` | `CGeneralVolume__ApplyPitchInputByWeaponClass` | Reads owner `this+0x20`, applies the same weapon-class token multiplier, scales the axis input by `DAT_005d8c90`, then subtracts into owner pitch field `+0x280`. |

Context continuity:

- `0x0040dc60 CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect` dispatches the `+0x578` and `+0x57c` volume groups through the disabled-entry helpers, including the linked reselect row reviewed here.
- `0x00411e70 CBattleEngineJetPart__ChangeWeapon` still matches Stuart source `CBattleEngineJetPart::ChangeWeapon` shape: count weapons, select next active/usable weapon, clear slow movement, lose weapon charge, and auto-zoom out if zoom mode changes.
- Source snapshot corroborates the BattleEngine/JetPart/WalkerPart weapon reselect shape, but the current source snapshot does not include a concrete `Generalvolume.cpp` body. Treat CGeneralVolume names as static saved labels, not exact source-file proof.
- The first three primary rows have saved comments but no function tags; two comments still contain old "tags ... unproven" wording. Cursor `composer-2.5-fast` consult and root review both treated that as a documented discoverability gap, not enough evidence for a Wave966 Ghidra save.

Read-back evidence:

- Fresh exports: `13` metadata rows, `13` tag rows, `68` xref rows, `2465` around-address instruction rows, `728` function-body instruction rows, `13` decompile rows, `128` CGeneralVolume vtable rows, and `400` global-time/scalar xref rows. Body-instruction anchors include `0x00402025 MOV [ECX + 0xd4]`, `0x0040b10d MOV [EAX]`, `0x0040c724 CALL 0x00406460`, `0x0040c734 CALL 0x00401000`, `0x0040c73c CALL 0x00402020`, `0x004128cd CALL 0x00411e70`, `0x004136ab CALL 0x00409e60`, and `0x00413728 CALL 0x00409e60`.
- Queue remains `6152` total functions, `6152` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`; export-contract function-quality closure remains `6152/6152 = 100.00%`.
- Wave911 focused re-audit progress after Wave966: `340/1408 = 24.15%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-151637_post_wave966_generalvolume_active_reader_input_review_verified`, `19` files, `173542279` bytes, `DiffCount=0`.

What this proves:

- The reviewed GeneralVolume active-reader/input rows still exist in the saved Ghidra database with coherent saved names/signatures/comments.
- The xref/decompile/body-instruction evidence still supports the existing bounded active-reader timestamp, linked-entry disable/reselect, and yaw/pitch input summaries.
- The three untagged active-reader/constructor rows are a documentation/hygiene gap only for this wave; no semantic contradiction was found.

What remains unproven:

- Runtime active-reader behavior, selected-weapon behavior, yaw/pitch control feel, or option/input behavior.
- Exact `CGeneralVolume`, entry, BattleEngine owner, or weapon-list layouts and field names.
- Exact source-file or source-body identity for CGeneralVolume helpers.
- BEA patching behavior and rebuild parity.

Probe token anchor: Wave966; generalvolume-active-reader-input-review-wave966; 0x00402020 CGeneralVolume__ResetCooldownTimestamp; 0x0040b100 CGeneralVolume__ctor_base; 0x0040c720 CGeneralVolume__ResetAndSetActiveReader; 0x00412830 CGeneralVolume__DisableLinkedEntriesByNameAndReselect; 0x00413660 CGeneralVolume__ApplyYawInputByWeaponClass; 0x004136e0 CGeneralVolume__ApplyPitchInputByWeaponClass; 0x005d892c; tag gap documented; 340/1408 = 24.15%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-151637_post_wave966_generalvolume_active_reader_input_review_verified; no mutation.
