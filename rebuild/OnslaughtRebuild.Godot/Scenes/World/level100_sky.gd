# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## The Level 100 Kempy cube 25 backdrop for the offline import: five faces of
## the released sky box (Steam's formatter indexes the suffixes cent, up, right,
## down, left in that order), 500 units out, lower sides ending half-way down.

const AyaTexture = preload("res://Scenes/Shared/retail_aya_texture.gd")
const RADIUS: float = 500.0
const HALF_LOWER_EXTENT: float = 0.5
const MIN_UV: float = 1.0 / 512.0
const MAX_UV: float = 511.0 / 512.0
const SIDE_BOTTOM_UV: float = 383.5 / 512.0
const FACE_NAMES: Array[String] = ["cent", "up", "right", "down", "left"]
const DXT1: int = 0
const SKY_SHADER_CODE: String = """shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, fog_disabled;

uniform sampler2D sky_texture : source_color, filter_linear_mipmap, repeat_disable;

void vertex() {
    POSITION = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
    // Godot uses a different reversed-Z far value in Compatibility
    // and Forward+/Mobile. Keep the backdrop just inside that value
    // while never writing depth, so it cannot hide world geometry.
    POSITION.z = (CLIP_SPACE_FAR + 0.000001) * POSITION.w;
}

void fragment() {
    ALBEDO = texture(sky_texture, UV).rgb;
}"""

static var _face_vertices: Array = [
	[Vector3(-1, -1, -1), Vector3(1, -1, -1), Vector3(-1, 1, -1), Vector3(1, 1, -1)],
	[Vector3(1, 1, -1), Vector3(1, 1, HALF_LOWER_EXTENT), Vector3(-1, 1, -1), Vector3(-1, 1, HALF_LOWER_EXTENT)],
	[Vector3(1, -1, -1), Vector3(1, -1, HALF_LOWER_EXTENT), Vector3(1, 1, -1), Vector3(1, 1, HALF_LOWER_EXTENT)],
	[Vector3(-1, -1, -1), Vector3(-1, -1, HALF_LOWER_EXTENT), Vector3(1, -1, -1), Vector3(1, -1, HALF_LOWER_EXTENT)],
	[Vector3(-1, 1, -1), Vector3(-1, 1, HALF_LOWER_EXTENT), Vector3(-1, -1, -1), Vector3(-1, -1, HALF_LOWER_EXTENT)],
]


## Returns {ok, value: MeshInstance3D}. Level 100 selects the retained cube 25.
static func create(sky_cube: int) -> Dictionary:
	if sky_cube != 25:
		return _invalid("Level 100 does not select the retained Kempy cube 25.")
	var mesh := ArrayMesh.new()
	var shader := Shader.new()
	shader.code = SKY_SHADER_CODE
	var top_uvs := PackedVector2Array([Vector2(MIN_UV, MIN_UV), Vector2(MAX_UV, MIN_UV), Vector2(MIN_UV, MAX_UV),
		Vector2(MAX_UV, MAX_UV)])
	var side_uvs := PackedVector2Array([Vector2(MAX_UV, MIN_UV), Vector2(MAX_UV, SIDE_BOTTOM_UV), Vector2(MIN_UV, MIN_UV),
		Vector2(MIN_UV, SIDE_BOTTOM_UV)])
	for face: int in range(FACE_NAMES.size()):
		var vertices := PackedVector3Array()
		for bea: Vector3 in _face_vertices[face]:
			vertices.append(Vector3(bea.x, -bea.z, -bea.y) * RADIUS)
		var arrays: Array = []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = vertices
		arrays[Mesh.ARRAY_TEX_UV] = top_uvs if face == 0 else side_uvs
		arrays[Mesh.ARRAY_INDEX] = PackedInt32Array([0, 1, 2, 2, 1, 3])
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		var texture: Dictionary = AyaTexture.new().load_texture_checked(
			"res://Assets/Level100/Sky/cube25-%s.texture.aya" % FACE_NAMES[face], 512, 512, DXT1, null, null)
		if not texture.ok:
			return _invalid(texture.error)
		var material := ShaderMaterial.new()
		material.shader = shader
		material.set_shader_parameter("sky_texture", texture.value)
		mesh.surface_set_material(face, material)
	var instance := MeshInstance3D.new()
	instance.name = "RetailLevel100KempyCube25"
	instance.mesh = mesh
	return {"ok": true, "value": instance}


static func _invalid(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
