# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const Render = preload("res://Client/render_interpolation.gd")
const Target = preload("res://Client/target_presentation.gd")
const Float32 = preload("res://Core/retail_float24.gd")
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
	_check(group, name + " success", actual.get("ok"), expected.ok)
	if expected.ok:
		if expected.has("value"):
			_check(group, name + " exact value", actual.get("value"), expected.value)
	else:
		_check(group, name + " error class", actual.get("error_type"), expected.error_type)
		_check(group, name + " parameter", actual.get("parameter", ""), expected.parameter)
		_check(group, name + " no usable result", actual.has("value") or actual.has("bits"), false)


func _projection_checks(oracle: Dictionary) -> void:
	_check("projection", "nonempty cases", not oracle.projection.is_empty(), true)
	_check("projection", "six exact binding rows", Target.rendered_bindings(), oracle.bindings)
	_check("projection", "exact binding count", Target.rendered_bindings().size(), 6)
	for row: Dictionary in oracle.projection:
		var before: Variant = row.target.duplicate(true) if row.target is Dictionary else row.target
		_result("projection", row.name, Target.project(row.target), row.expected)
		_check("projection", row.name + " source unchanged", row.target, before)
	_completed.append("projection")


func _primitive_checks(oracle: Dictionary) -> void:
	_check("primitives", "nonempty sine fixtures", not oracle.trig.is_empty(), true)
	_check("primitives", "nonempty acos fixtures", not oracle.acos.is_empty(), true)
	_check("primitives", "retained teleport threshold", Render.TELEPORT_METERS_BITS, oracle.teleport_bits)
	for row: Dictionary in oracle.trig:
		_check("primitives", "native float sine " + str(row.input_bits),
			Float32.store_word(Render._sin(Float32.read_word(row.input_bits))), row.sin_bits)
	for row: Dictionary in oracle.acos:
		_check("primitives", "native clamped float acos " + str(row.input_bits),
			Float32.store_word(Render._acos_clamped(Float32.read_word(row.input_bits))), row.output_bits)
	_completed.append("primitives")


func _vector_checks(rows: Array) -> void:
	_check("vectors", "nonempty cases", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var linear: Dictionary = Render.lerp(row.previous, row.current, row.alpha_bits)
		var distance: Dictionary = Render.distance_squared(row.previous, row.current)
		var position: Dictionary = Render.interpolate_position(row.previous, row.current, row.alpha_bits, row.teleport_bits)
		_check("vectors", row.name + " all operations completed", linear.get("ok") and distance.get("ok") and position.get("ok"), true)
		_check("vectors", row.name + " lerp words", linear.get("value"), row.lerp)
		_check("vectors", row.name + " distance word", distance.get("bits"), row.distance_bits)
		_check("vectors", row.name + " teleport law", position.get("value"), row.interpolated)
	_completed.append("vectors")


func _basis_checks(rows: Array) -> void:
	_check("basis", "nonempty cases", not rows.is_empty(), true)
	for row: Dictionary in rows:
		_check("basis", row.name + " previous rotation admission", Render._is_proper_rotation(row.previous), row.previous_proper)
		_check("basis", row.name + " current rotation admission", Render._is_proper_rotation(row.current), row.current_proper)
		var result: Dictionary = Render.interpolate_basis(row.previous, row.current, row.alpha_bits)
		_check("basis", row.name + " completed", result.get("ok"), true)
		_check("basis", row.name + " all quaternion/fallback words", result.get("value"), row.expected)
	_completed.append("basis")


func _entity_checks(oracle: Dictionary) -> void:
	_check("entities", "nonempty targets", not oracle.targets.is_empty(), true)
	_check("entities", "nonempty projectiles", not oracle.projectiles.is_empty(), true)
	for row: Dictionary in oracle.targets:
		var current_before: Dictionary = row.current.duplicate(true)
		var previous_before: Variant = row.previous.duplicate(true) if row.previous is Dictionary else null
		var result: Dictionary = Render.interpolate_target(row.previous, row.current, row.alpha_bits)
		_check("entities", row.name + " target completed", result.get("ok"), true)
		_check("entities", row.name + " target exact fields", result.get("value"), row.expected)
		_check("entities", row.name + " target inputs unchanged", [row.previous, row.current], [previous_before, current_before])
	for row: Dictionary in oracle.projectiles:
		var result: Dictionary = Render.interpolate_projectile(row.previous, row.spawn, row.current, row.alpha_bits)
		_check("entities", row.name + " projectile completed", result.get("ok"), true)
		_check("entities", row.name + " projectile exact fields", result.get("value"), row.expected)
	_completed.append("entities")


func _trail_checks(oracle: Dictionary) -> void:
	_check("trails", "nonempty histories", not oracle.trails.is_empty(), true)
	for row: Dictionary in oracle.kinds:
		_check("trails", str(row.kind) + " authored use", Render.uses_authored_trail(row.kind), {"ok": true, "value": row.uses})
		_result("trails", str(row.kind) + " authored points", Render.authored_point_count(row.kind), row.points)
		_result("trails", str(row.kind) + " authored lifetime", Render.authored_lifetime_ticks(row.kind), row.lifetime)
	for row: Dictionary in oracle.constructors:
		_result("trails", str(row.capacity) + "/" + str(row.lifetime), Render.create_trail_history(row.capacity, row.lifetime), row.expected)
	for row: Dictionary in oracle.trails:
		var history: RefCounted = Render.create_trail_history(row.capacity, row.lifetime).value
		_check("trails", "uninitialized rendered head", history.with_rendered_head(_vector(1.0, 2.0, 3.0)).get("value"), row.before)
		var index: int = 0
		for step: Dictionary in row.steps:
			var name: String = str(row.capacity) + "/" + str(row.lifetime) + "/" + str(index)
			_result("trails", name, history.advance(step.current, step.velocity, step.remaining), step.expected)
			_check("trails", name + " points", history.points(), step.points)
			_check("trails", name + " last tick and mutation order", history.snapshot().last_remaining_ticks, step.last_remaining_ticks)
			_check("trails", name + " rendered head", history.with_rendered_head(step.head).get("value"), step.with_head)
			_check("trails", name + " rendered head does not advance", history.points(), step.points)
			index += 1
	var extreme: Dictionary = oracle.extreme_tail
	var bounded: RefCounted = Render.create_trail_history(extreme.capacity, extreme.lifetime).value
	_check("source_derived_tail", "native extreme call completes", bounded.advance(extreme.current, extreme.velocity, 0).get("ok"), true)
	_check("source_derived_tail", "retained tail equals bounded original reference", bounded.points(), extreme.points)
	_check("source_derived_tail", "remaining tick preserved", bounded.snapshot().last_remaining_ticks, extreme.last_remaining_ticks)
	# This comparison exercises the algebraic discarded-prefix equivalence;
	# the oracle explicitly never executes the original 2^31 first-call loop.
	_completed.append("trails")


func _vector(x: float, y: float, z: float) -> Dictionary:
	return {"x_bits": Float32.store_word(x), "y_bits": Float32.store_word(y), "z_bits": Float32.store_word(z)}


func _identity() -> Dictionary:
	return {"x_axis": _vector(1, 0, 0), "y_axis": _vector(0, 1, 0), "z_axis": _vector(0, 0, 1)}


func _refused(name: String, result: Dictionary) -> void:
	_check("admission", name + " refused", result.get("ok"), false)
	_check("admission", name + " no usable output", result.has("value") or result.has("bits"), false)
	_check("admission", name + " explicit error", str(result.get("error", "")).is_empty(), false)


func _admission_checks(oracle: Dictionary) -> void:
	var zero: Dictionary = _vector(0, 0, 0)
	var next: Dictionary = _vector(1, 2, 3)
	var basis: Dictionary = _identity()
	for invalid: Variant in [null, false, 0.0, "0", -1, 4294967296]:
		_refused("alpha carrier", Render.lerp(zero, next, invalid))
		_refused("threshold carrier", Render.interpolate_position(zero, next, 0, invalid))
		_refused("basis alpha carrier", Render.interpolate_basis(basis, basis, invalid))
		for axis: String in Render.AXES:
			var value: Dictionary = next.duplicate(true)
			value[axis] = invalid
			_refused("vector word " + axis, Render.lerp(zero, value, 0))
	for invalid: Variant in [null, false, 1.0, "1", -1, 256]:
		_refused("projectile enum storage", Render.uses_authored_trail(invalid))
	for invalid: Variant in [null, false, 1.0, "1", -2147483649, 2147483648]:
		_refused("capacity storage", Render.create_trail_history(invalid, 20))
		_refused("lifetime storage", Render.create_trail_history(5, invalid))
	for axis: String in Render.BASIS_AXES:
		var incomplete: Dictionary = basis.duplicate(true)
		incomplete.erase(axis)
		_refused("missing basis column " + axis, Render.interpolate_basis(incomplete, basis, 0))
	var descriptor: Dictionary = oracle.targets[0].current.duplicate(true)
	var source: Dictionary = descriptor.duplicate(true)
	var returned: Dictionary = Render.interpolate_target(null, descriptor, 0).value
	returned.position.x_bits = 0x7f800001
	returned.basis.x_axis.x_bits = 0
	returned.definition_name[0] = 0
	_check("detachment", "returned target is detached across all nested fields", descriptor, source)
	var bindings: Array[Dictionary] = Target.rendered_bindings()
	bindings[0].definition_name[0] = 0
	bindings.clear()
	_check("detachment", "callers cannot edit binding constants", Target.rendered_bindings(), oracle.bindings)
	var history: RefCounted = Render.create_trail_history(5, 20).value
	history.advance(next, _vector(1, 0, 0), 15)
	var saved: Dictionary = history.snapshot()
	var points: Array = history.points()
	points[0].x_bits = 0
	points.clear()
	var head: Dictionary = _vector(4, 5, 6)
	var heads: Array = history.with_rendered_head(head).value
	head.x_bits = 0
	heads[-1].x_bits = 0
	_check("detachment", "points and rendered head cannot mutate trail history", history.snapshot(), saved)
	for invalid: Variant in [null, false, 15.0, "15", -1, 21, 2147483648]:
		_refused("remaining tick admission", history.advance(next, zero, invalid))
		_check("admission", "failed trail advance retains history", history.snapshot(), saved)
	_refused("bad trail vector", history.advance({}, zero, 14))
	_refused("bad trail velocity", history.advance(next, {}, 14))
	_refused("bad rendered head", history.with_rendered_head({}))
	_check("admission", "bad trail carriers leave state untouched", history.snapshot(), saved)
	var target: Dictionary = oracle.projection[1].target.duplicate(true)
	for field: String in ["actor_id", "definition_name", "mesh_binding", "is_active", "pose"]:
		var missing: Dictionary = target.duplicate(true)
		missing.erase(field)
		_refused("missing projected field " + field, Target.project(missing))
	for field: String in Target.BASIS_KEYS:
		var missing: Dictionary = target.duplicate(true)
		missing.pose.basis_float_bits.erase(field)
		_refused("missing Core basis word " + field, Target.project(missing))
	_completed.append("admission")


func _decode_transport(value: Variant, key_name: String = "") -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = _decode_transport(value[key], key)
		return result
	if value is Array:
		if key_name in ["definition_name", "mesh_binding"]:
			var units := PackedInt32Array()
			for unit: Variant in value:
				if typeof(unit) != TYPE_FLOAT or not is_finite(unit) or unit != floor(unit) or unit < 0 or unit > 65535:
					_transport_ok = false
					return null
				units.append(int(unit))
			return units
		var result: Array = []
		for item: Variant in value:
			result.append(_decode_transport(item))
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
		push_error("Render checks require existing oracle and new absolute task-owned report paths.")
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("renderInterpolation") is Dictionary:
		push_error("Missing renderInterpolation oracle object.")
		quit(2)
		return
	var oracle: Dictionary = _decode_transport(parsed.renderInterpolation)
	for key: String in ["projection", "bindings", "vectors", "bases", "targets", "projectiles", "kinds", "constructors", "trails", "trig", "acos"]:
		if not oracle.get(key) is Array: _transport_ok = false
	if not _transport_ok:
		push_error("Render fixture transport is incomplete or loses exact words.")
		quit(2)
		return
	_projection_checks(oracle)
	_primitive_checks(oracle)
	_vector_checks(oracle.vectors)
	_basis_checks(oracle.bases)
	_entity_checks(oracle)
	_trail_checks(oracle)
	_admission_checks(oracle)
	for section: String in ["projection", "primitives", "vectors", "basis", "entities", "trails", "admission"]:
		_check("completion", section + " returned", _completed.has(section), true)
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures,
		"completed": ["render_interpolation"] if _completed.size() == 7 else []}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
