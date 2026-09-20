# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production Loading page. Session/launch timing remain in the frontend owner.
## The fixed bar is the existing documented bbox fallback, not invented progress.
## Original measurements and omissions remain in Tests/LoadingReference.cs.
## The caption's Node2D origin deliberately preserves source y=393.5. The old
## RetailFrontendPart Control proxy snapped that half-pixel away: its composed
## image is therefore not identical. All four tested viewport sizes match the
## retained DrawLoading source; no viewport snapping policy has been changed.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const CaptionSource = preload("res://Scenes/Frontend/loading_strings.gd")
const FrozenProgress = preload("res://Scenes/Frontend/loading_preview.gd")
const Values = preload("res://Core/retail_career_values.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const CAPTION_PARTS: Array[String] = ["OutlineBottomLeft", "OutlineBottomRight", "OutlineTopLeft", "OutlineTopRight", "Body"]
@export var title_font: AtlasFont
@export var caption_source: CaptionSource
@export var editor_progress: FrozenProgress:
	set(value):
		if editor_progress != null and editor_progress.changed.is_connected(_editor_changed):
			editor_progress.changed.disconnect(_editor_changed)
		editor_progress = value
		if editor_progress != null:
			editor_progress.changed.connect(_editor_changed)
		if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied):
			show_editor_progress()
## Deliberate enhanced text applies consistently to all four outlines and body.
@export var override_caption: bool = false:
	set(value):
		override_caption = value
		_refresh_caption()
@export var caption: String = "Loading...":
	set(value):
		caption = value
		_refresh_caption()
var _caption := PackedInt32Array()
var _facts: Dictionary = {}
var _assets_configured: bool = false
var _frame_supplied: bool = false
var _error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	if not _assets_configured:
		var result: Dictionary = configure_assets({})
		if not result.ok:
			_error = result.error
			if not Engine.is_editor_hint():
				push_error(_error)
			return
	if not _frame_supplied:
		show_editor_progress()


## The host supplies its already-admitted font and caption once. Standalone
## editing reads the identical public recipes and verified private receipt.
func configure_assets(paths: Dictionary, shared_font: AtlasFont = null, admitted_caption: Variant = null) -> Dictionary:
	for key: Variant in paths:
		if not key is String or not paths[key] is String:
			return _failure("ArgumentException", "Loading asset routes require string paths.")
	var next_caption: Dictionary
	if admitted_caption == null:
		if caption_source == null:
			return _failure("InvalidDataException", "Loading is missing its caption receipt.")
		next_caption = caption_source.load_caption()
	else:
		next_caption = _admit_caption(admitted_caption)
	if not next_caption.ok:
		return next_caption
	# The retained host admits localization before touching its texture pages.
	var next_font: AtlasFont = shared_font if shared_font != null else title_font
	if next_font == null:
		return _failure("InvalidDataException", "Loading is missing its title-font recipe.")
	var loaded: Dictionary = next_font.ensure_loaded()
	if not loaded.ok:
		return loaded
	var background: Texture2D = get_node("Background").texture
	if background == null or not background.has_method("ensure_loaded"):
		return _failure("InvalidDataException", "Loading is missing its production background recipe.")
	background = background.duplicate(true)
	if paths.has("background"):
		background.set("source_path", paths.background)
	loaded = background.call("ensure_loaded")
	if not loaded.ok:
		return loaded
	title_font = next_font
	_caption = next_caption.value.duplicate()
	get_node("Background").texture = background
	_assets_configured = true
	_refresh_caption()
	return {"ok": true}


func set_frame(facts: Dictionary, text: Variant) -> Dictionary:
	if not facts.has("loading_frames") or not Values.is_int32(facts.loading_frames):
		return _failure("ArgumentException", "Loading frame count requires a signed32 value.")
	for key: String in ["launch_requested", "ready"]:
		if not facts.has(key) or not facts[key] is bool:
			return _failure("ArgumentException", "Loading requires Boolean host fact: " + key)
	var admitted: Dictionary = _admit_caption(text)
	if not admitted.ok:
		return admitted
	_facts = facts.duplicate(true)
	_frame_supplied = true
	if _caption != admitted.value:
		_caption = admitted.value.duplicate()
		_refresh_caption()
	return {"ok": true}


func show_editor_progress() -> Dictionary:
	if editor_progress == null:
		return _failure("InvalidDataException", "Loading editor progress fixture is missing.")
	var result: Dictionary = set_frame(editor_progress.snapshot(), _caption)
	_frame_supplied = false
	return result


func _editor_changed() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied):
		show_editor_progress()


func _refresh_caption() -> void:
	if not _assets_configured or not has_node("Caption"):
		return
	var displayed: PackedInt32Array = Text.units(caption).value if override_caption else _caption
	for part: String in CAPTION_PARTS:
		get_node("Caption/" + part).bind(displayed, title_font)


func view_snapshot() -> Dictionary:
	return {"facts": _facts.duplicate(true), "caption": _caption.duplicate()}


static func _admit_caption(value: Variant) -> Dictionary:
	var admitted: Dictionary = Text.units(value)
	if not admitted.ok or admitted.value == null:
		return _failure("ArgumentException", "Loading caption requires non-null UTF-16 text.")
	return {"ok": true, "value": admitted.value.duplicate()}


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
