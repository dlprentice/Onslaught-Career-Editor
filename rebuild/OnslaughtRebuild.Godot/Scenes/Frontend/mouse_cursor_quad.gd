# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## Last frontend draw: posted stage coordinate is the unclamped top-left.
## This is plain MODULATE white, not the other frontend sprites' MODULATE2X.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var source_offset: Vector2 = Vector2.ZERO:
	set(value): source_offset = value; queue_redraw()
@export var quad_size: Vector2 = Vector2(32, 32):
	set(value): quad_size = value; queue_redraw()
@export var region: Rect2 = Rect2(0, 0, 124, 124):
	set(value): region = value; queue_redraw()
var _cursor_position: Variant = Vector2.ZERO
var _draw_enabled: bool = false
var _pointer_source: WeakRef
var _last_position: Vector2 = Vector2.ZERO
var _last_draw_live: bool = false
var _last_drawn: bool = false


func bind(cursor_position: Variant, enabled: bool) -> void:
	_cursor_position = cursor_position
	_draw_enabled = enabled
	visible = enabled
	queue_redraw()


func drawing_rect() -> Rect2:
	var position: Vector2 = _last_position if _cursor_position == null else _cursor_position
	return Rect2(position + source_offset, quad_size)


func draws_content() -> bool:
	return _draw_enabled and texture != null


func _draw() -> void:
	_last_drawn = false
	if not draws_content() or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	# Preserve the old draw phase: load first, then sample the posted position.
	# Missing optional assets do not sample a live pointer and retry next draw.
	var loaded: Dictionary = texture.call("ensure_loaded")
	if not loaded.ok: return
	_last_draw_live = _cursor_position == null
	if _last_draw_live:
		if not can_read_live_pointer(): return
		var source: Control = _pointer_source.get_ref() as Control
		_last_position = to_design_position(source.get_local_mouse_position(), source.size)
	else:
		_last_position = _cursor_position
	_last_drawn = true
	# The cursor is a viewport overlay, outside the GUI-snapped Stage. Retail's
	# old Node2D submitted this fit as a draw transform; putting it on a Control
	# ancestor rounds a fractional letterbox offset before the GPU sees it.
	var pose: Transform2D = source_transform()
	if _pointer_source != null:
		var source: Control = _pointer_source.get_ref() as Control
		if source != null and source.is_inside_tree(): pose = stage_fit(source.size) * pose
	draw_set_transform_matrix(pose)
	draw_texture_rect_region(texture, drawing_rect(), region, ink_color)


func configure_live_pointer(source: Control) -> void:
	_pointer_source = weakref(source)


func can_read_live_pointer() -> bool:
	if Engine.is_editor_hint() or _pointer_source == null: return false
	var source: Control = _pointer_source.get_ref() as Control
	return source != null and source.is_inside_tree()


func draw_snapshot() -> Dictionary:
	return {"drawn": _last_drawn, "live": _last_draw_live, "position": _last_position}


static func stage_fit(source_size: Vector2) -> Transform2D:
	# RetailFrontendFlow.DesignTransform, including each C# binary32 store.
	var scale: float = minf(F.value(source_size.x / 640.0), F.value(source_size.y / 480.0))
	var offset := Vector2(F.value(F.value(source_size.x - F.value(640.0 * scale)) * 0.5),
		F.value(F.value(source_size.y - F.value(480.0 * scale)) * 0.5))
	return Transform2D(Vector2(scale, 0.0), Vector2(0.0, scale), offset)


static func to_design_position(viewport_position: Vector2, source_size: Vector2) -> Vector2:
	# A canvas inverse changes the old half-open boundary rounding.
	var fit: Transform2D = stage_fit(source_size)
	return Vector2.ZERO if fit.x.x <= 0.0 else (viewport_position - fit.origin) / fit.x.x


func _validate_property(property: Dictionary) -> void:
	if property.name == "rectangle": property.usage = PROPERTY_USAGE_NONE
