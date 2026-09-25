# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Deterministic CEventManager pool, ring, overflow ordering and recycler.
## Port of Core/RetailEventScheduler.cs and pinned eventmanager.cpp/.h.
## Retail identities: AddEvent 0x0044b370, Update 0x0044b5c0, Flush 0x0044b640;
## evidence boundary: reverse-engineering/source-code/io/event-system.md.
## No clocks, scene nodes, files or Godot timers own this state.
##
## Operations return {ok, value} or {ok:false, error}. A retail refusal is an
## admitted Placement value, not an API error. Callbacks are synchronous and
## MUST return an explicit {ok:true} or failed result. A missing/default return
## (including a GDScript runtime error) interrupts and poisons Flush until init.
## A caller may handle a nested-operation refusal and return success, matching
## C#'s caught-exception path; propagating it matches the uncaught path.

const Float24 = preload("res://Core/retail_float24.gd")
const EVENT_LIST_BUFFERS: int = 200
const PRIORITY_LANES: int = 3
const MAX_EVENTS: int = 20000
const OVERFLOW_BUCKET_THRESHOLD: int = 198
const NEXT_FRAME: float = -1.0
enum Priority { START_OF_FRAME, MIDDLE_OF_FRAME, END_OF_FRAME }
enum Placement { REJECTED_INVALID_MANAGER, REJECTED_NULL_LISTENER,
	REJECTED_TOO_FAR_AHEAD, REJECTED_POOL_EXHAUSTED,
	IMMEDIATE_BUCKET, DELAYED_BUCKET, OVERFLOW }

static var _clock_tick: float = Float24.read_word(0x3d4ccccd)
static var _immediate_window: float = Float24.read_word(0x3d50e560)
static var _immediate_floor: float = Float24.read_word(0x38d1b717)
static var _delay_bias: float = Float24.read_word(0x3a83126f)

var _float24: bool
var _next_free := PackedInt32Array()
var _event_num := PackedInt32Array()
var _listener := PackedInt32Array()
var _data := PackedInt32Array()
var _time_bits := PackedInt64Array()
var _reuse := PackedByteArray()
var _ring: Array[Array] = []
var _overflow: Array[int] = []
var _dispatched: Array[Dictionary] = []
var _changed: Dictionary = {}
var _free_list: int = -1
var _time: float = 0.0
var _frame_count: int = 0
var _current_buffer: int = 0
var _ready_buffer: int = 0
var _live_events: int = 0
var _overflow_cursor: int = 0
var _total_processed: int = 0
var _processed_this_update: int = 0
var _valid: bool = false
var _flushing: bool = false
var _interrupted: bool = false


func _init(use_float24_arithmetic: bool = false) -> void:
	_float24 = use_float24_arithmetic
	_next_free.resize(MAX_EVENTS)
	_event_num.resize(MAX_EVENTS)
	_listener.resize(MAX_EVENTS)
	_data.resize(MAX_EVENTS)
	_time_bits.resize(MAX_EVENTS)
	_reuse.resize(MAX_EVENTS)
	for _index: int in range(EVENT_LIST_BUFFERS * PRIORITY_LANES):
		_ring.append([])
	init()


func init() -> Dictionary:
	if _flushing:
		return _fail("Cannot reset during Flush.")
	_interrupted = false
	_changed.clear()
	_time = 0.0
	_current_buffer = 0
	_frame_count = 0
	_live_events = 0
	_processed_this_update = 0
	_total_processed = 0
	_ready_buffer = 0
	_overflow_cursor = 0
	_overflow.clear()
	_dispatched.clear()
	for lane: Array in _ring:
		lane.clear()
	_event_num.fill(0)
	_listener.fill(0)
	_data.fill(0)
	_time_bits.fill(0)
	_reuse.fill(0)
	for index: int in range(MAX_EVENTS):
		_next_free[index] = index + 1 if index < MAX_EVENTS - 1 else -1
	_free_list = 0
	_valid = true
	return _ok()


func shutdown() -> Dictionary:
	_valid = false
	for lane: Array in _ring:
		lane.clear()
	_overflow.clear()
	return _ok()


## These are the same observable scalar fields available on the C# owner.
func public_state() -> Dictionary:
	return {"time_bits": Float24.store_word(_time), "frame_count": _frame_count,
		"current_buffer": _current_buffer, "ready_buffer": _ready_buffer,
		"live_events": _live_events, "total_processed": _total_processed,
		"processed_this_update": _processed_this_update, "valid": _valid,
		"free_list": _free_list, "float24": _float24}


func snapshot() -> Dictionary:
	if _flushing or _interrupted:
		return _fail("Cannot capture an active or interrupted Flush.")
	var state: Dictionary = public_state()
	var handles: Array = _changed.keys()
	handles.sort()
	var slots: Array[Dictionary] = []
	for handle: int in handles:
		slots.append(_slot(handle))
	var lanes: Array[Dictionary] = []
	for index: int in range(_ring.size()):
		if not _ring[index].is_empty():
			lanes.append({"lane_index": index, "handles": _ring[index].duplicate()})
	state["slots"] = slots
	state["lanes"] = lanes
	state["overflow"] = _overflow.duplicate()
	return _ok(state)


## A failed restore never mutates an existing owner. All supplied collections
## are copied; callers must decode JSON integer tokens before this boundary.
static func from_snapshot(state: Variant) -> Dictionary:
	var owner = load_self_new()
	var result: Dictionary = owner._restore(state)
	return _ok(owner) if result.ok else result


static func load_self_new():
	# Explicit self preload is unnecessary: new() resolves this script directly,
	# without a global class-name/import cache.
	return new()


func _restore(state: Variant) -> Dictionary:
	if not state is Dictionary:
		return _fail("Scheduler snapshot must be a Dictionary.")
	for key: String in ["time_bits", "frame_count", "total_processed", "processed_this_update"]:
		if not _integer(state.get(key), 0, 0xffffffff):
			return _fail("Invalid unsigned scheduler field: " + key)
	for key: String in ["current_buffer", "ready_buffer"]:
		if not _integer(state.get(key), 0, EVENT_LIST_BUFFERS - 1):
			return _fail("Invalid scheduler buffer: " + key)
	if not _integer(state.get("free_list"), -1, MAX_EVENTS - 1) or not _integer(state.get("live_events"), 0, MAX_EVENTS):
		return _fail("Invalid scheduler ownership counts.")
	if typeof(state.get("valid")) != TYPE_BOOL or typeof(state.get("float24")) != TYPE_BOOL:
		return _fail("Invalid scheduler flags.")
	if state.time_bits != Float24.store_word(time_at_frame_count(state.frame_count)):
		return _fail("Scheduler time does not match its frame counter.")
	for key: String in ["slots", "lanes", "overflow"]:
		if not state.get(key) is Array:
			return _fail("Invalid scheduler collection: " + key)
	var previous: int = -1
	for item: Variant in state.slots:
		if not item is Dictionary:
			return _fail("Invalid scheduler slot.")
		if not _integer(item.get("handle"), 0, MAX_EVENTS - 1) or item.handle <= previous:
			return _fail("Invalid or noncanonical pool slot.")
		if not _integer(item.get("next_free"), -1, MAX_EVENTS - 1) or not _integer(item.get("event_num"), -32768, 32767):
			return _fail("Invalid pool slot words.")
		if not _integer(item.get("listener"), -2147483648, 2147483647) or not _integer(item.get("data"), -2147483648, 2147483647):
			return _fail("Invalid pool identities.")
		if not _integer(item.get("time_bits"), 0, 0xffffffff) or typeof(item.get("reuse")) != TYPE_BOOL:
			return _fail("Invalid pool time or reuse flag.")
		var handle: int = item.handle
		previous = handle
		_next_free[handle] = item.next_free
		_event_num[handle] = item.event_num
		_listener[handle] = item.listener
		_data[handle] = item.data
		_time_bits[handle] = item.time_bits
		_reuse[handle] = 1 if item.reuse else 0
		_track_slot(handle)
		if not _changed.has(handle):
			return _fail("Baseline pool slots must be omitted.")
	var queued: Dictionary = {}
	previous = -1
	for item: Variant in state.lanes:
		if not item is Dictionary or not _integer(item.get("lane_index"), 0, _ring.size() - 1):
			return _fail("Invalid scheduler lane.")
		if item.lane_index <= previous or not item.get("handles") is Array or item.handles.is_empty():
			return _fail("Invalid or noncanonical lane.")
		previous = item.lane_index
		for handle: Variant in item.handles:
			if not _integer(handle, 0, MAX_EVENTS - 1) or queued.has(handle):
				return _fail("Invalid or multiply queued handle.")
			queued[handle] = true
			_ring[item.lane_index].append(handle)
	for handle: Variant in state.overflow:
		if not _integer(handle, 0, MAX_EVENTS - 1) or queued.has(handle):
			return _fail("Invalid or multiply queued overflow handle.")
		queued[handle] = true
		_overflow.append(handle)
	var free: Dictionary = {}
	var cursor: int = state.free_list
	while cursor != -1:
		if free.has(cursor) or queued.has(cursor):
			return _fail("Free-list cycle or queued ownership overlap.")
		free[cursor] = true
		cursor = _next_free[cursor]
	if (state.valid and state.live_events != queued.size()) or (not state.valid and not queued.is_empty()):
		return _fail("Scheduler event count disagrees with queue ownership.")
	_float24 = state.float24
	_free_list = state.free_list
	_time = Float24.read_word(state.time_bits)
	_frame_count = state.frame_count
	_current_buffer = state.current_buffer
	_ready_buffer = state.ready_buffer
	_live_events = state.live_events
	_total_processed = state.total_processed
	_processed_this_update = state.processed_this_update
	_valid = state.valid
	return _ok()


func get_next_free_event() -> Dictionary:
	var head: int = _free_list
	if head >= 0:
		_free_list = _next_free[head]
	return _ok(head)


func add_event(event_num: Variant, listener: Variant, due: Variant,
		priority: Variant = Priority.START_OF_FRAME, data: Variant = 0, reuse_handle: Variant = -1) -> Dictionary:
	if not _request_integers(event_num, listener, priority, data, reuse_handle):
		return _fail("Event admission requires int32 identities, priority and reuse handle.")
	if not _numeric(due):
		return _fail("Event time must be numeric.")
	var time: float = Float24.store_float32(float(due))
	if not _valid:
		return _admission(Placement.REJECTED_INVALID_MANAGER)
	if listener == 0:
		return _admission(Placement.REJECTED_NULL_LISTENER)
	var next_bits: int = Float24.store_word(time)
	var offset: int
	var placement: int
	var immediate: float = Float24.add_finite(_time, _immediate_window) if _float24 else _time + _immediate_window
	if immediate >= time:
		placement = Placement.IMMEDIATE_BUCKET
		offset = _current_buffer
		if time < 0.0:
			next_bits = Float24.store_word(_stored_sum(_time, _immediate_floor))
	else:
		if time > 1000000.0:
			return _admission(Placement.REJECTED_TOO_FAR_AHEAD, -1, -1, -1, next_bits)
		# The PC24 owner throws at its first nonfinite rounded subtraction.
		# The net8 PC53 owner's unchecked NaN-to-int32 conversion instead gives
		# INT_MIN. Preserve its subsequent modulo/Acquire/indexing order; do not
		# reject early and silently change pool mutation. Differential fixtures
		# pin the selected C# runtime's conversion, including a valid aliased lane.
		if is_nan(time):
			if _float24:
				return _fail("Retail arithmetic must receive a finite rounding input.")
			offset = -2147483648
		else:
			var delay: float = Float24.multiply_finite(Float24.subtract_finite(Float24.subtract_finite(time, _time), _delay_bias), 20.0) if _float24 else ((time - _time) - _delay_bias) * 20.0
			offset = int(floor(delay))
		if offset >= OVERFLOW_BUCKET_THRESHOLD:
			var add_point: int = _overflow_cursor
			while add_point < _overflow.size() and _due_time(_overflow[add_point]) <= time:
				add_point += 1
			var handle: int = _acquire(reuse_handle, event_num, next_bits, listener, data)
			if handle == -2:
				return _fail("Reuse handle is outside the event pool.")
			if handle < 0:
				return _admission(Placement.REJECTED_POOL_EXHAUSTED, -1, -1, -1, next_bits)
			_overflow.insert(add_point, handle)
			_live_events = _signed32(_live_events + 1)
			return _admission(Placement.OVERFLOW, handle, -1, add_point, next_bits)
		placement = Placement.DELAYED_BUCKET
		offset = (_current_buffer + offset) % EVENT_LIST_BUFFERS
	var handle: int = _acquire(reuse_handle, event_num, next_bits, listener, data)
	if handle == -2:
		return _fail("Reuse handle is outside the event pool.")
	if handle < 0:
		return _admission(Placement.REJECTED_POOL_EXHAUSTED, -1, -1, -1, next_bits)
	# C#'s int-backed enum also admits other int32 values. Flat lane indexing
	# can alias another valid lane; invalid indices fail AFTER Acquire, with no
	# live-count increment. This is reconstruction API parity, not a claim about
	# which priorities retail callers use.
	var lane_index: int = _signed32(offset * PRIORITY_LANES + int(priority))
	if lane_index < 0 or lane_index >= _ring.size():
		return _fail("Computed event lane is outside the ring.")
	_ring[lane_index].append(handle)
	_live_events = _signed32(_live_events + 1)
	return _admission(placement, handle, offset, -1, next_bits)


func add_event_time_from_now(delay: Variant, event_num: Variant, listener: Variant,
		priority: Variant = Priority.START_OF_FRAME, data: Variant = 0, reuse_handle: Variant = -1) -> Dictionary:
	if not _numeric(delay):
		return _fail("Relative event time must be numeric.")
	var sum: float = _time + Float24.store_float32(float(delay))
	if _float24:
		var rounded: Float24.Result = Float24.try_round(sum)
		if not rounded.ok:
			return _fail(rounded.error)
		sum = rounded.value
	return add_event(event_num, listener, Float24.store_float32(sum), priority, data, reuse_handle)


func prepare_owned_event(event_num: Variant, listener: Variant, due: Variant, data: Variant = 0) -> Dictionary:
	if not _request_integers(event_num, listener, 0, data, -1) or not _numeric(due):
		return _fail("Invalid owned event fields.")
	return _ok(_acquire(-1, event_num, Float24.store_word(float(due)), listener, data))


func add_owned_event(handle: Variant) -> Dictionary:
	if not _integer(handle, -2147483648, MAX_EVENTS - 1):
		return _fail("Invalid owned event handle.")
	if handle < 0:
		return _admission(Placement.REJECTED_NULL_LISTENER)
	var admitted: Dictionary = add_event_time_from_now(_due_time(handle), _event_num[handle], _listener[handle], Priority.START_OF_FRAME, _data[handle])
	if admitted.ok:
		_free_event(handle)
	return admitted


func clear_listener(handle: Variant) -> Dictionary:
	if not _integer(handle, 0, MAX_EVENTS - 1):
		return _fail("Invalid listener handle.")
	_listener[handle] = 0
	_track_slot(handle)
	return _ok()


func free_event(handle: Variant) -> Dictionary:
	if not _integer(handle, 0, MAX_EVENTS - 1):
		return _fail("Invalid free handle.")
	_free_event(handle)
	return _ok()


func free_event_count() -> Dictionary:
	var visited: Dictionary = {}
	var cursor: int = _free_list
	while cursor >= 0:
		if cursor >= MAX_EVENTS or visited.has(cursor):
			return _fail("Free-list cycle or invalid link.")
		visited[cursor] = true
		cursor = _next_free[cursor]
	return _ok(visited.size())


func slot(handle: Variant) -> Dictionary:
	if not _integer(handle, 0, MAX_EVENTS - 1):
		return _fail("Invalid pool handle.")
	return _ok(_slot(handle))


## Deliberately allowed during a callback, as in the existing overflow-bound test.
func advance_time() -> Dictionary:
	_frame_count = (_frame_count + 1) & 0xffffffff
	_ready_buffer = _current_buffer
	_time = time_at_frame_count(_frame_count)
	_current_buffer = (_current_buffer + 1) % EVENT_LIST_BUFFERS
	return _ok()


static func time_at_frame_count(frame_count: int) -> float:
	# The argument is a uint32 word, not elapsed seconds. It has one F32 store.
	return Float24.store_float32(float(frame_count & 0xffffffff) * _clock_tick)


func update(handler: Variant = null) -> Dictionary:
	if _flushing or _interrupted:
		return _fail("Cannot resume an active or interrupted Flush.")
	if not _handler_valid(handler):
		return _fail("Scheduler handler must be a valid synchronous Callable or null.")
	advance_time()
	return flush(handler)


func flush(handler: Variant = null) -> Dictionary:
	if _flushing or _interrupted:
		return _fail("Cannot resume an active or interrupted Flush.")
	if not _handler_valid(handler):
		return _fail("Scheduler handler must be a valid synchronous Callable or null.")
	_flushing = true
	var result: Dictionary = _flush_core(handler)
	_flushing = false
	if result.get("ok") != true:
		_interrupted = true
		return _fail(str(result.get("error", "Scheduler callback or flush did not complete.")))
	return result


func _flush_core(handler: Variant) -> Dictionary:
	var previous: int = _total_processed
	var ready: int = _ready_buffer
	_overflow_cursor = 0
	_dispatched.clear()
	for lane: int in range(PRIORITY_LANES):
		var entries: Array = _ring[ready * PRIORITY_LANES + lane]
		var index: int = 0
		while index < entries.size():
			var handle: int = entries[index]
			_reuse[handle] = 0
			_track_slot(handle)
			if _listener[handle] != 0:
				var result: Dictionary = _dispatch(handler, handle, lane, false)
				if result.get("ok") != true:
					return result
			_total_processed = (_total_processed + 1) & 0xffffffff
			index += 1
	# Capture AFTER ring callbacks, BEFORE the first overflow callback.
	var overflow_count: int = _overflow.size()
	while overflow_count > _overflow_cursor and _due_time(_overflow[_overflow_cursor]) < _time:
		var handle: int = _overflow[_overflow_cursor]
		_reuse[handle] = 0
		_track_slot(handle)
		_overflow_cursor += 1
		if _listener[handle] != 0:
			var result: Dictionary = _dispatch(handler, handle, Priority.END_OF_FRAME, true)
			if result.get("ok") != true:
				return result
		_total_processed = (_total_processed + 1) & 0xffffffff
	for lane: int in range(PRIORITY_LANES):
		var entries: Array = _ring[ready * PRIORITY_LANES + lane]
		for handle: int in entries:
			if _reuse[handle] == 0:
				_free_event(handle)
			_live_events = _signed32(_live_events - 1)
		entries.clear()
	if _overflow_cursor > 0:
		for index: int in range(_overflow_cursor - 1, -1, -1):
			var handle: int = _overflow[index]
			if _reuse[handle] == 0:
				_free_event(handle)
			_live_events = _signed32(_live_events - 1)
		_overflow = _overflow.slice(_overflow_cursor)
	_overflow_cursor = 0
	_processed_this_update = (_total_processed - previous) & 0xffffffff
	return _ok(_dispatched.duplicate(true))


func _dispatch(handler: Variant, handle: int, priority: int, from_overflow: bool) -> Dictionary:
	var dispatch: Dictionary = {"handle": handle, "event_num": _event_num[handle],
		"listener": _listener[handle], "due_time_bits": _time_bits[handle],
		"priority": priority, "from_overflow": from_overflow}
	_dispatched.append(dispatch)
	if handler == null:
		return _ok()
	# Dispatch is a value in C#, so a callback receives a detached dictionary.
	var result: Variant = handler.call(self, dispatch.duplicate())
	if not result is Dictionary or typeof(result.get("ok")) != TYPE_BOOL:
		return _fail("Scheduler callback must return an explicit operation result.")
	return result


func _free_event(handle: int) -> void:
	_next_free[handle] = _free_list
	_data[handle] = 0
	_listener[handle] = 0
	_free_list = handle
	_track_slot(handle)


func _acquire(reuse_handle: int, event_num: int, time_bits: int, listener: int, data: int) -> int:
	if reuse_handle >= MAX_EVENTS:
		return -2 # Explicit equivalent of the C# pool-index exception, not exhaustion.
	if reuse_handle >= 0:
		_time_bits[reuse_handle] = time_bits
		_event_num[reuse_handle] = _signed16(event_num)
		_reuse[reuse_handle] = 1
		if data != 0:
			_data[reuse_handle] = data
		_track_slot(reuse_handle)
		return reuse_handle
	var handle: int = _free_list
	if handle < 0:
		return -1
	_free_list = _next_free[handle]
	_event_num[handle] = _signed16(event_num)
	_time_bits[handle] = time_bits
	_listener[handle] = listener
	_data[handle] = data
	_reuse[handle] = 0
	_next_free[handle] = -1
	_track_slot(handle)
	return handle


func _track_slot(handle: int) -> void:
	var initial_next: int = handle + 1 if handle < MAX_EVENTS - 1 else -1
	if _next_free[handle] == initial_next and _event_num[handle] == 0 and _listener[handle] == 0 and _data[handle] == 0 and _time_bits[handle] == 0 and _reuse[handle] == 0:
		_changed.erase(handle)
	else:
		_changed[handle] = true


func _slot(handle: int) -> Dictionary:
	return {"handle": handle, "next_free": _next_free[handle], "event_num": _event_num[handle],
		"listener": _listener[handle], "data": _data[handle], "time_bits": _time_bits[handle], "reuse": _reuse[handle] != 0}


func _due_time(handle: int) -> float:
	return Float24.read_word(_time_bits[handle])


func _stored_sum(left: float, right: float) -> float:
	return Float24.store_float32(Float24.add_finite(left, right) if _float24 else left + right)


static func _signed16(value: int) -> int:
	var word: int = value & 0xffff
	return word - 0x10000 if word >= 0x8000 else word


static func _signed32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word >= 0x80000000 else word


static func _request_integers(event_num: Variant, listener: Variant, priority: Variant, data: Variant, reuse_handle: Variant) -> bool:
	return _integer(event_num, -2147483648, 2147483647) and _integer(listener, -2147483648, 2147483647) and _integer(data, -2147483648, 2147483647) and _integer(priority, -2147483648, 2147483647) and _integer(reuse_handle, -2147483648, 2147483647)


static func _handler_valid(handler: Variant) -> bool:
	return handler == null or (typeof(handler) == TYPE_CALLABLE and handler.is_valid())


static func _integer(value: Variant, minimum: int, maximum: int) -> bool:
	return typeof(value) == TYPE_INT and value >= minimum and value <= maximum


static func _numeric(value: Variant) -> bool:
	return typeof(value) == TYPE_FLOAT or typeof(value) == TYPE_INT


static func _admission(placement: int, handle: int = -1, buffer_index: int = -1, overflow_index: int = -1, due_time_bits: int = 0) -> Dictionary:
	return _ok({"placement": placement, "handle": handle, "buffer_index": buffer_index,
		"overflow_index": overflow_index, "due_time_bits": due_time_bits})


static func _ok(value: Variant = null) -> Dictionary:
	return {"ok": true, "value": value}


static func _fail(error: String) -> Dictionary:
	return {"ok": false, "error": error}
