# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Args: owned reference.variant, fresh report.json, optional --write-reference
## for the .NET reference pass. Run --headless --audio-driver Dummy. The same
## standard-engine script also runs with --editor, admitting no playback there.
const Scene = preload("res://Scenes/Audio/Level100Audio.tscn")
const Audio = preload("res://Scenes/Audio/level100_audio.gd")
const Recipe = preload("res://Scenes/Audio/retail_audio_stream.gd")
const Catalog = preload("res://Client/audio_catalog.gd")
const F32 = preload("res://Core/retail_float24.gd")
const Text = preload("res://Core/canonical_json_string.gd")
var _failures: Array[String] = []
var _counts: Dictionary = {}
var _completed: Array[String] = []
var _report: String
var _pending: Array[WeakRef] = []
var _starts: int = 0
var _owners: Dictionary = {}
var _reference_adapter: RefCounted

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2 or args.size() > 3 or (args.size() == 3 and args[2] != "--write-reference"):
		quit(2)
		return
	var writing: bool = args.size() == 3
	if not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] \
			or FileAccess.file_exists(args[1]) or (writing and FileAccess.file_exists(args[0])):
		quit(2)
		return
	_report = args[1]
	if not _check("isolation", "dummy_driver", AudioServer.get_driver_name(), "Dummy"):
		_finish()
		return
	AudioServer.set_bus_mute(0, true)
	var audio: Audio = Scene.instantiate()
	root.add_child(audio)
	_scene_layout(audio)
	_completed.append("scene")
	if Engine.is_editor_hint():
		_check("editor", "refuses_configure", audio.configure(_observe).ok, false)
		_check("editor", "refuses_advance", audio.advance(1.0).ok, false)
		_check("editor", "refuses_music", audio.start_frontend_music().ok, false)
		_check("editor", "refuses_sample", audio.play_frontend_cue("Move").ok, false)
		_check("editor", "refuses_stream_decode", audio.frontend_music_recipe.load_stream().ok, false)
		_check("editor", "no_starts", _starts, 0)
		_check("editor", "no_processing", audio.is_processing(), false)
		_check("editor", "no_active_audio", AudioServer.get_bus_peak_volume_left_db(0, 0), -200.0)
		_completed.append("editor")
		audio.queue_free()
		await process_frame
		# Give the editor its own startup/scan lifecycle before shutdown.
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
		_finish()
		return
	var operations: Array = _operations()
	var before: Dictionary = _input_hashes()
	var reference: Dictionary = _reference(args[0], writing, operations)
	if reference.is_empty():
		audio.queue_free()
		await _drain()
		_finish()
		return
	_check("fixture", "schema", reference.get("schema"), 1)
	_check("fixture", "operations", reference.get("operations"), operations)
	_check("fixture", "snapshots", reference.snapshots.size(), operations.size() + 1)
	_check("runtime", "configure", audio.configure(_observe), {"ok": true})
	_check("runtime", "refuses_second_configure", audio.configure(_observe).ok, false)
	audio.set_process(false)
	for name: String in ["trainer", "transport", "repair"]:
		var attachment := Node3D.new()
		attachment.name = name
		audio.add_child(attachment)
		_owners[name] = attachment
	seed(42042)
	_compare_row(audio, {"ok": true}, reference.snapshots[0], "initial")
	for index: int in range(operations.size()):
		var result: Dictionary = _apply(audio, operations[index])
		_compare_row(audio, result, reference.snapshots[index + 1], str(index) + ":" + operations[index].op)
	_completed.append("runtime")
	_interleavings(audio)
	_completed.append("interleaving")
	for index: int in range(128):
		audio.call("_set_music_volume", index)
		_check("music_words", str(index), F32.store_word(audio.get_node("Music").volume_db), reference.music_volume_words[index])
	for index: int in range(reference.positions.size()):
		var row: Dictionary = reference.positions[index]
		var p: Dictionary = {"x": row.input[0], "y": row.input[1], "z": row.input[2]}
		_check("coordinates", str(index) + ":sim", _vector_words(Audio.sim_world(p)), row.sim)
		_check("coordinates", str(index) + ":retail", _vector_words(Audio.retail_world(p)), row.retail)
	_completed.append("numeric")
	_check("resources", "authored_flight_recipe_is_runtime_owner", audio.get("_recipes")["0:1:" + Catalog.get_aquila_transition(1).value.resource_path],
		audio.get_node("Attachments/Aquila/FlightLoop").stream_recipe)
	_publication_guard(audio)
	_completed.append("publication")
	_check("cleanup", "stop", audio.stop_level100_audio(), {"ok": true})
	var stopped: Dictionary = audio.inspection_snapshot()
	for name: String in ["queued_messages", "gameplay_shots", "terminal_shots", "frontend_shots"]:
		_check("cleanup", name, stopped[name], 0)
	_check("cleanup", "loops_empty", stopped.live_loops.size(), 0)
	_check("cleanup", "actor_released", stopped.aquila_actor_id, null)
	_check("cleanup", "observed_real_playback", _starts > 10, true)
	_owners.clear()
	audio.queue_free()
	await _drain()
	_completed.append("cleanup")
	_check("read_only", "all_used_inputs_unchanged", _input_hashes(), before)
	_completed.append("read_only")
	_finish()

func _operations() -> Array:
	var actors: Array = [{"actor_id": 7, "position_mm": {"x": 1000, "y": 2000, "z": 3000}}]
	var near: Array = [{"actor_id": 7, "position_mm": {"x": 0, "y": 0, "z": 0}}]
	var far: Array = [{"actor_id": 7, "position_mm": {"x": 50000, "y": 0, "z": 0}}]
	var message: int = Catalog.character_messages()[0].message_id
	var ops: Array = [{"op": "transition", "value": 0}, {"op": "bind", "id": 7, "actors": actors},
		{"op": "frontend", "value": "Move"}, {"op": "frontend", "value": "Select"},
		{"op": "terminal", "value": 0}, {"op": "terminal", "value": 3},
		{"op": "master", "value": 0.4}, {"op": "mix", "value": 0.25}, {"op": "pause", "value": true},
		{"op": "frontend", "value": "Back"}, {"op": "terminal", "value": 1}, {"op": "advance", "value": 0.2},
		{"op": "pause", "value": false}, {"op": "music_frontend"}, {"op": "music_frontend"},
		{"op": "music_option", "value": 0.2}, {"op": "advance", "value": 0.05}, {"op": "advance", "value": 0.05},
		{"op": "music_tutorial"}, {"op": "music_finished"}, {"op": "advance", "value": -1.0},
		{"op": "queue", "speaker": 3, "message": message}, {"op": "queue", "speaker": -2147483648, "message": message},
		{"op": "queue", "speaker": 3, "message": -1}, {"op": "advance", "value": 0.1},
		{"op": "pause", "value": true}, {"op": "advance", "value": 2.0}, {"op": "pause", "value": false},
		{"op": "advance", "value": 0.1}, {"op": "voice_finished"}, {"op": "advance", "value": 0.3},
		{"op": "advance", "value": 0.19}, {"op": "advance", "value": 0.02}, {"op": "voice_stop"},
		{"op": "stop_all"}, {"op": "pose", "actors": near}, {"op": "transition", "value": 0}]
	for index: int in range(51):
		ops.append({"op": "advance", "value": 0.05})
	ops.append_array([{"op": "transition", "value": 1}, {"op": "pitch", "value": 1.0},
		{"op": "pitch", "value": -0.1}, {"op": "transition", "value": 2}, {"op": "advance", "value": 0.15},
		{"op": "transition", "value": 1}, {"op": "warning", "value": 1}, {"op": "warning", "value": 0},
		{"op": "advance", "value": 0.5}, {"op": "warning", "value": 1}, {"op": "advance", "value": 3.0},
		{"op": "warning", "value": 1}, {"op": "warning", "value": 2}, {"op": "warning", "value": 99},
		{"op": "warning", "value": 0}, {"op": "effect", "value": 15}, {"op": "pose", "actors": far},
		{"op": "effect", "value": 0}, {"op": "transition", "value": 0}, {"op": "pose", "actors": near},
		{"op": "advance", "value": 0.05}, {"op": "loop", "name": "trainer", "active": true},
		{"op": "loop", "name": "trainer", "active": true}, {"op": "loop", "name": "transport", "active": true},
		{"op": "loop", "name": "repair", "active": true}, {"op": "repair", "full": false}, {"op": "repair", "full": true},
		{"op": "owner_pose", "name": "trainer", "value": Vector3(25, 0, 0)}, {"op": "advance", "value": 0.0},
		{"op": "master", "value": 0.8}, {"op": "mix", "value": 1.0}, {"op": "pause", "value": true},
		{"op": "pause", "value": false}, {"op": "loop", "name": "trainer", "active": false},
		{"op": "weapons", "events": [{"weapon": 2, "round_count": 4}, {"weapon": 1}, {"weapon": 3}]},
		{"op": "weapons", "events": [{"weapon": 2}, {"weapon": 99}]},
		{"op": "destruction", "events": [{"effect_kind": 5, "position": {"x": 0, "y": 0, "z": 0}},
			{"effect_kind": 1, "position": {"x": 1000, "y": 2000, "z": 3000}}, {"effect_kind": 3, "position": {"x": 50000, "y": 0, "z": 0}}]},
		{"op": "flight", "tick": 1000, "mission": 0, "events": [{"kind": 64, "tick": 1100, "mode": 0}]},
		{"op": "flight", "tick": 1201, "mission": 201, "events": [{"kind": 64, "tick": 1201, "mode": 0}]},
		{"op": "flight", "tick": 1300, "mission": 300, "events": [{"kind": 64, "tick": 1200, "mode": 0}]},
		{"op": "flight", "tick": 1300, "mission": -1, "events": []},
		{"op": "frame", "facts": {"actors": near, "warning_state": 1, "messages": [{"speaker_id": 2, "message_id": message}],
			"flight_events": [{"kind": 2048, "tick": 1301, "mode": 0}, {"kind": 4096, "tick": 1301, "mode": 0}],
			"simulation_tick": 1301, "mission_tick": 301, "weapon_events": [{"weapon": 1}], "thruster_fraction": 0.5,
			"destruction_events": [{"effect_kind": 0, "position": {"x": 0, "y": 0, "z": 0}}], "gameplay_mix": 0.5, "gameplay_paused": true}},
		{"op": "stop_gameplay"}, {"op": "bind", "id": 8, "actors": [{"actor_id": 8, "position_mm": {"x": 1, "y": 2, "z": 3}}]},
		{"op": "exit", "select": true}, {"op": "stop_level"}])
	return ops

func _apply(audio: Audio, op: Dictionary) -> Dictionary:
	match op.op:
		"bind": return audio.bind_aquila(op.id, op.actors)
		"pose": return audio.update_aquila_pose(op.actors)
		"transition": return audio.play_aquila_transition(op.value)
		"effect": return audio.play_on_aquila(op.value)
		"warning": return audio.set_aquila_warning_state(op.value)
		"terminal": return audio.play_terminal_cue(op.value)
		"frontend": return audio.play_frontend_cue(op.value)
		"master": return audio.set_master_sound_option(op.value)
		"music_option": return audio.set_music_option(op.value)
		"mix": return audio.set_gameplay_mix(op.value)
		"pitch": return audio.set_aquila_flight_pitch(op.value)
		"pause": return audio.set_gameplay_paused(op.value)
		"advance": return audio.advance(op.value)
		"music_frontend": return audio.start_frontend_music()
		"music_tutorial": return audio.start_tutorial_music()
		"music_stop": return audio.stop_music()
		"music_finished": audio.get_node("Music").stop(); audio.get_node("Music").finished.emit()
		"queue": return audio.queue_character_message(op.speaker, op.message)
		"voice_finished": audio.get_node("CharacterVoice").stop(); audio.get_node("CharacterVoice").finished.emit()
		"voice_stop": return audio.stop_character_messages()
		"flight": return audio.consume_aquila_flight_events(op.events, op.tick, op.mission)
		"weapons": return audio.consume_weapon_fire_events(op.events)
		"destruction": return audio.consume_destruction_events(op.events)
		"loop":
			match op.name:
				"trainer": return audio.set_trainer_flying(_owners[op.name], op.active)
				"transport": return audio.set_transport_flying(_owners[op.name], op.active)
				"repair": return audio.set_repair_pad_idle(_owners[op.name], op.active)
		"repair": return audio.play_repair_full(_owners.repair) if op.full else audio.play_repair_charging(_owners.repair)
		"owner_pose": _owners[op.name].position = op.value
		"stop_gameplay": return audio.stop_gameplay_samples()
		"stop_all": return audio.stop_all_samples()
		"stop_level": return audio.stop_level100_audio()
		"exit": return audio.stop_for_level_exit(op.select)
		"frame": return audio.consume_frame(op.facts)
	return {"ok": true}

func _compare_row(audio: Audio, result: Dictionary, expected: Dictionary, label: String) -> void:
	var status: Dictionary = {"ok": result.ok}
	if not result.ok:
		status.error_type = result.error_type
	_check("results", label, status, expected.result)
	var actual: Dictionary = _snapshot(audio)
	for key: String in expected.state:
		_check("state", label + ":" + key, actual.get(key), expected.state[key])
	_check("rng", label, randi(), expected.next_random)

func _snapshot(audio: Audio) -> Dictionary:
	var s: Dictionary = audio.inspection_snapshot()
	var music: Dictionary = s.music.duplicate(true)
	music.configured_volume = F32.store_word(music.configured_volume)
	for key: String in ["current_track_identity", "queued_track_identity", "selection_track_identity"]:
		music[key] = null if music[key] == null else Text.native_string(music[key]).value
	var loops: Dictionary = {}
	for key: String in audio.get("_live_loops"):
		loops[key] = _player(audio.get("_live_loops")[key])
	var actor: Node3D = audio.get("_aquila")
	return {"sound_master": F32.store_word(s.sound_master), "gameplay_mix": F32.store_word(s.gameplay_mix), "paused": s.paused,
		"warning_state": s.warning_state, "warning_loop_state": s.warning_loop_state, "mission_start": s.mission_start_tick,
		"last_contact": s.last_hostile_contact, "actor": s.aquila_actor_id, "actor_position": null if actor == null else _vector_words(actor.position),
		"music_accumulator": s.music_accumulator, "voice_lead": s.voice_lead, "handoff": s.handoff,
		"queue_count": s.queued_messages, "speaker": s.playback.active_speaker_id, "message": s.playback.active_message_id,
		"voice_length": s.playback.length_seconds, "voice": _player(audio.get_node("CharacterVoice")),
		"music_player": _player(audio.get_node("Music")), "music": music, "flight_fade": _fade(s.fades.flight),
		"warning_fade": _fade(s.fades.warning), "loops": loops, "spatial": _players(audio.get("_gameplay_shots")),
		"terminal": _players(audio.get("_terminal_shots")), "frontend": _players(audio.get("_frontend_shots"))}

func _interleavings(audio: Audio) -> void:
	var actors: Array = [{"actor_id": 7, "position_mm": {"x": 0, "y": 0, "z": 0}}]
	var facts: Dictionary = {"actors": actors, "warning_state": 1,
		"messages": [{"speaker_id": 3, "message_id": Catalog.character_messages()[0].message_id}],
		"flight_events": [], "simulation_tick": 1, "mission_tick": 1, "weapon_events": [{"weapon": 1}],
		"thruster_fraction": 0.5, "destruction_events": [{"effect_kind": 1, "position": {"x": 0, "y": 0, "z": 0}}],
		"gameplay_mix": 1.0, "gameplay_paused": false}
	_check("interleaving", "bind", audio.bind_aquila(7, actors).ok, true)
	var phases: Array = []
	var callback: Callable = func(phase: int) -> Dictionary:
		var state: Dictionary = audio.inspection_snapshot()
		phases.append([phase, state.warning_state, state.queued_messages, state.gameplay_shots])
		return {"ok": true}
	_check("interleaving", "frame", audio.consume_frame(facts, callback).ok, true)
	_check("interleaving", "exact_host_boundaries", phases, [[0, 1, 0, 0], [1, 1, 1, 1], [2, 1, 1, 1]])
	_check("interleaving", "destruction_after_host", audio.inspection_snapshot().gameplay_shots, 2)
	audio.stop_gameplay_samples()
	phases.clear()
	var failing: Callable = func(phase: int) -> Dictionary:
		phases.append(phase)
		return {"ok": false, "error_type": "OwnedTestFailure", "error": "deliberate host failure"} if phase == 1 else {"ok": true}
	_check("interleaving", "host_failure", audio.consume_frame(facts, failing).get("error_type"), "OwnedTestFailure")
	_check("interleaving", "abort_order", phases, [0, 1])
	_check("interleaving", "earlier_effect_survives", audio.inspection_snapshot().gameplay_shots, 1)
	var detached: Dictionary = audio.inspection_snapshot()
	detached.fades.flight.sub = 0.9
	detached.music.current_volume = -1
	_check("snapshot", "fade_detached", audio.inspection_snapshot().fades.flight.sub, 0.0)
	_check("snapshot", "music_detached", audio.inspection_snapshot().music.current_volume >= 0, true)
	audio.stop_level100_audio()


func _fade(value: Dictionary) -> Dictionary:
	return {"sub": F32.store_word(value.sub), "target": F32.store_word(value.target), "step": F32.store_word(value.step), "accumulator": value.accumulator}

func _player(player: Node) -> Dictionary:
	var value: Dictionary = {"volume": F32.store_word(player.volume_db), "pitch": F32.store_word(player.pitch_scale),
		"paused": player.stream_paused, "stream": player.stream != null}
	if player is AudioStreamPlayer3D:
		value.position = _vector_words(player.position)
		value.global_position = _vector_words(player.global_position)
	return value

func _players(players: Array) -> Array:
	var values: Array = []
	for player: Node in players:
		values.append(_player(player))
	return values

func _scene_layout(audio: Audio) -> void:
	_check("scene", "unconfigured", audio.inspection_snapshot().initialized, false)
	_check("scene", "not_processing", audio.is_processing(), false)
	for path: String in ["Music", "CharacterVoice", "Attachments/Aquila/FlightLoop", "Attachments/Aquila/WarningLoop",
			"Attachments/AirTrainer/Loop", "Attachments/Transport/Loop", "Attachments/RepairPad/Loop"]:
		var player: Node = audio.get_node(path)
		_check("scene", path + ":native_player", player is AudioStreamPlayer or player is AudioStreamPlayer3D, true)
		_check("scene", path + ":recipe", player.stream_recipe is Recipe, true)
		_check("scene", path + ":no_autoplay", player.autoplay, false)
		_check("scene", path + ":no_playback", player.playing, false)
		_check("scene", path + ":no_decode", player.stream, null)
		_check("scene", path + ":no_cached_payload", player.stream_recipe.get("_decoded"), null)
		if player is AudioStreamPlayer3D:
			_check("scene", path + ":retail_attenuation", player.attenuation_model, AudioStreamPlayer3D.ATTENUATION_DISABLED)
			_check("scene", path + ":no_engine_cutoff", player.max_distance, 0.0)
	for path: String in ["Aquila", "AirTrainer", "Transport", "RepairPad"]:
		_check("scene", path + ":attachment", audio.get_node("Attachments/" + path) is Marker3D, true)

func _publication_guard(audio: Audio) -> void:
	# Bind a real decoded production resource to an authored node at the save
	# boundary, including after previous playback and queue cleanup.
	var loaded: Dictionary = audio.frontend_music_recipe.load_stream()
	_check("publication", "production_stream_decoded", loaded.ok, true)
	if not loaded.ok:
		return
	audio.get_node("Music").stream = loaded.value
	var packed := PackedScene.new()
	_check("publication", "pack", packed.pack(audio), OK)
	var state: SceneState = packed.get_state()
	for node_index: int in range(state.get_node_count()):
		for property_index: int in range(state.get_node_property_count(node_index)):
			_check("publication", str(node_index) + ":" + str(property_index), state.get_node_property_name(node_index, property_index) != &"stream", true)
	for recipe: Recipe in audio.get("_recipes").values():
		for property: Dictionary in recipe.get_property_list():
			if property.name == "_decoded":
				_check("publication", "decoded_not_stored", int(property.usage) & PROPERTY_USAGE_STORAGE, 0)
	audio.get_node("Music").stream = null

func _observe(player: Node) -> void:
	if player.has_stream_playback():
		_pending.append(weakref(player.get_stream_playback()))
		_starts += 1

func _drain() -> void:
	for iteration: int in range(100):
		await create_timer(0.01).timeout
		_pending = _pending.filter(func(item: WeakRef) -> bool: return item.get_ref() != null)
		if _pending.is_empty() and (_reference_adapter == null or _reference_adapter.call("PendingPlaybackCount") == 0):
			break
	_check("cleanup", "native_handles_retired", _pending.size(), 0)
	if _reference_adapter != null:
		_check("cleanup", "reference_handles_retired", _reference_adapter.call("PendingPlaybackCount"), 0)
		_reference_adapter.call("ReleaseObserver")
		_reference_adapter = null

func _input_hashes() -> Dictionary:
	var paths: Array[String] = [Catalog.frontend_music().resource_path, Catalog.tutorial_music().resource_path,
		Text.native_string(Catalog.character_messages()[0].resource_path).value]
	for index: int in range(Catalog.EFFECTS.size()):
		paths.append(Catalog.get_effect(index).value.resource_path)
	for index: int in range(Catalog.TERMINALS.size()):
		paths.append(Catalog.get_terminal(index).value.resource_path)
	for index: int in range(3):
		paths.append(Catalog.get_aquila_transition(index).value.resource_path)
		paths.append(Catalog.get_actor_loop(index).value.resource_path)
	for index: int in [1, 2]:
		paths.append(Catalog.get_aquila_warning(index).value.resource_path)
	for name: String in Catalog.FRONTEND:
		paths.append(Catalog.get_frontend(name).value.resource_path)
	var hashes: Dictionary = {}
	for path: String in paths:
		hashes[path] = FileAccess.get_sha256(path)
		_check("read_only", "present:" + path, String(hashes[path]).length(), 64)
	return hashes

func _reference(path: String, writing: bool, operations: Array) -> Dictionary:
	if writing:
		if not _check("fixture", "dotnet", ClassDB.class_exists("CSharpScript"), true):
			return {}
		var script: Script = load("res://Scenes/Audio/Tests/AudioRuntimeReference.cs")
		_reference_adapter = script.new()
		var result: Dictionary = _reference_adapter.call("CreateReference", root, operations)
		if not _check("fixture", "created", result.get("ok"), true):
			return {}
		var output := FileAccess.open(path, FileAccess.WRITE)
		if output == null:
			_failures.append("fixture:output")
			return {}
		output.store_var(result.value, false)
		output.close()
		return result.value
	var input := FileAccess.open(path, FileAccess.READ)
	if input == null:
		_failures.append("fixture:missing")
		return {}
	var value: Variant = input.get_var(false)
	input.close()
	return value if value is Dictionary else {}

func _owned_path(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") \
			or not path.begins_with(owned + "/") or path.get_file().is_empty():
		return false
	var owner_parent := DirAccess.open(owned.get_base_dir())
	if owner_parent == null or owner_parent.is_link(owned.get_file()):
		return false
	var directory := DirAccess.open(owned)
	if directory == null:
		return false
	var segments: PackedStringArray = path.trim_prefix(owned + "/").split("/", false)
	for index: int in range(segments.size()):
		if directory.is_link(segments[index]):
			return false
		if index + 1 < segments.size() and directory.change_dir(segments[index]) != OK:
			return false
	return true

func _vector_words(value: Vector3) -> PackedInt64Array:
	return PackedInt64Array([F32.store_word(value.x), F32.store_word(value.y), F32.store_word(value.z)])

func _check(category: String, label: String, actual: Variant, expected: Variant) -> bool:
	_counts[category] = int(_counts.get(category, 0)) + 1
	if actual != expected:
		_failures.append(category + ":" + label)
		return false
	return true

func _finish() -> void:
	var required: Array = ["scene", "editor"] if Engine.is_editor_hint() else ["scene", "runtime", "interleaving", "numeric", "publication", "cleanup", "read_only"]
	var report: Dictionary = {"schema": 1, "counts": _counts, "failure_count": _failures.size(), "failures": _failures, "completed": _completed}
	var output := FileAccess.open(_report, FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("AUDIO_SCENE_CHECKS: " + JSON.stringify(report))
	quit(0 if _failures.is_empty() and _completed == required else 1)
