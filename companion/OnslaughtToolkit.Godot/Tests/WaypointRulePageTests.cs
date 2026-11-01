// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Read-only rule checks on an authored page. No compiler, mod publication or launch is invoked.</summary>
internal static class WaypointRulePageTests
{
    internal sealed record Fixture(LevelEditorPage Page, GameLibrary Game, Control Popups, Theme Theme, string GameRoot);

    internal static async Task<Fixture> CreateAsync(SceneTree tree, string output, Vector2 size)
    {
        string gameRoot = LevelEditorTests.GameWithLevels(output);
        File.WriteAllText(Path.Combine(gameRoot, "BEA.exe"), "Authored waypoint fixture; not an executable.");
        string archive = Path.Combine(gameRoot, "data", "resources", "100_res_PC.aya");
        File.WriteAllBytes(archive, AuthoredTerrainFixture.WithAuthoredTerrain(File.ReadAllBytes(archive)));
        AuthoredTerrainFixture.AddDraftSources(gameRoot);
        SettingsStore settings = new(Path.Combine(output, "settings.json"));
        GameLibrary game = new([], settings, ceUserFolder: Path.Combine(output, "unused-ce"), ceEnvironment: _ => null);
        typeof(GameLibrary).GetProperty(nameof(GameLibrary.Folder))!.SetValue(game, GameFolder.Inspect(gameRoot, "Authored waypoint fixture"));
        Control popups = new();
        AppServices services = new()
        {
            Workspace = new CareerWorkspace(new SaveFileWorker(new ProtectedSaveFiles())),
            Game = game, Status = new StatusLine(), Backups = new(settings, Path.Combine(output, "unused-backups")), GameRunning = () => false,
            OpenUrl = _ => throw new InvalidOperationException("Unexpected external action."), Navigate = _ => { },
            OpenCareer = null!, ChooseCareer = null!, OpenCareerFile = () => throw new InvalidOperationException("Unexpected career action."),
            AskToDiscard = (_, _, _) => throw new InvalidOperationException("Unexpected discard."), LevelEditsUnsaved = () => 0,
            Play = new CePlay(game, Path.Combine(output, "unused-play")), Popups = popups, CatchUp = () => Task.CompletedTask,
        };
        Theme theme = CompanionTheme.Build();
        LevelEditorPage page = new(services);
        page.Root.Theme = theme; page.Root.Size = size;
        await LevelTriggerInspectorPageTests.Frames(tree, 1);
        tree.Root.AddChild(popups); tree.Root.AddChild(page.Root);
        page.Refresh();
        await LevelTriggerInspectorPageTests.Frames(tree);
        return new(page, game, popups, theme, gameRoot);
    }

    internal static string DraftFor(WorldBody world) =>
        "// Authored mission-rule draft.\ninit()\n{\nFollowWaypoint(\"" + world.WaypointPaths[0].Name + "\", 0);\n" +
        "FollowWaypointWait(\"Missing authored route\", 0, 5);\nFollowWaypoint(route, 0);\n}\n";

    internal static async Task DisposeAsync(SceneTree tree, Fixture fixture)
    {
        fixture.Page.Root.QueueFree(); fixture.Popups.QueueFree();
        await LevelTriggerInspectorPageTests.Frames(tree);
        fixture.Theme.Dispose();
    }

    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("waypoint rule check through editor page");
        Fixture fixture = await CreateAsync(tree, Path.Combine(output, "waypoint-page"), new Vector2(1280, 800));
        LevelEditorPage page = fixture.Page;
        try
        {
            if (page.Model is not { Session: { } session } model || session.Body.Scripts.Count == 0 || session.Body.WaypointPaths.Count == 0)
            { check.Fail("the authored page opens a world with scripts and a waypoint path"); return; }
            string name = session.Body.Scripts[0].Name;
            byte[] worldBefore = session.ToBytes();
            string[] filesBefore = LevelEditorPageTests.Snapshot(fixture.GameRoot);
            check.That(page.Scripts.CurrentSource?.Source is not null && !page.CheckWaypointRules.Disabled, "the source selected when the page opens can be checked");
            check.That(page.ShowScript(name) && !page.CheckWaypointRules.Disabled, "selecting authored source enables its read-only waypoint check");
            page.EditSource.ButtonPressed = true;
            string draft = DraftFor(session.Body);
            page.Scripts.Source.Text = draft;
            await LevelTriggerInspectorPageTests.Frames(tree);
            int changes = page.ChangeCount;
            long revision = page.ConfirmationRevision;
            string draftHash = page.Scripts.DraftContentHash();
            bool saveDisabled = page.Save.Disabled, playDisabled = page.Play.Disabled;
            page.CheckWaypointRules.EmitSignal(BaseButton.SignalName.Pressed);
            WaypointRuleReport? report = page.WaypointRules;
            check.That(report is { Available: true, Calls: 3, Resolved: 1, Unresolved: 1, Unchecked: 1 },
                "the actual button audits a resolved literal, missing literal and dynamic expression in the current draft");
            check.That(page.WaypointRulesText.Contains("runtime behavior are unchecked", StringComparison.Ordinal) &&
                page.WaypointRulesText.Contains("includes/macros", StringComparison.Ordinal), "the visible result states its source-only and runtime limitations");
            Tree results = (Tree)page.Root.FindChild("WaypointRuleFindings", true, false);
            results.GetRoot().GetChild(1).Select(0);
            await LevelTriggerInspectorPageTests.Frames(tree);
            check.That(page.Scripts.Source.GetCaretLine() == 4 && page.Scripts.Source.GetCaretColumn() == 0,
                "selecting an actual finding row navigates to its original source line");
            check.That(session.ToBytes().SequenceEqual(worldBefore) && !session.CanUndo && page.Scripts.SourceText == draft &&
                page.Scripts.DraftContentHash() == draftHash && page.ChangeCount == changes && page.ConfirmationRevision == revision &&
                page.Save.Disabled == saveDisabled && page.Play.Disabled == playDisabled,
                "checking and source navigation preserve world bytes, draft ownership, history and action availability");
            page.Scripts.Source.Text = draft + "// Newer draft.\n";
            await LevelTriggerInspectorPageTests.Frames(tree);
            check.That(page.WaypointRules is null && page.WaypointRulesText.Length == 0 && !page.GoToWaypointRule(0) && page.Scripts.SourceText.EndsWith("// Newer draft.\n", StringComparison.Ordinal),
                "editing text clears stale findings and cannot navigate or replace the newer draft");
            page.RunWaypointRuleCheck();
            typeof(LevelEditorModel).GetProperty(nameof(LevelEditorModel.Session))!.SetValue(model, new EditSession(worldBefore));
            check.That(!page.GoToWaypointRule(0) && page.WaypointRules is null, "a silently replaced session cannot reuse old source navigation");

            page.OpenLevel(100); page.ShowScript(name); page.EditSource.ButtonPressed = true;
            page.Scripts.Source.Text = draft;
            page.RunWaypointRuleCheck();
            page.OpenLevel(200);
            check.That(page.WaypointRules is null && page.WaypointRulesText.Length == 0, "opening another authored level clears the old rule report");
            page.OpenLevel(100); page.ShowScript(name); page.EditSource.ButtonPressed = true;
            page.Scripts.Source.Text = draft;
            check.That(model.BeginTerrainPreview(out _) && model.ChangeTerrainPreview(0, 0, true).Result == MoveResult.Moved,
                "the authored fixture can hold a terrain preview change");
            if (model.TerrainPreviewSurface is not { } surface) { check.Fail("the authored terrain preview is available"); return; }
            System.Numerics.Vector3[] preview = surface.Vertices.ToArray();
            check.That(page.RunWaypointRuleCheck() is { Available: true } && model.TerrainHasChanges && page.Save.Disabled && page.Play.Disabled &&
                model.TerrainPreviewSurface.Vertices.Span.SequenceEqual(preview) && page.Scripts.SourceText == draft,
                "a source-rule check preserves the terrain draft and cannot lift its export or play fences");
            typeof(GameLibrary).GetProperty(nameof(GameLibrary.Busy))!.SetValue(fixture.Game, true);
            page.Refresh();
            check.That(page.CheckWaypointRules.Disabled && page.RunWaypointRuleCheck() is null && !page.GoToWaypointRule(0) && page.Scripts.SourceText == draft,
                "a pending folder read refuses checks and old navigation without consuming source drafts");
            typeof(GameLibrary).GetProperty(nameof(GameLibrary.Busy))!.SetValue(fixture.Game, false);
            page.OpenLevel(400);
            check.That(page.CheckWaypointRules.Disabled && page.RunWaypointRuleCheck() is null, "an unavailable world cannot produce a successful page check");
            check.That(LevelEditorPageTests.Snapshot(fixture.GameRoot).SequenceEqual(filesBefore), "the complete authored game-shaped fixture stays untouched");
        }
        finally { await DisposeAsync(tree, fixture); }
    }
}
