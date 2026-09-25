# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## The Level 100 base world from the hash-pinned level100-static-world.json:
## 33 placed statics (three with released idle loops split by hierarchy part),
## 1,481 pines as close meshes and six-face far imposters, and the water. build()
## makes it for the offline import; bind_scene() binds the imported nodes at
## runtime without constructing a second world. Both return {ok, value:
## {root, objects, surface_count, pine_count, water, water_counts, animation}}.
## Every float stored the way the former C# owner stored binary32 values.

const Json = preload("res://Client/manifest_json.gd")
const AnimationManifest = preload("res://Client/static_world_animation_manifest.gd")
const StaticAnimation = preload("res://Scenes/World/static_world_animation.gd")
const ObjMesh = preload("res://Scenes/World/curated_obj_mesh.gd")
const AyaTexture = preload("res://Scenes/Shared/retail_aya_texture.gd")
const FixedFunction = preload("res://Scenes/Shared/retail_fixed_function_material.gd")
const Words = preload("res://Core/retail_float24.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")

const MANIFEST_PATH: String = "res://Assets/Level100/StaticWorld/level100-static-world.json"
const ANIMATION_MANIFEST_PATH: String = "res://Assets/Level100/StaticWorld/level100-static-world-animation.json"
const MANIFEST_SHA256: String = "17D6112A96D548FB546999B79D3980D173CE5BB0A6F0DA4573EAE28FC5B62C09"
const SOURCE_ARCHIVE_SHA256: String = "ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A"
const MAXIMUM_MANIFEST_BYTES: int = 512_000
const SAT_TURRET_DEFINITION: String = "SAT Turret"
const SAT_TURRET_MESH: String = "ft_sam"
const STATIC_RESOURCE_PREFIX: String = "res://Assets/Level100/StaticWorld/"
const WATER_SCENE_PATH: String = "res://Scenes/World/Water.tscn"
## Level100Terrain's player start: 73,904/256, 62,272/256 and -10,000 mm.
const PLAYER_START_X: float = 288.6875
const PLAYER_START_Z: float = 243.25
const PLAYER_START_ELEVATION: float = -10.0
## D3DTOP_MODULATE2X, measured on all 134 mode-0 static-world and 442 CRTTree
## draws of one Level 100 frame. The 19 later mode-4 MODULATE draws come from
## CRTMesh objects not mapped to this manifest, so none is given MODULATE here.
const MODULATE_2X: int = 5
## D3DRS_AMBIENT at all 442 close-pine draws, 0x0039293e: measured, with no
## established shipped source (no image operand holds it).
const CLOSE_PINE_AMBIENT_RGB24: int = 0x0039293E
## CRTTree::BuildRenderOutputs scales the sun colour by [0x005d85c0] = 0.1.
const CLOSE_PINE_KEY_LIGHT_SCALE: float = 0.1
const COMPRESSIONS: Dictionary = {"Dxt1": 0, "Dxt2": 1, "Rgba8": 2}
const EXPECTED_PINE_CENTERS: Array = [
	[0xBCCC7F20, 0x39BA4000, 0xBF6303AA],
	[0x3D8FAD60, 0xBDA96080, 0xBF696408],
	[0x3C9B2D60, 0xBDF5D470, 0xBF6A0AB4],
	[0x3D429CA0, 0x3CD68540, 0xBF506532],
]
const PINE_FAR_IMPOSTER_SHADER_CODE: String = """shader_type spatial;
render_mode unshaded, cull_disabled;

uniform sampler2D atlas : filter_nearest_mipmap, repeat_enable;
uniform vec3 fog_color;
uniform float fog_density;
uniform float mesh_distance_squared;
varying float face_alignment;
varying float horizontal_distance_squared;
varying float view_depth;

vec3 retail_output(vec3 color) {
    if (OUTPUT_IS_SRGB) {
        return color;
    }
    vec3 low = color / 12.92;
    vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
    return mix(low, high, step(vec3(0.04045), color));
}

void vertex() {
    vec3 world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    vec3 world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);
    face_alignment = dot(
        world_normal,
        CAMERA_POSITION_WORLD - world_position);
    vec2 horizontal_offset =
        MODEL_MATRIX[3].xz - CAMERA_POSITION_WORLD.xz;
    horizontal_distance_squared = dot(
        horizontal_offset,
        horizontal_offset);
    vec3 camera_position = (VIEW_MATRIX * vec4(world_position, 1.0)).xyz;
    view_depth = max(-camera_position.z, 0.0);
}

void fragment() {
    if (horizontal_distance_squared <= mesh_distance_squared ||
        face_alignment <= 0.0) {
        discard;
    }
    vec4 texel = texture(atlas, UV);
    if (texel.a < (8.0 / 255.0)) {
        discard;
    }
    float visibility = clamp(
        exp(-fog_density * view_depth),
        0.0,
        1.0);
    vec3 tree_color = min(texel.rgb * 2.0, vec3(1.0));
    ALBEDO = retail_output(mix(fog_color, tree_color, visibility));
}"""



## The verified manifest bytes: Core's actor definitions and this owner both
## read exactly these bytes.
static func load_manifest_bytes() -> Dictionary:
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(MANIFEST_PATH)
	if bytes.is_empty() or bytes.size() > MAXIMUM_MANIFEST_BYTES or Json.sha256_hex(bytes) != MANIFEST_SHA256:
		return _invalid("The locally materialized Level 100 static-world manifest is missing or changed.")
	return {"ok": true, "value": bytes}


static func load_animation() -> Dictionary:
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(ANIMATION_MANIFEST_PATH)
	if bytes.is_empty() or bytes.size() > 512_000:
		return _invalid("The locally materialized Level 100 static-world animation manifest is missing.")
	return AnimationManifest.decode(bytes)


static func load_manifest() -> Dictionary:
	var bytes: Dictionary = load_manifest_bytes()
	if not bytes.ok:
		return bytes
	var parsed: Dictionary = Json.parse(bytes.value)
	if not parsed.ok:
		return parsed
	if parsed.value == null:
		return _invalid("The Level 100 static-world manifest is empty.")
	return {"ok": true, "value": _project(parsed.value)}


## The DTO view of the manifest, with JsonSerializer's case-insensitive binding.
static func _project(root: Dictionary) -> Dictionary:
	var pine_billboards: Variant = Json.field(root, "PineBillboards", {})
	var variants: Array = []
	for variant: Variant in Json.field(pine_billboards, "Variants", []):
		variants.append({"center_offset": Json.field(variant, "CenterOffset", []), "views": Json.field(variant, "Views", [])})
	var meshes: Dictionary = {}
	var mesh_source: Variant = Json.field(root, "Meshes", {})
	for key: String in mesh_source:
		var definition: Variant = mesh_source[key]
		var materials: Dictionary = {}
		var material_source: Variant = Json.field(definition, "Materials", {})
		for name: String in material_source:
			var layers: Array = []
			for layer: Variant in Json.field(material_source[name], "Layers", []):
				layers.append(null if layer == null else {"offset": Json.field(layer, "Offset", []),
					"opacity": Json.field(layer, "Opacity", 0.0), "scale": Json.field(layer, "Scale", []),
					"texture": Json.field(layer, "Texture", "")})
			materials[name] = {"layers": layers}
		meshes[key] = {"base_clearance": Json.field(definition, "BaseClearance", 0.0), "materials": materials,
			"resource_path": Json.field(definition, "ResourcePath", "")}
	var textures: Dictionary = {}
	var texture_source: Variant = Json.field(root, "Textures", {})
	for key: String in texture_source:
		var definition: Variant = texture_source[key]
		textures[key] = {"blend_texture_alpha": Json.field(definition, "BlendTextureAlpha", false),
			"compression": Json.field(definition, "Compression", ""), "height": Json.field(definition, "Height", 0),
			"resource_path": Json.field(definition, "ResourcePath", ""), "width": Json.field(definition, "Width", 0)}
	var objects: Array = []
	for item: Variant in Json.field(root, "Objects", []):
		objects.append({"definition": Json.field(item, "Definition", ""), "mesh": Json.field(item, "Mesh", ""),
			"name": Json.field(item, "Name", ""), "ordinal": Json.field(item, "Ordinal", 0),
			"retail_position": Json.field(item, "RetailPosition", []), "yaw": Json.field(item, "Yaw", 0.0)})
	var water: Variant = Json.field(root, "Water", {})
	return {"schema": Json.field(root, "Schema", ""), "source_archive_sha256": Json.field(root, "SourceArchiveSha256", ""),
		"unit_record_count": Json.field(root, "UnitRecordCount", 0), "visible_object_count": Json.field(root, "VisibleObjectCount", 0),
		"suppressed_fern_count": Json.field(root, "SuppressedFernCount", 0), "pine_instance_count": Json.field(root, "PineInstanceCount", 0),
		"pine_billboards": {"fast_standing_view_phase": Json.field(pine_billboards, "FastStandingViewPhase", 0),
			"mesh_quality_distance": Json.field(pine_billboards, "MeshQualityDistance", 0.0),
			"texture": Json.field(pine_billboards, "Texture", ""), "variants": variants},
		"meshes": meshes, "textures": textures, "objects": objects, "pines": Json.field(root, "Pines", []),
		"water": {"caustic_texture": Json.field(water, "CausticTexture", ""), "level": Json.field(water, "Level", 0.0),
			"reflection_texture": Json.field(water, "ReflectionTexture", ""), "sun_blob_texture": Json.field(water, "SunBlobTexture", ""),
			"sun_reflection_texture": Json.field(water, "SunReflectionTexture", ""),
			"surface_resource_path": Json.field(water, "SurfaceResourcePath", ""), "surface_sha256": Json.field(water, "SurfaceSha256", ""),
			"texture_index": Json.field(water, "TextureIndex", 0), "waves_texture": Json.field(water, "WavesTexture", "")}}


## Builds the base world under a new "RetailLevel100StaticWorld" root for the
## offline import. terrain is the native height field owner.
static func build(terrain: RefCounted, terrain_bytes: PackedByteArray) -> Dictionary:
	var loaded: Dictionary = load_manifest()
	if not loaded.ok:
		return loaded
	var manifest: Dictionary = loaded.value
	var metadata: Dictionary = terrain.metadata()
	var valid: Dictionary = validate(manifest, metadata)
	if not valid.ok:
		return valid
	var animation: Dictionary = load_animation()
	if not animation.ok:
		return animation
	var pine_mesh_distance: float = F.value(manifest.pine_billboards.mesh_quality_distance)
	var root := Node3D.new()
	root.name = "RetailLevel100StaticWorld"
	var textures: Dictionary = {}
	for key: String in manifest.textures:
		var texture: Dictionary = _load_texture(manifest.textures[key])
		if not texture.ok:
			return texture
		textures[key] = texture.value
	var meshes: Dictionary = {}
	var partitioned: Dictionary = {}
	for key: String in manifest.meshes:
		var definition: Dictionary = manifest.meshes[key]
		# The four pinesnow meshes are the only keys no placed object uses; the
		# close-pine meshes are their only consumer, so this selects exactly
		# retail's CRTTree draws, which the measured light rig split needs.
		var close_pine: bool = key.begins_with("pinesnow")
		var rig: Dictionary = close_pine_rig(metadata) if close_pine else static_world_rig(metadata)
		var materials: Dictionary = {}
		for name: String in definition.materials:
			var material: Dictionary = _create_material(definition.materials[name], textures, manifest.textures, metadata,
				pine_mesh_distance if close_pine else 0.0, rig)
			if not material.ok:
				return material
			materials[name] = material.value
		# Only meshes the released data says loop are split by part. The three
		# one-shot turrets hold their rest pose, virtual frame 0, which is exactly
		# the merged mesh, so splitting them would only fragment their surfaces.
		var mesh_animation: Variant = animation.value.meshes.get(key)
		if mesh_animation != null and mesh_animation.playback == AnimationManifest.Playback.CYCLIC_LOOP:
			var ranges: Array = []
			for part: Dictionary in mesh_animation.parts:
				ranges.append({"part": part.part, "first_vertex": part.obj_vertex_start, "vertex_count": part.obj_vertex_count})
			var split: Dictionary = ObjMesh.load_partitioned(definition.resource_path, materials, ranges)
			if not split.ok:
				return split
			partitioned[key] = split.value
			continue
		var mesh: Dictionary = ObjMesh.load_mesh(definition.resource_path, materials)
		if not mesh.ok:
			return mesh
		meshes[key] = mesh.value
	var objects: Array[MeshInstance3D] = []
	var animated: Array[Dictionary] = []
	for world_object: Dictionary in _ordered_objects(manifest.objects):
		var relative_x: float = F.value(F.value(world_object.retail_position[0]) - PLAYER_START_X)
		var relative_z: float = F.value(F.value(world_object.retail_position[1]) - PLAYER_START_Z)
		var retail_z: float = F.value(world_object.retail_position[2])
		# CThing__Init (0x004F34A0) is the whole vertical placement: it copies
		# the authored position (Z down at +0x24), then clamps to the bilinear
		# height sample (0x0047EB80, FSTP at 0x004F3529) and to the water level
		# (0x006FBDFC, FSTP at 0x004F3559). Both write the pivot, so it is
		# min(authored, support) Z-down, the maximum here. No mesh extent is
		# read: retail seats the pivot, never the bounding box (a -min(vertexZ)
		# term lifted FB_Docks' pilings 3.2318 above the water).
		var relative_height: float = dotnet_max(F.value(PLAYER_START_ELEVATION - retail_z),
			dotnet_max(sample(terrain, relative_x, relative_z), F.value(metadata.water_relative_height)))
		var object_root := Node3D.new()
		object_root.name = "RetailWorldObject%02d" % world_object.ordinal
		object_root.position = Vector3(relative_x, relative_height, -relative_z)
		object_root.rotation = Vector3(0.0, F.value(world_object.yaw), 0.0)
		var split: Variant = partitioned.get(world_object.mesh)
		var geometry := MeshInstance3D.new()
		geometry.name = String(world_object.name) + "Geometry"
		geometry.mesh = split.remainder if split != null else meshes[world_object.mesh]
		geometry.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
		if split != null:
			# geometry's -90 degree X rotation is all that separates the OBJ
			# vertices from this object, so its local frame is the OBJ space the
			# released deltas use and its children take them verbatim.
			var mesh_animation: Dictionary = animation.value.meshes[world_object.mesh]
			for part: Dictionary in mesh_animation.parts:
				var part_node := MeshInstance3D.new()
				part_node.name = "Part%02d-%s" % [part.part, sanitize_node_name(part.name)]
				part_node.mesh = split.parts[part.part]
				var transform: Dictionary = StaticAnimation.to_obj_space_transform(frame_facts(part.frames[0]))
				if not transform.ok:
					return transform
				part_node.transform = transform.value
				geometry.add_child(part_node)
				animated.append({"mesh": mesh_animation, "part": part, "node": part_node})
		object_root.add_child(geometry)
		root.add_child(object_root)
		objects.append(geometry)
	# Every part the manifest says moves on a looping mesh must reach a node, or
	# a drifting mesh key would silently freeze that scenery again.
	var expected_bindings: int = 0
	for world_object: Dictionary in manifest.objects:
		if partitioned.has(world_object.mesh):
			expected_bindings += animation.value.meshes[world_object.mesh].parts.size()
	if animated.size() != expected_bindings or animated.is_empty():
		return _invalid("The Level 100 static-world animated parts were not all bound at load.")
	var pines: Dictionary = _add_pines(root, manifest, terrain, metadata, meshes, textures)
	if not pines.ok:
		return pines
	var water := (load(WATER_SCENE_PATH) as PackedScene).instantiate() as Node3D
	var water_textures: Dictionary = {"reflection_texture": textures[manifest.water.reflection_texture],
		"caustic_texture": textures[manifest.water.caustic_texture], "waves_texture": textures[manifest.water.waves_texture],
		"sun_blob_texture": textures[manifest.water.sun_blob_texture],
		"sun_reflection_texture": textures[manifest.water.sun_reflection_texture]}
	var configured: Dictionary = _configure_water(water, terrain_bytes, false, water_textures,
		manifest.water.surface_resource_path, manifest.water.surface_sha256)
	if not configured.ok:
		water.free()
		return configured
	root.add_child(water)
	return _result(root, objects, animated, pines.value, water, animation.value.frames_per_second)


## Binds the imported "RetailLevel100StaticWorld" nodes at runtime.
static func bind_scene(root: Node3D, terrain: RefCounted, terrain_bytes: PackedByteArray) -> Dictionary:
	var loaded: Dictionary = load_manifest()
	if not loaded.ok:
		return loaded
	var manifest: Dictionary = loaded.value
	var valid: Dictionary = validate(manifest, terrain.metadata())
	if not valid.ok:
		return valid
	var animation: Dictionary = load_animation()
	if not animation.ok:
		return animation
	var objects: Array[MeshInstance3D] = []
	var animated: Array[Dictionary] = []
	for world_object: Dictionary in _ordered_objects(manifest.objects):
		var placement: Node = root.get_node_or_null("RetailWorldObject%02d" % world_object.ordinal)
		if placement == null:
			return _invalid("Imported scenery lost a placed static-world object.")
		var geometries: Array[MeshInstance3D] = []
		for child: Node in placement.get_children():
			if child is MeshInstance3D:
				geometries.append(child)
		if geometries.size() != 1:
			return _invalid("Sequence contains no elements or more than one element.")
		var geometry: MeshInstance3D = geometries[0]
		objects.append(geometry)
		var mesh_animation: Variant = animation.value.meshes.get(world_object.mesh)
		if mesh_animation != null and mesh_animation.playback == AnimationManifest.Playback.CYCLIC_LOOP:
			for part: Dictionary in mesh_animation.parts:
				var node: Node = geometry.get_node_or_null("Part%02d-%s" % [part.part, sanitize_node_name(part.name)])
				if not node is MeshInstance3D:
					return _invalid("Imported scenery lost an animated part.")
				animated.append({"mesh": mesh_animation, "part": part, "node": node})
	var pine_count: int = 0
	for variant: int in range(4):
		var close: Node = root.get_node_or_null("RetailPineSnow%dCloseMeshInstances" % variant)
		var far: Node = root.get_node_or_null("RetailPineSnow%dFarSixFaceInstances" % variant)
		if not close is MultiMeshInstance3D or not far is MultiMeshInstance3D \
				or close.multimesh.instance_count != far.multimesh.instance_count:
			return _invalid("Imported pine representations disagree.")
		pine_count += close.multimesh.instance_count
	if pine_count != manifest.pines.size() or animated.is_empty():
		return _invalid("Imported scenery lost pine or animation bindings.")
	var water: Node = root.get_node_or_null("RetailLevel100Water")
	if not water is Node3D:
		return _invalid("The imported water is stale. Rebuild the private production scene.")
	var configured: Dictionary = _configure_water(water, terrain_bytes, true, {}, "", "")
	if not configured.ok:
		return configured
	return _result(root, objects, animated, pine_count, water, animation.value.frames_per_second)


static func _result(root: Node3D, objects: Array[MeshInstance3D], animated: Array[Dictionary], pine_count: int,
		water: Node3D, frames_per_second: int) -> Dictionary:
	var surface_count: int = 0
	for geometry: MeshInstance3D in objects:
		surface_count += 0 if geometry.mesh == null else geometry.mesh.get_surface_count()
	var rows: Array = []
	for binding: Dictionary in animated:
		surface_count += 0 if binding.node.mesh == null else binding.node.mesh.get_surface_count()
		var frames: Array = []
		for frame: Dictionary in binding.part.frames:
			frames.append(frame_facts(frame))
		rows.append({"mesh": {"playback": binding.mesh.playback, "loop_frame_count": binding.mesh.loop_frame_count},
			"part": {"frames": frames}, "node": binding.node})
	var driver: Dictionary = StaticAnimation.create(frames_per_second, rows)
	if not driver.ok:
		return driver
	return {"ok": true, "value": {"root": root, "objects": objects, "surface_count": surface_count,
		"pine_count": pine_count, "water": water, "water_counts": water.counts(), "animation": driver.value,
		"binding_count": animated.size()}}


static func _configure_water(water: Node3D, terrain_bytes: PackedByteArray, retain_saved: bool, textures: Dictionary,
		surface_path: String, surface_sha256: String) -> Dictionary:
	if not water.has_method("configure"):
		return _invalid("The imported water is stale. Rebuild the private production scene.")
	var result: Dictionary = water.configure(terrain_bytes, retain_saved, textures, surface_path, surface_sha256)
	return result if result.ok else _invalid(result.error)


## One released delta as float32 words for the native pose law.
static func frame_facts(frame: Dictionary) -> Dictionary:
	var basis_bits := PackedInt64Array()
	for value: float in frame.basis:
		basis_bits.append(Words.store_word(value))
	var origin_bits := PackedInt64Array()
	for value: float in frame.origin:
		origin_bits.append(Words.store_word(value))
	return {"basis_bits": basis_bits, "origin_bits": origin_bits}


static func sample(terrain: RefCounted, relative_x: float, relative_z: float) -> float:
	return F.value(terrain.sample_relative_height(relative_x, relative_z))


static func sanitize_node_name(value: String) -> String:
	if value.is_empty():
		return "Part"
	var result: String = ""
	for index: int in range(value.length()):
		var unit: int = value.unicode_at(index)
		var ascii_alnum: bool = (unit >= 48 and unit <= 57) or (unit >= 65 and unit <= 90) or (unit >= 97 and unit <= 122)
		result += value[index] if ascii_alnum else "_"
	return result


## .NET Math.Max(float, float): NaN propagates from the first argument and a
## tie prefers the non-negative zero.
static func dotnet_max(left: float, right: float) -> float:
	if left != right:
		if not is_nan(left):
			return left if right < left else right
		return left
	return left if (Words.store_word(right) & 0x80000000) != 0 else right


## The 130 mode-0 CRTMesh static-world draws: D3DRS_AMBIENT is the height
## field's own ambient, light 0 its sun colour along its sun vector and light 1
## the full anti-sun travelling the other way.
static func static_world_rig(metadata: Dictionary) -> Dictionary:
	return {"ambient_color": _color_vector(metadata.ambient_color_rgb24, 255.0),
		"key_light_color": _color_vector(metadata.sun_color_rgb24, 256.0),
		"fill_light_color": _color_vector(metadata.anti_sun_color_rgb24, 256.0),
		"key_light_direction": metadata.sunlight_direction}


## The 442 CRTTree close-pine draws: the measured 0x0039293e ambient, the sun
## colour times 0.1 travelling straight down BEA +Z (Godot (0,-1,0)) and the full
## anti-sun travelling straight up.
static func close_pine_rig(metadata: Dictionary) -> Dictionary:
	return {"ambient_color": _color_vector(CLOSE_PINE_AMBIENT_RGB24, 255.0),
		"key_light_color": _color_vector(metadata.sun_color_rgb24, 256.0) * CLOSE_PINE_KEY_LIGHT_SCALE,
		"fill_light_color": _color_vector(metadata.anti_sun_color_rgb24, 256.0),
		"key_light_direction": Vector3(0.0, -1.0, 0.0)}


static func _color_vector(rgb: int, divisor: float) -> Vector3:
	return Vector3(F.value(((rgb >> 16) & 0xFF) / divisor), F.value(((rgb >> 8) & 0xFF) / divisor),
		F.value((rgb & 0xFF) / divisor))


static func terrain_facts(metadata: Dictionary) -> Dictionary:
	return {"ambient_color_rgb24": metadata.ambient_color_rgb24, "sun_color_rgb24": metadata.sun_color_rgb24,
		"anti_sun_color_rgb24": metadata.anti_sun_color_rgb24, "sunlight_direction": metadata.sunlight_direction,
		"fog_color": metadata.fog_color, "fog_density": metadata.fog_density}


static func _create_material(definition: Dictionary, textures: Dictionary, definitions: Dictionary, metadata: Dictionary,
		maximum_horizontal_distance: float, rig: Dictionary) -> Dictionary:
	var layers: Array = []
	layers.resize(6)
	for slot: int in range(definition.layers.size()):
		var layer: Variant = definition.layers[slot]
		if layer == null or slot not in [0, 1, 2, 4]:
			continue
		layers[slot] = {"texture": textures[layer.texture], "opacity": F.value(layer.opacity),
			"offset": Vector2(F.value(layer.offset[0]), F.value(layer.offset[1])),
			"scale": Vector2(F.value(layer.scale[0]), F.value(layer.scale[1])),
			"blend_texture_alpha": definitions[layer.texture].blend_texture_alpha}
	var created: Dictionary = FixedFunction.create(layers if definition.layers.size() == 6 else [], terrain_facts(metadata),
		maximum_horizontal_distance, F.value(8.0 / 255.0) if maximum_horizontal_distance > 0.0 else 0.5, MODULATE_2X, rig)
	return created if created.ok else {"ok": false, "error_type": created.get("error_type", "InvalidDataException"),
		"error": created.get("error", "Native fixed-function material failed.")}


static func _load_texture(definition: Dictionary) -> Dictionary:
	if not COMPRESSIONS.has(definition.compression):
		return _invalid("Static-world texture has unsupported compression '%s'." % definition.compression)
	var loaded: Dictionary = AyaTexture.new().load_texture_checked(definition.resource_path, definition.width,
		definition.height, COMPRESSIONS[definition.compression], null, null)
	return loaded if loaded.ok else _invalid(loaded.error)


static func _ordered_objects(objects: Array) -> Array:
	var ordered: Array = objects.duplicate()
	# Stable by ordinal, as Enumerable.OrderBy.
	var indexed: Array = []
	for index: int in range(ordered.size()):
		indexed.append([ordered[index].ordinal, index, ordered[index]])
	indexed.sort_custom(func(left: Array, right: Array) -> bool:
		return left[0] < right[0] or (left[0] == right[0] and left[1] < right[1]))
	var result: Array = []
	for row: Array in indexed:
		result.append(row[2])
	return result


## A retail pine has two representations: the pinesnow mesh at or inside the
## authored mesh-quality distance (retail's default 30.0: the Geometry detail
## setter 0x004DD6B0's middle arm, the image's own initialiser at 0x006321A0)
## and the six-face imposter outside it. The two shader gates are
## complementary about that one value, so every pine shows at every distance.
static func _add_pines(root: Node3D, manifest: Dictionary, terrain: RefCounted, metadata: Dictionary, meshes: Dictionary,
		textures: Dictionary) -> Dictionary:
	# CTree::Init (0x004F6080) stores the height query result straight into
	# mPos.Z (FSTP [EBX+0xC] at 0x004F61F4) with no mesh extent read, and both
	# draw paths inherit that pivot; CThing::Init's water clamp is the maximum.
	var placements: Array[Dictionary] = []
	for pine: Array in manifest.pines:
		var relative_x: float = F.value(F.value(pine[0]) - PLAYER_START_X)
		var relative_z: float = F.value(F.value(pine[1]) - PLAYER_START_Z)
		var height: float = dotnet_max(sample(terrain, relative_x, relative_z), F.value(metadata.water_relative_height))
		placements.append({"variant": int(pine[2]), "origin": Vector3(relative_x, height, -relative_z)})
	var mesh_basis := Basis(Vector3.RIGHT, -PI / 2.0)
	for variant: int in range(4):
		var instances: Array = placements.filter(func(item: Dictionary) -> bool: return item.variant == variant)
		var multimesh := MultiMesh.new()
		multimesh.transform_format = MultiMesh.TRANSFORM_3D
		multimesh.mesh = meshes["pinesnow%d" % variant]
		multimesh.instance_count = instances.size()
		for index: int in range(instances.size()):
			multimesh.set_instance_transform(index, Transform3D(mesh_basis, instances[index].origin))
		var close := MultiMeshInstance3D.new()
		close.name = "RetailPineSnow%dCloseMeshInstances" % variant
		close.multimesh = multimesh
		root.add_child(close)
	var material: Dictionary = _pine_imposter_material(textures[manifest.pine_billboards.texture], metadata,
		manifest.pine_billboards.mesh_quality_distance)
	if not material.ok:
		return material
	for variant: int in range(4):
		var instances: Array = placements.filter(func(item: Dictionary) -> bool: return item.variant == variant)
		var mesh: ArrayMesh = _far_pine_imposter_mesh(manifest.pine_billboards.variants[variant], material.value)
		# The stored VIEW half-extents are this variant's own mesh bounds times
		# 1.05 and the centre is already inside the geometry, so the box must sit
		# on the same transform as the mesh or the tree steps at the swap
		# (CDXEngine::RenderImposterBillboardSet 0x00543300 adds only the centre).
		var multimesh := MultiMesh.new()
		multimesh.transform_format = MultiMesh.TRANSFORM_3D
		multimesh.mesh = mesh
		multimesh.instance_count = instances.size()
		for index: int in range(instances.size()):
			multimesh.set_instance_transform(index, Transform3D(Basis.IDENTITY, instances[index].origin))
		var far := MultiMeshInstance3D.new()
		far.name = "RetailPineSnow%dFarSixFaceInstances" % variant
		far.multimesh = multimesh
		far.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		root.add_child(far)
	return {"ok": true, "value": placements.size()}


static func _pine_imposter_material(atlas: Texture2D, metadata: Dictionary, mesh_quality_distance: float) -> Dictionary:
	# Every imposter is distance-gated: the box appears only where the mesh is discarded.
	var distance: float = F.value(mesh_quality_distance)
	if not is_finite(distance) or distance <= 0.0:
		return _invalid("Level 100 pine imposters require a positive mesh-quality distance.")
	# One shader and one material serve all four far variants of a build.
	var shader := Shader.new()
	shader.code = PINE_FAR_IMPOSTER_SHADER_CODE
	var material := ShaderMaterial.new()
	material.shader = shader
	material.render_priority = 0
	material.set_shader_parameter("atlas", atlas)
	var fog: Color = metadata.fog_color
	material.set_shader_parameter("fog_color", Vector3(fog.r, fog.g, fog.b))
	material.set_shader_parameter("fog_density", metadata.fog_density)
	material.set_shader_parameter("mesh_distance_squared", F.value(distance * distance))
	return {"ok": true, "value": material}


static func _far_pine_imposter_mesh(definition: Dictionary, material: Material) -> ArrayMesh:
	var raw_rights: Array[Vector3] = [Vector3.RIGHT, Vector3(0, -1, 0), Vector3.LEFT, Vector3(0, 1, 0), Vector3.RIGHT, Vector3.RIGHT]
	var raw_ups: Array[Vector3] = [Vector3.BACK, Vector3.BACK, Vector3.BACK, Vector3.BACK, Vector3(0, -1, 0), Vector3(0, 1, 0)]
	var offset: Array = definition.center_offset
	var center := Vector3(F.value(offset[0]), -F.value(offset[2]), -F.value(offset[1]))
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	vertices.resize(24)
	normals.resize(24)
	uvs.resize(24)
	indices.resize(36)
	for face: int in range(6):
		var view: Array = definition.views[face]
		var right: Vector3 = _to_godot(raw_rights[face]) * F.value(view[4] * 0.99)
		var up: Vector3 = _to_godot(raw_ups[face]) * F.value(view[5] * 0.99)
		var normal: Vector3 = _to_godot(raw_ups[face].cross(raw_rights[face])).normalized()
		var vertex: int = face * 4
		vertices[vertex] = center - right - up
		vertices[vertex + 1] = center + right - up
		vertices[vertex + 2] = center + right + up
		vertices[vertex + 3] = center - right + up
		for index: int in range(4):
			normals[vertex + index] = normal
		var u0: float = F.value(view[0])
		var u1: float = F.value(view[1])
		var v0: float = F.value(view[2])
		var v1: float = F.value(view[3])
		uvs[vertex] = Vector2(u0, v0)
		uvs[vertex + 1] = Vector2(u1, v0)
		uvs[vertex + 2] = Vector2(u1, v1)
		uvs[vertex + 3] = Vector2(u0, v1)
		var triangle: int = face * 6
		for index: int in [0, 1, 2, 2, 3, 0]:
			indices[triangle] = vertex + index
			triangle += 1
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	mesh.surface_set_material(0, material)
	return mesh


static func _to_godot(bea: Vector3) -> Vector3:
	return Vector3(bea.x, -bea.z, -bea.y)


static func validate(manifest: Dictionary, metadata: Dictionary) -> Dictionary:
	# v13 -> v14 on 2026-07-27 with the waypoint-path coordinate correction; the
	# schema is pinned independently of the actor-definition reader.
	var water: Dictionary = manifest.water
	var blend_count: int = 0
	for texture: Dictionary in manifest.textures.values():
		if texture.blend_texture_alpha:
			blend_count += 1
	var blend: Variant = manifest.textures.get("meshtex-a8-fb-hangermorebits-lit")
	var variants_present: bool = true
	for variant: int in range(4):
		variants_present = variants_present and manifest.meshes.has("pinesnow%d" % variant)
	if manifest.schema != "onslaught.level100-static-world.v14" \
			or String(manifest.source_archive_sha256).to_upper() != SOURCE_ARCHIVE_SHA256 \
			or manifest.unit_record_count != 35 or manifest.visible_object_count != 33 \
			or manifest.suppressed_fern_count != 753 or manifest.pine_instance_count != 1481 \
			or manifest.objects.size() != 33 or manifest.pines.size() != 1481 or manifest.meshes.size() != 28 \
			or manifest.textures.size() != 34 or not variants_present \
			or not _valid_pine_billboards(manifest.pine_billboards, manifest.textures) \
			or blend == null or not blend.blend_texture_alpha or blend_count != 1 \
			or water.texture_index != metadata.water_texture \
			or Words.store_word(F.value(water.level)) != Words.store_word(F.value(metadata.water_level)) \
			or not manifest.textures.has(water.reflection_texture) or not manifest.textures.has(water.caustic_texture) \
			or not manifest.textures.has(water.waves_texture) or not manifest.textures.has(water.sun_blob_texture) \
			or not manifest.textures.has(water.sun_reflection_texture) or String(water.surface_sha256).strip_edges().is_empty():
		return _invalid("Level 100 static-world identity, counts, or reconstruction profile changed.")
	var variants: Array = [0, 0, 0, 0]
	for pine: Variant in manifest.pines:
		if not pine is Array or pine.size() != 3 or not _all_finite(pine):
			return _invalid("Level 100 has an invalid pine instance.")
		var variant: int = int(pine[2])
		if variant < 0 or variant > 3 or float(pine[2]) != float(variant):
			return _invalid("Level 100 has an invalid pine variant.")
		variants[variant] += 1
	if variants != [383, 355, 318, 425]:
		return _invalid("Level 100 pine variant counts do not match retail.")
	var ordinals: Dictionary = {}
	for item: Dictionary in manifest.objects:
		ordinals[item.ordinal] = true
	if ordinals.size() != 33:
		return _invalid("Level 100 static-world ordinals are not unique.")
	var sat_turrets: Array = manifest.objects.filter(func(item: Dictionary) -> bool: return item.definition == SAT_TURRET_DEFINITION)
	var misplaced: bool = manifest.objects.any(func(item: Dictionary) -> bool:
		return item.mesh == SAT_TURRET_MESH and item.definition != SAT_TURRET_DEFINITION)
	if sat_turrets.size() != 1 or sat_turrets[0].mesh != SAT_TURRET_MESH or misplaced:
		return _invalid("Level 100 SAT Turret identity does not match retail.")
	for item: Dictionary in manifest.objects:
		if String(item.definition).strip_edges().is_empty() or item.retail_position.size() != 3 \
				or not _all_finite(item.retail_position) or not is_finite(float(item.yaw)) or not manifest.meshes.has(item.mesh):
			return _invalid("Level 100 has an invalid static-world object.")
	for mesh: Dictionary in manifest.meshes.values():
		if not _owned(mesh.resource_path):
			return _invalid("Level 100 static-world resource escaped its local owner.")
		if not is_finite(float(mesh.base_clearance)) or mesh.materials.is_empty():
			return _invalid("Level 100 has an invalid static-world mesh.")
		for material: Dictionary in mesh.materials.values():
			if not _valid_material(material, manifest.textures):
				return _invalid("Level 100 has an invalid static-world mesh.")
	for texture: Dictionary in manifest.textures.values():
		if not _owned(texture.resource_path):
			return _invalid("Level 100 static-world resource escaped its local owner.")
		if texture.width < 1 or texture.width > 1024 or texture.height < 1 or texture.height > 1024:
			return _invalid("Level 100 has invalid static-world texture dimensions.")
	if not _owned(water.surface_resource_path):
		return _invalid("Level 100 static-world resource escaped its local owner.")
	return {"ok": true}


static func _valid_pine_billboards(definition: Dictionary, textures: Dictionary) -> bool:
	var texture: Variant = textures.get(definition.texture)
	# Retail's authored Geometry detail default 30.0 (0x004DD6B0 arm 1, the
	# image's initialiser at .data 0x006321A0 = 00 00 F0 41), not one machine's
	# defaultoptions.bea. The fast standing view phase is identity only.
	if texture == null or texture.width != 1024 or texture.height != 256 or texture.compression != "Dxt2" \
			or Words.store_word(F.value(definition.mesh_quality_distance)) != Words.store_word(30.0) \
			or definition.fast_standing_view_phase != 0 or definition.variants.size() != 4:
		return false
	for variant: int in range(definition.variants.size()):
		var item: Dictionary = definition.variants[variant]
		if item.center_offset.size() != 3 or item.views.size() != 6 or not _all_finite(item.center_offset):
			return false
		for view: Variant in item.views:
			if not view is Array or view.size() != 6 or not _all_finite(view) or view[0] < 0.0 or view[0] >= view[1] \
					or view[1] > 1.0 or view[2] < 0.0 or view[2] >= view[3] or view[3] > 1.0 or view[4] <= 0.0 or view[5] <= 0.0:
				return false
		for axis: int in range(3):
			if Words.store_word(F.value(item.center_offset[axis])) != EXPECTED_PINE_CENTERS[variant][axis]:
				return false
	return true


static func _valid_material(material: Dictionary, textures: Dictionary) -> bool:
	if material.layers.size() != 6 or material.layers[0] == null:
		return false
	for index: int in range(material.layers.size()):
		var layer: Variant = material.layers[index]
		if layer == null:
			continue
		if not textures.has(layer.texture) or not is_finite(float(layer.opacity)) or layer.opacity < 0.0 \
				or layer.opacity > 1.0 or layer.offset.size() != 2 or layer.scale.size() != 2 \
				or not _all_finite(layer.offset) or not _all_finite(layer.scale):
			return false
		for value: Variant in layer.scale:
			if value < 0.0 or value > 100.0 or (index == 4 and value <= 0.0):
				return false
	return true


static func _owned(resource_path: String) -> bool:
	return resource_path.begins_with(STATIC_RESOURCE_PREFIX) and not resource_path.contains("..")


static func _all_finite(values: Array) -> bool:
	for value: Variant in values:
		if typeof(value) not in [TYPE_INT, TYPE_FLOAT] or not is_finite(float(value)):
			return false
	return true


static func _invalid(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
