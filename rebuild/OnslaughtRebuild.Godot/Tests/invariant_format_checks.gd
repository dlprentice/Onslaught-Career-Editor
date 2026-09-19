# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const Formatter = preload("res://Client/invariant_int32_format.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed_sections: PackedStringArray = []


func _initialize() -> void:
    _run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
    counts[group] = int(counts.get(group, 0)) + 1
    if actual != expected:
        failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _check_oracle(cases: Array) -> void:
    _check("oracle", "nonempty fixture set", not cases.is_empty(), true)
    for row: Dictionary in cases:
        # The fixture loader is Godot JSON, whose numeric tokens are doubles.
        # Admit the exact Int32 range before the intentional integer conversion.
        var carrier: Variant = row.argument
        if typeof(carrier) != TYPE_FLOAT or not is_finite(carrier) or carrier != floor(carrier) or carrier < -2147483648 or carrier > 2147483647:
            _check("oracle", row.name + " argument carrier", false, true)
            continue
        var result: Dictionary = Formatter.format_composite(row.template, int(carrier))
        if row.unsupported:
            _check("bounded", row.name + " is accepted by .NET", row.ok, true)
            _check("bounded", row.name + " result", result.get("ok"), false)
            _check("bounded", row.name + " reason", result.get("error_type"), "UnsupportedFormat")
        else:
            _check("oracle", row.name + " admission", result.get("ok"), row.ok)
            if row.ok:
                _check("oracle", row.name + " exact text", result.get("value"), row.value)
            else:
                _check("oracle", row.name + " error class", result.get("error_type"), row.error_type)
        if not result.get("ok", false):
            _check("failure", row.name + " cannot carry a partial filename", result.has("value"), false)
            _check("failure", row.name + " diagnostic", str(result.get("error", "")).is_empty(), false)
    completed_sections.append("oracle")


func _check_admission() -> void:
    for value: Variant in [null, false, true, 1.0, "1", [], {}, -2147483649, 2147483648]:
        var result: Dictionary = Formatter.format_composite("f{0:D5}.png", value)
        _check("arguments", "invalid argument " + str(value), result.get("error_type"), "ArgumentException")
        _check("arguments", "invalid argument has no partial filename", result.has("value"), false)
    for template: Variant in [null, false, 1, 1.0, [], {}]:
        var result: Dictionary = Formatter.format_composite(template, 1)
        _check("arguments", "invalid template " + str(template), result.get("error_type"), "ArgumentException")
    for template: Variant in [null, "{0}", [123, 48, 125], PackedInt32Array([-1]), PackedInt32Array([65536])]:
        var result: Dictionary = Formatter.format_composite_units(template, 1)
        _check("raw_arguments", "invalid UTF16 carrier " + str(template), result.get("error_type"), "ArgumentException")
        _check("raw_arguments", "invalid UTF16 carrier has no partial filename", result.has("value"), false)
    _check("producer", "first frame", Formatter.format_composite("lost-toys-logo/f{0:D5}.png", 1).value, "lost-toys-logo/f00001.png")
    _check("producer", "expanded frame width", Formatter.format_composite("f{0:D5}.png", 100000).value, "f100000.png")
    _check("failure", "a rejected call cannot poison a later call", Formatter.format_composite("f{0:D5}.png", 12).value, "f00012.png")
    completed_sections.append("admission")


func _check_raw_oracle(cases: Array) -> void:
    _check("raw_oracle", "nonempty UTF16 fixture set", not cases.is_empty(), true)
    for row: Dictionary in cases:
        var carrier: Variant = row.argument
        if typeof(carrier) != TYPE_FLOAT or not is_finite(carrier) or carrier != floor(carrier) or carrier < -2147483648 or carrier > 2147483647:
            _check("raw_oracle", row.name + " argument carrier", false, true)
            continue
        var template := PackedInt32Array()
        var valid: bool = true
        for unit: Variant in row.templateUnits:
            if typeof(unit) != TYPE_FLOAT or not is_finite(unit) or unit != floor(unit) or unit < 0 or unit > 65535:
                valid = false
                break
            template.append(int(unit))
        if not valid:
            _check("raw_oracle", row.name + " template unit carrier", false, true)
            continue
        var before: PackedInt32Array = template.duplicate()
        var result: Dictionary = Formatter.format_composite_units(template, int(carrier))
        _check("raw_oracle", row.name + " immutable template", template, before)
        if row.unsupported:
            _check("raw_oracle", row.name + " accepted by .NET", row.ok, true)
            _check("raw_oracle", row.name + " bounded explicitly", result.get("error_type"), "UnsupportedFormat")
        else:
            _check("raw_oracle", row.name + " admission", result.get("ok"), row.ok)
            if row.ok:
                var expected := PackedInt32Array()
                for unit: Variant in row.valueUnits:
                    if typeof(unit) != TYPE_FLOAT or not is_finite(unit) or unit != floor(unit) or unit < 0 or unit > 65535:
                        valid = false
                        break
                    expected.append(int(unit))
                _check("raw_oracle", row.name + " expected units admitted", valid, true)
                _check("raw_oracle", row.name + " exact UTF16 units", result.get("value"), expected)
            else:
                _check("raw_oracle", row.name + " error class", result.get("error_type"), row.error_type)
        if not result.get("ok", false):
            _check("raw_failure", row.name + " cannot carry a partial filename", result.has("value"), false)
    completed_sections.append("raw_oracle")


func _check_dependency_boundary(report_path: String) -> void:
    var information: Dictionary = Formatter.dependency_info()
    var expected_source: String = ProjectSettings.globalize_path("res://").path_join(Formatter.SOURCE_RELATIVE_PATH).simplify_path()
    _check("dependency", "source checkout loaded", information.get("ok"), true)
    _check("dependency", "separate tools owner selected", information.get("mode"), "source_checkout")
    _check("dependency", "explicit absolute source path", information.get("path"), expected_source)
    _check("dependency", "source utility is outside the rebuild project", expected_source.begins_with(ProjectSettings.globalize_path("res://")), false)
    var absent_source: String = report_path + ".absent-format-dependency.gd"
    var absent_resource: String = "res://Tests/__absent_format_dependency__.gd"
    _check("dependency", "missing fixture is absent", FileAccess.file_exists(absent_source), false)
    _check("dependency", "missing resource fixture is absent", ResourceLoader.exists(absent_resource), false)
    var missing: Dictionary = Formatter._resolve_location(absent_source, absent_resource)
    _check("dependency", "absent dependency refuses explicitly", missing.get("error_type"), "MissingDependency")
    _check("dependency", "absence never returns a filename", missing.has("value"), false)
    _check("dependency", "existing source remains usable after separate missing-path probe", Formatter.format_composite("f{0:D5}.png", 1).get("value"), "f00001.png")
    completed_sections.append("dependency")


func _run() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() != 2 or not args[1].is_absolute_path() or FileAccess.file_exists(args[1]):
        push_error("Expected existing oracle and a new absolute owned report path.")
        quit(2)
        return
    var vectors: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
    if not vectors is Dictionary or not vectors.get("invariantFormat") is Dictionary:
        push_error("Missing invariantFormat oracle object.")
        quit(2)
        return
    var cases: Variant = vectors.invariantFormat.get("cases")
    var raw_cases: Variant = vectors.invariantFormat.get("rawCases")
    if not cases is Array or not raw_cases is Array:
        push_error("Missing invariantFormat cases.")
        quit(2)
        return
    _check_oracle(cases)
    _check_raw_oracle(raw_cases)
    _check_admission()
    _check_dependency_boundary(args[1])
    _check("completion", "oracle helper returned", completed_sections.has("oracle"), true)
    _check("completion", "raw oracle helper returned", completed_sections.has("raw_oracle"), true)
    _check("completion", "admission helper returned", completed_sections.has("admission"), true)
    _check("completion", "dependency helper returned", completed_sections.has("dependency"), true)
    var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(),
        "failures": failures, "completed": ["invariant_format"] if completed_sections.size() == 4 else []}
    var output := FileAccess.open(args[1], FileAccess.WRITE)
    if output == null:
        quit(2)
        return
    output.store_string(JSON.stringify(report, "\t"))
    output.close()
    print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
    quit(0 if failures.is_empty() else 1)
