// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>Development-package entry. Missing explicit owned configuration fails before Companion is constructed.</summary>
public partial class CeWorkflowEntry : Node
{
    public override void _Ready() => _ = new CeLiveWorkflow(GetTree()).RunAsync();
}
