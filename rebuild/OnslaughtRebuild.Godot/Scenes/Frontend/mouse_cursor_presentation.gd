# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Native RetailFrontendFlow.Cursor presentation. The 2026-07-27 d3d9 sweep
## (local-lab/D3D9-FULL-SWEEP-2026-07-27.md) measured the last interactive-page
## draw: 32-square quad, zero hotspot, 124-square source and literal white.
## Boot pages 2-4 belong to ClickToStart; boot-first/loading have no cursor.
## Startup video/splash/black/finished have no producer in the 2026-07-28 FMV
## log. Parent visibility retains that separation; no media owner is added.
## Asset identity: mouse.tga, AYA SHA256
## 366021def699de220ad018c40250eefaccaab356c6c5d93fe0aa1b7f5302354c,
## 128-square DXT2 with eight stored mip levels.
## The native recipe converts it to RGBA8 through the existing curated loader.
## The component sits beside Stage so GUI pixel snapping cannot round its
## fractional fit. The configured runtime source supplies viewport size and,
## only when requested, the live pointer; captured positions remain explicit.
## Frozen/editor use never reads it; no mode, movement or capture is owned here.
const CursorTexture = preload("res://Scenes/Frontend/mouse_cursor_texture.gd")
const Session = preload("res://Client/frontend_session.gd")
const Values = preload("res://Core/retail_career_values.gd")
@export var editor_screen: int = Session.Screen.CLICK_TO_START:
	set(value): editor_screen = value; _refresh_preview()
@export var editor_cursor_position: Vector2 = Vector2.ZERO:
	set(value): editor_cursor_position = value; _refresh_preview()
var _facts: Dictionary = {}
var _frame_supplied: bool = false
var _assets_configured: bool = false
var _error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	if not _assets_configured:
		var admitted: Dictionary = configure_assets()
		if not admitted.ok:
			_error = admitted.error
			if not Engine.is_editor_hint(): push_error(_error)
			return
	if not _frame_supplied: show_editor_preview()


func configure_assets(paths: Dictionary = {}) -> Dictionary:
	for key: Variant in paths:
		if not key is String or key != "cursor" or not paths[key] is String:
			return _failure("Mouse cursor accepts only its cursor string route.")
	var recipe: CursorTexture = get_node("Quad").texture as CursorTexture
	if recipe == null: return _failure("Mouse cursor requires its production texture recipe.")
	if paths.has("cursor") and paths.cursor != recipe.source_path:
		recipe = recipe.duplicate(true)
		recipe.source_path = paths.cursor
	# Deliberately do not load here. The original layer first attempts the asset
	# from an eligible _Draw, and a missing file is retried by a later draw.
	get_node("Quad").texture = recipe
	_assets_configured = true
	_error = ""
	return {"ok": true}


func set_frame(facts: Dictionary) -> Dictionary:
	if not Values.is_int32(facts.get("screen")):
		return _failure("Mouse cursor screen requires the host's signed32 enum value.")
	if not facts.has("cursor_position") or (facts.cursor_position != null and not facts.cursor_position is Vector2):
		return _failure("Mouse cursor requires a stage Vector2 or explicitly configured live source.")
	if facts.cursor_position == null and not get_node("Quad").can_read_live_pointer():
		return _failure("Mouse cursor live position requires an in-tree runtime source.")
	if not _assets_configured: return _failure("Mouse cursor recipe has not been admitted.")
	_facts = {"screen": facts.screen, "cursor_position": facts.cursor_position}
	_frame_supplied = true
	get_node("Quad").bind(facts.cursor_position, accepts_screen(facts.screen))
	return {"ok": true}


func configure_live_pointer(source: Control) -> Dictionary:
	if Engine.is_editor_hint() or source == null:
		return _failure("Live pointer source is available only through explicit runtime host configuration.")
	get_node("Quad").configure_live_pointer(source)
	return {"ok": true}


static func accepts_screen(screen: int) -> bool:
	# Unknown signed enum values retain the original exclusion predicate.
	return screen not in [Session.Screen.LOADING, Session.Screen.INTRO_CUTSCENE, Session.Screen.GAMEPLAY]


func show_editor_preview() -> Dictionary:
	var result: Dictionary = set_frame({"screen": editor_screen, "cursor_position": editor_cursor_position})
	if result.ok: _frame_supplied = false
	return result


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


func _refresh_preview() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied): show_editor_preview()


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
