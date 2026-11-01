// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Authored source files and typed text only: no installation, careers, publication or external action.</summary>
internal static class EditorProjectScriptsTests
{
    private static ScriptEntry[] Entries(WorldBody body) => [.. ScriptCatalog.Of(body).Select(summary => new ScriptEntry(summary, 130, false))];

    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("editor project script ownership");
        string root = Path.Combine(output, "project-script-fixture");
        string sources = Path.Combine(root, "data", "MissionScripts", "level130");
        Directory.CreateDirectory(sources);
        const string alpha = "// authored alpha\ninit()\n{\n}\n", beta = "// authored beta\n";
        File.WriteAllText(Path.Combine(sources, "alpha.msl"), alpha);
        File.WriteAllText(Path.Combine(sources, "beta.msl"), beta);
        WorldBody body = LevelScriptTests.Body(LevelScriptTests.Script("alpha", [0], []), LevelScriptTests.Script("beta", [], []));
        EditSession session = new(body.Write());
        ScriptEntry[] entries = Entries(body);
        Theme theme = CompanionTheme.Build();
        ScriptsPanel panel = new() { Theme = theme, Size = new Vector2(720, 520) };
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        tree.Root.AddChild(panel);
        try
        {
            panel.SetScripts(root, entries);
            panel.SetEditing(true);
            panel.Source.Text = "// alpha draft one\n";
            panel.Select("beta");
            panel.Source.Text = "// beta draft\n";
            IReadOnlyList<EditorProjectScript> captured = panel.CaptureProjectScripts(session, index => index == 0 ? "// compiled alpha\n" : null);
            check.That(captured.Count == 2 && captured[0].SourceText == alpha && captured[1].SourceText == beta &&
                       captured[0].DraftText == "// alpha draft one\n" && captured[1].DraftText == "// beta draft\n" &&
                       captured[0].UsedText == "// compiled alpha\n" && captured[0].UsedRecordHash == EditorProject.Hash(WorldBodyWriter.ScriptBytes(body.Scripts[0])),
                       "capture preserves both actual sources, the hidden and visible drafts, and a separate compiled-text claim");
            EditorProjectBase basis = new(130, false, -1, false, session.Baseline, session.Baseline, null, null);
            RestoredEditorProject restored = EditorProject.Restore(EditorProject.Capture(basis, session, null, captured), basis);
            check.That(panel.TryPrepareProjectScripts(entries, restored.Scripts, out PreparedScriptProject? stale, out _) && stale is not null,
                       "an import is staged without changing the current panel");
            panel.Source.Text = "// beta draft changed while already dirty\n";
            check.That(stale is not null && !panel.CommitProjectScripts(stale) && panel.SourceText.Contains("changed while already dirty", StringComparison.Ordinal),
                       "dirty-to-dirty typing invalidates a pending import without losing the newer text");
            EditorScriptDraftStamp beforeTyping = panel.CaptureDraftState();
            string beforeRoundTrip = panel.SourceText;
            panel.Source.Text = beforeRoundTrip + "// later typing\n";
            panel.Source.Text = beforeRoundTrip;
            check.That(!panel.MatchesDraftState(beforeTyping), "typing and returning to the same text still invalidates an earlier confirmation");
            EditorScriptDraftStamp discard = panel.CaptureDraftState();
            panel.Source.Text = "// beta draft after discard request\n";
            check.That(!panel.TryDiscardEdit("beta", discard) && panel.SourceText == "// beta draft after discard request\n" && panel.HasDraft("alpha"),
                       "a delayed discard cannot erase a newer visible draft or another script's hidden draft");
            EditorScriptDraftStamp exactDiscard = panel.CaptureDraftState();
            check.That(panel.TryDiscardEdit("beta", exactDiscard) && panel.SourceText == beta && !panel.HasDraft("beta") && panel.HasDraft("alpha"),
                       "an exact confirmed discard drops only the named draft");

            check.That(panel.TryPrepareProjectScripts(entries, restored.Scripts, out PreparedScriptProject? ready, out _) && ready is not null,
                       "the preserved script state prepares again at the new draft checkpoint");
            File.WriteAllText(Path.Combine(sources, "alpha.msl"), "// fixture source changed externally\n");
            check.That(ready is not null && panel.IsPreparedProjectCurrent(ready) && panel.CommitProjectScripts(ready),
                       "import restores its preserved source baseline without reading changed installed source text");
            panel.Select("alpha");
            check.That(panel.SourceText == "// alpha draft one\n" && panel.CurrentSource?.Source?.Text == alpha && panel.Info.Contains("project source", StringComparison.Ordinal),
                       "the restored alpha shows its draft and labels the original source preserved by the project");
            panel.Select("beta");
            check.That(panel.SourceText == "// beta draft\n" && panel.Editing && panel.UnusedDraftCount == 2,
                       "the second restored draft is editable and both unused drafts remain owned by the panel");
            IReadOnlyList<EditorProjectScript> capturedAgain = panel.CaptureProjectScripts(restored.Session);
            check.That(capturedAgain.Select(script => (script.Name, script.SourceText, script.DraftText)).SequenceEqual(
                           captured.Select(script => (script.Name, script.SourceText, script.DraftText))),
                       "a second capture preserves all restored source and draft text exactly");

            string before = panel.SourceText;
            EditorProjectScript[] collision = [captured[0], captured[1] with { Name = "ALPHA" }];
            check.That(!panel.TryPrepareProjectScripts(entries, collision, out _, out _) && panel.SourceText == before && panel.HasDraft("alpha"),
                       "a case-colliding import is refused without replacing existing dirty text");
            check.That(!panel.TryPrepareProjectScripts(entries, [captured[0] with { Index = 1 }], out _, out _) && panel.SourceText == before,
                       "a source bound to another record is refused before the panel changes");
            check.That(!panel.TryPrepareProjectScripts(entries, [captured[0] with { SourceText = "changed" }], out _, out _) && panel.SourceText == before,
                       "a stale source identity is refused before the panel changes");
            check.That(panel.TryPrepareProjectScripts(entries, captured, out PreparedScriptProject? switched, out _) && switched is not null,
                       "a pending import can be prepared before switching levels");
            panel.SetScripts(root, entries);
            check.That(switched is not null && !panel.CommitProjectScripts(switched), "switching the panel's level invalidates its pending import");

            ScriptEntry[] ambiguous = [entries[0], entries[0] with { Summary = entries[0].Summary with { Name = "ALPHA" } }];
            panel.SetScripts(root, ambiguous);
            panel.SetEditing(true);
            check.That(!panel.Editing, "source names that collide ignoring case cannot share an editable draft");
            panel.SetScripts(null, entries);
            bool missingRefused = false;
            try { panel.CaptureProjectScripts(session, index => index == 0 ? "// used source without a baseline\n" : null); }
            catch (InvalidDataException) { missingRefused = true; }
            check.That(missingRefused, "capture refuses used text without a source baseline instead of silently dropping it");
            check.That(panel.TryPrepareProjectScripts(entries, captured, out PreparedScriptProject? portable, out _) && portable is not null &&
                       panel.CommitProjectScripts(portable) && panel.SourceText == "// alpha draft one\n" && panel.Editing,
                       "preserved source and draft text reopen without a selected source directory");
        }
        finally
        {
            panel.QueueFree();
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            theme.Dispose();
        }
    }
}
