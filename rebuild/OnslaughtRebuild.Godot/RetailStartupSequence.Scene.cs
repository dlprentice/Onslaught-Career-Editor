// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailStartupSequence
{
    public const string ProductionScenePath = "res://Scenes/Frontend/Startup.tscn";

    public static RetailStartupSequence InstantiateScene()
    {
        var bridge = new RetailStartupSequence { Name = "RetailStartupBridge" };
        bridge.Presentation = GD.Load<PackedScene>(ProductionScenePath).Instantiate<Control>();
        bridge.Presentation.Connect("completed", Callable.From(() => bridge.Completed?.Invoke()));
        bridge.AddChild(bridge.Presentation);
        return bridge;
    }
}
