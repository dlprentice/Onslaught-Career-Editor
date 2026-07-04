# Ghidra CUnit Constructor / Mat34 Euler Wave548 Readiness Note

Date: 2026-05-18

## Scope

Wave548 hardened two adjacent static Ghidra functions:

| Address | Saved symbol |
| --- | --- |
| `0x004f7e90` | `void * __fastcall CUnit__ctor_base(void * this)` |
| `0x004f8140` | `void __thiscall Mat34__SetFromEulerDegrees(void * this, int yaw_deg, int pitch_deg, int roll_deg)` |

## Evidence

- `CUnit__ctor_base` calls `CComplexThing__ctor_base`, installs transient CActor vtables, then installs CUnit primary/secondary vtables `0x005df998`/`0x005df920`, initializes active-reader/list/health/orientation/state fields, calls `Mat34__SetFromEulerDegrees` twice, and returns `this`.
- `Mat34__SetFromEulerDegrees` takes the destination matrix in ECX, converts three integer degree arguments through constant `0x005dfb6c`, builds basis rows through Vec3/Mat34 helpers, copies 12 dwords into the destination, and returns with `RET 0x0c`.
- Xrefs for the constructor are object/unit factory paths including `OID__CreateObject`, `CGroundUnit__Constructor`, `CBigAirUnit`/`CAirUnit` constructors, `CWorldPhysicsManager__CreateThingByType`, and `CWorldPhysicsManager__CreateCharacter`.
- Xrefs for the matrix helper include CUnit construction, CEquipment construction, CMonitor tracking, and ProjectileBurst spawning, making the previous CActor-specific helper name too narrow.

## Read-Back

- Dry: `updated=0 skipped=2 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply: `updated=2 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Verify dry: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`.
- Ghidra save reported `REPORT: Save succeeded`.
- Post exports verified `2` metadata rows, `2` tag rows, `25` xref rows, `858` instruction rows, and `2` decompile exports.
- Focused probe: `py -3 tools\ghidra_cunit_ctor_matrix_wave548_probe.py --check` PASS.
- npm wrapper: `cmd.exe /c npm run test:ghidra-cunit-ctor-matrix-wave548` PASS.
- Queue refresh: PASS with `6089` total functions, `2656` commented, `3433` commentless, `1535` exact-undefined signatures, and `1286` `param_N` signatures.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-120643_post_wave548_cunit_ctor_matrix_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

- Exact CUnit source body.
- Concrete CUnit or Mat34 layout and field names/types.
- Exact angle order or convention beyond the static argument flow.
- Runtime construction/orientation behavior.
- BEA patching or rebuild parity.
