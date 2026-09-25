# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Runs the actual production page in standard Godot or the .NET editor.
const LoadingPage = preload("res://Scenes/Frontend/loading_presentation.gd")
const Strings = preload("res://Scenes/Frontend/loading_strings.gd")
const Text = preload("res://Core/canonical_json_string.gd")
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var pointer: int = Input.mouse_mode
	var packed: PackedScene = load("res://Scenes/Frontend/Loading.tscn")
	var view: LoadingPage = packed.instantiate()
	_check(view.get_child_count() == 4 and view.get_node("Caption").get_child_count() == 5,
		"Clear, background, five caption passes and fixed bar are authored before Ready.")
	_check(view.get_node("Caption") is Node2D and view.get_node("Caption").position == Vector2(270, 393.5),
		"Source half-pixel caption anchor survives GUI control snapping without changing viewport policy.")
	_check(view.get_node("Clear").get_rect() == Rect2(0, 0, 640, 480) and view.get_node("Clear").color == Color.BLACK,
		"Loading retains its opaque full-stage black clear.")
	_check(view.get_node("Background").get_rect() == Rect2(0, 0, 640, 480), "Background stretches over the source stage.")
	_check(view.get_node("Background").texture.dimensions == Vector2i(512, 512)
		and view.get_node("Background").texture.compression == 0, "LoadingScreen keeps its exact DXT1 dimensions/admission.")
	_check(view.get_node("Bar").get_rect() == Rect2(78, 423, 485, 25) and view.get_node("Bar").color == Color.BLACK,
		"Known fallback remains one opaque measured bbox, without unrelated DrawBar caps or invented fill.")
	var offsets: Array[Vector2] = [Vector2(-1, 1), Vector2(1, 1), Vector2(-1, -1), Vector2(1, -1), Vector2.ZERO]
	for index: int in range(5):
		var label: Control = view.get_node("Caption").get_child(index)
		_check(label.name == LoadingPage.CAPTION_PARTS[index] and label.position == offsets[index], "Caption draw order and offsets match the retained source.")
		_check(not label.shadow and not label.body_origin, "Loading passes are outlined bodies, never ordinary drop shadows.")
		_check(label.ink_color == (Color.WHITE if index == 4 else Color.BLACK), "Four black passes precede the white caption body.")
	for node: Node in view.find_children("*", "Control", true, false):
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Every authored control loads in standard Godot.")
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Presentation controls do not capture input.")
	_done("authored_scene")
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	viewport.add_child(view)
	await process_frame
	await process_frame
	_check(view.get("_assets_configured") and view.get("_error") == "", "Production recipes load from the read-only private routes.")
	_check(not view.is_processing() and not view.is_processing_input() and not view.is_processing_unhandled_input(), "Loading owns no lifecycle, clock or input loop.")
	_check(view.title_font.glyph_widths().size() == 256, "Production font measures every original glyph slot.")
	_check(view.title_font.measure("Loading...") == 98.0, "Admitted Loading caption keeps the measured 98-pixel advance.")
	_check(not view.get("_frame_supplied") and view.view_snapshot().facts == _facts(0, false, false), "Opening shows explicit frozen facts without requesting a load.")
	var source: String = FileAccess.get_file_as_string("res://Assets/Frontend/english.json")
	var receipt: Dictionary = Strings.admit_source(source)
	_check(receipt.ok and receipt.value == Text.units("Loading...").value, "Standalone caption consumes the same verified English receipt.")
	for sample: Dictionary in [
		{"source": "", "type": "InvalidDataException"},
		{"source": "{", "type": "JsonReaderException"},
		{"source": "[]", "type": "InvalidOperationException"},
		{"source": "{}", "type": "KeyNotFoundException"},
		{"source": source.replace("onslaught.frontend-strings.v1", "unverified"), "type": "InvalidDataException"},
		{"source": source.replace(Strings.SOURCE_SHA256, "unverified"), "type": "InvalidDataException"},
		{"source": source.replace('"Loading..."', 'null'), "type": "InvalidDataException"},
		{"source": source.replace('"Loading..."', '7'), "type": "InvalidOperationException"},
		{"source": source.replace('"Loading..."', '"\\ud800"'), "type": "InvalidOperationException"}]:
		var rejected: Dictionary = Strings.admit_source(sample.source)
		_check(not rejected.ok and rejected.error_type == sample.type, "Source admission rejects the same malformed or unverified receipt kind.")
	var raw_source: Dictionary = Strings.admit_source(source.replace('"Loading..."', '"A\\u0000B\\ud83d\\ude80\\ufeff"'))
	_check(raw_source.ok and raw_source.value == PackedInt32Array([65, 0, 66, 0xd83d, 0xde80, 0xfeff]), "Receipt text preserves UTF-16 NUL/non-BMP and leading/trailing code units.")
	_done("production_assets_and_receipt")
	for frames: int in [-2147483648, -1, 0, 1, 2, 3, 2147483647]:
		for requested: bool in [false, true]:
			for ready: bool in [false, true]:
				var facts: Dictionary = _facts(frames, requested, ready)
				_check(view.set_frame(facts, receipt.value).ok and view.view_snapshot().facts == facts, "Signed32 boundary facts are detached display data, not a second loading state machine.")
				_check(view.get_node("Bar").get_rect() == Rect2(78, 423, 485, 25) and view.get_node("Bar").color == Color.BLACK,
					"Frame/ready/request transitions never fabricate a fill animation.")
	var raw := PackedInt32Array([65, 0, 66, 0xd83d, 0xde80, 0xfeff])
	var facts: Dictionary = _facts(2, true, false)
	_check(view.set_frame(facts, raw).ok, "Raw runtime caption is accepted without lossy String transport.")
	facts.loading_frames = 99
	raw[0] = 90
	var detached: Dictionary = view.view_snapshot()
	detached.facts.ready = true
	detached.caption[0] = 90
	_check(view.view_snapshot().facts == _facts(2, true, false) and view.view_snapshot().caption[0] == 65, "Inputs and returned snapshots cannot mutate live presentation.")
	var before: Dictionary = view.view_snapshot()
	for invalid: Dictionary in [{}, {"loading_frames": 2147483648, "launch_requested": true, "ready": false},
		{"loading_frames": 2.0, "launch_requested": true, "ready": false}, {"loading_frames": 2, "launch_requested": 1, "ready": false}]:
		_check(not view.set_frame(invalid, "bad").ok and view.view_snapshot() == before, "Malformed facts fail before presentation mutation.")
	for text: Variant in [null, 7, PackedInt32Array([-1]), PackedInt32Array([65536])]:
		_check(not view.set_frame(_facts(0, false, false), text).ok and view.view_snapshot() == before, "Malformed raw caption fails before frame mutation.")
	_check(view.set_frame(_facts(0, false, false), "").ok, "A directly supplied empty caption preserves the old zero-glyph draw behavior.")
	_done("facts_and_transport")
	view.get_node("Caption").position += Vector2(0.25, 0.25)
	view.get_node("Bar").position += Vector2(5, 3)
	view.caption = "Enhanced loading"
	view.override_caption = true
	view.set_frame(_facts(2, true, true), receipt.value)
	for part: String in LoadingPage.CAPTION_PARTS:
		_check(view.get_node("Caption/" + part).displayed_units() == Text.units("Enhanced loading").value, "Explicit enhanced caption updates the same five production passes.")
	_check(view.get_node("Caption").position == Vector2(270.25, 393.75) and view.get_node("Bar").position == Vector2(83, 426), "Runtime batches preserve deliberate authored placement.")
	view.override_caption = false
	_check(view.get_node("Caption/Body").displayed_units() == receipt.value, "Disabling override restores imported caption.")
	if Engine.is_editor_hint():
		view.editor_progress = view.editor_progress.duplicate(true)
		view.editor_progress.loading_frames = 2
		view.editor_progress.ready = true
		_check(view.view_snapshot().facts.loading_frames == 2 and view.view_snapshot().facts.ready and not view.get("_frame_supplied"), "Inspector facts refresh the same frozen page without advancing loading.")
	var storage := PackedScene.new()
	_check(storage.pack(view) == OK, "Production page remains packable after private rendering.")
	var state: SceneState = storage.get_state()
	for index: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(index)):
			_stored(state.get_node_property_value(index, property), {})
	_check(Input.mouse_mode == pointer and view.find_children("*", "AudioStreamPlayer", true, false).is_empty()
		and view.find_children("*", "Camera3D", true, false).is_empty(), "No pointer, audio or game-world owner is introduced.")
	_done("editor_and_publication")
	viewport.queue_free()
	await process_frame
	await process_frame
	if Engine.is_editor_hint():
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	print("LOADING_SCENE_CHECKS: ", JSON.stringify({"schema": 1, "checks": _checks, "failure_count": _failures.size(),
		"failures": _failures, "completed": _completed, "editor": Engine.is_editor_hint()}))
	quit(0 if _failures.is_empty() else 1)


func _facts(frames: int, requested: bool, ready: bool) -> Dictionary:
	return {"loading_frames": frames, "launch_requested": requested, "ready": ready}


func _stored(value: Variant, visited: Dictionary) -> void:
	if value is Resource:
		if visited.has(value.get_instance_id()):
			return
		visited[value.get_instance_id()] = true
		_check(not value is Image and not value is ImageTexture, "Serialized recipes never embed private pixels.")
		for property: Dictionary in value.get_property_list():
			if (int(property.usage) & PROPERTY_USAGE_STORAGE) != 0:
				_stored(value.get(property.name), visited)
	elif value is Array:
		for item: Variant in value:
			_stored(item, visited)
	elif value is Dictionary:
		for key: Variant in value:
			_stored(value[key], visited)


func _check(condition: bool, message: String) -> bool:
	_checks += 1
	if not condition:
		_failures.append(message)
		push_error(message)
	return condition


func _done(section: String) -> void:
	_completed.append(section)
	print("LOADING_SCENE_SECTION: ", section)
