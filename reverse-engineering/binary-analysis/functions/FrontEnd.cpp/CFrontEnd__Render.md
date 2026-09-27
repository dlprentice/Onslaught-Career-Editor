# CFrontEnd__Render

Status: active — retail dispatch and three frontend ABIs rechecked; bounded Options tail execution
Last updated: 2026-09-27
Summary: page render ordering and argument transport, including the Options
transition-factor exception; complete visual behavior remains unvalidated.

- **Address:** `0x00468200`

Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Body `[00468200,004684c6)`, raw SHA-256
`3a396dbbe16747094675a3ce8a8436a41ef8b3c022ba32f5261e95d9d0ed9244`.
Pinned source `5352a81c` defines `BOOL CFrontEnd::Render(BOOL forcerender)`
at `references/Onslaught/FrontEnd.cpp:1259`. The old zero-argument source
description was wrong. Retail preserves ECX in ESI, returns the status saved
from `00540f70` in EBX, and executes RET 4. Both direct callers at
`0046852f` / `0046853c` push a zero DWORD, supply ECX and test full EAX.
The complete body never reads that stack slot. Its saved prototype is now
`int __thiscall CFrontEnd__Render(void *this, int force_render)` through the
[frontend ABI cohort](../../../ghidra/README.md#re-audit-frontend-callback-abi--september-27).
The source supplies the parameter name; exact original typedef/signedness and
all helper semantics remain unproved.

The source's initial elapsed-time/forcerender test at `FrontEnd.cpp:1261–1262`
is absent in retail. Retail immediately increments frame counter `008a9aac`,
samples the clock and stores last-render time at receiver `+0xbe20`. This
establishes omission of that function-local 60 Hz gate, not an unlimited global
frame rate: callers, helpers and device pacing still need their own evidence.

## Purpose

Frontend render pass used by `CFrontEnd__Run`. The source is a map to check,
not authority for retail page IDs or frame timing.

## Key Behavior

The rechecked dispatch at `0046836f` uses page slot 4 (`RenderPreCommon`);
`0046837d`, `004683a6`, `004683e7` and `00468415` use slot 5 (`Render`).
The surviving explicit `CFEPGoodies` declarations, its installed retail table
and the common receiver array establish those identities without guessing the
missing base header's layout. The array begins at receiver `+0x214`.

Transition ratio `p` comes from float fields `+0x204 / +0x208`. Incoming
pages receive `(p, previousPage)`; outgoing pages receive `(1-p, nextPage)`.
The higher-numbered page is dispatched first. Stable active rendering passes
`(1.0f, -2)`. The second argument is therefore the **other endpoint**, despite
the source parameter name `dest`; it is not always the incoming destination.
The common page is rendered between the pre-common and ordinary page passes.

## Options transition factor

Raw RTTI table `005db8a8`, slot 5, identifies `0051f700` as Options render.
The old `CFEPOptions__Update` label and `(void *this, float transition)` stack
prototype are misleading: its first stack DWORD is float transition `t`, its
second is the other page ID. Complete body `[0051f700,0051f7db)` has SHA-256
`12d6f1309699a794d9dd19f8ce7d169e0a1fb5c916782ade5f820f8e66359e6e`.

The tail beginning at `0051f76e` passes this factor to `00452df0` on receiver
`0089da08`:

| Other page | Factor |
| --- | --- |
| 18 or 19 | Exact binary32 `1.0`, bypassing the arithmetic below |
| Other values | `(t - 0.75) * 4`, bounded to `[0,1]` by the actual x87 comparisons |

Retail page 18 is **Credits**: initializer `0046649e` installs object
`this+0x4118` at array offset `+0x25c`; constructor `0046606c` sets its table
to `005db880`, whose RTTI names `CFEPCredits`. Page 19 is **Screen Position**:
`004664b0` installs `this+0x4124` at `+0x260`; `00466076` sets `005db858`,
whose RTTI names `CFEPScreenPos`. The source declares/binds a Controller page
alongside Credits, but its numeric page-enum header is absent. Do not infer
source numeric ID 19 or replace the measured retail Screen Position identity.

The first x87 comparison treats unordered as below zero. With masked invalid
exceptions, NaNs produce positive zero on ordinary-page paths; negative
infinity produces zero and positive infinity produces one. Both special pages
still pass exact one for these inputs. This only changes the factor sent to
`00452df0`: earlier Options helpers receive the original transition value.
Calling it whole-page opacity would exceed the measured scope.

**Executed evidence:** 85 native x86 cases ran the unchanged 109-byte span
`[0051f76e,0051f7db)` with authored entry registers/stack and an intercepted
`00452df0` call. The ELF's loaded span was compared with pristine; its SHA-256
is `17c2954cfb4668c4ad3d82d68f3d1c783cff1a75cf973fdb3ea9bc8ad561a66b`.
Cases cover adjacent IDs 17/18/19/20 and -2, threshold neighbors, infinities,
quiet/signaling NaNs, callee-saved registers, RET 8 stack cleanup and x87 stack
balance. Every run starts with FNINIT (nearest extended precision, exceptions
masked); a verified syscall filter permits only read, write and exit calls,
with this harness using stdin/stdout.
No game, window or physical input ran. Earlier helpers and drawing were omitted.

Private driver: `local-data/test-runs/re-audit-20260926/frontend-options/original_fade.py`.
Result: sibling `run-5aleo33r/fade.json`, with exact input/output files and
driver/ELF hashes. Fresh static packets are in
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-page-identities/`.

The saved listing's split instruction at `[0051f7be,0051f7c6)` was corrected
through the [Options instruction promotion](../../../ghidra/README.md#re-audit-options-instruction-repair--september-27).
The original bytes were always intact. The subsequent
[frontend identity cohort](../../../ghidra/README.md#re-audit-frontend-page-identities--september-27)
corrected the Options name to `CFEPOptions__Render`. The subsequent three-row
ABI cohort replaces its old stdcall interpretation with an implicit ECX receiver,
`float transition` at stack `+4` and `int other_page` at `+8`. Intro notification
at `0051be70` also gains its unused source-page DWORD, consumed by RET 4.
No missing page-enum or class definition is synthesized.

## Remaining limits

The native cases establish this tail's argument transformation, not rendered
appearance, sound, whole-menu state or real frame pacing. The
[Process timer note](CFrontEnd__Process.md) separately records 166 original-code
cases for the clock filter and completion comparison. The upstream clock,
exceptional x87 modes and every drawing helper still need their own evidence. Cheapest visual falsifier: a controlled copied-retail
transition involving Options and each of Credits, Screen Position and an
ordinary page, compared at matched transition ratios.

## Call Relationship

- Called from `CFrontEnd__Run` (`0x004684d0`) in the transition wait loop.
- Works alongside `CFrontEnd__Process` (`0x00466ba0`) to form the frontend frame loop.
