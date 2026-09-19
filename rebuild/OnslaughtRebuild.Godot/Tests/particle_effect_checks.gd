# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Resolver = preload("res://Client/particle_effect_resolver.gd")
const Plan = preload("res://Client/particle_effect_plan.gd")
const SetFile = preload("res://Client/particle_set.gd")
const Text = preload("res://Core/canonical_json_string.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var _completed: PackedStringArray = []
var _transport_ok: bool = true


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check(group, name + " completed", actual.get("ok"), expected.ok)
	if expected.ok:
		_check(group, name + " exact authored plan", actual.get("value"), expected.value)
	else:
		_check(group, name + " error class", actual.get("error_type"), expected.error_type)
		_check(group, name + " error parameter", actual.get("parameter", ""), expected.parameter)
		_check(group, name + " no partial plan", actual.has("value") or actual.has("bits"), false)


func _plan_checks(oracle: Dictionary) -> void:
	_check("plans", "nonempty fixtures", not oracle.cases.is_empty(), true)
	for row: Dictionary in oracle.cases:
		var source: PackedInt32Array = row.source.duplicate()
		var parsed: Dictionary = SetFile.parse_units(row.source)
		_check("plans", row.name + " source admission", parsed.get("ok"), true)
		if not parsed.get("ok", false): continue
		var result: Dictionary = Resolver.resolve(parsed.value, row.effect_name)
		_result("plans", row.name, result, row.expected)
		_check("plans", row.name + " source units unchanged", row.source, source)
	_completed.append("plans")


func _law_checks(oracle: Dictionary) -> void:
	_check("laws", "turns per second", Resolver.GAME_TURNS_PER_SECOND, oracle.constants.turns)
	_check("laws", "blend selector", Resolver.BLEND_MODE_SELECTS_SHIPPED_TEXTURE_FORMAT, oracle.constants.blend)
	_check("laws", "declared reconstruction bound", Resolver.MAXIMUM_INSTANCES_PER_EFFECT, oracle.constants.instances)
	_check("laws", "radius factor raw word", Resolver.AUTHORED_RADIUS_IS_HALF_THE_QUAD_SIDE_BITS, oracle.constants.radius_bits)
	_check("laws", "animation enum", [Plan.ANIMATION_STATIC, Plan.ANIMATION_PLAY_ONCE, Plan.ANIMATION_LOOP], [0, 1, 2])
	for row: Dictionary in oracle.atlas:
		_result("laws", "atlas " + str(row.value), Resolver.atlas_grid_side(row.value), row.expected)
	for row: Dictionary in oracle.quad:
		var result: Dictionary = Resolver.billboard_quad_side(row.input_bits)
		_check("laws", "quad operation completed", result.get("ok"), true)
		_check("laws", "quad exact float store " + str(row.input_bits), result.get("bits"), row.output_bits)
	for row: Dictionary in oracle.totals:
		var layers: Array = []
		for count: int in row.counts: layers.append({"instance_count": count})
		_check("laws", "unchecked TotalInstances", Plan.total_instances(layers), {"ok": true, "value": row.expected})
	_completed.append("laws")


func _unicode_checks(oracle: Dictionary) -> void:
	var mappings: Dictionary = {}
	for row: Array in oracle.lowercase.mappings:
		_check("unicode", "unique changed scalar " + str(row[0]), mappings.has(row[0]), false)
		mappings[row[0]] = row[1]
	_check("unicode", "complete scalar range advertised", oracle.lowercase.maximum_scalar, 0x10ffff)
	var compared: int = 0
	for scalar: int in range(0x110000):
		if scalar >= 0xd800 and scalar <= 0xdfff: continue
		var expected: int = mappings.get(scalar, scalar)
		var actual: int = Resolver._lower_scalar(scalar)
		if actual != expected:
			failures.append({"group": "unicode_scalars", "name": "invariant scalar U+%06X" % scalar, "actual": actual, "expected": expected})
		compared += 1
	counts["unicode_scalars"] = compared
	_check("unicode", "every valid Unicode scalar compared", compared, 1112064)
	# The scalar sweep deliberately excludes surrogate code units; sequences
	# prove pair decoding as well as literal NUL and unpaired-unit preservation.
	for units: PackedInt32Array in [PackedInt32Array([0]), PackedInt32Array([0xd800]), PackedInt32Array([0xdfff]),
		PackedInt32Array([0xd800, 0, 0xdfff]), PackedInt32Array([0xd800, 0xd800, 0xdfff])]:
		var expected: PackedInt32Array = units.duplicate()
		if units == PackedInt32Array([0xd800, 0xd800, 0xdfff]):
			# U+103FF has no lowercase mapping; the leading lone surrogate stays.
			_check("unicode", "raw supplementary fallback has no authored change", mappings.get(0x103ff, 0x103ff), 0x103ff)
		_check("unicode", "NUL/unpaired carrier remains intact", Resolver.leaf_texture_name(units), expected)
	_completed.append("unicode")


func _refused(name: String, result: Dictionary, error_type: String = "") -> void:
	_check("admission", name + " refused", result.get("ok"), false)
	_check("admission", name + " no usable result", result.has("value") or result.has("bits"), false)
	_check("admission", name + " explicit explanation", str(result.get("error", "")).is_empty(), false)
	if not error_type.is_empty(): _check("admission", name + " error class", result.get("error_type"), error_type)


func _admission_checks(oracle: Dictionary) -> void:
	var parsed: Dictionary = SetFile.parse_units(oracle.cases[0].source)
	_check("admission", "fixture set admitted", parsed.get("ok"), true)
	if not parsed.get("ok", false): return
	var fixture: RefCounted = parsed.value
	_refused("null set precedes null effect", Resolver.resolve(null, null), "ArgumentNullException")
	_check("admission", "null set parameter", Resolver.resolve(null, null).get("parameter"), "set")
	_refused("null effect", Resolver.resolve(fixture, null), "ArgumentNullException")
	_refused("empty effect", Resolver.resolve(fixture, ""), "ArgumentException")
	for invalid: Variant in [false, 1, 1.0, [], {}, PackedInt32Array([-1]), PackedInt32Array([65536])]:
		_refused("invalid name carrier", Resolver.resolve(fixture, invalid))
	for invalid: Variant in [false, 1, "", [], {}]:
		_refused("invalid set carrier", Resolver.resolve(invalid, "Sprite"))
	for invalid: Variant in [null, false, 1.0, "1", -1, 4294967296]:
		_refused("invalid float-word carrier", Resolver.billboard_quad_side(invalid))
	for invalid: Variant in [null, false, 1.0, "1", -2147483649, 2147483648]:
		_refused("invalid enum storage", Resolver.atlas_grid_side(invalid))
	_refused("null plan layers", Plan.total_instances(null), "NullReferenceException")
	_refused("null plan layer", Plan.total_instances([null]), "NullReferenceException")
	_refused("missing layer count", Plan.total_instances([{}]))
	_refused("invalid layer count", Plan.total_instances([{"instance_count": 2147483648}]))
	var extreme: Dictionary = SetFile.parse_units(oracle.nonterminating_source)
	_check("source_derived_refusal", "extreme fixture admitted", extreme.get("ok"), true)
	if not extreme.get("ok", false): return
	var refusal: Dictionary = Resolver.resolve(extreme.value, "Emitter")
	_refused("source Int32 loop wrap cannot terminate", refusal, "NonTerminatingInput")
	# The oracle supplied only this source text. It did NOT call C# Resolve on
	# it: that loop wraps forever even with an emission rate of zero.
	_completed.append("admission")


func _detachment_checks(oracle: Dictionary) -> void:
	var parsed: Dictionary = SetFile.parse_units(oracle.cases[0].source)
	if not parsed.get("ok", false): return
	var first: Dictionary = Resolver.resolve(parsed.value, "Sprite")
	if not first.get("ok", false): return
	var saved: Dictionary = first.value.duplicate(true)
	first.value.effect_name[0] = 0
	first.value.layers[0].descriptor_name[0] = 0
	first.value.layers[0].path[0] = 0
	first.value.layers[0].start_turns[0] = -99
	first.value.layers[0].initial_velocity.x_bits = 0x7f800001
	first.value.unimplemented.append(PackedInt32Array([0]))
	_check("detachment", "mutating one result leaves future resolution unchanged", Resolver.resolve(parsed.value, "Sprite").get("value"), saved)
	var name := PackedInt32Array([65, 0, 0xd800])
	var layers: Array = [{"instance_count": 1, "nested": {"raw": PackedInt32Array([66, 0, 0xdfff])}}]
	var omissions: Array = [PackedInt32Array([67, 0, 0xd800])]
	var plan: Dictionary = Plan.create(name, -1, layers, omissions)
	_check("detachment", "data plan created", plan.get("ok"), true)
	if not plan.get("ok", false): return
	var before: Dictionary = plan.value.duplicate(true)
	name[0] = 0
	layers[0].nested.raw[0] = 0
	omissions[0][0] = 0
	_check("detachment", "data plan owns detached nested carriers", plan.value, before)
	_completed.append("detachment")


func _units(value: Variant) -> Variant:
	if value == null: return null
	if not value is Array:
		_transport_ok = false
		return null
	var result := PackedInt32Array()
	for code: Variant in value:
		if typeof(code) != TYPE_FLOAT or not is_finite(code) or code != floor(code) or code < 0 or code > 65535:
			_transport_ok = false
			return null
		result.append(int(code))
	return result


func _decode_transport(value: Variant, key_name: String = "") -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value: result[key] = _decode_transport(value[key], key)
		return result
	if value is Array:
		if key_name in ["source", "effect_name", "descriptor_name", "path", "texture_name", "name", "nonterminating_source"]:
			return _units(value)
		var result: Array = []
		for entry: Variant in value:
			result.append(_units(entry) if key_name == "unimplemented" else _decode_transport(entry))
		return result
	if typeof(value) == TYPE_FLOAT:
		if not is_finite(value) or value != floor(value) or value < -2147483648 or value > 4294967295:
			_transport_ok = false
			return null
		return int(value)
	return value


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not args[1].is_absolute_path() or FileAccess.file_exists(args[1]):
		push_error("Particle effect checks require existing oracle and new absolute task-owned report paths.")
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("particleEffects") is Dictionary:
		push_error("Missing particleEffects oracle object.")
		quit(2)
		return
	var oracle: Dictionary = _decode_transport(parsed.particleEffects)
	for key: String in ["cases", "atlas", "quad", "totals"]:
		if not oracle.get(key) is Array: _transport_ok = false
	if not oracle.get("lowercase") is Dictionary or not oracle.get("constants") is Dictionary:
		_transport_ok = false
	if not _transport_ok:
		push_error("Particle effect transport is incomplete or loses raw words/UTF-16 units.")
		quit(2)
		return
	_plan_checks(oracle)
	_law_checks(oracle)
	_unicode_checks(oracle)
	_admission_checks(oracle)
	_detachment_checks(oracle)
	for section: String in ["plans", "laws", "unicode", "admission", "detachment"]:
		_check("completion", section + " returned", _completed.has(section), true)
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures,
		"completed": ["particle_effects"] if _completed.size() == 5 else []}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
