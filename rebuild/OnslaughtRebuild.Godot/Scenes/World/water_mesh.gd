# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends MeshInstance3D
## A normal inspectable mesh/material slot with private-derived storage guarded.
## The authored base material contains only shader and virtual texture recipes.
@export var base_material: ShaderMaterial
@export_storage var _private_bake: bool = false


func _ready() -> void:
	set_process(false)
	retain_private_origin()


func retain_private_origin() -> void:
	if mesh != null and mesh.resource_path.begins_with("res://Assets/Level100/Scenes/"):
		_private_bake = true


func enable_private_bake() -> void:
	_private_bake = true
	notify_property_list_changed()


func _validate_property(property: Dictionary) -> void:
	if property.name not in ["mesh", "material_override"] or _private_bake:
		return
	var resource: Resource = get(property.name)
	if resource == null or not resource.resource_path.begins_with("res://Assets/Level100/Scenes/"):
		property.usage = int(property.usage) & ~PROPERTY_USAGE_STORAGE
