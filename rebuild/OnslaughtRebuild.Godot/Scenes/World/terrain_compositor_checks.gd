# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-engine exact comparison with the unchanged C# compositor. The two
## arguments are an existing private value fixture and a fresh owned report.
## No texture, mesh, scene, input or gameplay owner is created by the subject.
const TerrainCompositor = preload("res://Client/terrain_compositor.gd")
const REQUIRED: Array[String] = ["admission", "root", "tiles", "pines", "arithmetic", "boundaries", "read_only"]
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _completed: Array[String] = []
var _report: String
var _finished: bool = false
var _compared_bytes: int = 0
var _lifetime_release: Dictionary = {}


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if Engine.is_editor_hint() or DisplayServer.get_name() != "headless" or args.size() != 2 \
		or not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] or FileAccess.file_exists(args[1]):
		quit(2)
		return
	_report = args[1]
	create_timer(150.0).timeout.connect(func() -> void:
		if not _finished:
			_failures.append({"group": "completion", "name": "compositor harness timed out"})
			_finish())
	var file := FileAccess.open(args[0], FileAccess.READ)
	if file == null:
		quit(2)
		return
	var reference: Variant = file.get_var(false)
	file.close()
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["terrain_compositor_reference"]:
		push_error("Compositor reference fixture is incomplete.")
		quit(2)
		return
	var pointer: int = Input.mouse_mode
	var source: PackedByteArray = FileAccess.get_file_as_bytes(reference.hierarchy_path)
	_check("read_only", "hierarchy identity", _sha(source), reference.hierarchy_sha256)
	_check("read_only", "root identity", _sha(reference.root_bytes), reference.root_sha256)
	if _admission_cases(source, reference): _completed.append("admission")
	var admitted: Dictionary = TerrainCompositor.from_bytes(source, reference.sun, reference.ambient)
	_check("admission", "unchanged pinned hierarchy admitted", admitted.get("ok"), true)
	if not admitted.get("ok", false):
		_finish()
		return
	var owner: RefCounted = admitted.value
	admitted.clear()
	# The constructor retained parsed copies. Changing the caller's byte array
	# cannot alter its input after its hash has passed.
	source[20] ^= 0xff
	if await _root_case(owner, reference): _completed.append("root")
	if _tile_cases(owner, reference.tiles): _completed.append("tiles")
	if _pine_cases(owner, reference.pines): _completed.append("pines")
	if _arithmetic_cases(reference): _completed.append("arithmetic")
	if _boundary_cases(owner, reference.boundaries): _completed.append("boundaries")
	var owner_ref: WeakRef = weakref(owner)
	owner = null
	# _run resumes inside _root_case's completion signal; its owner argument
	# stays on that coroutine stack until the signal unwinds. Record the
	# immediate observation, then require release after exactly one frame.
	# A separate boolean helper avoids retaining get_ref()'s temporary value
	# in this suspended function while observing the weak reference.
	_lifetime_release["retained_in_resuming_frame"] = _owner_alive(owner_ref)
	await process_frame
	if _finished: return
	_lifetime_release["alive_after_one_frame"] = _owner_alive(owner_ref)
	_check("read_only", "compositor releases without cycles after coroutine unwinds", _lifetime_release.alive_after_one_frame, false)
	_check("read_only", "pointer ownership unchanged", Input.mouse_mode, pointer)
	_check("read_only", "retained hierarchy unchanged", _sha(FileAccess.get_file_as_bytes(reference.hierarchy_path)), reference.hierarchy_sha256)
	_check("read_only", "retained root unchanged", _sha(FileAccess.get_file_as_bytes(reference.root_path)), reference.root_sha256)
	_completed.append("read_only")
	await process_frame
	_finish()


func _admission_cases(source: PackedByteArray, reference: Dictionary) -> bool:
	for row: Dictionary in reference.admission:
		var changed: Variant
		match row.kind:
			"null": changed = null
			"truncate": changed = source.slice(0, row.argument)
			"append":
				changed = source.duplicate()
				changed.append(row.argument)
			"flip":
				changed = source.duplicate()
				changed[row.argument] ^= 1
			_: return false
		var result: Dictionary = TerrainCompositor.from_bytes(changed, reference.sun, reference.ambient)
		_check("admission", "%s/%d refused" % [row.kind, row.argument], result.get("ok"), false)
		_check("admission", "%s/%d exception type" % [row.kind, row.argument], result.get("error_type"), row.error_type)
		_check("admission", "%s/%d has no partial owner" % [row.kind, row.argument], result.has("value"), false)
		if row.kind != "null":
			_check("admission", "identity checked before header or length", result.get("error"),
				"Level 100 terrain hierarchy does not match its retail-derived identity.")
	for invalid: Variant in [true, 1, 1.0, "LTH1", [], {}]:
		_check("admission", "wrong byte carrier refused: " + type_string(typeof(invalid)),
			TerrainCompositor.from_bytes(invalid, reference.sun, reference.ambient).get("error_type"), "ArgumentException")
	for invalid: Variant in [null, true, 1.0, -1, 0x100000000]:
		_check("admission", "wrong sun carrier refused", TerrainCompositor.from_bytes(source, invalid, reference.ambient).get("error_type"), "ArgumentException")
		_check("admission", "wrong ambient carrier refused", TerrainCompositor.from_bytes(source, reference.sun, invalid).get("error_type"), "ArgumentException")
		_check("admission", "wrong diffuse light refused", TerrainCompositor.terrain_vertex_diffuse(invalid, 0).get("error_type"), "ArgumentException")
	var uninitialized: RefCounted = TerrainCompositor.new()
	_check("admission", "bare new is not an admitted owner", uninitialized.render_tile(PackedByteArray(), 0, 0, 0, 0, 0).get("error_type"), "InvalidOperationException")
	# The pin makes malformed internal structure unreachable at public Create.
	# These bounded checks separately falsify the new reader's hard-EOF latch;
	# they do not claim C# admitted any unhashed malformed hierarchy.
	var reader = TerrainCompositor.HierarchyReader.new(PackedByteArray([1, 2, 3]))
	_check("reader", "primitive EOF is explicit", reader.u32(), 0)
	_check("reader", "primitive EOF preserves exception kind", reader.error.get("error_type"), "EndOfStreamException")
	_check("reader", "subsequent read cannot clear failure", reader.u8(), 0)
	_check("reader", "failure stops offset advance", reader.position, 0)
	reader = TerrainCompositor.HierarchyReader.new(PackedByteArray([1, 2, 3]))
	_check("reader", "short exact blob refuses", reader.exact(4), PackedByteArray())
	_check("reader", "short blob failure kind", reader.error.get("error_type"), "InvalidDataException")
	_check("reader", "later validation preserves first failure", reader.invalid("later").get("error"), "Level 100 terrain hierarchy is truncated.")
	return true


func _root_case(owner: RefCounted, reference: Dictionary) -> bool:
	var destination := PackedByteArray()
	destination.resize(TerrainCompositor.ROOT_TEXTURE_LENGTH)
	for y: int in range(64):
		for x: int in range(64):
			var result: Dictionary = owner.render_tile(destination, 0, x, y, x, y)
			_check("root_tile", "%d/%d" % [x, y], result.get("ok"), true)
			if not result.get("ok", false): return false
		if y % 8 == 7:
			await process_frame
			if _finished: return false
	_check("root", "all 524288 fixed root bytes, including detached source mutation", destination, reference.root_bytes)
	_check("root", "unchanged pinned root SHA256", _sha(destination), reference.root_sha256)
	return true


func _tile_cases(owner: RefCounted, cases: Array) -> bool:
	_check("tiles", "bounded sample count", cases.size(), 32)
	var seen_shadow: bool = false
	var seen_overlap: bool = false
	var seen_layers: bool = false
	var levels: Dictionary = {}
	for row: Dictionary in cases:
		var destination := PackedByteArray()
		destination.resize(TerrainCompositor.ROOT_TEXTURE_LENGTH)
		destination.fill(0xa5)
		var result: Dictionary = owner.render_tile(destination, row.level, row.tile_x, row.tile_y, row.slot_x, row.slot_y)
		_check("tiles", row.name + " accepted", result.get("ok"), true)
		if not result.get("ok", false): return false
		var size: int = 8 << row.level
		var expected := PackedByteArray()
		expected.resize(destination.size())
		expected.fill(0xa5)
		var block: PackedByteArray = row.bytes
		for y: int in range(size):
			var offset: int = ((row.slot_y * size + y) * 512 + row.slot_x * size) * 2
			for x: int in range(size * 2): expected[offset + x] = block[y * size * 2 + x]
		_check("tiles", row.name + " exact block and untouched destination surround", destination, expected)
		_check("tiles", row.name + " exact full destination hash", _sha(destination), row.cache_sha256)
		seen_shadow = seen_shadow or row.has_shadow
		seen_overlap = seen_overlap or row.pine_count > 1
		seen_layers = seen_layers or row.layers > 1
		levels[row.level] = true
	_check("tiles", "all four higher resolutions covered", levels.size(), 4)
	_check("tiles", "real bitmask shadow covered", seen_shadow, true)
	_check("tiles", "ordered overlapping pine shadows covered", seen_overlap, true)
	_check("tiles", "multiple material layers covered", seen_layers, true)
	return true


func _pine_cases(owner: RefCounted, cases: Array) -> bool:
	_check("pines", "bounded five-resolution fixture count", cases.size(), 5)
	var saved_pines: PackedInt32Array = owner._pines
	var saved_alpha: PackedByteArray = owner._pine_alpha
	for row: Dictionary in cases:
		owner._pines = row.descriptors
		owner._pine_alpha = row.alpha
		var block: PackedInt32Array = row.before.duplicate()
		owner._apply_pine_shadows(block, 8 << row.level, row.level, 0, 0)
		_check("pines", "level %d signed origins, clipping, alpha>=32 skip and reverse descriptor order" % row.level, block, row.after)
	owner._pines = saved_pines
	owner._pine_alpha = saved_alpha
	return true


func _arithmetic_cases(reference: Dictionary) -> bool:
	for row: Dictionary in reference.blends:
		_check("blend", "%08x/%08x" % [row.color, row.candidate], TerrainCompositor._blend_material(row.color, row.candidate), row.value)
	for row: Dictionary in reference.lighting:
		_check("gradient", "%08x/%08x" % [row.sun, row.ambient], TerrainCompositor._build_lighting_gradient(row.sun, row.ambient), row.gradient)
		var diffuse: Dictionary = TerrainCompositor.terrain_vertex_diffuse(row.sun, row.ambient)
		_check("diffuse", "uint32 colours accepted", diffuse.get("ok"), true)
		if not diffuse.get("ok", false): return false
		var color: PackedFloat32Array = diffuse.value
		_check("diffuse", "%08x/%08x exact float32 words" % [row.sun, row.ambient], color.to_byte_array().to_int32_array(), row.diffuse)
	return true


func _boundary_cases(owner: RefCounted, cases: Array) -> bool:
	for row: Dictionary in cases:
		var destination: Variant = null
		if row.length >= 0:
			destination = PackedByteArray()
			destination.resize(row.length)
			destination.fill(0xa5)
		var result: Dictionary = owner.render_tile(destination, row.level, row.tile_x, row.tile_y, row.slot_x, row.slot_y)
		_check("boundary", row.name + " success/refusal", result.get("ok"), row.error_type.is_empty())
		_check("boundary", row.name + " exact exception type", result.get("error_type", ""), row.error_type)
		if destination != null:
			_check("boundary", row.name + " exact bytes including partial writes", destination, row.bytes)
	var unchanged := PackedByteArray([1, 2, 3])
	for invalid: Variant in [null, true, 1.0, "0", -0x80000001, 0x80000000]:
		_check("boundary", "invalid coordinate carrier refuses", owner.render_tile(unchanged, invalid, 0, 0, 0, 0).get("error_type"), "ArgumentException")
		_check("boundary", "invalid coordinate leaves destination unchanged", unchanged, PackedByteArray([1, 2, 3]))
	return true


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = _counts.get(group, 0) + 1
	if actual is PackedByteArray and expected is PackedByteArray: _compared_bytes += expected.size()
	if actual == expected: return
	var failure: Dictionary = {"group": group, "name": name}
	if (actual is PackedByteArray and expected is PackedByteArray) or (actual is PackedInt32Array and expected is PackedInt32Array) \
		or (actual is PackedInt64Array and expected is PackedInt64Array):
		failure["actual_count"] = actual.size()
		failure["expected_count"] = expected.size()
		for index: int in range(mini(actual.size(), expected.size())):
			if actual[index] != expected[index]:
				failure["first_index"] = index
				failure["actual"] = actual[index]
				failure["expected"] = expected[index]
				break
	else:
		failure["actual"] = str(actual)
		failure["expected"] = str(expected)
	_failures.append(failure)
	if _failures.size() <= 12: push_error(JSON.stringify(failure))


func _finish() -> void:
	if _finished: return
	_finished = true
	for group: String in REQUIRED:
		if not _completed.has(group): _failures.append({"group": "completion", "name": "missing " + group})
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "failures": _failures,
		"counts": _counts, "compared_bytes": _compared_bytes, "completed": _completed,
		"lifetime_release": _lifetime_release}
	var output := FileAccess.open(_report, FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "  "))
	output.close()
	var total: int = 0
	for count: int in _counts.values(): total += count
	print("TERRAIN_COMPOSITOR_CHECKS: %d assertions, %d exact bytes, %d failures; %s" % [total, _compared_bytes, _failures.size(), _report])
	quit(0 if _failures.is_empty() else 1)


static func _sha(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()


static func _owner_alive(reference: WeakRef) -> bool:
	return reference.get_ref() != null


static func _owned_path(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") or not path.begins_with(owned + "/"):
		return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	var parts: PackedStringArray = path.trim_prefix(owned + "/").split("/", false)
	for index: int in range(parts.size()):
		if directory.is_link(parts[index]): return false
		if index < parts.size() - 1 and directory.change_dir(parts[index]) != OK: return false
	return not parts.is_empty()
