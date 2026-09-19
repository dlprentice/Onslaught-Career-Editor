# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production scene checks. Runtime receives a batch from the unchanged
## C# verifier; --startup-verified-fixture=ABS may write it ONCE under this
## checkout's local-data for a repeat with the standard engine. The fixture is
## an object-free Variant dictionary, never an alternate runtime JSON loader.
## Use --audio-driver Dummy; this process also mutes its own Master bus.

const Playback = preload("res://Scenes/Frontend/startup_sequence.gd")
const Schedule = preload("res://Client/startup_schedule.gd")
var failures: Array[String] = []
var checks: int = 0
var _scene: PackedScene
var _batch: Dictionary
var _sections: Dictionary = {}
var _capture_directory: String = ""
var _requested_captures: Array[String] = []
var _completed_captures: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(condition: bool, message: String) -> bool:
	checks += 1
	if not condition:
		failures.append(message)
	return condition


func run_checks() -> void:
	if not read_capture_options():
		finish_checks()
		return
	_scene = load("res://Scenes/Frontend/Startup.tscn")
	if not check(_scene != null, "Production Startup.tscn did not load"):
		finish_checks()
		return
	var view: Control = _scene.instantiate()
	var pointer_before: int = Input.mouse_mode
	check_authored(view)
	if Engine.is_editor_hint():
		await check_editor(view)
	else:
		_batch = load_verified_batch()
		if _batch.is_empty():
			view.free()
			finish_checks()
			return
		AudioServer.set_bus_mute(AudioServer.get_bus_index("Master"), true)
		check_skip_law()
		check_fixed_runtime(view)
		check_routes_and_admission()
		await check_wall_audio()
		if ClassDB.class_exists("CSharpScript"):
			await check_host_bridge()
		if not _capture_directory.is_empty():
			await capture_production_samples()
	check(Input.mouse_mode == pointer_before, "Startup changed pointer ownership")
	view.queue_free()
	await process_frame
	if Engine.is_editor_hint():
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	else:
		# AudioServer releases stopped streams/playbacks on a later mixer and
		# main-thread turn. These tests never own playback handles; allow the
		# actual backend cleanup to drain after all scene nodes are freed.
		await create_timer(0.25).timeout
		await process_frame
		_sections["retirement"] = true
	finish_checks()


func finish_checks() -> void:
	var required: Array[String] = ["authored", "editor", "layout"]
	if not Engine.is_editor_hint():
		required.assign(["authored", "batch", "skip", "fixed", "layout", "routes", "audio", "retirement"])
	if not _capture_directory.is_empty():
		required.append("captures")
	if not Engine.is_editor_hint() and ClassDB.class_exists("CSharpScript"):
		required.append("host_bridge")
	for section: String in required:
		check(bool(_sections.get(section, false)), "Check group did not finish: " + section)
	check(_requested_captures == _completed_captures, "A requested rendered capture did not complete")
	for message: String in failures:
		push_error(message)
	print("STARTUP_SCENE_CHECKS: ", checks, " checks; failures=", failures.size(),
		"; editor=", Engine.is_editor_hint(),
		"; actual authored scene, verified provider, two buffers, exact skip set, lifecycle and transient pixels")
	quit(0 if failures.is_empty() else 1)


func check_authored(view: Control) -> void:
	var video: TextureRect = view.get_node("Stage/Video")
	var splash: TextureRect = view.get_node("Stage/SplashFade/Splash")
	var voice: AudioStreamPlayer = view.get_node("RetailFmvVoice")
	check(view.get_script().resource_path.ends_with("/startup_sequence.gd"), "Production root is not GDScript")
	check(view.get_node("Black") is ColorRect, "Startup has no native black background")
	check(video.position == Vector2(0, 40) and video.size == Vector2(640, 400), "Measured FMV quad changed")
	check(video.self_modulate == Color8(254, 254, 254, 255), "Measured FMV diffuse changed")
	check(splash.position == Vector2.ZERO and splash.size == Vector2(640, 480), "Measured splash stage changed")
	check(not voice.autoplay and voice.stream == null and voice.process_mode == Node.PROCESS_MODE_ALWAYS,
		"Authored voice must start unbound and inactive")
	check(voice.bus == &"Master" and voice.volume_db == 0.0, "Authored voice routing/gain changed")
	_sections["authored"] = true


func check_editor(view: Control) -> void:
	var completions: Array[bool] = []
	view.connect("completed", func() -> void: completions.append(true))
	root.add_child(view)
	await process_frame
	var video: TextureRect = view.get_node("Stage/Video")
	var splash: TextureRect = view.get_node("Stage/SplashFade/Splash")
	var voice: AudioStreamPlayer = view.get_node("RetailFmvVoice")
	check(splash.texture != null and splash.get_parent().visible, "Editor did not bind the actual splash image")
	if splash.texture != null:
		check(splash.texture.get_size() == Vector2(512, 512), "Unexpected canonical splash dimensions")
	for cue: int in [0, 1, 3]:
		view.set("editor_cue", cue)
		check(video.texture != null and video.visible, "Editor cue did not bind an actual video frame")
		if video.texture != null:
			check(video.texture.get_size() == Vector2(480, 300), "Canonical video frame dimensions changed")
		var rid: RID = video.texture.get_rid() if video.texture != null else RID()
		view.call("_process", 1000.0)
		view.call("abort_for_harness")
		var skip := InputEventKey.new()
		skip.keycode = KEY_SPACE
		skip.pressed = true
		view.call("_input", skip)
		await process_frame
		check(video.texture != null and video.texture.get_rid() == rid, "Editor advanced its frozen preview")
		check(not view.is_processing() and not view.is_processing_input(), "Editor processed startup input or time")
	check(not voice.playing and voice.stream == null, "Editor started or loaded audio")
	check(completions.is_empty() and not view.call("is_initialized"), "Editor initialized or completed playback")
	check(not view.call("configure_verified_media", empty_batch(), 0, 2, 0, Callable()).ok,
		"Editor admitted runtime configuration")
	check_layout_and_serialization(view)
	_sections["editor"] = true


func check_fixed_runtime(view: Control) -> void:
	var data: Dictionary = _batch.duplicate(true)
	var configured: Dictionary = view.call("configure_verified_media", data, 0, 2, 0, Callable())
	if not check(configured.ok, "Verified canonical cold-start batch was rejected"):
		return
	check(view.call("get_scheduled_seconds") == 229.0 / 25.0 + 2054.0 / 25.0 + 4.5,
		"Cold-start duration changed")
	# Caller mutation cannot rewrite the live schedule or its paths.
	data.clips.clear()
	data.frame_paths.clear()
	var completion_states: Array[Dictionary] = []
	view.connect("completed", func() -> void: completion_states.append(completion_state(view)))
	root.add_child(view)
	check(view.is_processing() and view.is_processing_input(), "Configured runtime did not acquire frame/input ownership")
	view.set_process(false) # Deterministic test drives the actual callback directly.
	var video: TextureRect = view.get_node("Stage/Video")
	var voice: AudioStreamPlayer = view.get_node("RetailFmvVoice")
	check(video.texture != null and video.visible, "Ready did not present frame zero on the actual control")
	check(not voice.playing and voice.stream == null, "Fixed-tick Ready bound audio")
	var buffers: Dictionary[int, RID] = {}
	var elapsed: float = 0.0
	for tick: int in range(24):
		view.call("_process", 99.0 if tick % 2 == 0 else -20.0)
		elapsed += 1.0 / 60.0
		var index: int = int(floor(elapsed * 25.0))
		check(view.get("_resident_cue") == 0 and view.get("_resident_index") == index,
			"Fixed-tick frame selection used engine delta")
		check(view.get("_presented_buffer") == index % 2, "Frame buffer parity changed")
		if video.texture != null:
			var rid: RID = video.texture.get_rid()
			if buffers.has(index % 2):
				check(buffers[index % 2] == rid, "A frame allocated a new texture instead of reusing its buffer")
			buffers[index % 2] = rid
	check(buffers.size() == 2 and buffers[0] != buffers[1], "Video did not use exactly two distinct buffers")
	check(not voice.playing and voice.stream == null, "Fixed-tick frame updates started audio")
	check_layout_and_serialization(view)
	var rejected := InputEventKey.new()
	rejected.keycode = KEY_A
	rejected.physical_keycode = KEY_SPACE
	rejected.pressed = true
	view.call("_input", rejected)
	view.call("_process", 0.0)
	check(view.visible and completion_states.is_empty(), "Physical or unrelated key skipped startup")
	var accepted := InputEventKey.new()
	accepted.keycode = KEY_SPACE
	accepted.pressed = true
	view.call("_input", accepted)
	check(completion_states.is_empty(), "Input completed synchronously instead of on the next process")
	view.call("_process", 0.0)
	check(completion_states.size() == 1, "Accepted input did not skip the entire chain")
	if not completion_states.is_empty():
		check(completion_states[0] == retired_state(), "Completion fired before frame/audio/input retirement")
	view.call("_process", 1000.0)
	view.call("abort_for_harness")
	view.call("_process", 1000.0)
	check(completion_states.size() == 1, "Completed emitted more than once")
	_sections["fixed"] = true


func check_layout_and_serialization(view: Control) -> void:
	var video: TextureRect = view.get_node("Stage/Video")
	video.position += Vector2(16, 4)
	video.size += Vector2(20, 10)
	if not Engine.is_editor_hint():
		view.call("_process", 0.0)
	check(video.position == Vector2(16, 44) and video.size == Vector2(660, 410),
		"Frame updates overwrote authored video geometry")
	# This Inspector-size edit deliberately detaches the test instance from
	# viewport stretch first. Gameplay retains the production Full Rect setup;
	# its native stage transform is still the method being exercised below.
	view.set_anchors_preset(Control.PRESET_TOP_LEFT, true)
	view.size = Vector2(1280, 720)
	var stage: Control = view.get_node("Stage")
	check(stage.scale == Vector2(1.5, 1.5) and stage.position == Vector2(160, 0), "Startup widescreen fit changed")
	var packed := PackedScene.new()
	if not check(packed.pack(view) == OK, "Startup production scene cannot be packed"):
		return
	var state: SceneState = packed.get_state()
	for node: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(node)):
			var value: Variant = state.get_node_property_value(node, property)
			check(not value is ImageTexture and not value is AudioStreamWAV,
				"Packing startup retained private decoded media")
	var copy: Control = packed.instantiate()
	check(copy.get_node("Stage/Video").position == video.position, "Scene roundtrip discarded authored position")
	check(copy.get_node("Stage/Video").size == video.size, "Scene roundtrip discarded authored size")
	check(copy.get_node("Stage/Video").texture == null, "Scene roundtrip retained transient image")
	copy.free()
	_sections["layout"] = true


func check_skip_law() -> void:
	for key: int in [KEY_SPACE, KEY_ENTER, KEY_ESCAPE, KEY_KP_ENTER, KEY_A, KEY_TAB, KEY_UP]:
		for pressed: bool in [false, true]:
			for echo: bool in [false, true]:
				var event := InputEventKey.new()
				event.keycode = key
				event.physical_keycode = KEY_SPACE
				event.pressed = pressed
				event.echo = echo
				var expected: bool = pressed and not echo and key in [KEY_SPACE, KEY_ENTER, KEY_ESCAPE, KEY_KP_ENTER]
				check(Playback.accepts_skip_event(event) == expected, "Startup key skip law changed")
	for button: int in range(1, 10):
		for pressed: bool in [false, true]:
			var event := InputEventMouseButton.new()
			event.button_index = button
			event.pressed = pressed
			check(Playback.accepts_skip_event(event) == (pressed and button in [1, 2, 3]), "Startup mouse skip law changed")
	var pad := InputEventJoypadButton.new()
	pad.pressed = true
	check(not Playback.accepts_skip_event(pad), "Joypad button incorrectly skips startup")
	check(not Playback.accepts_skip_event(InputEventMouseMotion.new()), "Pointer motion incorrectly skips startup")
	_sections["skip"] = true


func check_routes_and_admission() -> void:
	for row: Dictionary in [{"route": 1, "cue": 2, "seconds": 229.0 / 25.0 + 2054.0 / 25.0},
			{"route": 2, "cue": 3, "seconds": 3095.0 / 25.0}]:
		var view: Control = _scene.instantiate()
		check(view.call("configure_verified_media", _batch, row.route, row.cue, 0, Callable()).ok, "Attract/single route rejected")
		check(view.call("get_scheduled_seconds") == row.seconds, "Attract/single route duration changed")
		check(not view.call("configure_verified_media", {}, 0, 2, 0, Callable()).ok, "Repeated configuration was admitted")
		check(view.call("get_scheduled_seconds") == row.seconds, "Rejected configuration mutated schedule")
		view.free()
	var invalid: Control = _scene.instantiate()
	check(not invalid.call("configure_verified_media", {}, 0, 2, 0, Callable()).ok, "Unverified-shaped batch was admitted")
	check(not invalid.call("is_initialized"), "Rejected batch initialized the scene")
	check(not invalid.call("configure_verified_media", _batch, 0, 2, 1, Callable()).ok, "Wall audio admitted no retirement observer")
	check(not invalid.call("is_initialized"), "Missing retirement observer partially initialized scene")
	invalid.free()
	var empty: Control = _scene.instantiate()
	check(empty.call("configure_verified_media", empty_batch(), 0, 2, 0, Callable()).ok, "Empty verified batch rejected")
	var missing: Array = empty.call("get_missing_cues")
	check(missing == [0, 1, 2], "Missing cold-start cue order changed")
	missing.clear()
	check(empty.call("get_missing_cues") == [0, 1, 2], "Missing-cue snapshot aliases schedule state")
	var completed: Array[Dictionary] = []
	empty.connect("completed", func() -> void: completed.append(completion_state(empty)))
	root.add_child(empty)
	check(completed.size() == 1 and completed[0] == retired_state(), "Empty schedule did not retire during Ready")
	empty.queue_free()
	_sections["routes"] = true


func check_wall_audio() -> void:
	var view: Control = _scene.instantiate()
	var starts: Array[Dictionary] = []
	var stopped: Array[Dictionary] = []
	var observer: Callable = func(player: AudioStreamPlayer) -> void:
		starts.append({"cue_before_present": view.get("_resident_cue"), "frame_before_present": view.get("_resident_index"),
			"has_stream": player.stream != null, "elapsed": view.get("_elapsed_seconds"), "voice_id": player.get_instance_id()})
	if not check(view.call("configure_verified_media", _batch, 0, 2, 1, observer).ok, "Wall-time batch rejected"):
		view.free()
		return
	view.connect("completed", func() -> void: stopped.append(completion_state(view)))
	root.add_child(view)
	view.set_process(false)
	var voice: AudioStreamPlayer = view.get_node("RetailFmvVoice")
	check(starts.is_empty() and voice.stream == null, "Ready started audio before the first process")
	view.call("_process", 0.1304)
	check(starts.size() == 1 and voice.stream != null, "First video process did not start verified voice once")
	if not starts.is_empty():
		check(starts[0].frame_before_present == 0 and starts[0].cue_before_present == 0,
			"Voice started after the corresponding frame was presented")
		check(starts[0].has_stream and starts[0].elapsed == 0.1304, "Voice observer did not run at the beat-local start")
	if voice.stream is AudioStreamWAV:
		var stream: AudioStreamWAV = voice.stream
		check(stream.format == AudioStreamWAV.FORMAT_16_BITS and stream.mix_rate == 44100 and stream.stereo,
			"Verified canonical WAV was transformed")
		check(stream.loop_mode == AudioStreamWAV.LOOP_DISABLED, "Startup voice unexpectedly loops")
	view.call("_process", -30.0)
	check(view.get("_elapsed_seconds") == 0.1304 and starts.size() == 1, "Negative delta advanced or restarted audio")
	view.call("_process", 0.02)
	check(starts.size() == 1, "A video frame restarted its existing voice")
	var to_montage: float = 229.0 / 25.0 - float(view.get("_elapsed_seconds"))
	view.call("_process", to_montage)
	check(view.get("_resident_cue") == 1 and view.get("_resident_index") == 0, "Exact clip boundary did not present montage frame zero")
	check(starts.size() == 2, "Clip transition did not observe its new voice exactly once")
	var to_splash: float = 229.0 / 25.0 + 2054.0 / 25.0 - float(view.get("_elapsed_seconds"))
	view.call("_process", to_splash)
	var fade: Control = view.get_node("Stage/SplashFade")
	check(fade.visible and fade.modulate.a == 0.0 and not view.get_node("Stage/Video").visible,
		"Exact splash boundary did not begin the actual fade at zero")
	check(voice.stream == null and not voice.playing, "Video audio survived into the splash")
	view.call("_process", 0.75)
	check(fade.modulate.a == 0.5, "Splash half-fade alpha changed")
	view.call("_process", 0.75)
	check(fade.modulate.a == 1.0, "Splash hold boundary alpha changed")
	view.call("_process", 3.0)
	check(stopped.size() == 1 and stopped[0] == retired_state(), "Natural completion did not retire before notifying")
	view.queue_free()
	await process_frame
	# A separate active single-cutscene exercises ExitTree before completion.
	var cutscene: Control = _scene.instantiate()
	var exit_starts: Array[bool] = []
	var exit_completed: Array[bool] = []
	var exit_observer: Callable = func(_player: AudioStreamPlayer) -> void: exit_starts.append(true)
	check(cutscene.call("configure_verified_media", _batch, 2, 3, 1, exit_observer).ok, "Single voice configuration rejected")
	cutscene.connect("completed", func() -> void: exit_completed.append(true))
	root.add_child(cutscene)
	cutscene.set_process(false)
	cutscene.call("_process", 0.1)
	var exit_voice: AudioStreamPlayer = cutscene.get_node("RetailFmvVoice")
	check(exit_starts.size() == 1 and exit_voice.stream != null, "Single clip did not start its own voice")
	root.remove_child(cutscene)
	check(exit_voice.stream == null and not exit_voice.playing, "ExitTree retained cutscene voice")
	check(exit_completed.is_empty(), "Early teardown invented successful completion")
	cutscene.free()
	_sections["audio"] = true


func completion_state(view: Control) -> Dictionary:
	var voice: AudioStreamPlayer = view.get_node("RetailFmvVoice")
	return {"visible": view.visible, "processing": view.is_processing(), "input": view.is_processing_input(),
		"voice": voice.stream != null or voice.playing,
		"video": view.get_node("Stage/Video").texture != null,
		"splash": view.get_node("Stage/SplashFade/Splash").texture != null,
		"buffers": view.get("_video_buffers") != [null, null]}


func check_host_bridge() -> void:
	var adapter_script: Script = load("res://Scenes/Frontend/Tests/StartupSceneCheckMedia.cs")
	var adapter: RefCounted = adapter_script.new()
	var bridge: Node = adapter.call("CreateInitializedBridge", Playback.resolve_media_root(OS.get_cmdline_user_args()))
	var state: Dictionary = adapter.call("BridgeSnapshot", bridge)
	var view: Control = state.presentation
	check(state.scheduled_seconds == 3095.0 / 25.0 and state.missing_count == 0 and state.unavailable == "",
		"Managed host did not preserve its single-cutscene initialization contract")
	check(bridge.get_child_count() == 1 and bridge.get_child(0) == view,
		"Managed bridge does not host the actual production scene")
	check(view.get_script().resource_path == "res://Scenes/Frontend/startup_sequence.gd",
		"Managed bridge bypasses GDScript playback")
	root.add_child(bridge)
	view.set_process(false)
	check(view.size == root.get_visible_rect().size, "Node bridge changed production full-viewport layout")
	view.call("_process", 0.1)
	state = adapter.call("BridgeSnapshot", bridge)
	check(state.pending_audio == 1 and state.completions == 0,
		"Managed audio observer did not see the live GDScript voice start")
	adapter.call("AbortBridge", bridge)
	check(adapter.call("BridgeSnapshot", bridge).completions == 0, "Managed abort skipped the process boundary")
	view.call("_process", 0.0)
	check(adapter.call("BridgeSnapshot", bridge).completions == 1, "Managed host did not receive completion once")
	check(completion_state(view) == retired_state(), "Managed completion left playback or input active")
	view.call("_process", 0.0)
	check(adapter.call("BridgeSnapshot", bridge).completions == 1, "Managed completion repeated")
	await create_timer(0.25).timeout
	check(adapter.call("BridgeSnapshot", bridge).pending_audio == 0, "Managed audio observer retained a stopped playback")
	bridge.queue_free()
	await process_frame
	adapter.call("DisposeRetirement")
	_sections["host_bridge"] = true


func retired_state() -> Dictionary:
	return {"visible": false, "processing": false, "input": false, "voice": false,
		"video": false, "splash": false, "buffers": false}


func empty_batch() -> Dictionary:
	return {"schema": Playback.VERIFIED_BATCH_SCHEMA, "clips": {}, "frame_paths": {}, "audio": {},
		"splash_path": "", "unavailable": ""}


func load_verified_batch() -> Dictionary:
	var fixture: String = ""
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--startup-verified-fixture="):
			fixture = argument.substr("--startup-verified-fixture=".length())
	if not fixture.is_empty() and FileAccess.file_exists(fixture):
		var input := FileAccess.open(fixture, FileAccess.READ)
		var value: Variant = input.get_var(false)
		if check(typeof(value) == TYPE_DICTIONARY, "Verified test fixture is not an object-free dictionary"):
			_sections["batch"] = true
			return value
		return {}
	if not check(ClassDB.class_exists("CSharpScript"), "First runtime check needs .NET to create its verified fixture; standard repeat needs --startup-verified-fixture"):
		return {}
	var adapter_script: Script = load("res://Scenes/Frontend/Tests/StartupSceneCheckMedia.cs")
	var adapter: RefCounted = adapter_script.new()
	var batch: Dictionary = adapter.call("LoadVerifiedMedia", Playback.resolve_media_root(OS.get_cmdline_user_args()))
	if not check(batch.clips.size() == 3 and batch.audio.size() == 3, "Canonical verified startup clips/audio are unavailable"):
		return {}
	if not fixture.is_empty():
		var owned_root: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/") + "/"
		if not check(fixture.is_absolute_path() and fixture.simplify_path().begins_with(owned_root), "New verified test fixture must remain in this checkout's local-data"):
			return {}
		if not check(DirAccess.dir_exists_absolute(fixture.get_base_dir()), "Create the owned fixture parent before running checks"):
			return {}
		var output := FileAccess.open(fixture, FileAccess.WRITE)
		if not check(output != null, "Could not create the owned verified test fixture"):
			return {}
		output.store_var(batch, false)
	_sections["batch"] = true
	return batch


func read_capture_options() -> bool:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--startup-scene-capture-dir="):
			_capture_directory = argument.substr("--startup-scene-capture-dir=".length())
	if _capture_directory.is_empty():
		return true
	var owned_root: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/") + "/"
	if not check(_capture_directory.is_absolute_path() \
			and _capture_directory.simplify_path().begins_with(owned_root) \
			and DirAccess.dir_exists_absolute(_capture_directory),
			"Capture directory must already exist under this checkout's local-data at an absolute owned path"):
		return false
	if not check(not Engine.is_editor_hint(), "Timed startup captures use the actual runtime scene; run frozen editor checks separately"):
		return false
	return check(DisplayServer.get_name() != "headless", "Rendered captures require the task-owned isolated display, not the headless dummy renderer")


func capture_production_samples() -> void:
	# FrontendCaptureRig's 'startup' plan skips FMVs and is not a movie-frame
	# oracle. These exact injected times use the real production player and
	# its 640x480 FMV law in RetailStartupSchedule.cs/RetailFmvPresentation.
	# They establish bounded rendered observations, not retail pixel parity.
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var view: Control = _scene.instantiate()
	var voice_starts: Array[bool] = []
	var observer: Callable = func(_player: AudioStreamPlayer) -> void: voice_starts.append(true)
	if not check(view.call("configure_verified_media", _batch, 0, 2, 1, observer).ok, "Rendered sample initialization failed"):
		view.free()
		viewport.queue_free()
		return
	viewport.add_child(view)
	view.set_process(false)
	view.set_process_input(false)
	var splash_start: float = 229.0 / 25.0 + 2054.0 / 25.0
	var samples: Array[Dictionary] = [
		{"name": "startup-logo-t003000-f00075.png", "seconds": 3.0, "cue": 0, "frame": 75, "alpha": 1.0},
		{"name": "startup-montage-t013160-f00100.png", "seconds": 229.0 / 25.0 + 4.0, "cue": 1, "frame": 100, "alpha": 1.0},
		{"name": "startup-splash-t092070-alpha050.png", "seconds": splash_start + 0.75, "cue": 2, "frame": 0, "alpha": 0.5},
		{"name": "startup-splash-t093070-alpha100.png", "seconds": splash_start + 1.75, "cue": 2, "frame": 0, "alpha": 1.0},
	]
	for sample: Dictionary in samples:
		_requested_captures.append(sample.name)
		view.call("_process", float(sample.seconds) - float(view.get("_elapsed_seconds")))
		var frame: Dictionary = view.get("_schedule").sample(view.get("_elapsed_seconds")).value
		check(frame.cue == sample.cue and frame.frame_index == sample.frame and frame.alpha == sample.alpha,
			"Rendered sample missed its exact production schedule point: " + String(sample.name))
		var destination: String = _capture_directory.path_join(sample.name)
		if not check(not FileAccess.file_exists(destination), "Capture cannot overwrite an earlier observation"):
			continue
		await RenderingServer.frame_post_draw
		var image: Image = viewport.get_texture().get_image()
		if check(image != null and image.get_size() == Vector2i(640, 480), "Rendered sample has the wrong viewport size") \
				and check(image.save_png(destination) == OK, "Could not save the task-owned rendered capture"):
			_completed_captures.append(sample.name)
			print("STARTUP_CAPTURE: ", destination, "; schedule_seconds=", view.get("_elapsed_seconds"),
				"; cue=", frame.cue, "; frame_index=", frame.frame_index, "; alpha=", frame.alpha)
	check(voice_starts.size() == 2, "Rendered cold-start samples changed the once-per-clip voice lifecycle")
	view.call("abort_for_harness")
	view.call("_process", 0.0)
	check(completion_state(view) == retired_state(), "Rendered samples did not retire their production player")
	viewport.queue_free()
	await process_frame
	_sections["captures"] = true
