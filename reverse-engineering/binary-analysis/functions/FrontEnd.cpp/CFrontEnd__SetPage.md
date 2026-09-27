# CFrontEnd__SetPage

Status: active — complete static dispatch body rechecked; runtime callbacks remain open
Last updated: 2026-09-27
Summary: entry point for the authoritative SetPage transport/order contract; unqualified source parity is withdrawn.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Address: `0x00466ae0`. Pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

The [existing SetPage contract](../../../contracts/frontend/CFrontEnd__SetPage__00466ae0.md#september-27-complete-dispatch-body-recheck)
now owns the re-derived receiver, two stack arguments, immediate/timed callback
order, field writes and falsifiers. The function forwards the source page on
the stack; EDX holds different things at its two transition dispatches. The
immediate path rereads active-page state after callbacks, and the timed path
stores float duration, so the old blanket “source-parity” description was
unsupported. No SetPage runtime or complete frontend acceptance is claimed.
