# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production Quit confirmation, ported from RetailFrontendFlow.DrawQuitConfirm
## and RetailFeMessBox.cs. Width/center are pinned there; height 140 remains an
## explicit reconstruction. FEMessBox source and a retail Quit capture remain
## unavailable. English prompt/Yes/No retain the existing localization gap.
## This view never accepts input, advances a session, plays sound or quits.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Values = preload("res://Core/retail_career_values.gd")
# Localization__GetStringById(0xe4): the English table in BEA.exe, not english.dat.
const PROMPT: String = "Are you sure you want to quit the game?"
const YES_LABEL: String = "Yes"
const NO_LABEL: String = "No"
@export var body_font: AtlasFont:
	set(value):
		body_font = value
		if is_node_ready(): get_node("Dialog/Prompt").atlas_font = value
@export var choice_font: AtlasFont:
	set(value):
		choice_font = value
		if is_node_ready():
			get_node("Dialog/Yes/Label").atlas_font = value
			get_node("Dialog/No/Label").atlas_font = value
@export_enum("No", "Yes") var editor_selected_index: int = 0:
	set(value):
		editor_selected_index = value
		if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied): show_editor_preview()
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
	if not _frame_supplied: show_editor_preview()


func configure_assets(paths: Dictionary = {}, shared_body: Resource = null, shared_choice: Resource = null) -> Dictionary:
	for key: Variant in paths:
		if not key is String or key not in ["blank", "body_font", "choice_font"] or not paths[key] is String:
			return _failure("Quit confirmation accepts only blank/body_font/choice_font string routes.")
	var body: Resource = shared_body if shared_body != null else body_font
	var choice: Resource = shared_choice if shared_choice != null else choice_font
	if not body is AtlasFont or not choice is AtlasFont:
		return _failure("Quit confirmation requires its production frontend font recipes.")
	if body.page == null or choice.page == null:
		return _failure("Quit confirmation font has no page recipe.")
	for font: AtlasFont in [body, choice]:
		if not font.page.has_method("ensure_loaded") or not font.page.get("source_path") is String:
			return _failure("Quit confirmation font requires its production page recipe.")
	var loaded: Dictionary = _font_recipe(body, paths.get("body_font", body.page.source_path))
	if not loaded.ok: return loaded
	var next_body: AtlasFont = loaded.value
	loaded = _font_recipe(choice, paths.get("choice_font", choice.page.source_path))
	if not loaded.ok: return loaded
	var next_choice: AtlasFont = loaded.value
	var blank: Texture2D = get_node("Dialog/Panel").texture
	if blank == null or not blank.has_method("ensure_loaded"):
		return _failure("Quit confirmation is missing its 16x16 blank recipe.")
	if paths.has("blank") and paths.blank != blank.get("source_path"):
		blank = blank.duplicate(true)
		blank.set("source_path", paths.blank)
	loaded = blank.call("ensure_loaded")
	if not loaded.ok: return loaded
	body_font = next_body
	choice_font = next_choice
	get_node("Dialog/Panel").texture = blank
	get_node("Dialog/Prompt").bind(PROMPT, body_font)
	for pair: Array in [["Yes", YES_LABEL], ["No", NO_LABEL]]:
		get_node("Dialog/" + pair[0] + "/Highlight").texture = blank
		get_node("Dialog/" + pair[0] + "/Label").bind(pair[1], choice_font)
	_assets_configured = true
	_error = ""
	return {"ok": true}


func set_frame(facts: Dictionary) -> Dictionary:
	if not facts.has("selected_index") or not Values.is_int32(facts.selected_index) or facts.selected_index < 0 or facts.selected_index > 1:
		return _failure("Quit confirmation requires selected_index 0 (No) or 1 (Yes).")
	if not _assets_configured: return _failure("Quit confirmation assets have not been admitted.")
	_facts = {"selected_index": facts.selected_index}
	_frame_supplied = true
	get_node("Dialog/Yes/Highlight").set_selected(facts.selected_index == 1)
	get_node("Dialog/No/Highlight").set_selected(facts.selected_index == 0)
	return {"ok": true}


func hit_test(design_point: Vector2) -> int:
	# Original overlap order is No first, then Yes, using full 400x32 rows.
	if get_node("Dialog/No").contains_design_point(design_point, self): return 0
	if get_node("Dialog/Yes").contains_design_point(design_point, self): return 1
	return -1


func show_editor_preview() -> Dictionary:
	var result: Dictionary = set_frame({"selected_index": editor_selected_index})
	if result.ok: _frame_supplied = false
	return result


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


static func _font_recipe(source: AtlasFont, path: String) -> Dictionary:
	if source.page == null: return _failure("Quit confirmation font has no page recipe.")
	var font: AtlasFont = source
	if path != source.page.get("source_path"):
		font = source.duplicate(true)
		font.page.set("source_path", path)
	var loaded: Dictionary = font.ensure_loaded()
	return {"ok": true, "value": font} if loaded.ok else loaded


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
