# `CThing` base-interface semantic crosswalk

Status: active, bounded semantic recovery  
Last updated: 2026-08-11  
Evidence: MEASURED — strict retail/demo RTTI, paired vtables, gapless decoded
bodies, constants, and dataflow; SOURCE — pinned `thing.h` and `thing.cpp`;
UNKNOWN — the one render-interface property explicitly left descriptive.  
Verdict: 30 of the 31 uniquely `CThing`-owned virtual targets now have exact
source/ABI identities. The remaining target has an exact forwarding contract
but no defensible historical method name in the retained source version.

Specimen: pristine PC retail `BEA.exe`, SHA-256 `74154bfae14ddc8e…`;
PC demo `BEA.exe`, SHA-256 `d8637dd755b21c720…`. Full hashes are pinned in
[`DEMO_VS_RETAIL.md`](../DEMO_VS_RETAIL.md).

## Result

Strict RTTI pairs the two `CThing` tables:

| Table | Retail | Demo | Slots | Structural key |
| --- | --- | --- | ---: | --- |
| Secondary render-facing table | `0x005DF550` | `0x005E0550` | 29 | `743d38fd03c128c5d58607c36d57c009a7e47b56e202ccb9f091662b4723fbc8` |
| Primary/audible `CThing` table | `0x005DF5C8` | `0x005E05C8` | 59 | `dafa51fa044b985ec33dec3ed9d0bda38f22a18f9c9fb77e563951ea6ef1a1e5` |

The semantic-owner cohort contains 31 targets, 1,401 retail body bytes, and
502 instructions. Nineteen bodies contain 49 raw-different instructions (92
bytes) in the independently linked demo; all differences disappear after
encoded address/displacement normalization. No target differs in opcode,
register, branch shape, or literal after normalization.

The full row set is
[`cthing-vtable-semantics-2026-08-11.tsv`](cthing-vtable-semantics-2026-08-11.tsv).
That 5,922-byte table has SHA-256
`5ae2f7aa713f549153de959b1a022489f09a297502b21b9ae447284ab79df710`.
The broader build comparison is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Interface recovery

The multiple-interface layout explains several old ownership mistakes:

- primary slots 3–5 are the audible position, orientation, and velocity
  projections;
- secondary render slots 0 and 1 are render position and orientation;
- secondary slots 9 and 10 reuse the position body for render start/end;
- primary slots 27, 30, and 31 are velocity, old position, and old orientation.

MSVC folds source-identical methods. `0x004040A0` implements
`GetRenderPos`, `GetRenderStartPos`, and `GetRenderEndPos` for the adjusted
secondary `this`. `0x0043E9F0` implements both `GetSoundPos` and `GetOldPos`.
Three separate identity-matrix copies at `0x004BFA00`, `0x004BFA20`, and
`0x004BFA40` have distinct ABIs: render orientation, sound orientation, and old
orientation. Address-only naming loses those distinctions.

## Corrected identities

Representative corrections include:

| Retail target | Old label | Recovered identity |
| --- | --- | --- |
| `0x00401400` | field/slot radius forward | `CThing::GetRenderRadius` |
| `0x00401440` | `GetRenderRadiusFromRenderThing` | `CThing::GetRadius` |
| `0x0043E9C0` | global-vector copy | `CThing::GetVelocity` |
| `0x0043E9F0` | `GetRenderPos` | folded `GetSoundPos` / `GetOldPos` |
| `0x004BFA00` | global-matrix copy | `GetRenderOrientation` |
| `0x004BFA20` | global-matrix copy | `GetSoundOrientation` |
| `0x004BFA40` | global-matrix copy | `GetOldOrientation` |
| `0x004F3470` | mask-or-one helper | `CThing::SetThingType` |
| `0x004F3760` | unnamed shutdown helper | `CThing::AddShutdownEvent` |
| `0x004F37A0` | unnamed death helper | `CThing::StartDieProcess` |

The larger lifecycle bodies also match the pinned source in order: `Init`
performs render initialization, type setup, ground/water clipping, map/collision
registration, activation, and world insertion; `Shutdown` removes membership,
shuts down the monitor, then deletes the object; `HandleEvent` owns the two base
terminal events; render and collision initialization preserve their exact
guards and fallbacks.

## Deliberate open name

`0x004F3D20`, secondary slot 21, adjusts `this`, reads `mRenderThing`, and
tail-dispatches its virtual slot 4, returning null when no render thing exists.
The retained header's nearby late render-interface declarations do not align
cleanly enough with the retail table to choose one historical name without
guessing. Its behavior is therefore recorded as `render-interface slot 21
property forward`, not promoted to a fabricated source symbol.

This is the only name left open in the owner cohort. It does not block use of
the function contract or inherited-table alignment.

## Recursive use

`CThing` supplies the ABI spine inherited by actors, units, squads, buildings,
projectiles, triggers, and level-script objects. Resolving these base slots lets
later passes identify subclass overrides by interface position even when their
source files are absent. That is the next use of this result; repeatedly proving
the same 31 envelopes would add no value.
