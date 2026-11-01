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
            new ScriptSummary("alpha", Array.Empty<string>(), Array.Empty<NativeCall>(), 0,
                new[] { new ScriptUse(2, "main"), new ScriptUse(3, "spawn") }),
            new ScriptSummary("beta", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>()),
            new ScriptSummary("line\n" + new string('x', 130), Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>())
        };
        var rows = new IReadOnlyList<ScriptReference>[]
        {
            Array.Empty<ScriptReference>(),
            new[] { new ScriptReference("main", "missing-one", false) },
            new[] { new ScriptReference("main", "alpha", true) },
            new[] { new ScriptReference("spawn", "alpha", true), new ScriptReference("main", "missing-two", false) }
        };
        var first = MissionReferenceIndex.FromSummaries(summaries, rows.Length, i => rows[i], 3, 8);
        var empty = MissionReferenceIndex.FromSummaries(Array.Empty<ScriptSummary>(), 0, _ => throw new Exception(), 0, 0);
        var single = MissionReferenceIndex.FromSummaries(
            [new ScriptSummary("one", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, [new ScriptUse(0, "main")])],
            1, _ => [new ScriptReference("main", "one", true), new ScriptReference("spawn", "not here", false)], 1, 2);
        var panel = new MissionReferencePanel();
        try
        {
            int scriptEvents = 0, useEvents = 0, missingEvents = 0, lastScript = -1, lastUse = -1, lastMissing = -1;
            MissionReferenceIndex? eventSnapshot = null;
            panel.ScriptSelected += (which, script) => { scriptEvents++; eventSnapshot = which; lastScript = script; };
            panel.UseSelected += (which, script, use) => { useEvents++; eventSnapshot = which; lastScript = script; lastUse = use; };
            panel.MissingSelected += (which, index) => { missingEvents++; eventSnapshot = which; lastMissing = index; };
            check.That(panel.Snapshot == null && panel.ScriptItems.GetItemCount() == 0 && panel.UseItems.GetItemCount() == 0 && panel.MissingItems.GetItemCount() == 0,
                "The panel starts with no mission or selection");
            panel.SetSnapshot(first);
            check.That(panel.ExplanationsWrap, "The mission explanations wrap");
            check.That(panel.ContentScroll.HorizontalScrollMode == ScrollContainer.ScrollMode.Disabled
                && panel.ContentScroll.FollowFocus, "The mission details use a vertical scroll area that follows focus");
            check.That(panel.ScriptItems.GetItemCount() == 3 && panel.UseItems.GetItemCount() == 0 && panel.MissingItems.GetItemCount() == 2
                && panel.SelectedScriptIndex == null && scriptEvents == 0, "A snapshot lists scripts and missing assignments without selecting a script");
            check.That(panel.ScriptItems.GetItemText(0) != panel.ScriptItems.GetItemText(1), "Different script names have distinct labels");
            string bounded = panel.ScriptItems.GetItemText(2);
            check.That(!bounded.Contains('\n') && bounded.Length <= 102 && bounded.EndsWith("...", StringComparison.Ordinal),
                "Untrusted captions are single-line and bounded");
            check.That(panel.OverviewText.Contains("not found in this world", StringComparison.Ordinal)
                && panel.MissingItems.GetItemText(0).Contains("Object row 1", StringComparison.Ordinal)
                && panel.MissingItems.GetItemText(1).Contains("missing-two", StringComparison.Ordinal),
                "Missing assignments show their actual object rows and explain the world scope");
            panel.ScriptItems.EmitSignal(ItemList.SignalName.ItemSelected, 0L);
            check.That(panel.SelectedScriptIndex == 0 && scriptEvents == 1 && lastScript == 0 && ReferenceEquals(eventSnapshot, first),
                "A script selection carries the current snapshot and script index");
            check.That(panel.UseItems.GetItemCount() == 2
                && panel.UseItems.GetItemText(0).Contains("Object row 2", StringComparison.Ordinal)
                && panel.UseItems.GetItemText(1).Contains("spawn", StringComparison.Ordinal),
                "A selected script lists the object rows that actually use it");
            panel.UseItems.EmitSignal(ItemList.SignalName.ItemSelected, 1L);
            check.That(useEvents == 1 && lastScript == 0 && lastUse == 1 && ReferenceEquals(eventSnapshot, first)
                && first.Scripts[lastScript].Uses[lastUse].Row == 3, "A use selection identifies the corresponding object row");
            panel.MissingItems.EmitSignal(ItemList.SignalName.ItemSelected, 1L);
            check.That(missingEvents == 1 && lastMissing == 1 && ReferenceEquals(eventSnapshot, first)
                && first.Unresolved[lastMissing].Row == 3, "A missing-assignment selection identifies the corresponding object row");
            panel.ScriptItems.EmitSignal(ItemList.SignalName.ItemSelected, long.MaxValue);
            panel.UseItems.EmitSignal(ItemList.SignalName.ItemSelected, -1L);
            panel.MissingItems.EmitSignal(ItemList.SignalName.ItemSelected, long.MaxValue);
            check.That(!panel.TrySelectScript(-1) && !panel.TrySelectScript(int.MaxValue)
                && !panel.TrySelectUse(-1) && !panel.TrySelectUse(int.MaxValue)
                && !panel.TrySelectMissing(-1) && !panel.TrySelectMissing(int.MaxValue)
                && panel.SelectedScriptIndex == 0 && scriptEvents == 1 && useEvents == 1 && missingEvents == 1,
                "Invalid selections leave the snapshot and event counts unchanged");
            check.That(panel.TrySelectScript(1) && panel.UseItems.GetItemCount() == 0
                && panel.DetailText.Contains("No object", StringComparison.Ordinal)
                && !panel.TrySelectUse(0), "A script with no uses has an explicit empty state");
            Action<MissionReferenceIndex, int> switchDuringSelection = (_, _) => panel.SetSnapshot(empty);
            panel.ScriptSelected += switchDuringSelection;
            check.That(panel.TrySelectScript(0) && ReferenceEquals(panel.Snapshot, empty) && panel.SelectedScriptIndex == null,
                "An event can replace the snapshot without preserving a stale selection");
            panel.ScriptSelected -= switchDuringSelection;
            panel.SetSnapshot(first);
            panel.TrySelectScript(0);
            int eventsBeforeReset = scriptEvents + useEvents + missingEvents;
            panel.SetSnapshot(empty);
            check.That(ReferenceEquals(panel.Snapshot, empty) && panel.SelectedScriptIndex == null
                && panel.ScriptItems.GetItemCount() == 0 && panel.UseItems.GetItemCount() == 0 && panel.MissingItems.GetItemCount() == 0
                && scriptEvents + useEvents + missingEvents == eventsBeforeReset, "Replacing a snapshot clears selections without emitting events");
            panel.SetSnapshot(null);
            check.That(panel.Snapshot == null && panel.OverviewText == "No mission is open."
                && !panel.TrySelectScript(0) && !panel.TrySelectUse(0) && !panel.TrySelectMissing(0), "Closing the mission disables all selections");
            panel.SetSnapshot(single);
            check.That(panel.OverviewText.StartsWith("1 script; 1 object assignment ", StringComparison.Ordinal)
                && panel.TrySelectScript(0) && panel.DetailText == "1 object assignment uses this script.",
                "Single scripts, uses and missing assignments use singular wording");
        }
        finally { panel.Free(); }
    }
}
