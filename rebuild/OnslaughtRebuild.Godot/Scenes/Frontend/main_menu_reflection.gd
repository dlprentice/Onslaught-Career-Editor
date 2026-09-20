# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Node2D
## Existing ONE/ONE title sheen; the measured scroll phase and 29.95 px/s rate
## remain the same bounded reconstruction. The shader is the unchanged C# code.
const Laws = preload("res://Client/main_menu_laws.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var texture: Texture2D
@export var reflection: Texture2D
var _material: ShaderMaterial
var _scroll: float = 0.0


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	_prepare_material()


func configure_textures(logo: Texture2D, page: Texture2D) -> void:
	texture = logo
	reflection = page
	_prepare_material()
	queue_redraw()


func _prepare_material() -> void:
	if _material == null and material is ShaderMaterial:
		_material = material.duplicate(false)
		material = _material
	if _material != null:
		_material.set_shader_parameter("reflection", reflection)
		_material.set_shader_parameter("gain", F.value(126.0 / 255.0))
		_material.set_shader_parameter("scroll", _scroll)


func set_frame(seconds: float, logo: Control) -> void:
	_scroll = Laws.reflection_scroll(seconds)
	_prepare_material()
	var ratio: Vector2 = logo.size / Vector2(512.0, 256.0)
	var source_to_logo := Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -Vector2(64.0, 2.0) * ratio)
	transform = get_parent().get_global_transform_with_canvas().affine_inverse() * logo.get_global_transform_with_canvas() * source_to_logo
	queue_redraw()


func view_snapshot() -> Dictionary:
	return {"scroll": _scroll, "gain": F.value(126.0 / 255.0), "transform": transform}


func _draw() -> void:
	if texture != null:
		draw_texture_rect(texture, Rect2(64.0, 2.0, 512.0, 256.0), false, Color.WHITE)
