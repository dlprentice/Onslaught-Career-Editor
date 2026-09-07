# CUnit__UpdateTransform

Status: bounded static contract with a connected World110 implementation
Last updated: 2026-09-07
Summary: profile attachment caching, exact float-store order, mesh lookup and
the four landing-craft Component constructor inputs. Retail execution and
complete child initialization remain unvalidated.
Source File: Unit.cpp (implementation absent from the pinned partial source); Binary: BEA.exe

> Address: 0x004fc4e0 | Source: Unit.cpp

No `Unit.cpp` implementation exists in the pinned partial GPL source.
This helper obtains an emitter pose. It is not a general movement,
terrain or collision update. The retained signature has four explicit arguments
(`RET 0x10`):

```c
void __thiscall CUnit__UpdateTransform(
    void *this,
    int emitter_slot_tag,
    int attachment_index,
    void *out_position4,
    void *out_basis3x4);
```

## Evidence boundary

The September 7 readback used the pristine
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
PE-mapped bytes matched the selected retained instruction rows, including final
returns. Ranges are half-open. Exports remain under
`local-lab/ghidra-fullpass-2026-07-23/exports/<wave>/instructions.tsv`.

| Body | Range | SHA-256 | Rows |
| --- | --- | --- | ---: |
| Unit attachment helper, W008 | `4fc4e0–4fc6de` | `6dca7328222914c701059e10645e6bbd420b8feaa1e3a6b81197bd690b29a4b0` | 167 |
| Slot/name routing, W008 | `4fc6e0–4fcbaf` | `0274f5fc8873012da9465c0a4fb8c294a719cef5447156f3db624a1629335ca8` | 445 |
| Matrix product, W001 | `40d320–40d470` | `fe3499fccd70b85b2d86fe58743db8c5bd84768ff0c1462541abd5744d8bd198` | 113 |
| Selected CEMT loader loop, W006 | `4ab210–4ab2af` | `28c94d4a96c86d8b6e0d85ba9512b0d34b43ee60ff91d795d1c983ff6d076702` | 53 |
| Name/selector lookup, W006 | `4aa820–4aa897` | `b5971f8c4e2fd788d75479c6ea0dc7f799958ff11beb2ca9eb3d3c24efd966b9` | 49 |
| Matrix-to-Euler, W003 | `44adb0–44ae13` | `050913e451bcb790be780e84b9af8f03a2235d6dcd97907d519f198c411c3254` | 36 |
| Asin arithmetic core, W011 | `55dccd–55dd7b` | `e463f0c1d4c485c396e47d94068839003b64d4841186aca1157de756198d5047` | 48 |

## Cache and mesh selection

The local-cache path requires Unit `+0x110 == 0`, a non-null profile at
`+0x164`, profile `+0x1a0 == 0`, and a tag outside 15 through 19. Its shared
profile list at `+0x6c` holds 72-byte entries: tag/index at `+0/+4`, position4
at `+8`, and basis12 at `+0x18`. Only the tag and index form the key.
This body performs no invalidation and includes no frame or pose in that key;
invalidation elsewhere has not been audited here.

A miss requests local mesh pose with skip-controller and force-refresh both
one. An all-zero XYZ returns without caching or world transformation. Otherwise
it stores the local pose, then applies the current Unit basis `+0x3c` and origin
`+0x1c` on every use. The fallback requests skip-controller zero and
force-refresh one. The eligible arm does not use interpolated render pose.

Tag 20 selects `Component`. Lookup compares the requested index directly with
the serialized emitter word at `+0x14c`; index 1 is not decremented or replaced
by record order. The chunked CEMT loader copies each 336-byte record, then reads
a trailing part index **only if record `+0x40` is nonzero**. Other records consume
no trailing dword. Names can repeat; selectors and nullable part bindings must
survive parsing. The materializer now uses the framed sibling, avoiding a
tag-shaped sequence inside a name or unrelated payload. Unknown emitter fields
remain carried raw by the existing mesh re-emitter.

## Arithmetic stores

For parent basis `A` and local position `p`, each row dot uses
`(A[i,2]*p.z + A[i,1]*p.y) + A[i,0]*p.x`. X adds the parent origin before
its float32 store. Y and Z first store their dots to float32, then add their
parent coordinates and store again. A uniform float expression or a uniformly
wide expression changes this contract.

For the basis product `C=A*B`, the first two products are added before the third
in these orders; each component has one final float32 store:

| Output row | Column 0 | Column 1 | Column 2 |
| --- | --- | --- | --- |
| 0 | 1,0,2 | 2,1,0 | 2,1,0 |
| 1 | 2,1,0 | 0,2,1 | 0,2,1 |
| 2 | 2,1,0 | 0,2,1 | 2,1,0 |

Those helpers do not select an x87 precision control. Core declares 53-bit,
round-to-nearest intermediates and explicit float32 stores. That is not a
claim about every retail runtime caller. Copied vector/matrix padding includes
unwritten temporary words; only XYZ and nine basis components are admitted.

## Four World110 Component inputs

The exact mesh and profile identities are recorded in the
[World110 constructor owner](../../../game-mechanics/world-110-initial-constructor-seeds.md#four-landing-craft-turret-children).
`Component`/1 selects part 31 (`Emit08`) through part 1 (`mainbody`) and part 0
(`Dummy root node`). Each has one hierarchy pose and 36 zero frame-map entries.
The selected stored CPOS/CORI meaningful components equal the parser's model
pose. Fresh parent/profile cache gates are zero; both parent attachment queries
precede installation of the Dropship animation and motion controller.

The four parent origins survive their actual ground/water clamps and delayed
collision responses. Complex Init `0x004f4008..0x004f40cc` separately stores
FCOS/FSIN of authored yaw. With pitch/roll positive zero, its signed-zero stores
matter: all four have negative-zero `M20`; the three negative-sine/negative-cosine
yaws also have negative-zero `M02`. The recipe preserves these words.

**The attachment matrix is not passed directly as child orientation.** Parent
initializer mode zero causes `0x004f8c99..0x004f8cc9` to call `0x0044adb0`, then
copy three Euler words into child `+0x44/+0x48/+0x4c`, with child mode zero.
The finite interior path computes pitch `asin(M21)`, yaw `atan2(-M01,M11)` and
roll `atan2(-M20,M22)`. Despite retained `Acos` labels, `0x0055dccd` computes
`sqrt((1+x)*(1-x))` followed by `FPATAN(x,sqrt)` for finite `|x|<1`.
Pitch is stored float32 but its unrounded result gates strict `(-pi,+pi)`;
the alternative writes positive-zero yaw/roll. There is no input clamp.
The four actual matrices take the interior, nonzeroing path. The helper keeps
control `0x027f` unchanged; other control-word and exceptional paths are outside
the Core claim.

`RetailWorld110InitialConstruction.Create()` now prepares four ordered
`ComponentInitInputs` using the actual parent identities and shared mesh data.
`RetailUnitAttachmentPose` computes the attachment and Euler words. It does not
allocate a child, bind its parent reader, run child Init or publish events.
The later child Euler-to-basis conversion remains part of unfinished Init.

An original native arithmetic probe under explicit x87 control `0x027f` measured
all four XYZ/basis/Euler results without executing any game code. Source and log
are in `local-data/test-runs/linux-route-20260906-af1sa_l9/` as
`x87-attachment-probe.c` (SHA-256 `1fb9411bb9ac16ea43396a72bc6da6e7f837f1ff1f20c580bcae80cc0285883c`)
and `.log` (SHA-256 `c33591ab4ab526c4cce593ebdce0def992fed4854a756af06db74ec3d5e65e86`).
The Core facts compare every meaningful output word against that probe and
separately falsify uniform translation spilling and generic matrix accumulation.
General animated attachments, exceptional inverse trig, complete construction
and player-visible parity remain open.
