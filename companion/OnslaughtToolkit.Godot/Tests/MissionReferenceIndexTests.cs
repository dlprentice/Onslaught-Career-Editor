using System;
using System.Collections.Generic;
using System.Linq;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

internal static class MissionReferenceIndexTests
{
    internal static void Run(Checks check)
    {
        var events = new List<string> { "start" };
        var calls = new List<NativeCall> { new("known", 1) };
        var uses = new List<ScriptUse> { new(2, "main"), new(3, "spawn") };
        var summaries = new List<ScriptSummary>
        {
            new("alpha", events, calls, 1, uses),
            new("beta", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>())
        };
        var first = new List<ScriptReference> { new("main", "missing-one", false) };
        var second = new List<ScriptReference> { new("main", "alpha", true) };
        var third = new List<ScriptReference> { new("spawn", "alpha", true), new("main", "missing-two", false) };
        IReadOnlyList<ScriptReference>[] referenceLists = [Array.Empty<ScriptReference>(), first, second, third];
        var index = MissionReferenceIndex.FromSummaries(summaries, referenceLists.Length, i => referenceLists[i], 3, 8);
        check.That(index.Scripts.Count == 2 && index.Scripts[0].Index == 0 && index.Scripts[1].Index == 1,
            "Script ordering and snapshot-local indices are retained");
        check.That(index.References.Count == 4 && index.Unresolved.Count == 2
            && index.Unresolved[0].Row == 1 && index.Unresolved[1].Row == 3
            && index.Unresolved[0].Name == "missing-one" && index.Unresolved[1].Name == "missing-two",
            "Assignments are indexed by object row, including objects beyond the script count");
        check.That(index.Scripts[0].Events.Count == 1 && index.Scripts[0].Calls.Count == 1
            && index.Scripts[0].Uses.Count == 2 && index.Scripts[0].Uses[0].Row == 2,
            "Each script keeps its events, calls and object uses");
        first.Clear(); second.Clear(); third.Clear(); events.Clear(); calls.Clear(); uses.Clear(); summaries.Clear();
        check.That(index.Scripts.Count == 2 && index.Scripts[0].Events.Count == 1
            && index.Scripts[0].Calls.Count == 1 && index.Scripts[0].Uses.Count == 2
            && index.References.Count == 4 && index.Unresolved.Count == 2,
            "The snapshot owns its data after the source collections change");
        bool immutable = false;
        try { ((IList<MissionReferenceIndex.ObjectReference>)index.References).Add(default); }
        catch (NotSupportedException) { immutable = true; }
        check.That(immutable, "Snapshot assignments cannot be modified through the public list");

        var single = new[] { new ScriptSummary("alpha", Array.Empty<string>(), Array.Empty<NativeCall>(), 0, Array.Empty<ScriptUse>()) };
        int providerCalls = 0;
        bool scriptLimit = false, referenceLimit = false, negativeLimit = false, negativeObjects = false, nullReferences = false;
        try { MissionReferenceIndex.FromSummaries(single, 1, _ => { providerCalls++; return Array.Empty<ScriptReference>(); }, 0, 1); }
        catch (InvalidOperationException) { scriptLimit = true; }
        try { MissionReferenceIndex.FromSummaries(single, 1, _ => [new ScriptReference("main", "x", false)], 1, 0); }
        catch (InvalidOperationException) { referenceLimit = true; }
        try { MissionReferenceIndex.FromSummaries(single, 0, _ => Array.Empty<ScriptReference>(), -1, 1); }
        catch (ArgumentOutOfRangeException) { negativeLimit = true; }
        try { MissionReferenceIndex.FromSummaries(single, -1, _ => Array.Empty<ScriptReference>(), 1, 1); }
        catch (ArgumentOutOfRangeException) { negativeObjects = true; }
        try { MissionReferenceIndex.FromSummaries(single, 1, _ => null!, 1, 1); }
        catch (InvalidOperationException) { nullReferences = true; }
        check.That(scriptLimit && providerCalls == 0 && referenceLimit && negativeLimit && negativeObjects && nullReferences,
            "The index refuses invalid limits, overflow and missing details without returning a partial snapshot");
        var empty = MissionReferenceIndex.FromSummaries(Array.Empty<ScriptSummary>(), 0, _ => throw new Exception(), 0, 0);
        check.That(empty.Scripts.Count == 0 && empty.References.Count == 0 && empty.Unresolved.Count == 0,
            "An empty world does not fetch object assignments");

        var authored = new WorldBody();
        authored.Scripts.Add(new MissionScript { Name = "alpha" });
        authored.Scripts.Add(new MissionScript { Name = "beta" });
        authored.Things.Add(new PlacedObject { Init = new ObjectInit { Script = "beta" } });
        authored.Things.Add(new PlacedObject { Init = new ObjectInit { Script = "Beta" } });
        authored.Things.Add(new PlacedObject { Init = new ObjectInit { Script = "missing-late", SpawnScript = "alpha" } });
        var indexed = MissionReferenceIndex.Capture(authored, 8, 16);
        check.That(indexed.Scripts[0].Uses.Count == 1 && indexed.Scripts[0].Uses[0].Row == 2
            && indexed.Scripts[1].Uses.Count == 1 && indexed.Scripts[1].Uses[0].Row == 0,
            "Script uses follow the assigned script even when script and object order differ");
        check.That(indexed.Unresolved.Count == 2 && indexed.Unresolved.Any(reference => reference.Row == 2 && reference.Name == "missing-late")
            && indexed.Unresolved.Any(reference => reference.Row == 1 && reference.Name == "Beta"),
            "Late object assignments and exact-case mismatches are found without assigning them to a script");
        bool matchesPublicLookup = Enumerable.Range(0, authored.Things.Count).All(row =>
            indexed.References.Where(reference => reference.Row == row)
                .Select(reference => new ScriptReference(reference.Role, reference.Name, reference.Resolved))
                .SequenceEqual(ScriptCatalog.ReferencesOf(authored, row)));
        check.That(matchesPublicLookup, "The shared name set agrees with the existing exact-case object lookup for every row");
        authored.Things[2].Init.Script = "alpha";
        var refreshed = MissionReferenceIndex.Capture(authored, 8, 16);
        check.That(indexed.Unresolved.Count == 2 && indexed.Unresolved.Any(reference => reference.Name == "missing-late")
            && refreshed.Unresolved.Count == 1 && refreshed.Scripts[0].Uses.Count == 2,
            "Refreshing after an edit changes the new snapshot without mutating the old one");
        var noScripts = new WorldBody();
        noScripts.Things.Add(new PlacedObject { Init = new ObjectInit { Script = "unavailable" } });
        var withoutScripts = MissionReferenceIndex.Capture(noScripts, 0, 1);
        check.That(withoutScripts.Scripts.Count == 0 && withoutScripts.Unresolved.Count == 1 && withoutScripts.Unresolved[0].Row == 0,
            "Objects are checked even when the world contains no scripts");
        bool actualLimit = false;
        try { MissionReferenceIndex.Capture(authored, 8, 3); }
        catch (InvalidOperationException) { actualLimit = true; }
        check.That(actualLimit, "The reference bound includes assignments on every object");
        var oversized = new WorldBody();
        oversized.Scripts.Add(new MissionScript { Name = "alpha", Code = null! });
        oversized.Things.Add(new PlacedObject { Init = new ObjectInit { Script = "alpha", SpawnScript = "beta" } });
        bool boundedBeforeSummary = false;
        try { MissionReferenceIndex.Capture(oversized, 1, 1); }
        catch (InvalidOperationException) { boundedBeforeSummary = true; }
        check.That(boundedBeforeSummary, "An oversized assignment set is refused before script summaries are built");
    }
}
