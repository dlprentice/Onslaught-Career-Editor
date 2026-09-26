// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

public enum StatusKind { Info, Success, Failure }

/// <summary>The footer: the outcome of the latest action on the left, the game folder on the right.</summary>
internal sealed class StatusLine
{
    internal StatusLine()
    {
        Root = new PanelContainer { ThemeTypeVariation = "StatusBar" };
        HBoxContainer row = Root.Add(Build.Margin(20, 8, 20, 8)).Add(Build.Row(16));
        Label = row.Add(Build.Text("Ready. Open a career or choose your game folder to begin.", "Muted", wrap: false, clip: true));
        Label.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        Game = row.Add(Build.Text("", "Faint", wrap: false));
    }

    internal PanelContainer Root { get; }
    internal Label Label { get; }
    internal Label Game { get; }
    internal StatusKind Kind { get; private set; } = StatusKind.Info;
    internal bool Failed => Kind == StatusKind.Failure;

    internal void Show(string message, bool failed = false) => Show(message, failed ? StatusKind.Failure : StatusKind.Info);

    internal void Show(string message, StatusKind kind)
    {
        Kind = kind;
        Label.Text = kind switch
        {
            StatusKind.Success => "✓  " + message,
            StatusKind.Failure => "✕  " + message,
            _ => message,
        };
        Label.TooltipText = message;
        Label.ThemeTypeVariation = kind switch
        {
            StatusKind.Success => "Good",
            StatusKind.Failure => "Bad",
            _ => "Muted",
        };
    }

    /// <summary>Runs a button's workflow to completion; an unexpected fault is reported, never swallowed.</summary>
    internal async void Track(Task workflow)
    {
        try
        {
            await workflow;
        }
        catch (Exception error)
        {
            Show("The action stopped unexpectedly and nothing further was done: " + error.Message, StatusKind.Failure);
            GD.PushError(error.ToString());
        }
    }
}
