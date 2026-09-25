# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## The released Level 100 base-world hierarchy idle loops, decoded from the
## hash-pinned level100-static-world-animation.json.
##
## frameMaps is the released VHFM byte array of every directly authored mover:
## one entry per virtual frame, naming the HORI/HPOS pose played on that frame.
## Its shape separates an idle cycle from a one-shot by exact integer tests:
## holds_at_end (the last two entries select the same pose, the saturation of a
## triggered one-shot holding its final pose: ft_sam holds pose 9 for 11 frames,
## ft_blaster pose 17 for 22, ft_pulse pose 17 for 83) and closes_on_start (the
## first and last entries match, so a cycle is one frame shorter than its frame
## count). Over the shipped file those flags split the six meshes 3/3, matching
## the WRES active flag in level100-static-world.json: the three cyclic meshes
## are the three active facilities (Forseti Docks, Radar Station, Forseti Solar
## Pod) and the saturating ones the four inactive turrets, so no trigger is
## invented for the turrets.
##
## decode() returns {ok, value: {frames_per_second, meshes: {key: mesh}}} where
## each mesh is {mesh_key, virtual_frame_count, playback, loop_frame_count,
## resource_path, parts: [{part, name, obj_vertex_start, obj_vertex_count,
## frames: [{basis: PackedFloat32Array(9), origin: PackedFloat32Array(3)}]}]}.

const Json = preload("res://Client/manifest_json.gd")

enum Playback { CYCLIC_LOOP = 0, ONE_SHOT_HOLD = 1 }

const EXPECTED_MANIFEST_SHA256: String = "B826DC2D1F62069E3285F4F8CDDEAFB84511519B32065CF6C028615498AFA9C3"
const EXPECTED_SCHEMA: String = "onslaught.level100-static-world-animation.v1"
const RETAIL_HIERARCHY_PLAYBACK_HZ: int = 20
const EXPECTED_VIRTUAL_FRAME_COUNTS: Dictionary = {"FB_Docks": 26, "FB_Solar_Pod": 11, "FB_radar_station": 26,
	"ft_blaster": 41, "ft_pulse": 101, "ft_sam": 21}
const MAXIMUM_MANIFEST_BYTES: int = 512_000


static func decode(bytes: PackedByteArray) -> Dictionary:
	if bytes.is_empty() or bytes.size() > MAXIMUM_MANIFEST_BYTES or Json.sha256_hex(bytes) != EXPECTED_MANIFEST_SHA256:
		return _invalid("The locally materialized Level 100 static-world animation manifest is missing or changed.")
	var parsed: Dictionary = Json.parse(bytes)
	if not parsed.ok:
		return parsed
	var root: Variant = parsed.value
	if root == null:
		return _invalid("The Level 100 static-world animation manifest is empty.")
	var meshes_source: Variant = Json.field(root, "Meshes", {})
	var frames_per_second: Variant = Json.field(root, "FramesPerSecond", 0)
	if Json.field(root, "Schema", "") != EXPECTED_SCHEMA or frames_per_second != RETAIL_HIERARCHY_PLAYBACK_HZ \
			or not meshes_source is Dictionary or meshes_source.size() != EXPECTED_VIRTUAL_FRAME_COUNTS.size():
		return _invalid("The Level 100 static-world animation schema, rate or mesh count changed.")
	var meshes: Dictionary = {}
	for mesh_key: String in meshes_source:
		var record: Variant = meshes_source[mesh_key]
		if not EXPECTED_VIRTUAL_FRAME_COUNTS.has(mesh_key) \
				or Json.field(record, "VirtualFrameCount", 0) != EXPECTED_VIRTUAL_FRAME_COUNTS[mesh_key]:
			return _invalid("The Level 100 static-world animated mesh set changed at '%s'." % mesh_key)
		var mesh: Dictionary = _decode_mesh(mesh_key, record)
		if not mesh.ok:
			return mesh
		meshes[mesh_key] = mesh.value
	return {"ok": true, "value": {"frames_per_second": frames_per_second, "meshes": meshes}}


static func _decode_mesh(mesh_key: String, record: Dictionary) -> Dictionary:
	var virtual_frames: int = Json.field(record, "VirtualFrameCount", 0)
	var frame_maps: Variant = Json.field(record, "FrameMaps", {})
	if not frame_maps is Dictionary or frame_maps.is_empty():
		return _invalid("The Level 100 static-world animation for '%s' has no released frame map." % mesh_key)
	var holds_at_end: bool = true
	var closes_on_start: bool = true
	for key: String in frame_maps:
		var frame_map: Variant = frame_maps[key]
		if not frame_map is Array or frame_map.size() != virtual_frames or frame_map.size() < 2:
			return _invalid("The Level 100 static-world frame map for '%s' does not cover its virtual frames." % mesh_key)
		holds_at_end = holds_at_end and frame_map[-1] == frame_map[-2]
		closes_on_start = closes_on_start and frame_map[0] == frame_map[-1]
	var playback: int = Playback.ONE_SHOT_HOLD if holds_at_end else Playback.CYCLIC_LOOP
	# A cycle that closes on its start pose repeats that pose as its last
	# virtual frame, so playing it would stall for one frame every lap.
	var loop_frames: int = 0
	if playback == Playback.CYCLIC_LOOP:
		loop_frames = virtual_frames - 1 if closes_on_start else virtual_frames
	var obj_vertex_count: int = Json.field(record, "ObjVertexCount", 0)
	var parts: Array[Dictionary] = []
	for part: Variant in Json.field(record, "Parts", []):
		var frames_source: Variant = Json.field(part, "Frames", null)
		if frames_source == null:
			continue
		var name: String = Json.field(part, "Name", "")
		var start: int = Json.field(part, "ObjVertexStart", 0)
		var count: int = Json.field(part, "ObjVertexCount", 0)
		if not frames_source is Array or frames_source.size() != virtual_frames or start < 1 or count < 1 \
				or start + count - 1 > obj_vertex_count:
			return _invalid("The Level 100 static-world animated part '%s/%s' is inconsistent." % [mesh_key, name])
		var frames: Array[Dictionary] = []
		for frame: Variant in frames_source:
			var basis: Variant = Json.field(frame, "Basis", [])
			var origin: Variant = Json.field(frame, "Origin", [])
			if not basis is Array or not origin is Array or basis.size() != 9 or origin.size() != 3 \
					or not _all_finite(basis) or not _all_finite(origin):
				return _invalid("The Level 100 static-world animated part '%s/%s' has an invalid frame." % [mesh_key, name])
			# PackedFloat32Array stores each exact binary64 as its binary32 cast.
			frames.append({"basis": PackedFloat32Array(basis), "origin": PackedFloat32Array(origin)})
		parts.append({"part": int(Json.field(part, "Part", 0)), "name": name, "obj_vertex_start": start,
			"obj_vertex_count": count, "frames": frames})
	if parts.is_empty():
		return _invalid("The Level 100 static-world animation for '%s' binds no part." % mesh_key)
	return {"ok": true, "value": {"mesh_key": mesh_key, "virtual_frame_count": virtual_frames, "playback": playback,
		"loop_frame_count": loop_frames, "resource_path": String(Json.field(record, "ResourcePath", "")), "parts": parts}}


static func _all_finite(values: Array) -> bool:
	for value: Variant in values:
		if typeof(value) not in [TYPE_INT, TYPE_FLOAT] or not is_finite(float(value)):
			return false
	return true


static func _invalid(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
