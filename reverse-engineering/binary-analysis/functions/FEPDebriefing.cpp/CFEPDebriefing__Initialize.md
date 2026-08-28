# CFEPDebriefing__Initialize

> Address: `0x00456780` | Pristine PC `BEA.exe.original.backup`
> Exact body: `0x00456780..0x0045682F` (176 bytes, 52 instructions)
> Body SHA-256: `249e35617340b38cccb3944b278be54cea5db67a308129ef2ec56753cc922b44`
> Source path embedded by retail: `FEPDebriefing.cpp`; that file is absent from the pinned Stuart drop

## Status

- **Named in Ghidra:** yes; vtable data reference at `0x005DB9C0`
- **Specimen:** pristine PC `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- **Evidence grade:** reproduced static body; no source-body or runtime equivalence claim

## Signature

```c
int __fastcall CFEPDebriefing__Initialize(void *this);
```

The receiver is in `ECX` and the body returns with a plain `RET`. With no stack
arguments, one-argument MSVC fastcall and thiscall spellings are ABI-equivalent;
the saved declaration is retained rather than claiming unavailable source syntax.

## Exact behavior

1. Allocates `0x324` bytes at 128-byte alignment. The leading dword is set to
   `100`; the returned array begins four bytes later.
2. Constructs exactly 100 eight-byte global-list/particle-link elements with
   `eh_vector_constructor_iterator`, storing the array at `this+0x20`.
3. Allocates a second `0x640`-byte block at 128-byte alignment and stores it at
   `this+0x24`.
4. Clears `this+0x1C`, `this+0x10`, and `this+0x18`.
5. Returns `1`. Allocation failures are not converted into a false return; the
   first array pointer may be null and the second allocator result is stored as
   returned.

The only direct callees are the memory manager (twice) and the vector-constructor
iterator. This body does **not** read `END_LEVEL_DATA`, call Career, calculate a
grade, inspect kills or goodies, draw UI, or play sound.

## Work owned by sibling functions

- `CFEPDebriefing__Render` (`0x00456DD0`) reads final state, objective statuses,
  world number, and ranking; it draws the mission/objective summary and the
  victory-only grade. It does not read `mThingsKilled`.
- `CFEPDebriefing__TransitionNotification` (`0x00457CF0`) consumes the two
  goodie latches and initializes transition timing.
- `CFEPDebriefing__Process` (`0x00456930`) owns transient goodie effects and the
  first-goodie message path.
- `CFEPDebriefing__ButtonPressed` (`0x004568A0`) owns page exit, sound `1`, and
  clearing the 100 link handles.
- `CCareer::Update` runs before debrief page notification
  (`FrontEnd.cpp:49-67`). It owns career progression and kill accumulation;
  world 100 is explicitly excluded from kill accumulation.

## Evidence and remaining falsifier

Primary read-back:
`local-lab/ghidra-fullpass-2026-07-23/exports/W004/decompile/00456780_CFEPDebriefing__Initialize.c`
(decompile SHA-256
`898b0bc6e120ac24fc656bb2fdd01a9521cacecc144768f220782f4f4222bad0`).
The exact raw body was independently re-extracted from the pristine PE before
promotion of this correction.

The cheapest runtime falsifier is an isolated copied-runtime call with allocator
success and failure arms, followed by reads of `this+0x10/+0x18/+0x1C/+0x20/+0x24`
and all 100 constructed link elements. Runtime allocation/list side effects and
exception behavior remain open until that probe exists.
