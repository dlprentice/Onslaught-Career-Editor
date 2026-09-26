# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Headless replay and tape persistence contracts, ported from the retired
## HeadlessApplicationTests: the GDScript replayer's options, work budget,
## expectations, report and exit codes; the recorded-tape round trip through
## the GDScript session; and TapeFile's create-new destination boundary
## through the production PersistRecordedTape. Needs the .NET engine and a
## current build (the replayer reaches Core through the bridge). Usage:
##   --script res://Tests/headless_replay_checks.gd -- <fresh owned local-data dir> <report.json>
const Replay = preload("res://Client/headless_replay.gd")
const InteractiveSession = preload("res://Client/interactive_session.gd")
const InteractiveInput = preload("res://Client/interactive_input.gd")
const PlatformInput = preload("res://Client/platform_input_edges.gd")
const SimInput = preload("res://Core/sim_input.gd")
const BRIDGE_SCRIPT_PATH: String = "res://Bridge/SimulationBridge.cs"
const TAPE_SCHEMA: String = "onslaught-rebuild-command-tape.v5"
const PREVIOUS_TAPE_SCHEMA: String = "onslaught-rebuild-command-tape.v4"
# first-flight.v1.json (838 ticks) as pinned by Core.Tests FirstFlightFingerprintTests.
const FIRST_FLIGHT_TRACE: String = "0872e009a2fb254927a3014d539ae1039332ad5eb8bd8af38a6e77cc86575ec9"
const FIRST_FLIGHT_STATE: String = "69bd64ac4b2f344c1300d64e6619931f57dc06d768dbd70a5f1b816aedb1f59a"
const ONE_STEP_TICKS: int = 500_000
var counts: Dictionary = {}
var failures: Array[Dictionary] = []
var _directory: String = ""
var _serial: int = 0
var _manifest: PackedByteArray


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not _owned_directory(args[0]) or not DirAccess.get_files_at(args[0]).is_empty() \
			or not DirAccess.get_directories_at(args[0]).is_empty():
		push_error("Usage: -- <fresh owned local-data directory> <report.json>")
		quit(2)
		return
	_directory = args[0]
	_manifest = FileAccess.get_file_as_bytes(Replay.ACTOR_MANIFEST)
	_replayer()
	_persistence()
	_recorded_round_trip()
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		push_error("Cannot write the headless replay check report.")
		quit(2)
		return
	file.store_string(JSON.stringify(report, "  ", false) + "\n")
	file.close()
	print("headless replay checks: %d groups, %d failures" % [counts.size(), failures.size()])
	quit(0 if failures.is_empty() else 1)


func _replayer() -> void:
	var g: String = "replayer"
	var built_in: String = Replay.built_in_tape_path()
	_check(g, "built-in tape is the project's scenario", built_in.ends_with("/rebuild/scenarios/first-flight.v1.json")
		and built_in.is_absolute_path() and FileAccess.file_exists(built_in), true)

	# Default tape, repeated: deterministic, no embedded expectation, stable report.
	var first: Dictionary = Replay.run(PackedStringArray(["--repeat", "2"]))
	var second: Dictionary = Replay.run(PackedStringArray(["--repeat", "2"]))
	_check(g, "default exit", first.exit_code, 0)
	_check(g, "default repeat exit", second.exit_code, 0)
	_check(g, "default report stable", first.output, second.output)
	_check(g, "default error empty", first.error + second.error, "")
	var report: Dictionary = _json(first.output)
	_check(g, "default schema", report.get("schemaVersion"), "onslaught-rebuild-headless-result.v2")
	_check(g, "default tape name", report.get("tape"), "first-flight")
	_check(g, "default unchecked trace", [report.get("traceHashChecked"), report.get("traceHashVerified")], [false, null])
	_check(g, "default unchecked state", [report.get("finalStateHashChecked"), report.get("finalStateHashVerified")], [false, null])
	_check(g, "default no expectation", [report.get("expectedTraceHash"), report.get("verificationSource")], [null, "none"])
	_check(g, "default determinism", report.get("determinism"), {"schemaVersion": "onslaught-rebuild-replay-diff.v1",
		"traceHashMismatch": false, "behavioralEventMismatch": false, "finalStateMismatch": false, "firstDivergence": null})
	_check(g, "report key order", report.keys(), ["schemaVersion", "tape", "ticks", "repeats", "traceHash", "finalStateHash",
		"expectedTraceHash", "expectedFinalStateHash", "verificationSource", "traceHashChecked", "traceHashVerified",
		"finalStateHashChecked", "finalStateHashVerified", "mode", "energy", "shield", "hull", "targetsDestroyed",
		"activeProjectiles", "determinism", "comparisonTape", "comparisonTraceHash", "comparisonFinalStateHash", "comparison"])

	# The pinned first-flight fingerprint through the command-line expectation.
	var pinned: Dictionary = Replay.run(PackedStringArray(["--expect", FIRST_FLIGHT_TRACE, "--repeat", "2"]))
	var pinned_report: Dictionary = _json(pinned.output)
	_check(g, "fingerprint exit", pinned.exit_code, 0)
	_check(g, "fingerprint ticks", pinned_report.get("ticks"), 838)
	_check(g, "fingerprint verified", [pinned_report.get("traceHashChecked"), pinned_report.get("traceHashVerified"),
		pinned_report.get("verificationSource")], [true, true, "command-line"])
	_check(g, "fingerprint hashes", [pinned_report.get("traceHash"), pinned_report.get("finalStateHash")],
		[FIRST_FLIGHT_TRACE, FIRST_FLIGHT_STATE])
	_check(g, "fingerprint final state", [pinned_report.get("mode"), pinned_report.get("targetsDestroyed"),
		pinned_report.get("activeProjectiles")], ["Walker", 0, 0])
	_check(g, "fingerprint error empty", pinned.error, "")
	var upper: Dictionary = Replay.run(PackedStringArray(["--expect", FIRST_FLIGHT_TRACE.to_upper(), "--repeat", "1"]))
	_check(g, "expectation ignores hex case", [upper.exit_code, _json(upper.output).get("traceHashVerified")], [0, true])

	_usage(g, "invalid expected hash", ["--tape", built_in, "--expect", "not-a-sha256"], "64-character SHA-256")
	_usage(g, "unknown argument", ["--tapes", built_in], "Unknown argument: --tapes")
	_usage(g, "missing value", ["--repeat"], "--repeat requires a value.")
	_usage(g, "blank value", ["--tape", "  "], "--tape requires a value.")
	_usage(g, "repeat below range", ["--repeat", "0"], "from 1 through 1000")
	_usage(g, "repeat above range", ["--repeat", "1001"], "from 1 through 1000")
	_usage(g, "repeat not integer", ["--repeat", "2.5"], "from 1 through 1000")
	_usage(g, "relative tape path", ["--tape", "scenarios/first-flight.v1.json"], "absolute")
	_usage(g, "directory tape path", ["--tape", built_in.get_base_dir()], "directory")
	_usage(g, "missing tape file", ["--tape", _path("absent.json")], "Could not open")
	var help: Dictionary = Replay.run(PackedStringArray(["--repeat", "0", "--help"]))
	_check(g, "help wins", [help.exit_code, help.output.begins_with("OnslaughtRebuild headless replay"), help.error], [0, true, ""])

	# The tape codec's own refusals reach the caller as input errors.
	var malformed: String = _write_text("""{
  "schemaVersion": "%s",
  "name": "missing-spans",
  "seed": 1,
  "durationTicks": 10,
  "expectedFinalStateHash": null
}
""" % PREVIOUS_TAPE_SCHEMA)
	_usage(g, "malformed tape", ["--tape", malformed], "spans are required")
	_usage(g, "duplicate member", ["--tape", _write_text('{"schemaVersion": "%s", "name": "a", "name": "b", "seed": 1, "durationTicks": 1, "spans": []}' % TAPE_SCHEMA)],
		"Duplicate command tape JSON member")
	_usage(g, "not JSON", ["--tape", _write_text("{ not json")], "invalid")

	var oversized: String = _path("oversized.json")
	var file := FileAccess.open(oversized, FileAccess.WRITE)
	file.seek(8 * 1024 * 1024)
	file.store_8(32)
	file.close()
	_check(g, "oversized fixture length", FileAccess.get_file_as_bytes(oversized).size(), 8 * 1024 * 1024 + 1)
	_usage(g, "oversized tape", ["--tape", oversized], "8 MiB")
	var bom: PackedByteArray = PackedByteArray([0xEF, 0xBB, 0xBF])
	bom.append_array(_tape_json("bom", 1, 1, []).to_utf8_buffer())
	var bom_path: String = _path("bom.json")
	var bom_file := FileAccess.open(bom_path, FileAccess.WRITE)
	bom_file.store_buffer(bom)
	bom_file.close()
	var with_bom: Dictionary = Replay.run(PackedStringArray(["--tape", bom_path, "--repeat", "1"]))
	_check(g, "UTF-8 byte-order mark admitted", [with_bom.exit_code, _json(with_bom.output).get("tape")], [0, "bom"])

	# A wrong command-line expectation: verified false and the mismatch exit.
	var wrong: Dictionary = Replay.run(PackedStringArray(["--tape", built_in, "--expect", "0".repeat(64), "--repeat", "1"]))
	var wrong_report: Dictionary = _json(wrong.output)
	_check(g, "wrong expectation exit", wrong.exit_code, 2)
	_check(g, "wrong expectation report", [wrong_report.get("traceHashChecked"), wrong_report.get("traceHashVerified"),
		wrong_report.get("finalStateHashChecked")], [true, false, false])
	_check(g, "wrong expectation message", wrong.error, "Replay trace hash did not match the expected value.")

	# Comparing two tapes: one exact first-divergence receipt.
	var before: String = _write_text(_tape_json("before", 1, 2, []))
	var after: String = _write_text(_tape_json("after", 1, 2, [{"startTick": 1, "durationTicks": 1, "moveX": 1, "moveZ": 0}]))
	var compared: Dictionary = Replay.run(PackedStringArray(["--tape", before, "--compare-tape", after, "--repeat", "1"]))
	var compared_report: Dictionary = _json(compared.output)
	_check(g, "comparison exit", compared.exit_code, 4)
	_check(g, "comparison tape", compared_report.get("comparisonTape"), "after")
	_check(g, "comparison receipt", compared_report.get("comparison"), {"schemaVersion": "onslaught-rebuild-replay-diff.v1",
		"traceHashMismatch": true, "behavioralEventMismatch": true, "finalStateMismatch": false,
		"firstDivergence": {"tick": 1, "category": "input.moveX", "beforeValue": "0", "afterValue": "1"}})
	_check(g, "comparison hashes reported", [String(compared_report.get("comparisonTraceHash")).length(),
		String(compared_report.get("comparisonFinalStateHash")).length()], [64, 64])
	_check(g, "comparison message", compared.error, "Replay comparison diverged; inspect the comparison receipt.")
	var same: Dictionary = Replay.run(PackedStringArray(["--tape", before, "--compare-tape", before, "--repeat", "3"]))
	_check(g, "identical comparison passes", [same.exit_code, _json(same.output).get("comparison").get("firstDivergence")], [0, null])

	# The replay work budget is checked before any simulation.
	var long_tape: String = _write_text(_tape_json("work-limit", 1, 1_001, []))
	_usage(g, "repeat work over limit", ["--tape", long_tape, "--repeat", "100"], "100,000")
	var primary: String = _write_text(_tape_json("primary", 1, 1, []))
	var bad_compare: String = _write_text('{\n  "schemaVersion": "%s",\n  "name": "malformed-compare",\n  "seed": 1,\n  "durationTicks": 1\n}\n' % TAPE_SCHEMA)
	_usage(g, "malformed comparison tape", ["--tape", primary, "--compare-tape", bad_compare, "--repeat", "1"], "spans are required")
	var budget_a: String = _write_text(_tape_json("primary-budget", 1, 50_000, []))
	var budget_b: String = _write_text(_tape_json("comparison-budget", 1, 50_001, []))
	_usage(g, "comparison work over limit", ["--tape", budget_a, "--compare-tape", budget_b, "--repeat", "1"], "100,000")

	# An explicit trace expectation still checks a forged embedded final-state hash.
	var bridge: RefCounted = _bridge()
	var plain: String = _tape_json("forged-final-state", 23, 3, [])
	var actual: Dictionary = bridge.Replay(plain, _manifest)
	_check(g, "forged fixture replays", actual.ok, true)
	var forged: String = _write_text(_tape_json("forged-final-state", 23, 3, [], actual.value.trace_hash, "0".repeat(64)))
	var forged_run: Dictionary = Replay.run(PackedStringArray(["--tape", forged, "--expect", actual.value.trace_hash, "--repeat", "2"]))
	var forged_report: Dictionary = _json(forged_run.output)
	_check(g, "forged exit", forged_run.exit_code, 2)
	_check(g, "forged report", [forged_report.get("traceHashVerified"), forged_report.get("finalStateHashChecked"),
		forged_report.get("finalStateHashVerified"), forged_report.get("expectedFinalStateHash")], [true, true, false, "0".repeat(64)])
	_check(g, "forged message", forged_run.error, "Final state hash did not match the expected value.")
	var embedded: String = _write_text(_tape_json("embedded", 23, 3, [], actual.value.trace_hash, actual.value.final_state_hash))
	var embedded_run: Dictionary = Replay.run(PackedStringArray(["--tape", embedded, "--repeat", "1"]))
	_check(g, "embedded expectation", [embedded_run.exit_code, _json(embedded_run.output).get("verificationSource")], [0, "command-tape"])

	# Bridge refusals keep their input/internal classification.
	var refused: Dictionary = bridge.DecodeTape("")
	_check(g, "empty tape is an input error", [refused.ok, refused.get("input_error")], [false, true])
	var bad_manifest: Dictionary = bridge.Replay(plain, PackedByteArray([123, 125]))
	_check(g, "wrong manifest is an input error", [bad_manifest.ok, bad_manifest.get("input_error")], [false, true])


func _persistence() -> void:
	var g: String = "tape_file"
	# Refuses to overwrite: the first tape stays byte-for-byte.
	var path: String = _path("record/recorded.tape.json")
	var first: RefCounted = _recording(1)
	_check(g, "first write", first.PersistRecordedTape(path), {"ok": true, "value": true})
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
	var second: RefCounted = _recording(2)
	var refused: Dictionary = second.PersistRecordedTape(path)
	_check(g, "overwrite refused", [refused.ok, refused.get("error_type"), String(refused.get("error", "")).contains("refuses to overwrite")],
		[false, "IOException", true])
	_check(g, "overwrite left the tape", FileAccess.get_file_as_bytes(path), bytes)
	_check(g, "refused recorder retained", second.IsRecording(), {"ok": true, "value": true})
	var text: String = bytes.get_string_from_utf8()
	_check(g, "LF canonical JSON", [text.contains("\r"), text.ends_with("\n")], [false, true])
	var decoded: Dictionary = first.DecodeTape(text)
	_check(g, "persisted tape decodes", [decoded.ok, decoded.value.name if decoded.ok else null, decoded.value.duration_ticks if decoded.ok else null],
		[true, "recorded-1", 1])

	# Missing parents are created for an ordinary fresh destination.
	var nested: String = _path("fresh/deep/nested/recorded.tape.json")
	_check(g, "nested write", _recording(3).PersistRecordedTape(nested), {"ok": true, "value": true})
	_check(g, "nested exists", FileAccess.file_exists(nested), true)

	# Career saves, retail files and non-absolute spellings are never destinations.
	for destination: String in [_path("career.bes"), _path("BEA.exe"), "relative/tape.json", _path("tape.JSON.bak"),
			"\\\\?\\" + _path("extended.json"), "\\\\?\\GLOBALROOT\\onslaught-probe\\extended.json",
			"\\\\?\\Volume{9c5f8a3e-0000-0000-0000-000000000000}\\probe.json"]:
		var rejected: Dictionary = _recording(1).PersistRecordedTape(destination)
		_check(g, "refused " + destination, [rejected.ok, rejected.get("error_type"),
			String(rejected.get("error", "")).contains("absolute .json destination path")], [false, "ArgumentException", true])
		_check(g, "nothing written " + destination, FileAccess.file_exists(destination), false)
	var upper: String = _path("upper.JSON")
	_check(g, "extension is case-insensitive", _recording(1).PersistRecordedTape(upper), {"ok": true, "value": true})

	# A synthetic retail-install shape (BEA.exe beside data) refuses before any
	# parent is created; only the shape matters, never retail bytes.
	var retail: String = _path("retail")
	DirAccess.make_dir_recursive_absolute(retail.path_join("data"))
	var marker := FileAccess.open(retail.path_join("BEA.exe"), FileAccess.WRITE)
	marker.store_string("synthetic")
	marker.close()
	for destination: String in [retail.path_join("data/recording.json"), retail.path_join("savegames/nested/tape.json")]:
		var rejected: Dictionary = _recording(1).PersistRecordedTape(destination)
		_check(g, "retail shape refused " + destination.trim_prefix(_directory), [rejected.ok, rejected.get("error_type"),
			String(rejected.get("error", "")).contains("retail install layout")], [false, "ArgumentException", true])
		_check(g, "retail shape wrote nothing " + destination.trim_prefix(_directory), FileAccess.file_exists(destination), false)
	_check(g, "retail refusal created no parent", DirAccess.dir_exists_absolute(retail.path_join("savegames")), false)

	# A symbolic-link ancestor refuses, and nothing lands through the link.
	var target: String = _path("plain-target")
	DirAccess.make_dir_recursive_absolute(target)
	var link: String = _path("link")
	var made: int = DirAccess.open(_directory).create_link(target, link)
	_check(g, "link fixture", made, OK)
	if made == OK:
		var through: Dictionary = _recording(1).PersistRecordedTape(link.path_join("recording.json"))
		_check(g, "link ancestor refused", [through.ok, through.get("error_type"), String(through.get("error", "")).contains("reparse")],
			[false, "ArgumentException", true])
		_check(g, "nothing through the link", FileAccess.file_exists(target.path_join("recording.json")), false)

	# A session that never stepped has nothing replayable to write.
	var empty: RefCounted = _recording(0)
	var zero_path: String = _path("zero.json")
	_check(g, "zero-tick recording", empty.PersistRecordedTape(zero_path), {"ok": true, "value": false})
	_check(g, "zero-tick wrote nothing", [FileAccess.file_exists(zero_path), empty.IsRecording().value], [false, false])


# The GDScript session records its exact consumed inputs; the persisted tape
# replays under the headless expectation gate with both embedded hashes.
func _recorded_round_trip() -> void:
	var g: String = "recorded_round_trip"
	var bridge: RefCounted = _bridge()
	var platform := PlatformInput.new()
	var session := InteractiveSession.new(bridge, platform)
	_check(g, "start", session.start(23, _manifest), {"ok": true, "value": null})
	_check(g, "enable recording", bridge.EnableRecording(), {"ok": true, "value": null})
	for tick: int in 665:
		session.advance_frame_ticks(ONE_STEP_TICKS)
	_check(g, "player control at tick 665", bridge.SmokeFacts().value.get("level100_player_control_enabled"), true)
	session.queue_pointer_motion_milli_pixels(9_000, -4_000)
	session.queue_zoom_in()
	session.observe_input(InteractiveInput.create(0, 1, true, false, false).value)
	session.advance_frame_ticks(ONE_STEP_TICKS)
	var fired: Dictionary = bridge.GetLastConsumedInput().value
	_check(g, "held fire charges and zoom edge", [_has(fired, SimInput.Actions.CHARGE_WEAPON), _has(fired, SimInput.Actions.ZOOM_IN)], [true, true])
	_check(g, "pointer permille consumed", [fired.look_x_analog_permille != 0, fired.look_y_analog_permille != 0], [true, true])
	session.advance_frame_ticks(ONE_STEP_TICKS)
	var held: Dictionary = bridge.GetLastConsumedInput().value
	_check(g, "held level repeats, edge does not", [_has(held, SimInput.Actions.CHARGE_WEAPON), _has(held, SimInput.Actions.ZOOM_IN)], [true, false])
	session.observe_input(InteractiveInput.idle())
	session.queue_movement_pulse(1, 0)
	session.queue_zoom_out()
	session.advance_frame_ticks(ONE_STEP_TICKS)
	var released: Dictionary = bridge.GetLastConsumedInput().value
	_check(g, "release fires once with pulse and zoom", [_has(released, SimInput.Actions.FIRE), _has(released, SimInput.Actions.ZOOM_OUT),
		released.move_x], [true, true, 1])
	var final_hash: String = bridge.GetStateHash().value
	var path: String = _path("round-trip/recorded.tape.json")
	_check(g, "persist", bridge.PersistRecordedTape(path), {"ok": true, "value": true})
	var tape: Dictionary = bridge.DecodeTape(FileAccess.get_file_as_string(path))
	_check(g, "embedded expectations", [tape.value.name, tape.value.duration_ticks, tape.value.expected_final_state_hash],
		["recorded-668", 668, final_hash])
	var gate: Dictionary = Replay.run(PackedStringArray(["--tape", path, "--expect", tape.value.expected_trace_hash, "--repeat", "2"]))
	var report: Dictionary = _json(gate.output)
	_check(g, "expect gate passes", [gate.exit_code, gate.error], [0, ""])
	_check(g, "both hashes verified", [report.get("traceHashVerified"), report.get("finalStateHashChecked"),
		report.get("finalStateHashVerified"), report.get("finalStateHash")], [true, true, true, final_hash])


func _usage(group: String, name: String, args: Array, contains: String) -> void:
	var result: Dictionary = Replay.run(PackedStringArray(args))
	_check(group, name + " exit", result.exit_code, 1)
	_check(group, name + " no report", result.output, "")
	_check(group, name + " diagnostic", not result.error.is_empty() and (contains.is_empty() or result.error.contains(contains)), true)


func _recording(ticks: int) -> RefCounted:
	var bridge: RefCounted = _bridge()
	bridge.Start(23, _manifest)
	bridge.EnableRecording()
	for tick: int in ticks:
		bridge.Step(0, 0, 0, 0, 0, 0, 0)
	return bridge


func _bridge() -> RefCounted:
	return (load(BRIDGE_SCRIPT_PATH) as Script).new()


static func _has(input: Dictionary, action: int) -> bool:
	return (int(input.actions) & action) != 0


static func _tape_json(name: String, seed: int, duration: int, spans: Array, trace: Variant = null, final_state: Variant = null) -> String:
	return JSON.stringify({"schemaVersion": TAPE_SCHEMA, "name": name, "seed": seed, "durationTicks": duration,
		"expectedTraceHash": trace, "expectedFinalStateHash": final_state, "spans": spans}, "  ", false) + "\n"


func _write_text(text: String) -> String:
	var path: String = _path("tape-%d.json" % _serial)
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(text)
	file.close()
	return path


func _path(relative: String) -> String:
	_serial += 1
	return _directory.path_join(relative)


static func _json(text: String) -> Dictionary:
	var parser := JSON.new()
	if parser.parse(text) != OK or not parser.data is Dictionary:
		return {}
	return parser.data


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if not _same(actual, expected):
		failures.append({"group": group, "name": name, "actual": str(actual), "expected": str(expected)})


# JSON numbers parse as floats; compare them by value with the integer pins.
static func _same(actual: Variant, expected: Variant) -> bool:
	if actual is float and expected is int or actual is int and expected is float:
		return float(actual) == float(expected)
	if actual is Array and expected is Array:
		if actual.size() != expected.size():
			return false
		for index: int in actual.size():
			if not _same(actual[index], expected[index]):
				return false
		return true
	if actual is Dictionary and expected is Dictionary:
		if actual.keys() != expected.keys():
			return false
		for key: Variant in actual:
			if not _same(actual[key], expected[key]):
				return false
		return true
	return typeof(actual) == typeof(expected) and actual == expected


static func _owned_directory(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(owned + "/"):
		return false
	var directory := DirAccess.open(owned)
	if directory == null:
		return false
	for part: String in path.trim_prefix(owned + "/").split("/", false):
		if directory.is_link(part) or directory.change_dir(part) != OK:
			return false
	return true
