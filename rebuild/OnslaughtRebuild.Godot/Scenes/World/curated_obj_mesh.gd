# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Curated OBJ meshes for the offline Level 100 import. Accepts exactly the
## emitted subset: "v x y z [r g b]" (the retail FVF 0x152 DIFFUSE dword as an
## OBJ vertex-colour extension), "vt u v", "vn x y z", unified positive "f a/a/a"
## triangles and "usemtl" groups mapped to supplied materials. Faces use the
## OBJ counter-clockwise front winding; Godot ArrayMesh fronts are clockwise, so
## each triangle's second and third indices swap. Numbers round directly to
## binary32 as .NET float.Parse(Float, Invariant) does, never through binary64.
## Every call returns {ok, value} or an InvalidDataException.

const Number = preload("res://Core/invariant_number.gd")
const Float24 = preload("res://Core/retail_float24.gd")
const MAXIMUM_VERTICES: int = 100_000
const MAXIMUM_TRIANGLES: int = 200_000

static var _float_grammar: RegEx = null
static var _powers_of_ten: Array[float] = []


static func load_mesh(resource_path: String, materials: Dictionary) -> Dictionary:
	var parsed: Dictionary = _parse(resource_path, materials)
	if not parsed.ok:
		return parsed
	return {"ok": true, "value": _build_mesh(parsed.value, parsed.value.surfaces, materials)}


## Split one curated OBJ into a mesh per released hierarchy part plus the
## remainder every unlisted part shares. The released rigid tracks address
## geometry by contiguous 1-based OBJ vertex ranges, and every triangle lies
## wholly inside one range (measured over the three split meshes: 6,437
## triangles, none straddling), which is asserted rather than worked around.
## Each mesh keeps the whole vertex arrays and differs only in its indices.
## part_ranges: [{part, first_vertex, vertex_count}]. Returns {remainder, parts}.
static func load_partitioned(resource_path: String, materials: Dictionary, part_ranges: Array) -> Dictionary:
	var parsed: Dictionary = _parse(resource_path, materials)
	if not parsed.ok:
		return parsed
	var remainder: Array[Dictionary] = []
	var by_part: Dictionary = {}
	for surface: Dictionary in parsed.value.surfaces:
		var indices: PackedInt32Array = surface.indices
		for offset: int in range(0, indices.size(), 3):
			var a: int = indices[offset]
			var b: int = indices[offset + 1]
			var c: int = indices[offset + 2]
			var owner: int = -1
			for part_range: Dictionary in part_ranges:
				var first: int = part_range.first_vertex - 1
				var last: int = first + part_range.vertex_count - 1
				var inside: int = int(a >= first and a <= last) + int(b >= first and b <= last) + int(c >= first and c <= last)
				if inside == 0:
					continue
				if inside != 3 or owner >= 0:
					return _invalid("Curated mesh has a triangle straddling a released hierarchy part range.")
				owner = part_range.part
			var target: Array[Dictionary]
			if owner < 0:
				target = remainder
			else:
				if not by_part.has(owner):
					by_part[owner] = [] as Array[Dictionary]
				target = by_part[owner]
			var bucket: Dictionary = {}
			for item: Dictionary in target:
				if item.name == surface.name:
					bucket = item
					break
			if bucket.is_empty():
				bucket = {"name": surface.name, "indices": PackedInt32Array()}
				target.append(bucket)
			bucket.indices.append(a)
			bucket.indices.append(b)
			bucket.indices.append(c)
	var parts: Dictionary = {}
	for part_range: Dictionary in part_ranges:
		if not by_part.has(part_range.part):
			return _invalid("Curated mesh has a released hierarchy part range covering no triangle.")
		parts[part_range.part] = _build_mesh(parsed.value, by_part[part_range.part], materials)
	if remainder.is_empty():
		return _invalid("Curated mesh has no geometry outside its released hierarchy part ranges.")
	return {"ok": true, "value": {"remainder": _build_mesh(parsed.value, remainder, materials), "parts": parts}}


static func _parse(resource_path: String, materials: Dictionary) -> Dictionary:
	var source: String = FileAccess.get_file_as_string(resource_path)
	if source.is_empty():
		return _invalid("Curated mesh '%s' is missing or empty." % resource_path)
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var colors := PackedColorArray()
	var surfaces: Array[Dictionary] = []
	var by_name: Dictionary = {}
	var active: Dictionary = {}
	var triangles: int = 0
	for raw_line: String in source.split("\n"):
		var line: String = raw_line.trim_suffix("\r")
		if line.is_empty():
			continue
		var fields: PackedStringArray = line.split(" ", false)
		match fields[0]:
			"v":
				if fields.size() != 4 and fields.size() != 7:
					return _invalid("Curated mesh has an invalid vertex record.")
				var position: Dictionary = _vector3(fields, 1)
				if not position.ok:
					return position
				vertices.append(position.value)
				if fields.size() == 7:
					var color: Dictionary = _vector3(fields, 4)
					if not color.ok:
						return color
					var rgb: Vector3 = color.value
					if rgb.x < 0.0 or rgb.x > 1.0 or rgb.y < 0.0 or rgb.y > 1.0 or rgb.z < 0.0 or rgb.z > 1.0:
						return _invalid("Curated mesh contains an out-of-range vertex colour channel.")
					colors.append(Color(rgb.x, rgb.y, rgb.z, 1.0))
				if vertices.size() > MAXIMUM_VERTICES:
					return _invalid("Curated mesh exceeds the vertex limit.")
			"vt":
				if fields.size() != 3:
					return _invalid("Curated mesh has an invalid texture coordinate record.")
				var u: Dictionary = parse_float32(fields[1])
				var v: Dictionary = parse_float32(fields[2])
				if not u.ok:
					return u
				if not v.ok:
					return v
				uvs.append(Vector2(u.value, v.value))
			"vn":
				if fields.size() != 4:
					return _invalid("Curated mesh has an invalid normal record.")
				var normal: Dictionary = _vector3(fields, 1)
				if not normal.ok:
					return normal
				normals.append(normal.value)
			"f":
				if active.is_empty():
					return _invalid("Curated mesh has a triangle without a material group.")
				if fields.size() != 4:
					return _invalid("Curated mesh has an invalid triangle record.")
				for field: int in [1, 3, 2]:
					var index: int = _unified_index(fields[field])
					if index < 0:
						return _invalid("Curated mesh requires unified positive OBJ indices.")
					active.indices.append(index)
				triangles += 1
				if triangles > MAXIMUM_TRIANGLES:
					return _invalid("Curated mesh exceeds the triangle limit.")
			"usemtl":
				if fields.size() != 2:
					return _invalid("Curated mesh has an invalid material record.")
				if not materials.has(fields[1]):
					return _invalid("Curated mesh references unmapped material '%s'." % fields[1])
				if not by_name.has(fields[1]):
					by_name[fields[1]] = {"name": fields[1], "indices": PackedInt32Array()}
					surfaces.append(by_name[fields[1]])
				active = by_name[fields[1]]
			_:
				return _invalid("Curated mesh contains unsupported OBJ record '%s'." % fields[0])
	var consistent: bool = not vertices.is_empty() and not surfaces.is_empty() and normals.size() == vertices.size() \
		and uvs.size() == vertices.size() and (colors.is_empty() or colors.size() == vertices.size())
	for surface: Dictionary in surfaces:
		if surface.indices.is_empty():
			consistent = false
		for index: int in surface.indices:
			if index < 0 or index >= vertices.size():
				consistent = false
	if not consistent:
		return _invalid("Curated mesh has inconsistent geometry arrays.")
	return {"ok": true, "value": {"vertices": vertices, "normals": normals, "uvs": uvs, "colors": colors,
		"surfaces": surfaces}}


static func _build_mesh(parsed: Dictionary, surfaces: Array[Dictionary], materials: Dictionary) -> ArrayMesh:
	var mesh := ArrayMesh.new()
	for surface: Dictionary in surfaces:
		var arrays: Array = []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = parsed.vertices
		arrays[Mesh.ARRAY_NORMAL] = parsed.normals
		arrays[Mesh.ARRAY_TEX_UV] = parsed.uvs
		if not parsed.colors.is_empty():
			arrays[Mesh.ARRAY_COLOR] = parsed.colors
		arrays[Mesh.ARRAY_INDEX] = surface.indices
		var surface_index: int = mesh.get_surface_count()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		mesh.surface_set_name(surface_index, surface.name)
		mesh.surface_set_material(surface_index, materials[surface.name])
	return mesh


static func _vector3(fields: PackedStringArray, first: int) -> Dictionary:
	var x: Dictionary = parse_float32(fields[first])
	var y: Dictionary = parse_float32(fields[first + 1])
	var z: Dictionary = parse_float32(fields[first + 2])
	for value: Dictionary in [x, y, z]:
		if not value.ok:
			return value
	return {"ok": true, "value": Vector3(x.value, y.value, z.value)}


## Positive unified "a/a/a" indices, digits only (NumberStyles.None); -1 if not.
static func _unified_index(value: String) -> int:
	var parts: PackedStringArray = value.split("/")
	if parts.size() != 3:
		return -1
	var numbers: Array[int] = []
	for part: String in parts:
		if part.is_empty() or part.length() > 10:
			return -1
		for index: int in range(part.length()):
			var unit: int = part.unicode_at(index)
			if unit < 48 or unit > 57:
				return -1
		var parsed: int = int(part)
		if parsed > 2147483647:
			return -1
		numbers.append(parsed)
	if numbers[0] <= 0 or numbers[0] != numbers[1] or numbers[0] != numbers[2]:
		return -1
	return numbers[0] - 1


## The .NET float.TryParse(Float, Invariant) binary32 of a finite token.
## The binary64 below comes from the exact integer mantissa and an exactly
## representable power of ten, so its relative error is at most 2^-52 (one
## rounding of a mantissa above 2^53, one division or product). Unless it lies
## within 2^-49 of a binary32 rounding midpoint, rounding it once to binary32
## is the direct rounding; otherwise, or when the token is outside this fast
## form, the exact decimal reader decides. (Godot's own decimal reader is not
## accurate enough to take this shortcut.)
static func parse_float32(token: String) -> Dictionary:
	if _float_grammar == null:
		_float_grammar = RegEx.create_from_string("^([+-]?)([0-9]*)(?:\\.([0-9]*))?(?:[eE]([+-]?[0-9]+))?$")
		for power: int in range(0, 23):
			_powers_of_ten.append(float(10 ** mini(power, 18)) * float(10 ** maxi(0, power - 18)))
	var match: RegExMatch = _float_grammar.search(token)
	if match == null or (match.get_string(2).is_empty() and match.get_string(3).is_empty()) \
			or match.get_string(4).length() > 6:
		return _exact(token)
	var digits: String = (match.get_string(2) + match.get_string(3)).lstrip("0")
	var power: int = -match.get_string(3).length() + (int(match.get_string(4)) if not match.get_string(4).is_empty() else 0)
	if digits.is_empty() or digits.length() > 18 or absi(power) > 22:
		return _exact(token)
	var wide: float = float(int(digits))
	wide = wide / _powers_of_ten[-power] if power < 0 else wide * _powers_of_ten[power]
	if match.get_string(1) == "-":
		wide = -wide
	var bits: int = Float24.store_word(wide)
	var value: float = Float24.read_word(bits)
	var magnitude: int = bits & 0x7fffffff
	if magnitude == 0 or magnitude >= 0x7f7fffff:
		return _exact(token)
	var tolerance: float = absf(wide) * 1.7763568394002505e-15 # 2^-49
	var below: float = Float24.read_word(bits - 1)
	var above: float = Float24.read_word(bits + 1)
	if absf(wide - (value + below) * 0.5) <= tolerance or absf(wide - (value + above) * 0.5) <= tolerance:
		return _exact(token)
	return {"ok": true, "value": value}


static func _exact(token: String) -> Dictionary:
	var parsed: Dictionary = Number.parse_float32(token)
	if not parsed.ok or not parsed.has("bits"):
		return _invalid("Curated mesh contains a non-finite numeric value.")
	var value: float = Float24.read_word(parsed.bits)
	if not is_finite(value):
		return _invalid("Curated mesh contains a non-finite numeric value.")
	return {"ok": true, "value": value}


static func _invalid(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
