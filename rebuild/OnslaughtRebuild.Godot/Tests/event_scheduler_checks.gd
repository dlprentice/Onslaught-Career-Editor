# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Differential transcript from GdscriptEventSchedulerOracle.BuildFixtures().
## Inputs contain only integer identities/float words; there are no asset reads.

const Scheduler = preload("res://Core/retail_event_scheduler.gd")
const Float24 = preload("res://Core/retail_float24.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []
var _owner: RefCounted
var _trace: Array[Dictionary] = []
var _nested_callbacks: int = 0


func _initialize() -> void:
	call_deferred("run_checks")


func check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[category] = int(counts.get(category, 0)) + 1
	if actual != expected:
		failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	check("fixture", "object", parsed is Dictionary, true)
	if parsed is Dictionary:
		var vectors: Variant = _integer_tokens(parsed.get("scheduler"))
		var fixture_completed: bool = _run_fixtures(vectors)
		var boundary_completed: bool = _check_api_boundary()
		var retail_boundary_completed: bool = _check_committed_queue_boundaries()
		if fixture_completed and boundary_completed and retail_boundary_completed:
			completed.append("event_scheduler")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": completed}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() and completed == ["event_scheduler"] else 1)


func _integer_tokens(value: Variant) -> Variant:
	# Godot JSON parses all numeric tokens as doubles. This fixture schema has
	# integer tokens only, bounded below 2^53; no simulation value is converted.
	if typeof(value) == TYPE_FLOAT:
		var exact: bool = is_finite(value) and abs(value) <= 9007199254740991.0 and floor(value) == value
		if not exact:
			check("fixture", "integer_token", value, "exact integer")
			return value
		return int(value)
	if value is Array:
		var array: Array = []
		for item: Variant in value:
			array.append(_integer_tokens(item))
		return array
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value:
			result[key] = _integer_tokens(value[key])
		return result
	return value


func _run_fixtures(vectors: Variant) -> bool:
	check("fixture", "scheduler_object", vectors is Dictionary, true)
	if not vectors is Dictionary:
		return false
	check("fixture", "schema", vectors.get("schema"), 1)
	var cases: Variant = vectors.get("cases")
	check("fixture", "cases_array", cases is Array, true)
	if not cases is Array:
		return false
	check("fixture", "nonempty_cases", not cases.is_empty(), true)
	if cases.is_empty():
		return false
	var finished: int = 0
	for row: Dictionary in cases:
		var success: bool = _run_case(row)
		check("fixture", str(row.get("name")) + ":completed", success, true)
		if success:
			finished += 1
	return finished == cases.size()


func _run_case(row: Dictionary) -> bool:
	_owner = Scheduler.new(row.float24)
	var steps: Array = row.steps
	check("fixture", row.name + ":nonempty_steps", not steps.is_empty(), true)
	if steps.is_empty():
		return false
	for index: int in range(steps.size()):
		var step: Dictionary = steps[index]
		var name: String = "%s:%d:%s" % [row.name, index, step.input.op]
		_trace.clear()
		var result: Dictionary = _execute(step.input)
		check("result", name, _result_shape(result), step.result)
		check("state", name, _owner.public_state(), step.state)
		check("callback", name, _trace, step.trace)
		if step.snapshot != null:
			check("snapshot", name, _result_shape(_owner.snapshot()), step.snapshot)
	return true


func _execute(input: Dictionary) -> Dictionary:
	match input.op:
		"init": return _owner.init()
		"shutdown": return _owner.shutdown()
		"advance":
			for _index: int in range(int(input.get("count", 1))):
				_owner.advance_time()
			return _ok()
		"add":
			return _owner.add_event(input.event_num, input.listener, Float24.read_word(input.time_bits), input.priority, input.data, input.reuse_handle)
		"add_relative":
			return _owner.add_event_time_from_now(Float24.read_word(input.time_bits), input.event_num, input.listener, input.priority, input.data, input.reuse_handle)
		"prepare_owned":
			return _owner.prepare_owned_event(input.event_num, input.listener, Float24.read_word(input.time_bits), input.data)
		"add_owned": return _owner.add_owned_event(input.handle)
		"free": return _owner.free_event(input.handle)
		"clear_listener": return _owner.clear_listener(input.handle)
		"get_free": return _owner.get_next_free_event()
		"free_count": return _owner.free_event_count()
		"slot": return _owner.slot(input.handle)
		"snapshot": return _owner.snapshot()
		"restore": return _restore(_owner.snapshot())
		"mutate_restore":
			var captured: Dictionary = _owner.snapshot()
			if captured.get("ok") != true:
				return captured
			var changed: Dictionary = captured.value
			match input.mutation:
				"free_cycle", "baseline_slot":
					changed.slots = [{"handle": 0, "next_free": 0 if input.mutation == "free_cycle" else 1,
						"event_num": 0, "listener": 0, "data": 0, "time_bits": 0, "reuse": false}]
				"free_range": changed.free_list = Scheduler.MAX_EVENTS
				"clock_word": changed.time_bits = int(changed.time_bits) ^ 1
				"queued_free": changed.free_list = 0
				"queued_twice": changed.overflow = [0]
				_: return {"ok": false, "error": "Unknown snapshot mutation."}
			return _restore(_ok(changed))
		"restore_counters":
			var captured: Dictionary = _owner.snapshot()
			if captured.get("ok") != true:
				return captured
			captured.value.frame_count = input.frame
			captured.value.time_bits = Float24.store_word(Scheduler.time_at_frame_count(input.frame))
			captured.value.total_processed = input.processed
			return _restore(captured)
		"fill_pool":
			var admitted: int = 0
			var handle_sum: int = 0
			for _index: int in range(Scheduler.MAX_EVENTS):
				var admission: Dictionary = _owner.add_event(1, 1, Float24.read_word(0x3d4ccccd))
				if admission.get("ok") != true:
					return admission
				if admission.value.placement == Scheduler.Placement.IMMEDIATE_BUCKET:
					admitted += 1
				handle_sum += int(admission.value.handle)
			return _ok({"admitted": admitted, "handle_sum": handle_sum})
		"flush": return _owner.flush(_handler(str(input.get("handler", ""))))
		"update":
			var batches: Array[Dictionary] = []
			var handler: Variant = _handler(str(input.get("handler", "")))
			for index: int in range(int(input.get("count", 1))):
				var result: Dictionary = _owner.update(handler)
				if result.get("ok") != true:
					return result
				if not result.value.is_empty():
					batches.append({"iteration": index, "events": result.value})
			return _ok(batches)
	return {"ok": false, "error": "Unknown scheduler fixture operation."}


func _restore(captured: Dictionary) -> Dictionary:
	if captured.get("ok") != true:
		return captured
	var result: Dictionary = Scheduler.from_snapshot(captured.value)
	if result.get("ok") == true:
		_owner = result.value
		return _ok()
	return result


func _handler(mode: String) -> Variant:
	if mode.is_empty():
		return null
	return func(owner: RefCounted, item: Dictionary) -> Dictionary:
		return _callback(owner, item, mode)


func _callback(owner: RefCounted, item: Dictionary, mode: String) -> Dictionary:
	match mode:
		"snapshot_then_fail":
			_trace.append({"op": "active_snapshot", "result": _result_shape(owner.snapshot())})
			return {"ok": false, "error": "test callback interruption"}
		"uncaught_nested": return owner.update()
		"caught_nested":
			var before: Dictionary = owner.public_state()
			_nested_callbacks = 0
			var result: Dictionary = owner.update(_unexpected_nested)
			_trace.append({"op": "nested_update", "before": before, "result": _result_shape(result),
				"after": owner.public_state(), "callbacks": _nested_callbacks})
			return _rearm(owner, item, false)
		"rearm_start": return _rearm(owner, item, false)
		"rearm_same": return _rearm(owner, item, true)
		"overflow_append":
			if item.event_num != 99:
				return _ok()
			var admission: Dictionary = owner.add_event(100, 1, 20.0)
			if admission.get("ok") != true:
				return admission
			for _frame: int in range(201):
				owner.advance_time()
			_trace.append({"op": "overflow_append", "admission": admission.value, "state": owner.public_state()})
			return _ok()
	return {"ok": false, "error": "Unknown callback fixture mode."}


func _unexpected_nested(_owner_argument: RefCounted, _item: Dictionary) -> Dictionary:
	_nested_callbacks += 1
	return _ok()


func _rearm(owner: RefCounted, item: Dictionary, same_priority: bool) -> Dictionary:
	var reuse_before: bool = owner.slot(item.handle).value.reuse
	var admitted: Dictionary = owner.add_event(item.event_num, item.listener if same_priority else 999,
		-1.0, item.priority if same_priority else Scheduler.Priority.START_OF_FRAME, 0, item.handle)
	_trace.append({"op": "rearm", "reuse_before": reuse_before,
		"admission": admitted.get("value"), "reuse_after": owner.slot(item.handle).value.reuse})
	return admitted


func _check_api_boundary() -> bool:
	# These are explicit GDScript admission/value-isolation contracts, not new
	# expected retail behavior. C#'s typed parameters/exceptions provide their
	# corresponding boundary. Numeric failure/mutation order, including NaN and
	# int32 enum aliases, is instead covered by the C# differential transcript.
	var owner = Scheduler.new()
	var before: Dictionary = owner.snapshot().value
	for invalid: Variant in [null, "1", 1.5, -2147483649, 2147483648]:
		check("admission", "invalid_event", owner.add_event(invalid, 1, -1).ok, false)
		check("admission", "invalid_listener", owner.add_event(1, invalid, -1).ok, false)
		check("admission", "invalid_data", owner.add_event(1, 1, -1, 0, invalid).ok, false)
		check("admission", "invalid_keeps_state", owner.snapshot().value, before)
	for invalid: Variant in [-2147483649, 2147483648, 1.5, "1", null]:
		check("admission", "invalid_priority", owner.add_event(1, 1, -1, invalid).ok, false)
	for invalid: Variant in [null, "1"]:
		check("admission", "invalid_time", owner.add_event(1, 1, invalid).ok, false)
	check("admission", "invalid_reuse", owner.add_event(1, 1, -1, 0, 0, Scheduler.MAX_EVENTS).ok, false)
	check("admission", "invalid_handler", owner.update(Callable()).ok, false)
	check("admission", "invalid_calls_keep_state", owner.snapshot().value, before)
	var malformed: Dictionary = before.duplicate(true)
	malformed.frame_count = 0.5
	check("admission", "snapshot_fractional_word", Scheduler.from_snapshot(malformed).ok, false)
	malformed = before.duplicate(true)
	malformed.valid = 1
	check("admission", "snapshot_integer_flag", Scheduler.from_snapshot(malformed).ok, false)
	check("admission", "snapshot_null", Scheduler.from_snapshot(null).ok, false)

	owner.add_event(42, 11, -1, 0, 91)
	owner.add_event(99, 12, 10.0)
	var snapshot: Dictionary = owner.snapshot().value
	var saved: Dictionary = snapshot.duplicate(true)
	snapshot.slots[0].listener = 999
	snapshot.lanes[0].handles[0] = 7
	snapshot.overflow.clear()
	check("isolation", "snapshot_is_detached", owner.snapshot().value, saved)
	var restored_result: Dictionary = Scheduler.from_snapshot(saved)
	check("isolation", "restore_admitted", restored_result.ok, true)
	if not restored_result.ok:
		return false
	var restored: RefCounted = restored_result.value
	var expected: Dictionary = saved.duplicate(true)
	saved.slots[0].data = -999
	saved.lanes[0].handles.clear()
	saved.overflow.clear()
	check("isolation", "restore_copies_input", restored.snapshot().value, expected)
	var dispatches: Dictionary = restored.update(func(_model: RefCounted, item: Dictionary) -> Dictionary:
		item.event_num = -999
		item.listener = -999
		return _ok())
	check("isolation", "callback_cannot_rewrite_dispatch", dispatches.value[0].event_num, 42)
	check("isolation", "callback_cannot_rewrite_listener", dispatches.value[0].listener, 11)
	var retained: Array = dispatches.value.duplicate(true)
	restored.update()
	check("isolation", "later_flush_does_not_clear_result", dispatches.value, retained)

	owner.init()
	owner.add_event(1, 1, -1)
	var refused: Dictionary = owner.update(func(_model: RefCounted, _item: Dictionary): return null)
	check("callback_contract", "missing_acknowledgement_refused", refused.ok, false)
	check("callback_contract", "missing_acknowledgement_poisons", owner.snapshot().ok, false)
	var interrupted: Dictionary = owner.public_state()
	check("callback_contract", "retry_refused", owner.update().ok, false)
	check("callback_contract", "retry_does_not_advance", owner.public_state(), interrupted)
	check("callback_contract", "init_recovers", owner.init().ok, true)
	check("callback_contract", "init_restores_baseline", owner.snapshot().value, before)
	return true


func _check_committed_queue_boundaries() -> bool:
	# Committed original-code evidence, independent of the managed oracle:
	# d34f565d, binary-analysis/functions/CEventManager.cpp.md, September 19.
	# This checks only scheduler delivery. Component flag writes, native monitor
	# storage/allocation and the live scheduler precision mode remain outside it.
	for pc24: bool in [false, true]:
		var owner := Scheduler.new(pc24)
		owner.advance_time()
		check("retail_queue", "frame1_current", owner.public_state().current_buffer, 1)
		check("retail_queue", "frame1_ready", owner.public_state().ready_buffer, 0)
		var added: Dictionary = owner.add_event_time_from_now(-1.0, 0x12340bb8, 7)
		check("retail_queue", "relative_minus1_queued", added.value.placement, Scheduler.Placement.IMMEDIATE_BUCKET)
		owner.add_event_time_from_now(-1.0, 2999, 7)
		check("retail_queue", "insertion_does_not_dispatch", owner.public_state().total_processed, 0)
		check("retail_queue", "old_bucket_does_not_dispatch", owner.flush().value.size(), 0)
		owner.advance_time()
		var delivered: Array = owner.flush().value
		check("retail_queue", "next_bucket_count", delivered.size(), 2)
		if delivered.size() != 2:
			return false
		check("retail_queue", "low_word_and_fifo_first", delivered[0].event_num, 3000)
		check("retail_queue", "fifo_second", delivered[1].event_num, 2999)

		for frame: int in [20, 40]:
			owner.init()
			for _index: int in range(frame):
				owner.advance_time()
			added = owner.add_event_time_from_now(-1.0, 3000, 7)
			check("retail_queue", "relative_due_is_added_before_admission", owner.slot(added.value.handle).value.time_bits, 0 if frame == 20 else 0x3f800000)
			check("retail_queue", "relative_current_bucket_still_waits", owner.flush().value.size(), 0)
			check("retail_queue", "relative_delivered_next_advance", owner.update().value.size(), 1)

		owner.init()
		added = owner.add_event(3000, 7, 10.0)
		check("retail_queue", "ten_seconds_uses_overflow", added.value.placement, Scheduler.Placement.OVERFLOW)
		for _index: int in range(200):
			check("retail_queue", "overflow_not_before_or_at_due", owner.update().value.size(), 0)
		check("retail_queue", "frame200_exact_time", owner.public_state().time_bits, 0x41200000)
		check("retail_queue", "overflow_after_due", owner.update().value.size(), 1)

	# Both operands of the quick-path sum are float32, and this bounded sum fits
	# in binary64 exactly. Our explicit PC53 path therefore shares the measured
	# PC64 result for these four inputs; this is not a general PC64 emulation.
	for row: Array in [[false, 0x3f00418a, 2], [true, 0x3f00418a, 1],
			[false, 0x3f004189, 1], [true, 0x3f00418b, 2]]:
		var owner := Scheduler.new(row[0])
		for _index: int in range(9):
			owner.advance_time()
		check("retail_precision", "frame9_clock", owner.public_state().time_bits, 0x3ee66667)
		var added: Dictionary = owner.add_event(3000, 7, Float24.read_word(row[1]))
		check("retail_precision", "selected_bucket", added.value.buffer_index, 9 if row[2] == 1 else 10)
		check("retail_precision", "old_bucket_empty", owner.flush().value.size(), 0)
		for advance: int in range(1, 3):
			check("retail_precision", "precision_selects_delivery", owner.update().value.size(), 1 if advance == row[2] else 0)
	return true


static func _result_shape(result: Dictionary) -> Dictionary:
	# Do not allow an aborted/default Dictionary to masquerade as a refusal.
	if typeof(result.get("ok")) != TYPE_BOOL:
		return {"invalid_operation_result": true}
	if result.ok:
		return {"ok": true, "value": result.get("value")}
	return {"ok": false}


static func _ok(value: Variant = null) -> Dictionary:
	return {"ok": true, "value": value}
