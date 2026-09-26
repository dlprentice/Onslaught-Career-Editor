# `CPCController` platform-interface semantic crosswalk

Status: active, bounded platform-interface evidence
Last updated: 2026-09-26
Evidence: MEASURED — fresh pristine instructions, RTTI and controlled original-code keyboard
experiments; the dated retail/demo comparison below is retained evidence.
Verdict: the keyboard receiver/return contract, repeated-query cache and release
table are re-grounded below. The earlier claim that all 15 targets have exact
behavior was too broad; historical source spelling, device timing and complete
runtime equivalence remain separate questions.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## September 26 keyboard recheck

The specimen above decides these findings. Pinned source commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb` provides counterparts and differences;
it is not a substitute for the retail interfaces.

RTTI identifies `0x005e48e0` as the `CPCController` vtable: its preceding locator
points to `0x00618620`, with type descriptor `0x0063df60` and a zero-offset
`CController` base. These key-query slots each take one explicit `int key` after
the ECX receiver. Their wrappers overwrite incoming ECX, but the real virtual
callers supply the controller receiver. All three pop four stack bytes.

| Slot / entry | Retail result and caller |
| --- | --- |
| 6 / `0x00514850`, `CPCController__GetKeyOnce` | Full EAX is 0 or 1 after masking the helper's AL. Mapping call `0x0042dfac` supplies one key and ECX; `0x0042dca6` compares EAX with 1. |
| 7 / `0x00514890`, `CPCController__GetKeyOn` | Full EAX is the zero-extended held byte from `0x00888c94+key`. Mapping call `0x0042dfd6` compares EAX with exactly 1 at `0x0042dfd9`. There is no nonzero-to-one normalization. |
| 8 / `0x00514870`, saved neutral name `CPCController__GetKeyState3` | Full EAX is the zero-extended release-event byte. Mapping call `0x0042dfbd` tests EAX for nonzero. Its old held-state plate description is incorrect. Exact historical method spelling is unknown. |

Thus the wrappers need an integer return and member receiver, not the former
saved `bool __stdcall` interpretation. The pinned `PCController.h:25–26` instead
declares **pad number plus key**; the retail callers and `RET 4` exclude that
extra argument. Helper `0x00513a80` defines only an eight-bit raw result in AL;
its `bool` interpretation is also too narrow. These four saved metadata
corrections are now live through the [preservation and readback gate](../ghidra/README.md#re-audit-keyboard-query-abi--september-26),
with independently restored Archive A recovery. Names and code remain unchanged.

### Remembered queries and reset lifetime

`0x00513a90` reads and clears the press byte at receiver `+0x331e4+key`.
With the normal receiver `0x00855bb0`, that is `0x00888d94+key`.
If the old byte was nonzero, it returns true and, if space remains, appends the
key to a DWORD list. If the byte was zero, it returns whether the key is already
in the active list. The controller wrapper masks the helper result to eight
bits; only the wrapper establishes a full-EAX 0/1 result.

The list begins at `0x00855424`; cursor `0x0063dc1c` initially points there.
The end pointer at `0x005e4884` is `0x008554a4`: **32 entries**, not necessarily
32 distinct keys. Re-pressing an already remembered key can append a duplicate.
When full, a press for an **uncached** key returns true once, then false on the
next query. A key already in the cache continues to return true.

Clearing keyboard arrays is a different operation. `0x00512fc0` clears all
three 256-byte arrays but leaves the list and cursor intact. A cached key can
therefore still return true after that clear, even with its press byte zero.

Two re-derived reset stores are the initializer at `0x00513123` and the common
message-pump exit at `0x0051261d`. The latter follows four pad-poll calls, for
indices 0–3. The return at `0x005125d4` bypasses both those calls and the reset:
no message was obtained, active/ready fields are nonzero, the timer-command-6
comparison sets x87 C3, and receiver `+0x32e50` is nonzero. Zero elapsed time
satisfies that comparison; an unordered comparison also does if masked
exceptions allow execution to continue. This early return produces EAX=0.

`0x00515880` calls the pump until it returns zero, supplying a true low-byte
pad-state flag on the first iteration and false thereafter. A call can therefore
reset the cursor repeatedly or exit without resetting it. **Do not implement a
universal once-per-frame cache reset from these findings.** This is a bounded
reset-site and caller investigation, not proof that arbitrary indirect writes
elsewhere are impossible.

### Release state and event production

`0x00513a80` reads receiver `+0x332e4+key` without clearing it. In
`0x00512e40`, the `WM_KEYUP` branch writes that byte to 1 at `0x00512f2c` and
clears the held byte at `0x00512f25`. `0x00512470` clears exactly the release
array. The slot-8 meaning is therefore a **nonconsuming release-event flag since
the table was cleared**, not currently-up, true-once, or necessarily released
this frame. A later keydown does not clear the release flag.

The retail table index is the scan-code byte from `lParam`, with `0x80` added
modulo 256 for its extended-key bit. Source `ltshell.cpp:1015` instead indexes
with `wParam`. Global `0x00662df4 != 0` suppresses the inspected keyboard-update
branches. With suppression clear, an installed key sink bypasses keydown's
array writes; keyup still performs its array writes. These producer branches
were inspected statically, not executed with real Windows events.

### Executed evidence and limits

Private owner: `local-data/test-runs/re-audit-20260926/controller-key-query/`.
Command: `python -B .../original_key_query.py`. The final retained
`run-dpflbd9l/key-query.json` (SHA-256
`e7afef86cdffa01284691920aa791e6c130d8b7653e73bf7773b65e70507b24b`)
records **27 cases / 135 query, clear, pump and authored setup operations**.
Its frozen driver, exact build commands, inputs, binary outputs, body pins and
ELF identity remain beside it. Nine original bodies were loaded unchanged at
their retail addresses. Integer register, stack and adjacent-memory guards
passed; snapshots include the complete list and all three arrays. A syscall
filter allowed only read/write/exit and returned EPERM for a `getpid` control.

Cases distinguish repeat queries, duplicate entries, full-cache cached and
uncached presses, raw held/release bytes 2/128/255 where supplied, release-only
clear, all-array clear and explicit cursor reset. Eleven controlled pump cases
distinguish its early and common exits, including zero/positive/negative/NaN
timer values, inactive/not-ready states, message/accelerator paths and a generic
device failure `0x80004005`. The reset-device arm `0x88760869` was not executed.
Pump dependencies were explicit substitutes for Windows message APIs, the
device status, timer values and pad polling. Query cases used authored memory;
they establish neither hardware timing nor actual player input, Windows event
delivery, full game execution or rebuild parity.

Remaining falsifier: on an admitted copied retail runtime, trace these tables,
cursor and dispatches across real keydown/repeat/keyup, focus changes and menu
transitions. The static/isolated result predicts the internal transitions;
physical device and operating-system ordering remains unmeasured.

## Dated August 11 comparison

Strict RTTI pairs the 18-slot retail table at `0x005E48E0` with the demo table
at `0x005E58E0`; their structural key is
`57fcbb3e37307db044a499ef0d1fe2b32271f0948690fb669a0857459db62240`.
The 15 uniquely PC-owned targets contain 679 retail bytes and 199 decoded
instructions. Forty-five instructions differ in 74 raw bytes between the
builds, while all 15 pairs have zero normalized differences.

The machine-readable result is
[`cpccontroller-vtable-semantics-2026-08-11.tsv`](cpccontroller-vtable-semantics-2026-08-11.tsv).
That 3,375-byte table has SHA-256
`7a7e74803b48071d874ef99de3b582997e0e40be717ce2cf10709071b29485a2`.
The broader independent comparison is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Recovered platform boundary

This table is a literal instance of the shared/platform split documented in
Lost Toys' 2002 GDC presentation. Shared `CController` owns mapping, repeat,
record/playback orchestration, and delivery to `IController`; `CPCController`
adapts PC input primitives into that interface:

- DirectInput joystick X/Y/Z axes are normalized into the shared `[-1, 1]`
  convention, with right Y using the released `32768` centre/range law;
- button once/on/release wrappers delegate to the current/old DirectInput
  button-state helpers;
- keyboard once/on wrappers delegate to the global platform object;
- record/read transfer three four-byte digital words at receiver `+0x14/+0x18/+0x1c`.
  September 26 reinspection of `0x00514720`/`0x00514760` confirms three buffer calls
  in each body; the former four-analogue-float claim described the source and was
  incorrect for retail. See the [recording boundary](../source-code/frontend/controller-system.md#input-recordingplayback-system)
  for its separate EOF and tape limitations;
- the two retail-only POV slots return `sin(angle)` and `-cos(angle)` from the
  DirectInput hundredths-of-a-degree value, or zero when the value's low 16 bits
  equal `0xFFFF` (`CMP AX,FFFF` at `0x005148c1`/`0x00514911`);
- the remaining retail-only key slot returns one byte from the platform's
  third per-key state table. The September 26 recheck above proves its release
  meaning; the historical spelling remains unknown.

The complete table also contains three inherited/shared targets—no-op device
vibration, `Flush`, and `DoMappings`—which are not duplicated in the 15-row
unique-owner result. This distinction prevents platform-neutral controller
logic from being mislabeled as PC implementation code.
