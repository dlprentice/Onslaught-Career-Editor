// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.Core;

/// <summary>
/// Transitional differential fixture source for the production GDScript scheduler.
/// Sequences follow RetailEventSchedulerTests and RetailEventSchedulerUpdateGuardTests;
/// expected values are always obtained by executing the current C# owner. This is
/// a migration comparison, not additional evidence of retail listener behavior.
/// </summary>
public static class GdscriptEventSchedulerOracle
{
    public static object BuildFixtures()
    {
        var cases = new List<object>();
        Scenario Begin(string name, bool float24 = false)
        {
            var scenario = new Scenario(name, float24);
            cases.Add(scenario.Fixture);
            scenario.Step("init");
            return scenario;
        }

        var clock = Begin("stored_float_clock_and_ring_wrap");
        int previous = 0;
        foreach (int frame in new[] { 0, 1, 2, 3, 9, 13, 20, 21, 120, 121, 200, 20_000 })
        {
            clock.Step("advance", ("count", frame - previous));
            previous = frame;
        }

        foreach (bool pc24 in new[] { false, true })
        {
            var route = Begin($"routing_arms_{pc24}", pc24);
            foreach (float due in new[] { 0.05f, 0.051f, 0.0510001f, 0.06f, 0.1f,
                9.9f, 9.9005f, 9.95f, 1_000_000f, 1_000_001f, -0.0f })
            {
                route.Add(7, 1, due);
                route.Step("init");
            }
            route.Add(2000, 1, -1, 2);
            route.Step("advance", ("count", 1));
            route.Add(2000, 1, -1, 2);

            var immediate = Begin($"pc24_immediate_boundary_restore_{pc24}", pc24);
            immediate.Step("advance", ("count", 9));
            immediate.Step("restore");
            immediate.Add(1, 1, BitConverter.UInt32BitsToSingle(0x3f00418a));
            immediate.Step("update");
            immediate.Step("init");

            var delayed = Begin($"pc24_each_delay_operation_{pc24}", pc24);
            float boundary = BitConverter.UInt32BitsToSingle(0x3e9a1cac);
            delayed.Add(1, 1, boundary);
            delayed.Step("restore");
            delayed.Step("update", ("count", 6));
            delayed.Step("update");
            delayed.Step("init");
            delayed.Add(1, 1, boundary, relative: true);
            delayed.Step("init");
            delayed.Owned(1, 1, boundary);
            delayed.Step("add_owned", ("handle", 0));

            // Numeric failure order belongs to the comparison contract too.
            // These adversarial inputs are not claims about retail callers.
            float nan = BitConverter.UInt32BitsToSingle(0x7fc00000);
            var nonfinite = Begin($"nonfinite_acquire_and_reuse_order_{pc24}", pc24);
            nonfinite.Add(7, 1, nan);
            nonfinite.Step("slot", ("handle", 0));
            nonfinite.Step("free_count");
            nonfinite.Step("restore");
            nonfinite.Step("init");
            nonfinite.Add(42, 11, -1, data: 91);
            nonfinite.Add(99, 999, nan, data: 17, reuseHandle: 0);
            nonfinite.Step("slot", ("handle", 0));
            nonfinite.Step("update");
            nonfinite.Step("init");
            nonfinite.Add(7, 1, nan, relative: true);
            nonfinite.Step("init");
            nonfinite.Owned(71, 12, nan, 99);
            nonfinite.Step("add_owned", ("handle", 0));
            nonfinite.Step("restore");
            nonfinite.Step("init");
            nonfinite.Step("advance", ("count", 48));
            nonfinite.Add(7, 1, nan);
            nonfinite.Step("update", ("count", 153));
            nonfinite.Step("init");
            nonfinite.Add(1, 1, float.PositiveInfinity);
            nonfinite.Add(2, 1, float.NegativeInfinity);
            nonfinite.Add(3, 1, float.PositiveInfinity, relative: true);
            nonfinite.Step("update");

            var indexed = Begin($"int32_priority_and_reuse_failure_order_{pc24}", pc24);
            indexed.Add(1, 1, -1, priority: -1);
            indexed.Step("restore");
            indexed.Step("init");
            indexed.Add(2, 1, -1, priority: 3);
            indexed.Step("update", ("count", 2));
            indexed.Step("init");
            indexed.Add(3, 1, -1, priority: int.MaxValue);
            indexed.Add(4, 1, 10f, priority: int.MinValue);
            indexed.Step("restore");
            indexed.Add(5, 1, -1, reuseHandle: RetailEventScheduler.MaxEvents);
            indexed.Step("shutdown");
            indexed.Add(6, 1, nan, priority: -1, reuseHandle: RetailEventScheduler.MaxEvents);

            foreach (int initialFrames in new[] { 0, 199 })
            {
                var nested = Begin($"caught_nested_update_{pc24}_{initialFrames}", pc24);
                nested.Step("update", ("count", initialFrames));
                nested.Add(42, 11, -1, data: 91);
                nested.Step("update", ("handler", "caught_nested"));
                nested.Step("restore");
                nested.Step("update");
                nested.Step("free_count");
            }
            foreach (string handler in new[] { "snapshot_then_fail", "uncaught_nested" })
            {
                var poison = Begin($"interrupted_flush_{pc24}_{handler}", pc24);
                poison.Add(42, 11, -1, data: 91);
                poison.Step("update", ("handler", handler));
                for (int retry = 0; retry < 3; retry++)
                {
                    poison.Step("update");
                    poison.Step("flush");
                    poison.Step("snapshot");
                }
                poison.Step("init");
                poison.Add(7, 5, -1);
                poison.Step("update");
            }
        }

        var relative = Begin("relative_delayed_wrap_and_owned_rebase");
        relative.Step("update", ("count", 150));
        relative.Add(11, 1, 9.9f, relative: true);
        relative.Step("init");
        relative.Step("update");
        relative.Owned(77, 2, 0.2f);
        relative.Step("slot", ("handle", 0));
        relative.Step("add_owned", ("handle", 0));
        relative.Step("update", ("count", 4));

        var order = Begin("priority_fifo_signed_event_and_cleared_listener");
        order.Add(30, 1, 0.05f, 2);
        order.Add(20, 1, 0.05f, 1);
        order.Add(11, 1, 0.05f);
        order.Add(12, 1, 0.05f);
        order.Step("update");
        order.Step("free_count");
        order.Step("init");
        order.Add(40_000, 1, 0.05f);
        order.Step("slot", ("handle", 0));
        order.Step("update");
        order.Step("init");
        order.Add(5, 1, 0.05f);
        order.Add(6, 2, 0.05f);
        order.Step("clear_listener", ("handle", 0));
        order.Step("update");
        order.Step("free_count");

        var refusals = Begin("null_invalid_manager_and_pool_lifo");
        refusals.Add(1, 0, 0.05f);
        refusals.Step("shutdown");
        refusals.Add(1, 1, 0.05f);
        refusals.Step("init");
        refusals.Step("free_count");
        refusals.Add(1, 1, 0.05f);
        refusals.Add(2, 1, 0.05f);
        refusals.Add(3, 1, 0.05f);
        refusals.Step("free", ("handle", 1));
        refusals.Add(4, 1, 0.05f);
        // The preceding historical test deliberately freed a queued slot.
        // Its duplicate queue ownership is observable but not restorable.
        refusals.Step("restore");

        foreach (bool pc24 in new[] { false, true })
        {
            var exhausted = Begin($"pool_exhaustion_refuses_without_growth_{pc24}", pc24);
            exhausted.IncludeSnapshots = false;
            exhausted.Step("fill_pool");
            exhausted.Step("free_count");
            exhausted.Add(1, 1, 0.05f);
            exhausted.Add(7, 1, BitConverter.UInt32BitsToSingle(0x7fc00000));
        }

        var stable = Begin("overflow_order_ties_and_dead_listeners");
        foreach ((int number, float time) in new[] { (11, 12f), (12, 10f), (13, 10f), (14, 14f), (15, 11f) })
            stable.Add(number, 1, time);
        stable.Step("restore");
        stable.Step("init");
        stable.Add(1, 11, 10f);
        stable.Add(2, 12, 10f);
        stable.Add(3, 13, 10f);
        stable.Step("clear_listener", ("handle", 1));
        stable.Step("restore");
        stable.Step("update", ("count", 202));
        stable.Step("free_count");
        stable.Step("get_free");

        var strict = Begin("strict_overflow_gate_runs_after_ring");
        strict.Add(99, 1, 10f);
        strict.Step("update", ("count", 200));
        strict.Add(1, 1, 10.05f, 2);
        strict.Step("update");

        var append = Begin("overflow_captured_visit_count");
        append.Add(99, 1, 10f);
        append.Step("update", ("count", 200));
        append.Step("update", ("handler", "overflow_append"));
        append.Step("flush");
        append.Step("free_count");

        var rearm = Begin("rearm_same_handle_for_200_frames");
        rearm.Add(2000, 1, -1, 2);
        rearm.Step("update", ("count", 200), ("handler", "rearm_same"));
        rearm.Step("free_count");
        rearm.Step("init");
        rearm.Add(42, 11, -1, data: 91);
        rearm.Step("update", ("handler", "rearm_start"));
        rearm.Step("restore");
        rearm.Step("update", ("count", 5), ("handler", "rearm_start"));
        rearm.Step("slot", ("handle", 0));

        var owned = Begin("snapshot_sparse_pool_and_owned_unfiled_events");
        owned.Owned(71, 12, 0.25f, 99);
        owned.Owned(72, 13, 0.5f);
        owned.Step("free", ("handle", 1));
        owned.Step("restore");
        owned.Step("get_free");
        owned.Step("add_owned", ("handle", 0));
        owned.Step("update", ("count", 8));
        owned.Step("add_owned", ("handle", -1));

        var malformed = Begin("snapshot_refuses_cycles_overlap_and_noncanonical_slots");
        foreach (string mutation in new[] { "free_cycle", "baseline_slot", "free_range", "clock_word" })
            malformed.Step("mutate_restore", ("mutation", mutation));
        malformed.Add(1, 1, -1);
        malformed.Step("mutate_restore", ("mutation", "queued_free"));
        malformed.Step("mutate_restore", ("mutation", "queued_twice"));
        malformed.Step("shutdown");
        malformed.Step("restore");

        // Adversarial reconstruction-state comparison, not a retail runtime claim.
        var wrap = Begin("uint32_clock_and_processed_counter_wrap");
        wrap.Step("restore_counters", ("frame", uint.MaxValue), ("processed", uint.MaxValue));
        wrap.Add(1, 1, -1);
        wrap.Step("update");
        wrap.Step("restore");
        return new { schema = 1, cases };
    }

    private sealed class Scenario
    {
        private RetailEventScheduler _owner;
        private readonly List<object> _steps = [];
        private readonly List<object> _trace = [];
        public object Fixture { get; }
        public bool IncludeSnapshots { get; set; } = true;

        public Scenario(string name, bool float24)
        {
            _owner = new RetailEventScheduler(float24);
            Fixture = new { name, float24, steps = _steps };
        }

        public void Add(int number, int listener, float time, int priority = 0, int data = 0, bool relative = false, int reuseHandle = -1) =>
            Step(relative ? "add_relative" : "add", ("event_num", number), ("listener", listener),
                ("time_bits", BitConverter.SingleToUInt32Bits(time)), ("priority", priority), ("data", data), ("reuse_handle", reuseHandle));

        public void Owned(int number, int listener, float time, int data = 0) =>
            Step("prepare_owned", ("event_num", number), ("listener", listener),
                ("time_bits", BitConverter.SingleToUInt32Bits(time)), ("data", data));

        public void Step(string operation, params (string Key, object Value)[] arguments)
        {
            var input = arguments.ToDictionary(pair => pair.Key, pair => pair.Value);
            input["op"] = operation;
            _trace.Clear();
            object result = Attempt(() => Execute(input));
            _steps.Add(new { input, result, state = State(_owner), trace = _trace.ToArray(),
                snapshot = IncludeSnapshots ? Attempt(() => Snapshot(_owner.Snapshot)) : null });
        }

        private object? Execute(Dictionary<string, object> input)
        {
            int Int(string key, int fallback = 0) => input.TryGetValue(key, out object? value) ? Convert.ToInt32(value) : fallback;
            string Text(string key, string fallback = "") => input.TryGetValue(key, out object? value) ? (string)value : fallback;
            float Time() => BitConverter.UInt32BitsToSingle(Convert.ToUInt32(input["time_bits"]));
            switch (Text("op"))
            {
                case "init": _owner.Init(); return null;
                case "shutdown": _owner.Shutdown(); return null;
                case "advance": for (int i = 0; i < Int("count", 1); i++) _owner.AdvanceTime(); return null;
                case "add": return Admission(_owner.AddEvent(Int("event_num"), Int("listener"), Time(), (RetailEventPriority)Int("priority"), Int("data"), Int("reuse_handle", -1)));
                case "add_relative": return Admission(_owner.AddEventTimeFromNow(Time(), Int("event_num"), Int("listener"), (RetailEventPriority)Int("priority"), Int("data"), Int("reuse_handle", -1)));
                case "prepare_owned": return _owner.PrepareOwnedEvent(Int("event_num"), Int("listener"), Time(), Int("data"));
                case "add_owned": return Admission(_owner.AddOwnedEvent(Int("handle")));
                case "free": _owner.FreeEvent(Int("handle")); return null;
                case "clear_listener": _owner.ClearListener(Int("handle")); return null;
                case "get_free": return _owner.GetNextFreeEvent();
                case "free_count": return _owner.FreeEventCount();
                case "slot":
                    int handle = Int("handle");
                    return Slot(_owner.Snapshot.Slots.FirstOrDefault(item => item.Handle == handle) ??
                        new RetailEventSlotSnapshot(handle, handle < RetailEventScheduler.MaxEvents - 1 ? handle + 1 : -1, 0, 0, 0, 0, false));
                case "snapshot": return Snapshot(_owner.Snapshot);
                case "restore": _owner = new RetailEventScheduler(_owner.Snapshot); return null;
                case "mutate_restore":
                    var snapshot = _owner.Snapshot;
                    var changed = Text("mutation") switch
                    {
                        "free_cycle" => snapshot with { Slots = [new(0, 0, 0, 0, 0, 0, false)] },
                        "baseline_slot" => snapshot with { Slots = [new(0, 1, 0, 0, 0, 0, false)] },
                        "free_range" => snapshot with { FreeList = RetailEventScheduler.MaxEvents },
                        "clock_word" => snapshot with { TimeBits = snapshot.TimeBits ^ 1 },
                        "queued_free" => snapshot with { FreeList = 0 },
                        "queued_twice" => snapshot with { Overflow = [0] },
                        _ => throw new NotSupportedException(Text("mutation")),
                    };
                    _owner = new RetailEventScheduler(changed);
                    return null;
                case "restore_counters":
                    uint frame = Convert.ToUInt32(input["frame"]);
                    _owner = new RetailEventScheduler(_owner.Snapshot with { FrameCount = frame,
                        TimeBits = BitConverter.SingleToUInt32Bits((float)((double)frame * RetailEventScheduler.ClockTick)),
                        TotalProcessed = Convert.ToUInt32(input["processed"]) });
                    return null;
                case "fill_pool":
                    int admitted = 0;
                    long handleSum = 0;
                    for (int i = 0; i < RetailEventScheduler.MaxEvents; i++)
                    {
                        var admission = _owner.AddEvent(1, 1, 0.05f);
                        if (admission.Placement == RetailEventPlacement.ImmediateBucket) admitted++;
                        handleSum += admission.Handle;
                    }
                    return new { admitted, handle_sum = handleSum };
                case "flush": return _owner.Flush(Handler(Text("handler"))).Select(Dispatch).ToArray();
                case "update":
                    var batches = new List<object>();
                    for (int index = 0; index < Int("count", 1); index++)
                    {
                        var events = _owner.Update(Handler(Text("handler"))).Select(Dispatch).ToArray();
                        if (events.Length > 0) batches.Add(new { iteration = index, events });
                    }
                    return batches;
                default: throw new NotSupportedException(Text("op"));
            }
        }

        private Action<RetailEventScheduler, RetailEventDispatch>? Handler(string mode)
        {
            if (mode.Length == 0) return null;
            return (owner, item) =>
            {
                switch (mode)
                {
                    case "snapshot_then_fail":
                        _trace.Add(new { op = "active_snapshot", result = Attempt(() => Snapshot(owner.Snapshot)) });
                        throw new InvalidOperationException("test callback interruption");
                    case "uncaught_nested": owner.Update(); break;
                    case "caught_nested":
                        object before = State(owner);
                        int callbacks = 0;
                        object result = Attempt(() => owner.Update((_, _) => callbacks++));
                        _trace.Add(new { op = "nested_update", before, result, after = State(owner), callbacks });
                        goto case "rearm_start";
                    case "rearm_start":
                    case "rearm_same":
                        bool reuseBefore = owner.ReuseOf(item.Handle);
                        var admission = owner.AddEvent(item.EventNum, mode == "rearm_same" ? item.Listener : 999, -1,
                            mode == "rearm_same" ? item.Priority : RetailEventPriority.StartOfFrame, reuseHandle: item.Handle);
                        _trace.Add(new { op = "rearm", reuse_before = reuseBefore, admission = Admission(admission), reuse_after = owner.ReuseOf(item.Handle) });
                        break;
                    case "overflow_append":
                        if (item.EventNum != 99) break;
                        var appended = owner.AddEvent(100, 1, 20f);
                        for (int frame = 0; frame < 201; frame++) owner.AdvanceTime();
                        _trace.Add(new { op = "overflow_append", admission = Admission(appended), state = State(owner) });
                        break;
                    default: throw new NotSupportedException(mode);
                }
            };
        }
    }

    private static object Attempt(Func<object?> operation)
    {
        try { return new { ok = true, value = operation() }; }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException or IndexOutOfRangeException)
        { return new { ok = false }; }
    }

    private static object State(RetailEventScheduler owner) => new
    {
        time_bits = BitConverter.SingleToUInt32Bits(owner.Time), frame_count = owner.FrameCount,
        current_buffer = owner.CurrentBufferNum, ready_buffer = owner.ReadyToFlushBuffer,
        live_events = owner.TotalEvents, total_processed = owner.TotalEventsProcessed,
        processed_this_update = owner.EventsProcessedInLastUpdate, valid = owner.IsValid,
        free_list = owner.FreeListHead, float24 = owner.Float24Arithmetic,
    };
    private static object Snapshot(RetailEventSchedulerSnapshot value) => new
    {
        time_bits = value.TimeBits, frame_count = value.FrameCount, current_buffer = value.CurrentBufferNum,
        ready_buffer = value.ReadyToFlushBuffer, live_events = value.LiveEvents,
        total_processed = value.TotalProcessed, processed_this_update = value.ProcessedThisUpdate,
        valid = value.Valid, free_list = value.FreeList, float24 = value.Float24Arithmetic,
        slots = value.Slots.Select(Slot).ToArray(),
        lanes = value.Lanes.Select(lane => new { lane_index = lane.LaneIndex, handles = lane.Handles.ToArray() }).ToArray(),
        overflow = value.Overflow.ToArray(),
    };
    private static object Slot(RetailEventSlotSnapshot value) => new
    {
        handle = value.Handle, next_free = value.NextFree, event_num = value.EventNum,
        listener = value.Listener, data = value.Data, time_bits = value.TimeBits, reuse = value.Reuse,
    };
    private static object Admission(RetailEventAdmission value) => new
    {
        placement = (int)value.Placement, handle = value.Handle, buffer_index = value.BufferIndex,
        overflow_index = value.OverflowIndex, due_time_bits = value.DueTimeBits,
    };
    private static object Dispatch(RetailEventDispatch value) => new
    {
        handle = value.Handle, event_num = value.EventNum, listener = value.Listener,
        due_time_bits = value.DueTimeBits, priority = (int)value.Priority, from_overflow = value.FromOverflow,
    };
}
