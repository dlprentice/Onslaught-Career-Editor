# CFrontEnd__SetPage

> Address: `0x00466ae0` | Source: `references/Onslaught/FrontEnd.cpp` | Line: ~563

## Summary

Changes the active frontend page, optionally with a timed transition.

Source-parity with:

```cpp
void CFrontEnd::SetPage(EFrontEndPage page, SINT time)
```

## Signature

```c
// thiscall - ECX = CFrontEnd* this
void CFrontEnd__SetPage(void * this, int page, int time);
```

## Behavior

- If `time == 0`:
  - Calls `DeActiveNotification()` on the current page
  - Calls `TransitionNotification(from_page)` then `ActiveNotification(from_page)` on the destination page
  - Sets `mActivePage = page`
- If `time != 0`:
  - Sets up transition fields (`mTransitionFrom`, `mTransitionTo`, `mTransitionCount`, `mTransitionTime`)
  - Sets `mActivePage = FEP_TRANSITION`
  - Calls `TransitionNotification(mTransitionFrom)` on the destination page

## Notes

- This function drives the per-page virtual notification hooks used throughout the frontend (FEP) system.
- Many FEP page handlers call this directly to transition between menu pages.

