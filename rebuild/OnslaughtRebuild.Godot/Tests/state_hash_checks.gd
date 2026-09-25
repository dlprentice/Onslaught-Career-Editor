# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const Hasher = preload("res://Core/state_hasher.gd")
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


func _check_bytes(name: String, actual: PackedByteArray, expected: PackedByteArray) -> void:
	counts.canonical_bytes = int(counts.get("canonical_bytes", 0)) + 1
	if actual == expected:
		return
	var offset: int = 0
	while offset < mini(actual.size(), expected.size()) and actual[offset] == expected[offset]:
		offset += 1
	failures.append({"group": "canonical_bytes", "name": name, "first_difference": offset,
		"actual_size": actual.size(), "expected_size": expected.size(),
		"actual": actual.slice(maxi(0, offset - 8), offset + 24).hex_encode(),
		"expected": expected.slice(maxi(0, offset - 8), offset + 24).hex_encode()})


func _oracle_checks(rows: Array) -> void:
	_check("oracle", "nonempty snapshots", not rows.is_empty(), true)
	var schemas: Array[int] = []
	for row: Dictionary in rows:
		var before: Variant = row.snapshot.duplicate(true) if row.snapshot is Dictionary else row.snapshot
		var result: Dictionary = Hasher.get_canonical_bytes(row.snapshot)
		var digest: Dictionary = Hasher.compute_hex(row.snapshot)
		_check("oracle", row.name + " byte admission", result.get("ok"), row.expected.ok)
		_check("oracle", row.name + " hash admission", digest.get("ok"), row.expected.ok)
		_check("immutability", row.name + " source unchanged", row.snapshot, before)
		if row.expected.ok:
			if not result.get("ok", false) or not digest.get("ok", false):
				_check("oracle", row.name + " unexpected byte diagnostic", result.get("error"), null)
				_check("oracle", row.name + " unexpected hash diagnostic", digest.get("error"), null)
				continue
			var expected: PackedByteArray = String(row.expected.bytes).hex_decode()
			_check_bytes(row.name, result.bytes, expected)
			_check("hashes", row.name + " SHA256", digest.get("hex"), row.expected.hash)
			_check("schemas", row.name + " selected schema", result.get("schema"), row.expected.schema)
			_check("schemas", row.name + " checksum schema", digest.get("schema"), row.expected.schema)
			_check("schemas", row.name + " encoded schema", result.bytes.decode_s32(23), row.expected.schema)
			if row.expected.pinned_hash != null:
				_check("pinned", row.name + " existing SimulationTests fingerprint", digest.get("hex"), row.expected.pinned_hash)
			if not schemas.has(row.expected.schema): schemas.append(row.expected.schema)
		else:
			_check("refusals", row.name + " byte error class", result.get("error_type"), row.expected.error_type)
			_check("refusals", row.name + " hash error class", digest.get("error_type"), row.expected.error_type)
			for rejected: Dictionary in [result, digest]:
				_check("refusals", row.name + " no partial bytes", rejected.has("bytes"), false)
				_check("refusals", row.name + " no partial checksum", rejected.has("hex"), false)
				_check("refusals", row.name + " diagnostic", str(rejected.get("error", "")).is_empty(), false)
	schemas.sort()
	_check("schemas", "all existing versions exercised", schemas, [42, 43, 44, 45, 46, 47, 48])
	_check("pinned", "existing fixed fingerprint was executed", counts.get("pinned", 0), 1)
	_completed.append("oracle")


func _admission_checks(baseline: Dictionary) -> void:
	var expected: Dictionary = Hasher.get_canonical_bytes(baseline)
	_check("admission", "baseline admitted", expected.get("ok"), true)
	if not expected.get("ok", false): return
	for field: String in ["tick", "seed", "level100_mission", "level100_actors", "level100_actor_mechanics", "level100_destruction", "level100_actor_scripts", "level100_player_weapon_state", "retail_event_frame_count"]:
		var absent: Dictionary = baseline.duplicate(true)
		absent.erase(field)
		_rejected("missing " + field, absent)
	for value: Variant in [true, "1", 1.0, -2147483649, 2147483648, null]:
		var malformed: Dictionary = baseline.duplicate(true)
		malformed.tick = value
		_rejected("Int32 admission " + str(value), malformed)
	for value: Variant in [-1, 4294967296, 1.0, false]:
		var malformed: Dictionary = baseline.duplicate(true)
		malformed.seed = value
		_rejected("UInt32 admission " + str(value), malformed)
	for value: Variant in [-129, 128, 1.0, true]:
		var malformed: Dictionary = baseline.duplicate(true)
		malformed.facing_x = value
		_rejected("signed-byte admission " + str(value), malformed)
	for value: Variant in [0, 1, null, "true"]:
		var malformed: Dictionary = baseline.duplicate(true)
		malformed.player_on_ground = value
		_rejected("Boolean admission " + str(value), malformed)
	for value: Variant in [1.0, "9223372036854775807", null, false]:
		var malformed: Dictionary = baseline.duplicate(true)
		malformed.level100_mission.next_sequence = value
		_rejected("Int64 admission " + str(value), malformed)
	for value: Variant in [null, 1, [65], PackedInt32Array([-1]), PackedInt32Array([65536])]:
		var malformed: Dictionary = baseline.duplicate(true)
		malformed.level100_mission.program_sha256 = value
		_rejected("UTF16 admission " + str(value), malformed)
	for value: Variant in [null, {}, [null], [1]]:
		var malformed: Dictionary = baseline.duplicate(true)
		malformed.projectiles = value
		_rejected("collection admission " + str(value), malformed)
	var missing_nullable: Dictionary = baseline.duplicate(true)
	missing_nullable.level100_mission.erase("navigation_objective")
	_rejected("missing nullable is not null", missing_nullable)
	var malformed_basis: Dictionary = baseline.duplicate(true)
	malformed_basis.level100_actors.actors[0].pose.basis_float_bits.row0_x = 1.0
	_rejected("raw float word is an exact integer", malformed_basis)
	for carrier: Variant in [false, 1, "state", [], {}]:
		_rejected("root carrier " + str(carrier), carrier)
	var bytes: PackedByteArray = expected.bytes
	bytes[0] ^= 255
	_check_bytes("returned bytes are detached", Hasher.get_canonical_bytes(baseline).bytes, String(_baseline_hex).hex_decode())
	_completed.append("admission")


var _baseline_hex: String = ""


func _rejected(name: String, value: Variant) -> void:
	var result: Dictionary = Hasher.get_canonical_bytes(value)
	_check("admission", name + " fails", result.get("ok"), false)
	_check("admission", name + " no bytes", result.has("bytes"), false)
	_check("admission", name + " no checksum", result.has("hex"), false)
	_check("admission", name + " diagnostic", str(result.get("error", "")).is_empty(), false)


func _decode_transport(value: Variant) -> Variant:
	if value is Dictionary:
		if value.size() == 1 and value.has("$utf16"):
			var units := PackedInt32Array()
			if not value["$utf16"] is Array:
				_transport_ok = false
				return null
			for unit: Variant in value["$utf16"]:
				if typeof(unit) != TYPE_FLOAT or not is_finite(unit) or unit != floor(unit) or unit < 0 or unit > 65535:
					_transport_ok = false
					return null
				units.append(int(unit))
			return units
		if value.size() == 1 and value.has("$i64"):
			if not value["$i64"] is String:
				_transport_ok = false
				return null
			var text: String = value["$i64"]
			var integer: int = text.to_int()
			if str(integer) != text:
				_transport_ok = false
				return null
			return integer
		var decoded: Dictionary = {}
		for key: String in value:
			decoded[key] = _decode_transport(value[key])
		return decoded
	if value is Array:
		var decoded: Array = []
		for item: Variant in value:
			decoded.append(_decode_transport(item))
		return decoded
	if typeof(value) == TYPE_FLOAT:
		if not is_finite(value) or value != floor(value) or value < -2147483648 or value > 4294967295:
			_transport_ok = false
			return null
		return int(value)
	return value


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not args[1].is_absolute_path() or FileAccess.file_exists(args[1]):
		push_error("State hash checks require existing oracle and new absolute task-owned report paths.")
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("stateHash") is Dictionary or not parsed.stateHash.get("cases") is Array:
		push_error("Missing stateHash oracle cases.")
		quit(2)
		return
	var oracle: Dictionary = _decode_transport(parsed.stateHash)
	if not _transport_ok or oracle.cases.is_empty():
		push_error("State hash fixture transport is incomplete or loses exact values.")
		quit(2)
		return
	_baseline_hex = oracle.cases[0].expected.bytes
	_oracle_checks(oracle.cases)
	_admission_checks(oracle.cases[0].snapshot)
	for section: String in ["oracle", "admission"]:
		_check("completion", section + " returned", _completed.has(section), true)
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures,
		"completed": ["state_hash"] if _completed.size() == 2 else []}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
