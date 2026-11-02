// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Text;
using System.Text.Json.Nodes;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Tests;

internal static class CeMissionProjectTests
{
    internal static CeMissionProject Authored() => new("test_mission", "Authored mission Ω",
        [new("object_b", "Second object", "test.second", new Vector3(5, 0, 10)),
         new("object_a", "First object", "test.first", new Vector3(0, -0f, 4), "source_a")],
        [new("source_b", "Other source", "// Other authored source\n"),
         new("source_a", "Mission source", "// Authored Ω\r\n\t// Kept exactly\n")], "source_a");

    internal static void Run(Checks check)
    {
        check.Suite("CE mission authoring document");
        CeMissionProject project = Authored();
        byte[] bytes = CeMissionProjectJson.Write(project);
        CeMissionProject restored = CeMissionProjectJson.Read(bytes);
        check.That(bytes.AsSpan().SequenceEqual(CeMissionProjectJson.Write(restored)), "project JSON is deterministic after reopening");
        check.That(restored.Placements[0].Id == "object_a" && restored.Scripts[0].Id == "source_a", "stable IDs define canonical ordering");
        check.That(restored.Placement("object_a").ScriptId == "source_a" && restored.EntryScriptId == "source_a", "object and mission source links survive reopening");
        check.That(restored.Script("source_a").Text == project.Script("source_a").Text, "Unicode, tabs and source line endings survive exactly");
        check.That(BitConverter.SingleToUInt32Bits(restored.Placement("object_a").Position.Y) == BitConverter.SingleToUInt32Bits(-0f), "negative zero coordinates survive JSON");
        check.That(CeMissionProjectJson.Read(CeMissionProjectJson.Write(CeMissionProject.Empty("empty", "Empty"))).Placements.Count == 0,
            "an empty project needs no installed level or script");
        CeMissionPlacement[] owned = [new("object", "Object", "definition", Vector3.One)];
        CeMissionProject copied = new("copied", "Copied", owned, []);
        owned[0] = owned[0] with { Position = Vector3.Zero };
        check.That(copied.Placements[0].Position == Vector3.One, "project captures caller placement collections");

        RejectModel(check, () => new("bad id", "Name", [], []), "invalid project identifiers are refused");
        RejectModel(check, () => new("valid", "Name", [project.Placements[0], project.Placements[0]], project.Scripts), "duplicate placement IDs are refused");
        RejectModel(check, () => new("valid", "Name", [], [project.Scripts[0], project.Scripts[0]]), "duplicate script IDs are refused");
        RejectModel(check, () => new("valid", "Name", [project.Placements[0] with { ScriptId = "absent" }], project.Scripts), "dangling object script links are refused");
        RejectModel(check, () => new("valid", "Name", [], [], "absent"), "dangling mission entry source is refused");
        RejectModel(check, () => new("valid", "Name", [project.Placements[0] with { Position = new(float.NaN, 0, 0) }], project.Scripts), "nonfinite placement coordinates are refused");
        RejectModel(check, () => new("valid", "Name", [], [new("source", "Source", "bad\0source")]), "source NUL characters are refused");
        RejectModel(check, () => new("valid", "Name", [], [new("source", "Source", "\ud800")]), "unpaired Unicode surrogates are refused");
        RejectModel(check, () => new("valid", "Name", [], [new("source", "Source", new string('x', CeMissionProject.MaxSourceBytes + 1))]), "source resource limit is enforced");
        RejectModel(check, () => new("valid", "Name", Enumerable.Repeat(project.Placements[0], CeMissionProject.MaxPlacements + 1), project.Scripts), "placement resource limit is enforced");

        RejectJson(check, bytes, root => root["future_field"] = true, "unknown project fields are refused");
        RejectJson(check, bytes, root => root.Remove("coordinates"), "missing coordinate frames are refused");
        RejectJson(check, bytes, root => root["version"] = 2, "unknown project versions are refused");
        RejectJson(check, bytes, root => root["coordinates"] = "another-frame", "unknown coordinate frames are refused");
        RejectJson(check, bytes, root => root["source_language"] = "another-language", "unknown source languages are refused");
        RejectJson(check, bytes, root => root["placements"]![0]!["position"] = new JsonArray(0, 1), "positions need exactly three coordinates");
        RejectJson(check, bytes, root => root["placements"]![0]!["script"] = "missing", "JSON cannot introduce dangling source links");
        string duplicate = Encoding.UTF8.GetString(bytes).Replace("\"version\": 1", "\"version\": 1, \"version\": 1", StringComparison.Ordinal);
        RejectBytes(check, Encoding.UTF8.GetBytes(duplicate), "duplicate JSON fields are refused");
        RejectBytes(check, bytes.AsMemory(0, bytes.Length / 2), "truncated JSON is refused");
        RejectBytes(check, new byte[CeMissionProject.MaxDocumentBytes + 1], "document byte limit is checked before parsing");
        EditorChecks(check, project);
    }

    private static void EditorChecks(Checks check, CeMissionProject project)
    {
        CeMissionProjectEditor editor = new(project);
        CeMissionProjectMarkers snapshot = editor.CaptureMarkers();
        check.That(snapshot.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 20, out var hit) &&
            snapshot.TryResolve(editor, hit, out var picked) && picked?.Id == "object_a", "3D hits resolve to a stable authored ID");
        check.That(editor.TryMovePlacement("object_a", new Vector3(2, 3, 4), editor.Revision, out _), "authored objects move without a retail session");
        check.That(editor.Current.Placement("object_a").Position == new Vector3(2, 3, 4) && editor.HasUnsavedChanges, "placement changes update the document");
        check.That(!snapshot.TryResolve(editor, hit, out _), "document changes invalidate prior 3D hits");
        check.That(editor.Undo() && ReferenceEquals(editor.Current, project), "Undo restores the complete previous document");
        check.That(!snapshot.TryResolve(editor, hit, out _), "Undo does not resurrect stale 3D hits");
        check.That(editor.Redo() && editor.Current.Placement("object_a").Position.X == 2, "Redo restores the authored move");
        long stale = editor.Revision;
        check.That(editor.TrySetSource("source_a", "// Edited source\n", editor.Revision, out _), "source edits are undoable document changes");
        check.That(!editor.TryMovePlacement("object_a", Vector3.Zero, stale, out _), "delayed coordinate edits refuse stale revisions");
        check.That(editor.TryBindScript("object_b", "source_a", editor.Revision, out _) && editor.Current.Placement("object_b").ScriptId == "source_a",
            "authored objects can link to preserved mission source");
        CeMissionProject before = editor.Current;
        check.That(!editor.TryBindScript("object_b", "missing", editor.Revision, out _) && ReferenceEquals(editor.Current, before), "invalid source binding changes nothing");
        check.That(!editor.TryApplyDrafts(null, new Dictionary<string, Vector3> { ["object_a"] = new(float.NaN, 0, 0) },
            new Dictionary<string, string> { ["source_a"] = "// valid new source" }, editor.Revision, out _) && ReferenceEquals(editor.Current, before),
            "one invalid coordinate refuses the complete pending source/position batch");
        check.That(editor.TryApplyDrafts("Renamed", new Dictionary<string, Vector3> { ["object_b"] = new(10, 11, 12) },
            new Dictionary<string, string> { ["source_a"] = "// kept together\n" }, editor.Revision, out _), "name, positions and source can be kept as one edit");
        check.That(editor.Undo() && ReferenceEquals(editor.Current, before), "one Undo restores every draft field");
        check.That(editor.MarkSaved(editor.Revision) && !editor.HasUnsavedChanges, "the current revision can be marked saved");
        check.That(!editor.MarkSaved(editor.Revision - 1), "an older completed save cannot mark newer work saved");
        check.That(editor.TryAddScript(new("new_source", "New source", ""), editor.Revision, out _) &&
            editor.TryAddPlacement(new("new_object", "New object", "authored.definition", new(20, 30, 0), "new_source"), editor.Revision, out _),
            "a project can author a new source and object from nothing");
        check.That(editor.TrySetEntry("new_source", editor.Revision, out _) && editor.Current.EntryScriptId == "new_source", "mission entry source is explicit");
        editor.Open(CeMissionProjectJson.Read(CeMissionProjectJson.Write(editor.Current)));
        check.That(!editor.CanUndo && !editor.CanRedo && !editor.HasUnsavedChanges, "opening a project starts clean independent history");
        check.That(!editor.CaptureMarkers().TryResolve(editor, hit, out _), "one snapshot cannot accept another snapshot's hit");
    }

    private static void RejectModel(Checks check, Func<CeMissionProject> create, string message)
    {
        bool refused = false;
        try { _ = create(); } catch (ArgumentException) { refused = true; }
        check.That(refused, message);
    }

    private static void RejectJson(Checks check, byte[] original, Action<JsonObject> change, string message)
    {
        JsonObject root = JsonNode.Parse(original)!.AsObject();
        change(root);
        RejectBytes(check, Encoding.UTF8.GetBytes(root.ToJsonString()), message);
    }

    private static void RejectBytes(Checks check, ReadOnlyMemory<byte> bytes, string message)
    {
        bool refused = false;
        try { _ = CeMissionProjectJson.Read(bytes); } catch (InvalidDataException) { refused = true; }
        check.That(refused, message);
    }
}
