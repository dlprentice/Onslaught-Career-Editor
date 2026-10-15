# Loose root data contracts (`*.dat` and `Dial.raw`)

Status: active format contract — three unrelated DAT schemas plus one RAW asset;
never use a generic `.dat` parser
Date: 2026-08-28
Verdict: worldheaders and the hash-pinned Battle Engine configuration baseline
are byte-exact; the other two root files retain bounded, unrelated contracts.
Evidence: MEASURED — all nine mirror-index `.dat` rows and the one `.raw` row
were rechecked. Six DATs belong to
[localization-text.md](localization-text.md); this file owns the remaining three
root DATs plus `Dial.raw`.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population

| File | Bytes | SHA-256 | Contract state |
| --- | ---: | --- | --- |
| `battle engine configurations.dat` | 1,514 | `58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a` | hash-gated version-12 parser/re-encoder; unknown spans retained raw |
| `default physics.dat` | 175,603 | `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14` | complete outer statement framing; semantics partial |
| `worldheaders.dat` | 4,783 | `34f2f45027a165fedde0e306b61fbabf64332724ced1e7a763103248fea07524` | byte-exact parser/re-encoder |
| `Dial.raw` | 8,192 | `2c57b657b92cd8bd73ca8c8986e8ce60aaffb065fdde09940053a2dd6d59671c` | exact bounded HUD input; general layout open |

This corrects the earlier summary error: the non-localization count is **three
`.dat` files**, not four. `Dial.raw` is separate and must not be counted as DAT.

## `worldheaders.dat` exact layout

[`tools/worldheaders_decode.py`](../../tools/worldheaders_decode.py) parses and
re-encodes every byte:

```text
file:
  i32le file_version = 1
  i32le record_count = 97
  record[97]

record:
  i32le version = 3
  i32le payload_size
  i32le world_id
  i32le config_count
  repeat config_count: u8 byte_length; ASCII bytes[byte_length]
  i32le field_a, field_b, field_c, field_d
```

Strings are not NUL-terminated, padded, or aligned. In all records,
`payload_size = 24 + sum(1 + string_length)`. Configuration names join to the
Battle Engine configuration file; the four trailing integers remain deliberately
unnamed.

Retail routes: `CWorld__LoadWorldHeader @ 0x0050D4C0`, configuration list
load/skip at `0x0040F180` / `0x0040F260`, and lookup at `0x0040F2F0`.

## `battle engine configurations.dat`

[`tools/battle_engine_config_decode.py`](../../tools/battle_engine_config_decode.py)
consumes and re-encodes all 1,514 bytes as six version-12 profiles: Racer,
Standard, Sniper, Aquila Prototype, Laser, and Blaster. Exact-mode identity is
the hash above plus record starts `0x004`, `0x0D4`, `0x1EE`, `0x2D2`, `0x3DE`,
and `0x4DD`; parsing and encoding are in-memory and expose no installation-write
or patch-authorisation path. The public-safe
[`battle-engine-config-layout.tsv`](battle-engine-config-layout.tsv) covers all
1,514 bytes through 248 explicit spans with zero gap or overlap while retaining
689 unknown bytes raw and withholding their payload from the TSV. Supported
scalar/name/store spans cite existing shipped-byte owners; unadjudicated strings
and the final integer remain explicit `UNKNOWN` spans with offset, width,
raw-byte preservation, and a cheapest falsifier.

`CBattleEngineData__LoadFromMemBuffer @ 0x0040F980` is a 1,939-byte static field
consumer with 42 `CDXMemBuffer__Read` calls. Its unchecked legacy-version and
malformed-input behavior is not reproduced: this public tool fails closed on
wrong version, truncation, trailing slack, invalid framing, and exact-mode hash
drift. Complete profile-selection behavior remains outside this format owner.
`Paladin Prototype` appears in world 001's header but not among the six records.

## `default physics.dat`

The complete shallow framing consumes all 175,603 bytes:

| Type | Family | Statements |
| ---: | --- | ---: |
| 1 | Unit | 160 |
| 2 | Weapon | 139 |
| 3 | WeaponMode | 145 |
| 4 | Round | 91 |
| 5 | Spawner | 38 |
| 6 | Explosion | 118 |
| 7 | Component | 39 |
| 8 | Feature | 43 |
| 9 | Hazard | 4 |
|  | **Total** | **777** |

Header value 18 precedes 6,803 field/value nodes covering 185 unique type/field
pairs and 73,796 payload bytes. The stream ends with `-1` and no unconsumed
bytes. This is outer framing, not full field meaning. The static reload owner is
`CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData @ 0x00510800`;
individual value factories and consumers require their own contracts.

Record and field multiplicity are now explicit. The 777 ordered records contain
775 unique `(family, name)` keys: `Bullet Hit` occurs twice in Explosion and
`Boat Sabre Spawner` occurs twice in Spawner. Neither pair is byte-identical.
The two `Bullet Hit` records begin at `0x41ED` and `0x42AA`; their field-2 and
field-7 effect/timeline strings differ. The two `Boat Sabre Spawner` records
begin at `0x18C48` and `0x18E1F`; field 1 names `AV-14B Sabre Pulse Tank` in the
first and `M-1 Broadsword Main Battle Tank` in the second. In addition, 147
records repeat at least one field id. A parser that indexes either level with a
plain dictionary therefore loses released data. The rebuild materializer's
ordered parser now retains both multiplicities: its record accessor refuses an
ambiguous name, and its field accessor refuses an ambiguous field id instead of
silently selecting one.

### Unit behaviour and Spawner join

All 160 Unit records carry exactly one four-byte field 8. That value is a
serialized behaviour-leaf type, not the raw construction selector. The retail
type-12 factory, exact RTTI leaves, and leaf slot-1 returns close the complete
type-to-selector conversion in
[`CPhysicsScriptStatements.cpp.md`](../binary-analysis/functions/CPhysicsScriptStatements.cpp.md#unit-behaviour-type-to-selector-closure).
The corpus uses 24 of the 25 admitted types: type 2 / `CJeepBehaviourType` /
selector 11 is the sole absent type. Known released observations reproduce the
ordered Unit registry exactly: `Air Trainer` is ordinal 31 / selector 8,
`Target Tank` is 87 / 2, `Control Tower` is 120 / 7, and
`Forseti City Building 1` is 156 / 25.

Every one of the 38 Spawner records has one NUL-terminated field-1 Unit name,
and all 38 join exactly to one of the 160 Unit records with zero unresolved
names. They reference 21 distinct Units. The resulting raw-selector population
is:

| Selector | Member class | Spawner records |
| ---: | --- | ---: |
| `0` | `CMech` | 3 |
| `2` | `CGroundVehicle` | 16 |
| `3` | `CInfantryUnit` | 11 |
| `8` | `CPlane` | 6 |
| `16` | `CDiveBomber` | 2 |
|  | **Total** | **38** |

This is definition-corpus reach, not proof that every spawner is placed or
executes in a released world. The separate squad-size and concrete-factory
consequences are owned by
[`spawner-squad-cycle.md`](../game-mechanics/spawner-squad-cycle.md).

## `Dial.raw`

Measured shape: exactly 8,192 bytes, no identified header, and only byte values
0, 2, 4, 5, and 6. The released HUD path identifies frame zero as the compass
north treatment. The size permits multiple plausible dimensions and encodings;
it does not prove 64×64, 16-bit pixels, a palette, or frame count. The rebuild
retains the exact hash as a bounded consumer, not a general RAW decoder.

## Open questions and falsifiers

- Name the four world-header trailing fields only after static/runtime evidence.
- Adjudicate the remaining `UNKNOWN` Battle Engine spans and resolve `Paladin
  Prototype` without synthesizing missing content.
- Produce a type/value ledger for all 6,803 physics nodes and trace one value per
  family to behavior.
- Recover `Dial.raw` dimensions, frames, palette/lookup, and orientation from the
  retail HUD consumer; test only on copied inputs.

## Claim boundary

World-header layout and the exact shipped Battle Engine configuration baseline
are byte-exact; physics outer fields are bounded; Dial is exact-input only.
Unknown configuration-span semantics, runtime selection, retail malformed-input
behavior, and parity remain open.
