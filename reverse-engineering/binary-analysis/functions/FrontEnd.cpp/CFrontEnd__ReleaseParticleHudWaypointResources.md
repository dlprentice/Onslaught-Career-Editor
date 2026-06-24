# CFrontEnd__ReleaseParticleHudWaypointResources

- Address: 0x004691c0
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `void __fastcall CFrontEnd__ReleaseParticleHudWaypointResources(void * frontend)`

## Purpose

Releases frontend particle, HUD handle, waypoint, mesh, and texture-level resources during cleanup.

## Notes

Wave 377 hardened the saved signature/comment/tag. Static decompile evidence shows particle-manager cleanup, HUD handle-table clearing, release of retained object references, and level-resource teardown.

This is static evidence only. Runtime cleanup ordering and concrete frontend layout remain unproven by this page.
