// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>Development-package entry. Missing explicit owned configuration fails before Companion is constructed.</summary>
public partial class CeWorkflowEntry : Node
{
    public override void _Ready() => _ = RunAfterReadyAsync();

    private async Task RunAfterReadyAsync()
    {
        SceneTree tree = GetTree();
        // A main-scene _Ready callback still belongs to Root's child setup. Let that finish before the
        // shared workflow adds Companion to Root, as the source SceneTree entry does after initialization.
        await ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        await new CeLiveWorkflow(tree).RunAsync();
    }
}
