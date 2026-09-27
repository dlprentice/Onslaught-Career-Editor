# CFrontEnd__Process

Status: active — bounded timer execution; other frame-loop claims remain leads
Last updated: 2026-09-27
Summary: retail elapsed-time filtering, floating transition progress and its
completion comparison differ from the surviving source's integer counter.
Source File: `references/Onslaught/FrontEnd.cpp` | Binary: `BEA.exe.original.backup`

- **Address:** `0x00466ba0`

Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The rechecked timer span is `[00466cce,00466d52)`, 132 unchanged bytes,
SHA-256 `e16859e96eafa8b5d0358322b1aa078415f476d4b29c099858d5187ceb83ed66`.
Pinned source `5352a81c`, `FrontEnd.cpp:595` and `:666–676`, is a comparison
reference, not a substitute for these retail instructions.

## Retail timer and progress

The call at `00466cc9` obtains the current clock in x87 ST0. Its upstream clock
implementation and reachable clock values were not exercised here. The span
uses binary32 globals `00629b0c` (previous clock) and `00679af8` (filtered step):

1. If the previous value equals binary32 `-12345`, or that comparison is
   unordered, set the filtered step to bits `3c888889` (binary32 `1/60`).
2. Otherwise compute current minus previous. A delta greater than or equal to
   `2.0` takes the same reset. A negative delta is **not** clamped. An unordered
   delta takes the smoothing branch, not the reset branch.
3. Smoothing is `float32(delta * float32(0.1) + oldStep * float32(0.9))`, with
   intermediate x87 arithmetic. The exact constants are bits `3dcccccd` and
   `3f666666`; their real-number sum is slightly below one.
4. Store the current clock as the new binary32 previous value on every path.
   This occurs even when no page transition is active.
5. Only when receiver `+0x1f8 == -1`, form `counter + filteredStep * 50` in x87,
   store it to binary32 receiver `+0x204`, and compare the **unrounded value
   still in the register** with binary32 duration at `+0x208`.
   Below or unordered skips completion; equal or greater reaches `00466d52`.

The float store at `00466d3f` is FST, not FSTP. Under the tested nearest/extended
precision mode, a stored counter of `1.0` therefore does not imply completion.
For current clock `float32(0.02)`, previous zero, old filtered step
`float32(0.02)`, counter zero and duration one, the filtered step remains
`float32(0.02)`. Its exact product with 50 is `1 - 3/134217728`: the memory
counter rounds to one while the branch still skips completion.

Further observed consequences within the isolated span:

- Equal consecutive clock samples can retain a nonzero filtered step;
  they do not necessarily produce zero progress.
- A backwards clock sample can reduce the counter. There is no lower clamp in
  this span; reachability of such clock samples in retail remains unproven.
- A previous NaN resets the filter. A current NaN with an ordinary previous
  value propagates through smoothing; an unordered completion comparison skips.
- Stable-page calls update the clock/filter while preserving the counter and
  bypassing the completion branch.

## Source divergence and downstream dispatch

While a transition is active, the source increments `mTransitionCount` once
per call and compares it with
`mTransitionTime` for equality. Retail instead uses the filtered float step,
scale 50, and the comparison described above. A literal source port or a test
that checks the stored counter alone would miss this divergence.

Fresh static decoding after the tested span shows this completion order:
old-page slot 8 at `00466d61`; assignment of the incoming page to active at
`00466d70`; incoming-page slot 7 with the old page as its argument at
`00466d82`. Source calls those callbacks `DeActiveNotification` and
`ActiveNotification`. These callbacks and their effects were not executed by
the timer experiment. The subsequent slot-2 loop at `00466dc4` visits 24 page
entries. Earlier branches at `00466cb6` and `00466cbe` can return before clock
sampling; this note does not establish which real device states reach them.

The [render contract](CFrontEnd__Render.md) describes how the stored counter and
duration feed page-render arguments. These are separate update and render
boundaries; neither contract establishes whole-menu frame pacing.

## Executed evidence and limits

166 native x86 cases executed the unchanged 132-byte span with authored
binary32 current-clock input in ST0 and explicit memory state. Branch stubs at
`00466d52` and `00466d85` record completion/skip and return without invoking
page callbacks. The loaded ELF bytes and constants were compared with pristine.
Each case begins with FNINIT: masked exceptions, nearest rounding, extended
precision. Finite expectations use separate exact-rational rounding for each
64-significand operation and binary32 store. Exceptional cases check value
classification and branches. The harness also checks x87 stack balance, stack
and receiver preservation, unchanged duration/active fields and adjacent guards.
A syscall filter permits only read/write/exit; a denied getpid control ran in
every case. No game, window, input device or game file was opened by the ELF.

Private driver: `local-data/test-runs/re-audit-20260926/frontend-options/original_clock.py`.
Result: sibling `clock-run-723chelg/clock.json`, with exact input/output files
and driver/ELF identities. Static decoding is in
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-page-identities/body-00466ba0.txt`.

Open: the clock provider's precision and discontinuities, the actual runtime
x87 control word, full notification side effects, reconnect paths and visible
transition timing. The cheapest next falsifier is a controlled copied-runtime
trace of clock/filter/counter/control-word values across a transition and an
interrupted frame. The isolated cases are not full frontend acceptance.

## Earlier frame-loop leads

The earlier note associates the rest of this function with system/quit
processing, Event Manager update at `0044b5c0`, particles, sound, music,
controller flushing, video and the message box. Those helper identities and
complete side effects were not reverified by this timer pass. Its mention of
`CFEPOptions__GetState` is also an inherited lead, not endorsed evidence.
