# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Three existing background passes, backed by the shared native strip recipe.
## Missing strip keeps the current opaque clear+darkener fallback.
const Underlay = preload("res://Scenes/Frontend/frontend_underlay.gd")
const Laws = preload("res://Client/main_menu_laws.gd")
@export var recipe: Underlay
@export var source_rect: Rect2 = Rect2(0, 0, 640, 480)
var _frames: Array = []
var _alpha: float = 1.0
var _seconds: float = 0.0


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func configure(shared: Underlay = null) -> Dictionary:
	var selected: Underlay = shared if shared != null else recipe
	if selected == null: return {"ok": false, "error_type": "InvalidDataException", "error": "Main Menu is missing its underlay recipe."}
	var loaded: Dictionary = selected.load_frames(1 if Engine.is_editor_hint() else 2147483647)
	if not loaded.ok: return loaded
	recipe = selected
	_frames = loaded.frames.duplicate()
	queue_redraw()
	return {"ok": true, "missing": loaded.missing}


func set_frame(transition: float, seconds: float) -> void:
	_alpha = Laws.underlay_alpha(transition)
	_seconds = seconds
	queue_redraw()


func view_snapshot() -> Dictionary:
	return {"alpha": _alpha, "frame": Underlay.frame_index(_seconds, _frames.size()), "frame_count": _frames.size()}


func _draw() -> void:
	if source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	var ratio: Vector2 = size / source_rect.size
	draw_set_transform_matrix(Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio))
	draw_rect(Rect2(0.0, 0.0, 640.0, 480.0), Underlay.CLEAR)
	draw_rect(Rect2(-40.0, -3.0, 720.0, 486.0), Underlay.DARKENER)
	if not _frames.is_empty() and not _alpha <= 0.0:
		draw_texture_rect(_frames[Underlay.frame_index(_seconds, _frames.size())], Rect2(0.0, 0.0, 640.0, 480.0), false, Color(1.0, 1.0, 1.0, _alpha))
