// SPDX-License-Identifier: GPL-3.0-or-later
using System.Collections;
using System.Reflection;
using System.Runtime.ExceptionServices;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;
using M = System.Collections.Generic.Dictionary<string, object?>;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Synthetic/retained-test raw-word fixture from the unchanged weapon owners.
/// This does not load retail assets, install a registry or replace expected
/// behavior. The native harness compares every result and mutation separately.
/// </summary>
public sealed partial class RetailWeaponReferenceChecks : Node
{
    private const BindingFlags Internal = BindingFlags.Static | BindingFlags.NonPublic;
    private static readonly MethodInfo s_distance = typeof(RetailUnitWeaponSelection).GetMethod("RawDistance", Internal)!;
    private static readonly MethodInfo s_score = typeof(RetailUnitWeaponSelection).GetMethod("Score", Internal)!;
    private readonly List<M> _charge = [], _ready = [], _stores = [], _cycles = [], _unit = [];
    private int _steps;

    public override void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            if (args.Length != 2 || Engine.IsEditorHint() || DisplayServer.GetName() != "headless")
                throw new InvalidOperationException("Two fresh owned outputs and headless runtime are required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            if (fixturePath == reportPath) throw new ArgumentException("Fixture and report must differ.");
            Godot.Input.MouseModeEnum pointer = Godot.Input.MouseMode;
            ChargeCases(); StoreCases(); CycleCases(); UnitCases();
            M ownership = Ownership();
            var fixture = new M { ["schema"] = 1, ["charge"] = _charge, ["ready"] = _ready,
                ["stores"] = _stores, ["cycles"] = _cycles, ["unit"] = _unit, ["ownership"] = ownership,
                ["source_sha256"] = SourceHashes(), ["constants"] = new M {
                    ["level_count"] = RetailWeaponChargeTable.LevelCount, ["absent_level"] = RetailWeaponChargeTable.AbsentLevel,
                    ["value_per_level"] = RetailWeaponChargeTable.ValuePerLevel, ["increment_cap_bits"] = Word(RetailWeaponCharge.IncrementCap),
                    ["store_count"] = RetailWeaponStores.StoreCount, ["full_ammo_percentage_bits"] = Word(RetailWeaponStoreReadouts.FullAmmoPercentage) } };
            using (Variant packed = Pack(fixture))
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create weapon reference fixture.")) file.StoreVar(packed, false);
            if (Godot.Input.MouseMode != pointer) throw new InvalidOperationException("Pointer ownership changed.");
            using var version = Engine.GetVersionInfo();
            using Variant engine = version["string"];
            var report = new M { ["schema"] = 1, ["failure_count"] = 0,
                ["completed"] = new[] { "retail_weapon_reference" },
                ["counts"] = new M { ["charge_sequences"] = _charge.Count, ["charge_steps"] = _steps,
                    ["ready"] = _ready.Count, ["stores"] = _stores.Count, ["cycles"] = _cycles.Count, ["unit"] = _unit.Count },
                ["runtime"] = RuntimeInformation.FrameworkDescription, ["engine"] = engine.AsString(),
                ["fixture_sha256"] = Hash(File.ReadAllBytes(fixturePath)) };
            File.WriteAllText(reportPath, JsonSerializer.Serialize(report));
            GD.Print($"RETAIL_WEAPON_REFERENCE_CHECKS: {_charge.Count} charge sequences, {_steps} steps, {_ready.Count} ready, {_stores.Count} stores, {_cycles.Count} cycles, {_unit.Count} Unit; {fixturePath}");
            GetTree().Quit();
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private void ChargeCases()
    {
        int[] words = Words();
        ChargeSequence("null", null, 0);
        for (int mask = 0; mask < 32; mask++) for (int i = 0; i < words.Length; i++)
        {
            var table = new RetailWeaponChargeTable { Charge = Float(words[i]), ChargeRate = Float(words[(i + 7) % words.Length]),
                ReadyAtTime = Float(words[(i + 11) % words.Length]), ReadyToChargeGateActive = (i & 1) == 0 };
            for (int level = 0; level < 5; level++) table.Levels[level] = (mask & (1 << level)) != 0 ? level - 3 : -1;
            // Presence words are not interpreted as charge values. Include
            // level2 explicitly: its generated value would otherwise be -1.
            if ((mask & 4) != 0) table.Levels[2] = int.MinValue;
            ChargeSequence($"presence/{mask}/{i}", table, words[(i + 19) % words.Length]);
        }
        foreach (int left in words) foreach (int right in words)
            _ready.Add(new M { ["now"] = left, ["ready_at"] = right,
                ["result"] = Capture(() => RetailWeaponCharge.ReadyTimeElapsed(Float(left), Float(right))) });
        foreach (int rate in words.Where(w => !float.IsFinite(Float(w))))
            foreach (int value in words.Where(w => !float.IsFinite(Float(w))))
                ChargeSequence($"unordered-pair/{rate}/{value}", Table(value, rate), 0);
        var pulse = Table(0, Word(10));
        pulse.ReadyAtTime = Float(0x3dcccccd);
        List<M> steps = [];
        M initial = Snapshot(pulse)!;
        for (int i = 0; i < 12; i++)
        {
            ChargeStep(pulse, steps, "ready_to_charge", Word(i * .05f));
            ChargeStep(pulse, steps, "fully_charged");
            if (!RetailWeaponCharge.FullyCharged(pulse)) ChargeStep(pulse, steps, "charge");
            ChargeStep(pulse, steps, "get_charge_bits");
        }
        ChargeStep(pulse, steps, "level_set", 4, int.MaxValue);
        ChargeStep(pulse, steps, "level_set", -1, 0);
        ChargeStep(pulse, steps, "level_set", 5, 0);
        ChargeStep(pulse, steps, "word_set", "charge_bits", unchecked((int)0xff800001));
        ChargeStep(pulse, steps, "lose_charge");
        ChargeStep(pulse, steps, "gate_set", false);
        ChargeStep(pulse, steps, "ready_to_charge", 0x7fc12345);
        _charge.Add(new M { ["name"] = "retained-pulse-caller-stop-and-alias-writes", ["initial"] = initial, ["steps"] = steps });
    }
    private void ChargeSequence(string name, RetailWeaponChargeTable? table, int now)
    {
        List<M> steps = [];
        M? initial = Snapshot(table);
        foreach (string op in new[] { "max_charge", "get_charge_bits", "can_charge", "fully_charged", "ready_to_charge",
            "charge", "get_charge_bits", "fully_charged", "charge", "lose_charge", "get_charge_bits" })
            ChargeStep(table, steps, op, now);
        _charge.Add(new M { ["name"] = name, ["initial"] = initial, ["steps"] = steps });
    }
    private void ChargeStep(RetailWeaponChargeTable? table, List<M> steps, string op, params object?[] args)
    {
        M result = Capture(() => op switch
        {
            "max_charge" => RetailWeaponCharge.MaxCharge(table!),
            "get_charge_bits" => Word(RetailWeaponCharge.GetCharge(table!)),
            "can_charge" => RetailWeaponCharge.CanCharge(table!),
            "fully_charged" => RetailWeaponCharge.FullyCharged(table!),
            "ready_to_charge" => RetailWeaponCharge.ReadyToCharge(table!, Float((int)args[0]!)),
            "charge" => Do(() => RetailWeaponCharge.Charge(table!)),
            "lose_charge" => Do(() => RetailWeaponCharge.LoseCharge(table!)),
            "level_set" => Do(() => table!.Levels[(int)args[0]!] = (int)args[1]!),
            "word_set" => Do(() => table!.Charge = Float((int)args[1]!)),
            "gate_set" => Do(() => table!.ReadyToChargeGateActive = (bool)args[0]!),
            _ => throw new InvalidOperationException("Unknown charge fixture operation.")
        });
        steps.Add(new M { ["op"] = op, ["args"] = args, ["result"] = result, ["after"] = Snapshot(table) });
        _steps++;
    }

    private void StoreCases()
    {
        int[] words = Words();
        int[] flags = [0, 1, -1, int.MinValue, int.MaxValue];
        for (int i = 0; i < words.Length; i++) for (int j = 0; j < words.Length; j++)
        {
            var stores = Stores(words[i], words[j], flags[(i + j) % flags.Length], flags[(i * 3 + j) % flags.Length]);
            int index = (i + j) % 6;
            for (int slot = 0; slot < 6; slot++) if (slot != index)
            { stores.StoreValue[slot] = Float(words[(i + slot + 1) % words.Length]); stores.StoreHeat[slot] = flags[slot % flags.Length]; }
            StoreCase($"words/{i}/{j}/{index}", stores, index, flags[i % flags.Length],
                Mounted(flags[i % flags.Length], index, words[(i * 7 + j) % words.Length], flags[j % flags.Length]));
        }
        foreach (int? index in new int?[] { null, int.MinValue, -1, 0, 5, 6, int.MaxValue })
            foreach (int active in flags) foreach (bool nullStores in new[] { false, true })
                StoreCase($"admission/{index}/{active}/{nullStores}", nullStores ? null : Stores(Word(2.5f), 0, 0, 2), index, active,
                    Mounted(active, index ?? -1, 0x7f800001, 0));
        StoreCase("null-weapon-before-null-stores", null, 6, 0, null);
        StoreCase("null-weapon", new(), null, 0, null);
        foreach (int word in words) foreach (int heat in flags)
            StoreCase($"fistp/{word}/{heat}", Stores(word, Word(1), heat, -3), 0, 1, Mounted(1, 0, word, 0));
    }
    private void StoreCase(string name, RetailWeaponStores? stores, int? index, int active, RetailMountedWeapon? weapon)
    {
        var results = new M {
            ["ammo_percentage_bits"] = Capture(() => Word(RetailWeaponStoreReadouts.AmmoPercentage(stores!, index))),
            ["ammo_count"] = Capture(() => RetailWeaponStoreReadouts.AmmoCount(stores!, index)),
            ["is_energy_weapon"] = Capture(() => RetailWeaponStoreReadouts.IsEnergyWeapon(stores!, index)),
            ["is_weapon_overheated"] = Capture(() => RetailWeaponStoreReadouts.IsWeaponOverheated(stores!, index)),
            ["can_weapon_fire"] = Capture(() => RetailWeaponFireGate.CanWeaponFire(stores!, index)),
            ["can_walker_weapon_fire"] = Capture(() => RetailWeaponFireGate.CanWalkerWeaponFire(stores!, index, active)),
            ["is_selectable"] = Capture(() => RetailWeaponCycle.IsSelectable(weapon!, stores!)) };
        _stores.Add(new M { ["name"] = name, ["stores"] = Snapshot(stores), ["index"] = index, ["active"] = active,
            ["weapon"] = Snapshot(weapon), ["results"] = results });
    }

    private void CycleCases()
    {
        for (int count = 1; count <= 6; count++) for (int mask = 0; mask < 1 << count; mask++)
            for (int current = 0; current < count; current++)
            {
                RetailMountedWeapon?[] pool = Enumerable.Range(0, count).Select(i =>
                    (RetailMountedWeapon?)Mounted((mask & (1 << i)) == 0 ? 0 : -3, i, 0, i % 2)).ToArray();
                CycleCase($"exhaustive/{count}/{mask}/{current}", Stores(0, 0, 0, 0), pool, Enumerable.Range(0, count).ToArray(), current);
            }
        foreach (int count in new[] { 0, 1, 2 }) foreach (int current in new[] { int.MinValue, -1, 0, 1, 2, int.MaxValue })
        {
            RetailMountedWeapon?[] pool = Enumerable.Range(0, count).Select(_ => (RetailMountedWeapon?)Mounted(1, 0, 0, 0)).ToArray();
            CycleCase($"bounds/{count}/{current}", new(), pool, Enumerable.Range(0, count).ToArray(), current);
        }
        var shared = Mounted(1, 0, 0x7fc12345, 9);
        CycleCase("shared-object-different-indices", new(), [shared], [0, 0, 0], 2);
        shared.ZoomMode = -5;
        shared.Consumption = Float(unchecked((int)0xff800001));
        CycleCase("shared-object-mutated-before-call", new(), [shared], [0, 0], 0);
        CycleCase("null-current", new(), [null, shared], [0, 1], 0);
        CycleCase("null-candidate", new(), [shared, null], [0, 1], 0);
        CycleCase("null-unvisited-after-acceptance", new(), [shared, shared, null], [0, 1, 2], 0);
        CycleCase("inactive-bad-store", new(), [shared, Mounted(0, 6, 0, 0)], [0, 1], 0);
        CycleCase("active-bad-store", new(), [shared, Mounted(1, 6, 0, 0)], [0, 1], 0);
        CycleCase("current-bad-store-unused", new(), [Mounted(1, -1, 0, 0), shared], [0, 1], 0);
        CycleCase("null-stores-before-current", null, [null], [0], -1);
        CycleCase("null-list-before-null-stores", null, [], [], -1, true);
        foreach (int word in Words()) foreach (int heat in new[] { 0, 1, -1 })
            CycleCase($"unordered/{word}/{heat}", Stores(word, 0, heat, 1),
                [Mounted(1, 0, 0, 0), Mounted(1, 0, word, 1)], [0, 1], 0);
    }
    private void CycleCase(string name, RetailWeaponStores? stores, RetailMountedWeapon?[] pool, int[] order, int current, bool nullList = false)
    {
        RetailMountedWeapon[]? weapons = nullList ? null : order.Select(i => pool[i]!).ToArray();
        _cycles.Add(new M { ["name"] = name, ["stores"] = Snapshot(stores), ["pool"] = pool.Select(w => Snapshot(w)).ToArray(),
            ["order"] = order, ["current"] = current, ["null_list"] = nullList,
            ["terminates"] = Capture(() => RetailWeaponCycle.SearchTerminates(current, order.Length)),
            ["result"] = Capture(() => RetailWeaponCycle.ChangeWeapon(weapons!, current, stores!)) });
    }

    private void UnitCases()
    {
        var one = Candidate(10);
        var two = Candidate(20);
        RetailUnitAttackSelection prior = new(20, 123);
        Level100FloatVector3Bits owner = default, target = V(100, 0, 0);
        Unit("null-before-spawners", "select", null, 1, prior, owner, target, 1u, 0, 0, 0);
        Unit("spawner-refusal", "select", Array.Empty<RetailUnitWeaponSelectionCandidate>(), -1, prior, owner, null, 1u, 0, 0, 0);
        Unit("empty-clears", "select", Array.Empty<RetailUnitWeaponSelectionCandidate>(), 0, prior, owner, target, 1u, 0, 0, Word(10));
        Unit("empty-still-reads-now", "select", Array.Empty<RetailUnitWeaponSelectionCandidate>(), 0, prior, owner, target, 1u, 0, 0, 0x7fc12345);
        Unit("null-target-preserves", "select", new[] { one }, 0, prior, owner, null, 1u, 0x7fc12345, 0x7fc12345, 0x7fc12345);
        foreach (var refused in new[] { one with { HasCurrentMode = false }, one with { UsesBallisticArc = true }, one with { HasProjectileDefinition = false } })
            Unit("admission-before-burst-or-null-target", "select", new[] { one with { BurstCounter = -1, BurstSize = 1 }, refused }, 0, prior, owner, null, 1u, 0, 0, 0);
        foreach (int counter in new[] { int.MinValue, -1, 0, 1, 2, 3, int.MaxValue }) foreach (int size in new[] { int.MinValue, -1, 0, 1, 3, int.MaxValue })
            Unit($"burst/{counter}/{size}", "select", new[] { one with { ActiveWord = 0, TargetMask = 0, BurstCounter = counter, BurstSize = size }, two },
                0, prior, W(0x7fc12345, 0, 0), null, 1u, 0, 0, 0x7fc12345);
        foreach (uint mask in new uint[] { 0, 1, 2, 0x80000, 0x80001, 0x80000000, uint.MaxValue })
            foreach (int active in new[] { 0, 1, -3 }) foreach (int now in new[] { Word(10)-1, Word(10), Word(10)+1, 0x7fc00001 })
                Unit($"mask-time/{mask}/{active}/{now}", "select", new[] { one with { ActiveWord = active, TargetMask = mask, ReadyAtTimeFloatBits = Word(10) }, two },
                    0, prior, owner, target, mask, 0, 0, now);
        foreach (int distance in new[] { Word(10)-1, Word(10), Word(10)+1, Word(20)-1, Word(20), Word(20)+1 })
            Unit($"range/{distance}", "score", one with { MinimumRangeFloatBits = Word(10), MaximumRangeFloatBits = Word(20) }, target, 1u, distance, 0, 0, Word(10));
        foreach (int height in new[] { Word(-10)-1, Word(-10), Word(-10)+1, Word(10000)-1, Word(10000), Word(10000)+1 })
            foreach (int water in new[] { height, Word(10001), Word(-11) })
                Unit($"height/{height}/{water}", "score", one, target, 1u, Word(100), height, water, Word(10));
        string[] fields = ["ready", "minimum_range", "maximum_range", "minimum_height", "maximum_height"];
        foreach (string field in fields) foreach (int word in Words())
            Unit($"candidate/{field}/{word}", "score", CandidateWord(one, field, word), target, 1u, Word(100), 0, 0, Word(10));
        foreach (int word in Words())
        {
            Unit($"direct-distance/{word}", "score", one, target, 1u, word, 0, 0, Word(10));
            Unit($"direct-now/{word}", "score", one, target, 1u, Word(100), 0, 0, word);
            Unit($"terrain/{word}", "score", one, target, 1u, Word(100), word, 0, Word(10));
            Unit($"water/{word}", "score", one, target, 1u, Word(100), 0, word, Word(10));
            Unit($"inactive-skips/{word}", "score", CandidateWord(one with { ActiveWord = 0 }, "minimum_height", word), new Level100FloatVector3Bits(word, word, word), 1u, word, word, word, word);
            Unit($"mask-skips/{word}", "score", CandidateWord(one with { TargetMask = 0 }, "minimum_height", word), new Level100FloatVector3Bits(word, word, word), 1u, word, word, word, word);
            for (int axis = 0; axis < 3; axis++)
            {
                Unit($"distance-owner/{axis}/{word}", "raw_distance", Axis(default, axis, word), target);
                Unit($"distance-target/{axis}/{word}", "raw_distance", owner, Axis(default, axis, word));
                Unit($"distance-difference/{axis}/{word}", "raw_distance", Axis(default, axis, word), Axis(default, axis, word ^ int.MinValue));
            }
        }
        foreach (var pair in new[] { (default(Level100FloatVector3Bits), V(3, 4, 12)),
            (default(Level100FloatVector3Bits), V(16777216, 4096, 4096)), (V(1, 1, 1), V(33554432, 33554432, 33554432)),
            (default(Level100FloatVector3Bits), V(.1f, .1f, 1.1f)) })
            Unit("retained-distance", "raw_distance", pair.Item1, pair.Item2);
        Unit("retained-large-score", "score", one with { MaximumTargetHeightFloatBits = Word(1e20f) }, V(0, 0, 0), 1u, Word(16777216), 0, 0, Word(10));
        Unit("maximum-height-unused-on-lower-reject", "score", one with { MinimumTargetHeightFloatBits = 0, MaximumTargetHeightFloatBits = 0x7fc00001 }, target, 1u, 0, 0, 0, 0);
        Unit("both-ranges-read-before-branch", "score", one with { MinimumRangeFloatBits = Word(200), MaximumRangeFloatBits = 0x7fc00001 }, target, 1u, 0, 0, 0, 0);
        Unit("inactive-unsupported-score-no-admission", "score", one with { ActiveWord = 0, UsesBallisticArc = true, HasCurrentMode = false }, target, 1u, 0, 0, 0, 0);
        var random = new Random(0x57454150);
        for (int i = 0; i < 160; i++)
        {
            Level100FloatVector3Bits point = V(random.Next(-1000, 1001), random.Next(-1000, 1001), random.Next(-100, 101));
            var list = new[] { one with { MinimumRangeFloatBits = Word(random.Next(100)), MaximumRangeFloatBits = Word(random.Next(200)), TargetMask = (uint)(i % 4 + 1) },
                two with { ReadyAtTimeFloatBits = Word(i % 10), TargetMask = (uint)(i % 2 + 1) } };
            Unit("repeated-selection/" + i, "select", list, 0, prior, owner, point, 1u, Word(120), Word(150), Word(i * .05f));
            prior = RetailUnitWeaponSelection.Select(list, 0, prior, owner, point, 1, Word(120), Word(150), Word(i * .05f));
        }
    }
    private void Unit(string name, string operation, params object?[] args) => _unit.Add(new M {
        ["name"] = name, ["op"] = operation, ["args"] = args, ["result"] = Capture(() => operation switch {
            "select" => RetailUnitWeaponSelection.Select((RetailUnitWeaponSelectionCandidate[])args[0]!, (int)args[1]!,
                (RetailUnitAttackSelection)args[2]!, (Level100FloatVector3Bits)args[3]!, (Level100FloatVector3Bits?)args[4], (uint)args[5]!,
                (int)args[6]!, (int)args[7]!, (int)args[8]!),
            "raw_distance" => Word((float)Invoke(s_distance, args)!),
            "score" => Score(args),
            _ => throw new InvalidOperationException("Unknown Unit fixture operation.") }) });
    private static object? Score(object?[] args)
    {
        object? score = Invoke(s_score, [args[0], args[1], args[2], Float((int)args[3]!), args[4], args[5], Float((int)args[6]!)]);
        return score is float value ? Word(value) : null;
    }

    private static M Ownership()
    {
        var table = Table(Word(10), Word(2));
        int[] levels = table.Levels;
        levels[4] = -2;
        int maximum = RetailWeaponCharge.MaxCharge(table);
        var stores = new RetailWeaponStores();
        float[] values = stores.StoreValue, capacities = stores.ConfigurationStoreValue;
        int[] heats = stores.StoreHeat, overheats = stores.StoreOverheat;
        values[2] = 3.5f; capacities[2] = 7; heats[2] = 0; overheats[2] = -2;
        int count = RetailWeaponStoreReadouts.AmmoCount(stores, 2);
        var weapon = Mounted(1, 2, Word(4), 0);
        RetailMountedWeapon[] list = [weapon, weapon];
        bool before = RetailWeaponCycle.IsSelectable(list[1], stores);
        weapon.Consumption = 3;
        bool after = RetailWeaponCycle.IsSelectable(list[1], stores);
        heats[2] = 7;
        return new M { ["level_alias"] = ReferenceEquals(levels, table.Levels), ["maximum"] = maximum,
            ["store_aliases"] = new[] { ReferenceEquals(values, stores.StoreValue), ReferenceEquals(capacities, stores.ConfigurationStoreValue),
                ReferenceEquals(heats, stores.StoreHeat), ReferenceEquals(overheats, stores.StoreOverheat) },
            ["count_before_heat"] = count, ["count_after_heat"] = RetailWeaponStoreReadouts.AmmoCount(stores, 2),
            ["mounted_alias"] = ReferenceEquals(list[0], list[1]), ["selectable_before"] = before, ["selectable_after"] = after,
            ["cycle"] = RetailWeaponCycle.ChangeWeapon(list, 0, stores), ["table"] = Snapshot(table), ["stores"] = Snapshot(stores),
            ["weapon"] = Snapshot(weapon) };
    }

    private static RetailWeaponChargeTable Table(int charge, int rate)
    { var table = new RetailWeaponChargeTable { Charge = Float(charge), ChargeRate = Float(rate) }; table.Levels[0] = 0; table.Levels[1] = 0; return table; }
    private static RetailWeaponStores Stores(int value, int capacity, int heat, int overheat)
    { var stores = new RetailWeaponStores(); Array.Fill(stores.StoreValue, Float(value)); Array.Fill(stores.ConfigurationStoreValue, Float(capacity)); Array.Fill(stores.StoreHeat, heat); Array.Fill(stores.StoreOverheat, overheat); return stores; }
    private static RetailMountedWeapon Mounted(int active, int store, int consumption, int zoom) =>
        new() { IsActive = active, AmmoStore = store, Consumption = Float(consumption), ZoomMode = zoom };
    private static RetailUnitWeaponSelectionCandidate Candidate(int identity) => new(identity, 1, 1, 0, 3, Word(9), 0, Word(200), Word(-10), Word(10000));
    private static RetailUnitWeaponSelectionCandidate CandidateWord(RetailUnitWeaponSelectionCandidate c, string field, int value) => field switch
    { "ready" => c with { ReadyAtTimeFloatBits = value }, "minimum_range" => c with { MinimumRangeFloatBits = value },
        "maximum_range" => c with { MaximumRangeFloatBits = value }, "minimum_height" => c with { MinimumTargetHeightFloatBits = value },
        _ => c with { MaximumTargetHeightFloatBits = value } };
    private static M? Snapshot(RetailWeaponChargeTable? t) => t is null ? null : new M { ["levels"] = t.Levels.ToArray(),
        ["charge_rate_bits"] = Word(t.ChargeRate), ["charge_bits"] = Word(t.Charge), ["ready_at_time_bits"] = Word(t.ReadyAtTime), ["ready_to_charge_gate_active"] = t.ReadyToChargeGateActive };
    private static M? Snapshot(RetailWeaponStores? s) => s is null ? null : new M { ["store_value"] = s.StoreValue.Select(Word).ToArray(),
        ["store_overheat"] = s.StoreOverheat.ToArray(), ["store_heat"] = s.StoreHeat.ToArray(), ["configuration_store_value"] = s.ConfigurationStoreValue.Select(Word).ToArray() };
    private static M? Snapshot(RetailMountedWeapon? w) => w is null ? null : new M { ["is_active"] = w.IsActive, ["ammo_store"] = w.AmmoStore,
        ["consumption_bits"] = Word(w.Consumption), ["zoom_mode"] = w.ZoomMode };
    private static int Word(float value) => BitConverter.SingleToInt32Bits(value);
    private static float Float(int bits) => BitConverter.Int32BitsToSingle(bits);
    private static int[] Words() => [0, int.MinValue, 1, unchecked((int)0x80000001), 0x007fffff, 0x00800000, 0x3f000000,
        Word(1), Word(-1), Word(1.5f), Word(-1.5f), Word(2.5f), Word(-2.5f), Word(3.5f), Word(2.7f), Word(10), Word(100),
        Word(399), Word(400)-1, Word(400), Word(400)+1, Word(600), 0x4effffff, 0x4f000000, 0x4f000001,
        unchecked((int)0xcf000001), 0x5effffff, 0x5f000000, unchecked((int)0xdf000000), unchecked((int)0xdf000001),
        0x7f7fffff, unchecked((int)0xff7fffff), 0x7f800000, unchecked((int)0xff800000),
        0x7fc00001, 0x7fc12345, 0x7f800001, unchecked((int)0xffc54321), unchecked((int)0xff800002)];
    private static Level100FloatVector3Bits W(uint x, uint y, uint z) => new(unchecked((int)x), unchecked((int)y), unchecked((int)z));
    private static Level100FloatVector3Bits V(float x, float y, float z) => new(Word(x), Word(y), Word(z));
    private static Level100FloatVector3Bits Axis(Level100FloatVector3Bits v, int axis, int word) => axis switch
    { 0 => v with { X = word }, 1 => v with { Y = word }, _ => v with { Z = word } };
    private static object? Do(Action action) { action(); return null; }
    private static object? Invoke(MethodInfo method, object?[] args)
    {
        try { return method.Invoke(null, args); }
        catch (TargetInvocationException error) when (error.InnerException is not null)
        { ExceptionDispatchInfo.Capture(error.InnerException).Throw(); throw; }
    }
    private static M Capture(Func<object?> action)
    {
        try { return new M { ["ok"] = true, ["value"] = action() }; }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException or NotSupportedException or IndexOutOfRangeException or NullReferenceException)
        { return new M { ["ok"] = false, ["error_type"] = error.GetType().Name,
            ["parameter"] = error is ArgumentException argument ? argument.ParamName ?? "" : "" }; }
    }
    private static Variant Pack(object? value)
    {
        if (value is null) return default;
        if (value is bool boolean) return boolean;
        if (value is int integer) return integer;
        if (value is uint unsigned) return (long)unsigned;
        if (value is string text) return text;
        if (value is Level100FloatVector3Bits vector) return Pack(new M { ["x"] = vector.X, ["y"] = vector.Y, ["z"] = vector.Z });
        if (value is RetailUnitAttackSelection attack) return Pack(new M { ["weapon_identity"] = attack.WeaponIdentity, ["spawner_identity"] = attack.SpawnerIdentity });
        if (value is RetailWeaponCycleResult cycle) return Pack(new M { ["current_weapon"] = cycle.CurrentWeapon, ["changed"] = cycle.Changed,
            ["clears_slow_movement"] = cycle.ClearsSlowMovement, ["loses_charge_on_new_weapon"] = cycle.LosesChargeOnNewWeapon, ["auto_zooms_out"] = cycle.AutoZoomsOut });
        if (value is RetailUnitWeaponSelectionCandidate c) return Pack(new M { ["identity"] = c.Identity, ["active_word"] = c.ActiveWord,
            ["target_mask"] = c.TargetMask, ["burst_counter"] = c.BurstCounter, ["burst_size"] = c.BurstSize, ["ready_at_time_float_bits"] = c.ReadyAtTimeFloatBits,
            ["minimum_range_float_bits"] = c.MinimumRangeFloatBits, ["maximum_range_float_bits"] = c.MaximumRangeFloatBits,
            ["minimum_target_height_float_bits"] = c.MinimumTargetHeightFloatBits, ["maximum_target_height_float_bits"] = c.MaximumTargetHeightFloatBits,
            ["has_current_mode"] = c.HasCurrentMode, ["uses_ballistic_arc"] = c.UsesBallisticArc, ["has_projectile_definition"] = c.HasProjectileDefinition });
        if (value is IDictionary dictionary)
        {
            using D result = new();
            foreach (DictionaryEntry entry in dictionary) { using Variant item = Pack(entry.Value); result.Add((string)entry.Key, item); }
            return result;
        }
        if (value is IEnumerable sequence)
        {
            using A result = new();
            foreach (object? entry in sequence) { using Variant item = Pack(entry); result.Add(item); }
            return result;
        }
        throw new NotSupportedException("Unexpected fixture transport: " + value.GetType().FullName);
    }
    private static M SourceHashes()
    {
        M result = new();
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "OnslaughtRebuild.Core"));
        foreach (string file in new[] { "RetailWeaponCharge.cs", "RetailWeaponStores.cs", "RetailWeaponSelection.cs", "RetailFloat24.cs" })
            result[file] = Hash(File.ReadAllBytes(Path.Combine(root, file)));
        return result;
    }
    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static string Owned(string value)
    {
        string path = Path.GetFullPath(value);
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data"));
        if (!Path.IsPathFullyQualified(value) || path != value || !path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.Ordinal)
            || File.Exists(path) || Directory.Exists(path) || new FileInfo(path).LinkTarget is not null)
            throw new ArgumentException("Output must be fresh and below this checkout's local-data, without a final symlink.");
        for (DirectoryInfo? parent = new(Path.GetDirectoryName(path)!); parent is not null; parent = parent.Parent)
        {
            if (parent.LinkTarget is not null) throw new ArgumentException("Output ancestry must not contain symlinks.");
            if (parent.FullName == root) break;
        }
        if (!Directory.Exists(Path.GetDirectoryName(path))) throw new ArgumentException("Caller must create the owned output directory.");
        return path;
    }
}
