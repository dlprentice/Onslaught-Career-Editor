// SPDX-License-Identifier: GPL-3.0-only
using System.IO.Compression;
using System.Numerics;
using System.Text;
using System.Text.Json.Nodes;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Editor snapshot round trips and refusals on authored worlds and terrain, with no filesystem or game.</summary>
internal static class EditorProjectTests
{
    private static byte[] Unpack(string packed)
    {
        using MemoryStream input = new(Convert.FromBase64String(string.Concat(packed.Where(c => !char.IsWhiteSpace(c)))));
        using ZLibStream inflater = new(input, CompressionMode.Decompress);
        using MemoryStream output = new();
        inflater.CopyTo(output);
        return output.ToArray();
    }

    private static byte[] AuthoredWorld()
    {
        WorldBody body = WorldBody.Read(Unpack(LevelVectors.Valid.Single(vector => vector.Name == "authored-v50").Body));
        body.Scripts.Clear();
        body.Scripts.Add(new MissionScript { Name = "alpha" });
        return body.Write();
    }

    private static bool Refused(Action action)
    {
        try { action(); return false; }
        catch (InvalidDataException) { return true; }
    }

    private static byte[] Change(byte[] project, Action<JsonObject> edit)
    {
        JsonObject root = JsonNode.Parse(project)!.AsObject();
        edit(root);
        return Encoding.UTF8.GetBytes(root.ToJsonString());
    }

    private static bool SameBits(TerrainSurface left, TerrainSurface right)
    {
        Vector3[] a = left.Vertices.ToArray(), b = right.Vertices.ToArray();
        return left.Divisions == right.Divisions && a.Length == b.Length && a.Zip(b).All(pair =>
            BitConverter.SingleToUInt32Bits(pair.First.X) == BitConverter.SingleToUInt32Bits(pair.Second.X) &&
            BitConverter.SingleToUInt32Bits(pair.First.Y) == BitConverter.SingleToUInt32Bits(pair.Second.Y) &&
            BitConverter.SingleToUInt32Bits(pair.First.Z) == BitConverter.SingleToUInt32Bits(pair.Second.Z));
    }

    internal static void Run(Checks check)
    {
        check.Suite("editor project snapshot");
        byte[] baseline = AuthoredWorld(), eres = Unpack(LevelVectors.Terrain.Eres);
        EditorProjectBase basis = new(100, false, -1, false, baseline, baseline, null, eres);
        EditSession session = new(baseline);
        check.That(session.TryApply(new MoveObject(0, new Vector3(12.5f, -0f, 3f)), out _) &&
                   session.TryApply(new DuplicateObject(0, new Vector3(14f, 15f, 16f), "new unit"), out _),
                   "an authored move and unit copy are in the same session");
        MissionScript replacement = ScriptCopy.Of(session.Body.Scripts[0]);
        replacement.Code.Tail1 = 12345;
        check.That(session.TryApply(new ReplaceScript(0, replacement), out _), "an authored compiled script is replaced");
        TerrainSurface surface = TerrainSurface.Build(Heightfield.Read(eres), 4);
        TerrainDraft terrain = new(session.Body, surface);
        check.That(terrain.TryPrepare(256, 256, true, out IEditCommand? point, out _) && point is not null && session.TryApply(point, out _),
                   "an authored terrain point is raised");
        string sourceHash = EditorProject.Hash(Encoding.UTF8.GetBytes("base source"));
        string usedHash = EditorProject.Hash(WorldBodyWriter.ScriptBytes(session.Body.Scripts[0]));
        EditorProjectScript script = new(0, "alpha", sourceHash, "base source", "// uncompiled draft\r\nλ 🕹️", "// unverified text claim\n", usedHash);
        byte[] working = session.ToBytes(), saved = EditorProject.Capture(basis, session, terrain, [script]);
        RestoredEditorProject reopened = EditorProject.Restore(saved, basis);
        check.That(reopened.Session.Baseline.AsSpan().SequenceEqual(baseline) && reopened.Session.ToBytes().AsSpan().SequenceEqual(working),
                   "reopening preserves the baseline and every working world byte");
        check.That(reopened.Terrain is not null && reopened.Terrain.Offsets().SequenceEqual(terrain.Offsets()) && SameBits(reopened.Terrain.Surface, terrain.Surface),
                   "the terrain steps and sampled surface bits are restored");
        check.That(reopened.Scripts.Count == 1 && reopened.Scripts[0] == script,
                   "the actual source, uncompiled draft and unverified text claim round-trip exactly without asserting compilation");
        EditorProjectScript sourceOnly = script with { DraftText = null, UsedText = null, UsedRecordHash = null };
        check.That(EditorProject.Restore(EditorProject.Capture(basis, session, terrain, [sourceOnly]), basis).Scripts.Single() == sourceOnly,
                   "an unchanged actual source is preserved even when it has no draft or compiled-text claim");
        check.That(!reopened.Session.CanUndo && !reopened.Session.CanRedo, "reopening starts a new undo history");
        check.That(reopened.Session.TryApply(new MoveObject(0, new Vector3(20, 21, 22)), out _) && reopened.Session.Undo() &&
                   reopened.Session.ToBytes().AsSpan().SequenceEqual(working), "new edits remain undoable after reopening");

        TerrainDraft? restoredTerrain = reopened.Terrain;
        check.That(restoredTerrain is not null && restoredTerrain.TryPrepare(256, 256, false, out IEditCommand? lower, out _) && lower is not null &&
                   reopened.Session.TryApply(lower, out _) && reopened.Session.Undo() && SameBits(restoredTerrain.Surface, terrain.Surface),
                   "a new terrain edit and undo return to the restored surface exactly");

        byte[] otherAnchor = Unpack(LevelVectors.Valid.Single(vector => vector.Name == "authored-v43").Body);
        EditorProjectBase selected = basis with { SelectedWorld = true, AnchorWorld = otherAnchor };
        byte[] selectedProject = EditorProject.Capture(selected, session, terrain, [script]);
        check.That(EditorProject.Restore(selectedProject, selected).Session.ToBytes().AsSpan().SequenceEqual(working) &&
                   Refused(() => EditorProject.Restore(selectedProject, basis)), "selected-world identity is retained and cannot be silently changed");
        byte[] other = baseline.ToArray(); other[^1] ^= 1;
        byte[] otherTerrain = eres.ToArray(); otherTerrain[^1] ^= 1;
        check.That(Refused(() => EditorProject.Restore(saved, basis with { Level = 101 })) &&
                   Refused(() => EditorProject.Restore(saved, basis with { World = other, AnchorWorld = other })) &&
                   Refused(() => EditorProject.Restore(saved, basis with { Terrain = otherTerrain })),
                   "the level, world and terrain must all match the saved identities");
        check.That(Refused(() => EditorProject.Restore(Change(saved, root => root["version"] = 3), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["unknown"] = 1), basis)) &&
                   Refused(() => EditorProject.Restore(Encoding.UTF8.GetBytes("{\"kind\":\"x\",\"kind\":\"y\"}"), basis)),
                   "unknown versions and fields and repeated properties are refused");
        byte[] oldProject = Change(saved, root =>
        {
            root["version"] = 1;
            foreach (JsonNode? entry in root["scripts"]!.AsArray()) entry!.AsObject().Remove("source");
        });
        byte[] oldOriginal = oldProject.ToArray();
        bool oldRefused = false;
        try { EditorProject.Restore(oldProject, basis); }
        catch (InvalidDataException error) { oldRefused = error.Message.Contains("Version 1", StringComparison.Ordinal) && error.Message.Contains("source text", StringComparison.Ordinal); }
        check.That(oldRefused && oldProject.AsSpan().SequenceEqual(oldOriginal) && session.ToBytes().AsSpan().SequenceEqual(working),
                   "a version 1 project explicitly refuses missing source text without changing its input or the current edit");
        check.That(Refused(() => EditorProject.Restore(Change(saved, root => root["world_delta"]!["prefix"] = int.MaxValue), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["world_delta"]!["working_sha256"] = new string('0', 64)), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["world_delta"]!["insert"] = "!"), basis)),
                   "bad world bounds, hash and encoded bytes are refused");
        check.That(Refused(() => EditorProject.Restore(Change(saved, root => root["terrain_preview"]!["points"] = new JsonArray(new JsonArray(12, 1), new JsonArray(12, 1))), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["terrain_preview"]!["points"] = new JsonArray(new JsonArray(12, 33))), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["terrain_preview"]!["working_sha256"] = new string('0', 64)), basis)),
                   "duplicate points, excessive offsets and altered terrain identities are refused");
        check.That(Refused(() => EditorProject.Restore(Change(saved, root => root["scripts"]![0]!["name"] = "other"), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["scripts"]![0]!["used_record_sha256"] = new string('0', 64)), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["scripts"]!.AsArray().Add(root["scripts"]![0]!.DeepClone())), basis)),
                   "ambiguous or mismatched script associations are refused");
        check.That(Refused(() => EditorProject.Restore(Change(saved, root => root["scripts"]![0]!["source"] = "a different source"), basis)) &&
                   Refused(() => EditorProject.Restore(Change(saved, root => root["scripts"]![0]!.AsObject().Remove("source")), basis)) &&
                   Refused(() => EditorProject.Capture(basis, session, terrain, [script with { Name = "../alpha" }])),
                   "changed or missing actual source text and path-like source names are refused");
        check.That(Refused(() => EditorProject.Capture(basis, session, terrain, [script with { DraftText = "\ud800" }])) &&
                   Refused(() => EditorProject.Capture(basis, session, terrain, [script with { DraftText = new string('x', EditorProject.MaxTextBytes + 1) }])) &&
                   Refused(() => EditorProject.Restore(new byte[EditorProject.MaxProjectBytes + 1], basis)),
                   "unrepresentable text and oversized drafts or snapshots are refused");
        EditSession otherSession = new(baseline);
        TerrainDraft unrelated = new(otherSession.Body, surface);
        check.That(Refused(() => EditorProject.Capture(basis, session, unrelated, [])) && session.ToBytes().AsSpan().SequenceEqual(working) && terrain.HasChanges,
                   "a terrain from another session is refused without changing the edit");

        WorldBody many = WorldBody.Read(baseline);
        many.Scripts.Clear();
        for (int i = 0; i < 4096; i++) many.Scripts.Add(new MissionScript { Name = $"script-{i:D4}" });
        byte[] manyWorld = many.Write();
        EditSession manySession = new(manyWorld);
        EditorProjectBase manyBase = new(100, false, -1, false, manyWorld, manyWorld, null, null);
        EditorProjectScript[] drafts = [.. Enumerable.Range(0, EditorProject.MaxDrafts).Select(i =>
            new EditorProjectScript(i, $"script-{i:D4}", sourceHash, "base source", "authored draft", null, null))];
        RestoredEditorProject manyReopened = EditorProject.Restore(EditorProject.Capture(manyBase, manySession, null, drafts), manyBase);
        check.That(manyReopened.Scripts.SequenceEqual(drafts), "the supported maximum number of uniquely named drafts round-trips in a large authored script list");
        check.That(Refused(() => EditorProject.Capture(manyBase, manySession, null, [.. drafts, drafts[0]])),
                   "a draft count above the bound is refused");
        manySession.Body.Scripts[^1].Name = manySession.Body.Scripts[0].Name;
        check.That(Refused(() => EditorProject.Capture(manyBase, manySession, null, drafts)),
                   "a duplicated script name is refused even when the matching draft index is otherwise valid");
        manySession.Body.Scripts[^1].Name = manySession.Body.Scripts[0].Name.ToUpperInvariant();
        check.That(Refused(() => EditorProject.Capture(manyBase, manySession, null, drafts)),
                   "source names that collide ignoring letter case are refused");
    }

}
