# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production FEP_DEVSELECT presentation from RetailFrontendFlow.DrawDevSelect.
## Panel/guides were measured from the pristine 640x480 choose-game-name capture
## (local-lab/retail-reference-pristine/choose-game-name/choose-game-name-640x480.png).
## The shared Font22 title at scale1 retains the 2026-07-26 glyph-run correction.
## Header endcaps FET3_HEADER_BRACKET1 and the blue Forseti emblem remain missing;
## no replacement art or unevidenced transition/cursor is introduced here.
## This view owns neither career discovery/persistence nor input/session/audio.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const NameLabel = preload("res://Scenes/Frontend/career_name_label.gd")
const Values = preload("res://Core/retail_career_values.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const TITLE: String = "CHOOSE GAME NAME"
const ROW_COUNT: int = 11
@export var body_font: AtlasFont:
	set(value): body_font = value; _bind_fonts()
@export var title_font: AtlasFont:
	set(value): title_font = value; _bind_fonts()
@export var editor_career_names: PackedStringArray = PackedStringArray():
	set(value): editor_career_names = value; _refresh_preview()
@export var editor_selected_career_index: int = -1:
	set(value): editor_selected_career_index = value; _refresh_preview()
@export var editor_game_name: String = "BEA 1":
	set(value): editor_game_name = value; _refresh_preview()
@export var editor_game_name_is_fresh: bool = true:
	set(value): editor_game_name_is_fresh = value; _refresh_preview()
@export var editor_background_seconds: float = 0.0:
	set(value): editor_background_seconds = value; _refresh_preview()
var _facts: Dictionary = {}
var _frame_supplied: bool = false
var _assets_configured: bool = false
var _error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	if not _assets_configured:
		var result: Dictionary = configure_assets()
		if not result.ok:
			_error = result.error
			if not Engine.is_editor_hint(): push_error(_error)
			return
	_bind_fonts()
	if not _frame_supplied: show_editor_preview()


func configure_assets(paths: Dictionary = {}, fonts: Dictionary = {}, shared_frames: Array = []) -> Dictionary:
	for key: Variant in paths:
		if not key is String or key not in ["bracket", "arrow"] or not paths[key] is String:
			return _failure("Career presentation accepts only bracket/arrow string routes.")
	for key: Variant in fonts:
		if not key is String or key not in ["body_font", "title_font"] or not fonts[key] is AtlasFont:
			return _failure("Career presentation accepts only shared body_font/title_font recipes.")
	var body: AtlasFont = fonts.get("body_font", body_font)
	var title: AtlasFont = fonts.get("title_font", title_font)
	for font: AtlasFont in [body, title]:
		if font == null or font.page == null or not font.page.has_method("ensure_loaded") or not font.page.get("source_path") is String:
			return _failure("Career presentation font requires its production page recipe.")
		var admitted: Dictionary = font.ensure_loaded()
		if not admitted.ok: return admitted
	var bracket: Dictionary = _texture_recipe(get_node("Decoration/Body").texture, paths.get("bracket"))
	if not bracket.ok: return bracket
	var arrow: Dictionary = _texture_recipe(get_node("Navigation/Forward").texture, paths.get("arrow"))
	if not arrow.ok: return arrow
	var background: Dictionary = get_node("Background").prepare_frames(shared_frames)
	if not background.ok: return background
	# All admissions precede changes to the live production tree.
	body_font = body
	title_font = title
	for path: String in ["Decoration/Shadow", "Decoration/Body"]: get_node(path).texture = bracket.value
	for path: String in ["Navigation/Back", "Navigation/Forward"]: get_node(path).texture = arrow.value
	get_node("Background").bind_frames(background.frames)
	get_node("Header/Title").bind(Text.units(TITLE).value)
	_assets_configured = true
	_error = ""
	_bind_fonts()
	return {"ok": true, "missing_background": background.missing}


func set_frame(facts: Dictionary) -> Dictionary:
	if not facts.get("career_names") is Array: return _failure("Career names require an array of raw UTF-16 names.")
	var names: Array = []
	for index: int in range(facts.career_names.size()):
		var raw: Variant = facts.career_names[index]
		# The old renderer stops before visiting row11. Session descriptor names
		# remain nullable; an offscreen null stays null and is never dereferenced.
		if raw == null and index >= ROW_COUNT:
			names.append(null)
			continue
		var admitted: Dictionary = _raw_units(raw)
		if not admitted.ok: return admitted
		names.append(admitted.value)
	if not Values.is_int32(facts.get("selected_career_index")) or facts.selected_career_index < -1 or facts.selected_career_index >= names.size():
		return _failure("Career selection must be -1 or an existing row index.")
	var name: Dictionary = _raw_units(facts.get("game_name"))
	if not name.ok: return name
	if typeof(facts.get("game_name_is_fresh")) != TYPE_BOOL:
		return _failure("Career freshness must be Boolean.")
	if typeof(facts.get("background_seconds")) != TYPE_FLOAT or not is_finite(facts.background_seconds):
		return _failure("Career background time must be a finite floating-point value.")
	if not _assets_configured: return _failure("Career presentation assets have not been admitted.")
	var width: Dictionary = NameLabel.checked_name_width(name.value, body_font.glyph_widths(), get_node("Name/Label").glyph_scale.x)
	if not width.ok: return width
	# Unknown facts, including Object/Resource values, never enter the snapshot.
	_facts = {"career_names": names, "selected_career_index": facts.selected_career_index,
		"game_name": name.value, "game_name_is_fresh": facts.game_name_is_fresh,
		"background_seconds": facts.background_seconds}
	_frame_supplied = true
	for index: int in range(ROW_COUNT):
		get_node("List/Rows/Row%02d" % index).bind(names[index] if index < names.size() else PackedInt32Array(),
			index < names.size(), index == facts.selected_career_index)
	get_node("Name/Label").bind(name.value)
	get_node("Name/Highlight").set_fresh(facts.game_name_is_fresh)
	get_node("Background").set_frame(1.0, facts.background_seconds)
	return {"ok": true}


func hit_test(design_point: Vector2) -> int:
	# The retained host route only recognizes Back and Confirm. It never selects
	# a career row by clicking. Preserve Back's priority when authored targets overlap.
	if get_node("Navigation/Back").contains_design_point(design_point, self): return 1
	if get_node("Navigation/Forward").contains_design_point(design_point, self) or get_node("Name").contains_design_point(design_point, self): return 2
	return 0


func measure_name_extent(raw_units: PackedInt32Array) -> int:
	# Original host input helper: Font22, swapped inverted punctuation, unchecked
	# Int32 width += glyph+1. There is no centering subtraction or scale here.
	if title_font == null or not _raw_units(raw_units).ok: return 0
	var widths: PackedInt32Array = title_font.glyph_widths()
	return NameLabel.unchecked_name_extent(raw_units, widths) if widths.size() == 256 else 0


func show_editor_preview() -> Dictionary:
	var names: Array[PackedInt32Array] = []
	for name: String in editor_career_names: names.append(Text.units(name).value)
	var result: Dictionary = set_frame({"career_names": names, "selected_career_index": editor_selected_career_index,
		"game_name": Text.units(editor_game_name).value, "game_name_is_fresh": editor_game_name_is_fresh,
		"background_seconds": editor_background_seconds})
	if result.ok: _frame_supplied = false
	return result


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


func _refresh_preview() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied): show_editor_preview()


func _bind_fonts() -> void:
	if not is_node_ready(): return
	get_node("Header/Title").atlas_font = title_font
	get_node("Name/Label").atlas_font = body_font
	for index: int in range(ROW_COUNT): get_node("List/Rows/Row%02d" % index).atlas_font = body_font


static func _texture_recipe(source: Texture2D, route: Variant) -> Dictionary:
	if source == null or not source.has_method("ensure_loaded") or not source.get("source_path") is String:
		return _failure("Career presentation texture requires its production page recipe.")
	var texture: Texture2D = source
	if route != null and route != source.get("source_path"):
		texture = source.duplicate(true)
		texture.set("source_path", route)
	var loaded: Dictionary = texture.call("ensure_loaded")
	return {"ok": true, "value": texture} if loaded.ok else loaded


static func _raw_units(value: Variant) -> Dictionary:
	if not value is PackedInt32Array: return _failure("Career text requires raw PackedInt32Array UTF-16 units.")
	var result: Dictionary = Text.units(value)
	return result if result.ok else _failure(result.error)


static func _failure(message: String) -> Dictionary:
	return Values.failure("InvalidDataException", message)
