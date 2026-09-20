# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends MeshInstance3D
## Private converted geometry is stored only by an explicitly private bake or
## an existing ignored external mesh. Public previews remain transient.
@export_storage var _private_bake: bool = false


func _ready() -> void:
	set_process(false)
	if mesh != null and mesh.resource_path.begins_with("res://Assets/Level100/Scenes/"):
		_private_bake = true


func _validate_property(property: Dictionary) -> void:
	if property.name == "mesh" and not _private_bake:
		var resource: Mesh = mesh
		if resource == null or not resource.resource_path.begins_with("res://Assets/Level100/Scenes/"):
			property.usage = int(property.usage) & ~PROPERTY_USAGE_STORAGE
