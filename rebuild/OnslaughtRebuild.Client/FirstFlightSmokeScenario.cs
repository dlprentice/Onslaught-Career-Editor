// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client;

public static class FirstFlightSmokeScenario
{
    public const int DurationTicks = 120;

    public static InteractiveInput GetInputForTick(int tick)
    {
        if (tick < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(tick));
        }

        if (tick < 30)
        {
            return new InteractiveInput(0, 1, true, false, false);
        }

        if (tick == 30)
        {
            return new InteractiveInput(0, 0, false, true, false);
        }

        if (tick < 45)
        {
            return InteractiveInput.Idle;
        }

        if (tick < 60)
        {
            return new InteractiveInput(1, 0, false, false, false);
        }

        if (tick == 60)
        {
            return new InteractiveInput(0, 0, true, false, true);
        }

        if (tick < 91)
        {
            return new InteractiveInput(0, 1, true, false, false);
        }

        return InteractiveInput.Idle;
    }
}
