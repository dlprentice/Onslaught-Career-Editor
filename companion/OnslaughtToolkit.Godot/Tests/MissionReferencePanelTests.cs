using System;
using System.Collections.Generic;
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

internal static class MissionReferencePanelTests
{
    internal static void Run(Checks check)
    {
        var summaries = new[]
        {
            new ScriptSummary("same", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>()),
            new ScriptSummary("same", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>()),
            new ScriptSummary("long\n" + new string('x', 120), Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>())
        };
        var rows = new IReadOnlyList<ScriptReference>[]
        {
            new[] { new ScriptReference("unit", "present", true), new ScriptReference("path", "unknown", false) },
            Array.Empty<ScriptReference>(),
            new[] { new ScriptReference("unit", "other", false) }
        };
        var first = MissionReferenceIndex.FromSummaries(summaries, i => rows[i], 3, 3);
        var empty = MissionReferenceIndex.FromSummaries(Array.Empty<ScriptSummary>(), _ => throw new Exception(), 0, 0);
        var panel = new MissionReferencePanel();
        try
        {
            int scriptEvents = 0, referenceEvents = 0, lastScript = -1, lastReference = -1;
            MissionReferenceIndex? eventSnapshot = null;
            panel.ScriptSelected += (which, script) => { scriptEvents++; eventSnapshot = which; lastScript = script; };
            panel.ReferenceSelected += (which, script, reference) => { referenceEvents++; eventSnapshot = which; lastScript = script; lastReference = reference; };
            check.That(panel.Snapshot == null && panel.ScriptItems.GetItemCount() == 0 && panel.ReferenceItems.GetItemCount() == 0,
                "mission reference panel starts without a mission");
            panel.SetSnapshot(first);
            check.That(panel.ExplanationsWrap, "mission reference panel wraps its explanatory text");
            check.That(panel.ScriptItems.GetItemCount() == 3 && panel.ReferenceItems.GetItemCount() == 0
                && panel.SelectedScriptIndex == null && scriptEvents == 0, "mission reference panel shows scripts without choosing one");
            check.That(panel.ScriptItems.GetItemText(0) != panel.ScriptItems.GetItemText(1),
                "mission reference panel distinguishes duplicate script names");
            string bounded = panel.ScriptItems.GetItemText(2);
            check.That(!bounded.Contains('\n') && bounded.Length <= 110 && bounded.EndsWith("...", StringComparison.Ordinal),
                "mission reference panel keeps long control characters out of labels");
            check.That(panel.OverviewText.Contains("2 reference occurrences not resolved", StringComparison.Ordinal),
                "mission reference panel reports unresolved occurrences honestly");
            panel.ScriptItems.EmitSignal(ItemList.SignalName.ItemSelected, 0L);
            check.That(panel.SelectedScriptIndex == 0 && scriptEvents == 1 && lastScript == 0 && ReferenceEquals(eventSnapshot, first),
                "mission reference panel sends the selected snapshot and script");
            check.That(panel.ReferenceItems.GetItemCount() == 2
                && panel.ReferenceItems.GetItemText(0).StartsWith("Resolved:", StringComparison.Ordinal)
                && panel.ReferenceItems.GetItemText(1).StartsWith("Not resolved:", StringComparison.Ordinal),
                "mission reference panel displays both reference states");
            panel.ReferenceItems.EmitSignal(ItemList.SignalName.ItemSelected, 1L);
            check.That(referenceEvents == 1 && lastScript == 0 && lastReference == 1 && ReferenceEquals(eventSnapshot, first),
                "mission reference panel sends the selected reference in its snapshot");
            panel.ScriptItems.EmitSignal(ItemList.SignalName.ItemSelected, long.MaxValue);
            panel.ReferenceItems.EmitSignal(ItemList.SignalName.ItemSelected, -1L);
            check.That(!panel.TrySelectScript(-1) && !panel.TrySelectScript(int.MaxValue)
                && !panel.TrySelectReference(-1) && !panel.TrySelectReference(int.MaxValue)
                && panel.SelectedScriptIndex == 0 && scriptEvents == 1 && referenceEvents == 1,
                "mission reference panel rejects invalid selections without changing state");
            check.That(panel.TrySelectScript(1) && panel.ReferenceItems.GetItemCount() == 0
                && panel.DetailText.Contains("No references were identified", StringComparison.Ordinal)
                && !panel.TrySelectReference(0), "mission reference panel distinguishes an empty identified list");
            Action<MissionReferenceIndex, int> switchDuringSelection = (_, _) => panel.SetSnapshot(empty);
            panel.ScriptSelected += switchDuringSelection;
            check.That(panel.TrySelectScript(0) && ReferenceEquals(panel.Snapshot, empty) && panel.SelectedScriptIndex == null,
                "mission reference panel keeps a reentrant snapshot change");
            panel.ScriptSelected -= switchDuringSelection;
            panel.SetSnapshot(first);
            panel.TrySelectScript(0);
            int eventsBeforeReset = scriptEvents + referenceEvents;
            panel.SetSnapshot(empty);
            check.That(ReferenceEquals(panel.Snapshot, empty) && panel.SelectedScriptIndex == null
                && panel.ScriptItems.GetItemCount() == 0 && panel.ReferenceItems.GetItemCount() == 0
                && scriptEvents + referenceEvents == eventsBeforeReset, "mission reference panel drops old selections on model changes");
            panel.SetSnapshot(null);
            check.That(panel.Snapshot == null && panel.OverviewText == "No mission is open."
                && !panel.TrySelectScript(0) && !panel.TrySelectReference(0), "mission reference panel safely closes a mission");
        }
        finally { panel.Free(); }
    }
}
