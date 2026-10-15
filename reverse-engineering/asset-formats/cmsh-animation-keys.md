# CMSH animation keys: how a part's transform is evaluated

Status: active format contract — key convention, frame selection, interpolation and mode timing for PC meshes
Date: 2026-10-16
Last updated: 2026-10-16 (the skeletal path reads `last`; the companion's glTF export checked pose by pose)
Verdict: a part's keys (`HORI`, `HPOS`, chosen through `VHFM`) are relative to its parent. Composing them from the
root with column vectors (`position = Pp + Op·p`, `orientation = Op·O`) reproduces every cached model-space frame
in the installed corpus: 143,871 `CPOS` positions and 141,044 `CORI` orientations, all within single-precision
rounding (worst relative error 1.35e-6). Frames are selected by a mode's phase, scaled and offset into the
part's virtual frames, and interpolated linearly element by element. Phases advance by the mode's rate once
per 20 Hz game tick.
Evidence: SOURCE + MEASURED. The evaluation follows the retail functions as byte-matched in the private
decompilation, cited by name and address below. The composition was checked over the whole corpus with
`python tools/cmsh_grammar_walk.py --compose --game GAME_FOLDER`.
Specimen: retail addresses cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; the corpus is the installed
`data/resources/meshes/*.aya`, 213 files, manifest digest
`27ada81470ff8919cb832f63e78e24ac6d33625b26be54247b70b05a76690ae1` (as in [cmsh-fields.md](cmsh-fields.md)).

The stored lanes and their byte layout are in [cmsh-fields.md](cmsh-fields.md). Which meshes and scripts use
which tracks is in [cmsh-animation-usage.md](cmsh-animation-usage.md). How skinned vertices follow their bones
is in [cmsh-matrix-palette-skinning.md](cmsh-matrix-palette-skinning.md) and
[cmsh-matrix-normal-deformation.md](cmsh-matrix-normal-deformation.md). This document covers the step between
them: given a part and a moment of an animation, which transform the game uses.

## Vectors, matrices and the key convention

A stored orientation is three rows of four floats; the fourth float of each row is padding. The game applies a
matrix to a vector one row at a time: the result's `x` is row 0 dotted with the vector, and likewise for `y`
and `z`. Matrices multiply in the ordinary way. In column-vector terms, the stored rows *are* the matrix:
`v' = M v`.

Each part has `hframe_count` keys: an orientation (`HORI`) and a position (`HPOS`). Both are **relative to
the part's parent**, the part named by `PRNT`. A part's model-space transform at a virtual frame is built from
the root down:

- at the root (a part with no `PRNT`), the parent transform is the identity and the origin;
- for each part, with the parent's model-space orientation `Op` and position `Pp`, and the part's key `O`, `p`
  for that frame:
  - `position = Pp + Op · p`
  - `orientation = Op · O`

Every frame of every part's `CPOS`/`CORI` cache equals this composition (the counts are in the verdict). The
caches are the game's precomputed model-space frames: `CMeshPart::BuildCache`, `0x004b1a40`, composes
through `CMeshPart::GetWorldTransforms`, `0x004b0fb0`. An exporter can use either the keys or the caches; the
keys are the authored data.

A cache holds one frame per virtual frame, or a single frame when neither the part nor any ancestor has more
than one key. A part whose only key is the identity orientation, or the origin position, stores no
orientation or position cache and borrows its nearest ancestor's (`mPositionStatic`/`mOrientationStatic`
at part `+0x11C`/`+0x120`). That is why 38 parts have no `CPOS` and 1,263 no `CORI`: every one of them carries
the static flag. The cache-length rule holds for all 4,009 installed parts.

Every stored key orientation is orthonormal, but **920 of the 59,327 keys are reflections** (determinant −1).
A format that wants a rotation and a scale needs a negative scale on one axis for those keys.

The older mesh format stored keys in model space. Its loader converted them to parent-relative form
(`CMeshPart::HierarchyAdjust`, `0x004b0800`). The chunked PC files store the converted, parent-relative
keys.

## From a virtual frame to a key

A part has `vframe_count` virtual frames. Its `VHFM` byte map gives the key index for each one, so many
virtual frames can hold the same key. To evaluate frame `f` with fraction `t` (`0 ≤ t < 1`), the renderer
(`CMeshPart::EvaluateAnimatedTransform`, `0x004b5330`) does the following:

1. Clamp `f` to `vframe_count − 1`.
2. Take the next frame `f + 1`. If it passes the last virtual frame, it wraps to 0 when the thing's motion
   controller allows looping (the default), otherwise it stays on the last frame.
3. Map both frames through `VHFM` to keys `k0` and `k1`.
4. Interpolate linearly, **element by element**:
   - `p = p[k0] + (p[k1] − p[k0]) · t`
   - `O = O[k0] + (O[k1] − O[k0]) · t`

The bones of a **skeletal part** are sampled by the skinned draw in `CMeshRenderer::RenderMeshCore`, `0x00549570`,
with two differences:
- the frame is taken modulo `vframe_count` rather than clamped;
- the next frame wraps to the mode's `start` once it passes the mode's `last`, rather than wrapping to 0 or
  holding.

That draw also builds each bone's palette entry from the bone at frame 0 and at the current frame, both relative
to the skeletal part's own current transform (see
[cmsh-matrix-normal-deformation.md](cmsh-matrix-normal-deformation.md)). Every installed skeletal part and its
ancestors hold one key, so the part's own transform never changes.

The interpolated matrix is not re-orthonormalised: between two different rotations it is slightly shorter than
a rotation. This is the game's behaviour.

Other callers use `CMeshPart::GetTransforms`, `0x004b0d00`. It interpolates between two given frames in the
same element-by-element way, after clamping both. Callers that need a frame number from a time use
`CMeshPart::ResolveFrameNumber`, `0x004b24d0`, which wraps the frame modulo `vframe_count` instead of
clamping it.

## From time to a virtual frame

An animation mode is a record in the mesh's `CAMD` table:

| Field | Meaning |
| --- | --- |
| name | 16 characters, for example `Walk`, `idle`, `dead_back` |
| mode id | 1–10 are the engine's shared modes; 1000 and above are the mesh's own, chosen by name |
| start | the first virtual frame |
| last | `start + frame_scaler` (337 modes) or `start + frame_scaler − 1` (86 modes) |
| frame_scaler | the number of virtual frames the mode spans |
| rate | how much of the mode plays per game tick |

The engine's shared ids are walk (1), run (2), stand (3), shoot (4), shoot1 (5), shoot2 (6), shootwalk (7),
fly (8), hover (9) and idle (10). The 423 installed modes are 86 shared and 337 mesh-specific, in 61 files.

A thing playing a mode keeps a **phase** from 0 to 1 (`CAnimation::Process`, `0x00404790`):

- **Each tick.** Every game tick (20 per second; one tick is 0.05 s) the phase grows by the mode's rate.
- **Looping modes.** The shared modes walk to idle (ids 1–10) loop: the phase drops back by 1.
- **Other modes.** They stop at 1, and once the thing reports the animation finished, it returns to stand.
- **Zero rate.** A mode chosen with a rate of 0, or any rate up to 0.0001, plays at a rate of 1 instead
  (`CAnimation::SetAnimMode`, `0x00404860`). 143 installed modes store 0.
- **Drawing between ticks.** The phase is interpolated between the last two ticks by the render fraction
  (`CAnimation::GetRenderFrame`, `0x004048c0`), unless it just wrapped.

To draw, the phase becomes a virtual frame:

`frame = phase · frame_scaler + start`, then `f = floor(frame)` and `t = frame − floor(frame)`.

A motion controller attached to the thing may adjust that frame first. A mode lasts `1 / (20 · rate)`
seconds, so a mode whose rate is `1 / frame_scaler` (224 of the 423) shows one virtual frame per tick:
20 frames per second.

The same frame number, floored and taken modulo `vframe_count`, picks each texture lane value
([cmsh-fields.md](cmsh-fields.md#texture-record-cmst-entries-36-bytes-and-texture-lanes-texb)). A part drawn
without an animation uses virtual frame 0.

## Camera field of view

A camera part's `HFOV` holds one field of view per key, chosen through `VHFM` like its other keys. The
cutscene path reads it. The details are in [cmsh-animation-usage.md](cmsh-animation-usage.md#camera-lane).

## Outside the file

These change what is drawn at run time but are not stored in the mesh, so an exporter reproduces the
authored animation without them:

- **Motion controllers.** A thing's motion controller can adjust the frame, replace or offset a part's
  transform (`GetPartTransform`) and swap in damaged parts. Examples are walkers' legs and turrets aiming.
- **Hierarchy opt-out.** A thing can ask for a part's key to be used directly rather than composed with its
  parent (`RenderUseHierarchy`).
- **Cached transforms.** When no motion controller is involved, the game draws a part from its cache
  instead of composing its keys. That gives the same result to within rounding, as checked above.

## Mapping to glTF (guidance)

This mapping is not part of the format. It is how the companion's exporter (`companion/OnslaughtToolkit.Godot/Assets/GltfExport.cs`)
reproduces the game. Evaluated by the glTF rules from the exported files, every node of every exported
animation at every sample matches the composition above: 158 animations and 124,822 node poses, with a worst
error of 5e-7.

- **Nodes.** One node per part, parented as `PRNT` says. A node's rest transform is its key at virtual
  frame 0.
- **Animations.** One animation per mode. Sample each virtual frame from `start` to
  `start + frame_scaler`, at time `(frame − start) / frame_scaler × duration`:
  - translation: the key position;
  - rotation: the key orientation's quaternion;
  - for reflected keys, a scale of −1 on one axis, with the rotation taken from the corrected matrix.

  The game interpolates matrices element by element, while glTF interpolates quaternions spherically, so
  between samples the two differ slightly. They agree exactly at every sample.
- **Skins.** One skin per skeletal part. The joints are the parts in its `BONE` list. Each inverse bind matrix
  is the inverse of that bone's model-space transform at virtual frame 0, the game's bind pose (see
  [cmsh-matrix-normal-deformation.md](cmsh-matrix-normal-deformation.md)). The vertex weights follow
  [cmsh-matrix-palette-skinning.md](cmsh-matrix-palette-skinning.md).
- **Cameras.** Camera parts can become glTF perspective cameras, with the field of view from `HFOV`.
  The stored values (90 in 13 of the 17 cameras) read as degrees. Whether they are horizontal or vertical
  is open, and glTF wants a vertical angle in radians.

## Open questions

- **`last`.** Why `last` is `start + frame_scaler` in some modes and one less in others. Only the skeletal
  draw reads it (above), as the wrap point of the next frame. Falsifier: an installed skeletal mode whose
  interpolation across its last frame visibly depends on the difference.
- **Scripted speed.** Scripted `PlayAnimation` calls may set a speed other than the mode's rate. Falsifier:
  the script command's handler.
- **Reflected keys.** Whether the 920 reflected keys are deliberate mirroring or an authoring artefact. Their
  effect is visible either way, because the game draws them as stored.
