# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Host admission contracts: launch options, explicit career selections, the
## scripted smoke input and capture-rig arguments. Reads only the tracked gold
## career fixture; writes only the report. Usage (standard engine, headless):
##   --script res://Tests/host_checks.gd -- <gold_career_save.bin> <report.json>
const LaunchOptions = preload("res://Client/launch_options.gd")
const CareerSelections = preload("res://Client/career_selections.gd")
const CareerSave = preload("res://Core/retail_career_save.gd")
const SmokeScenario = preload("res://Client/smoke_scenario.gd")
const InteractiveInput = preload("res://Client/interactive_input.gd")
const CaptureRig = preload("res://Scenes/Game/frontend_capture_rig.gd")
var counts: Dictionary = {}
var failures: Array[Dictionary] = []


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if typeof(actual) != typeof(expected) or actual != expected:
		failures.append({"group": group, "name": name, "actual": str(actual), "expected": str(expected)})


func _refused(group: String, name: String, result: Dictionary, contains: String = "") -> void:
	_check(group, name + " refused", result.ok, false)
	if not result.ok:
		_check(group, name + " type", result.error_type, "ArgumentException")
		if not contains.is_empty():
			_check(group, name + " message", String(result.error).contains(contains), true)


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("Usage: -- <gold_career_save.bin> <report.json>")
		quit(2)
		return
	_launch_options()
	_career_selections(args[0])
	_smoke_scenario()
	_capture_rig()
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		push_error("Cannot write the host check report.")
		quit(2)
		return
	file.store_string(JSON.stringify(report, "  ", false) + "\n")
	file.close()
	print("host checks: %d groups, %d failures" % [counts.size(), failures.size()])
	quit(0 if failures.is_empty() else 1)


func _launch_options() -> void:
	var g: String = "launch_options"
	var normal: Dictionary = LaunchOptions.parse(["--career-save=/missing/first.bes", "--career-save=/missing/second.bes",
		"--startup-media=/missing/media"])
	_check(g, "normal ok", normal.ok, true)
	if normal.ok:
		_check(g, "normal smoke", normal.value.smoke, false)
		_check(g, "normal skip", normal.value.skip_startup_media, false)
		_check(g, "normal capture", normal.value.capture_arguments_present, false)
		_check(g, "normal tape", normal.value.record_tape_path, "")
	var independent: Dictionary = LaunchOptions.parse(["--skipfmv", "--intro", "--record-tape=/abs/recording.json",
		"--capture-plan=mainmenu"])
	_check(g, "independent ok", independent.ok, true)
	if independent.ok:
		_check(g, "independent tape", independent.value.record_tape_path, "/abs/recording.json")
		_check(g, "independent skip", independent.value.skip_startup_media, true)
		_check(g, "independent intro", independent.value.force_startup_media, true)
		_check(g, "independent capture", independent.value.capture_arguments_present, true)
	for argument: String in ["--career-svae=/missing/save.bes", "/missing/save.bes", "--post-mission-event=Won"]:
		_refused(g, "unknown " + argument, LaunchOptions.parse([argument]), "Unknown First Flight argument")
	for argument: String in ["--record-tape=relative.json", "--record-tape=/tmp/save.bes", "--record-tape="]:
		_refused(g, "tape " + argument, LaunchOptions.parse([argument]), "--record-tape requires")
	_refused(g, "smoke without report", LaunchOptions.parse(["--smoke"]), "absolute --report")
	_refused(g, "smoke relative report", LaunchOptions.parse(["--smoke", "--report=relative.json"]), "absolute --report")
	var smoke: Dictionary = LaunchOptions.parse(["--smoke", "--report=/abs/smoke.json"])
	_check(g, "smoke ok", smoke.ok, true)
	if smoke.ok:
		_check(g, "smoke flag", smoke.value.smoke, true)
		_check(g, "smoke report", smoke.value.report_path, "/abs/smoke.json")
	for capture: String in ["--capture-dir=/missing/capture", "--capture-plan=mainmenu", "--capture-size=960x720",
			"--capture-offsets-ms=0,100"]:
		_refused(g, "smoke+capture " + capture, LaunchOptions.parse(["--smoke", "--report=/abs/smoke.json", capture]),
			"Smoke mode and capture")
		_refused(g, "capture+smoke " + capture, LaunchOptions.parse([capture, "--report=/abs/smoke.json", "--smoke"]),
			"Smoke mode and capture")
	for prefix: String in ["--report=", "--record-tape="]:
		for same: bool in [false, true]:
			var arguments: Array[String] = [prefix + "/abs/first.json", prefix + ("/abs/first.json" if same else "/abs/second.json")]
			if prefix == "--report=":
				arguments.append("--smoke")
			_refused(g, "twice " + prefix + str(same), LaunchOptions.parse(arguments), prefix.left(-1) + " may only be specified once")
		for invalid: String in ["", "relative.json"]:
			var arguments: Array[String] = [prefix + invalid, prefix + "/abs/valid.json"]
			if prefix == "--report=":
				arguments.append("--smoke")
			_refused(g, "hidden invalid " + prefix + invalid, LaunchOptions.parse(arguments))
	var repeated: Dictionary = LaunchOptions.parse(["--skipfmv", "--intro", "--skipfmv", "--intro"])
	_check(g, "repeated ok", repeated.ok, true)
	if repeated.ok:
		_check(g, "repeated skip", repeated.value.skip_startup_media, true)
		_check(g, "repeated intro", repeated.value.force_startup_media, true)
		_check(g, "repeated smoke", repeated.value.smoke, false)
		_check(g, "repeated capture", repeated.value.capture_arguments_present, false)


func _career_selections(fixture: String) -> void:
	var g: String = "career_selections"
	var selected: Dictionary = CareerSelections.read_explicit_selections(["--career-save=" + fixture])
	_check(g, "gold ok", selected.ok, true)
	if selected.ok:
		_check(g, "one descriptor", selected.value.size(), 1)
		var descriptor: Dictionary = selected.value[0]
		_check(g, "no slot", descriptor.slot_number, null)
		_check(g, "file name", descriptor.name, "gold_career_save")
		var career: Dictionary = CareerSave.read(FileAccess.get_file_as_bytes(fixture))
		_check(g, "reader ok", career.ok, true)
		if career.ok:
			_check(g, "projected facts", descriptor.career, career.value.project())
			_check(g, "completed worlds", career.value.snapshot().completed_world_count, 43)
			_check(g, "container length", career.value.snapshot().container_length, 10_004)
	var bare: Dictionary = CareerSelections.read_explicit_selections(["--skipfmv", fixture])
	_check(g, "bare path ignored", bare.ok and bare.value.is_empty(), true)
	var empty: Dictionary = CareerSelections.read_explicit_selections(["--career-save= "])
	_check(g, "empty path refused", empty.ok, false)
	var missing: Dictionary = CareerSelections.read_explicit_selections(["--career-save=/nonexistent/career.bes"])
	_check(g, "missing file refused", missing.ok, false)


func _smoke_scenario() -> void:
	var g: String = "smoke_scenario"
	_check(g, "negative tick refused", SmokeScenario.input_for_tick(-1).ok, false)
	var expected: Dictionary = {}
	for tick: int in [0, 707, 1165, 1329, 1666, 2092, 2098, 2100, 2124, 2147, 2148]:
		expected[tick] = InteractiveInput.idle()
	for tick: int in [708, 851, 1330, 1359]:
		expected[tick] = InteractiveInput.create(-1, 0, false, false, false).value
	for tick: int in [852, 1164, 1360, 1665]:
		expected[tick] = InteractiveInput.create(0, 1, false, false, false).value
	for tick: int in [2093, 2097, 2120]:
		expected[tick] = InteractiveInput.create(0, 0, false, false, false, -1).value
	for tick: int in [2099, 2103, 2122]:
		expected[tick] = InteractiveInput.create(0, 0, false, false, false, 1).value
	for tick: int in [2104, 2109, 2115, 2123]:
		expected[tick] = InteractiveInput.create(0, 0, true, false, false).value
	for tick: int in expected:
		var actual: Dictionary = SmokeScenario.input_for_tick(tick)
		_check(g, "tick %d" % tick, actual.get("value"), expected[tick])
	var fire_ticks: int = 0
	for tick: int in range(SmokeScenario.DURATION_TICKS):
		if SmokeScenario.input_for_tick(tick).value.fire_held:
			fire_ticks += 1
	_check(g, "four fire-held ticks", fire_ticks, 4)
	_check(g, "duration", SmokeScenario.DURATION_TICKS, 2_148)


func _capture_rig() -> void:
	var g: String = "capture_rig"
	for pair: Array in [[0, 0], [8, 0], [9, 1], [250, 15], [16_000, 960], [41_999, 2_520], [42_000, 2_520]]:
		_check(g, "frame for %d ms" % pair[0], CaptureRig.frame_for_offset_ms(pair[0]), pair[1])
	var none: Dictionary = CaptureRig.try_create(["--skipfmv"], null)
	_check(g, "no capture dir", none.ok and none.value == null, true)
	_refused(g, "relative dir", CaptureRig.try_create(["--capture-dir=relative"], null), "absolute --capture-dir")
	_refused(g, "unknown plan", CaptureRig.try_create(["--capture-dir=/abs/capture", "--capture-plan=menu"], null), "Unknown capture plan")
	_refused(g, "negative offset", CaptureRig.try_create(["--capture-dir=/abs/capture", "--capture-offsets-ms=0,-5"], null), "Malformed --capture-offsets-ms")
	_refused(g, "empty offsets", CaptureRig.try_create(["--capture-dir=/abs/capture", "--capture-offsets-ms=,"], null), "listed no offsets")
	_refused(g, "bad size", CaptureRig.try_create(["--capture-dir=/abs/capture", "--capture-size=640by480"], null), "Malformed --capture-size")
	var rig: Dictionary = CaptureRig.try_create(["--capture-dir=/abs/capture", "--capture-plan=gameplay",
		"--capture-offsets-ms=100, 0,100", "--capture-size=960x720"], null)
	_check(g, "rig ok", rig.ok, true)
	if rig.ok and rig.value != null:
		_check(g, "offsets sorted and distinct", rig.value._requested_offsets_ms, [0, 100] as Array[int])
		_check(g, "size", Vector2i(rig.value._capture_width, rig.value._capture_height), Vector2i(960, 720))
		rig.value.free()
