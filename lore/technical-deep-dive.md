# Technical Deep Dive

- **Status:** live preservation record — this is the **developers' account** of
  the engine, from the post-mortem and from Jeremy Longley's cross-platform
  presentation. It is not a measurement of the shipped PC executable, and where
  it disagrees with one under
  [`reverse-engineering/`](../reverse-engineering/RE-INDEX.md), **the
  measurement wins**. One correction landed 2026-07-28 and is marked at the row
  it affects.
- **Last updated:** 2026-07-28
- **Summary:** the constraints the team worked under, their memory and resource
  systems, and the cross-platform architecture that let one codebase build for
  PC, Xbox and PS2.

### Technical Constraints

| Constraint | Impact |
|------------|--------|
| **PS2 had 32MB physical RAM (~28MB usable after executable load)** | Major limitation on battle size and map scope |
| **Island-based design** | Due to engine limitations (not story choice) |
| **Display resolution** | Default 640x480; dev machines used GeForce 3 cards. MEASURED: `CD3DApplication__Init` sets 640x480 as the default *creation* size only, `CD3DApplication__BuildDeviceList` enumerates adapter/device/mode support, and `-res W H` overrides it (minimum 640x480) — [display-settings.md](../reverse-engineering/binary-analysis/functions/display-settings.md) lines 73, 91, 95, 169, 195. SOURCE: the pinned GPL source selects 640x480 out of an enumerated mode list too (`references/Onslaught/d3dapp.cpp:420`), so it is a default there as well. GeForce 3 is from the post-mortem's dev-hardware inventory (see "Technical Stats" in [development-history.md](development-history.md)), not a stated minimum spec. |
| **PC version** | Not high priority — game was primarily for PS2/Xbox |

### Memory Management

From the post-mortem:
> "Right until the game went gold there was a constant battle to get everything to fit into memory... structures were ruthlessly compacted, data was decompressed on the fly or streamed off-disk as needed."

### Resource System

> "The process relied on an incredibly risky system of **saving objects to disk by writing the entire contents of a C++ class structure** and then manually fixing up pointers and other information when it was reloaded."

Any struct change invalidated all existing save files and required hours of rebuilding.

### Cross-Platform Architecture

From **Jeremy Longley's Presentation**: "Experiences With Battle Engine Aquila"

**Non-virtual overloaded singleton classes** for cross-platform code:

```cpp
// Cross-platform header
class CSoundManager {
    void PlaySound(CSample &s, Vector &v);
protected:
    SSoundEvent mEvents[MAX_EVENTS];
};
#if TARGET == XBOX
#include "XBOXSoundManager.h"
#elif TARGET == PS2
#include "PS2SoundManager.h"
#endif

// Platform-dependent implementation
class CXBOXSoundManager : public CSoundManager {
    void DevicePlay(SSoundEvent *e) { /* Xbox hardware */ }
};
extern CXBOXSoundManager SOUND_MANAGER;
```

### Systems with Cross-Platform Interfaces

**Engine:**
- Meshes, Textures, Renderstates, Cameras
- Particle systems, Lights, Custom/procedural stuff
- Fonts, 2D HUD/front-end

**Game:**
- Sound manager, File access
- Memory management, Timers/interrupts
- Controller support, **Collision** (notably cross-platform!)

### Platform Differences

| Aspect | Xbox | PS2 |
|--------|------|-----|
| Texture compression | 16-pixel block (DXT) | 8/4-bit palettized |
| Dynamic geometry | Better | Worse |
| Fill-rate | Slower | Faster |
| Gamma settings | Different | Different |

### TRC/TCR Gotchas

Even simple UI requirements differ between platforms:
- **PS2**: START button must resume gameplay from pause
- **Xbox**: START and A buttons must have identical functionality

### Production Advice from Lost Toys

1. **Always maintain a PC build** — even if not releasing on PC
   - Simplifies tool creation
   - Helps artists progress before complex PS2 issues resolved
   - Finds bugs (BoundsChecker, VTune work better on PC)
   - Cheaper — designers don't need $10K dev kits

2. Split cross-platform and platform-dependent tasks (they progress at different speeds)

3. Don't try to finish both versions on same day — finish the easier version first!

### Glenn Corpes - Technical Achievements

Glenn was responsible for many of BEA's most impressive visual systems:

| System | Notes |
|--------|-------|
| **Landscape/terrain system** | Alex Trowers called it "a fever dream only Glenn could unravel" |
| **Shadows and coastline rendering** | Core visual identity |
| **Impostor system** | 3D objects turning into sprites in distance for performance |
| **Red/blue battle map** | Strategic interface |

Glenn presented the terrain technology at **GDC Europe 2001**: "Procedural Landscapes"
