# Ghidra Dive/Dropship Aircraft Review Wave959

Status: read-only static re-audit PASS
Date: 2026-05-28
Tag: `dive-dropship-aircraft-review-wave959`

Wave959 re-reviewed the DiveBomber/Dropship aircraft slice after static export-contract closure. The wave made no Ghidra mutation: no renames, no signature changes, no comment/tag changes, no function-boundary changes, and no executable-byte changes.

## Scope

Focused Wave911 candidates re-reviewed:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00445380` | `CDiveBomberAI__scalar_deleting_dtor` | Live name/signature/comment/tags still match Wave358 static evidence. |
| `0x004453a0` | `CDiveBomberAI__dtor_base` | Live destructor-base evidence still shows pointer-set/monitor cleanup. |
| `0x00445440` | `CDiveBomberGuide__scalar_deleting_dtor` | Live scalar-deleting destructor evidence still matches Wave358. |
| `0x00445460` | `CDiveBomberGuide__dtor_base` | Live guide cleanup evidence still matches Wave358. |
| `0x00446d70` | `CDropship__Init` | Still calls `0x00496090 CMCDropship__Ctor` and references `wingflat`, `doorclosed`, and `Thruster Dust Effect`. |
| `0x00447040` | `CDropshipAI__scalar_deleting_dtor` | Live scalar-deleting destructor evidence still matches Wave358. |
| `0x00447060` | `CDropshipAI__dtor_base` | Live AI cleanup evidence still matches Wave358. |
| `0x00447100` | `CDropship__dtor_base` | Still calls `0x00402d30 CAirUnit__dtor_base` after occupancy-grid cleanup. |
| `0x00447120` | `CDropship__ProcessDoorThrustersAndChildUnits` | Current saved name is the Wave358 name, not the older historical `VFuncSlot_1c_00447120` boundary label. |
| `0x00402dd0` | `ShadowHeightfield__AnyBoundsCornerAboveSampledHeight` | Still called from `0x004478a3` inside `CDropship__ProcessDoorThrustersAndChildUnits`. |

Continuity/context anchors also re-read: `0x00448170 CDropship__TraceGroundAndSpawnThrusterDust`, `0x00445070 CDiveBomber__SelectTarget`, `0x0050eed0 CDiveBomber__scalar_deleting_dtor`, `0x0050ee70 CDropship__scalar_deleting_dtor`, `0x0050f1f0 CDropship__Destructor_VFunc01`, `0x0050f2d0 CDiveBomber__Destructor_VFunc01`, `0x00496090 CMCDropship__Ctor`, `0x004960c0 CMCDropship__ScalarDeletingDestructor`, `0x004960e0 CMCDropship__Dtor`, `0x00496100 CMCDropship__VFunc_05_UpdateDoorAnimationValue`, `0x00496200 CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow`, `0x0050f0a0 CAirUnit__ctor_base`, `0x0050f420 CAirUnit__scalar_deleting_dtor`, and `0x0050f440 CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct`.

## Evidence

Fresh serialized Ghidra exports under `subagents/ghidra-static-reaudit/wave959-divebomber-dropship-aircraft-review`:

- `24` metadata rows, all `OK`.
- `24` tag rows, all `OK`.
- `31` xref rows.
- `10296` around-address instruction rows.
- `1703` function-body instruction rows.
- `24` decompile-index rows, all `OK`.
- `256` vtable rows from `0x005e1dfc CDropship_vtable` and `0x005dc304 CMCDropship_vtable`.
- `8` direct string dumps: `C:\dev\ONSLAUGHT2\DiveBomber.cpp`, `C:\dev\ONSLAUGHT2\Dropship.cpp`, `wingflat`, `doorclosed`, `dooropening`, `doorclosing`, `Thruster Dust Effect`, and `Thruster`.

Representative anchors:

| Evidence | Anchor |
| --- | --- |
| `CDropship__Init` installs the motion controller | `0x00446e96 CALL 0x00496090`. |
| `CDropship__ProcessDoorThrustersAndChildUnits` calls the shadow-height helper | `0x004478a3 CALL 0x00402dd0`. |
| `CDropship__ProcessDoorThrustersAndChildUnits` spawns thruster dust through the helper | `0x004472b2` and `0x004473f9` call `0x00448170`. |
| `CDropship__dtor_base` delegates to the air-unit base cleanup | `0x00447110 CALL 0x00402d30`. |
| Primary aircraft scalar-deleting wrappers call their destructor bodies | `0x0050ee73 CALL 0x0050f1f0`, `0x0050eed3 CALL 0x0050f2d0`, and `0x0050f423 CALL 0x0050f440`. |
| AI/guide scalar-deleting wrappers retain one explicit stack argument | `0x0044539d RET 0x4`, `0x0044545d RET 0x4`, and `0x0044705d RET 0x4`. |
| Dropship dust helper retains stdcall cleanup | `0x0044835c RET 0x8`. |
| Vtable ownership still resolves to current names | `0x005e1dfc slot 57 -> 0x00447120`, `0x005dc304 slot 5 -> 0x00496100`, and `0x005dc304 slot 8 -> 0x00496200`. |

Continuity checks:

- `npm run test:ghidra-unitai-dive-dropship-signature`: PASS.
- `npm run test:ghidra-unitai-tail-guide-line-signature`: PASS.
- `npm run test:ghidra-meshpart-cmc-existing-signature`: PASS.
- `npm run test:ghidra-meshpart-cmc-slot-boundary`: PASS.
- `npm run test:ghidra-early-queue-signature-correction`: PASS.
- `npm run test:ghidra-heightfield-shadow-caller-boundary`: PASS.

The historical `npm run test:ghidra-air-unit-lifecycle-wave557` probe failed on two now-condensed master function-index tokens, and `npm run test:ghidra-gameplay-object-helpers-wave800` failed on current queue/state assertions tied to its 2026-05-24 snapshot. Wave959 treats those as stale continuity-probe coverage issues, not live Ghidra regressions; the focused Wave959 probe checks the relevant live metadata and instruction anchors directly.

Verified Ghidra backup:

```text
G:\GhidraBackups\BEA_20260528-120725_post_wave959_dive_dropship_aircraft_review_verified
```

Backup summary: `19` files, `173542279` bytes, `DiffCount=0`.

Wave911 focused re-audit progress after Wave959: `303/1408 = 21.52%`.
Static export-contract function-quality closure remains `6151/6151 = 100.00%`.

Probe anchor: Wave959; dive-dropship-aircraft-review-wave959; 0x00447120 CDropship__ProcessDoorThrustersAndChildUnits; 0x00448170 CDropship__TraceGroundAndSpawnThrusterDust; 0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight; 0x00445070 CDiveBomber__SelectTarget; 303/1408 = 21.52%; 6151/6151 = 100.00%; G:\GhidraBackups\BEA_20260528-120725_post_wave959_dive_dropship_aircraft_review_verified; no mutation.

## Boundaries

This wave proves static retail Ghidra continuity for the saved DiveBomber/Dropship/AirUnit names, signatures, comments, tags, xrefs, decompile output, vtable slots, instruction anchors, and string anchors listed above.

It does not prove runtime dropship door behavior, runtime thruster dust behavior, runtime child-unit deployment, runtime dive-bomber targeting, exact Stuart-source method identity, concrete `CDropship` / `CDiveBomber` / `CMCDropship` / AI/Guide layouts, BEA patching behavior, or rebuild parity.
