# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Scenery hierarchy playback (static_world_animation.gd) against the golden
## recorded from the retired C# driver (1bb29345 Level100StaticWorldAsset.cs,
## kept in StaticAnimationChecks.cs until its retirement): raw transform words
## and refusals, synthetic rigs (clock, LCM, aliases, malformed and freed
## bindings) and the pinned production tracks, with the recorded inputs.
## Also the native transport admission and detachment. Standard engine:
##   --script res://Scenes/World/static_animation_checks.gd -- <static-animation.golden> <report.json>
const StaticAnimation = preload("res://Scenes/World/static_world_animation.gd")
const Manifest = preload("res://Client/static_world_animation_manifest.gd")
const MANIFEST_PATH: String = "res://Assets/Level100/StaticWorld/level100-static-world-animation.json"
const ARGUMENT_TYPES: Array[String] = ["ArgumentException", "ArgumentOutOfRangeException", "ArgumentNullException"]
var counts: Dictionary = {}
var failures: Array[Dictionary] = []


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("Usage: -- <static-animation.golden> <report.json>")
		quit(2)
		return
	var golden: Variant = bytes_to_var(FileAccess.get_file_as_bytes(args[0]))
	if not golden is Array or golden.is_empty():
		push_error("The static animation golden is missing or unreadable.")
		quit(2)
		return
	var pointer: int = Input.mouse_mode
	var rigs: Array = []
	for entry: Dictionary in golden:
		match String(entry.kind):
			"transform":
				_transform(entry)
			"null_bindings":
				var refused: Dictionary = StaticAnimation.create(20, null)
				_error("playback", "null binding list", refused, entry.expected_error)
			"rig":
				rigs.append(entry)
				_rig(entry)
			"detached_copy":
				_native_admission(entry)
			_:
				_check("golden", "known entry kind " + String(entry.kind), false, true)
	_check("golden", "rig families", rigs.size(), 34)
	_production_tracks(rigs.back())
	_check("golden", "pointer untouched", Input.mouse_mode, pointer)
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		push_error("Cannot write the static animation report.")
		quit(2)
		return
	file.store_string(JSON.stringify(report, "  ", false) + "\n")
	file.close()
	print("static animation checks: %d groups, %d failures" % [counts.size(), failures.size()])
	quit(0 if failures.is_empty() else 1)


func _transform(entry: Dictionary) -> void:
	var result: Dictionary = StaticAnimation.to_obj_space_transform(entry.frame)
	if entry.has("expected"):
		_check("transform", "raw words", [result.ok, _words(result.value) if result.ok else null],
			[true, entry.expected])
	else:
		_error("transform", "refusal order", result, entry.expected_error)


func _rig(entry: Dictionary) -> void:
	var nodes: Array = []
	var groups: Dictionary = {}
	var bindings: Array = []
	for index: int in entry.specs.size():
		var spec: Dictionary = entry.specs[index]
		if spec.null_binding:
			bindings.append(null)
			continue
		var node: Variant = null
		if not spec.null_node:
			var key: int = index + 1000 if int(spec.node_group) < 0 else int(spec.node_group)
			if not groups.has(key):
				groups[key] = nodes.size()
				var made := MeshInstance3D.new()
				made.transform = Transform3D(Basis.IDENTITY, Vector3(900 + index, -700 - index, 31))
				nodes.append(made)
			node = nodes[groups[key]]
		bindings.append({"mesh": null if spec.null_mesh else {"playback": spec.playback, "loop_frame_count": spec.loop_frames},
			"part": null if spec.null_part else {"frames": spec.frames}, "node": node})
	var created: Dictionary = StaticAnimation.create(entry.fps, bindings)
	_check("rig", "native owner created", created.ok, true)
	if not created.ok:
		return
	var owner: RefCounted = created.value
	for step: Dictionary in entry.steps:
		if step.has("free_node"):
			nodes[step.free_node].free()
		elif step.has("delta_bits"):
			_error("rig", step.label, owner.update(_single(step.delta_bits)), step.expected_error)
		else:
			var state: Dictionary = owner.host_snapshot()
			var expected: Dictionary = step.state
			_check("rig", step.label + " rate and count", [state.frames_per_second, state.binding_count],
				[entry.fps, entry.specs.size()])
			_check("rig", step.label + " elapsed", state.elapsed_seconds_bits, expected.elapsed_bits)
			_check("rig", step.label + " shown frames", state.shown_frames, expected.shown_frames)
			for index: int in nodes.size():
				if expected.transforms[index] != null and is_instance_valid(nodes[index]):
					_check("rig", "%s node %d" % [step.label, index], _words(nodes[index].transform), expected.transforms[index])
	for node: Variant in nodes:
		if is_instance_valid(node):
			node.free()


# The golden's last rig is the pinned production manifest, as the retired
# driver's C# decoder projected it; the native decoder must give the same rows.
func _production_tracks(entry: Dictionary) -> void:
	var decoded: Dictionary = Manifest.decode(FileAccess.get_file_as_bytes(MANIFEST_PATH))
	_check("production", "manifest decodes", decoded.ok, true)
	if not decoded.ok:
		return
	var rows: Array = []
	for mesh: Dictionary in decoded.value.meshes.values():
		for part: Dictionary in mesh.parts:
			var frames: Array = []
			for frame: Dictionary in part.frames:
				frames.append({"basis_bits": _bits(frame.basis), "origin_bits": _bits(frame.origin)})
			rows.append({"playback": mesh.playback, "loop_frames": mesh.loop_frame_count, "frames": frames})
	_check("production", "rate", decoded.value.frames_per_second, entry.fps)
	_check("production", "part rows", rows.size(), entry.specs.size())
	for index: int in mini(rows.size(), entry.specs.size()):
		var spec: Dictionary = entry.specs[index]
		_check("production", "row %d" % index, rows[index], {"playback": spec.playback, "loop_frames": spec.loop_frames,
			"frames": spec.frames})
	_check("production", "production steps recorded", entry.steps.size(), 1 + 2 * 271)


func _native_admission(entry: Dictionary) -> void:
	var g: String = "admission"
	_refused(g, StaticAnimation.create(20, null), "NullReferenceException")
	_refused(g, StaticAnimation.create(20, 1), "ArgumentException")
	_refused(g, StaticAnimation.create(20.5, []), "ArgumentException")
	_refused(g, StaticAnimation.create(2147483648, []), "ArgumentException")
	_refused(g, StaticAnimation.to_obj_space_transform({"basis_bits": PackedInt64Array([0, 0, 0, 0, 0, 0, 0, 0, 0])}), "ArgumentException")
	_refused(g, StaticAnimation.to_obj_space_transform({"basis_bits": PackedInt64Array([-1]), "origin_bits": PackedInt64Array([0, 0, 0])}), "ArgumentException")
	_refused(g, StaticAnimation.to_obj_space_transform({"basis_bits": PackedInt32Array([0, 0, 0, 0, 0, 0, 0, 0, 0]), "origin_bits": PackedInt64Array([0, 0, 0])}), "ArgumentException")
	_refused(g, StaticAnimation.create(20, [{}]), "ArgumentException")
	_refused(g, StaticAnimation.create(20, [{"mesh": null, "part": null, "node": 123}]), "ArgumentException")

	# The deliberate immutable transport boundary: changing every supplied
	# container after creation cannot reach the admitted native track.
	var node := MeshInstance3D.new()
	var sentinel := Transform3D(Basis.IDENTITY, Vector3(900, -700, 31))
	node.transform = sentinel
	var frame_rows: Array = []
	for index: int in 4:
		frame_rows.append(_frame_facts(index))
	var mesh: Dictionary = {"playback": 0, "loop_frame_count": 4}
	var part: Dictionary = {"frames": frame_rows}
	var bindings: Array = [{"mesh": mesh, "part": part, "node": node}]
	var created: Dictionary = StaticAnimation.create(20, bindings)
	_check(g, "created", created.ok, true)
	if created.ok:
		var owner: RefCounted = created.value
		_check(g, "configuration applies no frame", _words(node.transform), _words(sentinel))
		mesh.loop_frame_count = 1
		frame_rows[1].basis_bits = PackedInt64Array([0, 0, 0, 0, 0, 0, 0, 0, 0])
		frame_rows.clear()
		part.frames = null
		bindings.clear()
		_check(g, "update", owner.update(_single(0x3d50e560)).ok, true)
		_check(g, "detached track", _words(node.transform), entry.expected)
		var snapshot: Dictionary = owner.host_snapshot()
		snapshot.elapsed_seconds_bits = 0
		snapshot.shown_frames[0] = 99
		var again: Dictionary = owner.host_snapshot()
		_check(g, "snapshots detach selected frames", again.shown_frames, PackedInt32Array([1]))
		var bytes := PackedByteArray()
		bytes.resize(8)
		bytes.encode_double(0, _single(0x3d50e560))
		_check(g, "snapshots detach the clock", again.elapsed_seconds_bits, bytes.decode_s64(0))
	node.free()


static func _frame_facts(index: int) -> Dictionary:
	var basis: Array = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] if index % 2 == 0 \
		else [0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
	return {"basis_bits": _bits(PackedFloat32Array(basis)),
		"origin_bits": _bits(PackedFloat32Array([index, -index, index * 0.25]))}


static func _bits(values: PackedFloat32Array) -> PackedInt64Array:
	var bytes: PackedByteArray = values.to_byte_array()
	var words := PackedInt64Array()
	for offset: int in range(0, bytes.size(), 4):
		words.append(bytes.decode_u32(offset))
	return words


# C# TransformWords order: Basis.X, Basis.Y, Basis.Z columns, then origin.
# The wire format stores basis rows, so column i component j is row j word i.
static func _words(transform: Transform3D) -> PackedInt64Array:
	var bytes: PackedByteArray = var_to_bytes(transform)
	var words := PackedInt64Array()
	for column: int in 3:
		for row: int in 3:
			words.append(bytes.decode_u32(4 + (row * 3 + column) * 4))
	for index: int in 3:
		words.append(bytes.decode_u32(40 + index * 4))
	return words


static func _single(bits: int) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_u32(0, bits)
	return bytes.decode_float(0)


func _error(group: String, name: String, result: Dictionary, expected: Variant) -> void:
	if expected == null:
		_check(group, name + " succeeds", [result.ok, result.get("error_type")], [true, null])
		return
	_check(group, name + " type", [result.ok, result.get("error_type")], [false, expected.type])
	if String(expected.type) in ARGUMENT_TYPES:
		_check(group, name + " parameter", String(result.get("parameter", "")), expected.param)


func _refused(group: String, result: Dictionary, type: String) -> void:
	_check(group, "refuses as " + type, [result.ok, result.get("error_type")], [false, type])


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if typeof(actual) != typeof(expected) or actual != expected:
		failures.append({"group": group, "name": name, "actual": str(actual), "expected": str(expected)})
