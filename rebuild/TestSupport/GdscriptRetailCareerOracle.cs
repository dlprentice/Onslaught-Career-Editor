// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.Core;
using OnslaughtRebuild.Client;

/// <summary>Temporary differential fixtures from existing pure C# owners.
/// No save is synthesized, read or written. Malformed object records exercise
/// the source's actual failure and partial-mutation order.</summary>
public static class GdscriptRetailCareerOracle
{
    public static object Build()
    {
        var grades = new List<object>();
        var words = new HashSet<uint> { 0, 0x80000000, 1, 0x80000001, 0x7f800000, 0xff800000,
            0x7fc00000, 0xffc00000, 0x7f7fffff, 0xff7fffff, 0x5e000000, 0x5dffffff };
        foreach (float f in new[] { -.001f, 0f, .001f, .25f, .5f, .75f, 1f, 1.25f, 17.25f, 64f })
            foreach (float sample in new[] { MathF.BitDecrement(f), f, MathF.BitIncrement(f) }) words.Add(Word(sample));
        uint seed = 0x43415245;
        uint Next() => seed = unchecked(seed * 1664525u + 1013904223u);
        for (int i = 0; i < 512; i++) words.Add(Next());
        foreach (uint word in words)
            grades.Add(new { word, expected = RetailCareerGrade.GradeByteFromRanking(Float(word)) });
        var gradeCompare = new List<object>();
        for (int held = 0; held < 256; held++)
            foreach (int required in new[] { 0, 65, 66, 67, 68, 69, 83, 127, 128, 255 })
                gradeCompare.Add(new { held, required, expected = new RetailGrade(unchecked((sbyte)held))
                    .IsAtLeast(new RetailGrade(unchecked((sbyte)required))) });

        var objectives = new List<object>();
        void Objective(string name, int[]? statuses) => objectives.Add(new { name, statuses,
            expected = Capture(() => { var v = RetailEndLevelObjectives.IsAllSecondaryObjectivesComplete(statuses!);
                return new { result = v.Result, any_objective_set = v.AnyObjectiveSet }; }) });
        Objective("null", null); Objective("short", new int[9]); Objective("long", new int[11]);
        Objective("none", new int[10]);
        for (int index = 0; index < 10; index++)
            foreach (int status in new[] { int.MinValue, -1, 0, 1, 2, 3, int.MaxValue })
            { var values = new int[10]; values[index] = status; Objective($"slot{index}:{status}", values); }
        for (int i = 0; i < 128; i++) Objective("mixed" + i,
            Enumerable.Range(0, 10).Select(_ => (int)(Next() % 6) - 1).ToArray());

        var debriefings = new List<object>();
        void Debrief(string name, RetailEndLevelSnapshot input, int count, int first) => debriefings.Add(
            new { name, input = EndLevel(input), count, first,
                expected = Capture(() => Debriefing(RetailDebriefingProjection.From(input, count, first))) });
        var won = RetailFillOutEndLevelData.ForLevel100Won();
        foreach (int state in new[] { int.MinValue, -1, 0, 4, 5, 6, int.MaxValue })
            foreach (int count in new[] { int.MinValue, -1, 0, 1, 99, 100, int.MaxValue })
                Debrief($"state{state}:count{count}", won with { FinalState = state }, count, -1);
        Debrief("null-primary-first", won with { PrimaryStatuses = null!, SecondaryStatuses = null! }, 5, 1);
        Debrief("short-primary-first", won with { PrimaryStatuses = new int[9], SecondaryStatuses = null! }, 5, 1);
        Debrief("null-secondary", won with { SecondaryStatuses = null! }, 5, 1);
        Debrief("long-secondary", won with { SecondaryStatuses = new int[11] }, 5, 1);
        foreach (int world in new[] { 100, 500 })
            foreach (int status in new[] { int.MinValue, -1, 0, 1, 2, 3, int.MaxValue })
            {
                int[] primary = new int[10]; primary[0] = 1; primary[9] = status;
                Debrief($"world{world}:status{status}", won with { WorldFinished = world,
                    PrimaryStatuses = primary, SecondaryStatuses = primary.Reverse().ToArray() }, 1, 0);
            }

        var scenarios = new List<object>();
        var firstPlay = new Scenario("cold-won-replay-latches");
        firstPlay.SetSlot(1, 1);
        firstPlay.SetNode(0, "num_attempts", 27);
        firstPlay.SetNode(1, "num_attempts", -1);
        firstPlay.Apply(won);
        firstPlay.SelectAll();
        firstPlay.ReadLatch("new_goodie_count"); firstPlay.ReadLatch("first_goodie");
        firstPlay.Apply(won);
        firstPlay.Apply(won with { Ranking = .25f });
        firstPlay.ReadLatch("new_goodie_count"); firstPlay.ReadLatch("first_goodie");
        scenarios.Add(firstPlay.Output());

        foreach (int final in new[] { 4, 5, 0, int.MinValue })
            foreach (float rank in new[] { 0f, .001f, .25f, .5f, .75f, 1f, float.NaN, float.PositiveInfinity, 17.25f })
            {
                var s = new Scenario($"leftovers:{final}:{Word(rank)}");
                s.SetNode(1, "complete", 1); s.SetNode(1, "ranking", rank);
                s.SetLatch("new_goodie_count", int.MaxValue); s.SetLatch("first_goodie", -42);
                s.SetGoodie(0, 1); s.SetGoodie(8, 3); s.SetGoodie(299, int.MaxValue);
                s.Apply(won with { FinalState = final, Ranking = rank });
                s.Apply(won with { FinalState = final, Ranking = rank });
                scenarios.Add(s.Output());
            }

        var errors = new Scenario("ordered-admission-and-partial-writes");
        errors.SetSlot(7, 1);
        errors.Apply(won with { SlotWords = new int[31], ThingsKilled = null!, SecondaryStatuses = null! });
        errors.Apply(won with { ThingsKilled = null!, SecondaryStatuses = null! });
        errors.Apply(won with { ThingsKilled = new int[4] });
        errors.Apply(won with { SecondaryStatuses = null!, BaseThingsLeft = [1, 2, -1, 1] });
        errors.Apply(won with { SecondaryStatuses = new int[9], BaseThingsLeft = [] });
        errors.Apply(won with { SecondaryStatuses = new int[11], BaseThingsLeft = null! });
        errors.Apply(won with { PrimaryStatuses = null! });
        errors.Apply(won with { FinalState = 4, SlotWords = [], ThingsKilled = null!, SecondaryStatuses = null! });
        scenarios.Add(errors.Output());

        var missing = new Scenario("missing-nodes-and-lost-prefix", cold: false);
        missing.Apply(won with { FinalState = 4 });
        missing.AddNode(100, 1); missing.Apply(won with { FinalState = 4 });
        missing.AddNode(110, 0); missing.Apply(won with { FinalState = 4 });
        missing.Apply(won with { WorldFinished = 999, ThingsKilled = [int.MaxValue, 1, -1, int.MinValue, 0] });
        missing.Apply(won with { WorldFinished = 999, ThingsKilled = [1, int.MaxValue, -1, -1, int.MinValue] });
        missing.AddNode(500, 0); missing.Apply(won with { WorldFinished = 500 });
        missing.Recalc(500, null, null); missing.Recalc(999, null, null);
        scenarios.Add(missing.Output());

        foreach (bool sameIdentity in new[] { false, true })
        {
            var s = new Scenario("competing-links:" + sameIdentity);
            s.SetLink(0, "link_type", 1); s.SetLink(1, "to_node", 1);
            s.AddNode(211, 1); s.SetNode(2, "lower_link", 0); s.SetNode(2, "higher_link", 1);
            if (sameIdentity) { s.AppendLinkReference(1); s.SetNode(0, "lower_link", 4); }
            s.Recalc(100, Enumerable.Repeat(1, 10).ToArray(), null);
            s.SetLink(0, "link_type", -1); s.Recalc(100, new int[10], null);
            s.SetLink(0, "to_node", int.MaxValue); s.SetLink(0, "link_type", 0);
            s.Recalc(100, new int[10], null);
            scenarios.Add(s.Output());
        }
        var nullLinks = new Scenario("null-link-selection-and-safe-recalc", cold: false);
        nullLinks.AppendNullLink(); nullLinks.SelectAll();
        nullLinks.AddNode(100, 0); nullLinks.SetNode(0, "lower_link", 0); nullLinks.Recalc(100, new int[10], null);
        scenarios.Add(nullLinks.Output());

        var storage = new Scenario("node-bit-slot-counter-boundaries");
        storage.SetNode(0, "is_start_of_new_island", int.MinValue);
        foreach (int offset in new[] { int.MinValue, -33, -32, -1, 0, 1, 31, 32, 63, 64, 255, 256, 287, 288, int.MaxValue })
            foreach (int value in new[] { 1, 0, -1, 2, int.MinValue }) storage.SetBase(0, offset, value);
        storage.BlankNode(0);
        foreach (int slot in new[] { int.MinValue, -1, 0, 31, 32, 63, 64, 255, 256, 1023, int.MaxValue })
            foreach (int value in new[] { 1, 0, -1, 2 }) storage.SetSlot(slot, value);
        storage.CopySlots(null); storage.CopySlots(new int[31]);
        storage.CopySlots(Enumerable.Range(0, 32).Select(i => unchecked((int)(0x80000001u * (uint)i))).ToArray());
        storage.UpdateKills(100, null); storage.UpdateKills(100, new int[4]);
        storage.UpdateKills(100, [1, 2, 3, 4, 5]);
        storage.UpdateKills(101, [int.MaxValue, int.MinValue, -1, 0, 17]);
        storage.UpdateKills(-1, [1, -1, int.MinValue, int.MaxValue, int.MaxValue]);
        foreach (int index in new[] { -1, 0, 299, 300 })
        { storage.SetGoodie(index, -1); storage.NewGoodie(index); }
        scenarios.Add(storage.Output());

        var table = new Scenario("first-match-and-node-limit", cold: false);
        table.AddNode(100, 2); table.AddNode(100, 1); table.AddNode(110, 1);
        table.Grade(100); table.Grade(999);
        for (int i = 3; i < 101; i++) table.AddNode(1000 + i, 0);
        scenarios.Add(table.Output());

        var graph = RetailWorldCatalog.Nodes.Select(row => new { index = row.Index, world_number = row.WorldNumber,
            lower_child_index = row.LowerChildIndex, higher_child_index = row.HigherChildIndex,
            primary_base_world = row.PrimaryBaseWorld, secondary_base_world = row.SecondaryBaseWorld }).ToArray();
        var graphQueries = new List<object>();
        int[] worlds = RetailWorldCatalog.Nodes.Select(n => n.WorldNumber).Concat([int.MinValue, -1, 0, 999, int.MaxValue]).ToArray();
        foreach (int current in worlds)
            foreach (int dies in worlds)
                graphQueries.Add(new { current, dies, expected = RetailWorldCatalog.IsWorldLater(current, dies) });
        var strings = worlds.Select(world => new { world, level_name = Units(RetailFrontendWorldStrings.LevelName(world)),
            briefing = RetailFrontendWorldStrings.Briefing(world).Select(Units).ToArray() }).ToArray();
        return new { grades, grade_compare = gradeCompare, objectives, debriefings, scenarios, graph, graph_queries = graphQueries,
            strings, won_snapshot = EndLevel(won) };
    }

    private sealed class Scenario(string name, bool cold = true)
    {
        private readonly RetailCareerCampaign career = cold ? RetailCareerReCalcLinks.CreateColdTrainingSlice() : new();
        private readonly List<object> steps = [];
        private void Step(string op, object args, Func<object?> action) =>
            steps.Add(new { op, args, expected = Capture(action), after = State(career) });
        public void Apply(RetailEndLevelSnapshot value) => Step("apply", EndLevel(value), () => { career.ApplyUpdate(value); return null; });
        public void Recalc(int world, int[]? secondary, int[]? bases) => Step("recalc", new { world, secondary, bases },
            () => { career.ReCalcLinks(world, secondary!, bases); return null; });
        public void AddNode(int world, int complete) => Step("add_node", new { world, complete },
            () => { career.Nodes.Add(world, complete); return null; });
        public void SetNode(int index, string field, object value) => Step("set_node", new { index, field,
            value = field == "ranking" ? (object)Word((float)value) : value }, () =>
        {
            var node = career.Nodes.Nodes[index];
            switch (field)
            {
                case "ranking": node.Ranking = (float)value; break;
                case "world_number": node.WorldNumber = (int)value; break;
                case "complete": node.Complete = (int)value; break;
                case "lower_link": node.LowerLink = (int)value; break;
                case "higher_link": node.HigherLink = (int)value; break;
                case "num_attempts": node.NumAttempts = (int)value; break;
                case "is_start_of_new_island": node.IsStartOfNewIsland = (int)value; break;
                default: throw new InvalidOperationException(field);
            }
            return null;
        });
        public void BlankNode(int index) => Step("blank_node", new { index }, () => { career.Nodes.Nodes[index].Blank(); return null; });
        public void SetBase(int index, int offset, int value) => Step("set_base", new { index, offset, value }, () =>
            { career.Nodes.Nodes[index].SetBaseThingExistTo(offset, value); return career.Nodes.Nodes[index].DoesBaseThingExist(offset); });
        public void SetLink(int index, string field, int value) => Step("set_link", new { index, field, value }, () =>
            { if (field == "link_type") career.Links[index].LinkType = value; else career.Links[index].ToNode = value; return null; });
        public void AppendLinkReference(int index) => Step("append_link_reference", new { index }, () => { career.Links.Add(career.Links[index]); return null; });
        public void AppendNullLink() => Step("append_null_link", new { }, () => { career.Links.Add(null!); return null; });
        public void SetSlot(int slot, int value) => Step("set_slot", new { slot, value }, () => { career.Slots.SetSlot(slot, value); return career.Slots.GetSlot(slot); });
        public void CopySlots(int[]? words) => Step("copy_slots", new { words }, () => { career.Slots.CopyWords(words!); return null; });
        public void UpdateKills(int world, int[]? words) => Step("update_kills", new { world, words }, () => { career.Counters.UpdateThingsKilled(world, words!); return null; });
        public void SetGoodie(int index, int value) => Step("set_goodie", new { index, value }, () => { career.Goodies.Set(index, value); return null; });
        public void NewGoodie(int index) => Step("new_goodie", new { index }, () => { career.Goodies.SetNewIfNotDone(index); return null; });
        public void SetLatch(string field, int value) => Step("set_latch", new { field, value }, () =>
            { if (field == "new_goodie_count") career.Counters.NewGoodieCount = value; else career.Counters.FirstGoodie = value; return null; });
        public void ReadLatch(string field) => Step("read_latch", new { field }, () => field == "new_goodie_count"
            ? career.Counters.GetAndResetGoodieNewCount() : career.Counters.GetAndResetFirstGoodie());
        public void Grade(int world) => Step("grade", new { world }, () => RetailWorldGrade.GradeByteForWorld(career.Nodes.Nodes
            .Select(n => new RetailWorldGradeNode(n.WorldNumber, n.Complete, n.Ranking)).ToArray(), world));
        public void SelectAll()
        { foreach (int world in RetailWorldCatalog.Nodes.Select(n => n.WorldNumber).Concat([0, -1, int.MinValue, int.MaxValue]))
            Step("selectable", new { world }, () => RetailWorldCatalog.IsWorldSelectable(career, world)); }
        public object Output() => new { name, cold, steps };
    }

    internal static object State(RetailCareerCampaign career) => new
    {
        nodes = career.Nodes.Nodes.Select(n => new { is_start_of_new_island = n.IsStartOfNewIsland,
            complete = n.Complete, lower_link = n.LowerLink, higher_link = n.HigherLink, world_number = n.WorldNumber,
            num_attempts = n.NumAttempts, ranking_word = Word(n.Ranking), base_words = n.BaseThingsExistsWordsView.ToArray() }).ToArray(),
        links = career.Links.Select(link => link is null ? null : new { link_type = link.LinkType, to_node = link.ToNode }).ToArray(),
        counters = new { new_goodie_count = career.Counters.NewGoodieCount, first_goodie = career.Counters.FirstGoodie,
            killed_things = career.Counters.KilledThings.ToArray() }, slots = career.Slots.Words.ToArray(),
        goodies = career.Goodies.States.ToArray(), career_in_progress = career.CareerInProgress,
    };
    internal static object EndLevel(RetailEndLevelSnapshot value) => new { world_finished = value.WorldFinished, final_state = value.FinalState,
        ranking_word = Word(value.Ranking), secondary_statuses = value.SecondaryStatuses, things_killed = value.ThingsKilled,
        slot_words = value.SlotWords, primary_statuses = value.PrimaryStatuses, base_things_left = value.BaseThingsLeft };
    internal static object? Debriefing(RetailDebriefingProjection? d) => d is null ? null : new
    { world_finished = d.WorldFinished, mission_status = (int)d.MissionStatus, primary_objectives = (int)d.PrimaryObjectives,
        secondary_objectives = (int)d.SecondaryObjectives, grade_byte = d.GradeByte, new_goodie_count = d.NewGoodieCount, first_goodie = d.FirstGoodie };
    internal static object Capture(Func<object?> action)
    { try { return new { ok = true, value = action() }; } catch (Exception e) { return new { ok = false,
        error_type = e.GetType().Name, parameter = e is ArgumentException argument ? argument.ParamName ?? "" : "" }; } }
    internal static uint Word(float value) => unchecked((uint)BitConverter.SingleToInt32Bits(value));
    private static float Float(uint word) => BitConverter.Int32BitsToSingle(unchecked((int)word));
    internal static int[]? Units(string? value) => value?.Select(c => (int)c).ToArray();
}
