// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Spherical-trigger radius edits on authored worlds, through the real command, history, validation and world
/// serializer. The model checks inject only an in-memory session and exercise its count/summary bridge; no UI,
/// stager, game, installed data or files are used.
/// </summary>
internal static class LevelTriggerEditTests
{
    internal static void Run(Checks check)
    {
        check.Suite("trigger radius edits");
        Commands(check);
        CapturedTargets(check);
        History(check);
        Validation(check);
        BaselineExceptions(check);
        ModelBridge(check);
    }

    private static WorldBody Authored(int version = 43, float radius = 3)
    {
        WorldBody body = new()
        {
            Version = version,
            BaseLevel = -1,
            MapNumber = 2,
            Header = new WorldHeader { HeaderVersion = 3, Unused1 = 7, Unused2 = 11, V2Words = [2, 3, 5], WorldType = 1 },
            InfluenceMap = new InfluenceMap
            {
                Version = 1, Nodes = 1, Links = 1,
                NodeBytes = Enumerable.Range(1, InfluenceMap.NodeSize(1)).Select(value => (byte)value).ToArray(),
                LinkBytes = Enumerable.Range(2, InfluenceMap.LinkSize(1)).Select(value => (byte)value).ToArray(),
            },
            Timings = new WorldTimings { OldF = 1.5f, OldG = 2.5f, OldH = 3.5f, TimeLimit = 12, SGrade = 4, DGrade = 9 },
        };
        body.Header.BattleEngineConfigurations.Add("authored-config");
        body.NamedMeshes.Add("authored-mesh");
        body.Things.Add(Trigger("authored trigger", radius, new Vector3(10, 20, 30), version));
        body.Things.Add(new PlacedObject
        {
            ObjectId = ObjectKinds.Unit, Definition = "authored-unit", DiesOn = 7,
            Init = new ObjectInit
            {
                Name = "authored unit", Position = new Vector3(50, 60, 70), Orientation = new Vector3(1, 2, 3),
                MeshNumber = 2, Allegiance = 1, Target = -1, Active = 1, AttachScriptsToUnits = version >= 46 ? 1 : null,
            },
        });
        body.Things.Add(Trigger("second trigger", 4, new Vector3(25, 35, 45), version));
        WaypointPath path = new() { Name = "authored-path" };
        path.Slots.AddRange([0, 1]);
        body.WaypointPaths.Add(path);
        if (version is >= 45 and <= 47) body.LegacyTimings = new LegacyTimings { A = 1, B = 2, C = 3, D = 4, E = 5 };
        if (version >= 47) body.OccupancyGrids = [new OccupancyGrid(), new OccupancyGrid(), new OccupancyGrid()];
        if (version is >= 47 and <= 49) body.LegacyGridWords = [1, 3, 5, 7, 9];
        if (version >= 49) body.LevelStartTime = 6;
        return body;
    }

    private static PlacedObject Trigger(string name, float radius, Vector3 position, int version) => new()
    {
        ObjectId = 36,
        Init = new ObjectInit
        {
            Name = name, Position = position, Orientation = new Vector3(3, 2, 1), MeshNumber = 4, Allegiance = 2,
            Target = -1, Active = 1, AttachScriptsToUnits = version >= 46 ? 1 : null,
            SphereTrigger = new SphereTriggerInit { Radius = radius },
        },
    };

    private static float Radius(WorldBody body, int row = 0) => body.Things[row].Init.SphereTrigger!.Radius;
    private static void SetRadius(WorldBody body, float value, int row = 0) => body.Things[row].Init.SphereTrigger!.Radius = value;
    private static bool Same(float left, float right) => BitConverter.SingleToUInt32Bits(left) == BitConverter.SingleToUInt32Bits(right);
    private static bool SameBytes(byte[] left, byte[] right) => left.AsSpan().SequenceEqual(right);

    private static void Refuses(Checks check, string message, Action action)
    {
        try { action(); check.Fail(message + ": accepted"); }
        catch (InvalidOperationException) { check.That(true, message); }
    }

    private static void Commands(Checks check)
    {
        WorldBody body = Authored();
        byte[] baseline = body.Write();
        ResizeSphereTrigger resize = new(body, 0, 8);
        check.That(resize.ThingIndex == 0 && Same(resize.Radius, 8) && resize.ChangesRadius && resize.Description.Contains("authored trigger", StringComparison.Ordinal),
            "the command captures its row, requested radius and description");
        Refuses(check, "undo before apply is refused", () => resize.Undo(body));
        resize.Do(body);
        check.That(Same(Radius(body), 8), "the command changes the existing trigger radius");
        WorldBody expected = WorldBody.Read(baseline);
        SetRadius(expected, 8);
        check.That(SameBytes(body.Write(), expected.Write()), "only the requested stored radius changes");
        Refuses(check, "a made command cannot be applied twice", () => resize.Do(body));
        resize.Undo(body);
        check.That(SameBytes(body.Write(), baseline), "undo restores every stored byte");
        resize.Do(body);
        check.That(SameBytes(body.Write(), expected.Write()), "redo reproduces the same edited world");
        resize.Undo(body);

        foreach (float invalid in new[] { -1f, float.NaN, float.PositiveInfinity, float.NegativeInfinity })
            Refuses(check, "an invalid requested radius is refused", () => _ = new ResizeSphereTrigger(body, 0, invalid));
        Refuses(check, "a negative row is refused", () => _ = new ResizeSphereTrigger(body, -1, 1));
        Refuses(check, "a missing row is refused", () => _ = new ResizeSphereTrigger(body, body.Things.Count, 1));
        Refuses(check, "a unit cannot be resized as a trigger", () => _ = new ResizeSphereTrigger(body, 1, 1));
        SphereTriggerInit block = body.Things[0].Init.SphereTrigger!;
        body.Things[0].Init.SphereTrigger = null;
        Refuses(check, "a trigger without its radius block is refused", () => _ = new ResizeSphereTrigger(body, 0, 1));
        body.Things[0].Init.SphereTrigger = block;
        check.That(SameBytes(body.Write(), baseline), "refused requests do not change the world");
        ResizeSphereTrigger zero = new(body, 0, 0);
        zero.Do(body);
        check.That(Same(Radius(body), 0), "a zero radius is an allowed explicit edit");
        zero.Undo(body);
    }

    private static void CapturedTargets(Checks check)
    {
        WorldBody body = Authored();
        byte[] baseline = body.Write();
        ResizeSphereTrigger resize = new(body, 0, 8);
        WorldBody twin = WorldBody.Read(baseline);
        Refuses(check, "a byte-identical different body is refused", () => resize.Do(twin));
        check.That(SameBytes(twin.Write(), baseline), "the other body is untouched");

        PlacedObject record = body.Things[0];
        body.Things[0] = record.Clone();
        Refuses(check, "a replaced record is refused even at the same row", () => resize.Do(body));
        body.Things[0] = record;
        ObjectInit init = record.Init;
        record.Init = init.Clone();
        Refuses(check, "a replaced common block is refused", () => resize.Do(body));
        record.Init = init;
        SphereTriggerInit trigger = init.SphereTrigger!;
        init.SphereTrigger = new SphereTriggerInit { Radius = trigger.Radius };
        Refuses(check, "a replaced trigger block is refused", () => resize.Do(body));
        init.SphereTrigger = trigger;
        record.ObjectId = ObjectKinds.Unit;
        Refuses(check, "a changed record kind is refused", () => resize.Do(body));
        record.ObjectId = 36;
        body.Things.RemoveAt(0);
        Refuses(check, "a shifted target row is refused", () => resize.Do(body));
        body.Things.Insert(0, record);
        trigger.Radius = 6;
        Refuses(check, "an unexpected radius before apply is refused", () => resize.Do(body));
        check.That(Same(trigger.Radius, 6), "a refused apply preserves the intervening radius");
        trigger.Radius = 3;
        resize.Do(body);
        trigger.Radius = 9;
        Refuses(check, "an unexpected radius before undo is refused", () => resize.Undo(body));
        check.That(Same(trigger.Radius, 9), "a refused undo preserves the intervening radius");
        trigger.Radius = 8;
        init.SphereTrigger = new SphereTriggerInit { Radius = 8 };
        Refuses(check, "undo also guards the captured record block", () => resize.Undo(body));
        init.SphereTrigger = trigger;
        Refuses(check, "undo refuses a different body", () => resize.Undo(twin));
        resize.Undo(body);
        check.That(SameBytes(body.Write(), baseline), "a refused attempt does not consume the command's undo state");
    }

    private static void History(Checks check)
    {
        EditSession session = new(Authored().Write());
        byte[] baseline = session.Baseline;
        int notifications = 0;
        session.Changed += () => notifications++;
        check.That(!session.ResizeTrigger(0, 3) && !session.CanUndo && !session.CanRedo && notifications == 0,
            "a bit-identical resize does not enter history or notify");
        Refuses(check, "a no-op command applied directly does not enter history", () => session.Apply(new ResizeSphereTrigger(session.Body, 0, 3)));
        check.That(!session.CanUndo && notifications == 0, "the refused direct no-op leaves history unchanged");
        check.That(session.ResizeTrigger(0, 8) && session.CanUndo && !session.CanRedo && notifications == 1,
            "a changed radius is one ordinary history entry");
        byte[] edited = session.ToBytes();
        SetRadius(session.Body, 7);
        Refuses(check, "stale undo is refused by the session", () => session.Undo());
        check.That(session.CanUndo && !session.CanRedo && notifications == 1 && Same(Radius(session.Body), 7),
            "failed undo preserves data, history and notifications");
        SetRadius(session.Body, 8);
        check.That(session.Undo() && SameBytes(session.ToBytes(), baseline) && session.CanRedo && notifications == 2,
            "undo restores the complete baseline and retains redo");
        check.That(!session.ResizeTrigger(0, 3) && session.CanRedo && notifications == 2,
            "a no-op preserves an existing redo entry");
        SetRadius(session.Body, 6);
        Refuses(check, "stale redo is refused by the session", () => session.Redo());
        check.That(session.CanRedo && !session.CanUndo && notifications == 2 && Same(Radius(session.Body), 6),
            "failed redo preserves data, history and notifications");
        SetRadius(session.Body, 3);
        check.That(session.Redo() && SameBytes(session.ToBytes(), edited) && notifications == 3,
            "redo restores the exact previously edited world");

        EditSession observed = new(Authored().Write());
        Action throws = () => throw new InvalidOperationException("authored observer failure");
        observed.Changed += throws;
        Refuses(check, "an observer can throw after the radius is recorded", () => observed.ResizeTrigger(0, 5));
        check.That(observed.CanUndo && Same(Radius(observed.Body), 5), "an observer failure does not lose the recorded edit");
        observed.Changed -= throws;
        check.That(observed.Undo() && SameBytes(observed.ToBytes(), observed.Baseline), "the recorded edit remains undoable after an observer failure");
    }

    private static void Validation(Checks check)
    {
        foreach (int version in new[] { 43, 50 })
        {
            EditSession session = new(Authored(version).Write());
            check.That(session.Validate().Errors.Any(error => error.Code == "no-change"), "the unchanged world retains the ordinary no-change refusal");
            session.ResizeTrigger(0, 8);
            check.That(session.Validate().CanSave, "a supported radius change passes session validation");
            check.That(session.TriggerChanges() is [{ Index: 0, Name: "authored trigger" } one] && Same(one.From, 3) && Same(one.To, 8),
                "the diff names the trigger row and its stored before/after radii");
            WorldBody reread = WorldBody.Read(session.ToBytes());
            check.That(Same(Radius(reread), 8) && reread.Version == version && reread.Things.Count == session.Body.Things.Count,
                "the edited radius survives the production serializer and reader");
            SetRadius(reread, 3);
            check.That(SameBytes(reread.Write(), session.Baseline), "normalizing only the radius restores all original data");
            session.Body.Things[0].Init.Active = 4;
            check.That(session.Validate().Errors.Any(error => error.Code == "other-change"), "an unrelated stored-field edit is still refused");
            session.Body.Things[0].Init.Active = 1;
            check.That(session.Validate().CanSave, "removing the unrelated change leaves the radius edit valid");
            foreach (float invalid in new[] { -2f, float.NaN, float.PositiveInfinity, float.NegativeInfinity })
            {
                SetRadius(session.Body, invalid);
                check.That(session.Validate().Errors.Any(error => error.Code == "trigger-radius"), "a directly introduced invalid radius cannot be saved");
            }
            SetRadius(session.Body, 8);
            check.That(session.Undo() && SameBytes(session.ToBytes(), session.Baseline) && session.TriggerChanges().Count == 0,
                "undo removes the radius diff exactly");
        }

        EditSession baseWorld = new(Authored().Write(), true);
        baseWorld.ResizeTrigger(0, 8);
        ValidationReport report = baseWorld.Validate();
        check.That(report.CanSave && report.Warnings.Any(warning => warning.Code == "base-world-triggers"),
            "a base-world radius edit is allowed with a warning about its wider effect");
    }

    private static void BaselineExceptions(Checks check)
    {
        foreach (float old in new[] { -3f, float.NaN, float.PositiveInfinity, float.NegativeInfinity })
        {
            EditSession session = new(Authored(radius: old).Write());
            byte[] baseline = session.Baseline;
            session.Apply(new MoveObject(1, new Vector3(55, 65, 75)));
            check.That(session.Validate().CanSave && session.TriggerChanges().Count == 0,
                "an unchanged out-of-contract baseline radius does not reject an unrelated supported edit");
            session.ResizeTrigger(0, 2);
            check.That(session.Validate().CanSave, "a baseline radius outside the request contract can be corrected");
            session.Undo();
            check.That(Same(Radius(session.Body), old) && session.Validate().CanSave,
                "undo restores the old radius bits without newly rejecting them");
            session.Undo();
            check.That(SameBytes(session.ToBytes(), baseline), "all undo steps restore the entire authored baseline exactly");
        }
        float negativeZero = BitConverter.Int32BitsToSingle(int.MinValue);
        EditSession zero = new(Authored(radius: negativeZero).Write());
        check.That(!zero.ResizeTrigger(0, negativeZero) && !zero.CanUndo, "a bit-identical negative-zero request is a no-op");
        check.That(zero.ResizeTrigger(0, 0) && zero.TriggerChanges().Count == 1, "changing the stored zero sign is an explicit bit change");
        zero.Undo();
        check.That(Same(Radius(zero.Body), negativeZero), "undo preserves the original zero sign");
    }

    private static LevelEditorModel Model(EditSession session)
    {
        LevelEditorModel model = new([]);
        typeof(LevelEditorModel).GetProperty(nameof(LevelEditorModel.Session))!.SetValue(model, session);
        return model;
    }

    private static void ModelBridge(Checks check)
    {
        EditSession session = new(Authored().Write());
        LevelEditorModel model = Model(session);
        check.That(model.UnsavedChangeCount == 0 && model.ChangeSummary() is null, "an untouched model has no changed work to report");
        session.ResizeTrigger(0, 8);
        check.That(model.UnsavedChangeCount == 1 && model.HasUnsavedChanges &&
                   model.ChangeSummary()?.Contains("1 trigger resized", StringComparison.Ordinal) == true,
            "the model counts and describes a radius edit");
        session.Apply(new MoveObject(0, new Vector3(11, 21, 31)));
        check.That(model.UnsavedChangeCount == 1 && model.ChangeSummary()?.Contains("1 object moved", StringComparison.Ordinal) == true &&
                   model.ChangeSummary()?.Contains("1 trigger resized", StringComparison.Ordinal) == true,
            "moving and resizing one trigger counts one object and describes both changes");
        session.ResizeTrigger(2, 9);
        check.That(model.UnsavedChangeCount == 2 && model.ChangeSummary()?.Contains("2 triggers resized", StringComparison.Ordinal) == true,
            "a second trigger is counted separately and the summary is plural");
        session.Apply(new MoveObject(1, new Vector3(51, 61, 71)));
        check.That(model.UnsavedChangeCount == 3, "a different moved object is added to the changed-object count");
        session.UndoAll();
        check.That(model.UnsavedChangeCount == 0 && model.ChangeSummary() is null, "undoing every supported edit clears the model bridge");
        session.Body.Things[1].Init.Active = 7;
        check.That(model.UnsavedChangeCount == 1 && model.HasUnsavedChanges &&
                   model.ChangeSummary()?.Contains("cannot describe or save", StringComparison.Ordinal) == true,
            "the existing at-least-one fallback still protects unsupported stored changes");
    }
}
