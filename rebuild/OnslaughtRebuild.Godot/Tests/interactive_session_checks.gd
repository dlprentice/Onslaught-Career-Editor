# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## The real-time session adapter (Client/interactive_session.gd) over the
## simulation bridge. The golden is SessionBridgeChecks' operation trace with
## the retired C# InteractiveSession's results: the 2,148-tick smoke, then 6,000
## seeded operations (held levels, edges, pulses, pointer motion, pause and
## suspension, sensitivity and frame lengths up to the cap) and the refusals.
## Every frame's steps, cap, phase, alpha, state hash and consumed input and
## every operation's metrics and flags must match. Needs the .NET engine:
##   --script res://Tests/interactive_session_checks.gd -- <session-trace.golden> <report.json>
const InteractiveSession = preload("res://Client/interactive_session.gd")
const PlatformInput = preload("res://Client/platform_input_edges.gd")
const BRIDGE_SCRIPT_PATH: String = "res://Bridge/SimulationBridge.cs"
const MANIFEST_PATH: String = "res://Assets/Level100/StaticWorld/level100-static-world.json"
const SEED: int = 0x4F4E534C
const METRICS: Array[String] = ["total_steps", "toggle_edges_consumed", "reset_edges_consumed", "reset_generation",
	"fire_held_ticks_sampled", "fire_pulse_edges_consumed", "change_weapon_edges_consumed",
	"movement_pulse_edges_consumed", "capped_frame_count", "dropped_elapsed_ticks"]
var counts: Dictionary = {}
var failures: Array[Dictionary] = []
var _bridge: RefCounted
var _session: RefCounted


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("Usage: -- <session-trace.golden> <report.json>")
		quit(2)
		return
	var trace: Variant = bytes_to_var(FileAccess.get_file_as_bytes(args[0]))
	if not trace is Array or trace.is_empty():
		push_error("The session trace golden is missing or unreadable.")
		quit(2)
		return
	_bridge = (load(BRIDGE_SCRIPT_PATH) as Script).new()
	_session = InteractiveSession.new(_bridge, PlatformInput.new())
	_check("trace", "start", _session.start(SEED, FileAccess.get_file_as_bytes(MANIFEST_PATH)).ok, true)
	var frames: int = 0
	var steps: int = 0
	for entry: Dictionary in trace:
		if entry.has("compare"):
			_compare(entry)
		elif entry.has("refusal"):
			_refusal(entry)
		elif entry.method == "advance_frame_ticks":
			var result: Dictionary = _session.advance_frame_ticks(entry.arguments[0])
			frames += 1
			_advance(entry.expected, result, frames)
			steps += int(entry.expected.steps_advanced)
		else:
			var result: Variant = _session.callv(entry.method, entry.arguments)
			if result is Dictionary:
				_check("operations", entry.method + " accepted", result.ok, true)
	_check("trace", "frames and steps replayed", [frames, steps], [4_248, 3_616])
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(),
		"failures": failures.slice(0, 40), "frames": frames, "steps": steps}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		push_error("Cannot write the session report.")
		quit(2)
		return
	file.store_string(JSON.stringify(report, "  ", false) + "\n")
	file.close()
	print("interactive session checks: %d frames, %d steps, %d failures" % [frames, steps, failures.size()])
	quit(0 if failures.is_empty() else 1)


func _advance(expected: Dictionary, result: Dictionary, frame: int) -> void:
	var label: String = "frame %d" % frame
	if not _check("frames", label + " accepted", result.ok, true):
		return
	var value: Dictionary = result.value
	var alpha := PackedByteArray()
	alpha.resize(8)
	alpha.encode_double(0, value.interpolation_alpha)
	_check("frames", label, [value.steps_advanced, value.frame_time_capped, value.interpolation_phase, alpha.decode_s64(0)],
		[expected.steps_advanced, expected.frame_time_capped, expected.interpolation_phase, expected.interpolation_alpha_bits])
	if int(expected.steps_advanced) > 0:
		_check("frames", label + " state hash", _bridge.GetStateHash().value, expected.state_hash)
		_check("frames", label + " consumed input", _bridge.GetLastConsumedInput().value, expected.consumed)


func _compare(entry: Dictionary) -> void:
	var metrics: Dictionary = _session.metrics()
	var actual: Dictionary = {}
	for key: String in METRICS:
		actual[key] = metrics[key]
	_check("metrics", entry.compare, actual, entry.metrics)
	_check("flags", entry.compare, [_session.is_paused(), _session.is_authentic_menu_paused(),
		_session.input_suspended_until_released(), _session.has_held_or_pending_input(), _session.interpolation_phase()], entry.flags)


func _refusal(entry: Dictionary) -> void:
	var result: Dictionary
	match String(entry.refusal):
		"zero movement pulse": result = _session.queue_movement_pulse(0, 0)
		"zero look pulse": result = _session.queue_look_pulse(0, 0)
		"out-of-range movement pulse": result = _session.queue_movement_pulse(2, 0)
		"zero pointer motion": result = _session.queue_pointer_motion_milli_pixels(0, 0)
		"negative frame": result = _session.advance_frame_ticks(-1)
		"zero sensitivity": result = _session.set_mouse_sensitivity(0.0)
		"out-of-range held input": result = _session.observe_input({"move_x": 2, "move_z": 0, "fire_held": false,
			"toggle_mode_held": false, "reset_held": false, "look_x": 0, "look_y": 0, "landing_jets_held": false})
		_: result = {"ok": true}
	_check("refusals", entry.refusal, [result.ok, result.get("error_type")], [false, entry.expected_type])


func _check(group: String, name: String, actual: Variant, expected: Variant) -> bool:
	counts[group] = int(counts.get(group, 0)) + 1
	if typeof(actual) != typeof(expected) or actual != expected:
		failures.append({"group": group, "name": name, "actual": str(actual), "expected": str(expected)})
		return false
	return true
