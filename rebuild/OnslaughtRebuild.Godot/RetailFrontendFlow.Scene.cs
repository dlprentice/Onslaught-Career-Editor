// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

public enum RetailFrontendEditorPage
{
    ClickToStart, MainMenu, QuitConfirm, CareerName, LevelSelect,
    MissionBriefing, SelectConfiguration, Loading, Options, Debriefing,
}

public sealed partial class RetailFrontendFlow
{
    public const string ProductionScenePath = "res://Scenes/Frontend/Frontend.tscn";

    public static RetailFrontendFlow Attach(Control view) => new(view);

    public static RetailFrontendFlow InstantiateScene()
    {
        using PackedScene scene = GD.Load<PackedScene>(ProductionScenePath)
            ?? throw new InvalidDataException("The native frontend scene is unavailable.");
        Control view = scene.Instantiate<Control>();
        try { return Attach(view); }
        catch
        {
            view.Free();
            throw;
        }
    }
}
