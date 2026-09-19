# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production scene checks in either standard Godot runtime or editor.
## Optional captures require the parent's isolated display and a fresh owned
## local-data directory. This harness never chooses or starts a display.
const Hud = preload("res://Scenes/Hud/first_flight_hud.gd")
const Part = preload("res://Scenes/Hud/hud_part.gd")
const MessagePanel = preload("res://Client/message_panel.gd")
const TextDraw = preload("res://Scenes/Hud/hud_text_draw.gd")
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _capture_dir: String = ""

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--hud-scene-capture-dir="):
			_capture_dir = argument.trim_prefix("--hud-scene-capture-dir=")
			var owned: String = ProjectSettings.globalize_path("res://../../local-data/").simplify_path().trim_suffix("/") + "/"
			if not _check(_capture_dir.is_absolute_path() and _capture_dir.simplify_path().begins_with(owned) and DirAccess.dir_exists_absolute(_capture_dir), "Capture output is an existing task-owned local-data directory."):
				quit(1)
				return
			if not _check(DisplayServer.get_name() != "headless", "Captures require an isolated rendered display."):
				quit(1)
				return
	var pointer_before: int = Input.mouse_mode
	var scene: PackedScene = load("res://Scenes/Hud/FirstFlightHud.tscn")
	var view: Hud = scene.instantiate()
	var stage: Control = view.get_node("Surface/DesignStage")
	var groups: Array[String] = []
	for group: Node in stage.get_children():
		groups.append(String(group.name))
	_check(groups == ["Base", "Glow", "Text"], "Three explicit production blend groups retain order.")
	var parts: Array[Part] = []
	var contents: Dictionary = {}
	for node: Node in view.find_children("*", "Control", true, false):
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Every authored node is standard-engine compatible.")
		if node is Part:
			parts.append(node)
			contents[int(node.part)] = true
			_check(node.use_parent_material, "Instrument inherits its blend group.")
	_check(parts.size() == 22 and contents.size() == 22, "All 22 authored parts and unique drawing identities exist before Play.")
	_check(view.find_children("*", "TextureRect", true, false).size() == 6, "Six native texture controls own static backing and crosshair layout.")
	for group: Control in stage.get_children():
		_check(not group.use_parent_material and group.material is ShaderMaterial, "Each blend group owns its authored material.")
		var shader: String = group.material.shader.code
		_check(shader.contains("COLOR.a < (8.0 / 255.0)"), "Post-modulate alpha threshold remains 8/255.")
		_check(shader.contains("blend_add" if group.name == "Glow" else "blend_mix"), "Only the Glow group uses additive blending.")
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	viewport.add_child(view)
	await process_frame
	await process_frame
	_check(view.ready_for_snapshot, "Actual production textures and drawing owners initialize.")
	_check(view.get_node("Surface").visible == Engine.is_editor_hint(), "Only the editor opens a frozen illustration before a snapshot.")
	var scanner: TextureRect = stage.get_node("Base/ScannerBackdrop")
	_check(scanner.position == Vector2(17, 368) and scanner.size == Vector2(128, 128), "Measured scanner rectangle is retained.")
	_check(scanner.texture.get_script().resource_path == "res://Scenes/Shared/retail_texture_page.gd", "Native control uses the shared private texture recipe.")
	_check(scanner.texture.get_image().get_width() == 128, "Actual private scanner page decodes.")
	var right: TextureRect = stage.get_node("Base/RightWeaponBacking")
	_check(right.position == Vector2(499, 339) and right.flip_h, "Right weapon backing retains native mirror and position.")
	var crosshair: Control = stage.get_node("Base/Crosshair")
	_check(crosshair.get_child(0).name == "Primary" and crosshair.get_child(1).name == "Secondary" and crosshair.get_child(2).name == "Dot", "Three measured crosshair quads retain issue order.")
	_near(crosshair.get_node("Primary").self_modulate.a, 0.6863, "Primary measured alpha.")
	_near(crosshair.get_node("Secondary").self_modulate.a, 0.3412, "Secondary measured alpha.")
	_near(crosshair.get_node("Dot").self_modulate.a, 0.3412, "Dot measured alpha.")
	_done("authored_scene")

	var compass: Part = stage.get_node("Base/Compass")
	for property: Dictionary in compass.get_property_list():
		if property.name in ["part", "source_rect"]:
			_check((int(property.usage) & PROPERTY_USAGE_READ_ONLY) != 0, "Imported drawing identity is distinguished from editable layout.")
	_near_vector(compass.get_transform() * (compass.retail_to_local_transform() * Vector2(320, 240)), Vector2(320, 240), "Measured mapping starts at identity.")
	compass.position += Vector2(37, -12)
	_near_vector(compass.get_transform() * (compass.retail_to_local_transform() * Vector2(320, 240)), Vector2(357, 228), "Native position edits move production draw coordinates.")
	compass.size *= 1.5
	compass.rotation = 0.25
	_near_vector(compass.get_transform() * (compass.retail_to_local_transform() * Vector2(320, 240)), compass.position + Vector2(192, 192).rotated(0.25), "Native size and rotation compose with the measured frame.")
	compass.position = Vector2(192, 112)
	compass.size = Vector2(256, 256)
	compass.rotation = 0
	for sample: Array in [[640,480,1.0,0.0,0.0], [1280,720,1.5,160.0,0.0], [1920,1080,2.25,240.0,0.0], [1280,1024,2.0,0.0,32.0]]:
		viewport.size = Vector2i(sample[0], sample[1])
		await process_frame
		_near(stage.scale.x, sample[2], "Production stage maintains 4:3 scale.")
		_near_vector(stage.position, Vector2(sample[3], sample[4]), "Production stage remains centered.")
	viewport.size = Vector2i(640, 480)
	await process_frame
	_done("layout")

	var batch: Dictionary = Hud.illustration_snapshot()
	batch.frame.mission_tick = 0
	batch.frame.energy = 4321
	batch.frame.hull = 12345
	_check(view.set_snapshot(batch).ok, "A detached runtime drawing batch is accepted.")
	_check(view.get_node("Surface").visible, "A snapshot opens the ordinary production HUD.")
	batch.frame.energy = 1
	_check(view.snapshot().frame.energy == 4321, "Mutating caller dictionaries cannot change live presentation.")
	var detached: Dictionary = view.snapshot()
	detached.frame.hull = 1
	_check(view.snapshot().frame.hull == 12345, "Presentation reads are detached.")
	var before: Dictionary = view.snapshot()
	var malformed: Dictionary = batch.duplicate(true)
	malformed.portrait_pose = 4
	_check(not view.set_snapshot(malformed).ok and view.snapshot() == before, "Invalid portrait admission is explicit and does not mutate presentation.")
	malformed = batch.duplicate(true)
	malformed.hud.contacts = [{"id": 1}]
	_check(not view.set_snapshot(malformed).ok and view.snapshot() == before, "Incomplete drawing records are rejected before publication.")
	batch.frame.energy = 4321
	batch.frame.mission_tick = 121
	batch.message = {"text": PackedInt32Array([65, 0, 0xd83d, 0xde00, 32, 66])}
	batch.playback = {"is_available": true, "position_seconds": 0.1}
	_check(view.set_snapshot(batch).ok, "Raw UTF-16 message text reaches the production panel.")
	var wrapped: Dictionary = MessagePanel.wrap(batch.message.text)
	var expected: Dictionary = MessagePanel.window(wrapped.value, MessagePanel.revealed_characters(0.1).value)
	_check(view.snapshot().message_window == expected.value, "Production text uses the validated native panel model without NUL loss.")
	var draw: TextDraw = view.get("_text")
	_near(draw.measure(PackedInt32Array([32])), 8.0, "Small HUD space advances eight pixels.")
	_near(draw.measure(PackedInt32Array([32]), true), 17.0, "Large HUD space retains its atlas advance.")
	var broken: Array[PackedInt32Array] = draw.wrap_lines(PackedInt32Array([13, 10, 65, 32, 32, 66, 13]), 360)
	_check(broken == [PackedInt32Array(), PackedInt32Array([65,32,32,66]), PackedInt32Array()], "HUD help/terminal wrapping preserves CRLF and intra-word separators.")
	batch.message = null
	batch.hud.terminal = {"visible": true, "outcome": 1, "failure_reason": 0, "ticks_remaining": 20}
	batch.terminal_title = "VICTORY"
	for index: int in range(12):
		_check(view.set_snapshot(batch).ok, "Terminal batch admitted.")
		_check(view.snapshot().terminal_darkener_alpha == mini(160, (index + 1) * 16), "Terminal darkener advances once per host snapshot, not per instrument draw.")
	batch.hud.terminal = {"visible": true, "outcome": 2, "failure_reason": 1, "ticks_remaining": 10}
	batch.terminal_title = "DEFEAT"
	batch.terminal_reason = "SYNTHETIC TEST REASON"
	_check(view.set_snapshot(batch).ok and view.snapshot().terminal_darkener_alpha == 16, "Changing the terminal outcome restarts its original fade.")
	batch.hud.terminal.visible = false
	_check(view.set_snapshot(batch).ok and view.snapshot().terminal_darkener_alpha == 0, "Leaving terminal clears its fade.")

	if Engine.is_editor_hint():
		_check(not view.configure_model({}, {}, {}).ok, "Editor refuses the live model boundary.")
	else:
		# Public/synthetic fixture only. The .NET actual-scene test separately
		# proves the unchanged SHA-admitted retail catalog boundary.
		var catalog: Dictionary = {"schema": "onslaught-hud-verified-catalog.v1", "messages": {}, "help": {},
			"terminal": {"victory": "TEST WIN", "defeat": "TEST LOSS", "tutorial_broken": "TEST TUTORIAL", "player_death": "TEST PLAYER", "water": "TEST WATER"}}
		for identity: int in range(1, 52):
			catalog.messages[identity] = "SYNTHETIC TEST MESSAGE"
		for identity: int in [1197607, 8268984, 17186000, 31505972, 2302408, 488286858]:
			catalog.help[identity] = "SYNTHETIC TEST HELP"
		var constants: Dictionary = {}
		for key: String in ["maximum_energy", "maximum_hull", "ticks_per_second", "damage_flash_lifetime_ticks", "message_box_allowed_tick"]:
			constants[key] = batch[key]
		_check(view.configure_model({}, catalog, constants).ok, "Standard engine initializes the one native HUD model from an explicit batch.")
		var facts: Dictionary = {"tick": 0, "player_position": {"x": 0, "z": 0}, "facing_yaw_micro_rad": 0,
			"mode": 0, "walker_selected_weapon": 1, "jet_selected_weapon": 2, "hud_emphasis_mask": 0,
			"mission": {"tick": 0, "pulse_cannon_availability": 2, "twin_vulcan_availability": 2,
				"mech_vulcan_availability": 0, "outcome": 0, "failure_reason": 0, "terminal_ticks_remaining": 0},
			"actors": [], "commanded_allegiances": [], "damage_flashes": []}
		var model_frame: Dictionary = batch.frame.duplicate(true)
		model_frame.tick = 0
		model_frame.mission_tick = 0
		_check(view.consume_events([{ "kind": "message", "tick": 0, "speaker_id": 1508464, "message_id": 1,
			"script_waits_for_duration": false, "expected_playback_ticks": 12 },
			{ "kind": "help", "tick": 0, "help_message_id": 1197607 }]).ok, "Production model consumes an ordered event batch once.")
		var projected: Dictionary = view.update_from_facts(facts, model_frame)
		_check(projected.ok and projected.value.delivered_message_ids == PackedInt32Array([1]) and projected.value.delivered_help_count == 1, "The native model and drawing handoff retain both delivery histories.")
		_check(view.update_from_facts(facts, model_frame).value.delivered_message_count == 1, "Repeated projection does not consume events again.")
		_check(view.consume_events([{ "kind": "message", "tick": 100, "speaker_id": 1508464, "message_id": 9999,
			"script_waits_for_duration": false, "expected_playback_ticks": 12 }]).ok, "Unmapped message remains a catalog lookup responsibility.")
		facts.tick = 100
		facts.mission.tick = 100
		model_frame.tick = 100
		model_frame.mission_tick = 100
		var refused: Dictionary = view.update_from_facts(facts, model_frame)
		_check(not refused.ok and refused.delivered_message_ids == PackedInt32Array([1,9999]), "Catalog failure carries IDs already published after model projection.")
		_check(view.snapshot().frame.tick == 0, "Catalog failure preserves the prior visible snapshot.")
		facts.tick = 0
		facts.mission.tick = 0
		model_frame.tick = 0
		model_frame.mission_tick = 0
		_check(view.update_from_facts(facts, model_frame).value.delivered_message_count == 0, "Backwards Core mission tick resets the production model history.")
	_done("snapshot")

	# Exercise every existing optional drawing branch in the actual scene. These
	# are clearly synthetic test records, not newly inferred retail behavior.
	batch = Hud.illustration_snapshot()
	batch.frame.tick = 7
	batch.frame.facing_yaw_micro_rad = 509830
	batch.hud.emphasized_parts = [0,1,2,3,4,5]
	batch.hud.contacts = [{"id": 7, "position": {"x": 10000, "z": 20000}, "velocity": {"x": 0, "z": 0}, "allegiance": 0, "size": 1, "is_objective": false, "on_scanner": true}]
	batch.hud.objectives = [{"actor_id": 5, "thing_name": "synthetic", "position_millimeters": {"x": 0, "y": 0, "z": 20000}}, {"actor_id": 6, "thing_name": "offscreen", "position_millimeters": {"x": 10000, "y": 0, "z": -20000}}]
	batch.hud.threats = [{"relative_yaw_micro_rad": 300000, "ticks_remaining": 450}]
	batch.hud.damage_flashes = [{"relative_yaw_micro_rad": -500000, "ticks_remaining": 20}]
	batch.hud.target = {"contact_id": 7, "hull_permille": 1000, "predicted_position": {"x": 12000, "z": 20000}, "lock_permille": 500}
	batch.hud.weapon = {"selected_weapon": 1, "pulse_cannon_enabled": true, "vulcan_cannon_enabled": true,
		"selection_panel_visible": true, "selection_slot": 1, "pulse_heat_permille": 375, "vulcan_ammo": 120,
		"charge_permille": 200, "pulse_cannon_overheated": true}
	for slot: int in [1,2,3]:
		batch.hud.weapon.selection_slot = slot
		_check(view.set_snapshot(batch).ok, "Weapon selection branch accepts its measured slot.")
		await process_frame
	for speaker: int in [1508464,10565784,919601]:
		for pose: int in range(4):
			batch.socket = 1
			batch.speaker = speaker
			batch.portrait_pose = pose
			batch.noise_phase = pose * 3
			_check(view.set_snapshot(batch).ok, "Each real speaker portrait pose is admitted.")
			await process_frame
	batch.speaker = null
	batch.portrait_pose = null
	_check(view.set_snapshot(batch).ok, "Promote-gap noise has no fabricated speaker.")
	await process_frame
	batch.socket = 2
	batch.hud.battle_line.has_influence_values = true
	batch.hud.battle_line.influence_permille = []
	var nodes: Array = preload("res://Client/hud_presentation.gd").influence_nodes()
	for index: int in range(nodes.size()):
		batch.hud.battle_line.influence_permille.append([-500, 0, 500][index % 3])
	_check(view.set_snapshot(batch).ok, "Authored influence geometry draws from supplied values.")
	await process_frame
	batch.socket = 3
	batch.hud.weapon.selected_weapon = 2
	_check(view.set_snapshot(batch).ok, "Forseti and ammo branches retain their production path.")
	await process_frame
	await _capture(viewport, "hud-native-exercised.png")
	_done("drawing_branches")

	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "An initialized production HUD can be packed.")
	var saved: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for node: int in range(saved.get_node_count()):
		for property: int in range(saved.get_node_property_count(node)):
			_stored(saved.get_node_property_value(node, property), visited)
	_check(view.find_children("*", "AudioStreamPlayer", true, false).is_empty(), "HUD creates no audio owner.")
	_check(view.find_children("*", "Camera3D", true, false).is_empty(), "HUD creates no camera or world.")
	_check(not view.is_processing() and not view.is_processing_input() and not view.is_processing_unhandled_input(), "HUD has no autonomous clock or device-input callback.")
	_check(Input.mouse_mode == pointer_before, "HUD never changes pointer ownership.")
	if Engine.is_editor_hint():
		view.show_editor_illustration = false
		_check(not view.get_node("Surface").visible, "Editor can hide its frozen illustration.")
		view.show_editor_illustration = true
		_check(view.get_node("Surface").visible, "Editor reuses the same production drawing path.")
		var frozen: Dictionary = view.snapshot()
		await process_frame
		await process_frame
		_check(view.snapshot() == frozen, "Editor illustration remains frozen across frames.")
	_done("editor_and_publication")
	batch = Hud.illustration_snapshot()
	_check(view.set_snapshot(batch).ok, "Full-gauge source-pinned state restores for comparison capture.")
	await _capture(viewport, "hud-native.png")
	viewport.size = Vector2i(1280, 720)
	await process_frame
	await _capture(viewport, "hud-widescreen.png")
	viewport.queue_free()
	view = null
	draw = null
	parts.clear()
	await process_frame
	await process_frame
	if Engine.is_editor_hint():
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
	print("HUD_NATIVE_SCENE_CHECKS: %d checks; %d failures; completed=%s" % [_checks, _failures.size(), ",".join(_completed)])
	quit(0 if _failures.is_empty() else 1)

func _stored(value: Variant, visited: Dictionary) -> void:
	if value is Resource:
		if visited.has(value.get_instance_id()):
			return
		visited[value.get_instance_id()] = true
		_check(not value is Image and not value is ImageTexture, "Public scene/resource storage cannot embed decoded private pixels.")
		for property: Dictionary in value.get_property_list():
			if (int(property.usage) & PROPERTY_USAGE_STORAGE) != 0:
				_stored(value.get(property.name), visited)
	elif typeof(value) == TYPE_ARRAY:
		for item: Variant in value:
			_stored(item, visited)
	elif typeof(value) == TYPE_DICTIONARY:
		for key: Variant in value:
			_stored(value[key], visited)

func _capture(viewport: SubViewport, filename: String) -> void:
	if _capture_dir.is_empty():
		return
	var destination: String = _capture_dir.path_join(filename)
	if not _check(not FileAccess.file_exists(destination), "Capture refuses overwriting an existing result."):
		return
	await RenderingServer.frame_post_draw
	_check(viewport.get_texture().get_image().save_png(destination) == OK, "Task-owned capture saved: " + filename)

func _check(condition: bool, message: String) -> bool:
	_checks += 1
	if not condition:
		_failures.append(message)
		push_error(message)
	return condition

func _near(value: float, expected: float, message: String) -> void:
	_check(absf(value - expected) < 0.0001, message)

func _near_vector(value: Vector2, expected: Vector2, message: String) -> void:
	_check(value.distance_to(expected) < 0.0001, message)

func _done(section: String) -> void:
	_completed.append(section)
	print("HUD_NATIVE_SCENE_SECTION: " + section)
