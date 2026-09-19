// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

/// <summary>Temporary oracle for the actual frontend state machine. The caller
/// supplies the existing tracked gold save unchanged. No file access, save
/// synthesis, retail payload extraction or new gameplay expectation lives here.</summary>
public static class GdscriptFrontendSessionOracle
{
    public static object Build(byte[] goldCareerContainer)
    {
        RetailCareerSave gold = RetailCareerSaveCodec.Read(goldCareerContainer);
        var constructors = new List<object>();
        void Constructor(string name, RetailCareerDescriptor[]? descriptors) => constructors.Add(new
        { name, descriptors = Descriptors(descriptors), expected = Capture(() => State(new RetailFrontendSession(descriptors))) });
        Constructor("null-default", null); Constructor("empty", []);
        Constructor("null-descriptor", [null!]);
        Constructor("later-null-descriptor", [new(1, "FIRST", gold), null!]);
        Constructor("null-name-is-admitted", [new(null, null!, gold)]);
        Constructor("null-career-is-admitted", [new(int.MinValue, "NO CAREER", null!)]);
        Constructor("int32-slots-and-order", [new(int.MaxValue, "FIRST", gold), new(int.MinValue, "SECOND", gold)]);

        var scenarios = new List<object>();
        for (int item = 0; item < 7; item++)
        {
            var s = new Scenario("main-item:" + item);
            s.Do("back"); s.Do("confirm");
            s.Do("select_main", int.MinValue); s.Do("select_main", 7);
            s.Do("select_main", item); s.Do("select_main", item);
            s.Do("confirm"); s.Do("append", 'A', 0);
            if (item == 6)
            {
                s.Do("select_quit", -1); s.Do("select_quit", 2); s.Do("previous");
                s.Do("next"); s.Do("next"); s.Do("confirm"); s.Do("back");
                s.Do("confirm"); s.Do("confirm"); s.Do("confirm");
                s.Do("select_quit", 1); s.Do("select_quit", 1); s.Do("previous");
            }
            s.Do("back"); s.Do("consume_launch"); s.Do("consume_career");
            scenarios.Add(s.Output());
        }
        var bounds = new Scenario("main-selection-bounds-and-unavailable-latch");
        bounds.Do("confirm"); bounds.Do("previous");
        for (int i = 0; i < 9; i++) bounds.Do("next");
        for (int i = 0; i < 9; i++) bounds.Do("previous");
        bounds.Do("select_main", 1); bounds.Do("confirm");
        bounds.Do("select_main", 1); bounds.Do("select_main", -1); bounds.Do("cursor", 1);
        bounds.Do("consume_launch"); bounds.Do("back"); bounds.Do("confirm"); bounds.Do("next");
        scenarios.Add(bounds.Output());

        foreach (bool intro in new[] { false, true })
        {
            var s = new Scenario("loading-intro-retry-exit:" + intro);
            s.ToLoading(); s.Do("complete_load"); s.Do("begin_intro"); s.Do("return_unconstructible");
            s.Do("consume_launch"); s.Do("consume_launch");
            if (intro) { s.Do("begin_intro"); s.Do("begin_intro"); s.Do("complete_load"); s.Do("complete_intro"); }
            else s.Do("complete_load");
            s.Do("restart"); s.Do("complete_load"); s.Do("consume_launch");
            s.Do("begin_intro"); s.Do("complete_intro"); s.Do("complete_load");
            s.Do("leave"); s.ToLoading(fromMain: true); s.Do("consume_launch");
            s.Do("begin_intro"); s.Do("complete_intro"); s.Do("leave");
            scenarios.Add(s.Output());
        }
        var backchain = new Scenario("back-chain-and-one-configuration");
        backchain.ToConfiguration(); backchain.Do("previous"); backchain.Do("next");
        foreach (int i in new[] { int.MinValue, -1, 0, 1, int.MaxValue }) backchain.Do("select_configuration", i);
        for (int i = 0; i < 5; i++) backchain.Do("back");
        scenarios.Add(backchain.Output());

        foreach (int screen in Enumerable.Range(0, 12))
        {
            var s = new Scenario("state-admission:" + screen);
            s.ToScreen((RetailFrontendScreen)screen);
            s.Do("select_world", int.MinValue); s.Do("select_world", 100); s.Do("select_world", 110);
            s.Do("select_configuration", int.MaxValue); s.Do("select_career", -1);
            s.Do("select_main", 7); s.Do("select_quit", 2);
            s.Do("complete_intro"); s.Do("complete_load"); s.Do("begin_intro");
            s.Do("won", 2, 2); s.Do("won", 1, 1); s.Do("won", -1, int.MinValue);
            s.Do("remove"); s.Do("cursor", 0); s.Do("return_unconstructible");
            s.Do("consume_career"); s.Do("consume_launch");
            scenarios.Add(s.Output());
        }

        var wonRoute = new Scenario("won-debrief-unlock-and-repeated-entry");
        wonRoute.ToGameplay(); wonRoute.Do("won", 1, 2); wonRoute.Do("won", 1, 2);
        wonRoute.Do("select_world", 110); wonRoute.Do("confirm"); wonRoute.Do("select_world", 110);
        wonRoute.Do("confirm"); wonRoute.Do("confirm"); wonRoute.Do("confirm");
        wonRoute.Do("return_unconstructible"); wonRoute.Do("consume_launch"); wonRoute.Do("return_unconstructible");
        wonRoute.Do("select_world", 200); wonRoute.Do("select_world", 100);
        wonRoute.Do("confirm"); wonRoute.Do("confirm"); wonRoute.Do("confirm");
        wonRoute.Do("consume_launch"); wonRoute.Do("complete_load"); wonRoute.Do("won", 1, 2);
        wonRoute.Do("back"); wonRoute.Do("select_world", 110);
        wonRoute.Do("confirm"); wonRoute.Do("confirm"); wonRoute.Do("confirm");
        wonRoute.Do("consume_launch"); wonRoute.Do("complete_load"); wonRoute.Do("leave");
        // Leaving does not reset SelectedWorldNumber; choosing New Game does.
        wonRoute.Do("select_main", 2); wonRoute.Do("confirm"); wonRoute.Do("back");
        wonRoute.Do("select_main", 0); wonRoute.Do("confirm");
        scenarios.Add(wonRoute.Output());

        var editedCareer = new Scenario("won-on-mutated-public-career");
        editedCareer.ToGameplay(); editedCareer.Do("node_world", 1, 999);
        editedCareer.Do("won", 1, 2); // 0/8 reward writes precede absent110 failure.
        editedCareer.Do("node_world", 1, 110); editedCareer.Do("node_complete", 1, 1);
        editedCareer.Do("node_rank", 1, unchecked((int)0x3e800000));
        editedCareer.Do("won", 1, 2); editedCareer.Do("back");
        scenarios.Add(editedCareer.Output());

        var selectionOrder = new Scenario("selection-query-precedes-page-check");
        selectionOrder.Do("append_null_link"); selectionOrder.Do("select_world", 999);
        selectionOrder.Do("select_world", 100); selectionOrder.Do("select_world", 110);
        selectionOrder.Do("confirm"); selectionOrder.Do("select_world", 200);
        scenarios.Add(selectionOrder.Output());

        var load = new Scenario("loaded-career-order-unavailable-and-once-request",
            [new(9, "SECOND SLOT", gold), new(2, "FIRST SLOT", gold)]);
        load.ToLoadPage(); load.Do("confirm"); load.Do("previous");
        load.Do("next"); load.Do("next"); load.Do("next");
        load.Do("append", 'X'); load.Do("cursor", 0); load.Do("remove");
        load.Do("confirm"); load.Do("consume_career"); load.Do("consume_career");
        foreach (int world in RetailWorldCatalog.Nodes.Select(n => n.WorldNumber).Concat([999, -1])) load.Do("select_world", world);
        load.Do("back"); load.Do("previous"); load.Do("confirm"); load.Do("consume_career");
        load.Do("back"); load.Do("back"); load.Do("consume_career");
        scenarios.Add(load.Output());

        var newSelected = new Scenario("new-name-row-does-not-activate-loaded-career", [new(null, "MY CAREER", gold)]);
        newSelected.Do("confirm"); newSelected.Do("confirm"); newSelected.Do("select_career", 0);
        newSelected.Do("append", 'A', int.MaxValue); newSelected.Do("confirm");
        newSelected.Do("select_world", 800); newSelected.Do("consume_career");
        scenarios.Add(newSelected.Output());

        foreach (string name in new[] { "", "A\0B", "\uFEFFname", "🚀X", "\uD800X", "Y\uDC00", new string('a', 28) + "🚀b", new string('x', 40) })
        {
            var s = new Scenario("UTF16-name:" + string.Join('-', name.Select(c => ((int)c).ToString("X4"))), [new(0, name, gold)]);
            s.Do("confirm"); s.Do("confirm"); s.Do("select_career", 0);
            s.Do("append", 'A', int.MaxValue); s.Do("cursor", 0); s.Do("remove");
            s.Do("append", '’', -1); s.Do("cursor", 0); s.Do("remove");
            s.Do("select_career", 0); s.Do("back");
            scenarios.Add(s.Output());
        }

        var edits = new Scenario("name-cursor-width-length-and-remap");
        edits.Do("append", 'A'); edits.Do("confirm"); edits.Do("confirm");
        edits.Do("append", '\n'); edits.Do("append", 'A', int.MaxValue);
        edits.Do("append", 'C', 383); edits.Do("cursor", 0); edits.Do("append", 'B', -1);
        edits.Do("remove"); edits.Do("append", 'X', 384); edits.Do("append", '–', int.MinValue);
        for (int i = 0; i < 35; i++) edits.Do("append", 'x');
        for (int i = 0; i < 36; i++) edits.Do("cursor", 0);
        edits.Do("remove");
        for (int i = 0; i < 36; i++) edits.Do("cursor", 1);
        for (int i = 0; i < 36; i++) edits.Do("remove");
        scenarios.Add(edits.Output());

        foreach (bool endFresh in new[] { false, true })
        {
            var s = new Scenario("null-name-partial-mutation:" + endFresh, [new(0, null!, gold)]);
            s.Do("confirm"); s.Do("confirm"); if (endFresh) s.Do("cursor", 0);
            s.Do("select_career", 0); s.Do("append", '\n'); s.Do("append", 'A');
            if (endFresh) { s.Do("remove"); s.Do("cursor", 1); s.Do("remove"); }
            else { s.Do("remove"); s.Do("append", 'A'); }
            s.Do("select_career", 0); s.Do("back");
            scenarios.Add(s.Output());
        }
        var nullCareer = new Scenario("null-career-request-mutation-before-error", [new(null, "BROKEN", null!)]);
        nullCareer.ToLoadPage(); nullCareer.Do("next"); nullCareer.Do("confirm");
        nullCareer.Do("consume_career"); nullCareer.Do("consume_career");
        nullCareer.Do("select_world", 100); nullCareer.Do("back"); nullCareer.Do("select_world", 110);
        scenarios.Add(nullCareer.Output());

        var seedCase = new Scenario("case-sensitive-name-seed", [new(0, "BEA 1", gold), new(1, "bea 2", gold), new(2, "BEA 3", gold)]);
        seedCase.Do("confirm"); seedCase.Do("confirm"); scenarios.Add(seedCase.Output());
        var seedCap = new Scenario("unchecked-name-seed-cap", Enumerable.Range(1, 4096)
            .Select(i => new RetailCareerDescriptor(i, $"BEA {i}", gold)).ToArray());
        seedCap.Do("confirm"); seedCap.Do("confirm"); scenarios.Add(seedCap.Output());

        var glyphs = new int[65536][];
        for (int unit = 0; unit <= ushort.MaxValue; unit++) glyphs[unit] = [unit,
            RetailFrontendSession.GameNameGlyphIndex((char)unit),
            RetailFrontendSession.GameNameRenderGlyphIndex((char)unit, false),
            RetailFrontendSession.GameNameRenderGlyphIndex((char)unit, true)];
        return new { constructors, scenarios, glyphs, enums = new
        {
            screen = Enum.GetValues<RetailFrontendScreen>().Select(v => (int)v),
            signal = Enum.GetValues<RetailFrontendSignal>().Select(v => (int)v),
            career_page_mode = Enum.GetValues<RetailFrontendCareerPageMode>().Select(v => (int)v),
            audio_cue = Enum.GetValues<RetailFrontendAudioCue>().Select(v => (int)v),
            language = Enum.GetValues<RetailFrontendLanguage>().Select(v => (int)v),
            cursor_mode = Enum.GetValues<RetailFrontendCursorMode>().Select(v => (int)v),
            menu_kind = Enum.GetValues<RetailFrontendMenuItemKind>().Select(v => (int)v),
        } };
    }

    private sealed class Scenario
    {
        private readonly string name;
        private readonly RetailCareerDescriptor[]? descriptors;
        private readonly RetailFrontendSession session;
        private readonly object initial;
        private readonly List<object> steps = [];
        public Scenario(string name, RetailCareerDescriptor[]? descriptors = null)
        { this.name = name; this.descriptors = descriptors; session = new(descriptors); initial = State(session); }
        public void Do(string op, int first = 0, int second = 0)
        {
            object expected = Capture(() => op switch
            {
                "confirm" => (int)session.Confirm(), "back" => (int)session.Back(),
                "previous" => session.MovePrevious(), "next" => session.MoveNext(),
                "select_main" => session.SelectMainIndex(first), "select_quit" => session.SelectQuitConfirmIndex(first),
                "select_career" => session.SelectCareerIndex(first), "select_configuration" => session.SelectConfigurationIndex(first),
                "select_world" => session.SelectWorld(first), "append" => session.AppendGameNameCharacter((char)first, second),
                "cursor" => session.MoveGameNameCursor(first != 0), "remove" => session.RemoveGameNameCharacter(),
                "consume_launch" => session.ConsumeLevel100LaunchRequest(),
                "consume_career" => Descriptor(session.ConsumeSelectedCareerLoadRequest()),
                "complete_load" => Run(session.CompleteLevel100Load), "begin_intro" => Run(session.BeginLevel100IntroCutscene),
                "complete_intro" => Run(session.CompleteLevel100IntroCutscene),
                "restart" => (int)session.RestartLevel100(), "leave" => (int)session.LeaveLevel100ForMainMenu(),
                "won" => session.TryAcceptWonHandoff((Level100MissionOutcome)first, (Level100MissionTerminalState)second),
                "return_unconstructible" => session.ReturnUnconstructibleLaunchToLevelSelect(),
                "node_world" => Run(() => session.Career.Nodes.Nodes[first].WorldNumber = second),
                "node_complete" => Run(() => session.Career.Nodes.Nodes[first].Complete = second),
                "node_rank" => Run(() => session.Career.Nodes.Nodes[first].Ranking = BitConverter.Int32BitsToSingle(second)),
                "append_null_link" => Run(() => session.Career.Links.Add(null!)),
                _ => throw new InvalidOperationException("Unknown fixture operation: " + op),
            });
            steps.Add(new { op, first, second, expected, after = State(session) });
        }
        public void ToConfiguration(bool fromMain = false)
        { for (int i = 0; i < (fromMain ? 4 : 5); i++) Do("confirm"); }
        public void ToLoading(bool fromMain = false) { ToConfiguration(fromMain); Do("confirm"); }
        public void ToGameplay() { ToLoading(); Do("consume_launch"); Do("complete_load"); }
        public void ToLoadPage() { Do("confirm"); Do("select_main", 2); Do("confirm"); }
        public void ToScreen(RetailFrontendScreen screen)
        {
            switch (screen)
            {
                case RetailFrontendScreen.ClickToStart: return;
                case RetailFrontendScreen.MainMenu: Do("confirm"); return;
                case RetailFrontendScreen.QuitConfirm: Do("confirm"); Do("select_main", 6); Do("confirm"); return;
                case RetailFrontendScreen.Options: Do("confirm"); Do("select_main", 5); Do("confirm"); return;
                case RetailFrontendScreen.DevSelect: Do("confirm"); Do("confirm"); return;
                case RetailFrontendScreen.LevelSelect: for (int i = 0; i < 3; i++) Do("confirm"); return;
                case RetailFrontendScreen.MissionBriefing: for (int i = 0; i < 4; i++) Do("confirm"); return;
                case RetailFrontendScreen.SelectConfiguration: ToConfiguration(); return;
                case RetailFrontendScreen.Loading: ToLoading(); return;
                case RetailFrontendScreen.IntroCutscene: ToLoading(); Do("consume_launch"); Do("begin_intro"); return;
                case RetailFrontendScreen.Gameplay: ToGameplay(); return;
                case RetailFrontendScreen.Debriefing: ToGameplay(); Do("won", 1, 2); return;
                default: throw new ArgumentOutOfRangeException(nameof(screen));
            }
        }
        public object Output() => new { name, descriptors = Descriptors(descriptors), initial, steps };
    }

    private static object State(RetailFrontendSession s) => new
    {
        screen = (int)s.Screen, selected_world_number = s.SelectedWorldNumber, selected_level_name = s.SelectedLevelName,
        selected_briefing_body = s.SelectedBriefingBody.ToArray(), debriefing = GdscriptRetailCareerOracle.Debriefing(s.Debriefing),
        selected_main_index = s.SelectedMainIndex, language = (int)s.Language, selected_quit_confirm_index = s.SelectedQuitConfirmIndex,
        selected_main_item = Item(s.SelectedMainItem), items = s.Items.Select(Item).ToArray(), configuration_count = s.ConfigurationCount,
        selected_configuration_index = s.SelectedConfigurationIndex, selected_configuration = Configuration(s.SelectedConfiguration),
        unavailable_selection = (int?)s.UnavailableSelection, career_descriptors = Descriptors(s.CareerDescriptors),
        career_names = s.CareerNames.Select(GdscriptRetailCareerOracle.Units).ToArray(), career_page_mode = (int)s.CareerPageMode,
        selected_career_index = s.SelectedCareerIndex, game_name = GdscriptRetailCareerOracle.Units(s.GameName),
        game_name_cursor = s.GameNameCursor, game_name_is_fresh = s.GameNameIsFresh, career = GdscriptRetailCareerOracle.State(s.Career),
        consume_launch_world_number = s.ConsumeLaunchWorldNumber, selected_world_is_constructible = s.SelectedWorldIsConstructible,
        level100_intro_cutscene_pending = s.Level100IntroCutscenePending,
    };
    private static object Item(RetailFrontendMenuItem item) => new { kind = (int)item.Kind, is_available = item.IsAvailable };
    private static object Weapon(RetailFrontendWeaponConfiguration w) => new { authored_name = w.AuthoredName, display_name = w.DisplayName };
    private static object Configuration(RetailFrontendBattleEngineConfiguration c) => new
    { catalog_record_index = c.CatalogRecordIndex, authored_name = c.AuthoredName, display_name = c.DisplayName,
        walker_primary = Weapon(c.WalkerPrimary), walker_secondary = Weapon(c.WalkerSecondary),
        jet_primary = Weapon(c.JetPrimary), jet_secondary = Weapon(c.JetSecondary) };
    private static object? Descriptor(RetailCareerDescriptor? d) => d is null ? null : new
    { slot_number = d.SlotNumber, name = GdscriptRetailCareerOracle.Units(d.Name), career = d.Career is null ? null : new
        { suggested_world_number = d.Career.SuggestedWorldNumber, selectable_world_numbers = d.Career.SelectableWorldNumbers.ToArray() } };
    private static object?[]? Descriptors(IEnumerable<RetailCareerDescriptor>? values) => values?.Select(Descriptor).ToArray();
    private static object Capture(Func<object?> action) => GdscriptRetailCareerOracle.Capture(action);
    private static object? Run(Action action) { action(); return null; }
}
