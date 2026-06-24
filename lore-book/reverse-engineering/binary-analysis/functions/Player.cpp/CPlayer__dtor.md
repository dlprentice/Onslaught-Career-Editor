# CPlayer__dtor

> Addresses: `0x004d2810` (`CPlayer__scalar_deleting_dtor`), `0x004d2830` (`CPlayer__dtor_base`)
>
> Source: `references/Onslaught/Player.cpp` (`CPlayer::~CPlayer()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave470)
- **Verified vs Source:** Partial static source bridge; retail cleanup behavior is compiler/member-lifecycle evidence

## Purpose
Destroy a `CPlayer` instance and service the compiler-emitted scalar deleting destructor wrapper.

## Signature
```c
void * __thiscall CPlayer__scalar_deleting_dtor(void * this, byte flags);
void __fastcall CPlayer__dtor_base(void * this);
```

## Key Observations
- Retail base destructor at `0x004d2830` restores the `CPlayer` vtable pointer.
- It removes the active BattleEngine reader stored around `this + 0x1c`, then calls `CMonitor__Shutdown`.
- Scalar deleting destructor at `0x004d2810` calls the base destructor and frees through `CDXMemoryManager` when `flags & 1` is set.
- In Stuart source the destructor body is empty, so the observed cleanup is compiler/member/base lifecycle behavior rather than explicit `Player.cpp` source code.

## Notes
- Older notes incorrectly pointed this doc at `0x004d28c0`, which is now verified as `CPlayer__GotoFPView`.
- Wave470 saved the corrected names/signatures/comments/tags after fresh metadata, decompile, xref, instruction, and source review.
- Exact `CPlayer`/ActiveReader layout, runtime camera behavior, BEA launch, game patching, and rebuild parity remain deferred.

## Related Functions
- [CPlayer__ctor](CPlayer__ctor.md) - CPlayer constructor
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md) - Pan-camera transition
