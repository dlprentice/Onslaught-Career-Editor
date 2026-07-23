// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public static class FirstFlightSmokeScenario
{
    // Begin after each objective is active, then follow the bounded left/forward
    // routes used by the copied-retail observer. Each forward hold stops at
    // Core's trigger. The final fixed yaw and four-shot sequence exercises the
    // bounded full-hit lifecycle demonstrated against retail Target Tank 1.
    // Exact first-run LevelScript waits assign Target Zone 1 at tick 1005;
    // this tape begins its observed route 57 ticks later.
    public const int TargetZoneInputStartTick = 1_062;
    private const int LeftTicks = 216;
    private const int ForwardTicks = 469;
    private const int FiringRangeInputStartTick = 1_995;
    private const int FiringRangeLeftTicks = 45;
    private const int FiringRangeForwardTicks = 459;
    private static readonly int[] PulseCannonProofTicks = [3_156, 3_164, 3_172, 3_184];
    public const int DurationTicks = 3_228;

    public static InteractiveInput GetInputForTick(int tick)
    {
        if (tick < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(tick));
        }

        if (tick < TargetZoneInputStartTick)
        {
            return InteractiveInput.Idle;
        }

        int routeTick = tick - TargetZoneInputStartTick;
        if (routeTick < LeftTicks)
        {
            return new InteractiveInput(-1, 0, false, false, false);
        }

        if (routeTick < LeftTicks + ForwardTicks)
        {
            return new InteractiveInput(0, 1, false, false, false);
        }

        if (tick >= FiringRangeInputStartTick &&
            tick < FiringRangeInputStartTick + FiringRangeLeftTicks)
        {
            return new InteractiveInput(-1, 0, false, false, false);
        }

        if (tick >= FiringRangeInputStartTick + FiringRangeLeftTicks &&
            tick < FiringRangeInputStartTick + FiringRangeLeftTicks + FiringRangeForwardTicks)
        {
            return new InteractiveInput(0, 1, false, false, false);
        }

        sbyte firingRangeLook = tick switch
        {
            >= 3_139 and <= 3_145 => -1,
            3_149 or 3_155 or 3_183 => 1,
            3_180 => -1,
            _ => 0,
        };
        if (firingRangeLook != 0)
        {
            return new InteractiveInput(0, 0, false, false, false, firingRangeLook);
        }

        if (Array.BinarySearch(PulseCannonProofTicks, tick) >= 0)
        {
            return new InteractiveInput(0, 0, true, false, false);
        }

        return InteractiveInput.Idle;
    }
}
