# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Direct numerical comparison plus the existing unchanged click fixture.
const Cosine = preload("res://Scenes/Shared/retail_cosf.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const REQUIRED: Array[String] = ["dependency", "cosine", "fma", "click", "refusals"]
var _completed: Array[String] = []
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _report: String
var _finished: bool = false


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 3 or Engine.is_editor_hint() or DisplayServer.get_name() != "headless":
		quit(2)
		return
	for path: String in args:
		if not _owned_path(path): quit(2); return
	if FileAccess.file_exists(args[2]): quit(2); return
	_report = args[2]
	create_timer(120).timeout.connect(func() -> void:
		if not _finished: _failures.append({"group": "completion", "name": "timeout"}); _finish())
	var reference: Dictionary = _read(args[0])
	var click: Dictionary = _read(args[1])
	if reference.get("completed") != ["cosf_reference"] or reference.get("schema") != 1 or click.get("schema") != 1:
		_failures.append({"group": "completion", "name": "fixture incomplete"})
		_finish()
		return
	var dependency: Dictionary = Cosine.dependency_info()
	_check("dependency", "source admitted", dependency.get("ok"), true)
	if not dependency.get("ok", false): _finish(); return
	_check("dependency", "outside subtree source mode", dependency.mode, "source_checkout")
	_check("dependency", "explicit retained path", dependency.path, ProjectSettings.globalize_path("res://../../tools/godot_compat/arm_cosf.gd").simplify_path())
	var implementation: GDScript = load(dependency.path) as GDScript
	if implementation == null: _finish(); return
	_completed.append("dependency")
	if _cosines(reference): _completed.append("cosine")
	if _fmas(implementation, reference.fmas): _completed.append("fma")
	if _click_values(click.cases): _completed.append("click")
	if _refusals(): _completed.append("refusals")
	implementation = null
	await process_frame
	_finish()


func _cosines(reference: Dictionary) -> bool:
	_check("cosine", "same input/output count", reference.inputs.size(), reference.outputs.size())
	for i: int in range(reference.inputs.size()):
		var word: int = reference.inputs[i]
		var result: Dictionary = Cosine.cos_bits(word)
		_check("cosine", "admission %08x" % (word & 0xffffffff), result.get("ok"), true)
		if not result.get("ok", false): return false
		_check("cosine", "raw %08x" % (word & 0xffffffff), result.bits, reference.outputs[i])
	return true


func _fmas(implementation: GDScript, cases: Array) -> bool:
	for i: int in range(cases.size()):
		var row: PackedInt64Array = cases[i]
		var a: float = _double(row[0])
		var b: float = _double(row[1])
		var c: float = _double(row[2])
		var value: float = implementation.call("_fma", a, b, c)
		_check("fma", "%d (%016x,%016x,%016x)" % [i, row[0], row[1], row[2]], _word64(value), row[3])
	return true


func _click_values(cases: Array) -> bool:
	for i: int in range(cases.size()):
		var row: Dictionary = cases[i]
		var timer: float = row.time
		var argument: float = F.value(timer) if timer <= 1.0 else 1.0
		var result: Dictionary = Cosine.cosine(F.value(argument * PI_SINGLE()))
		_check("click", "%d cosine admission" % i, result.get("ok"), true)
		if not result.get("ok", false): return false
		var scale: float = F.value(F.value(F.value(result.value + 1.0) * 0.375) + 0.46875)
		var x: float = F.value(F.value(558.0 - F.value(scale * 238.0)) - 126.4375)
		var y: float = F.value(F.value(18.0 - F.value(scale * -222.0)) - -117.9375)
		_check("click", "%d scale time=%s" % [i, str(timer)], _word32(scale), row.words[1])
		_check("click", "%d x" % i, _word32(x), row.words[2])
		_check("click", "%d y" % i, _word32(y), row.words[3])
	return true


func _refusals() -> bool:
	for word: Variant in [null, true, false, 0.0, "0", [], {}, 0x80000000, -0x80000001]:
		var result: Dictionary = Cosine.cos_bits(word)
		_check("refusal", "invalid carrier has no success", result.get("ok"), false)
		_check("refusal", "invalid carrier exception", result.get("error_type"), "ArgumentException")
		_check("refusal", "invalid carrier has no output", result.has("bits"), false)
	var missing: Dictionary = Cosine._resolve_location("/nonexistent/onslaught-cosine-dependency.gd", "res://NoSuchCosine.gd")
	_check("refusal", "missing dependency explicit", missing.get("error_type"), "MissingDependency")
	_check("refusal", "missing dependency cannot succeed", missing.get("ok"), false)
	return true


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = _counts.get(group, 0) + 1
	if actual == expected: return
	var failure: Dictionary = {"group": group, "name": name, "actual": str(actual), "expected": str(expected)}
	_failures.append(failure)
	if _failures.size() <= 12: push_error(JSON.stringify(failure))


func _finish() -> void:
	if _finished: return
	_finished = true
	for group: String in REQUIRED:
		if not _completed.has(group): _failures.append({"group": "completion", "name": "missing " + group})
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "counts": _counts, "completed": _completed, "failures": _failures}
	var output := FileAccess.open(_report, FileAccess.WRITE)
	if output == null: quit(2); return
	output.store_string(JSON.stringify(report, "  "))
	output.close()
	print("RETAIL_COSF_CHECKS: ", JSON.stringify({"failure_count": _failures.size(), "counts": _counts, "completed": _completed}), "; ", _report)
	quit(0 if _failures.is_empty() else 1)


static func _read(path: String) -> Dictionary:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null: return {}
	var value: Variant = file.get_var(false)
	file.close()
	return value if value is Dictionary else {}


static func _owned_path(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") or not path.begins_with(owned + "/"): return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	var parts: PackedStringArray = path.trim_prefix(owned + "/").split("/", false)
	for i: int in range(parts.size()):
		if directory.is_link(parts[i]): return false
		if i < parts.size() - 1 and directory.change_dir(parts[i]) != OK: return false
	return not parts.is_empty()


static func PI_SINGLE() -> float: return PackedInt32Array([0x40490fdb]).to_byte_array().decode_float(0)
static func _word32(value: float) -> int: return PackedFloat32Array([value]).to_byte_array().decode_s32(0)
static func _word64(value: float) -> int: return PackedFloat64Array([value]).to_byte_array().decode_s64(0)
static func _double(word: int) -> float: return PackedInt64Array([word]).to_byte_array().decode_double(0)
