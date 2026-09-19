// SPDX-License-Identifier: GPL-3.0-or-later
using System.Globalization;
using System.Text;
using OnslaughtRebuild.Client;

// Synthetic source text only. Existing Client is the temporary migration
// oracle; these cases establish no new retail behavior or random phase.
internal static class GdscriptParticleEffectOracle
{
    internal static object Build()
    {
        var cases = new List<object>();
        void Case(string name, string? effect, params string[] records)
        {
            string source = Set(records);
            object expected;
            try { expected = new { ok = true, value = Project(ParticleEffectResolver.Resolve(ParticleSetFile.Parse(source), effect!)) }; }
            catch (Exception error) { expected = Failure(error); }
            cases.Add(new { name, source = Raw(source), effect_name = Raw(effect), expected });
        }
        Case("direct", "Sprite", Sprite());
        Case("null root", null, Sprite());
        Case("empty root", "", Sprite());
        Case("missing root", "missing\0\ud800", Sprite());
        foreach (int size in new[] { int.MinValue, -1, 0, 1, 2, 3, 4, 5, int.MaxValue })
            Case("atlas-" + size, "Sprite", Sprite(changes: new() { ["Texture_Size"] = size.ToString(CultureInfo.InvariantCulture) }));
        foreach (int animation in new[] { -1, 0, 1, 2, 3, int.MaxValue })
            Case("animation-" + animation, "Sprite", Sprite(changes: new() { ["Anim_Type"] = animation.ToString(CultureInfo.InvariantCulture) }));
        foreach (string texture in new[] { "C:\\dev\\PARTICLE\\Fire.TGA", "mixed\\slash/TÉXTÜRE.Σ.TGA", "NO.DIRECTORY", "trailing/", "",
            "IİıſKΩÅẞᾈԱႠᲐ\0\ud800\udfff🚀𐐀𞤀.TGA", "C:\\nul\0folder\\FILE\0NAME.TGA" })
            Case("texture-" + cases.Count, "Sprite", Sprite(changes: new() { ["Texture"] = texture }));
        Case("no texture ignores malformed fields", "Sprite", Record(1, "Sprite", "Texture_Size nonsense", "Blend_Mode nope"));
        Case("texture field with no value", "Sprite", Record(1, "Sprite", "Texture", "Texture_Size nope"));
        Case("nullable/missing optional defaults", "Sprite", Sprite(changes: new() { ["Random_Start_Frame"] = null, ["Colour_Range"] = null, ["Modifier"] = null }));
        Case("sprite raw values and ignored radius modifier", "Sprite", Sprite(changes: new() { ["Blend_Mode"] = "2", ["Texture_Number"] = "-1",
            ["End_Frame"] = "2147483647", ["Random_Start_Frame"] = "-1", ["Life"] = "-2", ["Radius"] = "-0 Radius Function",
            ["Final_Radius"] = "-Infinity", ["Life_Pct"] = "NaN", ["Fade_Col"] = "-7", ["Axis_Aligned"] = "2147483647",
            ["Gravity"] = "-1", ["Velocity_Damp"] = "1.000000059604644775390625", ["Anim_Speed"] = "1E-45" }));
        foreach (int type in new[] { int.MinValue, -1, 0, 3, 5, 7, 8, 9, 10, 11, 13, 14, int.MaxValue })
            Case("undrawn type-" + type, "Root", Record(type, "Root"));

        Case("timeline ordering, missing, NONE", "Root", Timeline("Root", ("Sprite", "4"), ("NONE", "not an integer"), ("Absent", "7"), ("Sprite", "-5")), Sprite());
        Case("timeline mismatch", "Root", Record(6, "Root", "Num_Entries 2", "Particle_Descriptor Sprite", "Time 0"), Sprite());
        Case("timeline missing time field", "Root", Record(6, "Root", "Num_Entries 1", "Particle_Descriptor Sprite", "Time"), Sprite());
        Case("timeline negative declared", "Root", Record(6, "Root", "Num_Entries -1"));
        Case("timeline parses time before missing lookup", "Root", Timeline("Root", ("Absent", "bad")));
        Case("timeline none does not parse time", "Root", Timeline("Root", ("NONE", "bad")));
        Case("self cycle", "Root", Timeline("Root", ("Root", "0")));
        Case("mutual cycle, sibling remains admitted", "Root", Timeline("Root", ("Inner", "0"), ("Sprite", "1"), ("Inner", "3")),
            Timeline("Inner", ("Root", "2"), ("Sprite", "4")), Sprite());
        Case("timeline unchecked offset", "Root", Timeline("Root", ("Inner", "2147483647")), Timeline("Inner", ("Emitter", "1")), Emitter("Emitter", "Sprite", "1", "1"), Sprite());
        Case("emitter unchecked offset", "Root", Timeline("Root", ("Emitter", "2147483647")), Emitter("Emitter", "Sprite", "1", "1"), Sprite());
        Case("duplicate names first record wins", "Root", Timeline("Root", ("Sprite", "0")), Sprite(), Sprite(changes: new() { ["Anim_Type"] = "bad" }));
        Case("raw names/cycle/path", "R\0\ud800", Timeline("R\0\ud800", ("C\0🚀", "0")), Timeline("C\0🚀", ("R\0\ud800", "1"), ("S\0\udfff", "2")), Sprite("S\0\udfff"));

        foreach ((string rate, string life) in new[] { ("0", "0"), ("-0", "2"), ("0.2", "4"), ("0.1", "8"), ("0.1", "9"), ("0.5", "3"),
            ("1.25", "4"), ("80", "0"), ("0.33333334", "2"), ("1", "-2"), ("0.2", "-2"), ("-1", "2"), ("-0.1", "2"),
            ("1E-30", "0"), ("-1E+20", "0"), ("NaN", "0"), ("Infinity", "0"), ("-Infinity", "0") })
            Case("emission-" + rate + "/" + life, "Emitter", Emitter("Emitter", "Sprite", rate, life), Sprite());
        Case("missing emitter child ignores malformed reads", "Emitter", Record(2, "Emitter", "Particle_Descriptor Absent", "Life invalid"));
        Case("NONE emitter child ignores malformed reads", "Emitter", Record(2, "Emitter", "Particle_Descriptor NONE", "Life invalid"));
        Case("absent emitter child ignores malformed reads", "Emitter", Record(2, "Emitter", "Life invalid"));
        Case("nested emitter repeats complete schedules", "Outer", Emitter("Outer", "Inner", "1", "2"), Emitter("Inner", "Sprite", "2", "2"), Sprite());
        Case("single outer start is reused", "Root", Timeline("Root", ("Outer", "7")), Emitter("Outer", "Inner", "0.5", "1"), Emitter("Inner", "Sprite", "1", "1"), Sprite());
        Case("timeline resets incoming emitter context", "Outer", Emitter("Outer", "Root", "3", "0"), Timeline("Root", ("Sprite", "9")), Sprite());
        Case("FoR resets incoming context and preserves initial/death order", "Outer", Emitter("Outer", "System", "3", "0"),
            Record(12, "System", "Initial Sprite", "Death Sprite", "Mover Some Mover"), Sprite());
        Case("FoR missing references", "System", Record(12, "System", "Initial Lost Initial", "Death Lost Death", "Mover Missing Mover"));
        Case("FoR NONE references", "System", Record(12, "System", "Initial NONE", "Death NONE", "Mover NONE"));
        Case("emitter self cycle", "Emitter", Emitter("Emitter", "Emitter", "3", "0"));
        Case("all unresolved entries retain order", "Emitter", Emitter("Emitter", "Sprite", "1 Rate Curve", "-2",
            new() { ["Mover"] = "Mover\0Name", ["Shape"] = "Missing Shape" }), Sprite(changes: new() { ["Colour_Range"] = "Missing Colour", ["Modifier"] = "Sprite Modifier" }));
        Case("shape and colour fields, modifiers remain provisional", "Emitter", Emitter("Emitter", "Sprite", "2", "0", new() { ["Shape"] = "Shape",
            ["Initial_Velocity_X"] = "-0 Ignored X", ["Initial_Velocity_Y"] = "NaN Ignored Y", ["Initial_Velocity_Z"] = "1.25 NONE",
            ["Outward_Velocity"] = "-2 Ignored Outward", ["Velocity_Randomness"] = "0.375 Ignored By Direct Reader" }),
            Sprite(changes: new() { ["Colour_Range"] = "Colour" }), Shape(), Colour());
        Case("shape wrong descriptor type still reads fields", "Emitter", Emitter("Emitter", "Sprite", "1", "0", new() { ["Shape"] = "Shape" }), Shape(type: 11), Sprite());
        Case("shape missing Hollow means false", "Emitter", Emitter("Emitter", "Sprite", "1", "0", new() { ["Shape"] = "Shape" }), Shape(omitHollow: true), Sprite());
        Case("colour wrong descriptor type still reads fields", "Sprite", Sprite(changes: new() { ["Colour_Range"] = "Colour" }), Colour(type: 13));
        Case("colour missing field fails before sprite Blend_Mode", "Sprite", Sprite(changes: new() { ["Colour_Range"] = "Colour", ["Blend_Mode"] = "bad" }), Record(5, "Colour"));
        Case("full cap then malformed sprite is never read", "Root", Timeline("Root", ("Emitter", "0"), ("Bad", "1")), Emitter("Emitter", "Sprite", "300", "0"), Sprite(), Record(1, "Bad", "Texture bad.tga"));
        Case("cap split across siblings", "Root", Timeline("Root", ("First", "0"), ("Second", "1"), ("Third", "2")),
            Emitter("First", "Sprite", "200", "0"), Emitter("Second", "Sprite", "100", "0"), Emitter("Third", "Sprite", "1", "0"), Sprite());
        Case("nested visits retain omissions after cap", "Outer", Emitter("Outer", "Inner", "3", "0"), Emitter("Inner", "Sprite", "130 Curve", "0"), Sprite());

        Case("selector direct tie", "Choice", Selector("Choice", [1, 1, 1, 1]), Sprite("A"), Sprite("B"), Sprite("C"), Sprite("D"));
        foreach (int count in new[] { 1, 2, 3, 7, 20, 257 })
            Case("selector weighted-" + count, "Emitter", Emitter("Emitter", "Choice", count.ToString(CultureInfo.InvariantCulture), "0"),
                Selector("Choice", [1, 3, 2, 4]), Sprite("A"), Sprite("B"), Sprite("C"), Sprite("D"));
        Case("selector missing and zero branches", "Emitter", Emitter("Emitter", "Choice", "3", "0"),
            Selector("Choice", [1, 0, -1, 2], ["Missing", "A", "B", "NONE"]), Sprite("A"), Sprite("B"));
        Case("selector validates weight even with NONE child", "Choice", Record(4, "Choice", "Particle_Descriptor_0 NONE", "Probability_0 bad"));
        Case("selector sum wraps zero", "Choice", Selector("Choice", [1073741824, 1073741824, 1073741824, 1073741824]));
        Case("selector negative wrapped sum bounded", "Emitter", Emitter("Emitter", "Choice", "3", "0"), Selector("Choice", [int.MaxValue, 1, 0, 0]), Sprite("A"), Sprite("B"));
        Case("selector positive wrapped sum", "Emitter", Emitter("Emitter", "Choice", "3", "0"), Selector("Choice", [int.MaxValue, int.MaxValue, int.MaxValue, 0]), Sprite("A"), Sprite("B"), Sprite("C"));
        Case("selector out-of-range double cast bounded", "Emitter", Emitter("Emitter", "Choice", "3", "0"), Selector("Choice", [int.MaxValue, int.MaxValue, 0, 0]), Sprite("A"), Sprite("B"));
        Case("selector passes selected start prefix into nested emitter", "Outer", Emitter("Outer", "Choice", "1", "4"), Selector("Choice", [1, 2, 0, 0], ["Inner", "Sprite", "NONE", "NONE"]),
            Emitter("Inner", "Sprite", "1", "1"), Sprite());
        Case("selector cycle", "Choice", Selector("Choice", [1, 0, 0, 0], ["Choice", "NONE", "NONE", "NONE"]));

        foreach (string field in new[] { "Texture_Size", "Blend_Mode", "Texture_Number", "End_Frame", "Anim_Type", "Anim_Speed", "Life", "Radius",
            "Final_Radius", "Life_Pct", "Fade_Col", "Axis_Aligned", "Gravity", "Velocity_Damp" })
        {
            Case("missing required sprite field-" + field, "Sprite", Sprite(changes: new() { [field] = null }));
            Case("malformed required sprite field-" + field, "Sprite", Sprite(changes: new() { [field] = "bad" }));
        }
        foreach (string field in new[] { "Emit_Per_Turn", "Life", "Initial_Velocity_X", "Initial_Velocity_Y", "Initial_Velocity_Z", "Outward_Velocity", "Velocity_Randomness" })
            Case("malformed emitter field-" + field, "Emitter", Emitter("Emitter", "Sprite", "1", "0", new() { [field] = "bad" }), Sprite());

        var atlas = new List<object>();
        foreach (int size in new[] { int.MinValue, -1, 0, 1, 2, 3, 4, 5, int.MaxValue })
        {
            object expected;
            try { expected = new { ok = true, value = ParticleEffectResolver.AtlasGridSide(size) }; }
            catch (Exception error) { expected = Failure(error); }
            atlas.Add(new { value = size, expected });
        }
        var words = new uint[] { 0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000, 0x3f800000, 0xbf800000,
            0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001, 0x7f800001, 0xff800001 };
        object[] quad = words.Select(word => (object)new { input_bits = word, output_bits = Word(ParticleEffectResolver.BillboardQuadSide(BitConverter.UInt32BitsToSingle(word))) }).ToArray();
        var totals = new List<object>();
        var template = ParticleEffectResolver.Resolve(ParticleSetFile.Parse(Set(Sprite())), "Sprite").Layers[0];
        foreach (int[] counts in new[] { Array.Empty<int>(), new[] { 1, 2, 3 }, new[] { int.MaxValue, 1 }, new[] { int.MinValue, -1 }, new[] { -1, 0, 4 } })
        {
            var plan = new ParticleEffectPlan("Plan", (ParticleDescriptorType)(-1), counts.Select(count => template with { InstanceCount = count }).ToArray(), []);
            totals.Add(new { counts, expected = plan.TotalInstances });
        }

        // Compact exhaustive protocol: absent scalars mean identity. The test
        // visits every valid Unicode scalar; NUL/unpaired UTF-16 are tested as
        // sequences above, never passed through a lossy native String carrier.
        var lower = new List<int[]>();
        for (int scalar = 0; scalar <= 0x10ffff; scalar++)
        {
            if (scalar is >= 0xd800 and <= 0xdfff) continue;
            string input = char.ConvertFromUtf32(scalar);
            string output = input.ToLowerInvariant();
            int changed = char.ConvertToUtf32(output, 0);
            if (changed != scalar) lower.Add([scalar, changed]);
        }
        return new { cases, atlas, quad, totals, lowercase = new { maximum_scalar = 0x10ffff, mappings = lower },
            constants = new { turns = ParticleEffectResolver.GameTurnsPerSecond, blend = ParticleEffectResolver.BlendModeSelectsShippedTextureFormat,
                instances = ParticleEffectResolver.MaximumInstancesPerEffect, radius_bits = Word(ParticleEffectResolver.AuthoredRadiusIsHalfTheQuadSide) },
            culture = CultureInfo.CurrentCulture.Name,
            nonterminating_source = Raw(Set(Emitter("Emitter", "Sprite", "0", int.MaxValue.ToString(CultureInfo.InvariantCulture)), Sprite())) };
    }

    private static string Record(int type, string name, params string[] lines) =>
        "Particle_Descriptor_Type " + type.ToString(CultureInfo.InvariantCulture) + "\r\nParticle_Descriptor_Name " + name + "\r\n" +
        string.Concat(lines.Select(line => line + "\r\n")) + ParticleSetFile.RecordSeparator + "\r\n";
    private static string Set(params string[] records) => "ParticleSystemEd_File_synthetic\r\nFile_Version 1.000000\r\nNum_Particle_Descriptors " +
        records.Length.ToString(CultureInfo.InvariantCulture) + "\r\n" + string.Concat(records);
    private static string Changed(int type, string name, Dictionary<string, string?> fields, Dictionary<string, string?>? changes)
    {
        if (changes is not null) foreach ((string key, string? value) in changes) { if (value is null) fields.Remove(key); else fields[key] = value; }
        return Record(type, name, fields.Select(field => field.Key + " " + field.Value).ToArray());
    }
    private static string Sprite(string name = "Sprite", Dictionary<string, string?>? changes = null) => Changed(1, name, new() {
        ["Texture"] = "C:\\synthetic\\PARTICLE\\Fire.TGA", ["Texture_Size"] = "2", ["Blend_Mode"] = "0", ["Texture_Number"] = "1", ["End_Frame"] = "15",
        ["Anim_Type"] = "1", ["Anim_Speed"] = "1.4", ["Random_Start_Frame"] = "0", ["Life"] = "10", ["Radius"] = "0.3 NONE", ["Final_Radius"] = "1.5",
        ["Life_Pct"] = "0.75", ["Fade_Col"] = "1", ["Axis_Aligned"] = "0", ["Gravity"] = "0", ["Velocity_Damp"] = "0.125", ["Colour_Range"] = "NONE", ["Modifier"] = "NONE" }, changes);
    private static string Emitter(string name, string child, string rate, string life, Dictionary<string, string?>? changes = null) => Changed(2, name, new() {
        ["Particle_Descriptor"] = child, ["Emit_Per_Turn"] = rate, ["Life"] = life, ["Shape"] = "NONE", ["Mover"] = "NONE", ["Initial_Velocity_X"] = "1 NONE",
        ["Initial_Velocity_Y"] = "2 NONE", ["Initial_Velocity_Z"] = "3 NONE", ["Outward_Velocity"] = "0.5 NONE", ["Velocity_Randomness"] = "0.25 NONE" }, changes);
    private static string Timeline(string name, params (string Child, string Time)[] entries) => Record(6, name,
        new[] { "Num_Entries " + entries.Length.ToString(CultureInfo.InvariantCulture) }.Concat(entries.SelectMany(entry => new[] { "Particle_Descriptor " + entry.Child, "Time " + entry.Time, "Transmit_FoR 0" })).ToArray());
    private static string Selector(string name, int[] weights, string[]? names = null) => Record(4, name,
        Enumerable.Range(0, 4).SelectMany(index => new[] { "Particle_Descriptor_" + index + " " + (names ?? ["A", "B", "C", "D"])[index],
            "Probability_" + index + " " + weights[index].ToString(CultureInfo.InvariantCulture) }).ToArray());
    private static string Shape(int type = 7, bool omitHollow = false) => Changed(type, "Shape", new() {
        ["Type"] = "-1", ["Ring_Axis"] = "2", ["Hemisphere"] = "-2", ["Num_Particles"] = "7", ["Radius"] = "1.5 Ignored Radius", ["Hollow"] = "-1",
        ["RandomSX"] = "-0", ["RandomSY"] = "2.5", ["RandomSZ"] = "-3.5" }, omitHollow ? new() { ["Hollow"] = null } : null);
    private static string Colour(int type = 5) => Record(type, "Colour", "Start_Red 0.5 Curve", "Start_Green 1 NONE", "Start_Blue -0 NONE",
        "End_Red 2 NONE", "End_Green -1 NONE", "End_Blue 0.25 NONE", "Transition_Red 0.1 NONE", "Transition_Green 0.2 NONE", "Transition_Blue 0.3 NONE",
        "Use_End -1", "Use_Transition 2", "Transition_Point 0.375");
    private static object Failure(Exception error) => new { ok = false, error_type = error.GetType().Name,
        parameter = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
    private static int[]? Raw(string? value) => value?.Select(c => (int)c).ToArray();
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static object Vector((float X, float Y, float Z) value) => new { x_bits = Word(value.X), y_bits = Word(value.Y), z_bits = Word(value.Z) };
    private static object Rgb((float R, float G, float B) value) => new { r_bits = Word(value.R), g_bits = Word(value.G), b_bits = Word(value.B) };
    private static object? ShapeValue(ParticleEmissionShape? value) => value is not { } shape ? null : new { name = Raw(shape.Name), type_id = shape.TypeId,
        ring_axis = shape.RingAxis, hemisphere = shape.Hemisphere, num_particles = shape.NumParticles, radius_bits = Word(shape.Radius), hollow = shape.Hollow, random_scale = Vector(shape.RandomScale) };
    private static object? ColourValue(ParticleColourRange? value) => value is not { } colour ? null : new { name = Raw(colour.Name), start = Rgb(colour.Start), end = Rgb(colour.End),
        transition = Rgb(colour.Transition), use_end = colour.UseEnd, use_transition = colour.UseTransition, transition_point_bits = Word(colour.TransitionPoint) };
    private static object Project(ParticleEffectPlan plan) => new { effect_name = Raw(plan.EffectName), root_type = (int)plan.RootType, total_instances = plan.TotalInstances,
        unimplemented = plan.Unimplemented.Select(Raw).ToArray(), layers = plan.Layers.Select(layer => new {
            descriptor_name = Raw(layer.DescriptorName), path = Raw(layer.Path), texture_name = Raw(layer.TextureName), blend_mode = layer.BlendMode,
            atlas_columns = layer.AtlasColumns, atlas_rows = layer.AtlasRows, start_cell = layer.StartCell, end_cell = layer.EndCell, animation_mode = (int)layer.AnimationMode,
            animation_cells_per_turn_bits = Word(layer.AnimationCellsPerTurn), random_start_cell = layer.RandomStartCell, life_turns = layer.LifeTurns,
            start_radius_bits = Word(layer.StartRadius), final_radius_bits = Word(layer.FinalRadius), life_fraction_bits = Word(layer.LifeFraction), fade_colour = layer.FadeColour,
            axis_aligned = layer.AxisAligned, gravity = layer.Gravity, velocity_damp_bits = Word(layer.VelocityDamp), colour_range = ColourValue(layer.ColourRange),
            instance_count = layer.InstanceCount, start_turns = layer.StartTurns, shape = ShapeValue(layer.Shape), initial_velocity = Vector(layer.InitialVelocity),
            outward_velocity_bits = Word(layer.OutwardVelocity), velocity_randomness_bits = Word(layer.VelocityRandomness) }).ToArray() };
}
