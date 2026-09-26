# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Headless command-tape replay, formerly the OnslaughtRebuild.Headless CLI.
## Core's ReplayRunner (C#, the measured hot-path exception) replays and hashes
## through Bridge/SimulationBridge.cs, so this runs on the .NET engine:
##   godot48-mono --headless --path rebuild/OnslaughtRebuild.Godot
##     --script res://Client/headless_replay.gd -- [--tape PATH]
##     [--compare-tape PATH] [--expect HEX] [--repeat N]
## rebuild/tools/first_flight.py replay resolves relative paths first; this
## script admits only absolute ones. Exit codes: 0 verified or unchecked;
## 1 usage or input error; 2 an expected hash did not match; 3 repeated
## replays diverged; 4 the compared tape diverged; 70 internal failure.

const MAXIMUM_TAPE_BYTES: int = 8 * 1024 * 1024
const MAXIMUM_REPLAY_STEPS: int = 100_000
const BUILT_IN_TAPE: String = "../scenarios/first-flight.v1.json"
const ACTOR_MANIFEST: String = "res://Assets/Level100/StaticWorld/level100-static-world.json"
const BRIDGE_SCRIPT_PATH: String = "res://Bridge/SimulationBridge.cs"
const RESULT_SCHEMA: String = "onslaught-rebuild-headless-result.v2"
const DIFF_SCHEMA: String = "onslaught-rebuild-replay-diff.v1"
const HELP: String = """OnslaughtRebuild headless replay
  --tape <path>   Command tape (default: rebuild/scenarios/first-flight.v1.json)
  --compare-tape <path>  Optional second tape for first-divergence receipt
  --expect <hex>  Optional expected SHA-256 replay trace hash
  --repeat <n>    Replay count (default: 2; 100,000 total-step limit)"""


func _initialize() -> void:
	var result: Dictionary = run(OS.get_cmdline_user_args())
	if not String(result.output).is_empty():
		print(result.output)
	if not String(result.error).is_empty():
		printerr(result.error)
	quit(int(result.exit_code))


## Runs one replay request. Returns {exit_code, output, error}; output is the
## JSON report (empty on a usage or input error) and error the diagnostic line.
static func run(args: PackedStringArray, bridge: RefCounted = null) -> Dictionary:
	if args.has("--help"):
		return _done(0, HELP, "")
	var parsed: Dictionary = _parse(args)
	if not parsed.ok:
		return _done(1, "", parsed.error)
	var options: Dictionary = parsed.value
	if bridge == null:
		var script: Script = load(BRIDGE_SCRIPT_PATH)
		if script == null or not script.can_instantiate():
			return _done(70, "", "Headless replay requires the .NET engine and a current rebuild build.")
		bridge = script.new()
	var tape_text: Dictionary = _read_tape(options.tape_path)
	if not tape_text.ok:
		return _done(1, "", tape_text.error)
	var tape: Dictionary = bridge.DecodeTape(tape_text.value)
	if not tape.ok:
		return _refused(tape)
	var compare_text: String = ""
	var compare_tape: Variant = null
	if options.compare_tape_path != null:
		var read: Dictionary = _read_tape(options.compare_tape_path)
		if not read.ok:
			return _done(1, "", read.error)
		compare_text = read.value
		var decoded: Dictionary = bridge.DecodeTape(compare_text)
		if not decoded.ok:
			return _refused(decoded)
		compare_tape = decoded.value
	var requested_steps: int = int(tape.value.duration_ticks) * int(options.repeat_count) \
		+ (0 if compare_tape == null else int(compare_tape.duration_ticks))
	if requested_steps > MAXIMUM_REPLAY_STEPS:
		return _done(1, "", "Replay request exceeds the 100,000 total-step limit.")
	var expectation: Dictionary = _expectation(options, tape.value)
	var manifest: PackedByteArray = FileAccess.get_file_as_bytes(ACTOR_MANIFEST)
	if manifest.is_empty():
		return _done(1, "", "The Level 100 actor manifest could not be read: " + ACTOR_MANIFEST)

	var comparison: Variant = null
	var determinism: Dictionary = {"schema_version": DIFF_SCHEMA, "trace_hash_mismatch": false,
		"behavioral_event_mismatch": false, "final_state_mismatch": false, "first_divergence": null}
	var first: Dictionary
	var next_repeat: int
	if compare_tape != null:
		var compared: Dictionary = bridge.CompareReplays(tape_text.value, compare_text, manifest)
		if not compared.ok:
			return _refused(compared)
		comparison = compared.value
		first = compared.value.before
		next_repeat = 1
	elif options.repeat_count >= 2:
		var pair: Dictionary = bridge.CompareReplays(tape_text.value, tape_text.value, manifest)
		if not pair.ok:
			return _refused(pair)
		first = pair.value.before
		determinism = pair.value.diff
		next_repeat = 2
	else:
		var single: Dictionary = bridge.Replay(tape_text.value, manifest)
		if not single.ok:
			return _refused(single)
		first = single.value
		next_repeat = 1
	for repeat: int in range(next_repeat, options.repeat_count):
		var repeated: Dictionary = bridge.Replay(tape_text.value, manifest)
		if not repeated.ok:
			return _refused(repeated)
		var trace_mismatch: bool = first.trace_hash != repeated.value.trace_hash
		var final_state_mismatch: bool = first.final_state_hash != repeated.value.final_state_hash
		if trace_mismatch or final_state_mismatch:
			determinism = {"schema_version": DIFF_SCHEMA, "trace_hash_mismatch": trace_mismatch,
				"behavioral_event_mismatch": false, "final_state_mismatch": final_state_mismatch,
				"first_divergence": null}
			break

	var trace_checked: bool = expectation.trace_hash != null
	var trace_verified: Variant = String(first.trace_hash).to_lower() == String(expectation.trace_hash).to_lower() \
		if trace_checked else null
	var final_checked: bool = expectation.final_state_hash != null
	var final_verified: Variant = String(first.final_state_hash).to_lower() == String(expectation.final_state_hash).to_lower() \
		if final_checked else null
	var summary: Dictionary = {
		"schemaVersion": RESULT_SCHEMA,
		"tape": tape.value.name,
		"ticks": first.ticks,
		"repeats": options.repeat_count,
		"traceHash": first.trace_hash,
		"finalStateHash": first.final_state_hash,
		"expectedTraceHash": expectation.trace_hash,
		"expectedFinalStateHash": expectation.final_state_hash,
		"verificationSource": expectation.source,
		"traceHashChecked": trace_checked,
		"traceHashVerified": trace_verified,
		"finalStateHashChecked": final_checked,
		"finalStateHashVerified": final_verified,
		"mode": first.mode,
		"energy": first.energy,
		"shield": first.shield,
		"hull": first.hull,
		"targetsDestroyed": first.targets_destroyed,
		"activeProjectiles": first.active_projectiles,
		"determinism": _diff_report(determinism),
		"comparisonTape": null if compare_tape == null else compare_tape.name,
		"comparisonTraceHash": null if comparison == null else comparison.after.trace_hash,
		"comparisonFinalStateHash": null if comparison == null else comparison.after.final_state_hash,
		"comparison": null if comparison == null else _diff_report(comparison.diff),
	}
	var output: String = JSON.stringify(summary, "  ", false)
	if determinism.trace_hash_mismatch or determinism.behavioral_event_mismatch or determinism.final_state_mismatch:
		return _done(3, output, "Determinism failure: repeated replay diverged; inspect the determinism receipt.")
	if trace_verified == false:
		return _done(2, output, "Replay trace hash did not match the expected value.")
	if final_verified == false:
		return _done(2, output, "Final state hash did not match the expected value.")
	if comparison != null and (comparison.diff.trace_hash_mismatch or comparison.diff.behavioral_event_mismatch
			or comparison.diff.final_state_mismatch):
		return _done(4, output, "Replay comparison diverged; inspect the comparison receipt.")
	return _done(0, output, "")


## The packaged scenario beside the project, never a current-directory shadow.
static func built_in_tape_path() -> String:
	return ProjectSettings.globalize_path("res://").path_join(BUILT_IN_TAPE).simplify_path()


static func _parse(args: PackedStringArray) -> Dictionary:
	var options: Dictionary = {"tape_path": built_in_tape_path(), "compare_tape_path": null,
		"expected_trace_hash": null, "repeat_count": 2}
	var index: int = 0
	while index < args.size():
		var option: String = args[index]
		if option not in ["--tape", "--compare-tape", "--expect", "--repeat"]:
			return {"ok": false, "error": "Unknown argument: " + option}
		index += 1
		if index >= args.size() or args[index].strip_edges().is_empty():
			return {"ok": false, "error": option + " requires a value."}
		var value: String = args[index]
		match option:
			"--tape":
				options.tape_path = value
			"--compare-tape":
				options.compare_tape_path = value
			"--expect":
				if value.length() != 64 or not _is_hex(value):
					return {"ok": false, "error": "--expect must be a 64-character SHA-256 replay trace hash."}
				options.expected_trace_hash = value
			"--repeat":
				var text: String = value.strip_edges()
				if not text.is_valid_int() or text.to_int() < 1 or text.to_int() > 1_000:
					return {"ok": false, "error": "--repeat must be an integer from 1 through 1000."}
				options.repeat_count = text.to_int()
		index += 1
	return {"ok": true, "value": options}


static func _expectation(options: Dictionary, tape: Dictionary) -> Dictionary:
	if options.expected_trace_hash != null:
		return {"trace_hash": options.expected_trace_hash,
			"final_state_hash": tape.expected_final_state_hash, "source": "command-line"}
	if tape.expected_trace_hash != null or tape.expected_final_state_hash != null:
		return {"trace_hash": tape.expected_trace_hash,
			"final_state_hash": tape.expected_final_state_hash, "source": "command-tape"}
	return {"trace_hash": null, "final_state_hash": null, "source": "none"}


static func _read_tape(path: String) -> Dictionary:
	if not path.is_absolute_path() or path.begins_with("res://") or path.begins_with("user://"):
		return {"ok": false, "error": "Command tape paths must be absolute file-system paths: " + path}
	if DirAccess.dir_exists_absolute(path):
		return {"ok": false, "error": "Command tape path is a directory: " + path}
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {"ok": false, "error": "Could not open command tape '%s': %s" % [path, error_string(FileAccess.get_open_error())]}
	if file.get_length() > MAXIMUM_TAPE_BYTES:
		return {"ok": false, "error": "Command tape exceeds the 8 MiB input limit."}
	var bytes: PackedByteArray = file.get_buffer(file.get_length())
	if bytes.size() >= 3 and bytes[0] == 0xEF and bytes[1] == 0xBB and bytes[2] == 0xBF:
		bytes = bytes.slice(3)
	return {"ok": true, "value": bytes.get_string_from_utf8()}


static func _diff_report(diff: Dictionary) -> Dictionary:
	var first: Variant = diff.first_divergence
	return {"schemaVersion": diff.schema_version, "traceHashMismatch": diff.trace_hash_mismatch,
		"behavioralEventMismatch": diff.behavioral_event_mismatch, "finalStateMismatch": diff.final_state_mismatch,
		"firstDivergence": null if first == null else {"tick": first.tick, "category": first.category,
			"beforeValue": first.before_value, "afterValue": first.after_value}}


static func _is_hex(value: String) -> bool:
	for character: String in value:
		if not "0123456789abcdefABCDEF".contains(character):
			return false
	return true


static func _refused(result: Dictionary) -> Dictionary:
	if result.get("input_error", false):
		return _done(1, "", result.error)
	return _done(70, "", "Internal replay failure (%s): %s" % [result.error_type, result.error])


static func _done(exit_code: int, output: String, error: String) -> Dictionary:
	return {"exit_code": exit_code, "output": output, "error": error}
