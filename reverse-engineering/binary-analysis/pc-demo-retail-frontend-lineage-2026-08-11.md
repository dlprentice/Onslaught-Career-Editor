# PC demo/retail frontend lineage

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — three independently bounded function bodies in the exact
PC demo and pristine retail executable, exact texture-name multisets, mapped
calls and data offsets, strict RTTI/vtable placement, and the extracted demo
publisher texture; SOURCE — retained frontend virtual ordering; UNKNOWN —
rendered pixels, transition interpolation, and why retail retains an unused
intro-page texture pointer.
Verdict: the demo adds a publisher surface to the intro-page render sequence
and routes completed debriefing back to its dedicated demo main page. Retail
loads an Infogrames texture into the corresponding shared-resource field but
does not submit that field from its bounded `CFEPIntro::Render`; playable-demo
debrief completion instead writes the frontend quit/result sentinel.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The machine-readable result is
[`pc-demo-retail-frontend-lineage-2026-08-11.tsv`](pc-demo-retail-frontend-lineage-2026-08-11.tsv).
It is 2,343 bytes with SHA-256
`83299b9d4b1f067778f58cf217c95f496f6a71324533c945ef82f342d8df5499`.
The three retail bodies total 4,238 bytes / 1,325 instructions; their complete
demo bodies total 4,308 bytes / 1,346 instructions. Body hashes and exact
extents are retained in the table. This independently closes three more of the
65 address-mapped bodies that the first whole-executable census left changed
or incompletely bounded. Together with the five-function FMV/startup report,
eight are now semantically bounded and 57 remain in that queue.

## Shared-resource substitution

Retail `CFrontEnd::LoadSharedResources @ 0x004687E0` and demo
`0x00468800` are complete 832- and 834-instruction bodies. Each issues exactly
86 calls to its paired `CTexture::FindTexture` target and requests 86 unique
texture names. Their name multisets differ in exactly one element:

| Build | Edition-specific lookup |
| --- | --- |
| Retail | `FrontEnd\v2\fe_infogrames.tga` |
| Demo | `fe_publisher.tga` |

The paired `CFrontEnd::Init` callsites establish the receiver bases:
retail `0x0089D760`, demo `0x0089EBB8`. Both loaders store the edition-specific
lookup result at receiver offset `+0x124`. In the demo, the exact string is at
`0x0062B418`, the lookup call is at `0x00468E41`, and the result store is at
`0x00468E46`.

The read-only demo extraction independently contains:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `BattleEngine/EXE/fe_publisher.tga` | 12,827 | `5a0a8f79a7a8ec45810fa98197be7f238395ec2b5af3d3f1ee59b42670d87cdb` |

This proves an edition-specific resource substitution at one stable frontend
data field. It does not by itself prove that either texture is displayed; the
consumer body below supplies that second half for the demo.

## `CFEPIntro::Render` identity and added demo surface

Retail `0x0051B840` was previously saved as
`CFEPIntro__VFunc_5_0051b840`. Strict RTTI places the paired retail/demo targets
in `CFEPIntro` vtable slot 5. The retained frontend page declaration order fixes
slot 5 as `Render`, and the body shape independently agrees: it accepts two
explicit arguments (`RET 8`) and submits a sequence of frontend surfaces.

The source authority for the sibling virtual order is
`references/Onslaught/FEPGoodies.h`, SHA-256
`b03caf0728288bf680d53dd28100fa6e76cd28f49cdbe95e8b7d8296860ef4c7`.
The recovered semantic identity is therefore `CFEPIntro::Render`; this report
does not claim that the tracked Ghidra snapshot has already been renamed.

After masking only encoded address/displacement bytes, the two complete bodies
have a `SequenceMatcher` ratio of 0.9681668. Their major blocks align as follows:

| Retail | Demo | Result |
| --- | --- | --- |
| `0x0051B840–0x0051BB0F` | `0x0051BB10–0x0051BDDF` | 187 aligned instructions |
| — | `0x0051BDDF–0x0051BE2C` | 22 demo-only instructions |
| `0x0051BB51–0x0051BE69` | `0x0051BE62–0x0051C17A` | 242 aligned instructions through return |

The demo-only block reads absolute `0x0089ECDC`, which is the demo frontend
base plus `0x124`. It tests the pointer and, when nonzero, submits exactly one
`CDXSurf::RenderSurface` call at `0x0051BE24`. The common sequence then proceeds
to the next surface; demo `0x0051BE2C` and retail `0x0051BB0F` both read their
build-relative frontend base plus `0x5C`, the shared Lost Toys surface field.
The first common draw similarly reads base plus `0x120` in both builds.

Thus the demo loader's `fe_publisher.tga` pointer and the demo-only render block
form one exact producer/consumer chain. The bounded retail render body contains
no corresponding `+0x124` surface submission even though the retail loader
stores `fe_infogrames.tga` there. Whether another retail page consumes that
pointer remains open.

## Debrief completion policy

Retail `CFEPDebriefing::ButtonPressed @ 0x004568A0` and demo
`0x004568C0` are both complete 47-instruction bodies. Their common behavior is
exact:

- buttons `0x2C` and `0x2E` enter the completion path;
- button `0x2D` records system time plus a file-backed delay at `this+0x1C`;
- completion plays frontend sound `1`;
- completion clears 100 particle/link records across `0x320` bytes at an
  eight-byte stride.

The page/result branch is edition-specific:

| Build/state | Completion action |
| --- | --- |
| Retail, playable-demo false | `SetPage(FEP_LEVELSELECT = 7, 30)` |
| Retail, playable-demo true | write `-1` to frontend quit/result global `0x008A956C` |
| Demo, playable-demo true | `SetPage(FEP_DEMOMAIN = 22, 0)` |
| Demo, playable-demo false | `SetPage(FEP_LEVELSELECT = 7, 30)` |

The participating playable-demo globals are the same cross-build state already
recovered in the FMV/startup report: retail `0x0083D448` is zero-initialized and
opt-in, while demo `0x00633B1C` is file-backed and initialized to one. The demo
therefore normally returns from debriefing to its dedicated page; retail's
playable-demo path exits through the frontend result sentinel.

This resolves the first of the original strict-vtable divergences as product
policy rather than an uncertain function boundary.

## Boundary and next use

The recovered claims are exact function extents, virtual identity, resource
names and offset, pointer dataflow, draw presence/order, page ordinals, and
completion branching. They do not establish texture pixels, blend/render
state, transition interpolation, which input device generated a button, or
runtime frame timing.

Together with the FMV/startup cluster, all four original strict-vtable
divergences now have independently recovered whole functions and bounded
semantic explanations. The remaining cross-build work should continue through
coherent changed-body clusters and the 50 still-unmapped retail entries, using
the demo as a refuter rather than revisiting the 8,021 normalized-identical
bodies.
