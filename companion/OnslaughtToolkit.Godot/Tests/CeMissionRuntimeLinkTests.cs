// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Text;
using System.Text.Json.Nodes;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Tests;

internal static class CeMissionRuntimeLinkTests
{
    // Shared authored values are consumed by CE's standalone loader fixture, never by a retail data reader.
    internal static CeMissionProject Authored() => new("linked_fixture", "Authored linked placement",
        [new("beacon", "Authored beacon", "authored.beacon", new(12.5f, -7.25f, -3), "arrival")],
        [new("arrival", "Preserved source", "// Authored source Ω\r\n\t// Preserved; not executed.\n")], "arrival",
        new(777, [new("authored.beacon", "AuthoredAnchor")]));

    internal static void Run(string output, Checks check)
    {
        check.Suite("linked installed-map project contract");
        CeMissionProject legacy = CeMissionProjectTests.Authored();
        byte[] oldBytes = CeMissionProjectJson.Write(legacy);
        check.That(legacy.FormatVersion == 1 && !Encoding.UTF8.GetString(oldBytes).Contains("\"map\"", StringComparison.Ordinal) &&
            CeMissionProjectJson.Write(CeMissionProjectJson.Read(oldBytes)).AsSpan().SequenceEqual(oldBytes),
            "unlinked version-1 projects keep their source, IDs and deterministic bytes");
        CeMissionProject linked = Authored();
        byte[] bytes = CeMissionProjectJson.Write(linked);
        CeMissionProject reopened = CeMissionProjectJson.Read(bytes);
        check.That(linked.FormatVersion == 2 && reopened.Map?.Level == 777 && reopened.Map.Bindings.Single().SourceObject == "AuthoredAnchor" &&
            bytes.AsSpan().SequenceEqual(CeMissionProjectJson.Write(reopened)), "version-2 installed-map bindings round-trip deterministically");
        check.That(reopened.Placement("beacon").Position == new Vector3(12.5f, -7.25f, -3) &&
            reopened.Script("arrival").Text == linked.Script("arrival").Text && reopened.EntryScriptId == "arrival",
            "map links preserve the authored coordinates and exact source without compiling it");
        check.That(linked.RuntimeLinkStatus().Contains("existing-object", StringComparison.Ordinal) &&
            linked.RuntimeLinkStatus().Contains("not run", StringComparison.Ordinal), "runtime readiness names existing-object and source-execution limits");

        CeMissionObjectBinding[] caller = [new("authored.beacon", "AuthoredAnchor")];
        CeMissionMapLink captured = new(777, caller); caller[0] = new("changed", "Changed");
        check.That(captured.Bindings.Single().Definition == "authored.beacon", "map links capture caller collections");
        Reject(check, () => new CeMissionMapLink(0, []), "zero map links are refused");
        Reject(check, () => new CeMissionMapLink(10000, []), "map links have a bounded number");
        Reject(check, () => new CeMissionMapLink(777, [new("a", "One"), new("a", "Two")]), "a definition cannot bind two installed objects");
        Reject(check, () => new CeMissionMapLink(777, [new("a", "One"), new("b", "One")]), "one installed object cannot be targeted by two definitions");
        Reject(check, () => new CeMissionMapLink(777, [new("a", "NonASCIIΩ")]), "bounded engine object names use printable ASCII");
        CeMissionProject missing = new(linked.Id, linked.Name, linked.Placements, linked.Scripts, linked.EntryScriptId, new(777, []));
        check.That(missing.RuntimeLinkStatus().Contains("no named", StringComparison.Ordinal), "incomplete authoring remains saveable but is visibly unready for CE");
        CeMissionProject reused = new(linked.Id, linked.Name, linked.Placements.Append(linked.Placements[0] with { Id = "second" }),
            linked.Scripts, linked.EntryScriptId, linked.Map);
        check.That(reused.RuntimeLinkStatus().Contains("does not clone", StringComparison.Ordinal), "existing-object mode does not imply spawning or cloning");
        CeMissionProject far = new(linked.Id, linked.Name,
            [linked.Placements[0] with { Position = new(CeMissionProject.MaxRuntimeCoordinate + 1, 0, 0) }], linked.Scripts, linked.EntryScriptId, linked.Map);
        check.That(far.RuntimeLinkStatus().Contains("safety bound", StringComparison.Ordinal), "runtime coordinate limits do not erase an authored draft");

        CeMissionProjectEditor editor = new(linked);
        check.That(editor.TryApplyDrafts("Renamed", new Dictionary<string, Vector3> { ["beacon"] = new(2, 3, 4) },
            new Dictionary<string, string> { ["arrival"] = "// edited\n" }, editor.Revision, out _) && ReferenceEquals(editor.Current.Map, linked.Map),
            "atomic position/source/name drafts preserve their installed-map link");
        check.That(editor.TrySetMapLink(new(778, [new("authored.beacon", "OtherAnchor")]), editor.Revision, out _) &&
            editor.Current.Placement("beacon").Id == "beacon", "rebinding keeps authoring IDs stable for future added-object support");
        check.That(editor.Undo() && editor.Current.Map?.Level == 777 && editor.Current.Name == "Renamed", "map rebinding is one reversible command");
        long stale = editor.Revision;
        editor.TryMovePlacement("beacon", Vector3.One, editor.Revision, out _);
        check.That(!editor.TrySetMapLink(null, stale, out _) && editor.Current.Map is not null, "a stale map edit cannot change a newer document");
        check.That(editor.TrySetMapLink(null, editor.Revision, out _) && editor.Current.FormatVersion == 1 && editor.Current.Placement("beacon").Id == "beacon",
            "removing runtime links returns to portable authoring without losing objects or source");
        check.That(editor.Undo() && editor.Current.Map?.Level == 777, "Undo restores the exact runtime binding");

        RejectJson(check, bytes, root => root["map"]!["mode"] = "spawn-new-object", "unknown runtime modes are refused");
        RejectJson(check, bytes, root => root["map"]!["unreviewed"] = true, "unknown runtime-link fields are refused");
        RejectJson(check, bytes, root => root.Remove("map"), "a linked version requires its map record");
        RejectJson(check, bytes, root => root["version"] = 1, "a legacy version cannot silently discard a runtime link");
        RejectJson(check, bytes, root => root.Remove("version"), "a missing version is a bounded invalid-document result");

        string outputRoot = Path.Combine(output, "ce-runtime-link"); Directory.CreateDirectory(outputRoot);
        string path = Path.Combine(outputRoot, "linked.ceproject");
        CeProjectWrite written = new CeMissionProjectFiles().WriteNew(path, bytes, []);
        check.That(written.Ok && File.ReadAllBytes(path).AsSpan().SequenceEqual(bytes) &&
            CeMissionProjectJson.Read(File.ReadAllBytes(path)).Map?.Bindings.Single().SourceObject == "AuthoredAnchor",
            "the real editor file adapter publishes the authored fixture CE's loader can consume");
    }

    private static void Reject(Checks check, Action create, string label)
    {
        bool refused = false;
        try { create(); } catch (ArgumentException) { refused = true; }
        check.That(refused, label);
    }

    private static void RejectJson(Checks check, byte[] bytes, Action<JsonObject> change, string label)
    {
        JsonObject root = JsonNode.Parse(bytes)!.AsObject(); change(root); bool refused = false;
        try { CeMissionProjectJson.Read(Encoding.UTF8.GetBytes(root.ToJsonString())); } catch (InvalidDataException) { refused = true; }
        check.That(refused, label);
    }
}
