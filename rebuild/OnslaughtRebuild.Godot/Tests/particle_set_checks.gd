# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Particles = preload("res://Client/particle_set.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Writer = preload("res://Core/canonical_binary_writer.gd")
const Latin1 = preload("res://Core/latin1_encoding.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var _completed: Array[String] = []


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if _plain(actual) != _plain(expected):
		failures.append({"group": group, "name": name, "actual": _plain(actual), "expected": _plain(expected)})


func _result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check(group, name + ":completion", actual.get("ok"), expected.ok)
	if expected.ok:
		for key: String in ["bits", "value"]:
			if expected.has(key):
				_check(group, name + ":" + key, actual.get(key), expected[key])
	else:
		_check(group, name + ":class", actual.get("error_type"), expected.error_type)
		_check(group, name + ":parameter", actual.get("parameter", ""), expected.parameter)


func _cases(rows: Array) -> void:
	_check("cases", "nonempty", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var units: Variant = null if row.units == null else PackedInt32Array(row.units)
		var parsed: Dictionary = Particles.parse_units(units)
		_result("cases", row.name, parsed, row.expected)
		if parsed.get("ok") != true or not row.expected.ok:
			continue
		var set: RefCounted = parsed.value
		_check("cases", row.name + ":projection", _projection(set), row.expected.projection)
		for index: int in range(set.descriptors.size()):
			var descriptor: RefCounted = set.descriptors[index]
			var first: Dictionary = set.find(descriptor.name)
			_check("lookup", row.name + ":first", set.descriptors.find(first.value), row.expected.lookup_first[index])
			_check("lookup", row.name + ":require_identity", set.require(descriptor.name).value == first.value, true)
		for query: Dictionary in row.expected.queries:
			var descriptor: RefCounted = set.descriptors[query.index]
			var key: Variant = null if query.key == null else PackedInt32Array(query.key)
			var result: Dictionary = descriptor.int_or_default(key, -17) if query.operation == "int_or_default" else descriptor.call("reference_name" if query.operation == "reference" else query.operation, key)
			_result("getters", row.name + ":" + str(query.index) + ":" + query.operation, result, query.expected)
	_completed.append("cases")


func _contracts(oracle: Dictionary) -> void:
	_check("contracts", "nonempty", not oracle.kinds.is_empty(), true)
	for row: Dictionary in oracle.kinds:
		var result: Dictionary = Particles.try_get_parse_kind(null if row.name == null else PackedInt32Array(row.name))
		_check("contracts", "token", result, {"recognized": row.recognized, "kind": row.kind})
	for row: Dictionary in oracle.classes:
		_result("contracts", "class:" + str(row.type), Particles.descriptor_class_name(row.type), row.name)
		_result("contracts", "loader:" + str(row.type), Particles.descriptor_loader_address(row.type), row.address)
	var mapping: Dictionary = {}
	for row: Dictionary in oracle.latin1_single_overrides:
		_check("encoding", "single byte fallback", row.bytes.size(), 1)
		mapping[row.unit] = row.bytes[0]
	var units := PackedInt32Array()
	for unit: int in range(65536):
		units.append(unit)
	var encoded: Dictionary = Latin1.encode(units)
	_check("encoding", "all UTF-16 units admitted", encoded.ok, true)
	_check("encoding", "one byte per unit including surrogate pairs", encoded.value.size(), 65536)
	for unit: int in range(65536):
		_check("encoding", "unit " + str(unit), encoded.value[unit], unit if unit <= 255 else mapping.get(unit, 63))
	_check("encoding", "all original bytes roundtrip", Latin1.encode(Latin1.decode(encoded.value)).value, encoded.value)
	_completed.append("contracts")


func _corpus(rows: Array) -> void:
	_check("corpus", "three existing inputs", rows.size(), 3)
	var descriptors: int = 0
	var emitters: int = 0
	for row: Dictionary in rows:
		var source: PackedByteArray = FileAccess.get_file_as_bytes(row.path)
		_check("corpus", row.name + ":source_pin", _hash(source), row.sha256)
		_check("corpus", row.name + ":length", source.size(), row.length)
		var parsed: Dictionary = Particles.parse_bytes(source)
		_check("corpus", row.name + ":parse", parsed.get("ok"), true)
		if parsed.get("ok") != true:
			return
		_check("corpus", row.name + ":all_fields_and_numeric_getters", _projection(parsed.value), row.projection)
		_check("corpus", row.name + ":exact_reemission", parsed.value.to_bytes() == source, true)
		_check("corpus", row.name + ":original_unchanged", _hash(FileAccess.get_file_as_bytes(row.path)), row.sha256)
		descriptors += parsed.value.descriptors.size()
		for descriptor: RefCounted in parsed.value.descriptors:
			if descriptor.type_id == Particles.DescriptorType.EMITTER:
				emitters += 1
				var life: Dictionary = descriptor.int_value("Life")
				_check("corpus", row.name + ":finite_source_emitter_loop", life.ok and life.value != 2147483647, true)
	_check("corpus", "all_descriptors", descriptors, 1479)
	_check("corpus", "all_emitter_lifetimes_checked", emitters, 338)
	_completed.append("corpus")


func _ownership() -> void:
	var text: String = "ParticleSystemEd_File_test\r\nFile_Version x\r\nNum_Particle_Descriptors 1\r\nParticle_Descriptor_Type 1\r\nParticle_Descriptor_Name Named\r\nA original\r\n" + Particles.RECORD_SEPARATOR + "\r\n"
	var source: PackedByteArray = text.to_ascii_buffer()
	var owner: RefCounted = Particles.parse_bytes(source).value
	var before: Dictionary = _projection(owner)
	source[0] = 0
	var header: PackedInt32Array = owner.header
	header[0] = 0
	var rows: Array = owner.descriptors
	var descriptor: RefCounted = rows[0]
	rows.clear()
	var name: PackedInt32Array = descriptor.name
	name[0] = 0
	var fields: Array = descriptor.fields
	fields[0].key = PackedInt32Array([0])
	fields[0].value[0] = 0
	var raw: PackedInt32Array = descriptor.raw("A").value
	raw[0] = 0
	var all: Array = descriptor.raw_all("A").value
	all[0][0] = 0
	var bytes: PackedByteArray = owner.to_bytes()
	bytes[0] = 0
	_check("ownership", "input_and_projections_detached", _projection(owner), before)
	_check("ownership", "missing_field_has_null_raw", descriptor.raw("missing").value, null)
	_check("ownership", "null_name_refused", owner.find(null).error_type, "ArgumentNullException")
	_check("ownership", "missing_name_refused", owner.require("missing").error_type, "InvalidDataException")
	_completed.append("ownership")


func _projection(set: RefCounted) -> Dictionary:
	var writer := Writer.new()
	_utf16(writer, set.header)
	_utf16(writer, set.version_line)
	writer.write_i32(set.declared_count)
	writer.write_i32(set.descriptors.size())
	for descriptor: RefCounted in set.descriptors:
		writer.write_i32(descriptor.type_id)
		_utf16(writer, descriptor.name)
		var fields: Array = descriptor.fields
		writer.write_i32(fields.size())
		var keys: Dictionary = {}
		for field: Dictionary in fields:
			_utf16(writer, field.key)
			_utf16(writer, field.value)
			keys[field.key] = true
		for key: PackedInt32Array in keys:
			_utf16(writer, key)
			var kind: int = Particles.try_get_parse_kind(key).kind
			writer.write_i32(kind)
			var result: Dictionary = {}
			match kind:
				Particles.ParseKind.DIRECT_INT: result = descriptor.int_value(key)
				Particles.ParseKind.DIRECT_FLOAT: result = descriptor.retail_direct_float_bits(key)
				Particles.ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE: result = descriptor.float_with_modifier(key)
				Particles.ParseKind.REFERENCE_NAME: result = descriptor.reference_name(key)
				_: continue
			writer.write_bool(result.ok)
			if not result.ok:
				_utf16(writer, Text.units(result.error_type).value)
				_utf16(writer, Text.units(result.get("parameter", "")).value)
			else:
				match kind:
					Particles.ParseKind.DIRECT_INT: writer.write_i32(result.value)
					Particles.ParseKind.DIRECT_FLOAT: writer.write_u32(result.bits)
					Particles.ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE:
						writer.write_u32(result.value.bits)
						_utf16(writer, result.value.modifier)
					Particles.ParseKind.REFERENCE_NAME: _utf16(writer, result.value)
	var finished: Dictionary = writer.finish()
	if not finished.ok:
		return {"error": finished.error}
	var emitted: PackedByteArray = set.to_bytes()
	return {"declared_count": set.declared_count, "count": set.descriptors.size(),
		"facts_sha256": _hash(finished.bytes), "bytes_sha256": _hash(emitted), "bytes_length": emitted.size()}


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var document: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if document is Dictionary and document.get("particleSet") is Dictionary:
		var oracle: Dictionary = _integer_tokens(document.particleSet)
		_cases(oracle.cases)
		_contracts(oracle)
		_corpus(oracle.corpus)
		_ownership()
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": _completed}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 5)}))
	quit(0 if failures.is_empty() and _completed == ["cases", "contracts", "corpus", "ownership"] else 1)


static func _utf16(writer: RefCounted, value: Variant) -> void:
	writer.write_i32(-1 if value == null else value.size())
	if value != null:
		for unit: int in value:
			writer.write_u16(unit)


static func _hash(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	return hash.finish().hex_encode()


static func _plain(value: Variant) -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value:
			result[key] = _plain(value[key])
		return result
	if value is Array or value is PackedInt32Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_plain(item))
		return result
	return value


static func _integer_tokens(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		return int(value)
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value:
			result[key] = _integer_tokens(value[key])
		return result
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_integer_tokens(item))
		return result
	return value
