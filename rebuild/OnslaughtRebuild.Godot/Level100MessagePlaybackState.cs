// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Read-only audio presentation state consumed by the Level 100 HUD. The audio
/// adapter remains the sole playback owner.
/// </summary>
public readonly record struct Level100MessagePlaybackState(
    int? ActiveSpeakerId,
    int? ActiveMessageId,
    double PositionSeconds,
    double LengthSeconds,
    bool Playing,
    bool Paused);
