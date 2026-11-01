// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;
using NumericVector3 = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The real Godot inspector, edit history, model summaries and world serializer on small authored worlds.
/// Only the session is injected into the real model; no archive, compiler, stager, game or installed data is used.
/// This file is also a focused headless entry, without invoking the complete Companion workflow suite.
/// </summary>
public partial class SphereTriggerRadiusPanelTests : SceneTree
{
    public override void _Initialize() => _ = RunFocusedAsync();

    private async Task RunFocusedAsync()
    {
        Checks check = new();
        int exit = 1;
        try
        {
            await RunAsync(this, check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"SPHERE_TRIGGER_RADIUS_PANEL: {check.Count} checks, {check.Failures.Count} failures; authored headless UI scope only.");
            exit = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("SPHERE_TRIGGER_RADIUS_PANEL stopped: " + error); }
        finally { Quit(exit); }
    }

    internal static async Task RunAsync(SceneTree tree, Checks check)
    {
        check.Suite("trigger radius inspector");
        SphereTriggerRadiusPanel panel = new();
        tree.Root.AddChild(panel);
        await tree.ToSignal(tree, SignalName.ProcessFrame);
        try
        {
            check.That(!panel.Visible && panel.Apply.Disabled && !panel.HasDraft, "without a selection the inspector is hidden and has no draft");
            NormalEdits(panel, check);
            InvalidInput(panel, check);
            CapturedTargets(panel, check);
            BaselineExceptions(panel, check);
            await Listening(tree, panel, check);
            panel.Clear();
            check.That(!panel.Visible && panel.Apply.Disabled && !panel.HasDraft && panel.RadiusInput.Text.Length == 0,
                "Clear removes the target and its unapplied text");
        }
        finally
        {
            if (panel.GetParent() is { } parent) parent.RemoveChild(panel);
            panel.Free();
        }
    }

    private static EditSession Authored(float radius = 3)
    {
        WorldBody body = new() { Version = 43, BaseLevel = -1, MapNumber = 2 };
        body.Things.Add(new PlacedObject
        {
            ObjectId = 36,
            Init = new ObjectInit
            {
                Name = "authored trigger", Position = new NumericVector3(10, 20, 30),
                SphereTrigger = new SphereTriggerInit { Radius = radius }, Active = 1,
            },
        });
        body.Things.Add(new PlacedObject
        {
            ObjectId = ObjectKinds.Unit, Definition = "authored unit",
            Init = new ObjectInit { Name = "authored unit", Position = new NumericVector3(40, 50, 60), Active = 1 },
        });
        body.Things.Add(new PlacedObject
        {
            ObjectId = 36,
            Init = new ObjectInit { Name = "second trigger", SphereTrigger = new SphereTriggerInit { Radius = 6 } },
        });
        return new EditSession(body.Write());
    }

    private static LevelEditorModel Model(EditSession session)
    {
        LevelEditorModel model = new([]);
        ReplaceSession(model, session);
        return model;
    }

    private static void ReplaceSession(LevelEditorModel model, EditSession session) =>
        typeof(LevelEditorModel).GetProperty(nameof(LevelEditorModel.Session))!.SetValue(model, session);

    private static float Radius(EditSession session) => session.Body.Things[0].Init.SphereTrigger!.Radius;
    private static bool Same(float left, float right) => BitConverter.SingleToUInt32Bits(left) == BitConverter.SingleToUInt32Bits(right);
    private static void Type(SphereTriggerRadiusPanel panel, string text)
    {
        panel.RadiusInput.Text = text;
        panel.RadiusInput.EmitSignal(LineEdit.SignalName.TextChanged, text);
    }
    private static void Press(SphereTriggerRadiusPanel panel) => panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);

    private static void NormalEdits(SphereTriggerRadiusPanel panel, Checks check)
    {
        EditSession session = Authored();
        LevelEditorModel model = Model(session);
        byte[] baseline = session.ToBytes();
        int drafts = 0, outcomes = 0, changes = 0;
        MoveOutcome? last = null;
        void Draft() => drafts++;
        void Outcome(MoveOutcome value) { outcomes++; last = value; }
        panel.DraftChanged += Draft;
        panel.ResizeResult += Outcome;
        session.Changed += () => changes++;
        try
        {
            panel.Bind(model, 0);
            check.That(panel.Visible && !panel.Apply.Disabled && panel.RadiusInput.Text == "3" && !panel.HasDraft,
                "a spherical trigger shows its stored radius and an apply control");
            panel.Bind(model, 1);
            check.That(!panel.Visible && panel.Apply.Disabled && !panel.HasDraft, "a unit does not show trigger controls");
            foreach (int? row in new int?[] { null, -1, 3 })
            {
                panel.Bind(model, row);
                check.That(!panel.Visible && panel.Apply.Disabled, "an absent or out-of-range selection stays hidden");
            }
            panel.Bind(model, 0);
            Type(panel, "8");
            check.That(panel.HasDraft && drafts == 1 && Same(Radius(session), 3) && !session.CanUndo,
                "typing creates an unapplied draft without editing the world");
            Type(panel, "9");
            check.That(panel.HasDraft && drafts == 2 && Same(Radius(session), 3),
                "another typed value notifies pending confirmations even while the same one draft stays dirty");
            Type(panel, "8");
            panel.Bind(model, 0);
            panel.Refresh();
            check.That(panel.RadiusInput.Text == "8" && panel.HasDraft && drafts == 3,
                "repeated binding and refresh preserve the draft and emit no duplicate dirtiness transition");
            session.Apply(new MoveObject(1, new NumericVector3(41, 50, 60)));
            check.That(panel.RadiusInput.Text == "8" && panel.HasDraft && Same(Radius(session), 3),
                "an unrelated undoable edit does not erase the draft");
            session.Undo();
            Press(panel);
            byte[] resized = session.ToBytes();
            WorldBody expected = WorldBody.Read(baseline);
            expected.Things[0].Init.SphereTrigger!.Radius = 8;
            check.That(last?.Result == MoveResult.Moved && outcomes == 1 && Same(Radius(session), 8) && session.CanUndo &&
                resized.SequenceEqual(expected.Write()), "Apply edits only that radius through the actual session");
            check.That(!panel.HasDraft && drafts == 4 && panel.RadiusInput.Text == "8" && model.UnsavedChangeCount == 1 &&
                model.ChangeSummary()?.Contains("1 trigger resized", StringComparison.Ordinal) == true,
                "an applied radius clears the draft and reaches the actual model count and summary");
            check.That(session.Undo() && session.ToBytes().SequenceEqual(baseline) && panel.RadiusInput.Text == "3" && !panel.HasDraft &&
                model.UnsavedChangeCount == 0, "undo restores the complete world and refreshes the inspector");
            check.That(session.Redo() && session.ToBytes().SequenceEqual(resized) && panel.RadiusInput.Text == "8" && !panel.HasDraft,
                "redo restores the same bytes and refreshes the inspector");
            session.Undo();
            int priorChanges = changes;
            Type(panel, "3.0");
            Press(panel);
            check.That(last?.Result == MoveResult.Unchanged && !session.CanUndo && session.CanRedo && changes == priorChanges &&
                session.ToBytes().SequenceEqual(baseline) && !panel.HasDraft && panel.RadiusInput.Text == "3",
                "an equivalent numeric spelling adds no history or notification and preserves redo");
            Type(panel, "0.1");
            Press(panel);
            check.That(last?.Result == MoveResult.Moved && Same(Radius(session), 0.1f) &&
                panel.Note.Text.Contains("Rounded", StringComparison.Ordinal), "a rounded decimal reports the stored precision");
            session.Undo();
            Type(panel, "0");
            panel.RadiusInput.EmitSignal(LineEdit.SignalName.TextSubmitted, "0");
            check.That(last?.Result == MoveResult.Moved && Same(Radius(session), 0), "submitting the field applies a zero radius");
            session.Undo();
            Type(panel, "-0");
            Press(panel);
            check.That(Same(Radius(session), -0f) && session.CanUndo, "the inspector preserves an explicitly requested negative zero");
            session.Undo();
            check.That(session.ToBytes().SequenceEqual(baseline), "all ordinary edits undo to every original authored byte");
            Type(panel, "11");
            panel.Bind(model, 2);
            check.That(panel.RadiusInput.Text == "6" && !panel.HasDraft, "a genuinely different selection starts from its own radius");
        }
        finally { panel.DraftChanged -= Draft; panel.ResizeResult -= Outcome; }
    }

    private static void InvalidInput(SphereTriggerRadiusPanel panel, Checks check)
    {
        EditSession session = Authored();
        panel.Bind(Model(session), 0);
        byte[] baseline = session.ToBytes();
        MoveOutcome? last = null;
        void Outcome(MoveOutcome value) => last = value;
        panel.ResizeResult += Outcome;
        try
        {
            foreach (string invalid in new[] { "", "abc", "NaN", "Infinity", "-Infinity", "1e39", "-1", "1,5" })
            {
                Type(panel, invalid);
                Press(panel);
                check.That(last?.Result == MoveResult.Refused && panel.Note.Text.Length > 0 && session.ToBytes().SequenceEqual(baseline) &&
                    !session.CanUndo && panel.HasDraft, "invalid radius text is explained without editing or losing the draft");
            }
            panel.UseStoredRadius.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(panel.RadiusInput.Text == "3" && !panel.HasDraft && !session.CanUndo,
                "Use stored radius explicitly discards invalid unapplied text");
        }
        finally { panel.ResizeResult -= Outcome; }
    }

    private static void CapturedTargets(SphereTriggerRadiusPanel panel, Checks check)
    {
        Action<EditSession, LevelEditorModel>[] replacements =
        [
            (session, model) => ReplaceSession(model, Authored()),
            (session, _) => session.Body.Things[0] = session.Body.Things[0].Clone(),
            (session, _) => session.Body.Things[0].Init = session.Body.Things[0].Clone().Init,
            (session, _) => session.Body.Things[0].Init = null!,
            (session, _) => session.Body.Things[0].Init.SphereTrigger = new SphereTriggerInit { Radius = 3 },
            (session, _) => session.Body.Things[0].ObjectId = ObjectKinds.Unit,
            (session, _) => session.Body.Things[0].Init.SphereTrigger = null,
            (session, _) => session.Body.Things.RemoveAt(0),
        ];
        MoveOutcome? last = null;
        void Outcome(MoveOutcome value) => last = value;
        panel.ResizeResult += Outcome;
        try
        {
            foreach (Action<EditSession, LevelEditorModel> replace in replacements)
            {
                EditSession session = Authored();
                LevelEditorModel model = Model(session);
                panel.Bind(model, 0);
                Type(panel, "8");
                replace(session, model);
                // The direct mutation deliberately sends no notification, so Apply itself must guard the captured target.
                PlacedObject[] records = session.Body.Things.ToArray();
                Press(panel);
                check.That(last?.Result == MoveResult.Refused && !session.CanUndo && !model.Session!.CanUndo &&
                    session.Body.Things.SequenceEqual(records) &&
                    (model.Session.Body.Things[0].Init?.SphereTrigger is not { } trigger || Same(trigger.Radius, 3)),
                    "Apply refuses a stale session, record, init block, radius block, kind or row before editing");
            }

            EditSession radiusSession = Authored();
            LevelEditorModel radiusModel = Model(radiusSession);
            panel.Bind(radiusModel, 0);
            Type(panel, "8");
            radiusSession.ResizeTrigger(0, 9);
            panel.Bind(radiusModel, 0);
            panel.Refresh();
            byte[] externallyEdited = radiusSession.ToBytes();
            Press(panel);
            check.That(last?.Result == MoveResult.Refused && Same(Radius(radiusSession), 9) && panel.RadiusInput.Text == "8" && panel.HasDraft &&
                radiusSession.ToBytes().SequenceEqual(externallyEdited),
                "refresh never rebases a pending draft over another radius edit");
            panel.UseStoredRadius.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(panel.RadiusInput.Text == "9" && !panel.HasDraft, "explicit reload accepts the newer stored radius");
            Type(panel, "8");
            Press(panel);
            check.That(last?.Result == MoveResult.Moved && Same(Radius(radiusSession), 8), "a fresh draft can edit the explicitly reloaded radius");
            radiusSession.Undo();
            check.That(radiusSession.ToBytes().SequenceEqual(externallyEdited) && panel.RadiusInput.Text == "9",
                "undo restores the newer captured radius exactly");

            EditSession unannounced = Authored();
            panel.Bind(Model(unannounced), 0);
            Type(panel, "8");
            unannounced.Body.Things[0].Init.SphereTrigger!.Radius = 4;
            byte[] unexpectedRadius = unannounced.ToBytes();
            Press(panel);
            check.That(last?.Result == MoveResult.Refused && !unannounced.CanUndo && unannounced.ToBytes().SequenceEqual(unexpectedRadius) &&
                panel.RadiusInput.Text == "8" && panel.HasDraft, "Apply guards an unexpected radius even without a change notification");

            panel.Bind(radiusModel, 0);
            Type(panel, "12");
            EditSession fresh = Authored(4);
            ReplaceSession(radiusModel, fresh);
            panel.Bind(radiusModel, 0);
            check.That(panel.RadiusInput.Text == "4" && !panel.HasDraft, "rebinding a genuinely new session starts a fresh selection");
        }
        finally { panel.ResizeResult -= Outcome; }
    }

    private static void BaselineExceptions(SphereTriggerRadiusPanel panel, Checks check)
    {
        foreach (float radius in new[] { -2f, float.NaN, float.PositiveInfinity })
        {
            EditSession session = Authored(radius);
            panel.Bind(Model(session), 0);
            byte[] baseline = session.ToBytes();
            check.That(panel.Visible && !panel.HasDraft && !session.CanUndo && session.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["no-change"]) &&
                panel.Note.Text.Contains("stored radius", StringComparison.OrdinalIgnoreCase),
                "an unchanged out-of-range baseline is inspectable and is not newly rejected");
            Type(panel, "2");
            Press(panel);
            check.That(Same(Radius(session), 2) && session.Validate().CanSave, "an explicit valid edit can correct an older baseline radius");
            session.Undo();
            check.That(session.ToBytes().SequenceEqual(baseline) && Same(Radius(session), radius) && !panel.HasDraft,
                "undo restores the old baseline bits and refreshes without rewriting them");
        }
    }

    private static async Task Listening(SceneTree tree, SphereTriggerRadiusPanel panel, Checks check)
    {
        EditSession old = Authored();
        panel.Bind(Model(old), 0);
        EditSession current = Authored(4);
        LevelEditorModel model = Model(current);
        panel.Bind(model, 0);
        Type(panel, "5");
        old.ResizeTrigger(0, 7);
        check.That(panel.HasDraft && panel.RadiusInput.Text == "5" && Same(Radius(current), 4), "rebinding removes the old session listener");
        panel.UseStoredRadius.EmitSignal(BaseButton.SignalName.Pressed);
        tree.Root.RemoveChild(panel);
        current.ResizeTrigger(0, 6);
        check.That(panel.RadiusInput.Text == "4", "leaving the tree stops session notifications");
        tree.Root.AddChild(panel);
        await tree.ToSignal(tree, SignalName.ProcessFrame);
        check.That(panel.RadiusInput.Text == "6" && !panel.HasDraft, "returning to the tree refreshes the current stored radius");
    }
}
