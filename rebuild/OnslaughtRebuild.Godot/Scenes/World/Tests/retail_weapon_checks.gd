# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Synthetic raw-word comparisons against unchanged managed weapon owners.
## Only this harness reads/writes fixture receipts; the three Core modules
## own no files, engine vectors, clock, scene, input or registry.
const Charge = preload("res://Core/retail_weapon_charge.gd")
const Stores = preload("res://Core/retail_weapon_stores.gd")
const Selection = preload("res://Core/retail_weapon_selection.gd")
const Values = preload("res://Core/retail_career_values.gd")
var _checks: int = 0
var _failure_count: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _counts: Dictionary = {}
var _group: String = "admission"


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or Engine.is_editor_hint() or DisplayServer.get_name() != "headless":
		push_error("Two fixture/report paths and headless runtime are required.")
		quit(2)
		return
	if not _owned(args[0], false) or not _owned(args[1], true) or args[0] == args[1]:
		push_error("Fixture/report require existing/fresh owned local-data paths.")
		quit(2)
		return
	var fixture_hash: String = _hash(FileAccess.get_file_as_bytes(args[0]))
	var pointer: int = Input.mouse_mode
	var input: FileAccess = FileAccess.open(args[0], FileAccess.READ)
	if input == null:
		push_error("Cannot read weapon reference fixture.")
		quit(2)
		return
	var payload: Variant = input.get_var(false)
	input.close()
	if not payload is Dictionary or payload.get("schema") != 1 or not _object_free(payload):
		push_error("Unrecognized/object-bearing weapon fixture.")
		quit(2)
		return
	var fixture: Dictionary = payload
	_check(fixture.charge.size() >= 1200 and fixture.ready.size() >= 1500 and fixture.stores.size() >= 1700
		and fixture.cycles.size() >= 642 and fixture.unit.size() >= 900, "Complete operation groups present.")
	for file: String in fixture.source_sha256:
		var path: String = ProjectSettings.globalize_path("res://../OnslaughtRebuild.Core/" + file)
		_equal(_hash(FileAccess.get_file_as_bytes(path)), fixture.source_sha256[file], "Unchanged source identity: " + file)
	_equal({"level_count": Charge.LEVEL_COUNT, "absent_level": Charge.ABSENT_LEVEL, "value_per_level": Charge.VALUE_PER_LEVEL,
		"increment_cap_bits": Charge.INCREMENT_CAP_FLOAT_BITS, "store_count": Stores.STORE_COUNT,
		"full_ammo_percentage_bits": Stores.FULL_AMMO_PERCENTAGE_FLOAT_BITS}, fixture.constants, "Public constants")
	_finish()
	_group = "charge"
	for row: Dictionary in fixture.charge: _charge_sequence(row)
	_finish()
	_group = "ready"
	for row: Dictionary in fixture.ready:
		_result(Charge.ready_time_elapsed(row.now, row.ready_at), row.result, "ready/%d/%d" % [row.now, row.ready_at])
	_finish()
	_group = "stores"
	for row: Dictionary in fixture.stores: _store_case(row)
	_finish()
	_group = "cycles"
	for row: Dictionary in fixture.cycles: _cycle_case(row)
	_finish()
	_group = "unit"
	for row: Dictionary in fixture.unit:
		var arguments: Array = row.args.duplicate(true)
		_result(_unit(row.op, arguments), row.result, row.name)
		_equal(arguments, row.args, row.name + "/input-detached")
	_finish()
	_group = "ownership"
	_ownership(fixture.ownership)
	_finish()
	_group = "transport"
	_transport(fixture)
	_finish()
	_group = "safety"
	_equal(Input.mouse_mode, pointer, "Pointer unchanged")
	_equal(_hash(FileAccess.get_file_as_bytes(args[0])), fixture_hash, "Fixture unchanged")
	_finish()
	var report: Dictionary = {"schema": 1, "checks": _checks, "failure_count": _failure_count,
		"failures": _failures, "completed": _completed, "counts": _counts,
		"fixture_sha256": fixture_hash, "engine": Engine.get_version_info().string}
	var output: FileAccess = FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		push_error("Cannot create weapon check receipt.")
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("RETAIL_WEAPON_CHECKS: %d checks; %d failures; %s" % [_checks, _failure_count, args[1]])
	for failure: String in _failures.slice(0, 8): push_error(failure)
	quit(0 if _failure_count == 0 else 1)


func _charge_sequence(row: Dictionary) -> void:
	var table: Variant = null
	if row.initial != null:
		var created: Dictionary = Charge.from_snapshot(row.initial)
		_check(created.ok, row.name + "/table-import")
		if not created.ok: return
		table = created.value
		_equal(table.snapshot(), row.initial, row.name + "/initial-words")
	for index: int in range(row.steps.size()):
		var step: Dictionary = row.steps[index]
		var label: String = "%s/%d/%s" % [row.name, index, step.op]
		_result(_charge(table, step.op, step.args), step.result, label)
		_equal(null if table == null else table.snapshot(), step.after, label + "/state-after")


func _charge(table: Variant, operation: String, args: Array) -> Dictionary:
	match operation:
		"max_charge": return Charge.max_charge(table)
		"get_charge_bits": return Charge.get_charge_bits(table)
		"can_charge": return Charge.can_charge(table)
		"fully_charged": return Charge.fully_charged(table)
		"ready_to_charge": return Charge.ready_to_charge(table, args[0])
		"charge": return Charge.charge(table)
		"lose_charge": return Charge.lose_charge(table)
		"level_set": return table.levels().set_word(args[0], args[1])
		"word_set": return table.set_word(args[0], args[1])
		"gate_set": return table.set_ready_to_charge_gate_active(args[0])
		_: return Values.failure("HarnessFailure", "Unknown charge operation: " + operation)


func _store_case(row: Dictionary) -> void:
	var stores: Variant = null if row.stores == null else Stores.from_snapshot(row.stores).value
	var weapon: Variant = null if row.weapon == null else Selection.mounted_from_snapshot(row.weapon).value
	for operation: String in row.results:
		var actual: Dictionary
		match operation:
			"ammo_percentage_bits": actual = Stores.ammo_percentage_bits(stores, row.index)
			"ammo_count": actual = Stores.ammo_count(stores, row.index)
			"is_energy_weapon": actual = Stores.is_energy_weapon(stores, row.index)
			"is_weapon_overheated": actual = Stores.is_weapon_overheated(stores, row.index)
			"can_weapon_fire": actual = Selection.can_weapon_fire(stores, row.index)
			"can_walker_weapon_fire": actual = Selection.can_walker_weapon_fire(stores, row.index, row.active)
			"is_selectable": actual = Selection.is_selectable(weapon, stores)
			_: actual = Values.failure("HarnessFailure", "Unknown store operation.")
		_result(actual, row.results[operation], row.name + "/" + operation)
	_equal(null if stores == null else stores.snapshot(), row.stores, row.name + "/stores-unchanged")
	_equal(null if weapon == null else weapon.snapshot(), row.weapon, row.name + "/mounted-unchanged")


func _cycle_case(row: Dictionary) -> void:
	var stores: Variant = null if row.stores == null else Stores.from_snapshot(row.stores).value
	var pool: Array = []
	for record: Variant in row.pool:
		pool.append(null if record == null else Selection.mounted_from_snapshot(record).value)
	var weapons: Array = []
	for index: int in row.order: weapons.append(pool[index])
	_result(Selection.search_terminates(row.current, row.order.size()), row.terminates, row.name + "/terminates")
	_result(Selection.change_weapon(null if row.null_list else weapons, row.current, stores), row.result, row.name)
	_equal(null if stores == null else stores.snapshot(), row.stores, row.name + "/stores-unchanged")
	var after: Array = []
	for weapon: Variant in pool: after.append(null if weapon == null else weapon.snapshot())
	_equal(after, row.pool, row.name + "/shared-pool-unchanged")
	for index: int in range(weapons.size()):
		_check(is_same(weapons[index], pool[row.order[index]]), row.name + "/attachment-identity/%d" % index)


func _unit(operation: String, args: Array) -> Dictionary:
	match operation:
		"select": return Selection.select(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8])
		"raw_distance": return Selection.raw_distance_bits(args[0], args[1])
		"score": return Selection.score_bits(args[0], args[1], args[2], args[3], args[4], args[5], args[6])
		_: return Values.failure("HarnessFailure", "Unknown Unit operation.")


func _ownership(expected: Dictionary) -> void:
	var table := Charge.Table.new()
	table.levels().set_word(0, 0)
	table.levels().set_word(1, 0)
	table.set_word("charge_bits", 0x41200000)
	table.set_word("charge_rate_bits", 0x40000000)
	var levels: Stores.Words = table.levels()
	levels.set_word(4, -2)
	_equal(is_same(levels, table.levels()), expected.level_alias, "Level buffer retains identity")
	_equal(Charge.max_charge(table).value, expected.maximum, "Level alias mutation is observed")
	var stores := Stores.Stores.new()
	var values: Stores.Words = stores.store_value()
	var capacities: Stores.Words = stores.configuration_store_value()
	var heats: Stores.Words = stores.store_heat()
	var overheats: Stores.Words = stores.store_overheat()
	values.set_word(2, 0x40600000)
	capacities.set_word(2, 0x40e00000)
	heats.set_word(2, 0)
	overheats.set_word(2, -2)
	_equal([is_same(values, stores.store_value()), is_same(capacities, stores.configuration_store_value()),
		is_same(heats, stores.store_heat()), is_same(overheats, stores.store_overheat())], expected.store_aliases, "Four independent shared buffers")
	_equal(Stores.ammo_count(stores, 2).value, expected.count_before_heat, "Value alias before heat")
	var weapon := Selection.MountedWeapon.new()
	weapon.set_word("is_active", 1)
	weapon.set_word("ammo_store", 2)
	weapon.set_word("consumption_bits", 0x40800000)
	var list: Array = [weapon, weapon]
	_equal(is_same(list[0], list[1]), expected.mounted_alias, "Mounted objects retain aliases")
	_equal(Selection.is_selectable(list[1], stores).value, expected.selectable_before, "Consumption before shared mutation")
	weapon.set_word("consumption_bits", 0x40400000)
	_equal(Selection.is_selectable(list[1], stores).value, expected.selectable_after, "Consumption after shared mutation")
	heats.set_word(2, 7)
	_equal(Stores.ammo_count(stores, 2).value, expected.count_after_heat, "Heat alias affects later readout")
	_equal(Selection.change_weapon(list, 0, stores).value, expected.cycle, "Cycle returns effects without applying them")
	_equal(table.snapshot(), expected.table, "Table final raw words")
	_equal(stores.snapshot(), expected.stores, "Store final raw words")
	_equal(weapon.snapshot(), expected.weapon, "Mounted final raw words")
	var table_copy: Dictionary = table.snapshot()
	table_copy.levels[4] = -1
	table_copy.charge_bits = 0
	var store_copy: Dictionary = stores.snapshot()
	store_copy.store_value[2] = 0
	var words_copy: Array[int] = values.snapshot()
	words_copy.resize(1)
	var weapon_copy: Dictionary = weapon.snapshot()
	weapon_copy.is_active = 0
	_equal(table.snapshot(), expected.table, "Table snapshot detached")
	_equal(stores.snapshot(), expected.stores, "Stores and buffer snapshots detached")
	_equal(weapon.snapshot(), expected.weapon, "Mounted snapshot detached")
	var table_input: Dictionary = table.snapshot()
	var imported_table: Charge.Table = Charge.from_snapshot(table_input).value
	table_input.levels.clear()
	_equal(imported_table.snapshot(), expected.table, "Imported table detaches input")
	var store_input: Dictionary = stores.snapshot()
	var imported_store: Stores.Stores = Stores.from_snapshot(store_input).value
	store_input.store_value.clear()
	_equal(imported_store.snapshot(), expected.stores, "Imported stores detach input")
	var prior: Dictionary = {"weapon_identity": 10, "spawner_identity": 20}
	var selected: Dictionary = Selection.select([], 0, prior, {"x": 0, "y": 0, "z": 0}, null, 1, 0, 0, 0).value
	selected.weapon_identity = 77
	_equal(prior, {"weapon_identity": 10, "spawner_identity": 20}, "Previous selection return is a value copy")


func _transport(fixture: Dictionary) -> void:
	var table := Charge.Table.new()
	var stores := Stores.Stores.new()
	var weapon := Selection.MountedWeapon.new()
	var before: Dictionary = table.snapshot()
	for bad: Variant in [null, true, 0.0, "0", -2147483649, 2147483648]:
		_check(not table.set_word("charge_bits", bad).ok, "Reject non-signed32 table word")
		_check(not weapon.set_word("ammo_store", bad).ok, "Reject non-signed32 mounted word")
		_check(not stores.store_value().set_word(0, bad).ok, "Reject non-signed32 array word")
		_check(not stores.store_value().get_word(bad).ok, "Reject non-signed32 array index")
		_equal(table.snapshot(), before, "Rejected table write is atomic")
	_equal(stores.snapshot(), {"store_value": [0,0,0,0,0,0], "store_overheat": [0,0,0,0,0,0],
		"store_heat": [0,0,0,0,0,0], "configuration_store_value": [0,0,0,0,0,0]}, "Rejected store writes are atomic")
	_equal(weapon.snapshot(), {"is_active": 0, "ammo_store": 0, "consumption_bits": 0, "zoom_mode": 0}, "Rejected mounted writes are atomic")
	_check(not table.set_word("unexpected", 1).ok and not weapon.set_word("unexpected", 1).ok, "Unknown scalar property refused")
	_check(not table.set_ready_to_charge_gate_active(1).ok, "Gate requires actual boolean")
	for index: int in [-2147483648, -1, 6, 2147483647]:
		_result(stores.store_value().set_word(index, 0), {"ok": false, "error_type": "IndexOutOfRangeException", "parameter": ""}, "Array index refusal")
	for record: Variant in [null, [], true, {}]:
		_check(not Charge.from_snapshot(record).ok, "Malformed table transport")
		_check(not Stores.from_snapshot(record).ok, "Malformed store transport")
		_check(not Selection.mounted_from_snapshot(record).ok, "Malformed mounted transport")
	var source: Dictionary = fixture.ownership.table.duplicate(true)
	source.levels.append(1)
	_check(not Charge.from_snapshot(source).ok, "Table has exactly five fixed levels")
	var store_source: Dictionary = fixture.ownership.stores.duplicate(true)
	store_source.store_heat.pop_back()
	_check(not Stores.from_snapshot(store_source).ok, "Each store buffer has exactly six words")
	var record: Dictionary = {"identity": 1, "active_word": 1, "target_mask": 1, "burst_counter": 0, "burst_size": 0,
		"ready_at_time_float_bits": 0, "minimum_range_float_bits": 0, "maximum_range_float_bits": 0,
		"minimum_target_height_float_bits": 0, "maximum_target_height_float_bits": 0}
	var parsed: Dictionary = Selection.candidate(record)
	_check(parsed.ok and parsed.value.has_current_mode and not parsed.value.uses_ballistic_arc and parsed.value.has_projectile_definition,
		"Candidate optional flags match source constructor defaults")
	parsed.value.identity = 3
	_equal(record.identity, 1, "Candidate value copy detached")
	for mask: Variant in [-1, 4294967296, 1.0, true]:
		record.target_mask = mask
		_check(not Selection.candidate(record).ok, "Candidate uint32 mask width/type")


func _result(actual: Dictionary, expected: Dictionary, label: String) -> void:
	_equal(actual.get("ok"), expected.ok, label + "/success")
	if actual.get("ok") != expected.ok: return
	if expected.ok: _equal(actual.get("value"), expected.value, label + "/value")
	else:
		_equal(actual.get("error_type"), expected.error_type, label + "/error-type")
		_equal(actual.get("parameter", ""), expected.parameter, label + "/parameter")


func _equal(actual: Variant, expected: Variant, label: String) -> void:
	_check(_same(actual, expected), label + " expected=" + str(expected) + " actual=" + str(actual))


func _same(actual: Variant, expected: Variant) -> bool:
	if typeof(actual) != typeof(expected): return false
	if actual is Dictionary:
		if actual.size() != expected.size(): return false
		for key: Variant in expected:
			if not actual.has(key) or not _same(actual[key], expected[key]): return false
		return true
	if actual is Array:
		if actual.size() != expected.size(): return false
		for index: int in range(actual.size()):
			if not _same(actual[index], expected[index]): return false
		return true
	return actual == expected


func _check(condition: bool, label: String) -> void:
	_checks += 1
	_counts[_group] = _counts.get(_group, 0) + 1
	if not condition:
		_failure_count += 1
		if _failures.size() < 32: _failures.append(label)


func _finish() -> void:
	_completed.append(_group)
	print("RETAIL_WEAPON_GROUP: %s %d" % [_group, _counts.get(_group, 0)])


func _object_free(value: Variant) -> bool:
	if value is Dictionary:
		for key: Variant in value:
			if typeof(key) != TYPE_STRING or not _object_free(value[key]): return false
		return true
	if value is Array:
		for item: Variant in value:
			if not _object_free(item): return false
		return true
	return typeof(value) in [TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_STRING]


func _hash(bytes: PackedByteArray) -> String:
	var hashing := HashingContext.new()
	hashing.start(HashingContext.HASH_SHA256)
	hashing.update(bytes)
	return hashing.finish().hex_encode()


func _owned(path: String, fresh: bool) -> bool:
	var root: String = ProjectSettings.globalize_path("res://../..").simplify_path().path_join("local-data")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(root + "/"): return false
	if not DirAccess.dir_exists_absolute(path.get_base_dir()): return false
	var cursor: String = path
	while cursor.length() > root.length():
		var parent: DirAccess = DirAccess.open(cursor.get_base_dir())
		if parent == null or parent.is_link(cursor.get_file()): return false
		cursor = cursor.get_base_dir()
	if fresh: return not FileAccess.file_exists(path) and not DirAccess.dir_exists_absolute(path)
	return FileAccess.file_exists(path)
