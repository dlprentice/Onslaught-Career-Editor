# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Laws = preload("res://Client/main_menu_laws.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _cases_completed: int = 0
var _colors_completed: int = 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or DisplayServer.get_name() != "headless" or Engine.is_editor_hint(): quit(2); return
	if not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] \
			or FileAccess.file_exists(args[1]) or DirAccess.dir_exists_absolute(args[1]): quit(2); return
	var input: FileAccess = FileAccess.open(args[0], FileAccess.READ)
	if input == null: quit(2); return
	var fixture: Variant = input.get_var(false)
	input.close()
	if not fixture is Dictionary or fixture.get("schema") != 1 or fixture.get("completed") != ["main_menu_law_reference"] \
			or not fixture.get("cases") is Array or not fixture.get("colors") is Array \
			or fixture.cases.is_empty() or fixture.colors.is_empty() \
			or fixture.get("case_count") != fixture.cases.size() or fixture.get("color_count") != fixture.colors.size(): quit(2); return
	for index: int in range(fixture.cases.size()):
		var row: Dictionary = fixture.cases[index]
		var t: float = row.transition
		var seconds: float = row.seconds
		var values: Array[float] = [Laws.page_fade(t), Laws.icon_fade(t), Laws.underlay_alpha(t), Laws.reflection_scroll(seconds)]
		var decors: Array[Dictionary] = [Laws.left_decor(t), Laws.left_twin(t), Laws.right_decor(t), Laws.right_twin(t)]
		var matrix_words := PackedInt32Array()
		for decor_index: int in range(4):
			var decor: Dictionary = decors[decor_index]
			values.append_array([decor.scale, decor.rotation, decor.alpha])
			_check((1 if decor.draw else 0) == row.draws[decor_index], "draw predicate row=%d part=%d" % [index, decor_index])
			var first: Vector2 = Vector2.from_angle(decor.rotation)
			var second: Vector2 = Vector2.from_angle(F.value(decor.rotation + 0.0))
			matrix_words.append_array([_word(first.x), _word(first.y), _word(-second.y), _word(second.x)])
		for field: int in range(values.size()):
			_check(_word(values[field]) == row.words[field], "Single row=%d field=%d expected=%s actual=%s" % [index, field, row.words[field], _word(values[field])])
		for field: int in range(matrix_words.size()):
			_check(matrix_words[field] == row.matrices[field], "Transform2D Single row=%d field=%d expected=%s actual=%s" % [index, field, row.matrices[field], matrix_words[field]])
		var shadow: PackedFloat64Array = Laws.shadow_offset(seconds)
		var doubles := PackedFloat64Array([Laws.shadow_phase(seconds), shadow[0], shadow[1]])
		for field: int in range(3):
			_check(_double_word(doubles[field]) == row.double_words[field], "binary64 row=%d field=%d expected=%s actual=%s" % [index, field, row.double_words[field], _double_word(doubles[field])])
		_cases_completed += 1
	_check(_cases_completed == fixture.case_count, "Every expression case completed.")
	_completed.append("expressions")
	for row: Dictionary in fixture.colors:
		_check(Laws.label_base_color(row.selected, row.available) == row.base, "Selected/available packed color branch")
		_check(Laws.label_color(row.selected, row.available, row.fade) == row.label, "Wrapped label packed color")
		_check(Laws.selector_color(row.fade) == row.selector, "Selector packed alpha")
		_colors_completed += 1
	_check(_colors_completed == fixture.color_count, "Every packed color case completed.")
	_completed.append("packed_colors")
	var report: Dictionary = {"schema": 1, "checks": _checks, "completed": _completed,
		"cases": _cases_completed, "colors": _colors_completed, "failure_count": _failures.size(), "failures": _failures}
	var output: FileAccess = FileAccess.open(args[1], FileAccess.WRITE)
	if output == null: quit(2); return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("MAIN_MENU_LAW_CHECKS: ", JSON.stringify({"checks": _checks, "failure_count": _failures.size(), "completed": _completed}))
	quit(0 if _failures.is_empty() else 1)


func _check(condition: bool, message: String) -> void:
	_checks += 1
	if not condition: _failures.append(message)


static func _word(value: float) -> int:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.decode_s32(0)


static func _double_word(value: float) -> int:
	var bytes := PackedByteArray()
	bytes.resize(8)
	bytes.encode_double(0, value)
	return bytes.decode_s64(0)


static func _owned_path(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") or not path.begins_with(owned + "/"): return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	var parts: PackedStringArray = path.trim_prefix(owned + "/").split("/", false)
	for index: int in range(parts.size()):
		if directory.is_link(parts[index]): return false
		if index < parts.size() - 1 and directory.change_dir(parts[index]) != OK: return false
	return not parts.is_empty()
