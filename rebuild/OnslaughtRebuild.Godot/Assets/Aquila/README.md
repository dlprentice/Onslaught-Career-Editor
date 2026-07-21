# Aquila render and cockpit meshes

This directory owns the ignored local Federation Aquila inputs consumed by the
Level 100 slice. Run `npm run prepare:rebuild-assets` to materialize the exact
supported files from a user-provided retail installation. These payloads are
not tracked or packaged; `rebuild/LICENSE` covers reconstruction code only.

The three source meshes come from the released PC game's
`data/resources/meshes` directory. Stuart Gillam's pinned source independently
names `f_be1.msh`, `f_be2.msh`, and `cockpit2.msh` for the same walker, jet, and
first-person roles.

| Local materialized file | Role | SHA-256 |
| --- | --- | --- |
| `Source/m_f_be1.msh.aya` | Released walker CMSH archive | `D4C8FA752229AF4111B31EFA5FF5928C892736FAA6A807915412767F3CD3C6B2` |
| `Source/m_f_be2.msh.aya` | Released jet CMSH archive | `35AADA1313C3CBB796BA75DB071321035F7005096DA7C148A7514944F4772B4C` |
| `Source/m_cockpit2.msh.aya` | Released first-person cockpit CMSH archive | `008B9292C59A5564BA3696F65D5BD51030D3E57250BC792D9D2B7F01292CDD4A` |
| `Textures/cockpit.texture.aya` | Released 512×512 `meshtex%cockpit.tga(0)A1R5G5B5.aya` texture | `C62D0C668226F056DB7455C8A5A8FA7D55AB7621ADE1E58392D6AAAD3C00F0CC` |
| `Textures/bluegun-light.texture.aya` | Released 64×64 `meshtex%A8_bluegunlight_LIT.tga(0)A8R8G8B8.aya` texture | `85858E7809A974B74F3DB5A169E081FC9DD506558F1CA99FA47C7832D8552FC5` |
| `Textures/be-tex-a.texture.aya` | Released 512×512 `meshtex%BE_texA.tga(0)A1R5G5B5.aya` texture | `86F9F54AE97BA4E3782C65909D1D93B86566228B1132829EBB93816EB5A4705B` |
| `Textures/be-tex-b.texture.aya` | Released 1024×1024 `meshtex%BE_texB.tga(0)A1R5G5B5.aya` texture | `EA01431A4023ABD517DAF5A27066EB7EDF706100FB3991566726FB4530490B60` |
| `SoundEffects/engine-takeoff.wav` | Exact XAP record 25, `Battle Engine\N_BE_engine_takeoff` | `3698A4419C000AB982CBC92C6553AC2639272FB85930DF52A26528B232F00798` |
| `SoundEffects/engine-inflight.wav` | Exact XAP record 23, `Battle Engine\N_BE_engine_inflight` | `0E6EB03AA2C2991C0E59C3483956B1C608A79700E0DE179C855491CFF548AC04` |

Godot reads these exact AYA hierarchies directly. The bounded loader validates
archive hashes, CMSH counts, the complete parent/reference graph, virtual-frame
maps, transform streams, animation tables, geometry, and six ordered material
slots. It expands 63 walker parts into 54 surfaces, 54 jet parts into 58
surfaces, and 21 cockpit parts into 10 surfaces. No flattened Aquila or cockpit
OBJ is a runtime input.

Steam `CMeshPart::InterpolateSegmentTransform` maps a virtual frame through
`VHFM`, interpolates `HPOS`/`HORI`, and the mesh controller recursively composes
that local transform through each parent. The serialized base transform agrees
with the reviewed walker pose but is not an invariant for the animated jet or
cockpit, so each exact hierarchy is validated at its consumed frame instead.

One clean Level 100 control and two uninterrupted copies with the proven
early-flight mission change establish the walker-to-jet presentation:

- The same Transform action is rejected by the clean control with no render,
  animation, cockpit, or camera change.
- Both modified runs swap to the jet hierarchy as raw state `2 → 1` begins.
  The external `walktofly` animation advances from virtual frame 25 at 20 Hz
  and switches to looping `fly` frame 0 after 1.243 and 1.241 seconds.
- The cockpit has an independent `walktofly` range. Runtime has already
  advanced it to frame 27 on the first transition sample, shows through frame
  49, and switches to `fly` frame 0 after 1.138 and 1.141 seconds.
- The raw state commits to jet after 540 and 550 ms; that state boundary does
  not truncate either visual animation. The first-person camera pointer and
  type remain unchanged.
- Takeoff and looping in-flight effects begin at transition entry. The client
  consumes their exact decoded PCM records; exact retail spatial mixing and
  fade timing are not claimed.

The released `LegMotion` table supplies 100 usable per-leg extension poses, not
one shared movement-driven gait. Steam `CMCMech` identifies four exact five-part
chains and selects the closest frame independently for each planted-foot
distance. Core owns the four deterministic contacts and released diagonal
swing subset over the Level 100 HFLD; Godot only adapts those contacts to the
retained hierarchy.

This is bounded support for the walker pose and walker-to-jet presentation. It
does not establish exact toe-normal alignment, CMC body sway, non-heightfield
contact, damage states, jet handling, jet-to-walker presentation, cockpit FOV
animation, or the complete sound mix.
