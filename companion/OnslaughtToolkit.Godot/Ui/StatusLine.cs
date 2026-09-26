// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>The footer that reports the outcome of the latest action.</summary>
internal sealed class StatusLine
{
    internal StatusLine()
    {
        Root = new PanelContainer();
        Label = Root.Add(Build.Text("Ready. Open a career to begin."));
    }

    internal PanelContainer Root { get; }
    internal Label Label { get; }
    internal bool Failed { get; private set; }

    internal void Show(string message, bool failed = false)
    {
        Label.Text = message;
        Failed = failed;
        Label.Modulate = failed ? CompanionTheme.Failure : Colors.White;
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
            Show("The action stopped unexpectedly and nothing further was done: " + error.Message, failed: true);
            GD.PushError(error.ToString());
        }
    }
}
