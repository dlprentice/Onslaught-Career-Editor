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
	top_level = true
	z_as_relative = false
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
	# The retained renderer submits this shader at the canvas root. A nested
	# shader item produces different pixels at fractional window scales even
	# with the same final matrix. Top-level submission preserves that path;
	# the real authored title still supplies its complete pose and dimensions.
	transform = logo.get_global_transform() * source_to_logo
	var ancestors: Array[CanvasItem] = []
	var ancestor: Node = get_parent()
	while ancestor is CanvasItem:
		ancestors.push_front(ancestor)
		if ancestor.top_level or not ancestor.z_as_relative: break
		ancestor = ancestor.get_parent()
	var inherited_z: int = 0
	for item: CanvasItem in ancestors:
		inherited_z = clampi(inherited_z + item.z_index, RenderingServer.CANVAS_ITEM_Z_MIN, RenderingServer.CANVAS_ITEM_Z_MAX)
	z_index = inherited_z
	queue_redraw()


func view_snapshot() -> Dictionary:
	return {"scroll": _scroll, "gain": F.value(126.0 / 255.0), "transform": transform}


func _draw() -> void:
	if texture != null:
		draw_texture_rect(texture, Rect2(64.0, 2.0, 512.0, 256.0), false, Color.WHITE)


func _validate_property(property: Dictionary) -> void:
	# These values follow the title, rather than becoming a second saved pose.
	if property.name in ["position", "rotation", "scale", "skew", "z_index"]:
		property.usage = (property.usage & ~PROPERTY_USAGE_STORAGE) | PROPERTY_USAGE_EDITOR | PROPERTY_USAGE_READ_ONLY
