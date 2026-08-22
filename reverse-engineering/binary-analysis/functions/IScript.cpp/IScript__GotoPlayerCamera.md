# IScript__GotoPlayerCamera

> Address: `0x00533B70`

Status: superseded identity note. Current saved name:
`IScript__Create3PointPanCamera`.
<!-- ghidra-name-drift-accepted: 0x00533B70 IScript__Create3PointPanCamera (2026-08-22) -->
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: this historical filename is retained as a link-stable correction
record, but the body and registry prove native 114 `Goto3PointPanCamera`,
not native 116 `GotoPlayerCamera`. It resolves one thing plus three point
arguments, transforms the points through the thing, builds a three-point
spline and pan camera, then installs that camera. A null thing prints the
`Create3PointPanCamera` fatal warning and returns.
Evidence: MEASURED — pristine SHA verified before complete capstone body
decode and hash, registry/string reads, whole-`.text` rel32 scan, and
image-wide imm32 census. The earlier 82-byte head-only read is superseded.

## Identity correction

The old note joined one handler immediate to the wrong descriptor one row
later. The byte-correct registration is:

- `0x005328b5`: `mov dword ptr [0x64eaa0], 0x64f3dc`, where
  `0x0064f3dc` is `"Goto3PointPanCamera\0"`;
- `0x005328d0`: `mov ebp, 0x00533b70`;
- `0x005328d5`: `mov [0x64ead0], ebp` — handler cell at name cell +`0x30`.

The actual native 116 is the separate 14-byte
`IScript__GotoPlayerCamera 0x005342b0`: it loads global player
`[0x008a9d3c]`, calls `CPlayer__GotoControlView 0x004d2a50`, and returns
`ret 0xc`. Its descriptor name cell is `0x0064eb20`, handler cell
`0x0064eb50`. The mission-native corpus therefore correctly records native
114 as `AUTHORED_UNOBSERVED` (four active sites) and native 116 as
`DORMANT_CANDIDATE` (zero sites).

## Contract (byte-exact)

Body `0x00533b70`–`0x00533ea4` inclusive through the complete `ret 0xc`,
**821 bytes / 267 instructions**, SHA-256
`e29e104c77ae937591b626fc4c75523ca91fb7e75fd9eff5f33bbfe8deaa8455`.
SEH-framed, `sub esp,0x28`, saves EBX/EBP/ESI/EDI. It has 14 direct `E8`
calls; all direct jumps stay inside the body.

## Stage law

1. Resolve args element 0 through virtual byte offset `+0x40`. Null prints
   `.data 0x0064fa9c`,
   `"FATAL ERROR: null thing passed to 'Create3PointPanCamera'"`, through
   `CConsole__Printf`, restores SEH, and returns.
2. Allocate and initialize a temporary `CSPtrSet`.
3. For args elements 1, 2, and 3, call virtual byte offset `+0x44` to obtain
   each point, transform it by the thing's matrix (or the global matrix at
   `0x0083d9c0` when the thing's high flag is clear), allocate the resulting
   three-float vector, and append it to the set.
4. Allocate and construct `CBSpline 0x00416d10` from that set with point
   count 3.
5. Resolve args element 4 through virtual byte offset `+0x34`, allocate a
   `CPanCamera`, and call `CPanCamera__ctor 0x004198d0` with the thing,
   spline, and resolved scalar.
6. Call `CGame__SetCurrentCamera 0x004705e0` on global game
   `0x008a9a98`, passing the new camera between constants 0 and 1, then
   restore SEH and return `ret 0xc`.

The source-level names of the argument-element virtuals are not proved by
this body; their value shapes and consumers above are byte-proved.

## Callers and registration census

Zero inbound rel32 sites: registry dispatch only. Exactly one image-wide
imm32 of `0x00533b70`, the handler immediate at `0x005328d1`. The registry
string `Goto3PointPanCamera` and the fatal string
`Create3PointPanCamera` independently agree with the current saved name.

## Pinned-source and rebuild status

Absent from the pinned source. No reconstruction camera owner or focused
test changed in this slice.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00533b70`–`0x00533ea4` is not
  `e29e104c…aa8455`, or the final instruction is not `ret 0xc`.
- The descriptor at `0x0064eaa0` stops naming `Goto3PointPanCamera`, or its
  +`0x30` handler cell stops resolving to `0x00533b70`.
- Any inbound rel32 appears or a second image-wide imm32 of the entry
  appears.
- The point count passed to `CBSpline__ctor` stops being 3, or the terminal
  camera handoff leaves `CGame__SetCurrentCamera 0x004705e0`.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before
  reading. Complete 267-instruction body decode, raw hash, registry window,
  exact string references, rel32 and imm32 censuses reproduced with the
  read-only PE/capstone probe for this continuation.
