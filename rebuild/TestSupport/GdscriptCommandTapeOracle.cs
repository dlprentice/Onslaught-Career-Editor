// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Text;
using System.Text.Json;
using OnslaughtRebuild.Core;

/// <summary>
/// Synthetic wire/input/reader fixtures from the current C# owner. The caller
/// supplies the existing tracked first-flight JSON unchanged; no file or retail
/// input is read here and no simulation expectation is refreshed.
/// </summary>
public static class GdscriptCommandTapeOracle
{
    public static object Build(string trackedScenarioJson)
    {
        var jsonCases = new List<object>();
        void JsonCase(string name, string? json)
        {
            try
            {
                CommandTape tape = CommandTapeCodec.Deserialize(json!);
                jsonCases.Add(new { name, json_hex = json is null ? null : Hex(Encoding.UTF8.GetBytes(json)),
                    expected = Success(tape) });
            }
            catch (Exception error)
            {
                jsonCases.Add(new { name, json_hex = json is null ? null : Hex(Encoding.UTF8.GetBytes(json)),
                    expected = Failure(error) });
            }
        }
        JsonCase("tracked_first_flight_unchanged", trackedScenarioJson);
        JsonCase("v5_minimal_defaults", Document());
        JsonCase("v4_explicit_upgrade", Document(schema: CommandTape.PreviousUpgradableSchemaVersion));
        JsonCase("escaped_known_property", Document().Replace("\"seed\"", "\"\\u0073eed\"", StringComparison.Ordinal));
        JsonCase("empty_spans_and_uint32_max", Document(seed: "4294967295", duration: "1000000"));
        JsonCase("hashes_keep_case", Document(extra: ",\"expectedFinalStateHash\":\"" + new string('A', 64)
            + "\",\"expectedTraceHash\":\"" + new string('f', 64) + "\""));
        JsonCase("held_charge_and_landing", Document("[{\"durationTicks\":2,\"chargeWeapon\":true,\"landingJets\":true}]"));
        JsonCase("all_edge_bits_one_tick", Document("[{\"durationTicks\":1,\"toggleMode\":true,\"fire\":true,\"reset\":true,\"skipPanning\":true,\"changeWeapon\":true,\"zoomIn\":true,\"zoomOut\":true}]"));
        string[] names = ["quote\" slash/ reverse\\ amp& html<> apostrophe' plus+ grave`", "zero\0middle\0end", "Aquila Ω 🚀 漢字", "\b\t\n\f\r\u000b\u001f", "\u0085x\u00a0\u1680\u2000\u2028\u2029\u202f\u205f\u3000"];
        foreach (string name in names)
            JsonCase("string:" + Hex(Encoding.Unicode.GetBytes(name)), Document(nameJson: JsonSerializer.Serialize(name)));
        JsonCase("all_ascii_in_one_name", Document(nameJson: JsonSerializer.Serialize(new string(Enumerable.Range(0, 128).Select(i => (char)i).ToArray()))));
        foreach (string? text in new string?[] { null, "", " \t\r\n", "\u00a0\u2000", "\v\f", "null", "[]", "[null]", "17", "true", "\"text\"", "{}" })
            JsonCase("shape:" + (text is null ? "null_argument" : Hex(Encoding.UTF8.GetBytes(text))), text);
        foreach (string token in new[] { "0", "-1", "-0", "4294967296", "18446744073709551615", "1.0", "1e0", "\"1\"", "null", "true" })
            JsonCase("seed:" + token, Document(seed: token));
        foreach (string token in new[] { "0", "-1", "1000001", "2147483648", "-2147483649", "1.0", "1e0", "null" })
            JsonCase("duration:" + token, Document(duration: token));
        foreach (string member in new[] { "schemaVersion", "name", "seed", "durationTicks", "expectedFinalStateHash", "expectedTraceHash", "spans" })
        {
            string original = member switch { "expectedFinalStateHash" or "expectedTraceHash" => ",\"" + member + "\":null", _ => "" };
            JsonCase("duplicate_root:" + member, Document(extra: original + ",\"" + member + "\":null"));
        }
        JsonCase("duplicate_escaped_root", Document(extra: ",\"\\u0073eed\":2"));
        JsonCase("duplicate_before_later_syntax_error", Document(extra: ",\"seed\":2,\"bad\":[1,]"));
        JsonCase("nested_duplicate_beats_unknown_member", Document(extra: ",\"unknown\":{\"x\":1,\"x\":2}"));
        JsonCase("case_variant_unknown", Document(extra: ",\"Seed\":1"));
        JsonCase("unknown_member", Document(extra: ",\"unknown\":0"));
        JsonCase("unknown_nul_member", Document(extra: ",\"nu\\u0000l\":0"));
        JsonCase("surrogate_member", Document(extra: ",\"\\ud800\":0"));
        JsonCase("surrogate_name_value", Document(nameJson: "\"\\ud800\""));
        JsonCase("surrogate_name_pair", Document(nameJson: "\"\\ud83d\\ude80\""));
        JsonCase("unsupported_schema_precedes_name_seed", Document(schema: "onslaught-rebuild-command-tape.v3", nameJson: "null", seed: "0"));
        JsonCase("missing_schema", "{\"name\":\"x\",\"seed\":1,\"durationTicks\":2,\"spans\":[]}");
        JsonCase("missing_name", "{\"schemaVersion\":\"" + CommandTape.CurrentSchemaVersion + "\",\"seed\":1,\"durationTicks\":2,\"spans\":[]}");
        foreach (string? name in new string?[] { null, "", " \t\r\n", "\u00a0\u0085\u3000", "\0" })
            JsonCase("name_admission:" + (name is null ? "null" : Hex(Encoding.Unicode.GetBytes(name))), Document(nameJson: JsonSerializer.Serialize(name)));
        JsonCase("null_spans", Document("null"));
        JsonCase("null_span", Document("[null]"));
        JsonCase("wrong_span_shape", Document("[true]"));
        JsonCase("missing_span_fields", Document("[{}]"));
        foreach (string field in new[] { "moveX", "moveZ", "lookX", "lookY", "lookXAnalogPermille", "lookYAnalogPermille" })
        {
            int tooLarge = field.Contains("Analog", StringComparison.Ordinal) ? 32768 : 128;
            int semanticBad = field.Contains("Analog", StringComparison.Ordinal) ? 1001 : 2;
            foreach (string value in new[] { tooLarge.ToString(), semanticBad.ToString(), "1.0", "null", "true" })
                JsonCase(field + ":" + value, Document("[{\"durationTicks\":1,\"" + field + "\":" + value + "}]"));
        }
        foreach (string field in new[] { "toggleMode", "fire", "reset", "landingJets", "skipPanning", "changeWeapon", "chargeWeapon", "zoomIn", "zoomOut" })
        {
            JsonCase("bool_type:" + field, Document("[{\"durationTicks\":1,\"" + field + "\":1}]"));
            JsonCase("duplicate_span:" + field, Document("[{\"durationTicks\":1,\"" + field + "\":false,\"" + field + "\":true}]"));
            JsonCase("duration_two:" + field, Document("[{\"durationTicks\":2,\"" + field + "\":true}]"));
        }
        foreach (string field in new[] { "chargeWeapon", "zoomIn", "zoomOut" })
        {
            JsonCase("v4_refuses_even_false:" + field, Document("[{\"durationTicks\":1,\"" + field + "\":false}]", schema: CommandTape.PreviousUpgradableSchemaVersion));
            JsonCase("v4_bad_field_type_precedes_fieldset:" + field, Document("[{\"durationTicks\":1,\"" + field + "\":null}]", schema: CommandTape.PreviousUpgradableSchemaVersion));
        }
        JsonCase("start_overflow_before_duration", Document("[{\"startTick\":2147483647,\"durationTicks\":2}]"));
        JsonCase("negative_start_before_overflow", Document("[{\"startTick\":-2147483648,\"durationTicks\":-1}]"));
        JsonCase("overlap_before_invalid_input", Document("[{\"durationTicks\":1},{\"startTick\":0,\"durationTicks\":1,\"moveX\":2}]"));
        JsonCase("input_before_edge_duration", Document("[{\"durationTicks\":2,\"moveX\":2,\"fire\":true}]"));
        foreach (string syntax in new[] { Document() + "false", Document().Replace("\"seed\":1", "\"seed\":01", StringComparison.Ordinal), Document(extra: ","), "/*x*/" + Document(), "\ufeff" + Document() })
            JsonCase("syntax:" + Hex(Encoding.UTF8.GetBytes(syntax)), syntax);
        for (int depth = 62; depth <= 66; depth++)
            JsonCase("unknown_depth:" + depth, Document(extra: ",\"nested\":" + new string('[', depth) + "0" + new string(']', depth)));

        var validation = new List<object>();
        void Direct(string name, CommandTape tape)
        {
            object expected;
            try { expected = Success(tape); }
            catch (Exception error) { expected = Failure(error); }
            validation.Add(new { name, tape = Record(tape), expected });
        }
        CommandTape Valid(IReadOnlyList<CommandSpan>? spans = null) => new(CommandTape.CurrentSchemaVersion, "direct", 1, 8, null, null, spans ?? []);
        Direct("raw_valid", Valid());
        Direct("raw_v4_not_implicitly_upgraded", Valid() with { SchemaVersion = CommandTape.PreviousUpgradableSchemaVersion });
        Direct("raw_null_schema", Valid() with { SchemaVersion = null! });
        Direct("raw_null_name", Valid() with { Name = null! });
        Direct("raw_seed_zero", Valid() with { Seed = 0 });
        Direct("raw_duration_before_hash", Valid() with { DurationTicks = 0, ExpectedFinalStateHash = "bad" });
        Direct("raw_final_hash_before_trace", Valid() with { ExpectedFinalStateHash = "bad", ExpectedTraceHash = "bad" });
        Direct("raw_trace_hash", Valid() with { ExpectedTraceHash = new string('g', 64) });
        Direct("raw_name_unpaired_surrogate_serialization", Valid() with { Name = "left\ud800right\udc00" });
        Direct("raw_null_spans", new(CommandTape.CurrentSchemaVersion, "direct", 1, 8, null, null, null));
        Direct("raw_null_span", Valid([null!]));
        Direct("raw_unsorted", Valid([new(2, 1, 0, 0), new(1, 1, 0, 0)]));
        Direct("raw_span_end_overflow", Valid([new(int.MaxValue, 1, 0, 0)]));
        Direct("raw_span_outside", Valid([new(7, 2, 0, 0)]));
        Direct("raw_span_negative_duration", Valid([new(0, -1, 0, 0)]));
        Direct("raw_bad_analog_before_edge", Valid([new(0, 2, 0, 0, Fire: true, LookYAnalogPermille: 1001)]));

        var inputs = new List<object>();
        void InputCase(string name, SimInput input)
        {
            object validationResult;
            try { input.Validate(); validationResult = new { ok = true }; }
            catch (Exception error) { validationResult = Failure(error); }
            inputs.Add(new { name, input = Input(input), validation = validationResult,
                actions = new ushort[] { 0, 1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 65535 }
                    .Select(action => new { action, value = input.HasAction((SimActions)action) }).ToArray() });
        }
        InputCase("idle", SimInput.Idle);
        foreach (int action in Enumerable.Range(0, 1025).Concat([65535, 32768, 65534]))
            InputCase("actions:" + action, new(0, 0, (SimActions)action));
        foreach (sbyte value in new sbyte[] { -128, -2, -1, 0, 1, 2, 127 })
        {
            InputCase("move_x:" + value, new(value, 0));
            InputCase("move_z:" + value, new(0, value));
            InputCase("look_x:" + value, new(0, 0, LookX: value));
            InputCase("look_y:" + value, new(0, 0, LookY: value));
        }
        foreach (short value in new short[] { -32768, -1001, -1000, 0, 1000, 1001, 32767 })
        {
            InputCase("analog_x:" + value, new(0, 0, LookXAnalogPermille: value));
            InputCase("analog_y:" + value, new(0, 0, LookYAnalogPermille: value));
        }
        InputCase("validation_order_all_invalid", new(2, 2, (SimActions)65535, 2, 2, 1001, 1001));
        InputCase("validation_order_look_before_actions", new(0, 0, (SimActions)65535, 0, 2));
        InputCase("validation_order_analog_before_actions", new(0, 0, SimActions.Cloak, 0, 0, 1001));

        var strings = new List<object>();
        void StringCase(string name, string value) => strings.Add(new { name, units = Units(value),
            canonical_hex = Hex(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(value))) });
        for (int unit = 0; unit < 256; unit++) StringCase("unit:" + unit, new string((char)unit, 1));
        foreach (int unit in new[] { 0x1680, 0x2000, 0x2028, 0x2029, 0x3000, 0x4e00, 0xd7ff, 0xd800, 0xdbff, 0xdc00, 0xdfff, 0xe000, 0xfffd, 0xffff })
            StringCase("unit:" + unit, new string((char)unit, 1));
        foreach (string value in names.Concat(["\ud83d\ude80", "\ud800\udc00", "\udbff\udfff", "\ud800\ud800\udc00\udc00"]))
            StringCase("sequence:" + Hex(Encoding.Unicode.GetBytes(value)), value);

        var readers = new List<object>();
        void Reader(string name, CommandTape? tape, int[] ticks)
        {
            Type type = typeof(Simulation).Assembly.GetType("OnslaughtRebuild.Core.CommandTapeReader")!;
            object? reader;
            try { reader = Activator.CreateInstance(type, [tape]); }
            catch (Exception error)
            {
                readers.Add(new { name, tape = tape is null ? null : Record(tape), construction = Failure(Unwrap(error)), steps = Array.Empty<object>() });
                return;
            }
            MethodInfo read = type.GetMethod("ReadNext")!;
            FieldInfo next = type.GetField("_nextTick", BindingFlags.Instance | BindingFlags.NonPublic)!;
            FieldInfo span = type.GetField("_spanIndex", BindingFlags.Instance | BindingFlags.NonPublic)!;
            var steps = new List<object>();
            foreach (int tick in ticks)
            {
                object result;
                try { result = new { ok = true, input = Input((SimInput)read.Invoke(reader, [tick])!) }; }
                catch (Exception error) { result = Failure(Unwrap(error)); }
                steps.Add(new { tick, result, next_tick = (int)next.GetValue(reader)!, span_index = (int)span.GetValue(reader)! });
            }
            readers.Add(new { name, tape = Record(tape!), construction = new { ok = true }, steps });
        }
        Reader("strict_order_gaps_edges_and_retries", new(CommandTape.CurrentSchemaVersion, "reader", 1, 8, null, null,
            [new(1, 2, 0, 1, LandingJets: true, ChargeWeapon: true), new(4, 1, 1, 0, Fire: true, ZoomIn: true), new(5, 2, -1, 0, LookXAnalogPermille: 999)]),
            [1, -1, 0, 0, 2, 1, 2, 3, 4, 5, 6, 7, 8, 7]);
        Reader("reader_does_not_add_validation", Valid([new(0, 2, 2, 0, Fire: true)]), [0, 1, 2, 3]);
        Reader("expired_empty_span_advances", Valid([new(0, 0, 0, 0), new(1, 1, 0, 1)]), [0, 1, 2]);
        Reader("partial_span_cursor_before_null_failure", Valid([new(0, 0, 0, 0), null!]), [0, 0, 1]);
        Reader("partial_span_cursor_before_overflow", Valid([new(0, 0, 0, 0), new(int.MaxValue, 1, 0, 0)]), [0, 0, 1]);
        Reader("null_spans", new(CommandTape.CurrentSchemaVersion, "reader", 1, 2, null, null, null), [1, 0, 0]);
        Reader("invalid_duration_rejects_before_null_spans", new(CommandTape.CurrentSchemaVersion, "reader", 1, 0, null, null, null), [0]);
        Reader("null_tape", null, [0]);
        CommandTape scenario = CommandTapeCodec.Deserialize(trackedScenarioJson);
        Reader("tracked_scenario_every_tick", scenario, Enumerable.Range(0, scenario.DurationTicks).Append(scenario.DurationTicks).ToArray());
        return new { json_cases = jsonCases, validation, inputs, strings, readers,
            constants = new { current_schema = CommandTape.CurrentSchemaVersion, previous_schema = CommandTape.PreviousUpgradableSchemaVersion,
                declared_actions = (ushort)SimInput.DeclaredActions, implemented_actions = (ushort)SimInput.ImplementedActions } };
    }

    private static string Document(string spans = "[]", string extra = "", string? schema = null,
        string nameJson = "\"json-admission\"", string seed = "1", string duration = "2") =>
        "{\"schemaVersion\":\"" + (schema ?? CommandTape.CurrentSchemaVersion) + "\",\"name\":" + nameJson
        + ",\"seed\":" + seed + ",\"durationTicks\":" + duration + ",\"spans\":" + spans + extra + "}";

    private static object Success(CommandTape tape)
    {
        string json = CommandTapeCodec.Serialize(tape);
        return new { ok = true, tape = Record(tape), canonical_hex = Hex(Encoding.UTF8.GetBytes(json)), identity = CommandTape.IdentityOf(tape) };
    }

    private static object Failure(Exception error)
    {
        error = Unwrap(error);
        string code = error switch
        {
            JsonException => "json",
            ArgumentOutOfRangeException when error.Message.Contains("unknown action bit", StringComparison.Ordinal) => "unknown_actions",
            ArgumentOutOfRangeException when error.Message.Contains("does not implement", StringComparison.Ordinal) => "unimplemented_actions",
            ArgumentOutOfRangeException => "input_range",
            ArgumentNullException => "null_argument",
            ArgumentException => "argument",
            OverflowException => "overflow",
            NullReferenceException => "null_reference",
            InvalidDataException when error.Message.StartsWith("Duplicate command tape JSON member", StringComparison.Ordinal) => "duplicate_member",
            InvalidDataException when error.Message.StartsWith("Unsupported command tape schema", StringComparison.Ordinal) => "schema",
            InvalidDataException when error.Message.StartsWith("Command tape name", StringComparison.Ordinal) => "name",
            InvalidDataException when error.Message.StartsWith("Command tape seed", StringComparison.Ordinal) => "seed",
            InvalidDataException when error.Message.StartsWith("Command tape duration", StringComparison.Ordinal) => "duration",
            InvalidDataException when error.Message.StartsWith("Expected final state", StringComparison.Ordinal) => "final_hash",
            InvalidDataException when error.Message.StartsWith("Expected trace", StringComparison.Ordinal) => "trace_hash",
            InvalidDataException when error.Message == "Command tape spans are required." => "spans_required",
            InvalidDataException when error.Message == "Command tape spans cannot contain null entries." => "null_span",
            InvalidDataException when error.Message.StartsWith("Command spans must", StringComparison.Ordinal) => "span_order",
            InvalidDataException when error.Message.StartsWith("Command span end tick", StringComparison.Ordinal) => "span_overflow",
            InvalidDataException when error.Message.StartsWith("Command span is outside", StringComparison.Ordinal) => "span_duration",
            InvalidDataException when error.Message.StartsWith("Command span contains", StringComparison.Ordinal) => "span_input",
            InvalidDataException when error.Message.StartsWith("ToggleMode, Fire", StringComparison.Ordinal) => "edge_duration",
            InvalidDataException when error.Message.StartsWith("A v4 command tape", StringComparison.Ordinal) => "v4_fieldset",
            InvalidDataException when error.Message.StartsWith("Command tape JSON did not", StringComparison.Ordinal) => "not_document",
            InvalidOperationException when error.Message.StartsWith("Command tape reader expected", StringComparison.Ordinal) => "reader_tick",
            InvalidOperationException => "invalid_operation",
            _ => error.GetType().Name,
        };
        return new { ok = false, error_type = error.GetType().Name, error_code = code,
            parameter = (error as ArgumentException)?.ParamName ?? "",
            inner_parameter = (error.InnerException as ArgumentException)?.ParamName ?? "" };
    }

    private static object Record(CommandTape tape) => new
    {
        schema_version = Units(tape.SchemaVersion), name = Units(tape.Name), seed = tape.Seed,
        duration_ticks = tape.DurationTicks, expected_final_state_hash = Units(tape.ExpectedFinalStateHash),
        expected_trace_hash = Units(tape.ExpectedTraceHash), spans = tape.Spans?.Select(span => span is null ? null : Span(span)).ToArray(),
    };

    private static object Span(CommandSpan span) => new
    {
        start_tick = span.StartTick, duration_ticks = span.DurationTicks, move_x = span.MoveX, move_z = span.MoveZ,
        toggle_mode = span.ToggleMode, fire = span.Fire, reset = span.Reset, look_x = span.LookX, look_y = span.LookY,
        look_x_analog_permille = span.LookXAnalogPermille, look_y_analog_permille = span.LookYAnalogPermille,
        landing_jets = span.LandingJets, skip_panning = span.SkipPanning, change_weapon = span.ChangeWeapon,
        charge_weapon = span.ChargeWeapon, zoom_in = span.ZoomIn, zoom_out = span.ZoomOut,
    };

    private static object Input(SimInput input) => new
    {
        move_x = input.MoveX, move_z = input.MoveZ, actions = (ushort)input.Actions,
        look_x = input.LookX, look_y = input.LookY, look_x_analog_permille = input.LookXAnalogPermille,
        look_y_analog_permille = input.LookYAnalogPermille,
    };
    private static int[]? Units(string? value) => value?.Select(unit => (int)unit).ToArray();
    private static string Hex(byte[] value) => Convert.ToHexString(value).ToLowerInvariant();
    private static Exception Unwrap(Exception value) => value is TargetInvocationException { InnerException: { } inner } ? inner : value;
}
