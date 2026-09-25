# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Node3D
## The existing water presentation, shared by editor, importer and gameplay.
## No physics, input or autonomous time owner lives here. The current omitted
## late additive shoreline pass remains omitted: older provenance describes it,
## while the retained implementation/pixel guards reject the discarded model.
## This mechanical port does not resolve that discrepancy or claim new parity.
const Recipe = preload("res://Scenes/World/water_recipe.gd")
const WaterMesh = preload("res://Scenes/World/water_mesh.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Words = preload("res://Core/retail_float24.gd")
const CAUSTIC_PHASE_RADIANS_PER_SECOND: float = 1.0
const WAVE_SCROLL_PER_SECOND: float = 0.06
const SUN_GLINT_CENTER_HEIGHT_SCALE: float = 6.0
const SUN_GLINT_HALF_WIDTH_HEIGHT_SCALE: float = 2.0
const SUN_GLINT_HALF_LENGTH_HEIGHT_SCALE: float = 8.0
const CHILD_NAMES: Array[String] = ["RetailCameraRelativeWaterGrid", "RetailAuthoredShorelineBands", "RetailCameraRelativeWaterSunGlint"]

@export var source_recipe: Resource
var _configured: bool = false
var _caustic_phase: float = 0.0
var _main_wave_scroll: float = 0.0
var _direction: Vector3
var _water_height: float
var _metadata: Dictionary = {}
var _preview_error: String = ""


func _ready() -> void:
	set_process(false)
	_retain_nested_overrides()
	if Engine.is_editor_hint():
		var result: Dictionary = prepare_visual(false, {}, {}, "", "", true)
		_preview_error = "" if result.ok else result.error
		update_configuration_warnings()


func _notification(what: int) -> void:
	if what == NOTIFICATION_PARENTED:
		_retain_nested_overrides()


func _retain_nested_overrides() -> void:
	# The importer packs StaticWorld around this production scene instance.
	# Child Owner remains Water to retain that instance; the enclosing scene
	# must explicitly retain its changed child transforms/meshes/materials.
	# Otherwise Godot silently packs only Water's root properties. A public
	# transient preview never enables private overrides through this route.
	var parent: Node = get_parent()
	if not parent is Node3D or scene_file_path.is_empty():
		return
	for child_name: String in CHILD_NAMES:
		var child: Node = get_node_or_null(NodePath(child_name))
		if not child is WaterMesh or not child.get("_private_bake"):
			return
	parent.set_editable_instance(self, true)


func _get_configuration_warnings() -> PackedStringArray:
	return PackedStringArray() if _preview_error.is_empty() else PackedStringArray([_preview_error])


## Public preview and production configuration share every geometry/material
## definition. Retain mode validates the saved component without rebuilding it.
func prepare_visual(retain_saved: bool, metadata: Dictionary = {}, texture_bindings: Dictionary = {}, surface_path: String = "", surface_sha256: String = "", editor_preview: bool = false) -> Dictionary:
	if source_recipe == null or source_recipe.get_script() != Recipe:
		return _failure("The water requires its authored source recipe.")
	var children: Array[WaterMesh] = []
	for child_name: String in CHILD_NAMES:
		var node: Node = get_node_or_null(NodePath(child_name))
		if not node is WaterMesh or node.base_material == null:
			return _failure("The water scene is missing an authored mesh/material component: " + child_name)
		children.append(node)
		if editor_preview:
			node.retain_private_origin()
	# Editor inspection of an imported scene retains all saved resources and
	# authored transforms. A public scene creates only transient derived content.
	var saved: bool = retain_saved or (editor_preview and children.all(func(node: WaterMesh) -> bool: return node.mesh != null and node.material_override != null))
	if saved:
		for node: WaterMesh in children:
			if not node.mesh is ArrayMesh or not node.material_override is ShaderMaterial:
				return _failure("The imported water has no saved mesh/material.")
		if children[0].mesh.get_surface_count() != 1 or children[1].mesh.get_surface_count() != 2 or children[2].mesh.get_surface_count() != 1:
			return _failure("The imported water surface layout is stale.")
		return {"ok": true}
	var data: Dictionary = metadata
	if data.is_empty():
		var admitted: Dictionary = Recipe.preview_metadata()
		if not admitted.ok:
			return admitted
		data = admitted.value
	var shoreline: Dictionary = source_recipe.read_surface(surface_path, Recipe.SURFACE_SHA256 if surface_sha256.is_empty() else surface_sha256)
	if not shoreline.ok:
		return shoreline
	var materials: Array[ShaderMaterial] = []
	for index: int in range(children.size()):
		var material: ShaderMaterial = children[index].base_material.duplicate()
		var required: Array = [["reflection_texture", "caustic_texture"], ["reflection_texture", "caustic_texture", "waves_texture"], ["sun_blob_texture", "sun_reflection_texture"]][index]
		for uniform: String in required:
			var texture: Variant = material.get_shader_parameter(uniform)
			if texture_bindings.has(uniform):
				texture = texture_bindings[uniform]
			if not texture is Texture2D:
				return _failure("The water texture binding is invalid: " + uniform)
			var admitted: Dictionary = Recipe.admit_texture(texture, uniform)
			if not admitted.ok:
				return admitted
			material.set_shader_parameter(uniform, texture)
		materials.append(material)
	var water_color := Vector3(F.value(33.0 / 255.0), F.value(33.0 / 255.0), F.value(61.0 / 255.0))
	var rgb: int = data.fog_color_rgb24
	var fog_color := Vector3(F.value(float((rgb >> 16) & 255) / 255.0), F.value(float((rgb >> 8) & 255) / 255.0), F.value(float(rgb & 255) / 255.0))
	for index: int in range(2):
		materials[index].set_shader_parameter("water_color", water_color)
		materials[index].set_shader_parameter("fog_color", fog_color)
		materials[index].set_shader_parameter("fog_density", Words.read_word(data.fog_density_bits))
		materials[index].set_shader_parameter("caustic_phase", 0.0)
	for material: ShaderMaterial in materials:
		material.set_shader_parameter("retail_origin", Vector2(288.6875, 243.25))
	materials[1].set_shader_parameter("main_wave_scroll", 0.0)
	materials[1].set_shader_parameter("projection_depth_bias", F.value(float(Recipe.SHORELINE_DEPTH_BIAS_INDEX) * F.value(Recipe.RETAIL_DEPTH_BIAS_SCALE)))
	materials[2].set_shader_parameter("projection_depth_bias", F.value(float(Recipe.SUN_GLINT_DEPTH_BIAS_INDEX) * F.value(Recipe.RETAIL_DEPTH_BIAS_SCALE)))
	materials[2].set_shader_parameter("glint_phase", 0.0)
	var meshes: Array[ArrayMesh] = [Recipe.build_grid_mesh(), shoreline.value, Recipe.build_sun_glint_mesh()]
	# Commit presentation only after every input is admitted, allowing a failed
	# preparation to retry without half-mutated nodes or stale animation state.
	for index: int in range(children.size()):
		children[index].mesh = meshes[index]
		children[index].material_override = materials[index]
	return {"ok": true}


## Explicit once-per-instance host seam. The .NET transition adapter transfers
## one admitted input and existing textures; native code owns all frame math.
func configure(terrain_bytes: PackedByteArray, retain_saved: bool, texture_bindings: Dictionary = {}, surface_path: String = "", surface_sha256: String = "") -> Dictionary:
	if Engine.is_editor_hint():
		return _failure("Editor inspection cannot initialize live water animation.")
	var admitted: Dictionary = Recipe.metadata_from_bytes(terrain_bytes)
	if not admitted.ok:
		return admitted
	var visual: Dictionary = prepare_visual(retain_saved, admitted.value, texture_bindings, surface_path, surface_sha256)
	if not visual.ok:
		return visual
	_metadata = admitted.value
	var horizontal_sun := Vector3(Words.read_word(_metadata.sun_position_x_bits), 0.0, -Words.read_word(_metadata.sun_position_y_bits))
	_direction = -horizontal_sun.normalized() if horizontal_sun.length_squared() > 0.0 else Vector3.FORWARD
	_water_height = F.value(-10.0 - Words.read_word(_metadata.water_level_bits))
	_caustic_phase = 0.0
	_main_wave_scroll = 0.0
	_configured = true
	if not retain_saved:
		for child_name: String in CHILD_NAMES:
			get_node(NodePath(child_name)).enable_private_bake()
	_retain_nested_overrides()
	return {"ok": true}


func update_camera(camera_position: Vector3, frame_delta: float) -> Dictionary:
	if Engine.is_editor_hint() or not _configured:
		return _failure("The water has not been configured for gameplay.")
	var delta: float = F.value(frame_delta)
	if is_finite(delta) and delta > 0.0:
		_caustic_phase = _posmod(F.value(_caustic_phase + F.value(delta * CAUSTIC_PHASE_RADIANS_PER_SECOND)), F.value(TAU))
		_main_wave_scroll = _posmod(F.value(_main_wave_scroll + F.value(delta * F.value(WAVE_SCROLL_PER_SECOND))), 1.0)
	var grid: WaterMesh = get_node(NodePath(CHILD_NAMES[0]))
	var shoreline: WaterMesh = get_node(NodePath(CHILD_NAMES[1]))
	var glint: WaterMesh = get_node(NodePath(CHILD_NAMES[2]))
	grid.material_override.set_shader_parameter("caustic_phase", _caustic_phase)
	shoreline.material_override.set_shader_parameter("caustic_phase", _caustic_phase)
	shoreline.material_override.set_shader_parameter("main_wave_scroll", _main_wave_scroll)
	glint.material_override.set_shader_parameter("glint_phase", _caustic_phase)
	grid.position = Vector3(camera_position.x, _water_height, camera_position.z)
	var camera_height: float = F.value(camera_position.y - _water_height)
	var center := Vector3(camera_position.x, _water_height, camera_position.z)
	center += _direction * F.value(camera_height * SUN_GLINT_CENTER_HEIGHT_SCALE)
	glint.position = center
	# Vector2.angle selects native atan2(float,float), matching Mathf.Atan2.
	glint.rotation = Vector3(0.0, Vector2(_direction.z, _direction.x).angle(), 0.0)
	glint.scale = Vector3(F.value(camera_height * SUN_GLINT_HALF_WIDTH_HEIGHT_SCALE), 1.0, F.value(camera_height * SUN_GLINT_HALF_LENGTH_HEIGHT_SCALE))
	return {"ok": true}


func counts() -> Dictionary:
	return {"grid_vertices": Recipe.GRID_VERTICES * Recipe.GRID_VERTICES, "grid_triangles": Recipe.GRID_CELLS * Recipe.GRID_CELLS * 2, "shoreline_triangles": Recipe.SURFACE_SEGMENTS * 4}


func state() -> Dictionary:
	return {"configured": _configured, "caustic_phase": _caustic_phase, "main_wave_scroll": _main_wave_scroll, "direction": _direction, "water_height": _water_height, "metadata": _metadata.duplicate(true)}


static func _posmod(value: float, modulus: float) -> float:
	# C# Mathf.PosMod stores its float remainder before the conditional add.
	# fmod of two float32 operands has an exactly representable float remainder;
	# explicitly storing both steps also retains its signed-zero behavior.
	var remainder: float = F.value(fmod(value, modulus))
	if (remainder < 0.0 and modulus > 0.0) or (remainder > 0.0 and modulus < 0.0):
		remainder = F.value(remainder + modulus)
	return remainder


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
