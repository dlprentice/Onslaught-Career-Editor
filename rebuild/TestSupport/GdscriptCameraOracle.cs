// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.Core;

/// <summary>Exact comparisons of the committed camera value owners only.
/// No draft camera runtime, scene, viewport, clock, input or filesystem runs.</summary>
internal static class GdscriptCameraOracle
{
    internal static object Build()
    {
        uint[] words = [0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000,
            0x3f800000, 0xbf800000, 0xc0000000, 0x42b40000, 0x7f7fffff, 0xff7fffff,
            0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001, 0x7f800001, 0xff800001];
        var movie = new RetailMovieCameraZoom();
        var movieRows = new List<object>();
        void Sample(uint time, uint? fov)
        {
            uint result = Word(movie.GetZoom(Float(time), fov is uint word ? Float(word) : null));
            movieRows.Add(new { time_bits = time, fov_bits = fov, result,
                state = new { time_bits = Word(movie.LastCalcZoomTime), zoom_bits = Word(movie.LastCalcZoom),
                    old_zoom_bits = Word(movie.OldZoom) } });
        }
        // Sentinel hit, same event-frame cache, +0/-0 equality and null arms.
        Sample(0xc0000000, 0x42b40000); Sample(0, 0x42b40000); Sample(0x80000000, 0x43340000);
        Sample(0x3d4ccccd, null); Sample(0x3d4ccccd, 0); Sample(0x3dcccccd, 0x42b40001);
        foreach (uint time in words)
            foreach (uint? fov in words.Select(w => (uint?)w).Append(null))
            {
                Sample(time, fov);
                Sample(time, 0x42b40000);
            }
        var random = new Random(0x43414d);
        for (int i = 0; i < 512; i++)
        {
            uint time = i % 3 == 0 ? Word((float)(i / 20.0)) : 0x3f800000;
            uint fov = (uint)random.NextInt64(1L << 32);
            Sample(time, fov);
        }

        var viewpoints = new List<object>();
        foreach (uint far in words)
        {
            uint near = far == 0 ? 0x3dcccccd : far;
            var state = new EngineViewpointState(Float(near), Float(far));
            var operations = new List<object>();
            void Op(string name, int index = 0, EngineViewpointSlotState? value = null)
            {
                object result;
                try
                {
                    object? returned = null;
                    switch (name)
                    {
                        case "update": state.UpdateSlot(index, value!.Value); break;
                        case "select": state.SelectSlot(index); break;
                        case "get": returned = Slot(state.GetSlot(index)); break;
                        case "reset": state.Reset(); break;
                        default: throw new InvalidOperationException(name);
                    }
                    result = new { ok = true, value = returned };
                }
                catch (ArgumentOutOfRangeException error) { result = new { ok = false, error_type = error.GetType().Name }; }
                operations.Add(new { name, index, value = value is { } slot ? Slot(slot) : null, result,
                    state = State(state), hash = state.ComputeHash() });
            }
            object initial = State(state);
            string initialHash = state.ComputeHash();
            var first = new EngineViewpointSlotState("level-100.attached-pan", 7,
                new(640, 480, 0, 0, Float(0x80000000), Float(0x3f800000)));
            var second = new EngineViewpointSlotState("\uFEFFzero\0🚀\ud800\udfff", int.MinValue,
                new(int.MinValue, -1, int.MaxValue, -12, Float(far), Float(near)));
            Op("get", 0); Op("get", 1);
            Op("update", 0, first); Op("select", 0);
            Op("update", 0, second); Op("get", 0); // Current viewport still the first value.
            Op("select", 0); Op("update", 1, first); Op("select", 1);
            Op("update", 1, new("", null, null)); Op("get", 1);
            foreach (int bad in new[] { -1, 2, int.MinValue, int.MaxValue })
            {
                Op("get", bad); Op("select", bad); Op("update", bad, first);
            }
            Op("select", 1); Op("update", 0, EngineViewpointSlotState.Empty); Op("reset");
            viewpoints.Add(new { near_plane_bits = near, far_plane_bits = far, initial, initial_hash = initialHash, operations });
        }
        return new { aspect = new[] { new { multiplayer = false, bits = Word(RetailCameraLaws.AspectRatio(false)) },
            new { multiplayer = true, bits = Word(RetailCameraLaws.AspectRatio(true)) } }, movie = movieRows, viewpoints };
    }

    private static object State(EngineViewpointState state)
    {
        EngineViewpointSnapshot selected = state.SelectedSnapshot;
        return new { slot_count = state.SlotCount, slots = new[] { Slot(state.GetSlot(0)), Slot(state.GetSlot(1)) },
            selected = new { selected_slot = selected.SelectedSlot, selected_slot_state = Slot(selected.SelectedSlotState),
                current_viewport = Viewport(selected.CurrentViewport), near_plane_bits = Word(selected.NearPlane), far_plane_bits = Word(selected.FarPlane) } };
    }

    private static object Slot(EngineViewpointSlotState value) => new
    {
        camera_identity = value.CameraIdentity?.Select(c => (int)c).ToArray(),
        player_thing_identity = value.PlayerThingIdentity, viewport = Viewport(value.Viewport),
    };

    private static object? Viewport(EngineViewportValue? value) => value is { } v ? new
    {
        width = v.Width, height = v.Height, x = v.X, y = v.Y,
        min_depth_bits = Word(v.MinDepth), max_depth_bits = Word(v.MaxDepth),
    } : null;

    private static float Float(uint bits) => BitConverter.UInt32BitsToSingle(bits);
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
}
