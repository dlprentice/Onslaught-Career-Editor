# CFrontEnd__GetPlayer0ControllerPort

- Address: 0x00466980
- Status: Renamed (headless batch, read-back verified)
- Current saved signature: `int __thiscall CFrontEnd__GetPlayer0ControllerPort(void * this)`
- Source match: references/Onslaught/frontEnd.cpp:444 (int CFrontEnd::GetPlayer0ControllerPort())

## Purpose

Returns player-0 controller port, defaulting to 0 when unset.

## Notes

Wave 377 hardened the saved Ghidra signature/comment/tag. Retail implementation reads the player-0 controller port field and normalizes the internal `-1` sentinel to `0`.

This is static source/decompile parity evidence only. Runtime controller-selection behavior remains unproven by this page.
