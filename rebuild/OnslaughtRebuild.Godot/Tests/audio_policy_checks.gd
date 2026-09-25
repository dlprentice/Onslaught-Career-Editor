# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Differential pure-policy gate. Args: oracle JSON, fresh owned report path.
## No streams, asset reads, devices, simulation instances, or engine timers.

const Audio = preload("res://Client/audio_catalog.gd")
const Music = preload("res://Client/music_policy.gd")
const MessageQueue = preload("res://Client/character_message_queue.gd")
const F32 = preload("res://Core/retail_float24.gd")
var _failures: Array[Dictionary] = []
var _counts: Dictionary = {}
var _completed: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	_counts[category] = int(_counts.get(category, 0)) + 1
	if actual != expected:
		_failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	_check("fixture", "object", parsed is Dictionary, true)
	if parsed is Dictionary:
		var vectors: Variant = _integers(parsed.get("audio_policy"))
		_check("fixture", "audio_policy", vectors is Dictionary, true)
		if vectors is Dictionary:
			_check("fixture", "schema", vectors.get("schema"), 1)
			_run_catalog(vectors)
			_run_laws(vectors)
			_run_music(vectors)
			_run_queue(vectors)
			_run_host_admission_and_detachment()
			_completed.append("audio_policy")
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "counts": _counts,
		"failures": _failures, "completed": _completed}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"failure_count": _failures.size(), "counts": _counts, "first_failures": _failures.slice(0, 5)}))
	quit(0 if _failures.is_empty() and _completed == ["audio_policy"] else 1)


func _run_catalog(vectors: Dictionary) -> void:
	_check("fixture", "recipe_extent", vectors.recipes.size(), 75)
	for index: int in range(vectors.recipes.size()):
		var row: Dictionary = vectors.recipes[index]
		var actual: Dictionary
		match row.method:
			"effect": actual = Audio.get_effect(row.identity)
			"terminal": actual = Audio.get_terminal(row.identity)
			"transition": actual = Audio.get_aquila_transition(row.identity)
			"warning": actual = Audio.get_aquila_warning(row.identity)
			"loop": actual = Audio.get_actor_loop(row.identity)
			"frontend": actual = Audio.get_frontend(_units(row.cue_units))
			_: actual = {"ok": false, "error_type": "UnknownOperation"}
		if actual.ok:
			var recipe: Dictionary = actual.value.duplicate(true)
			recipe.linear_volume_word = F32.store_word(recipe.linear_volume)
			recipe.erase("linear_volume")
			actual = {"ok": true, "value": recipe}
		_check("recipes", str(index), _result(actual), row.expected)
	_check("character", "all_51_shared_specs", _plain(Audio.character_messages()), vectors.character_specs)
	_check("fixture", "character_extent", vectors.character.size(), 56)
	for row: Dictionary in vectors.character:
		_check("character", str(row.identity), _result(Audio.get_character_message(row.identity)), row.expected)
	_check("music_recipes", "tutorial", Audio.tutorial_music(), vectors.tutorial_music)
	_check("music_recipes", "frontend", Audio.frontend_music(), vectors.frontend_music)
	_check("constants", "exact", {
		"hostile_quiet_ticks": Audio.RETAIL_HOSTILE_ENVIRONMENT_QUIET_TICKS,
		"radio_volume_word": Audio.RETAIL_RADIO_MESSAGE_VOLUME_WORD,
		"hud_volume_word": Audio.RETAIL_HUD_MESSAGE_VOLUME_WORD,
		"default_effect_volume_word": Audio.RETAIL_DEFAULT_EFFECT_VOLUME_WORD,
		"weapon_launch_volume_word": Audio.RETAIL_WEAPON_LAUNCH_VOLUME_WORD,
		"far_sound_word": F32.store_word(Audio.RETAIL_FAR_SOUND_UNITS),
		"untracked_source_volume": Audio.RETAIL_UNTRACKED_SOURCE_VOLUME,
		"listener_source_volume": Audio.RETAIL_LISTENER_SOURCE_VOLUME,
		"unfaded_sub_volume_word": F32.store_word(Audio.RETAIL_UNFADED_SUB_VOLUME),
		"flight_fade_step_word": Audio.RETAIL_FLIGHT_LOOP_FADE_STEP_WORD,
		"authored_music_volume_word": Music.AUTHORED_DEFAULT_VOLUME_WORD,
		"music_full_volume": Music.FULL_VOLUME, "music_fade_step": Music.FADE_STEP,
		"playlist_extension": Music.PLAYLIST_EXTENSION}, vectors.constants)
	for row: Dictionary in vectors.track_indices:
		_check("track_index", str(row.selection), _result(Music.track_index(row.selection)), row.expected)


func _run_laws(vectors: Dictionary) -> void:
	_check("fixture", "law_extent", vectors.laws.size(), 2024)
	for row: Dictionary in vectors.laws:
		var values: Array[float] = []
		for word: int in row.words:
			values.append(F32.read_word(word))
		var result: Dictionary
		var float_result: bool = false
		match row.operation:
			"sound_option":
				result = Audio.to_retail_sound_master_volume(values[0])
				float_result = true
			"music_option": result = Audio.to_retail_music_set_volume(values[0])
			"distance": result = Audio.retail_source_volume_for_distance(values[0])
			"nonloop_start": result = Audio.retail_refuses_non_looping_start(values[0])
			"pc_shape": result = Audio.retail_pc_shaped_millibels(row.integers[0])
			"fade": result = Audio.retail_fade_millibels(row.integers[0], values[0], values[1], values[2], values[3])
			"volume_db":
				result = Audio.retail_volume_db(row.integers[0], values[0], values[1], values[2], values[3])
				float_result = true
			"pitch_word":
				result = Audio.retail_pc_pitch_multiplier_word(row.words[0])
				# Native floats have already promoted signaling NaNs. Compare their
				# ordinary API wherever that promotion cannot discard raw payload.
				if (int(row.words[0]) & 0x7f800000) != 0x7f800000 or (int(row.words[0]) & 0x00400000) != 0 \
						or (int(row.words[0]) & 0x007fffff) == 0:
					_check("pitch_numeric", row.name, _result(Audio.retail_pc_pitch_multiplier(values[0]), true), row.expected)
			_: result = {"ok": false, "error_type": "UnknownOperation"}
		_check("laws", row.name, _result(result, float_result), row.expected)
	_check("fixture", "contact_extent", vectors.contacts.size(), 10)
	for index: int in range(vectors.contacts.size()):
		var row: Dictionary = vectors.contacts[index]
		_check("hostile_contact", str(index), _result(Audio.observe_hostile_environment_contact(row.current, row.previous)), row.expected)
	_check("fixture", "flight_extent", vectors.flight.size(), 146)
	for index: int in range(vectors.flight.size()):
		var row: Dictionary = vectors.flight[index]
		_check("flight_fade", str(index), _result(Audio.advance_retail_flight_loop_sub_volume(
			F32.read_word(row.words[0]), F32.read_word(row.words[1]), F32.read_word(row.words[2])), true), row.expected)


func _run_music(vectors: Dictionary) -> void:
	_check("fixture", "music_scenario_extent", vectors.music_scenarios.size(), 9)
	for scenario: Dictionary in vectors.music_scenarios:
		var policy := Music.new()
		_check("music_snapshot", scenario.name + ":initial", _snapshot(policy.snapshot()), scenario.initial)
		_check("fixture", scenario.name + ":nonempty", not scenario.steps.is_empty(), true)
		for index: int in range(scenario.steps.size()):
			var step: Dictionary = scenario.steps[index]
			var input: Dictionary = step.input
			var result: Dictionary
			match step.operation:
				"selection": result = policy.play_selection(input.selection, _units(input.track_units), input.fade)
				"list": result = policy.play_from_list(_units(input.requested_units), _units(input.random_units), input.fade)
				"volume": result = policy.set_configured_volume(F32.read_word(input.word))
				"fade": result = policy.advance_fade_step()
				"finished": result = policy.handle_track_finished()
				"kill": result = policy.kill()
				"reset": result = policy.reset()
				_: result = {"ok": false, "error_type": "UnknownOperation"}
			var name: String = scenario.name + ":" + str(index)
			_check("music_actions", name, _result(result), step.result)
			_check("music_snapshot", name, _snapshot(policy.snapshot()), step.snapshot)


func _run_queue(vectors: Dictionary) -> void:
	var queue := MessageQueue.new()
	_check("queue", "initial_count", queue.count(), 0)
	_check("fixture", "queue_extent", vectors.queue.size(), 116)
	for index: int in range(vectors.queue.size()):
		var step: Dictionary = vectors.queue[index]
		var result: Dictionary
		match step.operation:
			"enqueue": result = queue.enqueue(step.speaker, step.message)
			"dequeue": result = queue.try_dequeue()
			"clear": result = queue.clear()
			_: result = {"ok": false, "error_type": "UnknownOperation"}
		_check("queue", str(index), _result(result), step.result)
		_check("queue_count", str(index), queue.count(), step.count)


func _run_host_admission_and_detachment() -> void:
	var policy := Music.new()
	var units := PackedInt32Array([65, 0, 0xd800, 66])
	var started: Dictionary = policy.play_selection(0, units)
	var expected: Dictionary = policy.snapshot()
	units[0] = 90
	_check("detachment", "input_text", policy.snapshot(), expected)
	started.value[1].track_identity = PackedInt32Array([90])
	_check("detachment", "action_text", policy.snapshot(), expected)
	var copy: Dictionary = policy.snapshot()
	var copy_text: PackedInt32Array = copy.selection_track_identity
	copy_text[0] = 90
	copy.selection_track_identity = copy_text
	copy.current_volume = 0
	_check("detachment", "snapshot", policy.snapshot(), expected)
	var queue := MessageQueue.new()
	queue.enqueue(1, 292562)
	queue.enqueue(1, 292562)
	var first: Dictionary = queue.try_dequeue()
	first.value.audio.symbol = PackedInt32Array([0])
	_check("detachment", "queued_duplicate", queue.try_dequeue().value.audio, Audio.get_character_message(292562).value)
	var recipe: Dictionary = Audio.get_effect(0).value
	var original: Dictionary = recipe.duplicate(true)
	recipe.resource_path = "changed"
	_check("detachment", "recipe", Audio.get_effect(0).value, original)
	var specs: Array[Dictionary] = Audio.character_messages()
	specs[0].message_id = 0
	_check("detachment", "shared_specs", Audio.character_messages()[0].message_id, 292562)
	for invalid: Variant in [null, true, 1.0, "1", [], {}, -2147483649, 2147483648]:
		_check("host_admission", "effect", Audio.get_effect(invalid).get("error_type"), "ArgumentException")
		_check("host_admission", "character", Audio.get_character_message(invalid).get("error_type"), "ArgumentException")
		_check("host_admission", "track_index", Music.track_index(invalid).get("error_type"), "ArgumentException")
		_check("host_admission", "selection", policy.play_selection(invalid, "A").get("error_type"), "ArgumentException")
		_check("host_admission", "queue", queue.enqueue(invalid, 292562).get("error_type"), "ArgumentException")
	_check("host_admission", "music_failures_do_not_mutate", policy.snapshot(), expected)
	_check("host_admission", "queue_failures_do_not_mutate", queue.count(), 0)
	for invalid: Variant in [null, true, "1", [], {}]:
		_check("host_admission", "sound_option", Audio.to_retail_sound_master_volume(invalid).get("error_type"), "ArgumentException")
		_check("host_admission", "music_option", policy.set_configured_volume(invalid).get("error_type"), "ArgumentException")
	_check("host_admission", "option_failures_do_not_mutate", policy.snapshot(), expected)


func _result(result: Dictionary, float_result: bool = false) -> Dictionary:
	var output: Dictionary
	if result.get("ok") != true:
		output = {"ok": false, "error_type": result.get("error_type", "MissingFailure"), "parameter": result.get("parameter", "")}
	else:
		output = {"ok": true, "value": F32.store_word(result.value) if float_result else _plain(result.get("value"))}
	for key: String in ["crossed_target", "previous_contact_tick", "found"]:
		if result.has(key):
			output[key] = result[key]
	return output


func _snapshot(value: Dictionary) -> Dictionary:
	var result: Dictionary = value.duplicate(true)
	result.configured_volume_word = F32.store_word(result.configured_volume)
	result.erase("configured_volume")
	return _plain(result)


func _units(value: Variant) -> Variant:
	return null if value == null else PackedInt32Array(value)


func _plain(value: Variant) -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value:
			result[key] = _plain(value[key])
		return result
	if value is Array or typeof(value) in [TYPE_PACKED_INT32_ARRAY, TYPE_PACKED_INT64_ARRAY]:
		var result: Array = []
		for item: Variant in value:
			result.append(_plain(item))
		return result
	return value


func _integers(value: Variant) -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value:
			result[key] = _integers(value[key])
		return result
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_integers(item))
		return result
	return int(value) if typeof(value) == TYPE_FLOAT and value == floor(value) else value
