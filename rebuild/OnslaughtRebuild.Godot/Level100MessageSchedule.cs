// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Which delivered Level 100 character message is on screen at a given Core
/// tick, and how far into it the tick is - computed from Core ticks alone.
///
/// WHY THIS EXISTS. The HUD used to take both of those from
/// <see cref="Level100MessagePlaybackState"/>, i.e. from
/// <c>AudioStreamPlayer.GetPlaybackPosition()</c>. That is the audio mixer's
/// WALL CLOCK. Under <c>--fixed-fps 60</c> the engine frames a capture samples
/// are reproducible and the Core tick at each of them is reproducible, but the
/// mixer position at that frame is not: the mixer advances in real time while
/// the simulation advances as fast as the host allows. The capture rig keys its
/// shots on engine frames derived from Core ticks
/// (<c>FrontendCaptureRig.FrameForOffsetMs</c>), so the message on screen at a
/// pinned offset was a race against the host's speed.
///
/// MEASURED CONSEQUENCE. Two captures of the SAME commit disagreed by
/// 21.28 % material / meanD 16.5 on the message panel and 25.15 % / 5.0 on the
/// portrait/compass region, against retail's 0.02 % cross-run floor on the same
/// frame and 0.00 % on five other regions of ours
/// (local-lab/COMPASS-GAUGE-BLEND-2026-07-26.md section 4). Both regions are
/// driven by this clock: the type-on reveal and both
/// <c>FirstFlightHud.PortraitPoseIndex</c> and
/// <c>FirstFlightHud.MessageNoisePhaseIndex</c> hash the same position.
///
/// WHAT THIS IS NOT. It is not a new schedule. It reproduces the queue
/// semantics <see cref="Level100Audio"/> already implements, in tick space
/// instead of seconds:
///
///   * messages play in the order Core requested them
///     (<c>Level100MessageRequested</c>, ordered by tick);
///   * a message requested while nothing is playing starts at its request tick;
///   * a message requested while one is playing waits, and then starts
///     <see cref="HandoffTicks"/> after the previous one ends - the same
///     <c>RetailCharacterMessageHandoffSeconds = 0.3</c> gap the audio adapter
///     applies from the voice's Finished signal;
///   * a message is on screen for its VOICE length, which is the
///     <c>ExpectedPlaybackTicks</c> Core carries on the event minus the
///     18-tick script-wait post-roll baked into that table - see
///     <see cref="VoiceWaitPostRollTicks"/>, which is measured off the shipped
///     Ogg granules rather than read out of a comment.
///
/// The one thing it deliberately does NOT do is move the reveal's zero point to
/// where retail has it. Retail starts its 0.3 s completion delay when the TEXT
/// REVEAL finishes, not when the voice ends (see the block comment on
/// <c>Level100Audio.RetailCharacterMessageHandoffSeconds</c>); that is a
/// SCHEDULE change and it needs its own evidence. Changing the clock and the
/// schedule at once would make neither verifiable.
/// </summary>
public static class Level100MessageSchedule
{
    /// <summary>
    /// The gap between one message ending and the next queued one starting, in
    /// Core ticks. <c>Level100Audio.RetailCharacterMessageHandoffSeconds</c> is
    /// 0.3 s - retail's <c>CMessageBox__AdvanceRevealAndScheduleNextTick</c>
    /// (<c>0x004b8020</c>) schedules event <c>0xbba</c> with the immediate
    /// <c>0x3e99999a = 0.30f</c>, six ticks of the released 0.05 s event clock.
    /// Expressed in seconds here so a Core tick-rate change keeps its meaning.
    /// </summary>
    public const int HandoffTicks = (3 * SimulationConstants.TicksPerSecond) / 10;

    /// <summary>
    /// <c>Level100MissionTiming.MessagePlaybackTicks</c> is a SCRIPT WAIT
    /// duration, not a voice duration: it is the shipped Ogg length plus an
    /// 18-tick post-roll. MEASURED, not taken from that file's comment - over
    /// all 43 catalogued messages that have a table entry, decoding the final
    /// Ogg page's granule position against the identification header's sample
    /// rate gives
    /// <c>ExpectedPlaybackTicks - 30 * oggSeconds = 18.03</c> (min 17.55, max
    /// 18.42, every single one rounding to 18). HUD_01 is 169 ticks against a
    /// 5.029 s stream; HUD_02 210 against 6.399 s.
    ///
    /// The HUD must subtract it. The panel and the portrait were previously on
    /// screen for exactly as long as <c>AudioStreamPlayer.Playing</c> was true,
    /// i.e. the voice length, and <see cref="Level100Audio"/> arms its handoff
    /// from the voice's Finished signal. Holding the message for the full wait
    /// duration would keep it up 0.6 s past the voice on every message and push
    /// every queued successor 0.6 s late - a SCHEDULE change smuggled into a
    /// clock change. Caught by an adversarial cross-model consult
    /// (grok-4.5, high effort) and then measured.
    ///
    /// OPEN, and not settled here: whether the shipped 18 is 18 retail ticks
    /// (0.9 s at retail's 20 Hz) rather than 18 of this reconstruction's 30 Hz
    /// ticks (0.6 s). This subtracts exactly the integer the table added, in
    /// the table's own units, so the two cancel whichever it is; a Core tick
    /// rate change must revisit both together.
    /// </summary>
    public const int VoiceWaitPostRollTicks = 18;

    /// <summary>
    /// How long a delivery is on screen: its voice length in Core ticks.
    /// </summary>
    public static int DisplayTicks(Level100HudMessageDeliverySnapshot delivery)
    {
        ArgumentNullException.ThrowIfNull(delivery);
        return Math.Max(1, delivery.ExpectedPlaybackTicks - VoiceWaitPostRollTicks);
    }

    /// <summary>
    /// The message on screen at <paramref name="tick"/>, or null in a gap.
    /// <paramref name="deliveries"/> is
    /// <c>Level100HudSnapshot.DeliveredMessages</c> in Core arrival order.
    /// </summary>
    public static Level100MessageScheduleEntry? ActiveAt(
        IReadOnlyList<Level100HudMessageDeliverySnapshot> deliveries,
        int tick)
    {
        ArgumentNullException.ThrowIfNull(deliveries);
        int previousEnd = int.MinValue;
        for (int index = 0; index < deliveries.Count; index++)
        {
            Level100HudMessageDeliverySnapshot delivery = deliveries[index];
            // A message requested at or after the previous one ended found the
            // voice idle and the handoff timer at zero, so it starts at once.
            // One requested earlier was queued and waits out the handoff.
            int start = delivery.Tick >= previousEnd
                ? delivery.Tick
                : previousEnd + HandoffTicks;
            int duration = DisplayTicks(delivery);
            int end = start + duration;
            if (tick >= start && tick < end)
            {
                return new Level100MessageScheduleEntry(delivery, start, duration);
            }
            previousEnd = end;
        }

        return null;
    }
}

/// <summary>
/// One scheduled message: which delivery, the Core tick it starts on, and how
/// many Core ticks it runs for.
/// </summary>
public readonly record struct Level100MessageScheduleEntry(
    Level100HudMessageDeliverySnapshot Delivery,
    int StartTick,
    int DurationTicks)
{
    public int ElapsedTicksAt(int tick) =>
        Math.Clamp(tick - StartTick, 0, DurationTicks);

    public double ElapsedSecondsAt(int tick) =>
        ElapsedTicksAt(tick) / (double)SimulationConstants.TicksPerSecond;

    public double DurationSeconds =>
        DurationTicks / (double)SimulationConstants.TicksPerSecond;
}
