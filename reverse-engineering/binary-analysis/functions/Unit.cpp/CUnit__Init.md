# CUnit__Init

> Address: `0x004f86d0`

Status: active static construction contract
Last updated: 2026-09-07
Summary: ordered profile, weapon, attached-spawner, Actor, recursive component,
world-list and event initialization. This supersedes the former speculative
armor, shield and kill-classification description; it does not establish live
Unit construction or runtime parity.
Evidence: MEASURED — selected complete pristine bodies and retained instruction
bytes were checked without opening Ghidra or running the game. Unit source is
absent from the pinned GPL drop `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: Unit.cpp (absent from the pinned GPL source) | Binary: BEA.exe.original.backup

## ABI and evidence

`thiscall`, ECX is the Unit and one stack argument is its initializer.
`RET 4` at `0x004f91ef` closes the complete 2,850-byte body
`[0x004f86d0,0x004f91f2)`, SHA-256
`dc3c02ae147e701c9840db77698dd0277501cab30f94f897179c06c762f7b7fd`.
Its fire-control callee `[0x004fb280,0x004fb3cd)` is 333 bytes, SHA-256
`5b5e4bf168556d656135d5fb780e330347a7df11c1c953d2e969f4193ceb1f85`.
The read-only instruction review matched 825 and 89 retained rows respectively,
with zero mismatches. The exports are W007 `004f86d0_CUnit__Init.c` and the W008
fire-control body under `local-lab/ghidra-fullpass-2026-07-23/exports/`, with
corresponding `instructions.tsv`. Static names do not prove callee behavior.
The independent base contract is [Actor.cpp.md](../Actor.cpp.md).

## Profile input

Unit Init begins by copying initializer `+0x3b4` (`mSpawnedBy`) into its
collision initializer `+0x6c`, copying initializer `+0x3bc` into Unit `+0x164`
(profile), and clearing Unit `+0x224` (the later fire-control gate). It does
not build a profile from the actor's display name or its numeric class ID.

| Profile field | Input consumed by Unit Init |
| --- | --- |
| `+0x2c`, `+0xe0` | Mesh name and internal behavior selector; selector 7 skips this body's mesh creation; the later CThing Init can invoke the class-specific render initializer. |
| `+0x3c` | Ordered weapon tuples: definition index, raw creation flags, mapped gun tag. |
| `+0x4c` | Ordered attached-spawner tuples: definition index, raw creation flags, mapped spawner tag. |
| `+0x5c` | Ordered component tuples: component-definition index and attachment index. |
| `+0xc0` | Raw life word copied to Unit `+0xf8` before Actor Init. |
| `+0xbc` | Turret-turn scalar; strictly greater than zero enables weapon-part inspection. |
| `+0x18`, `+0x1c` | Non-null gates for enumerating `Dust` and `Vent` attachment positions and allocating effect links. |

## Call and publication order

1. With a profile and selector other than 7, create render type 1 and initialize
   it from the profile mesh name. Selector 7 leaves lazy render initialization
   to the later base call when no renderer exists. Then walk weapon uses in list order.
   `CreateWeaponByIndex` (`0x0050f6d0`) creates a plain `CWeapon`, whose table
   `0x005dfc94` slot `+0x0c` points to the 24-byte shared initializer `0x0044a830`.
   That initializer copies owner Unit, literal 1, and gun tag into weapon
   `+0x08/+0x0c/+0x10`; Unit also writes tag `+0xac`. The weapon constructor
   selects mode zero through the real weapon/mode definition lists. When mesh
   and positive turret-turn scalar permit, inspect the selected `GunA` through
   `GunI` part chain: turret markers set weapon `+0x94`; barrel markers set
   weapon `+0x98`, Unit `+0x224`, barrel pointer `+0x220`, and reference angle
   `+0xf4`. Append each created weapon to Unit `+0x17c` only after these steps.
2. Walk attached spawners. The factory at `0x0050f970` allocates a `0x3f8`
   object using the attached-spawner constructor `0x004e37f0`. At Unit call
   `0x004f8a74`, embedded initializer `object+0x10` invokes Copy
   (`0x0048dbe0`), **not** standalone `CSpawnerThing::Init`. Override the
   copied initializer's target `+0xa4`, orientation type `+0x60` and roll
   `+0x4c` to zero; set active `+0x3ac` to one; clear script and name; retain
   copied spawn script. Set owner `object+0x3d4` and tag `+0x3e8`, then append
   to Unit `+0x18c`. This creates no immediate output unit. The constructor
   also resolves the spawn definition and can force its shared definition
   field `+0x10` to one when `IsSpawnTypeAllowed` rejects the selected class.
3. Copy profile life, then call Actor Init at `0x004f8b38`. Base initialization
   can publish, bind scripts, construct collision state and change pose
   before returning. Its movement scheduling consumes the shared RNG before
   the remaining Unit work. Script binding queues `INIT_SCRIPT` 2001; it does
   not execute the script's Init/Ready body inline. If initializer orientation
   type is Euler, Unit
   then copies its three authored angles into both `+0x114..+0x11c` and
   `+0x120..+0x128`; do not substitute these for the base's final pose.
4. Walk component uses. Create the actual component class through
   `0x0050fa40`, allocate a distinct reader and bind it to that child, obtain
   attachment position/orientation through owner virtual `+0x160`, then build
   a fresh component initializer with the selected profile, allegiance,
   active/attach words and spawn script. Call child virtual Init at
   `0x004f8d6c` before linking child back to its parent through `0x00428b50`
   and appending the reader to Unit `+0x19c`. This is recursive initialization,
   not an extra serialized world row or a mere child-ID assignment.
5. With a profile, allocate the primary effect link and enumerate nonzero
   `Dust`/`Vent` attachment positions under their profile gates. Then insert
   this Unit at the head of global list `0x008550d0` (`0x004f8fad`), and only
   afterward copy allegiance to Unit `+0x138`. This Unit-specific publication
   is separate from the earlier base Thing publication.
6. Scan mesh parts. An exact lowercase `turret` match causes a four-word copy
   from **mesh part index 2**, regardless of which index matched, into Unit
   `+0x1f8..+0x204` (`0x004f9037` proves the fixed index). Notify an existing
   squad reader via virtual `+0x110`; initialize an existing destructible
   segments controller (`0x00444660`); mark an existing exact profile-name catalog
   entry used (a miss changes nothing); increment
   the counter indexed by profile behavior for allegiance 0 or 1 only.
7. Call fire-control refresh at `0x004f90ce`, then scan all non-null mesh parts
   case-insensitively for `nexus` and `weakpoint`, setting `+0x228/+0x22c`.
   Clear `+0x230/+0x234/+0x238/+0x23c/+0x240/+0x244/+0x248`. If the squad
   reader is null, append allegiance 1 or 6 to list `0x008550c0`, then allegiance
   0 or 6 to `0x008550b0`. Finally request event 4003 at `-1.0f`, priority zero,
   null data and null reusable event (`0x004f91d8`). No active-state test
   guards this final request. Actual delivery belongs to the event manager.

## Conditional draw

Unit Init contains no direct RNG call. The fire-control helper is called
unconditionally; its enabled arm requires Unit `+0x224 != 0` and flags `+0x2c`
bit `0x04` clear. With no AI target,
it restores angle `+0xec` from `+0xf4` only when deadline `+0x20c < now`.
With a target, an eligible weapon profile can invoke the ballistic solver;
the target arm sets that deadline to `now + 10.0f`. For finite angles the
clamp is **-pi/2 to +pi**, with bits `0xbfc90fdb` and `0x40490fdb`; the stale
export comment claiming symmetric bounds is not the contract.

The enabled helper takes one shared RNG draw, uses the signed remainder by
65,536, multiplies by float word `0x35cccccd` (`0.1f / 65536`), adds the current
event time, and stores the resulting absolute time to float32 at
`0x004fb3bd` before calling `AddEvent_AtTime` for event 4001. Init passes null
reuse. Disabled gates take neither draw nor event. Actor, child initialization
and callbacks happen earlier, so this is not a total per-unit RNG count.

## Integration boundary

A complete owner still needs real ordered profile and weapon-mode resolution,
render/mesh state, base Actor/Thing script and collision effects, world
publication, recursive child Init, and present squad/destructible/target
callbacks. Later mesh accesses are unconditional: the null-profile branch is
not a usable default Unit. Preserve unknown fourth vector words rather than
zero-filling temporary storage. Static body closure does not establish all
allocation/resource failure paths or live behavior.

The [World110 admission](../../../game-mechanics/world-110-initial-constructor-seeds.md)
owns its actual profiles, dependency hashes, inherited-list caveat and four
landing-craft child inputs. Its first Control Tower now has bounded Core Init;
the 43 direct projections are not 43 completed Units. The resource-route usage
catalog remains empty, so the Tower's MarkUsed call is a no-op.
[The event handler](CUnit__HandleEvent.md) owns event 4003's later
behavior; scheduling it is not equivalent to executing it.
