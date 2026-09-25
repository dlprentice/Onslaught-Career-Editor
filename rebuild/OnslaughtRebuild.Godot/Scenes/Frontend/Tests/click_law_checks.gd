# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Laws = preload("res://Client/click_to_start_laws.gd")
var _checks: int = 0
var _failures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or DisplayServer.get_name() != "headless" or Engine.is_editor_hint():
		push_error("Two owned fixture/report paths and headless runtime are required.")
		quit(2)
		return
	var owner: String = ProjectSettings.globalize_path("res://../../local-data/").simplify_path().trim_suffix("/") + "/"
	if not args[0].begins_with(owner) or not args[1].begins_with(owner) or FileAccess.file_exists(args[1]):
		push_error("Report must be fresh under this worktree's local-data.")
		quit(2)
		return
	var source: FileAccess = FileAccess.open(args[0], FileAccess.READ)
	var fixture: Dictionary = source.get_var(false)
	source.close()
	for row: Dictionary in fixture.cases:
		var t: float = row.time
		var values: Array[float] = [Laws.splash_argument(t), Laws.splash_scale(t), Laws.splash_x(t), Laws.splash_y(t),
			Laws.slide_fade(t), Laws.slide_offset(t), Laws.slide_x(0, t), Laws.slide_x(1, t), Laws.title_scale(t), Laws.sixth_scale(t)]
		for index: int in range(values.size()):
			_check(_word(values[index]) == row.words[index], "float word time=" + str(t) + " field=" + str(index)
				+ " expected=" + str(row.words[index]) + " actual=" + str(_word(values[index])))
		_check(PackedInt64Array([Laws.title_outline_color(t), Laws.title_body_color(t), Laws.sixth_color(t)]) == row.colors, "Packed colors time=" + str(t))
		_check(Laws.prompt_visible(t) == row.prompt and Laws.title_visible(t) == row.title
			and Laws.sixth_visible(t) == row.sixth and Laws.idle_result_due(t) == row.idle, "Strict gates time=" + str(t))
	for row: Dictionary in fixture.advances:
		var bytes := PackedByteArray()
		bytes.resize(8)
		bytes.encode_double(0, Laws.advance(row.timer, row.page, row.delta))
		_check(bytes.decode_s64(0) == row.bits, "Double clock word")
	for row: Dictionary in fixture.glyphs:
		_check(_word(Laws.glyph_x(row.pass, row.width)) == row.bits, "Glyph centering Int32 width=" + str(row.width))
	var report: Dictionary = {"schema": 1, "checks": _checks, "failure_count": _failures.size(), "failures": _failures}
	var output: FileAccess = FileAccess.open(args[1], FileAccess.WRITE)
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("CLICK_LAW_CHECKS: ", JSON.stringify(report))
	quit(0 if _failures.is_empty() else 1)


func _check(condition: bool, message: String) -> void:
	_checks += 1
	if not condition:
		_failures.append(message)


func _word(value: float) -> int:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.decode_s32(0)
