# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production scene checks; captures require a caller-owned display.
const Debriefing = preload("res://Scenes/Frontend/debriefing_presentation.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _capture_dir: String = ""


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--debriefing-capture-dir="):
			_capture_dir = argument.trim_prefix("--debriefing-capture-dir=")
			var owned: String = ProjectSettings.globalize_path("res://../../local-data/").simplify_path().trim_suffix("/") + "/"
			if not _check(_capture_dir.is_absolute_path() and _capture_dir.simplify_path().begins_with(owned)
				and DirAccess.dir_exists_absolute(_capture_dir), "Capture must use an existing owned local-data directory."):
				quit(1)
				return
			if not _check(DisplayServer.get_name() != "headless", "Capture needs the caller's isolated rendered display."):
				quit(1)
				return
	var pointer: int = Input.mouse_mode
	var packed: PackedScene = load("res://Scenes/Frontend/Debriefing.tscn")
	var view: Debriefing = packed.instantiate()
	_check(view.get_node("Writing").get_child_count() == 4, "Four writing surfaces are authored before Ready.")
	_check(view.get_node("Grade").get_child_count() == 4, "Grade bracket and letter have separate body/shadow controls.")
	_check(view.get_node("Report").find_children("*", "Control", true, false).size() == 13,
		"Report labels, values and motion/layout origins are authored controls.")
	for node: Node in view.find_children("*", "Control", true, false):
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Every page control is standard-engine compatible.")
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Presentation controls do not capture pointer events.")
		if node.get_script() != null and node.has_method("displayed_units"):
			_check(not node.body_origin, "Debriefing retains the original shadow-anchor/body-minus-one font law.")
	_check(view.get_node("MetalRingOrigin") is Node2D, "Fractional art origin bypasses GUI control snapping without changing viewport policy.")
	_check(view.get_node("MetalRingOrigin").position == Vector2(-124.600006103515625, -184.600006103515625)
		and view.get_node("MetalRingOrigin/MetalRing").size == Vector2(819.20001220703125, 819.20001220703125)
		and view.get_node("MetalRingOrigin/MetalRing").scale == Vector2.ONE, "Metal ring submits the source float32 rectangle without a second sampling scale.")
	_check(view.get_node("Report/LevelName").position == Vector2(130, 149), "Level name is an editable title-font label at its source anchor.")
	_check(view.get_node("Report/Labels/MissionStatus").position == Vector2(130, 184), "Mission label retains y=184.")
	_check(view.get_node("Grade/BracketShadow").get_rect() == Rect2(241, 236, 168, 168), "Grade bracket shadow retains its distinct scale/offset.")
	_check(view.get_node("Grade/BracketBody").get_rect() == Rect2(240, 230, 160, 160), "Grade bracket body retains its distinct scale.")
	_check(view.get_node("Grade/LetterShadow").get_rect() == Rect2(291, 281, 64, 64), "Grade letter shadow retains +3,+3.")
	_check(view.get_node("Grade/LetterBody").get_rect() == Rect2(288, 278, 64, 64), "Grade letter is centred at 320,310.")
	for name: String in ["BracketBody", "LetterBody"]:
		_check(view.get_node("Grade/" + name).self_modulate == Color(1, 1, 1, 254.0 / 255.0), "Grade body retains submitted 0xfeffffff.")
	for index: int in range(4):
		_check(view.get_node("Writing/Tile%d" % index).get_rect() == Rect2(54, -38 + index * 180, 64, 256),
			"Writing keeps the documented cold-BSS y=90 phase and 180-pixel spacing.")
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	viewport.add_child(view)
	await process_frame
	await process_frame
	_check(view.get("_error") == "" and view.get("_assets_configured"), "Production private recipes load read-only.")
	_check(not view.is_processing() and not view.is_processing_input() and not view.is_processing_unhandled_input(),
		"No page-owned clock, input or gameplay loop starts.")
	_check(view.get_node("Underlay/Video").texture != null, "Same production FEBack component supplies a frozen real frame.")
	_check(view.body_font.glyph_widths().size() == 256 and view.title_font.glyph_widths().size() == 256, "Shared production fonts retain all 256 slots.")
	_check(view.get_node("Report/LevelName").displayed_units() == AtlasFont.units(WorldStrings.level_name(100)), "Editor label uses the admitted world string table.")
	_check(view.get_node("Report/Labels/MissionStatus").ink_color == Color(1.0, 1.0, 125.0 / 255.0, 1.0), "Submitted label word retains the released MODULATE2X product.")
	_check(view.get_node("Writing/Tile0").self_modulate == Color(253.0 / 255.0, 253.0 / 255.0, 253.0 / 255.0, 62.0 / 255.0), "Writing retains MODULATE2X RGB and independent submitted alpha.")
	_check(not view.get("_frame_supplied"), "Initial editor projection is explicitly separate from a runtime frame.")
	_done("authored_scene")

	var grade_bytes: Array = [null, 65, 66, 67, 68, 69, 83]
	for status: int in range(3):
		for primary: int in range(3):
			for secondary: int in range(3):
				for grade: Variant in grade_bytes:
					var snapshot: Dictionary = _projection(status, primary, secondary, grade)
					_check(view.set_frame(snapshot, "fallback", 0.0).ok, "Every settled outcome/objective/grade combination is admitted.")
					_check(view.get_node("Report/ValuesOrigin/Layout/MissionStatus").displayed_units() == AtlasFont.units(["Aborted", "Defeat", "Victory"][status]), "Outcome caption matches retained draw.")
					for entry: String in ["Primary", "Secondary"]:
						var summary: int = primary if entry == "Primary" else secondary
						var label: Control = view.get_node("Report/Labels/" + ("Primary" if entry == "Primary" else "SecondaryMotion/Secondary"))
						var value: Control = view.get_node("Report/ValuesOrigin/Layout/" + ("Primary" if entry == "Primary" else "SecondaryMotion/Secondary"))
						_check(label.visible == (summary != 0) and value.visible == (summary != 0), "Hidden objectives occupy no displayed row.")
						_check(value.displayed_units() == AtlasFont.units("Complete" if summary == 1 else "Incomplete"), "Objective text retains complete versus non-complete law.")
					_check(view.get_node("Report/Labels/SecondaryMotion/Secondary").global_position.y == (210.0 if primary == 0 else 226.0), "Secondary moves only when primary is hidden.")
					_check(view.get_node("Grade").visible == (grade != null) and view.get_node("Report/GradeLabel").visible == (grade != null), "Grade art and label follow nullable grade projection.")
					if grade != null:
						_check(view.get_node("Grade/LetterBody").texture == view.grade_textures[Debriefing.GRADE_BYTES.find(grade)], "Grade uses the selected production recipe.")
					_check(view.get_node("Report/ValuesOrigin").position.x == 150.0 + maxf(view.body_font.measure("Mission Status"), maxf(view.body_font.measure("Primary Objectives"), view.body_font.measure("Secondary Objectives"))), "Value column follows untranslated labels without colon/space.")
	_done("settled_projection")

	var raw := PackedInt32Array([65, 0, 0xd83d, 0xde80, 0xfeff])
	var unknown: Dictionary = _projection(-5, -1, 9, null)
	unknown.world_finished = 999999
	_check(view.set_frame(unknown, raw, 0.0).ok, "Unknown enum values preserve original render fallback behavior.")
	_check(view.get_node("Report/LevelName").displayed_units() == raw, "Fallback level name preserves NUL and raw surrogate units.")
	_check(view.get_node("Report/ValuesOrigin/Layout/MissionStatus").displayed_units() == AtlasFont.units("Aborted"), "Unknown status retains Aborted fallback.")
	var detached: Dictionary = view.view_snapshot()
	detached.projection.mission_status = 2
	detached.level_name[0] = 90
	unknown.mission_status = 2
	raw[0] = 90
	_check(view.view_snapshot().projection.mission_status == -5 and view.view_snapshot().level_name[0] == 65, "Input and output snapshots are detached from live presentation.")
	var before: Dictionary = view.view_snapshot()
	for invalid: Dictionary in [{}, _projection(0, 0, 0, 70), _projection(0, 0, 0, 256)]:
		_check(not view.set_frame(invalid, "invalid", 0.0).ok and view.view_snapshot() == before, "Invalid projection does not replace the current page.")
	var malformed: Dictionary = _projection(0, 0, 0, null)
	malformed.world_finished = 2147483648
	_check(not view.set_frame(malformed, "invalid", 0.0).ok, "Projection requires exact signed32 values.")
	_check(not view.set_frame(_projection(0, 0, 0, null), null, 0.0).ok, "Null fallback text fails explicitly.")
	_done("ownership_and_transport")

	var label: Control = view.get_node("Report/Labels/MissionStatus")
	label.position += Vector2(7, 3)
	label.text = "Enhanced status"
	label.override_text = true
	_check(view.set_frame(_projection(2, 1, 2, 65), "", 1.0).ok, "Production frame updates after a deliberate authoring override.")
	_check(label.position == Vector2(137, 187) and label.displayed_units() == AtlasFont.units("Enhanced status"), "Frame updates preserve authored layout and explicit enhanced text.")
	label.override_text = false
	_check(label.displayed_units() == AtlasFont.units("Mission Status: "), "Turning off override restores the faithful imported text.")
	label.position = Vector2(130, 184)
	if Engine.is_editor_hint():
		view.editor_projection = view.editor_projection.duplicate(true)
		view.editor_projection.mission_status = 1
		view.editor_projection.grade = 0
		_check(view.view_snapshot().projection.mission_status == 1 and not view.get_node("Grade").visible, "Inspector fixture changes update the same frozen scene.")
	var storage := PackedScene.new()
	_check(storage.pack(view) == OK, "Actual production page remains packable after private rendering.")
	var scene_state: SceneState = storage.get_state()
	for index: int in range(scene_state.get_node_count()):
		for property: int in range(scene_state.get_node_property_count(index)):
			_stored(scene_state.get_node_property_value(index, property), {})
	_check(Input.mouse_mode == pointer, "Editor and runtime checks never capture the pointer.")
	_done("editor_and_publication")
	for item: Dictionary in [
		{"name": "victory-a", "projection": _projection(2, 1, 2, 65)},
		{"name": "defeat-secondary", "projection": _projection(1, 0, 2, null)},
		{"name": "aborted-hidden", "projection": _projection(0, 0, 0, null)},
		{"name": "victory-s", "projection": _projection(2, 2, 1, 83)}]:
		view.set_frame(item.projection, "", 0.0)
		await _capture(viewport, item.name + ".png")
	viewport.queue_free()
	await process_frame
	await process_frame
	if Engine.is_editor_hint():
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	print("DEBRIEFING_SCENE_CHECKS: ", JSON.stringify({"schema": 1, "checks": _checks,
		"failure_count": _failures.size(), "failures": _failures, "completed": _completed,
		"editor": Engine.is_editor_hint()}))
	quit(0 if _failures.is_empty() else 1)


func _projection(status: int, primary: int, secondary: int, grade: Variant) -> Dictionary:
	return {"world_finished": 100, "mission_status": status, "primary_objectives": primary,
		"secondary_objectives": secondary, "grade_byte": grade, "new_goodie_count": 99, "first_goodie": true}


func _stored(value: Variant, visited: Dictionary) -> void:
	if value is Resource:
		if visited.has(value.get_instance_id()):
			return
		visited[value.get_instance_id()] = true
		_check(not value is Image and not value is ImageTexture, "Public scene storage cannot embed private pixels.")
		for property: Dictionary in value.get_property_list():
			if (int(property.usage) & PROPERTY_USAGE_STORAGE) != 0:
				_stored(value.get(property.name), visited)
	elif value is Array:
		for item: Variant in value:
			_stored(item, visited)
	elif value is Dictionary:
		for key: Variant in value:
			_stored(value[key], visited)


func _capture(viewport: SubViewport, filename: String) -> void:
	if _capture_dir.is_empty():
		return
	var destination: String = _capture_dir.path_join(filename)
	if not _check(not FileAccess.file_exists(destination), "Capture refuses an existing result."):
		return
	await process_frame
	await RenderingServer.frame_post_draw
	_check(viewport.get_texture().get_image().save_png(destination) == OK, "Owned Debriefing capture saved.")


func _check(condition: bool, message: String) -> bool:
	_checks += 1
	if not condition:
		_failures.append(message)
		push_error(message)
	return condition


func _done(section: String) -> void:
	_completed.append(section)
	print("DEBRIEFING_SCENE_SECTION: ", section)
