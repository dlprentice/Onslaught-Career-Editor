# CFrontEnd__GetPlayer0ControllerPort

- Address: 0x00466980
- Status: Renamed (headless batch, read-back verified)
- Source match: references/Onslaught/frontEnd.cpp:444 (int CFrontEnd::GetPlayer0ControllerPort())

## Purpose

Returns player-0 controller port, defaulting to 0 when unset.

## Notes

Retail implementation normalizes the internal -1 sentinel to 0.
