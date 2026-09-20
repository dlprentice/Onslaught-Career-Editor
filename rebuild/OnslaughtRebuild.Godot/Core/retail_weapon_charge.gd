# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure current RetailWeaponCharge.cs contract. Table presence/index scaling,
## strict ready-time comparison, unordered FullyCharged and the independent
## 400 increment cap retain the original owner's evidence and limitations.
## This does not add spending, overheat, firing or a second simulation owner.
const Values = preload("res://Core/retail_career_values.gd")
const Store = preload("res://Core/retail_weapon_stores.gd")
const Float24 = preload("res://Core/retail_float24.gd")
const LEVEL_COUNT: int = 5
const ABSENT_LEVEL: int = -1
const VALUE_PER_LEVEL: int = 100
const INCREMENT_CAP_FLOAT_BITS: int = 0x43c80000


class Table extends RefCounted:
	const Store = preload("res://Core/retail_weapon_stores.gd")
	const Values = preload("res://Core/retail_career_values.gd")
	var _levels := Store.Words.new(5, -1)
	var _charge_rate: int = 0
	var _charge: int = 0
	var _ready_at: int = 0
	var _gate: bool = true

	func levels() -> Store.Words: return _levels
	func charge_rate_bits() -> int: return _charge_rate
	func charge_bits() -> int: return _charge
	func ready_at_time_bits() -> int: return _ready_at
	func ready_to_charge_gate_active() -> bool: return _gate

	func set_word(field: String, word: Variant) -> Dictionary:
		if not Values.is_int32(word): return Store.transport(field)
		match field:
			"charge_rate_bits": _charge_rate = word
			"charge_bits": _charge = word
			"ready_at_time_bits": _ready_at = word
			_: return Store.transport(field)
		return Values.success()

	func set_ready_to_charge_gate_active(active: Variant) -> Dictionary:
		if typeof(active) != TYPE_BOOL: return Store.transport("ready_to_charge_gate_active")
		_gate = active
		return Values.success()

	func snapshot() -> Dictionary:
		return {"levels": _levels.snapshot(), "charge_rate_bits": _charge_rate,
			"charge_bits": _charge, "ready_at_time_bits": _ready_at, "ready_to_charge_gate_active": _gate}


static func from_snapshot(snapshot: Variant) -> Dictionary:
	if not snapshot is Dictionary: return Store.transport("snapshot")
	var levels: Dictionary = Values.words(snapshot.get("levels"), LEVEL_COUNT, "levels")
	if not levels.ok: return levels
	for key: String in ["charge_rate_bits", "charge_bits", "ready_at_time_bits"]:
		if not Values.is_int32(snapshot.get(key)): return Store.transport(key)
	if typeof(snapshot.get("ready_to_charge_gate_active")) != TYPE_BOOL:
		return Store.transport("ready_to_charge_gate_active")
	var table := Table.new()
	for index: int in range(LEVEL_COUNT): table.levels().set_word(index, levels.value[index])
	for key: String in ["charge_rate_bits", "charge_bits", "ready_at_time_bits"]: table.set_word(key, snapshot[key])
	table.set_ready_to_charge_gate_active(snapshot.ready_to_charge_gate_active)
	return Values.success(table)


static func max_charge(weapon: Variant) -> Dictionary:
	var admitted: Dictionary = _require(weapon)
	if not admitted.ok: return admitted
	var maximum: int = 0
	for index: int in range(LEVEL_COUNT):
		if weapon.levels().get_word(index).value != ABSENT_LEVEL: maximum = index * VALUE_PER_LEVEL
	return Values.success(maximum)


static func get_charge_bits(weapon: Variant) -> Dictionary:
	var maximum: Dictionary = max_charge(weapon)
	if not maximum.ok: return maximum
	if maximum.value == 0: return Values.success(0)
	return Values.success(Store.bits(Float24.read_word(weapon.charge_bits()) / float(maximum.value)))


static func can_charge(weapon: Variant) -> Dictionary:
	var admitted: Dictionary = _require(weapon)
	if not admitted.ok: return admitted
	for index: int in range(1, LEVEL_COUNT):
		if weapon.levels().get_word(index).value != ABSENT_LEVEL: return Values.success(true)
	return Values.success(false)


static func fully_charged(weapon: Variant) -> Dictionary:
	var allowed: Dictionary = can_charge(weapon)
	if not allowed.ok: return allowed
	if not allowed.value: return Values.success(true)
	return Values.success(not (float(max_charge(weapon).value) > Float24.read_word(weapon.charge_bits())))


static func lose_charge(weapon: Variant) -> Dictionary:
	var admitted: Dictionary = _require(weapon)
	if not admitted.ok: return admitted
	return weapon.set_word("charge_bits", 0)


static func charge(weapon: Variant) -> Dictionary:
	var allowed: Dictionary = can_charge(weapon)
	if not allowed.ok: return allowed
	if not allowed.value: return Values.success()
	var current: float = Float24.read_word(weapon.charge_bits())
	if current >= 400.0: return Values.success()
	return weapon.set_word("charge_bits", Store.bits(Float24.read_word(weapon.charge_rate_bits()) + current))


static func ready_to_charge(weapon: Variant, now_float_bits: Variant) -> Dictionary:
	var admitted: Dictionary = _require(weapon)
	if not admitted.ok: return admitted
	if not Values.is_int32(now_float_bits): return Store.transport("nowFloatBits")
	if not weapon.ready_to_charge_gate_active(): return Values.success(true)
	return ready_time_elapsed(now_float_bits, weapon.ready_at_time_bits())


static func ready_time_elapsed(now_float_bits: Variant, ready_at_time_float_bits: Variant) -> Dictionary:
	if not Values.is_int32(now_float_bits): return Store.transport("nowFloatBits")
	if not Values.is_int32(ready_at_time_float_bits): return Store.transport("readyAtTimeFloatBits")
	return Values.success(Float24.read_word(now_float_bits) > Float24.read_word(ready_at_time_float_bits))


static func _require(weapon: Variant) -> Dictionary:
	if weapon == null: return Store.null_argument("weapon")
	return Values.success() if weapon is Table else Store.transport("weapon")
