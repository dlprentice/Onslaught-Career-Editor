# CGame__GetController

> Address: 0x004705d0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::GetController`)

## Purpose
Returns `mController[player]`.

## Signature
```c
// __thiscall, pops 0x4 (1 arg)
void* CGame::GetController(int player); // returns CCONTROLLER*
```

## Source Reference
`references/Onslaught/game.cpp:3302`:
```cpp
CCONTROLLER* CGame::GetController(int number) { return mController[number]; }
```

