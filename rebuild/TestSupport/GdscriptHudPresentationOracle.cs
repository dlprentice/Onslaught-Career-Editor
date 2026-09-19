// SPDX-License-Identifier: GPL-3.0-or-later
using System.Text.Json;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;

// Synthetic projection facts only. These sparse WorldSnapshots must never be
// restored into simulation; all fields read by the existing HUD are set here.
// Current C# is a temporary migration oracle, not new retail evidence.
internal static class GdscriptHudPresentationOracle
{
    internal static object Build()
    {
        var scanner = new List<object>();
        var trig = new List<object>();
        var admittedAngles = new HashSet<uint>();
        void AddScanner(string name, float x, float z, float yaw)
        {
            // Independent inputs/outputs at the MathF boundary, before scanner
            // rotation, clamping or alpha can mask or amplify a one-bit change.
            if (admittedAngles.Add(Word(-yaw)))
                trig.Add(new { name, input_word = Word(-yaw),
                    expected = new { cosine_word = Word(MathF.Cos(-yaw)), sine_word = Word(MathF.Sin(-yaw)) } });
            foreach (string operation in new[] { "contact", "objective", "design" })
            {
                Level100ScannerPlacement value = operation switch
                {
                    "contact" => Level100ScannerProjection.Place(x, z, yaw),
                    "objective" => Level100ScannerProjection.PlaceObjective(x, z, yaw),
                    _ => Level100ScannerProjection.PlaceInDesignSpace(x, z, yaw),
                };
                scanner.Add(new { name = name + "/" + operation, operation,
                    words = new[] { Word(x), Word(z), Word(yaw) }, expected = Placement(value) });
            }
        }
        AddScanner("zero", 0f, 0f, 0f);
        AddScanner("signed-zero", -0f, -0f, -0f);
        AddScanner("near", 30f, 40f, .3f);
        AddScanner("far-same-bearing", 90f, 120f, .3f);
        foreach (float radius in new[] { 0f, 1f, 45.99f, 46f, 46.01f, 69f, 91.99f, 92f, 92.01f, 1000f })
            AddScanner("radial-" + Word(radius), radius / Level100ScannerProjection.PixelsPerWorldUnit, 0f, 0f);
        foreach (float distance in new[] { 110.3f, 110.4f, 110.5f, 220.79f, 220.8f, 220.81f })
            AddScanner("clamp-cull-boundary-" + Word(distance), 0f, distance, 0f);
        for (int step = 0; step < 72; step++)
        {
            float yaw = step * (MathF.Tau / 72f);
            AddScanner("forward-" + step, -MathF.Sin(yaw) * 72f, MathF.Cos(yaw) * 72f, yaw);
            AddScanner("starboard-" + step, MathF.Cos(yaw) * 72f, MathF.Sin(yaw) * 72f, yaw);
        }
        uint seed = 0x68756431;
        uint Next() => seed = unchecked(seed * 1664525u + 1013904223u);
        for (int i = 0; i < 512; i++)
            AddScanner("varied-" + i, ((int)(Next() % 600001) - 300000) / 1000f,
                ((int)(Next() % 600001) - 300000) / 1000f,
                unchecked((int)Next()) / 1000000f);
        foreach (uint word in new uint[] { 1, 0x80000001, 0x007fffff, 0x00800000, 0x7f7fffff,
                     0xff7fffff, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00000 })
        {
            float value = BitConverter.Int32BitsToSingle(unchecked((int)word));
            AddScanner("special-x-" + word, value, 1f, 0f);
            AddScanner("special-yaw-" + word, 1f, 1f, value);
        }

        var socket = new List<object>();
        foreach (bool holds in new[] { false, true })
            foreach (int influenceState in new[] { int.MinValue, -1, 0, 1, 2, 3, int.MaxValue })
                socket.Add(new { holds, influence = influenceState, expected = (int)Level100HudLowerRightSocketLaw.Select(
                    holds, (Level100HudInfluenceMapState)influenceState) });

        var schedules = new List<object>();
        void Schedule(string name, Level100HudMessageDeliverySnapshot[] deliveries, IEnumerable<int> ticks)
        {
            foreach (int tick in ticks)
            {
                var active = Level100MessageSchedule.ActiveAt(deliveries, tick);
                schedules.Add(new { name = name + "/" + tick, deliveries = deliveries.Select(Message).ToArray(), tick,
                    display = deliveries.Select(Level100MessageSchedule.DisplayTicks).ToArray(),
                    visible = deliveries.Select(Level100MessageSchedule.VisibleTicks).ToArray(),
                    active = active.HasValue ? new { delivery = Message(active.Value.Delivery),
                        start_tick = active.Value.StartTick, duration_ticks = active.Value.DurationTicks } : null,
                    holds = Level100MessageSchedule.MessageBoxHoldsActiveMessage(deliveries, tick) });
            }
        }
        foreach (int duration in new[] { int.MinValue, -1, 0, 1, 2, 3, 4, 5, 20, int.MaxValue })
        {
            var delivery = new Level100HudMessageDeliverySnapshot(10, Level100HudSpeaker.Kramer, 100, false, duration);
            Schedule("duration-" + duration, [delivery], Enumerable.Range(8, 30).Concat(
                new[] { int.MinValue, int.MaxValue, unchecked(10 + Math.Max(1, duration)) }));
        }
        Schedule("empty", [], [-1, 0, int.MaxValue]);
        Schedule("overlap-arrival-order", [Delivery(20, 2, 30), Delivery(10, 1, 50)], [9, 10, 19, 20, 46, 47, 50, 59, 60]);
        Schedule("overflow-window", [Delivery(int.MaxValue - 2, 3, 20), Delivery(int.MinValue, 4, 10)],
            [int.MinValue, int.MinValue + 7, int.MinValue + 10, int.MaxValue - 3, int.MaxValue - 2, int.MaxValue]);

        var scenarios = new List<object>();
        var empty = new Scenario("empty-and-unknown", null);
        empty.Project(Snapshot());
        empty.Project(null);
        empty.Project(Snapshot(tick: 1));
        scenarios.Add(empty.Output());

        var events = new Scenario("delivery-order-errors-and-restart", null);
        events.Consume(new Level100MessageRequested(5, 919601, 100, true, 20),
            new Level100HelpRequested(5, 1197607), new Level100HelpRequested(5, 31505972),
            new Level100HelpRequested(5, 1197607), new Level100HudEmphasisChanged(5, 4, true), null,
            new Level100MessageRequested(5, 1508464, 101, false, 30));
        events.Project(Snapshot(tick: 5));
        events.Project(Snapshot(tick: 5), new(10565784, 999, 123, .1, true, true));
        events.Consume(new Level100HelpRequested(6, 8268984), new Level100MessageRequested(6, -1, 200, false, 1),
            new Level100HelpRequested(6, 17186000));
        events.Project(Snapshot(tick: 6));
        events.Consume(new Level100MessageRequested(7, 10565784, 300, false, 0), new Level100HelpRequested(7, -1),
            new Level100MessageRequested(7, 919601, 301, false, 10));
        events.Project(Snapshot(tick: 7));
        events.ConsumeNull();
        events.Project(Snapshot(tick: 22));
        events.Project(Snapshot(tick: 2));
        events.Consume(new Level100HelpRequested(2, 488286858));
        events.Project(Snapshot(tick: 2));
        events.Consume(new Level100MessageRequested(int.MaxValue - 2, 919601, 400, false, int.MaxValue));
        events.Project(Snapshot(tick: int.MaxValue));
        events.Project(Snapshot(tick: int.MinValue));
        scenarios.Add(events.Output());

        var filtering = new Scenario("actors-filtering-order-and-last-override",
            new Dictionary<string, int>(StringComparer.Ordinal) { ["friendly"] = 0, ["enemy"] = 1, ["invalid"] = 99, ["Neutral"] = 1 });
        Level100ActorSnapshot[] actors = [
            Actor(20, "friendly", "live", -3688, 83750, objective: true),
            Actor(2, "enemy", "Player 1", -3688, 83750, objective: true),
            Actor(3, "enemy", "trigger", -3688, 83750, objective: true, trigger: true),
            Actor(4, "enemy", "inactive", 0, 0, active: false, objective: true),
            Actor(5, "enemy", "destroyed", 0, 0, lifecycle: 2, objective: true),
            Actor(6, "enemy", "dying", 0, 0, lifecycle: 1),
            Actor(7, "enemy", "awaiting", 1000, 1000, lifecycle: 3),
            Actor(8, "invalid", "invalid", 300000, 300000),
            Actor(9, "neutral", "player 1", 100, 100),
            Actor(10, "missing", "Ω 🚀", 200, -200),
        ];
        Level100ActorCommandIntentSnapshot[] commands = [Command(20, 1), Command(20, 0, false), Command(20, 2),
            Command(6, 0), Command(7, 99), Command(9, 1, false)];
        filtering.Project(Snapshot(actors: actors, commands: commands));
        filtering.Project(Snapshot(tick: 1, actors: actors.Reverse().ToArray(), commands: commands.Reverse().ToArray()));
        filtering.Project(Snapshot(tick: 2, actors: [Actor(1, "enemy", "edge", int.MaxValue, int.MaxValue)],
            player: new(int.MinValue, int.MinValue), yaw: int.MaxValue));
        filtering.Project(Snapshot(tick: 3, actors: [Actor(1, "enemy", "edge", int.MinValue, int.MinValue)],
            player: new(int.MaxValue, int.MaxValue), yaw: int.MinValue));
        scenarios.Add(filtering.Output());

        var influence = new Scenario("influence-local-ratio-neighbors-and-radius",
            new Dictionary<string, int> { ["friendly"] = 0, ["enemy"] = 1, ["neutral"] = 2 });
        foreach (var node in Level100HudInfluenceMap.Nodes)
        {
            influence.Project(Snapshot(actors: [Actor(1, "enemy", "enemy", node.Position.X, node.Position.Z)]));
            influence.Project(Snapshot(actors: [Actor(1, "friendly", "friend", node.Position.X, node.Position.Z),
                Actor(2, "enemy", "enemy", node.Position.X, node.Position.Z)]));
            foreach (int offset in new[] { 9999, 10000, 10001 })
                influence.Project(Snapshot(actors: [Actor(1, "enemy", "edge", node.Position.X + offset, node.Position.Z)]));
        }
        for (int i = 0; i < 40; i++)
        {
            var crowd = new List<Level100ActorSnapshot>();
            var overrides = new List<Level100ActorCommandIntentSnapshot>();
            for (int j = 0; j < 32; j++)
            {
                var node = Level100HudInfluenceMap.Nodes[(int)(Next() % 13)];
                crowd.Add(Actor(j + 1, Next() % 2 == 0 ? "friendly" : "enemy", "unit-" + j,
                    node.Position.X + (int)(Next() % 16001) - 8000,
                    node.Position.Z + (int)(Next() % 16001) - 8000, lifecycle: (int)(Next() % 4),
                    active: Next() % 5 != 0, trigger: Next() % 7 == 0));
                overrides.Add(Command(j + 1, (int)(Next() % 5) - 1, Next() % 3 == 0));
            }
            influence.Project(Snapshot(tick: i, actors: crowd.ToArray(), commands: overrides.ToArray()));
        }
        scenarios.Add(influence.Output());

        var scalar = new Scenario("weapons-terminal-emphasis-and-damage", null);
        foreach (int mode in new[] { 0, 1 })
            foreach (int weapon in new[] { int.MinValue, 0, 1, 2, 3, 4, 5, int.MaxValue })
                foreach (int availability in new[] { -1, 0, 1, 2, 3 })
                    scalar.Project(Snapshot(mode: mode, walker: weapon, jet: 4 - weapon, pulse: availability,
                        twin: availability, mech: 2 - availability, emphasis: weapon));
        foreach (int outcome in new[] { -1, 0, 1, 2, 3 })
            foreach (int reason in new[] { 0, 1, 2, 3, 4 })
                foreach (int ticks in new[] { -1, 0, 1, 39, 40, 100, 260, 261, 290, 300, int.MaxValue })
                    scalar.Project(Snapshot(outcome: outcome, failure: reason, terminal: ticks));
        foreach (int tick in new[] { int.MinValue, -1, 0, 40, 100, int.MaxValue })
            scalar.Project(Snapshot(tick: tick, flashes: [new(1, tick), new(2, unchecked(tick - 39)),
                new(3, unchecked(tick - 40)), new(4, unchecked(tick + 1)), new(5, int.MinValue), new(6, int.MaxValue)]));
        scalar.Consume(new Level100HelpRequested(10, 1197607));
        scalar.Project(Snapshot(tick: 10));
        scalar.Project(Snapshot(tick: 0, mode: 99));
        scalar.Project(Snapshot(tick: 0));
        scenarios.Add(scalar.Output());

        return new { scanner, trig, socket, schedules, scenarios,
            nodes = Level100HudInfluenceMap.Nodes.Select(n => new { id = n.Id, position = Vector(n.Position), radius_millimeters = n.RadiusMillimeters }),
            links = Level100HudInfluenceMap.Links.Select(l => new { first_node_id = l.FirstNodeId, second_node_id = l.SecondNodeId }),
            constants = new { scale_word = Word(Level100ScannerProjection.PixelsPerWorldUnit),
                fade_word = Word(Level100ScannerProjection.FadePerPixel), centre_x_word = Word(Level100ScannerProjection.CentreX),
                centre_y_word = Word(Level100ScannerProjection.CentreY), damage_ticks = SimulationConstants.Level100DamageFlashLifetimeTicks,
                clear_lead_ticks = Level100MessageSchedule.MessageTextClearLeadTicks, advance_ticks = Level100MissionTiming.MessageAdvanceDelayTicks },
            tints = new[] { -1, 0, 1, 2, 3 }.Select(a => new { allegiance = a, expected = Level100ScannerProjection.TintRgb((Level100HudAllegiance)a) }) };
    }

    private sealed class Scenario(string name, Dictionary<string, int>? authored)
    {
        private readonly Level100HudPresentationState _state = new(authored);
        private readonly List<object> _steps = [];
        internal void Consume(params Level100MissionEvent?[] events)
        {
            object expected;
            try { _state.Consume(events.Select(e => e!).ToArray()); expected = new { ok = true }; }
            catch (Exception error) when (error is ArgumentException or InvalidDataException)
            { expected = new { ok = false, error_type = error.GetType().Name }; }
            _steps.Add(new { operation = "consume", events = events.Select(Event).ToArray(), expected });
        }
        internal void ConsumeNull()
        {
            try { _state.Consume(null!); throw new InvalidOperationException("Null must throw."); }
            catch (ArgumentNullException error)
            { _steps.Add(new { operation = "consume", events = (object?)null, expected = new { ok = false, error_type = error.GetType().Name } }); }
        }
        internal void Project(WorldSnapshot? snapshot, Level100MessagePlaybackState playback = default)
        {
            object expected;
            try { expected = new { ok = true, value = Projection(_state.Project(snapshot!, playback)) }; }
            catch (Exception error) when (error is ArgumentException or InvalidDataException)
            { expected = new { ok = false, error_type = error.GetType().Name }; }
            _steps.Add(new { operation = "project", facts = snapshot is null ? null : Facts(snapshot),
                playback = new { active_speaker_id = playback.ActiveSpeakerId, active_message_id = playback.ActiveMessageId,
                    position_seconds = playback.PositionSeconds, length_seconds = playback.LengthSeconds, playing = playback.Playing, paused = playback.Paused }, expected });
        }
        internal object Output() => new { name, authored, steps = _steps };
    }

    private static T Blank<T>() => JsonSerializer.Deserialize<T>("{}")!;
    private static WorldSnapshot Snapshot(int tick = 0, Level100ActorSnapshot[]? actors = null,
        Level100ActorCommandIntentSnapshot[]? commands = null, SimVector2 player = default, int yaw = 0,
        int mode = 0, int walker = 1, int jet = 2, int pulse = 0, int twin = 0, int mech = 0,
        int emphasis = 0, int outcome = 0, int failure = 0, int terminal = 0, Level100DamageFlashSnapshot[]? flashes = null) =>
        Blank<WorldSnapshot>() with { Tick = tick, Mode = (VehicleMode)mode, PlayerPosition = player, FacingYawMicroRad = yaw,
            Level100WalkerSelectedWeapon = (Level100MissionWeapon)walker, Level100JetSelectedWeapon = (Level100MissionWeapon)jet,
            Level100HudEmphasisMask = emphasis, Level100DamageFlashes = flashes ?? [],
            Level100Mission = Blank<Level100MissionSnapshot>() with { Tick = tick,
                PulseCannonAvailability = (Level100MissionWeaponAvailability)pulse, TwinVulcanAvailability = (Level100MissionWeaponAvailability)twin,
                MechVulcanAvailability = (Level100MissionWeaponAvailability)mech, Outcome = (Level100MissionOutcome)outcome,
                FailureReason = (Level100MissionFailureReason)failure, TerminalTicksRemaining = terminal },
            Level100Actors = new("synthetic-hud-projection", 1, 1, actors ?? [], [], []),
            Level100ActorMechanics = new(0, commands ?? [], 0, 1, [], []) };
    private static Level100ActorSnapshot Actor(int id, string definition, string name, int x, int z,
        bool active = true, bool objective = false, int lifecycle = 0, bool trigger = false) =>
        new(new(id), definition, name, null, null, null, 0, null, null, false, active, objective,
            (Level100ActorLifecycle)lifecycle, 1, new(new(x, id, z), default, new(id, -id, id * 2), default),
            default, 0, trigger ? (Level100MissionTrigger)0 : null, false, null, false);
    private static Level100ActorCommandIntentSnapshot Command(int id, int allegiance, bool hasOverride = true) =>
        new(new(id), 0, allegiance, hasOverride, default, null, null, 0, 0, false, 0);
    private static Level100HudMessageDeliverySnapshot Delivery(int tick, int id, int duration) =>
        new(tick, Level100HudSpeaker.Kramer, id, false, duration);
    private static uint Word(float value) => unchecked((uint)BitConverter.SingleToInt32Bits(value));
    private static object Placement(Level100ScannerPlacement v) => new { offset_x_word = Word(v.OffsetX), offset_y_word = Word(v.OffsetY), alpha = v.Alpha, drawn = v.Drawn, clamped = v.Clamped };
    private static object Vector(SimVector2 v) => new { x = v.X, z = v.Z };
    private static object Vector(SimVector3 v) => new { x = v.X, y = v.Y, z = v.Z };
    private static object Message(Level100HudMessageDeliverySnapshot v) => new { tick = v.Tick, speaker = (int)v.Speaker,
        message_id = v.MessageId, script_waits_for_duration = v.ScriptWaitsForDuration, expected_playback_ticks = v.ExpectedPlaybackTicks };
    private static object? Event(Level100MissionEvent? e) => e switch
    {
        null => null,
        Level100MessageRequested m => new { kind = "message", tick = m.Tick, speaker_id = m.SpeakerId,
            message_id = m.MessageId, script_waits_for_duration = m.ScriptWaitsForDuration, expected_playback_ticks = m.ExpectedPlaybackTicks },
        Level100HelpRequested h => new { kind = "help", tick = h.Tick, help_message_id = h.HelpMessageId },
        _ => new { kind = "other" },
    };
    private static object Facts(WorldSnapshot v) => new { tick = v.Tick, player_position = Vector(v.PlayerPosition), facing_yaw_micro_rad = v.FacingYawMicroRad,
        mode = (int)v.Mode, walker_selected_weapon = (int)v.Level100WalkerSelectedWeapon, jet_selected_weapon = (int)v.Level100JetSelectedWeapon,
        hud_emphasis_mask = v.Level100HudEmphasisMask,
        mission = new { tick = v.Level100Mission.Tick, pulse_cannon_availability = (int)v.Level100Mission.PulseCannonAvailability,
            twin_vulcan_availability = (int)v.Level100Mission.TwinVulcanAvailability, mech_vulcan_availability = (int)v.Level100Mission.MechVulcanAvailability,
            outcome = (int)v.Level100Mission.Outcome, failure_reason = (int)v.Level100Mission.FailureReason, terminal_ticks_remaining = v.Level100Mission.TerminalTicksRemaining },
        actors = v.Level100Actors.Actors.Select(a => new { actor_id = a.ActorId.Value, name = a.Name, definition_identity = a.DefinitionIdentity,
            active = a.Active, is_objective = a.IsObjective, lifecycle = (int)a.Lifecycle, has_trigger = a.Trigger.HasValue,
            position = Vector(a.Pose.PositionMillimeters), velocity = Vector(a.Pose.LinearVelocityMillimetersPerTick) }),
        commanded_allegiances = v.Level100ActorMechanics.Actors.Select(a => new { actor_id = a.ActorId.Value, allegiance = a.Allegiance, has_override = a.HasAllegianceOverride }),
        damage_flashes = v.Level100DamageFlashes.Select(f => new { relative_yaw_micro_rad = f.RelativeYawMicroRad, start_tick = f.StartTick }) };
    private static object Projection(Level100HudSnapshot v) => new {
        weapon = new { selected_weapon = (int?)v.Weapon.SelectedWeapon, pulse_cannon_enabled = v.Weapon.PulseCannonEnabled,
            vulcan_cannon_enabled = v.Weapon.VulcanCannonEnabled, selection_panel_visible = v.Weapon.SelectionPanelVisible,
            selection_slot = (int?)v.Weapon.SelectionSlot, pulse_heat_permille = v.Weapon.PulseHeatPermille, vulcan_ammo = v.Weapon.VulcanAmmo,
            charge_permille = v.Weapon.ChargePermille, pulse_cannon_overheated = v.Weapon.PulseCannonOverheated },
        contacts = v.Contacts.Select(c => new { id = c.Id, position = Vector(c.Position), velocity = Vector(c.Velocity), allegiance = (int)c.Allegiance,
            size = (int)c.Size, is_objective = c.IsObjective, on_scanner = c.OnScanner }),
        objectives = v.Objectives.Select(o => new { actor_id = o.ActorId.Value, thing_name = o.ThingName, position_millimeters = Vector(o.PositionMillimeters) }),
        threats = v.Threats.Select(t => new { relative_yaw_micro_rad = t.RelativeYawMicroRad, ticks_remaining = t.TicksRemaining }),
        damage_flashes = v.DamageFlashes.Select(t => new { relative_yaw_micro_rad = t.RelativeYawMicroRad, ticks_remaining = t.TicksRemaining }),
        target = v.Target is null ? null : new { contact_id = v.Target.ContactId, hull_permille = v.Target.HullPermille,
            predicted_position = Vector(v.Target.PredictedPosition), lock_permille = v.Target.LockPermille },
        active_message = v.ActiveMessage is null ? null : Message(v.ActiveMessage), emphasized_parts = v.EmphasizedParts.Select(p => (int)p),
        delivered_messages = v.DeliveredMessages.Select(Message), active_help = v.ActiveHelp.Select(h => (int)h), delivered_help = v.DeliveredHelp.Select(h => (int)h),
        battle_line = new { has_influence_values = v.BattleLine.HasInfluenceValues, influence_permille = v.BattleLine.InfluencePermille,
            influence_map = (int)v.BattleLine.InfluenceMap },
        terminal = new { visible = v.Terminal.Visible, outcome = (int)v.Terminal.Outcome, failure_reason = (int)v.Terminal.FailureReason,
            ticks_remaining = v.Terminal.TicksRemaining } };
}
