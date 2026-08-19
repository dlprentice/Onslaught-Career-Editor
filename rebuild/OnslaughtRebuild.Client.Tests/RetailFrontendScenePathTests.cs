// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// The player-visible cold-start path the Godot scene drives: Lost Toys /
/// opening FMV / splash skip, then CFEPIntro click-to-start, then CFEPMain.
/// Isolated helper pins already exist. These cases kill a path that only
/// those helpers know about, or a host that still uses
/// <c>ConfirmForSmoke</c> instead of the same accept owner.
/// </summary>
public sealed class RetailFrontendScenePathTests
{
    [Fact]
    public void SkipThenClickReachesCfepMainAndDoesNotConfirmDuringTheMovie()
    {
        var path = new RetailFrontendScenePath();
        var session = new RetailFrontendSession();
        path.Begin([]);

        Assert.True(path.StartupMediaActive);
        Assert.Equal(RetailFrontendScreen.ClickToStart, session.Screen);
        Assert.False(path.TryAcceptClickToStartMouse(session, 320f, 240f));
        Assert.Equal(RetailFrontendScreen.ClickToStart, session.Screen);

        Assert.False(path.TrySkipStartup(left: false, middle: false, right: false, dik: 0x1E));
        Assert.True(path.StartupMediaActive);
        Assert.True(path.TrySkipStartup(left: false, middle: false, right: false, dik: 0x39));
        Assert.False(path.StartupMediaActive);

        Assert.True(path.TryAcceptClickToStartMouse(session, 320f, 240f));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);
        Assert.Equal(RetailFrontendMenuItemKind.NewGame, session.SelectedMainItem.Kind);
    }

    [Fact]
    public void SkipfmvStartsOnClickToStartAndEnterReachesCfepMain()
    {
        var path = new RetailFrontendScenePath();
        var session = new RetailFrontendSession();
        path.Begin(["--skipfmv"]);

        Assert.False(path.StartupMediaActive);
        Assert.True(RetailFrontendScenePath.IsStartupSuppressed(["--skipfmv"]));
        Assert.False(RetailFrontendScenePath.IsStartupSuppressed([]));
        Assert.False(path.TrySkipStartup(left: true, middle: false, right: false, dik: 0));
        Assert.True(path.TryAcceptClickToStartKey(session, 0x1C));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);
    }

    [Fact]
    public void ClickToStartAcceptsOnlyTheSpecimenMouseAndKeys()
    {
        var path = new RetailFrontendScenePath();
        path.Begin(["--skipfmv"]);

        Assert.True(
            RetailFrontendScenePath.AcceptsClickToStartMouse(
                RetailFrontendScreen.ClickToStart,
                320f,
                240f));
        Assert.False(
            RetailFrontendScenePath.AcceptsClickToStartMouse(
                RetailFrontendScreen.MainMenu,
                320f,
                240f));
        Assert.True(
            RetailFrontendScenePath.AcceptsClickToStartKey(
                RetailFrontendScreen.ClickToStart,
                0x1C));
        Assert.True(
            RetailFrontendScenePath.AcceptsClickToStartKey(
                RetailFrontendScreen.ClickToStart,
                0x39));
        Assert.False(
            RetailFrontendScenePath.AcceptsClickToStartKey(
                RetailFrontendScreen.ClickToStart,
                0x9C));
        Assert.False(
            RetailFrontendScenePath.AcceptsClickToStartKey(
                RetailFrontendScreen.ClickToStart,
                0x01));

        var session = new RetailFrontendSession();
        Assert.False(path.TryAcceptClickToStartKey(session, 0x9C));
        Assert.Equal(RetailFrontendScreen.ClickToStart, session.Screen);
    }

    [Fact]
    public void FirstFlightGameAndFlowDriveThePathInsteadOfSmokeConfirm()
    {
        string game = ReadGodotSource("FirstFlightGame.cs");
        string flow = ReadGodotSource("RetailFrontendFlow.cs");
        string sequence = ReadGodotSource("RetailStartupSequence.cs");
        string startMedia = Slice(game, "private void StartRetailStartupMedia()");
        string pointer = Slice(flow, "private bool HandlePointerConfirm(");
        string key = Slice(flow, "private bool HandleKey(");
        string sequenceInput = Slice(sequence, "public override void _Input(");
        string clickArm = CaseArm(pointer, "case RetailFrontendScreen.ClickToStart:");

        Assert.Contains("RetailFrontendScenePath.IsStartupSuppressed", startMedia, StringComparison.Ordinal);
        Assert.Contains("RetailFrontendScenePath.AcceptsStartupSkip", sequenceInput, StringComparison.Ordinal);
        Assert.Contains("RetailFrontendScenePath.AcceptsClickToStartMouse", clickArm, StringComparison.Ordinal);
        Assert.Contains("RetailFrontendScenePath.AcceptsClickToStartKey", key, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", startMedia, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", pointer, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", key, StringComparison.Ordinal);
        Assert.Contains("RetailClickToStartSplash.Scale", flow, StringComparison.Ordinal);
        Assert.Contains("RetailClickToStartSlide.ShouldDraw", flow, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendScenePath", Slice(flow, "private void DrawClickToStart()"), StringComparison.Ordinal);
    }

    [Fact]
    public void MainMenuAcceptChangesCampaignOptionsAndExitPages()
    {
        var path = new RetailFrontendScenePath();
        var campaign = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(campaign, 0));
        Assert.Equal(RetailFrontendScreen.DevSelect, campaign.Screen);

        var options = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(options, 5));
        Assert.Equal(RetailFrontendScreen.Options, options.Screen);

        var exit = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(exit, 6));
        Assert.Equal(RetailFrontendScreen.QuitConfirm, exit.Screen);

        var continueGame = AfterClickToStart(path);
        Assert.False(path.TryAcceptMainMenuRow(continueGame, 1));
        Assert.Equal(RetailFrontendScreen.MainMenu, continueGame.Screen);
        Assert.False(path.TryAcceptMainMenuRow(continueGame, 2));
        Assert.Equal(RetailFrontendScreen.MainMenu, continueGame.Screen);
    }

    [Fact]
    public void FlowAcceptsMainMenuRowsThroughThePathAndDoesNotTreatLatchAsAccept()
    {
        string flow = ReadGodotSource("RetailFrontendFlow.cs");
        string pointer = Slice(flow, "private bool HandlePointerConfirm(");
        string mainArm = CaseArm(pointer, "case RetailFrontendScreen.MainMenu:");
        string options = ReadGodotSource("RetailFrontendFlow.Options.cs");
        string cancel = Slice(options, "private bool HandleOptionsPointerCancel");

        Assert.Contains("RetailFrontendScenePath.CanAcceptMainMenuRow", mainArm, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendLatchToButton", mainArm, StringComparison.Ordinal);
        Assert.Contains("RetailFrontendLatchToButton.Set", cancel, StringComparison.Ordinal);
    }

    private static RetailFrontendSession AfterClickToStart(RetailFrontendScenePath path)
    {
        var session = new RetailFrontendSession();
        path.Begin(["--skipfmv"]);
        Assert.True(path.TryAcceptClickToStartMouse(session, 320f, 240f));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);
        return session;
    }

    private static string ReadGodotSource(string fileName) =>
        File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", fileName));

    private static string Slice(string source, string signature)
    {
        int start = source.IndexOf(signature, StringComparison.Ordinal);
        Assert.True(start >= 0, signature);
        string rest = source[start..];
        int next = rest.IndexOf("\n    private ", signature.Length, StringComparison.Ordinal);
        if (next < 0)
        {
            next = rest.IndexOf("\n    public ", signature.Length, StringComparison.Ordinal);
        }

        return next >= 0 ? rest[..next] : rest;
    }

    private static string CaseArm(string handlePointerConfirm, string caseLabel)
    {
        int click = handlePointerConfirm.IndexOf(caseLabel, StringComparison.Ordinal);
        Assert.True(click >= 0, caseLabel);
        string arm = handlePointerConfirm[click..];
        int next = arm.IndexOf(
            "case RetailFrontendScreen.",
            caseLabel.Length,
            StringComparison.Ordinal);
        return next >= 0 ? arm[..next] : arm;
    }
}
