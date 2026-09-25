// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Text.RegularExpressions;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;

internal static class GdscriptMissionTimingOracle
{
    internal static object Build()
    {
        var cases = new List<object>();
        void Add(Type type, string method, string native, params object[] arguments)
        {
            object expected;
            try
            {
                object? value = type.GetMethod(method, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static)!.Invoke(null, arguments);
                expected = value is float number ? new { ok = true, bits = BitConverter.SingleToUInt32Bits(number) }
                    : new { ok = true, value = value is Enum ? Convert.ToInt32(value)
                        : value is SimVector2 vector ? (object)new { x = vector.X, z = vector.Z } : value };
            }
            catch (TargetInvocationException wrapper) when (wrapper.InnerException is Exception error)
            {
                expected = new { ok = false, error_type = error.GetType().Name,
                    parameter = (error as ArgumentException)?.ParamName ?? "",
                    message = error is InvalidOperationException ? error.Message : null };
            }
            cases.Add(new { method = native, arguments = arguments.Select(value => value is float f
                ? (object)BitConverter.SingleToUInt32Bits(f) : value is Enum ? Convert.ToInt32(value) : value).ToArray(), expected });
        }
        void Timing(string method, string native, params object[] arguments) => Add(typeof(Level100MissionTiming), method, native, arguments);
        int[] integers = [int.MinValue, -1, 0, 1, 2, 3, 4, int.MaxValue];
        int[] remaining = [int.MinValue, int.MinValue + 300, -1, 0, 1, 2, 39, 40, 41, 259, 260, 261, 299, 300, 301, int.MaxValue];
        foreach (int reason in integers)
        {
            Timing("FailureTerminalTicks", "failure_terminal_ticks", (Level100MissionFailureReason)reason);
            foreach (int ticks in remaining)
            {
                Timing("FailureOverlayTicksRemaining", "failure_overlay_ticks_remaining", (Level100MissionFailureReason)reason, ticks);
                foreach (int outcome in new[] { -1, 0, 1, 2, 3 })
                {
                    Timing("GameplayPaused", "gameplay_paused", (Level100MissionOutcome)outcome, (Level100MissionFailureReason)reason, ticks);
                    Timing("GameplayPausesOnNextTick", "gameplay_pauses_on_next_tick", (Level100MissionOutcome)outcome, (Level100MissionFailureReason)reason, ticks);
                    Timing("GameplayMix", "gameplay_mix", (Level100MissionOutcome)outcome, (Level100MissionFailureReason)reason, ticks);
                }
            }
        }
        for (int ticks = 0; ticks <= 300; ticks++)
            Timing("GameplayMix", "gameplay_mix", Level100MissionOutcome.Lost, Level100MissionFailureReason.PlayerDeath, ticks);
        foreach (int trigger in integers.Append(5).Append(6))
        {
            Timing("TriggerPosition", "trigger_position", (Level100MissionTrigger)trigger);
            Timing("RequiresNotInJetMode", "requires_not_in_jet_mode", (Level100MissionTrigger)trigger);
        }
        foreach (int mode in new[] { -1, 0, 1, 2, int.MaxValue })
            foreach (int transition in new[] { -1, 0, 1, 2, 3 })
                foreach (int ticks in new[] { int.MinValue, -1, 0, 9, 10, 11, int.MaxValue })
                {
                    Timing("JetModeState", "jet_mode_state", (VehicleMode)mode, (VehicleTransition)transition, ticks);
                    foreach (uint mask in new uint[] { 0, 7, 8, 9, uint.MaxValue })
                        Add(typeof(RetailIScriptInJetMode), "Evaluate", "iscript_in_jet_mode", mask, (VehicleMode)mode, (VehicleTransition)transition, ticks);
                }
        foreach (int world in integers.Concat(new[] { 100, 740, 741, 742, 743 }))
            Add(typeof(RetailGameEndCountdown), "UsesZeroWonCountdown", "uses_zero_won_countdown", world);
        foreach (int message in Level100AudioCatalog.CharacterMessages.Select(row => row.MessageId).Concat(new[] { 8444036, int.MinValue, 0, int.MaxValue }))
            Timing("MessagePlaybackTicks", "message_playback_ticks", message);
        uint[] words = [0, 0x80000000, 1, 0x80000001, 0x3ccccccc, 0x3ccccccd, 0x3cccccce,
            0x3f800000, 0xbf800000, 0x4ccccccc, 0x4ccccccd, 0x4ccccccf,
            0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00000, 0x7f800001];
        foreach (uint word in words) Timing("PauseTicks", "pause_ticks", BitConverter.UInt32BitsToSingle(word));
        var random = new Random(0x54494d45);
        for (int i = 0; i < 512; i++)
            Timing("PauseTicks", "pause_ticks", BitConverter.UInt32BitsToSingle((uint)random.NextInt64(1L << 32)));
        for (int i = 0; i < 100; i++)
        {
            float midpoint = (i + 0.5f) / 20f;
            Timing("PauseTicks", "pause_ticks", MathF.BitDecrement(midpoint));
            Timing("PauseTicks", "pause_ticks", midpoint);
            Timing("PauseTicks", "pause_ticks", MathF.BitIncrement(midpoint));
        }
        string Native(string name) => Regex.Replace(name, "([a-z0-9])([A-Z])", "$1_$2").ToUpperInvariant();
        var constants = new Dictionary<string, object>();
        foreach (FieldInfo field in typeof(Level100MissionTiming).GetFields(BindingFlags.Public | BindingFlags.Static))
        {
            object value = field.GetValue(null)!;
            constants.Add(Native(field.Name) + (value is float ? "_BITS" : ""),
                value is float f ? BitConverter.SingleToUInt32Bits(f) : value);
        }
        constants.Add("LOST_COUNTDOWN_BITS", RetailGameEndCountdown.LostCountdownBits);
        constants.Add("WON_COUNTDOWN_BITS", RetailGameEndCountdown.WonCountdownBits);
        constants.Add("IN_JET_MODE_HANDLER_ADDRESS", RetailIScriptInJetMode.HandlerAddress);
        constants.Add("RECENTLY_GROUNDED_WALKER_ADDRESS", RetailIScriptInJetMode.RecentlyGroundedWalkerAddress);
        constants.Add("BATTLE_ENGINE_TYPE_BIT", RetailIScriptInJetMode.BattleEngineTypeBit);
        return new { constants, cases };
    }
}
