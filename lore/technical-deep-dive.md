# Technical Deep Dive

### Technical Constraints

| Constraint | Impact |
|------------|--------|
| **PS2 had 32MB physical RAM (~28MB usable after executable load)** | Major limitation on battle size and map scope |
| **Island-based design** | Due to engine limitations (not story choice) |
| **Display resolution** | Hardcoded to 640x480, assumed GeForce 3 card |
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
