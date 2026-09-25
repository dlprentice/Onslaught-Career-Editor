# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends RefCounted
## Exact three-specimen CMSH admission and motion data from
## RetailAquilaWalkerAsset.cs. No filesystem, nodes, clock or simulation owner.
## Matrices are nine row-major Singles followed by three position Singles;
## every arithmetic operation retains its original C# Single store. In
## particular, CMeshPart__InterpolateSegmentTransform (0x004b0d00) interpolates
## all nine HORI words independently, including proper rotations.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Aya = preload("res://Scenes/Shared/retail_aya_texture.gd")
const MAXIMUM_INFLATED_LENGTH: int = 2 * 1024 * 1024
const PROFILES: Dictionary = {
	"walker": {"display_name": "Aquila walker", "root_name": "RetailAquilaWalker", "source_sha256": "D4C8FA752229AF4111B31EFA5FF5928C892736FAA6A807915412767F3CD3C6B2", "source_length": 484616,
		"inflated_length": 932797, "texture_count": 8, "part_count": 63, "surface_count": 54, "animated_count": 20, "cemt_length": 3404,
		"is_walker": true, "base_frame": 0.0, "initial_frame": 1.0, "root_offset": Vector3.ZERO, "cast_shadow": true, "operation": 5,
		"modes": [["walk", 1, 1, 1, 1.0], ["transform", 1, 1, 0, 0.0], ["LegMotion", 1, 100, 99, 1.0 / 99.0]]},
	"jet": {"display_name": "Aquila jet", "root_name": "RetailAquilaJet", "source_sha256": "35AADA1313C3CBB796BA75DB071321035F7005096DA7C148A7514944F4772B4C", "source_length": 334813,
		"inflated_length": 965200, "texture_count": 6, "part_count": 54, "surface_count": 58, "animated_count": 37, "cemt_length": 2044,
		"is_walker": false, "base_frame": null, "initial_frame": 25.0, "root_offset": Vector3(0.0, 0.6706632, 0.0), "cast_shadow": true, "operation": 5,
		"modes": [["walk", 25, 25, 1, 1.0], ["walktofly", 25, 50, 25, 0.04], ["flytowalk", 0, 25, 25, 0.04], ["fly", 0, 0, 1, 1.0]]},
	"cockpit": {"display_name": "Aquila cockpit", "root_name": "RetailAquilaCockpit", "source_sha256": "008B9292C59A5564BA3696F65D5BD51030D3E57250BC792D9D2B7F01292CDD4A", "source_length": 31750,
		"inflated_length": 137757, "texture_count": 3, "part_count": 21, "surface_count": 10, "animated_count": 6, "cemt_length": 4084,
		"is_walker": false, "base_frame": null, "initial_frame": 25.0, "root_offset": Vector3.ZERO, "cast_shadow": false, "operation": 4,
		"modes": [["walktofly", 26, 50, 24, 1.0 / 24.0], ["walk", 25, 25, 1, 1.0], ["flytowalk", 1, 25, 24, 1.0 / 24.0], ["fly", 0, 0, 1, 1.0]]}}
# Exterior COLOROP remains unmeasured and retains MODULATE2X. The cockpit's
# MODULATE is the measured seven-batch/16-read contract carried in the original
# profile. Its zero root offset follows the released position providers;
# FirstFlightWorldView retains ownership of the observed camera orientation.
const LEGS: Array = [[0, 18, 25, [18, 21, 22, 23, 24]], [1, 28, 34, [28, 30, 31, 32, 33]],
	[2, 46, 55, [46, 51, 52, 53, 54]], [3, 3, 12, [3, 8, 9, 10, 11]]]
# Existing observed standing pose: canonical Steam Level 100, raw walker
# state 2 at authored spawn, two samples 100ms apart. The actor root was
# removed; the complete pose-buffer SHA-256 was
# 53FD05BBFCF2E72B9AFBF7E9EC120DDFD5449EC2ED00A79D3A94B2069A4E5465.
const STANDING: Dictionary = {
	3: [0.761326793, 0.359408711, 0.539635826, 0.623082613, -0.635733713, -0.455642889, 0.179302603, 0.683130860, -0.707942486, 0.264985863, -0.240135936, 0.192155838],
	8: [0.999999881, -0.000000067, 0.000000089, 0, 0.853719029, 0.520733486, 0.000000124, -0.520733462, 0.853719112, 0.016658484, 0.667089011, 0.081205942],
	9: [0.999999881, 0, 0.000000129, -0.000000067, 0.853718584, -0.520734130, 0.000000089, 0.520734163, 0.853718716, 0.002022146, -0.316406124, 0.092081674],
	10: [0.999999879, 0.000000059, 0.000000107, 0, 0.835001183, -0.550247591, 0.000000140, 0.550247746, 0.835001243, -0.000014044, 0.526826375, 0.077583322],
	11: [0.999999876, -0.000000101, 0.000000091, 0.000000056, 0.349686880, 0.936866403, 0.000000122, -0.936866271, 0.349687003, -0.004456563, 0.365370782, -0.045191237],
	18: [-0.815748495, -0.450529976, -0.362735548, -0.578401559, 0.632749656, 0.514858875, -0.002438605, 0.629801989, -0.776751876, -0.264029511, 0.235405520, 0.194670677],
	21: [0.999999947, -0.000000081, -0.000000069, -0.000000070, 0.911006247, 0.412392461, 0, -0.412392326, 0.911006596, 0.015948282, 0.667869326, 0.081984562],
	22: [0.999999947, -0.000000088, 0, -0.000000087, 0.907372543, -0.420327126, -0.000000066, 0.420327208, 0.907372909, 0.002016941, -0.331826637, 0.096348314],
	23: [0.999999947, -0.000000101, 0, -0.000000095, 0.813683381, -0.581308174, 0, 0.581308538, 0.813683546, -0.000009314, 0.542245624, 0.073320433],
	24: [0.999999947, 0, -0.000000082, -0.000000101, 0.090553397, 0.995891700, 0, -0.995891584, 0.090553774, -0.003310197, 0.294647794, -0.061619548],
	28: [0.732616259, 0.507456906, -0.453608418, -0.664665069, 0.676933473, -0.316197685, 0.146605998, 0.533149362, 0.833221555, 0.264990639, 0.234743025, 0.190869331],
	30: [0.999999587, 0, -0.000000087, 0, 0.953800761, -0.300438797, -0.000000072, 0.300438816, 0.953800794, 0.016667433, 0.668478490, -0.081851848],
	31: [0.999999587, 0, -0.000000063, 0, 0.953800975, 0.300438154, -0.000000087, -0.300438115, 0.953801019, 0.002014266, -0.329448259, -0.107830470],
	32: [0.999999587, 0.000000058, 0, 0, 0.832961669, 0.553330163, -0.000000063, -0.553330172, 0.832961735, -0.000025600, 0.539871676, -0.061838969],
	33: [0.999999577, 0, 0, 0.000000073, 0.013604437, -0.999907166, -0.000000068, 0.999907204, 0.013604478, -0.000996739, 0.312797201, 0.042775920],
	46: [0.695770255, -0.341931611, -0.631653668, -0.664584183, -0.640052036, -0.385565466, -0.272454292, 0.688052118, -0.672571540, -0.262623694, -0.240139779, 0.192155838],
	51: [0.999999753, -0.000000074, -0.000000182, -0.000000131, 0.853718887, 0.520733426, -0.000000126, -0.520733362, 0.853718923, 0.016676005, 0.667087769, 0.081200642],
	52: [0.999999750, -0.000000171, -0.000000135, -0.000000078, 0.853718513, -0.520734095, -0.000000196, 0.520734065, 0.853718507, 0.002017372, -0.316407125, 0.092092830],
	53: [0.999999750, -0.000000254, 0, -0.000000171, 0.835000958, -0.550247735, -0.000000135, 0.550247673, 0.835001097, -0.000001134, 0.526826393, 0.077580618],
	54: [0.999999753, -0.000000078, -0.000000241, -0.000000240, 0.349686857, 0.936866195, 0, -0.936866345, 0.349686983, -0.004460498, 0.365365977, -0.045196509]
}


static func from_bytes(source: Variant, profile_name: Variant) -> Dictionary:
	if not source is PackedByteArray or not profile_name is String or not PROFILES.has(profile_name):
		return {"ok": false, "error_type": "ArgumentException", "error": "Aquila requires bytes and one reviewed profile: walker, jet or cockpit."}
	var asset := Asset.new()
	asset._profile = PROFILES[profile_name].duplicate(true)
	asset._profile.name = profile_name
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	if not source.is_empty(): hash.update(source)
	if source.size() != asset._profile.source_length or hash.finish().hex_encode().to_upper() != asset._profile.source_sha256:
		return asset.fail("The retained " + asset._profile.display_name + " source does not match its reviewed specimen.")
	var inflated: Dictionary = inflate_aya(source)
	if not inflated.ok: return inflated
	if inflated.value.size() != asset._profile.inflated_length:
		return asset.fail("The retained " + asset._profile.display_name + " has an unexpected decoded length.")
	return asset.parse(inflated.value)


## This framing function is separate for focused comparison with the old
## private inflater. Live admission above always checks the exact source pin.
## It is deliberately not an unpinned file-reader API: the shared decoder is
## stricter about incomplete/trailing zlib than the old private ZLibStream
## helper. All three admitted inputs are byte-exact; malformed-source tests
## compare the public pre-inflate rejection, with helper differences retained
## separately as non-production diagnostics.
static func inflate_aya(source: PackedByteArray) -> Dictionary:
	var output := PackedByteArray()
	var position: int = 0
	var records: int = 0
	var decoder: RefCounted = Aya.new()
	while position < source.size():
		if source.size() - position < 4:
			return {"ok": false, "error_type": "InvalidDataException", "error": "The retained Aquila walker has a truncated AYA record."}
		var declared: int = source.decode_u32(position)
		position += 4
		if declared == 0 or declared > 2147483647 or declared > source.size() - position:
			return {"ok": false, "error_type": "InvalidDataException", "error": "The retained Aquila walker has invalid AYA framing."}
		var bytes: PackedByteArray = decoder._inflate_record(source.slice(position, position + declared), MAXIMUM_INFLATED_LENGTH - output.size())
		if not decoder.error_message.is_empty():
			var message: String = "The archive entry was compressed using an unsupported compression method."
			if decoder.error_message.contains("limit"):
				message = "The retained Aquila walker exceeds its decoded-size limit."
			elif decoder.error_message.contains("trailing compressed"):
				message = "The retained Aquila walker has trailing compressed data."
			return {"ok": false, "error_type": "InvalidDataException", "error": message}
		output.append_array(bytes)
		position += declared
		records += 1
	if records == 0:
		return {"ok": false, "error_type": "InvalidDataException", "error": "The retained Aquila walker contains no AYA records."}
	return {"ok": true, "value": output}


## Parser-test seam only: callers wanting live assets must use from_bytes.
## This mirrors the private decoded parser, hierarchy and clearance pipeline.
static func parse_decoded_for_checks(data: PackedByteArray, profile_name: String) -> Dictionary:
	if not PROFILES.has(profile_name):
		return {"ok": false, "error_type": "ArgumentException", "error": "Unknown Aquila profile."}
	var asset := Asset.new()
	asset._profile = PROFILES[profile_name].duplicate(true)
	asset._profile.name = profile_name
	return asset.parse(data)


class Asset extends RefCounted:
	var _profile: Dictionary
	var _parts: Array[Dictionary] = []
	var _textures: Array[Dictionary] = []
	var _surfaces: int = 0
	var _leg_lengths: Array[PackedFloat32Array] = []
	var _clearance: float = 0.0
	var _data: PackedByteArray
	var _error: Dictionary = {}

	func definition() -> Dictionary:
		return {"profile": _profile.duplicate(true), "parts": _parts.duplicate(true), "textures": _textures.duplicate(true),
			"surface_count": _surfaces, "standing_clearance": _clearance, "leg_lengths": _leg_lengths.duplicate(true)}

	func fail(message: String, type: String = "InvalidDataException") -> Dictionary:
		if _error.is_empty(): _error = {"ok": false, "error_type": type, "error": message}
		return _error.duplicate()

	func fail_tag(prefix: String, offset: int, suffix: String) -> void:
		var display: String = prefix
		var units := PackedInt32Array()
		for index: int in range(prefix.length()): units.append(prefix.unicode_at(index))
		var raw_carrier: bool = false
		for index: int in range(4):
			var code: int = _data[offset + index] if _data[offset + index] < 128 else 63
			units.append(code)
			if code == 0:
				raw_carrier = true
				display += "\\u0000"
			else: display += String.chr(code)
		for index: int in range(suffix.length()): units.append(suffix.unicode_at(index))
		display += suffix
		fail(display)
		if raw_carrier: _error.error_units = units

	func parse(data: PackedByteArray) -> Dictionary:
		_data = data
		var cursor: int = 0
		var cmsh: Dictionary = chunk(cursor, data.size(), "CMSH", 372)
		if not _error.is_empty(): return _error
		cursor = cmsh.end
		var textures: int = integer(cmsh.offset + 4)
		var parts: int = integer(cmsh.offset + 0x15c)
		if textures != _profile.texture_count or parts != _profile.part_count:
			return fail("The retained " + _profile.display_name + " has unexpected CMSH counts.")
		var cmst: Dictionary = chunk(cursor, data.size(), "CMST", textures * 36)
		if not _error.is_empty(): return _error
		cursor = cmst.end
		for index: int in range(textures):
			var msht: Dictionary = chunk(cursor, data.size(), "MSHT", 156)
			if not _error.is_empty(): return _error
			cursor = msht.end
			var texb: Dictionary = chunk(msht.offset, msht.end, "TEXB", 148)
			if not _error.is_empty(): return _error
			_textures.append({"opacity": single(texb.offset), "offset": Vector2(single(texb.offset + 4), single(texb.offset + 8)), "scale": Vector2(single(texb.offset + 12), single(texb.offset + 16))})
			require_end(texb.end, msht.end, "MSHT")
			if not _error.is_empty(): return _error
		for index: int in range(parts):
			var mesp: Dictionary = chunk(cursor, data.size(), "MESP")
			if not _error.is_empty(): return _error
			cursor = mesp.end
			_parts.append(parse_part(mesp, index, parts))
			if not _error.is_empty(): return _error
		for part: Dictionary in _parts:
			var geometry: Variant = part.geometry
			var geometry_owner: int = part.index
			if geometry == null and part.reference != null:
				var reference: int = part.reference
				if reference >= part.index or _parts[reference].reference != null:
					return fail("The retained " + _profile.display_name + " has an unsupported geometry reference.")
				geometry = _parts[reference].geometry
				if geometry == null: return fail("The retained " + _profile.display_name + " references an empty geometry part.")
				part.geometry = geometry
				geometry_owner = reference
			part.geometry_owner = null if geometry == null else geometry_owner
			_surfaces += 0 if geometry == null else geometry.groups.size()
		var camd: Dictionary = chunk(cursor, data.size(), "CAMD", _profile.modes.size() * 36)
		if not _error.is_empty(): return _error
		cursor = camd.end
		validate_animations(camd)
		if not _error.is_empty(): return _error
		var bbox: Dictionary = chunk(cursor, data.size(), "BBOX", 48)
		if not _error.is_empty(): return _error
		var cemt: Dictionary = chunk(bbox.end, data.size(), "CEMT", _profile.cemt_length)
		if not _error.is_empty(): return _error
		require_end(cemt.end, data.size(), "CMSH")
		if not _error.is_empty(): return _error
		var animated: int = 0
		for part: Dictionary in _parts:
			if part.horizontal_count > 1: animated += 1
		if _parts.size() != _profile.part_count or _surfaces != _profile.surface_count or animated != _profile.animated_count:
			return fail("The retained " + _profile.display_name + " does not match its reviewed hierarchy.")
		validate_hierarchy()
		if not _error.is_empty(): return _error
		if _profile.is_walker:
			build_leg_lengths()
			if not _error.is_empty(): return _error
			build_clearance()
			if not _error.is_empty(): return _error
		_data = PackedByteArray()
		return {"ok": true, "value": self}

	func parse_part(mesp: Dictionary, index: int, part_count: int) -> Dictionary:
		var cmsp: Dictionary = chunk(mesp.offset, mesp.end, "CMSP", 316)
		if not _error.is_empty(): return {}
		var cursor: int = cmsp.end
		var number: int = integer(cmsp.offset + 0x88)
		var child_count: int = integer(cmsp.offset + 0x90)
		var virtual_count: int = integer(cmsp.offset + 0xb8)
		var horizontal_count: int = integer(cmsp.offset + 0xbc)
		if number != index or child_count < 0 or child_count > part_count or virtual_count < 1 or virtual_count > 101 or horizontal_count < 1 or horizontal_count > 101:
			fail("The retained " + _profile.display_name + " has invalid part metadata.")
			return {}
		var part: Dictionary = {"index": index, "name": fixed_string(cmsp.offset + 0xdc, 32), "virtual_count": virtual_count, "horizontal_count": horizontal_count,
			"base_transform": transform_at(cmsp.offset + 0x30, cmsp.offset + 0x70), "parent": null, "reference": null, "children": PackedInt32Array(),
			"frame_map": PackedByteArray(), "orientations": [], "positions": PackedVector3Array(), "geometry": null}
		if not _error.is_empty(): return {}
		while cursor < mesp.end:
			var tag: String = read_tag(cursor, mesp.end)
			var record: Dictionary = chunk(cursor, mesp.end, tag)
			if not _error.is_empty(): return {}
			cursor = record.end
			match tag:
				"CHLD":
					if record.length != child_count * 4 or child_count == 0:
						fail("The retained Aquila walker has invalid child metadata.")
						return {}
					part.children = indices(record, child_count, part_count)
				"PRNT": part.parent = index_at(record, part_count, "parent")
				"REFR": part.reference = index_at(record, part_count, "geometry reference")
				"VHFM":
					if record.length != virtual_count:
						fail("The retained Aquila walker has an invalid virtual-frame map.")
						return {}
					part.frame_map = _data.slice(record.offset, record.end)
					for frame: int in part.frame_map:
						if frame >= horizontal_count:
							fail("The retained Aquila walker maps beyond a stored transform.")
							return {}
				"HORI":
					if record.length != horizontal_count * 48:
						fail("The retained Aquila walker has invalid orientation frames.")
						return {}
					part.orientations = []
					for frame: int in range(horizontal_count): part.orientations.append(matrix(record.offset + frame * 48))
				"HPOS":
					if record.length != horizontal_count * 16:
						fail("The retained Aquila walker has invalid position frames.")
						return {}
					part.positions = PackedVector3Array()
					for frame: int in range(horizontal_count): part.positions.append(vector(record.offset + frame * 16))
				"HFOV":
					if record.length != horizontal_count * 4:
						fail("The retained " + _profile.display_name + " has invalid field-of-view frames.")
						return {}
					for frame: int in range(horizontal_count): single(record.offset + frame * 4)
				"PMVB": part.geometry = parse_geometry(record, part.reference != null)
				"BBOX", "PBKT", "CPOS", "CORI", "NMIC": pass
				_:
					fail_tag("The retained Aquila walker contains unsupported part data '", record.offset - 8, "'.")
			if not _error.is_empty(): return {}
		if part.children.size() != child_count or part.frame_map.size() != virtual_count or part.orientations.size() != horizontal_count or part.positions.size() != horizontal_count:
			fail("The retained Aquila walker part is incomplete.")
		return part

	func parse_geometry(pmvb: Dictionary, is_reference: bool) -> Variant:
		var cmvb: Dictionary = chunk(pmvb.offset, pmvb.end, "CMVB", 296)
		if not _error.is_empty(): return null
		var cursor: int = cmvb.end
		var count: int = _data[cmvb.offset + 264]
		var stride: int = integer(cmvb.offset + 276)
		var fvf: int = integer(cmvb.offset + 280)
		var topology: int = integer(cmvb.offset + 284)
		if is_reference:
			if count != 0: fail("The retained Aquila walker has an invalid referenced geometry source.")
			require_end(cursor, pmvb.end, "referenced PMVB")
			return null
		if count > 12 or (count > 0 and (stride != 36 or fvf != 0x152 or topology != 4)):
			fail("The retained Aquila walker has an unsupported geometry profile.")
			return null
		if count == 0:
			require_end(cursor, pmvb.end, "empty PMVB")
			return null
		var geometry: Dictionary = {"vertices": PackedVector3Array(), "normals": PackedVector3Array(), "uvs": PackedVector2Array(), "colors": PackedColorArray(), "groups": []}
		var declared_bytes: int = -1
		var declared_count: int = -1
		for group_index: int in range(count):
			var mmpt: Dictionary = chunk(cursor, pmvb.end, "MMPT", 24)
			if not _error.is_empty(): return null
			cursor = mmpt.end
			var vertex_bytes: int = integer(mmpt.offset)
			var index_bytes: int = integer(mmpt.offset + 4)
			var index_count: int = integer(mmpt.offset + 8)
			var vertex_count: int = integer(mmpt.offset + 12)
			var primitive_count: int = integer(mmpt.offset + 16)
			var active: int = integer(mmpt.offset + 20)
			if active != 1 or index_count < 3 or index_bytes != signed32(index_count * 2) or primitive_count != signed32(index_count - 2) or vertex_count < 1 or vertex_count > 100000 or vertex_bytes != vertex_count * 36:
				fail("The retained Aquila walker has invalid material-group metadata.")
				return null
			if group_index == 0:
				declared_bytes = vertex_bytes
				declared_count = vertex_count
			elif vertex_bytes != declared_bytes or vertex_count != declared_count:
				fail("The retained Aquila walker has inconsistent shared vertices.")
				return null
			var ibuf: Dictionary = chunk(cursor, pmvb.end, "IBUF", index_bytes)
			if not _error.is_empty(): return null
			var vbuf: Dictionary = chunk(ibuf.end, pmvb.end, "VBUF", vertex_bytes if group_index == 0 else 0)
			if not _error.is_empty(): return null
			var texr: Dictionary = chunk(vbuf.end, pmvb.end, "TEXR", 24)
			if not _error.is_empty(): return null
			cursor = texr.end
			if group_index == 0:
				for index: int in range(vertex_count):
					var offset: int = vbuf.offset + index * 36
					var position: Vector3 = vector(offset)
					var normal: Vector3 = vector(offset + 12)
					var uv := Vector2(single(offset + 28), single(offset + 32))
					if not _error.is_empty(): return null
					geometry.vertices.append(map_vector(position))
					geometry.normals.append(normalized(map_vector(normal)))
					geometry.uvs.append(uv)
					var diffuse: int = _data.decode_u32(offset + 24)
					if (diffuse >> 24) != 255:
						fail("The retained Aquila walker has a non-opaque vertex diffuse alpha.")
						return null
					geometry.colors.append(Color(F.value(float((diffuse >> 16) & 255) / 255.0), F.value(float((diffuse >> 8) & 255) / 255.0), F.value(float(diffuse & 255) / 255.0), 1.0))
			var strip := PackedInt32Array()
			for index: int in range(index_count):
				var value: int = _data.decode_u16(ibuf.offset + index * 2)
				if value >= vertex_count:
					fail("The retained Aquila walker contains an out-of-range index.")
					return null
				strip.append(value)
			var triangles: PackedInt32Array = build_triangles(strip)
			if not _error.is_empty(): return null
			var layers := PackedInt32Array()
			for layer: int in range(6): layers.append(integer(texr.offset + layer * 4))
			geometry.groups.append({"triangles": triangles, "texture_indices": layers})
		require_end(cursor, pmvb.end, "PMVB")
		return geometry

	func build_triangles(strip: PackedInt32Array) -> PackedInt32Array:
		var triangles := PackedInt32Array()
		for ordinal: int in range(strip.size() - 2):
			var a: int = strip[ordinal if (ordinal & 1) == 0 else ordinal + 1]
			var b: int = strip[ordinal + 1 if (ordinal & 1) == 0 else ordinal]
			var c: int = strip[ordinal + 2]
			if a != b and b != c and a != c: triangles.append_array(PackedInt32Array([a, b, c]))
		if triangles.is_empty(): fail("The retained Aquila walker contains an empty triangle strip.")
		return triangles

	func validate_animations(camd: Dictionary) -> void:
		for index: int in range(_profile.modes.size()):
			var entry: int = camd.offset + index * 36
			var expected: Array = _profile.modes[index]
			var name: String = fixed_string(entry, 16)
			var start: int = integer(entry + 20)
			var end: int = integer(entry + 24)
			var span: int = integer(entry + 28)
			var increment: float = single(entry + 32)
			if not _error.is_empty(): return
			if name != expected[0] or start != expected[1] or end != expected[2] or span != expected[3] or absf(F.value(increment - F.value(expected[4]))) > F.value(0.000001):
				fail("The retained " + _profile.display_name + " has an unexpected '" + expected[0] + "' animation range.")
				return

	func validate_hierarchy() -> void:
		var claimed := PackedInt32Array()
		claimed.resize(_parts.size())
		claimed.fill(-1)
		for parent: Dictionary in _parts:
			for child: int in parent.children:
				if claimed[child] != -1:
					fail("The retained Aquila walker has a multiply-owned part.")
					return
				claimed[child] = parent.index
		var roots: int = 0
		var globals: Array[PackedFloat32Array] = []
		globals.resize(_parts.size())
		for index: int in range(_parts.size()):
			var part: Dictionary = _parts[index]
			if part.parent == null:
				roots += 1
				if claimed[index] != -1:
					fail("The retained Aquila walker root is also claimed as a child.")
					return
				if _profile.base_frame != null: globals[index] = part_transform(part, _profile.base_frame)
			else:
				if part.parent >= index or claimed[index] != part.parent:
					fail("The retained Aquila walker hierarchy is not reciprocal.")
					return
				if _profile.base_frame != null: globals[index] = compose(globals[part.parent], part_transform(part, _profile.base_frame))
			if _profile.base_frame != null and not approximately(globals[index], part.base_transform, F.value(0.0001)):
				fail("The retained " + _profile.display_name + " authored hierarchy is inconsistent at part " + str(index) + " '" + part.name + "' for frame " + str(int(_profile.base_frame)) + ".")
				return
		if roots != 1:
			fail("The retained Aquila walker must have one hierarchy root.")
			return
		for transform: PackedFloat32Array in global_transforms(_profile.initial_frame):
			for value: float in transform:
				if not is_finite(value):
					fail("The retained " + _profile.display_name + " has an invalid composed pose.")
					return

	func global_transforms(virtual_frame: float, observed: bool = false) -> Array[PackedFloat32Array]:
		var result: Array[PackedFloat32Array] = []
		for part: Dictionary in _parts:
			var local: PackedFloat32Array = standing_transform(part) if observed else part_transform(part, virtual_frame)
			result.append(local if part.parent == null else compose(result[part.parent], local))
		return result

	func build_leg_lengths() -> void:
		for leg: Array in LEGS:
			var values := PackedFloat32Array()
			values.resize(101)
			_leg_lengths.append(values)
		for frame: int in range(1, 101):
			var globals: Array[PackedFloat32Array] = global_transforms(frame)
			for leg: Array in LEGS:
				var length: float = distance(position_of(globals[leg[1]]), position_of(globals[leg[2]]))
				if not is_finite(length) or length <= 0.0:
					fail("The retained Aquila walker has an invalid LegMotion extension.")
					return
				_leg_lengths[leg[0]][frame] = length

	func build_clearance() -> void:
		var globals: Array[PackedFloat32Array] = global_transforms(1.0, true)
		var lowest: float = INF
		for part: Dictionary in _parts:
			if part.geometry == null: continue
			for mapped: Vector3 in part.geometry.vertices:
				var y: float = map_vector(transform_point(globals[part.index], map_vector(mapped))).y
				lowest = minf(lowest, y)
		if not is_finite(lowest):
			fail("The retained Aquila walker has no bounded geometry.")
			return
		_clearance = -lowest

	static func part_transform(part: Dictionary, virtual_frame: float) -> PackedFloat32Array:
		var frame: float = F.value(virtual_frame)
		# Mathf.Clamp leaves NaN unchanged. The supported Godot .NET host's
		# unchecked FloorToInt converts NaN to zero; differential tests pin it.
		var clamped: float = 0.0 if frame < 0.0 else float(part.virtual_count - 1) if frame > part.virtual_count - 1 else frame
		var first: int = 0 if is_nan(clamped) else int(floor(clamped))
		var second: int = mini(first + 1, part.virtual_count - 1)
		var a: int = part.frame_map[first]
		var b: int = part.frame_map[second]
		var weight: float = F.value(clamped - first)
		var result := PackedFloat32Array()
		result.resize(12)
		for index: int in range(9):
			var from: float = part.orientations[a][index]
			result[index] = F.value(from + F.value(F.value(part.orientations[b][index] - from) * weight))
		var p: Vector3 = part.positions[a]
		var q: Vector3 = part.positions[b]
		for axis: int in range(3): result[9 + axis] = F.value(p[axis] + F.value(F.value(q[axis] - p[axis]) * weight))
		return result

	static func standing_transform(part: Dictionary) -> PackedFloat32Array:
		return PackedFloat32Array(STANDING[part.index]) if STANDING.has(part.index) else part_transform(part, 1.0)

	static func compose(a: PackedFloat32Array, b: PackedFloat32Array) -> PackedFloat32Array:
		var result := PackedFloat32Array()
		result.resize(12)
		for row: int in range(3):
			for column: int in range(3):
				result[row * 3 + column] = sum3(a[row * 3], b[column], a[row * 3 + 1], b[column + 3], a[row * 3 + 2], b[column + 6])
		var mapped: Vector3 = transform_point(a, position_of(b))
		result[9] = mapped.x
		result[10] = mapped.y
		result[11] = mapped.z
		return result

	static func transform_point(transform: PackedFloat32Array, value: Vector3) -> Vector3:
		return Vector3(F.value(sum3(transform[0], value.x, transform[1], value.y, transform[2], value.z) + transform[9]),
			F.value(sum3(transform[3], value.x, transform[4], value.y, transform[5], value.z) + transform[10]),
			F.value(sum3(transform[6], value.x, transform[7], value.y, transform[8], value.z) + transform[11]))

	static func sum3(a: float, b: float, c: float, d: float, e: float, f: float) -> float:
		return F.value(F.value(F.value(a * b) + F.value(c * d)) + F.value(e * f))

	static func position_of(transform: PackedFloat32Array) -> Vector3:
		return Vector3(transform[9], transform[10], transform[11])

	static func map_vector(value: Vector3) -> Vector3:
		return Vector3(value.x, -value.z, -value.y)

	static func to_godot(transform: PackedFloat32Array) -> Transform3D:
		return Transform3D(Basis(Vector3(transform[0], -transform[6], -transform[3]),
			Vector3(-transform[2], transform[8], transform[5]), Vector3(-transform[1], transform[7], transform[4])), map_vector(position_of(transform)))

	static func squared_length(value: Vector3) -> float:
		return sum3(value.x, value.x, value.y, value.y, value.z, value.z)

	static func distance(a: Vector3, b: Vector3) -> float:
		return F.value(sqrt(squared_length(a - b)))

	static func normalized(value: Vector3) -> Vector3:
		var length: float = F.value(sqrt(squared_length(value)))
		return Vector3.ZERO if length == 0.0 else Vector3(F.value(value.x / length), F.value(value.y / length), F.value(value.z / length))

	static func approximately(a: PackedFloat32Array, b: PackedFloat32Array, tolerance: float) -> bool:
		for index: int in range(9):
			if not absf(F.value(a[index] - b[index])) <= tolerance: return false
		return distance(position_of(a), position_of(b)) <= tolerance

	func transform_at(orientation_offset: int, position_offset: int) -> PackedFloat32Array:
		var result: PackedFloat32Array = matrix(orientation_offset)
		var position: Vector3 = vector(position_offset)
		result.append_array(PackedFloat32Array([position.x, position.y, position.z]))
		return result

	func matrix(offset: int) -> PackedFloat32Array:
		var result := PackedFloat32Array()
		for delta: int in [0, 4, 8, 16, 20, 24, 32, 36, 40]: result.append(single(offset + delta))
		return result

	func indices(record: Dictionary, count: int, limit: int) -> PackedInt32Array:
		var result := PackedInt32Array()
		for index: int in range(count):
			var value: int = integer(record.offset + index * 4)
			if value < 0 or value >= limit:
				fail("The retained Aquila walker contains an out-of-range part index.")
				return result
			result.append(value)
		return result

	func index_at(record: Dictionary, limit: int, role: String) -> int:
		if record.length != 4:
			fail("The retained Aquila walker has invalid " + role + " metadata.")
			return 0
		var value: int = integer(record.offset)
		if value < 0 or value >= limit: fail("The retained Aquila walker has an out-of-range " + role + ".")
		return value

	func chunk(cursor: int, end: int, expected: String, exact: Variant = null) -> Dictionary:
		if cursor < 0 or end > _data.size() or cursor + 8 > end:
			fail("The retained Aquila walker ended before " + expected + ".")
			return {}
		var actual: String = read_tag(cursor, end)
		var length: int = integer(cursor + 4)
		var offset: int = cursor + 8
		var next: int = offset + length
		if next > 2147483647 or next < -2147483648:
			fail("The retained Aquila walker has an overflowing chunk length.")
			return {}
		if actual != expected or length < 0 or next > end or (exact != null and length != exact):
			if expected.contains(String.chr(0xfffd)):
				fail_tag("The retained Aquila walker has an invalid ", cursor, " chunk.")
			else: fail("The retained Aquila walker has an invalid " + expected + " chunk.")
			return {}
		return {"offset": offset, "length": length, "end": next}

	func read_tag(offset: int, end: int) -> String:
		if offset < 0 or offset + 4 > end or end > _data.size():
			fail("The retained Aquila walker ended before a chunk tag.")
			return ""
		# Invalid tags can contain NUL, which Godot String cannot carry. A
		# non-ASCII sentinel keeps tag equality exact without decoding NUL;
		# unsupported-part diagnostics below preserve authoritative raw units.
		return ascii(offset, 4, true)

	func fixed_string(offset: int, length: int) -> String:
		if offset < 0 or offset + length > _data.size():
			fail("The retained Aquila walker has a truncated name.")
			return ""
		var count: int = 0
		while count < length and _data[offset + count] != 0: count += 1
		return ascii(offset, count)

	func ascii(offset: int, length: int, tag: bool = false) -> String:
		var text: String = ""
		for index: int in range(length):
			var value: int = _data[offset + index]
			text += String.chr(0xfffd if tag and value == 0 else value if value < 128 else 63)
		return text

	func integer(offset: int) -> int:
		if offset < 0 or offset + 4 > _data.size():
			fail("The retained Aquila walker ended before an integer field.")
			return 0
		return _data.decode_s32(offset)

	func single(offset: int) -> float:
		integer(offset)
		if not _error.is_empty(): return 0.0
		var value: float = _data.decode_float(offset)
		if not is_finite(value): fail("The retained Aquila walker contains a non-finite number.")
		return value

	func vector(offset: int) -> Vector3:
		return Vector3(single(offset), single(offset + 4), single(offset + 8))

	func require_end(cursor: int, expected: int, role: String) -> void:
		if cursor != expected: fail("The retained Aquila walker has trailing " + role + " data.")

	static func signed32(value: int) -> int:
		var word: int = value & 0xffffffff
		return word if word < 2147483648 else word - 4294967296
