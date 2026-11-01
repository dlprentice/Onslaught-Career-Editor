using System;
using System.Collections.Generic;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

internal static class MissionReferenceIndexTests
{
    internal static void Run(Checks check)
    {
        var events = new List<string> { "event-alpha" };
        var calls = new List<NativeCall> { new("call-alpha", 2) };
        var uses = new List<ScriptUse> { new(7, "owner") };
        var summaries = new List<ScriptSummary>
        {
            new("same-name", events, calls, 4, uses),
            new("same-name", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>())
        };
        var first = new List<ScriptReference> { new("unit", "target", false), new("unit", "present", true) };
        var second = new List<ScriptReference> { new("path", "target", false), new("path", "target", false) };
        var referenceLists = new[] { first, second };
        var index = MissionReferenceIndex.FromSummaries(summaries, i => referenceLists[i], 2, 4);
        check.That(index.Scripts.Count == 2 && index.Scripts[0].Index == 0 && index.Scripts[1].Index == 1,
            "mission reference index preserves script order and distinct duplicate names");
        check.That(index.Unresolved.Count == 3 && index.Unresolved[0].ScriptIndex == 0
            && index.Unresolved[1].ScriptIndex == 1 && index.Unresolved[2].ScriptIndex == 1,
            "mission reference index keeps unresolved occurrences on their own script");
        check.That(index.Unresolved[0].Role == "unit" && index.Unresolved[1].Role == "path"
            && index.Unresolved[1].Name == "target", "mission reference index preserves reference roles and names");
        check.That(index.Scripts[0].References.Count == 2 && index.Scripts[0].References[1].Resolved,
            "mission reference index preserves resolved references");
        check.That(index.Scripts[0].Events.Count == 1 && index.Scripts[0].Calls.Count == 1
            && index.Scripts[0].Uses.Count == 1 && index.Scripts[0].Uses[0].Row == 7,
            "mission reference index keeps events, calls and map-object uses");
        first.Clear(); events.Clear(); calls.Clear(); uses.Clear(); summaries.Clear();
        check.That(index.Scripts.Count == 2 && index.Scripts[0].Events.Count == 1
            && index.Scripts[0].Calls.Count == 1 && index.Scripts[0].Uses.Count == 1
            && index.Scripts[0].References.Count == 2 && index.Unresolved.Count == 3,
            "mission reference index copies inputs instead of following later edits");
        bool immutable = false;
        try { ((IList<string>)index.Scripts[0].Events).Add("changed"); }
        catch (NotSupportedException) { immutable = true; }
        check.That(immutable, "mission reference index does not expose writable snapshot lists");

        var single = new[] { new ScriptSummary("single", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>()) };
        int providerCalls = 0;
        bool scriptLimit = false, referenceLimit = false, negativeLimit = false, nullReferences = false;
        try { MissionReferenceIndex.FromSummaries(single, _ => { providerCalls++; return Array.Empty<ScriptReference>(); }, 0, 1); }
        catch (InvalidOperationException) { scriptLimit = true; }
        try { MissionReferenceIndex.FromSummaries(single, _ => new[] { new ScriptReference("unit", "x", false) }, 1, 0); }
        catch (InvalidOperationException) { referenceLimit = true; }
        try { MissionReferenceIndex.FromSummaries(single, _ => Array.Empty<ScriptReference>(), -1, 1); }
        catch (ArgumentOutOfRangeException) { negativeLimit = true; }
        try { MissionReferenceIndex.FromSummaries(single, _ => null!, 1, 1); }
        catch (InvalidOperationException) { nullReferences = true; }
        check.That(scriptLimit && providerCalls == 0 && referenceLimit && negativeLimit && nullReferences,
            "mission reference index refuses missing details and limit overflow without returning a partial index");
        var empty = MissionReferenceIndex.FromSummaries(Array.Empty<ScriptSummary>(), _ => throw new Exception(), 0, 0);
        check.That(empty.Scripts.Count == 0 && empty.Unresolved.Count == 0,
            "mission reference index accepts an empty mission without fetching references");
    }
}
