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
/// WHAT THIS IS NOT. It is not a schedule. Since the message-box law was
/// recovered (see <c>Level100MissionTiming.MessageBoxAllowedTick</c> and
/// <c>MessageAdvanceDelayTicks</c>), Core owns the schedule outright: it holds
/// each <c>Level100MessageRequested</c> back to the tick the message actually
/// becomes active, so the delivery tick IS the start tick and the audio adapter
/// and the HUD read the same instant. This type is the lookup over that stream.
///
/// WHY THE FULL TABLE VALUE IS THE DISPLAY DURATION. It was previously
/// <c>ExpectedPlaybackTicks - 18</c>, on the reading that the shipped table is a
/// script wait carrying a post-roll (it is the Ogg granule length plus 18.03
/// ticks on all 43 catalogued messages, which is not in dispute). That reading
/// is REFUTED as a display rule. Retail activates the message BEFORE the voice
/// starts - <c>CMessageBox__TryAdvanceQueuedMessage</c> (<c>0x004b7b80</c>)
/// waits 0.2 s before entering the voice/reveal path - and RETAINS it through
/// the 0.3 s completion hold of
/// <c>CMessageBox__AdvanceRevealAndScheduleNextTick</c> (<c>0x004b8020</c>).
/// Subtracting the 18 produced a voice-only window, i.e. the old
/// <c>AudioStreamPlayer.Playing</c> behaviour under a new name. The measured
/// retail spans in <c>rebuild/PROVENANCE.md</c> equal the table entries to
/// within the 50 ms sampler, and the gaps between them are a uniform six ticks.
/// </summary>
public static class Level100MessageSchedule
{
    /// <summary>
    /// How long a delivery is on screen, in Core ticks.
    /// </summary>
    public static int DisplayTicks(Level100HudMessageDeliverySnapshot delivery)
    {
        ArgumentNullException.ThrowIfNull(delivery);
        return Math.Max(1, delivery.ExpectedPlaybackTicks);
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
        for (int index = 0; index < deliveries.Count; index++)
        {
            Level100HudMessageDeliverySnapshot delivery = deliveries[index];
            int start = delivery.Tick;
            int duration = DisplayTicks(delivery);
            if (tick >= start && tick < start + duration)
            {
                return new Level100MessageScheduleEntry(delivery, start, duration);
            }
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
