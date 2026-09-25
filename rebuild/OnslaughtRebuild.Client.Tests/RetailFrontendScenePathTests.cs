// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// The player-visible cold-start path the Godot scene drives: Lost Toys /
/// opening FMV / splash skip, then CFEPIntro click-to-start, then CFEPMain,
/// then Options apply pulse and dropdown confirm / right-click cancel,
/// then New Game campaign accept, campaign Back, QuitConfirm Yes/No,
/// then Loading → Gameplay (and the intro-cutscene handoff).
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
        string facade = ReadGodotSource("RetailFrontendFlow.cs");
        string sequence = ReadGodotSource("RetailStartupSequence.cs");
        string playback = ReadGodotSource("startup_sequence.gd");
        string startMedia = Slice(game, "private void StartRetailStartupMedia()");
        string pointer = NativeFrontendSource.RootFunction("handle_pointer_confirm");
        string key = NativeFrontendSource.RootFunction("handle_key");
        string clickArm = NativeFrontendSource.PointerArm("CLICK_TO_START");

        Assert.Contains("RetailFrontendScenePath.IsStartupSuppressed", startMedia, StringComparison.Ordinal);
        Assert.Contains("configure_from_cache", sequence, StringComparison.Ordinal);
        Assert.DoesNotContain("public override void _Input(", sequence, StringComparison.Ordinal);
        Assert.Contains("if not accepts_skip_event(event):", playback, StringComparison.Ordinal);
        Assert.Contains("Path.accepts_click_to_start_mouse(_session.get_screen(), design.x, design.y)", clickArm, StringComparison.Ordinal);
        Assert.Contains("Path.accepts_click_to_start_key(_session.get_screen(), scan_code_for(key))", key, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", startMedia, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", pointer, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", key, StringComparison.Ordinal);
        Assert.Contains("Laws.splash_scale(timer)", NativeClickSource.Controller, StringComparison.Ordinal);
        Assert.Contains("-Laws.slide_offset(timer)", NativeClickSource.Controller, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendScenePath", NativeClickSource.Presentation, StringComparison.Ordinal);
        Assert.Contains("_click.set_frame(", NativeClickSource.Bridge, StringComparison.Ordinal);
        Assert.DoesNotContain("private void DrawClickToStart()", facade, StringComparison.Ordinal);
        NativeClickSource.HasNoPresentationSideEffects();
    }

    [Fact]
    public void MainMenuAcceptChangesCampaignLoadOptionsAndExitPages()
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

        var loadGame = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(loadGame, 2));
        Assert.Equal(RetailFrontendScreen.DevSelect, loadGame.Screen);
        Assert.Equal(RetailFrontendCareerPageMode.Load, loadGame.CareerPageMode);
    }

    [Fact]
    public void FlowAcceptsMainMenuRowsThroughThePathAndDoesNotTreatLatchAsAccept()
    {
        string mainArm = NativeFrontendSource.PointerArm("MAIN_MENU");
        string cancel = NativeFrontendSource.RootFunction("cancel_options");
        Assert.Contains("Path.can_accept_main_menu_row(_session, index)", mainArm, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendLatchToButton", mainArm, StringComparison.Ordinal);
        Assert.Contains("_options_view.pointer_cancel(true)", cancel, StringComparison.Ordinal);
        Assert.Contains("Laws.cancel_applies(false, right_down)", NativeOptionsSource.Function("options_controller.gd", "pointer_cancel"), StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendLatchToButton.Set", mainArm, StringComparison.Ordinal);
    }

    [Fact]
    public void OptionsDeferredDropdownPulsesApplyUntilApplyAndRightClickCancels()
    {
        var path = new RetailFrontendScenePath();
        var session = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(session, 5));
        Assert.Equal(RetailFrontendScreen.Options, session.Screen);

        var menu = new RetailOptionsMenu();
        menu.Enter(RetailOptionsPage.Sound);
        int soundQuality = IndexOfLabel(menu, "Sound quality:");
        Assert.Equal(RetailOptionsApplyTiming.OnApply, menu.Rows[soundQuality].Timing);
        Assert.True(menu.Hover(soundQuality));
        Assert.True(path.TryConfirmOptions(menu, out RetailOptionsSignal expand));
        Assert.Equal(RetailOptionsSignal.ValueChanged, expand);
        Assert.True(menu.IsExpanded);

        int committed = menu.SelectedRow.CommittedIndex;
        int other = committed == 0 ? 1 : 0;
        Assert.True(menu.SelectState(other));
        Assert.True(path.TryConfirmOptions(menu, out RetailOptionsSignal closed));
        Assert.Equal(RetailOptionsSignal.ValueChanged, closed);
        Assert.False(menu.IsExpanded);
        Assert.Equal(other, menu.Rows[soundQuality].CurrentIndex);
        Assert.Equal(committed, menu.Rows[soundQuality].CommittedIndex);
        Assert.Equal(0, menu.Settings.SoundQuality);
        Assert.True(RetailFrontendScenePath.ApplyPulseIsPending(menu));
        Assert.True(
            RetailOptionsApplyPulse.DropdownRowIsPending(
                menu.Rows[soundQuality].CommittedIndex,
                menu.Rows[soundQuality].CurrentIndex));
        Assert.NotEqual(
            RetailOptionsApplyPulse.IdlePackedColor,
            RetailOptionsApplyPulse.PackedColor(
                RetailFrontendScenePath.ApplyPulseIsPending(menu),
                0f));

        int apply = IndexOfLabel(menu, "Apply");
        Assert.True(menu.Hover(apply));
        Assert.True(path.TryConfirmOptions(menu, out RetailOptionsSignal applied));
        Assert.Equal(RetailOptionsSignal.Applied, applied);
        Assert.False(RetailFrontendScenePath.ApplyPulseIsPending(menu));
        Assert.Equal(other, menu.Settings.SoundQuality);

        Assert.True(menu.Hover(soundQuality));
        Assert.True(path.TryConfirmOptions(menu, out _));
        int next = menu.SelectedRow.CurrentIndex == 0 ? 1 : 0;
        Assert.True(menu.SelectState(next));
        Assert.False(path.TryCancelOptionsDropdown(menu, rightDown: false));
        Assert.True(menu.IsExpanded);
        Assert.True(path.TryCancelOptionsDropdown(menu, rightDown: true));
        Assert.False(menu.IsExpanded);
        Assert.Equal(other, menu.SelectedRow.CurrentIndex);
        Assert.False(RetailFrontendScenePath.AcceptsOptionsPointerCancel(rightDown: false));
        Assert.True(RetailFrontendScenePath.AcceptsOptionsPointerCancel(rightDown: true));
    }

    [Fact]
    public void FlowDrivesOptionsApplyConfirmAndRightClickCancelFromThePath()
    {
        string input = NativeFrontendSource.RootFunction("handle_input");
        string confirm = NativeFrontendSource.RootFunction("confirm_options");
        string cancel = NativeFrontendSource.RootFunction("cancel_options");
        string draw = NativeOptionsSource.Function("options_row.gd", "update_time");
        string pointerCancel = NativeFrontendSource.RootFunction("handle_pointer_cancel");
        Assert.Contains("MOUSE_BUTTON_RIGHT", input, StringComparison.Ordinal);
        Assert.Contains("handle_pointer_cancel()", input, StringComparison.Ordinal);
        Assert.Contains("_options_view.handle_key(false, false, false, false, true, false)", confirm, StringComparison.Ordinal);
        Assert.Contains("_menu.confirm()", NativeOptionsSource.Function("options_controller.gd", "_confirm"), StringComparison.Ordinal);
        Assert.Contains("_options_view.pointer_cancel(true)", cancel, StringComparison.Ordinal);
        Assert.Contains("Laws.cancel_applies(false, right_down)", NativeOptionsSource.Function("options_controller.gd", "pointer_cancel"), StringComparison.Ordinal);
        Assert.Contains("cancel_options() if _session.get_screen() == Frontend.Screen.OPTIONS", pointerCancel, StringComparison.Ordinal);
        Assert.Contains("Laws.pulse_packed_color", draw, StringComparison.Ordinal);
        Assert.Contains("Laws.dropdown_row_is_pending", draw, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendScenePath", draw, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", confirm, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendLatchToButton", NativeFrontendSource.RootFunction("handle_pointer_confirm"), StringComparison.Ordinal);
    }

    [Fact]
    public void NewGameAcceptWalksToLevel100LaunchThroughThePath()
    {
        var path = new RetailFrontendScenePath();
        var session = AfterClickToStart(path);

        Assert.False(path.TryAcceptDevSelect(session));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);

        Assert.True(path.TryAcceptMainMenuRow(session, 0));
        Assert.Equal(RetailFrontendScreen.DevSelect, session.Screen);
        Assert.Equal(RetailFrontendSession.DefaultGameName, session.GameName);

        Assert.True(path.TryAcceptDevSelect(session));
        Assert.Equal(RetailFrontendScreen.LevelSelect, session.Screen);
        Assert.False(session.ConsumeLevel100LaunchRequest());

        Assert.True(path.TryAcceptLevelSelect(session));
        Assert.Equal(RetailFrontendScreen.MissionBriefing, session.Screen);

        Assert.True(path.TryAcceptMissionBriefing(session));
        Assert.Equal(RetailFrontendScreen.SelectConfiguration, session.Screen);

        Assert.True(path.TryAcceptSelectConfiguration(session, out RetailFrontendSignal launch));
        Assert.Equal(RetailFrontendSignal.LevelLaunchRequested, launch);
        Assert.Equal(RetailFrontendScreen.Loading, session.Screen);
        Assert.True(session.ConsumeLevel100LaunchRequest());

        Assert.False(path.TryAcceptDevSelect(session));
        Assert.False(path.TryAcceptLevelSelect(session));
        Assert.False(path.TryAcceptMissionBriefing(session));
        Assert.False(path.TryAcceptSelectConfiguration(session, out RetailFrontendSignal idle));
        Assert.Equal(RetailFrontendSignal.None, idle);
    }

    [Fact]
    public void StartupMediaBlocksCampaignAcceptUntilSkip()
    {
        var path = new RetailFrontendScenePath();
        var session = new RetailFrontendSession();
        path.Begin([]);
        session.Confirm();
        session.Confirm();
        Assert.Equal(RetailFrontendScreen.DevSelect, session.Screen);
        Assert.True(path.StartupMediaActive);

        Assert.False(path.TryAcceptDevSelect(session));
        Assert.Equal(RetailFrontendScreen.DevSelect, session.Screen);

        Assert.True(path.TrySkipStartup(left: true, middle: false, right: false, dik: 0));
        Assert.True(path.TryAcceptDevSelect(session));
        Assert.Equal(RetailFrontendScreen.LevelSelect, session.Screen);
    }

    [Fact]
    public void QuitConfirmYesExitsAndNoReturnsToMainMenu()
    {
        var path = new RetailFrontendScenePath();
        var no = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(no, 6));
        Assert.Equal(RetailFrontendScreen.QuitConfirm, no.Screen);
        Assert.Equal(0, no.SelectedQuitConfirmIndex);
        Assert.True(path.TryAcceptQuitConfirm(no, out RetailFrontendSignal cancelled));
        Assert.Equal(RetailFrontendSignal.PageChanged, cancelled);
        Assert.Equal(RetailFrontendScreen.MainMenu, no.Screen);

        var yes = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(yes, 6));
        Assert.True(yes.SelectQuitConfirmIndex(1));
        Assert.True(path.TryAcceptQuitConfirm(yes, out RetailFrontendSignal exit));
        Assert.Equal(RetailFrontendSignal.ExitRequested, exit);
        Assert.Equal(RetailFrontendScreen.QuitConfirm, yes.Screen);
    }

    [Fact]
    public void FlowConfirmsCampaignAndQuitThroughThePath()
    {
        string confirm = NativeFrontendSource.RootFunction("confirm");
        string key = NativeFrontendSource.RootFunction("handle_key");
        string devArm = NativeFrontendSource.PointerArm("DEV_SELECT");
        string debriefingArm = NativeFrontendSource.PointerArm("DEBRIEFING");
        string levelArm = NativeFrontendSource.PointerArm("LEVEL_SELECT");
        string configArm = NativeFrontendSource.PointerArm("SELECT_CONFIGURATION");
        string quitArm = NativeFrontendSource.PointerArm("QUIT_CONFIRM");
        Assert.Contains("Path.try_confirm_page(_session, false)", confirm, StringComparison.Ordinal);
        Assert.DoesNotContain("_session.confirm()", confirm, StringComparison.Ordinal);
        Assert.Contains("_confirm_page_target(career_name_target_at(design))", devArm, StringComparison.Ordinal);
        Assert.Contains("_handled(confirm())", debriefingArm, StringComparison.Ordinal);
        Assert.Contains("Rect2(0, 0, 640, 480).has_point(design)", debriefingArm, StringComparison.Ordinal);
        Assert.DoesNotContain("try_back_page", debriefingArm, StringComparison.Ordinal);
        Assert.Contains("_handled(confirm())", levelArm, StringComparison.Ordinal);
        Assert.Contains("_confirm_page_target(configuration_target_at(design))", configArm, StringComparison.Ordinal);
        Assert.Contains("_select_then_confirm(_session.select_quit_confirm_index(choice))", quitArm, StringComparison.Ordinal);
        Assert.Contains("_handled(confirm())", NativeFrontendSource.RootFunction("_select_then_confirm"), StringComparison.Ordinal);
        Assert.Contains("_handled(confirm()) if target == 2", NativeFrontendSource.RootFunction("_confirm_page_target"), StringComparison.Ordinal);
        Assert.Contains("_handled(confirm())", key, StringComparison.Ordinal);
        Assert.DoesNotContain("ConfirmForSmoke", confirm, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailFrontendLatchToButton", confirm, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailLevelSelectLater", confirm, StringComparison.Ordinal);
    }

    [Fact]
    public void WonHandoff_DebriefingConfirmAndBackUseTheCentralPagePath()
    {
        var path = new RetailFrontendScenePath();

        RetailFrontendSession confirm = AtDebriefing(path);
        Assert.True(RetailFrontendScenePath.TryConfirmPage(
            confirm,
            startupMediaActive: false,
            out RetailFrontendSignal confirmSignal));
        Assert.Equal(RetailFrontendSignal.PageChanged, confirmSignal);
        Assert.Equal(RetailFrontendScreen.LevelSelect, confirm.Screen);

        RetailFrontendSession back = AtDebriefing(path);
        Assert.True(RetailFrontendScenePath.TryBackPage(
            back,
            startupMediaActive: false,
            out RetailFrontendSignal backSignal));
        Assert.Equal(RetailFrontendSignal.PageChanged, backSignal);
        Assert.Equal(RetailFrontendScreen.LevelSelect, back.Screen);
    }

    [Fact]
    public void DebriefingDrawUsesWritingChromeAndNoPageChevrons()
    {
        string flow = ReadGodotSource("RetailFrontendFlow.cs");
        string sourceRoot = Path.Combine(AppContext.BaseDirectory, "godot-debriefing-source");
        string reference = File.ReadAllText(Path.Combine(sourceRoot, "DebriefingReference.cs"));
        string scene = File.ReadAllText(Path.Combine(sourceRoot, "Debriefing.tscn"));
        string presenter = File.ReadAllText(Path.Combine(sourceRoot, "debriefing_presentation.gd"));
        string draw = Slice(reference, "private void DrawDebriefing(");
        string chrome = Slice(reference, "private void DrawDebriefingWritingChrome(");
        string debriefingLoads = Slice(reference, "private void LoadTextures(");

        Assert.DoesNotContain("private void DrawDebriefing(", flow, StringComparison.Ordinal);
        Assert.Contains("DrawDebriefingWritingChrome();", draw, StringComparison.Ordinal);
        Assert.DoesNotContain("DrawBriefingStage", draw, StringComparison.Ordinal);
        Assert.DoesNotContain("DrawPageChevrons", draw, StringComparison.Ordinal);
        Assert.Contains("_forsetiWritingLarge", chrome, StringComparison.Ordinal);
        Assert.Contains("index < 4", chrome, StringComparison.Ordinal);
        Assert.Contains(
            "RetailColor(0xfeffffff)",
            reference,
            StringComparison.Ordinal);
        Assert.Equal(
            2,
            draw.Split("DebriefingGradeBodyTint", StringSplitOptions.None).Length - 1);
        Assert.Equal(
            7,
            debriefingLoads.Split(
                "LegacyCuratedAyaTextureReference.Compression.Dxt2",
                StringSplitOptions.None).Length - 1);
        Assert.DoesNotContain(
            "LegacyCuratedAyaTextureReference.Compression.Rgba8",
            debriefingLoads,
            StringComparison.Ordinal);
        Assert.Contains("unmeasured score/time", reference, StringComparison.Ordinal);
        Assert.Contains("entry/exit interpolation", reference, StringComparison.Ordinal);
        Assert.Contains("delayed grade glint", reference, StringComparison.Ordinal);
        Assert.Contains("_modulate2x", presenter, StringComparison.Ordinal);
        Assert.Contains("Math.Min(255u, (channel * 255u) >> 7) / 255f", reference, StringComparison.Ordinal);
        Assert.DoesNotContain("Chevrons", scene, StringComparison.Ordinal);
        Assert.DoesNotContain("BriefingStage", scene, StringComparison.Ordinal);
        for (int index = 0; index < 4; index++)
            Assert.Contains($"[node name=\"Tile{index}\" type=\"TextureRect\" parent=\"Writing\"]", scene, StringComparison.Ordinal);
        Assert.Equal(2, scene.Split("self_modulate = Color(1, 1, 1, 0.9960784316062927)", StringSplitOptions.None).Length - 1);
        foreach (string name in new[] { "MetalRing", "GradeA", "GradeB", "GradeC", "GradeD", "GradeE", "GradeS" })
        {
            string recipe = File.ReadAllText(Path.Combine(sourceRoot, $"Debriefing{name}.tres"));
            Assert.Contains("compression = 1", recipe, StringComparison.Ordinal);
            Assert.DoesNotContain("compression = 2", recipe, StringComparison.Ordinal);
        }
    }

    [Fact]
    public void CampaignBackWalksHomeThroughThePath()
    {
        var path = new RetailFrontendScenePath();
        var session = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(session, 0));
        Assert.True(path.TryAcceptDevSelect(session));
        Assert.True(path.TryAcceptLevelSelect(session));
        Assert.True(path.TryAcceptMissionBriefing(session));
        Assert.Equal(RetailFrontendScreen.SelectConfiguration, session.Screen);

        Assert.True(path.TryBack(session));
        Assert.Equal(RetailFrontendScreen.MissionBriefing, session.Screen);
        Assert.True(path.TryBack(session));
        Assert.Equal(RetailFrontendScreen.LevelSelect, session.Screen);
        Assert.True(path.TryBack(session));
        Assert.Equal(RetailFrontendScreen.DevSelect, session.Screen);
        Assert.True(path.TryBack(session));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);
        Assert.False(path.TryBack(session));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);
    }

    [Fact]
    public void StartupMediaBlocksCampaignBackUntilSkip()
    {
        var path = new RetailFrontendScenePath();
        var session = new RetailFrontendSession();
        path.Begin([]);
        session.Confirm();
        session.Confirm();
        Assert.Equal(RetailFrontendScreen.DevSelect, session.Screen);
        Assert.True(path.StartupMediaActive);
        Assert.False(path.TryBack(session));
        Assert.Equal(RetailFrontendScreen.DevSelect, session.Screen);

        Assert.True(path.TrySkipStartup(left: true, middle: false, right: false, dik: 0));
        Assert.True(path.TryBack(session));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);
    }

    [Fact]
    public void LoadingCompleteWalksToGameplayThroughThePath()
    {
        var path = new RetailFrontendScenePath();
        var session = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(session, 0));
        Assert.True(path.TryAcceptDevSelect(session));
        Assert.True(path.TryAcceptLevelSelect(session));
        Assert.True(path.TryAcceptMissionBriefing(session));
        Assert.True(path.TryAcceptSelectConfiguration(session, out _));
        Assert.Equal(RetailFrontendScreen.Loading, session.Screen);

        Assert.False(path.TryCompleteLoading(session, launchConsumed: false));
        Assert.Equal(RetailFrontendScreen.Loading, session.Screen);
        Assert.True(session.ConsumeLevel100LaunchRequest());
        Assert.True(path.TryCompleteLoading(session, launchConsumed: true));
        Assert.Equal(RetailFrontendScreen.Gameplay, session.Screen);
        Assert.False(path.TryCompleteLoading(session, launchConsumed: true));
        Assert.Equal(RetailFrontendScreen.Gameplay, session.Screen);
    }

    [Fact]
    public void StartupMediaBlocksLoadingCompleteUntilSkip()
    {
        var path = new RetailFrontendScenePath();
        var session = new RetailFrontendSession();
        path.Begin([]);
        session.Confirm();
        session.Confirm();
        session.Confirm();
        session.Confirm();
        session.Confirm();
        session.Confirm();
        Assert.Equal(RetailFrontendScreen.Loading, session.Screen);
        Assert.True(session.ConsumeLevel100LaunchRequest());
        Assert.True(path.StartupMediaActive);
        Assert.False(path.TryCompleteLoading(session, launchConsumed: true));
        Assert.Equal(RetailFrontendScreen.Loading, session.Screen);

        Assert.True(path.TrySkipStartup(left: true, middle: false, right: false, dik: 0));
        Assert.True(path.TryCompleteLoading(session, launchConsumed: true));
        Assert.Equal(RetailFrontendScreen.Gameplay, session.Screen);
    }

    [Fact]
    public void FlowCompletesLoadingThroughThePath()
    {
        string process = NativeFrontendSource.RootFunction("advance");
        string finish = NativeFrontendSource.RootFunction("finish_level100_intro_cutscene");
        Assert.Contains("Path.try_complete_loading(_session, false, _load_request_raised)", process, StringComparison.Ordinal);
        Assert.DoesNotContain("_session.complete_level100_load()", process, StringComparison.Ordinal);
        Assert.Contains("Path.try_complete_intro_cutscene(_session, false)", finish, StringComparison.Ordinal);
        Assert.DoesNotContain("_session.complete_level100_intro_cutscene()", finish, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailLevelSelectLater", process, StringComparison.Ordinal);
    }

    [Fact]
    public void IntroCutsceneCompleteWalksToGameplayThroughThePath()
    {
        var path = new RetailFrontendScenePath();
        var session = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(session, 0));
        Assert.True(path.TryAcceptDevSelect(session));
        Assert.True(path.TryAcceptLevelSelect(session));
        Assert.True(path.TryAcceptMissionBriefing(session));
        Assert.True(path.TryAcceptSelectConfiguration(session, out _));
        Assert.True(session.ConsumeLevel100LaunchRequest());
        session.BeginLevel100IntroCutscene();
        Assert.Equal(RetailFrontendScreen.IntroCutscene, session.Screen);

        Assert.False(path.TryCompleteLoading(session, launchConsumed: true));
        Assert.Equal(RetailFrontendScreen.IntroCutscene, session.Screen);
        Assert.True(path.TryCompleteIntroCutscene(session));
        Assert.Equal(RetailFrontendScreen.Gameplay, session.Screen);
        Assert.False(path.TryCompleteIntroCutscene(session));
    }

    [Fact]
    public void FlowDrivesCampaignBackFromThePath()
    {
        string pointer = NativeFrontendSource.RootFunction("handle_pointer_confirm");
        string key = NativeFrontendSource.RootFunction("handle_key");
        string back = NativeFrontendSource.RootFunction("_back_page");
        string pageTarget = NativeFrontendSource.RootFunction("_confirm_page_target");
        string backFromOptions = NativeFrontendSource.RootFunction("_dispatch_options_effect");
        Assert.Contains("Path.try_back_page(_session, false)", back, StringComparison.Ordinal);
        Assert.Contains("_back_page()", key, StringComparison.Ordinal);
        Assert.Contains("if target == 1: return _back_page()", pageTarget, StringComparison.Ordinal);
        foreach (string screen in new[] { "DEV_SELECT", "LEVEL_SELECT", "SELECT_CONFIGURATION" })
            Assert.Contains("_confirm_page_target(", NativeFrontendSource.PointerArm(screen), StringComparison.Ordinal);
        Assert.Contains("\"frontend_back\": return _back_page()", backFromOptions, StringComparison.Ordinal);
        Assert.DoesNotContain("_session.back()", key, StringComparison.Ordinal);
        Assert.DoesNotContain("_session.back()", pointer, StringComparison.Ordinal);
        Assert.DoesNotContain("_session.back()", backFromOptions, StringComparison.Ordinal);
        Assert.DoesNotContain("RetailLevelSelectLater", key, StringComparison.Ordinal);
    }

    private static RetailFrontendSession AfterClickToStart(RetailFrontendScenePath path)
    {
        var session = new RetailFrontendSession();
        path.Begin(["--skipfmv"]);
        Assert.True(path.TryAcceptClickToStartMouse(session, 320f, 240f));
        Assert.Equal(RetailFrontendScreen.MainMenu, session.Screen);
        return session;
    }

    private static RetailFrontendSession AtDebriefing(RetailFrontendScenePath path)
    {
        RetailFrontendSession session = AfterClickToStart(path);
        Assert.True(path.TryAcceptMainMenuRow(session, 0));
        Assert.True(path.TryAcceptDevSelect(session));
        Assert.True(path.TryAcceptLevelSelect(session));
        Assert.True(path.TryAcceptMissionBriefing(session));
        Assert.True(path.TryAcceptSelectConfiguration(session, out _));
        Assert.True(session.ConsumeLevel100LaunchRequest());
        Assert.True(path.TryCompleteLoading(session, launchConsumed: true));
        Assert.True(RetailFrontendScenePath.TryAcceptWonHandoff(
            session,
            Level100MissionOutcome.Won,
            Level100MissionTerminalState.FrontEndHandoffReady));
        Assert.Equal(RetailFrontendScreen.Debriefing, session.Screen);
        return session;
    }

    private static int IndexOfLabel(RetailOptionsMenu menu, string label)
    {
        for (int i = 0; i < menu.Rows.Count; i++)
        {
            if (string.Equals(menu.Rows[i].Label, label, StringComparison.Ordinal))
            {
                return i;
            }
        }

        Assert.Fail(label);
        return -1;
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

    private static string SliceUntil(string source, string signature, string endSignature)
    {
        int start = source.IndexOf(signature, StringComparison.Ordinal);
        Assert.True(start >= 0, signature);
        string rest = source[start..];
        int next = rest.IndexOf(endSignature, signature.Length, StringComparison.Ordinal);
        return next >= 0 ? rest[..next] : rest;
    }
}
