# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## The settled production FEP_DEBRIEFING page, using its authored Controls.
## RetailDebriefingProjection already owns the outcome/objective/grade laws.
## The retained comparison and provenance are in Tests/DebriefingReference.cs.
## No entry/exit interpolation, goodie effects, grade glint or new clock is
## invented. Writing remains at the documented cold-BSS y=90 phase.
## MetalRingOrigin is Node2D so the viewport's GUI pixel snapping does not
## round its fractional origin; its child TextureRect owns the exact size.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const BitmapLabel = preload("res://Scenes/Frontend/frontend_bitmap_label.gd")
const EditorProjection = preload("res://Scenes/Frontend/debriefing_projection.gd")
const Underlay = preload("res://Scenes/Frontend/frontend_underlay.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Values = preload("res://Core/retail_career_values.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const GRADE_BYTES: Array[int] = [65, 66, 67, 68, 69, 83]
const LABELS: Array[String] = ["Mission Status", "Primary Objectives", "Secondary Objectives"]

@export var body_font: AtlasFont
@export var title_font: AtlasFont
@export var underlay: Underlay
@export var grade_textures: Array[Texture2D] = []
@export var editor_projection: EditorProjection:
	set(value):
		if editor_projection != null and editor_projection.changed.is_connected(_editor_projection_changed):
			editor_projection.changed.disconnect(_editor_projection_changed)
		editor_projection = value
		if editor_projection != null:
			editor_projection.changed.connect(_editor_projection_changed)
		if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied):
			show_editor_projection()

var _snapshot: Dictionary = {}
var _level_name: PackedInt32Array = PackedInt32Array()
var _frames: Array = []
var _assets_configured: bool = false
var _frame_supplied: bool = false
var _error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	if not _assets_configured:
		var admitted: Dictionary = configure_assets({})
		if not admitted.ok:
			_error = admitted.error
			if not Engine.is_editor_hint():
				push_error(_error)
			return
	if not _frame_supplied:
		show_editor_projection()


## One initialization batch. Runtime can share the frontend's native font
## resources and decoded FEBack frames; standalone editing uses these same
## public recipes and a frozen first frame. Private pixels are never stored.
func configure_assets(paths: Dictionary, fonts: Dictionary = {}, shared_frames: Array = []) -> Dictionary:
	for key: Variant in paths:
		if not key is String or not paths[key] is String:
			return _failure("ArgumentException", "Debriefing asset routes require string paths.")
	for key: String in ["body_font", "title_font"]:
		if fonts.has(key) and not fonts[key] is AtlasFont:
			return _failure("ArgumentException", "Debriefing font batches require the production atlas resource.")
	var next_body: AtlasFont = fonts.get("body_font", body_font)
	var next_title: AtlasFont = fonts.get("title_font", title_font)
	for font: AtlasFont in [next_body, next_title]:
		if font == null:
			return _failure("InvalidDataException", "Debriefing is missing an authored font recipe.")
		var loaded: Dictionary = font.ensure_loaded()
		if not loaded.ok:
			return loaded
	if grade_textures.size() != GRADE_BYTES.size():
		return _failure("InvalidDataException", "Debriefing requires the six admitted grade recipes.")
	var next_grades: Array[Texture2D] = []
	for index: int in range(GRADE_BYTES.size()):
		var grade: Texture2D = _routed(grade_textures[index], paths.get("grade_" + char(GRADE_BYTES[index]).to_lower(), ""))
		if grade == null:
			return _failure("InvalidDataException", "Debriefing grade recipe is missing.")
		next_grades.append(grade)
	var metal: Texture2D = _routed(get_node("MetalRingOrigin/MetalRing").texture, paths.get("metal_ring", ""))
	var writing: Texture2D = _routed(get_node("Writing/Tile0").texture, paths.get("writing", ""))
	var bracket: Texture2D = _routed(get_node("Grade/BracketBody").texture, paths.get("symbol_bracket", ""))
	var recipes: Array[Texture2D] = [metal, writing, bracket]
	recipes.append_array(next_grades)
	for recipe: Texture2D in recipes:
		if recipe == null or not recipe.has_method("ensure_loaded"):
			return _failure("InvalidDataException", "Debriefing requires a private-page recipe.")
		var loaded: Dictionary = recipe.call("ensure_loaded")
		if not loaded.ok:
			return loaded
	var next_frames: Array = shared_frames.duplicate()
	for frame: Variant in next_frames:
		if not frame is Texture2D:
			return _failure("ArgumentException", "Debriefing FEBack frames require textures.")
	if next_frames.is_empty() and underlay != null:
		var loaded: Dictionary = underlay.load_frames(1)
		if not loaded.ok:
			return loaded
		next_frames = loaded.frames
	body_font = next_body
	title_font = next_title
	grade_textures = next_grades
	_frames = next_frames
	get_node("MetalRingOrigin/MetalRing").texture = metal
	for tile: TextureRect in get_node("Writing").get_children():
		tile.texture = writing
	get_node("Grade/BracketBody").texture = bracket
	get_node("Grade/BracketShadow").texture = bracket
	_assets_configured = true
	if not _snapshot.is_empty():
		_apply_projection()
	return {"ok": true}


static func _routed(source: Texture2D, path: String) -> Texture2D:
	if source == null:
		return null
	var result: Texture2D = source.duplicate(true)
	if not path.is_empty():
		result.set("source_path", path)
	return result


## One host call carries this page's detached projection and shared clock.
## Presentation never applies career updates or starts a gameplay session.
func set_frame(snapshot: Dictionary, fallback_level_name: Variant, seconds: float) -> Dictionary:
	var admitted: Dictionary = _admit(snapshot, fallback_level_name)
	if not admitted.ok:
		return admitted
	_frame_supplied = true
	var next: Dictionary = admitted.value
	if _snapshot != next.snapshot or _level_name != next.level_name:
		_snapshot = next.snapshot
		_level_name = next.level_name
		if _assets_configured:
			_apply_projection()
	var video: TextureRect = get_node("Underlay/Video")
	video.texture = null if _frames.is_empty() else _frames[Underlay.frame_index(seconds, _frames.size())]
	return {"ok": true}


func show_editor_projection() -> Dictionary:
	if editor_projection == null:
		return _failure("InvalidDataException", "Debriefing editor projection is missing.")
	var result: Dictionary = set_frame(editor_projection.snapshot(), editor_projection.fallback_level_name, 0.0)
	_frame_supplied = false
	return result


func _editor_projection_changed() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied):
		show_editor_projection()


func view_snapshot() -> Dictionary:
	return {"projection": _snapshot.duplicate(true), "level_name": _level_name.duplicate()}


func _apply_projection() -> void:
	get_node("Report/LevelName").bind(_level_name, title_font)
	get_node("Report/Labels/MissionStatus").bind(LABELS[0] + ": ", body_font)
	get_node("Report/Labels/Primary").bind(LABELS[1] + ": ", body_font)
	get_node("Report/Labels/SecondaryMotion/Secondary").bind(LABELS[2] + ": ", body_font)
	var width: float = maxf(body_font.measure(LABELS[0]), maxf(body_font.measure(LABELS[1]), body_font.measure(LABELS[2])))
	get_node("Report/ValuesOrigin").position.x = F.value(F.value(130.0 + width) + 20.0)
	var status: int = _snapshot.mission_status
	var status_text: String = "Victory" if status == 2 else ("Defeat" if status == 1 else "Aborted")
	var status_color: Color = _color(0xff3fff2f if status == 2 else (0xffff3f1f if status == 1 else 0xff3f3f3f))
	get_node("Report/ValuesOrigin/Layout/MissionStatus").bind(status_text, body_font)
	get_node("Report/ValuesOrigin/Layout/MissionStatus").set_tint(status_color)
	for name: String in ["Primary", "Secondary"]:
		var primary: bool = name == "Primary"
		var summary: int = _snapshot.primary_objectives if primary else _snapshot.secondary_objectives
		var label: BitmapLabel = get_node("Report/Labels/Primary" if primary else "Report/Labels/SecondaryMotion/Secondary")
		var value: BitmapLabel = get_node("Report/ValuesOrigin/Layout/Primary" if primary else "Report/ValuesOrigin/Layout/SecondaryMotion/Secondary")
		label.visible = summary != 0
		value.visible = summary != 0
		value.bind("Complete" if summary == 1 else "Incomplete", body_font)
		value.set_tint(_color(0xff3fff2f if summary == 1 else 0xffff3f1f))
	var secondary_offset: float = -16.0 if _snapshot.primary_objectives == 0 else 0.0
	get_node("Report/Labels/SecondaryMotion").position.y = secondary_offset
	get_node("Report/ValuesOrigin/Layout/SecondaryMotion").position.y = secondary_offset
	get_node("Grade").visible = _snapshot.grade_byte != null
	get_node("Report/GradeLabel").visible = _snapshot.grade_byte != null
	get_node("Report/GradeLabel").bind("Grade:", title_font)
	if _snapshot.grade_byte != null:
		var grade: Texture2D = grade_textures[GRADE_BYTES.find(_snapshot.grade_byte)]
		get_node("Grade/LetterShadow").texture = grade
		get_node("Grade/LetterBody").texture = grade
	get_node("Header/Title").bind("DEBRIEFING", title_font)


static func _admit(snapshot: Dictionary, fallback_level_name: Variant) -> Dictionary:
	for key: String in ["world_finished", "mission_status", "primary_objectives", "secondary_objectives", "new_goodie_count"]:
		if not snapshot.has(key) or not Values.is_int32(snapshot[key]):
			return _failure("ArgumentException", "Debriefing projection requires signed32 field: " + key)
	if not snapshot.has("first_goodie") or not snapshot.first_goodie is bool or not snapshot.has("grade_byte"):
		return _failure("ArgumentException", "Debriefing projection requires its grade and goodie fields.")
	if snapshot.grade_byte != null and (not snapshot.grade_byte is int or snapshot.grade_byte < 0 or snapshot.grade_byte > 255):
		return _failure("ArgumentException", "Debriefing grade must be a byte or null.")
	if snapshot.grade_byte != null and not snapshot.grade_byte in GRADE_BYTES:
		return _failure("InvalidDataException", "Retail debriefing has no grade surface for byte 0x%02X." % snapshot.grade_byte)
	var fallback: Dictionary = Text.units(fallback_level_name)
	if not fallback.ok or fallback.value == null:
		return _failure("ArgumentException", "Debriefing fallback level name requires UTF-16 text.")
	var name: Variant = WorldStrings.level_name(snapshot.world_finished)
	return {"ok": true, "value": {"snapshot": snapshot.duplicate(true),
		"level_name": AtlasFont.units(name).duplicate() if name != null else fallback.value.duplicate()}}


static func _color(word: int) -> Color:
	# Retained RetailColor models the released MODULATE2X byte product.
	return Color(_modulate2x((word >> 16) & 255), _modulate2x((word >> 8) & 255),
		_modulate2x(word & 255), F.value(((word >> 24) & 255) / 255.0))


static func _modulate2x(channel: int) -> float:
	return F.value(mini(255, (channel * 255) >> 7) / 255.0)


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
