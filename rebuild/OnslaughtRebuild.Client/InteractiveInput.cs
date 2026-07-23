// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public readonly record struct InteractiveInput(
    sbyte MoveX,
    sbyte MoveZ,
    bool FireHeld,
    bool ToggleModeHeld,
    bool ResetHeld,
    sbyte LookX = 0,
    sbyte LookY = 0,
    bool LandingJetsHeld = false)
{
    public static InteractiveInput Idle => new(0, 0, false, false, false);

    public void Validate()
    {
        new SimInput(MoveX, MoveZ, LookX: LookX, LookY: LookY).Validate();
    }
}
