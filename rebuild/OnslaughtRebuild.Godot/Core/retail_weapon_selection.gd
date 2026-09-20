# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure RetailWeaponSelection.cs family. The mounted objects retain reference
## identity; cycle results report effects and never apply them. Unit selection
## is the existing finite, weapon-only/current-mode/nonballistic admission,
## with ordered PC24 operations and explicit float32 spills. Spawners, common
## AI, ballistic range and reference-reader lifetime remain unimplemented.
## Original source comments own pristine 74154bfa… evidence and the deliberate
## unordered energy/cycle comparisons; source-like >= replacements are wrong.
const Values = preload("res://Core/retail_career_values.gd")
const Store = preload("res://Core/retail_weapon_stores.gd")
const Charge = preload("res://Core/retail_weapon_charge.gd")
const Float24 = preload("res://Core/retail_float24.gd")
const Actor = preload("res://Core/thing_actor_state.gd")


class MountedWeapon extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	const Store = preload("res://Core/retail_weapon_stores.gd")
	var _active: int = 0
	var _ammo_store: int = 0
	var _consumption: int = 0
	var _zoom: int = 0

	func is_active() -> int: return _active
	func ammo_store() -> int: return _ammo_store
	func consumption_bits() -> int: return _consumption
	func zoom_mode() -> int: return _zoom

	func set_word(field: String, word: Variant) -> Dictionary:
		if not Values.is_int32(word): return Store.transport(field)
		match field:
			"is_active": _active = word
			"ammo_store": _ammo_store = word
			"consumption_bits": _consumption = word
			"zoom_mode": _zoom = word
			_: return Store.transport(field)
		return Values.success()

	func snapshot() -> Dictionary:
		return {"is_active": _active, "ammo_store": _ammo_store, "consumption_bits": _consumption, "zoom_mode": _zoom}


class Arithmetic extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	const Float24 = preload("res://Core/retail_float24.gd")
	var error: Dictionary = {}

	func read(word: int) -> float:
		if not error.is_empty(): return 0.0
		if not Float24.is_finite_word(word):
			error = Values.failure("NotSupportedException", "Unit selection requires finite float inputs.")
			return 0.0
		return Float24.read_word(word)

	func store(value: float) -> float:
		if not error.is_empty(): return 0.0
		var stored: float = Float24.store_float32(value)
		if not is_finite(stored):
			error = Values.failure("NotSupportedException", "Unit selection exceeded its finite float-store domain.")
			return 0.0
		return stored

	func _result(result: Float24.Result) -> float:
		if not result.ok and error.is_empty():
			error = Values.failure("ArgumentOutOfRangeException", "Retail arithmetic must receive a finite rounding input.", "value")
		return result.value if error.is_empty() else 0.0

	func add(left: float, right: float) -> float:
		return _result(Float24.try_add(left, right)) if error.is_empty() else 0.0
	func sub(left: float, right: float) -> float:
		return _result(Float24.try_subtract(left, right)) if error.is_empty() else 0.0
	func mul(left: float, right: float) -> float:
		return _result(Float24.try_multiply(left, right)) if error.is_empty() else 0.0
	func sqrt24(value: float) -> float:
		return _result(Float24.try_sqrt(value)) if error.is_empty() else 0.0
	func finish(value: Variant = null) -> Dictionary:
		return Values.success(value) if error.is_empty() else error.duplicate(true)


static func mounted_from_snapshot(snapshot: Variant) -> Dictionary:
	if not snapshot is Dictionary: return Store.transport("snapshot")
	for key: String in ["is_active", "ammo_store", "consumption_bits", "zoom_mode"]:
		if not Values.is_int32(snapshot.get(key)): return Store.transport(key)
	var weapon := MountedWeapon.new()
	for key: String in ["is_active", "ammo_store", "consumption_bits", "zoom_mode"]: weapon.set_word(key, snapshot[key])
	return Values.success(weapon)


static func can_walker_weapon_fire(stores: Variant, ammo_store: Variant, is_active: Variant) -> Dictionary:
	var admitted: Dictionary = Store.require_stores(stores)
	if not admitted.ok: return admitted
	if not Values.is_int32(is_active): return Store.transport("isActive")
	return can_weapon_fire(stores, ammo_store) if is_active != 0 else Values.success(false)


static func can_weapon_fire(stores: Variant, ammo_store: Variant) -> Dictionary:
	var admitted: Dictionary = Store.require_stores(stores)
	if not admitted.ok: return admitted
	if ammo_store == null: return Values.success(false)
	var heat: Dictionary = stores.store_heat().get_word(ammo_store)
	if not heat.ok: return heat
	var value: float = Float24.read_word(stores.store_value().get_word(ammo_store).value)
	if heat.value != 0:
		if value >= Float24.read_word(stores.configuration_store_value().get_word(ammo_store).value):
			return Values.success(false)
		return Values.success(stores.store_overheat().get_word(ammo_store).value == 0)
	return Values.success(value > 0.0)


static func search_terminates(current_weapon: Variant, weapon_count: Variant) -> Dictionary:
	if not Values.is_int32(current_weapon): return Store.transport("currentWeapon")
	if not Values.is_int32(weapon_count): return Store.transport("weaponCount")
	return Values.success(current_weapon >= 0 and current_weapon < weapon_count)


static func is_selectable(weapon: Variant, stores: Variant) -> Dictionary:
	if weapon == null: return Store.null_argument("weapon")
	var admitted: Dictionary = Store.require_stores(stores)
	if not admitted.ok: return admitted
	if not weapon is MountedWeapon: return Store.transport("weapon")
	if weapon.is_active() == 0: return Values.success(false)
	var heat: Dictionary = stores.store_heat().get_word(weapon.ammo_store())
	if not heat.ok: return heat
	if heat.value != 0: return Values.success(true)
	return Values.success(not (Float24.read_word(weapon.consumption_bits()) >
		Float24.read_word(stores.store_value().get_word(weapon.ammo_store()).value)))


static func change_weapon(weapons: Variant, current_weapon: Variant, stores: Variant) -> Dictionary:
	if weapons == null: return Store.null_argument("weapons")
	var admitted: Dictionary = Store.require_stores(stores)
	if not admitted.ok: return admitted
	if not weapons is Array: return Store.transport("weapons")
	var terminating: Dictionary = search_terminates(current_weapon, weapons.size())
	if not terminating.ok: return terminating
	if not terminating.value:
		return Values.failure("InvalidOperationException", "Retail dereferences null when there is no current weapon.")
	if weapons[current_weapon] == null:
		return Values.failure("NullReferenceException", "Object reference not set to an instance of an object.")
	if not weapons[current_weapon] is MountedWeapon: return Store.transport("weapon")
	var old_zoom: int = weapons[current_weapon].zoom_mode()
	var total: int = weapons.size()
	var cursor: int = current_weapon + 1
	while cursor != current_weapon:
		if cursor >= 0 and cursor < total:
			var selectable: Dictionary = is_selectable(weapons[cursor], stores)
			if not selectable.ok: return selectable
			if selectable.value:
				return Values.success(_cycle(cursor, true, old_zoom != weapons[cursor].zoom_mode()))
		cursor += 1
		if cursor >= total: cursor = 0
	return Values.success(_cycle(current_weapon, false, false))


static func _cycle(index: int, changed: bool, zooms: bool) -> Dictionary:
	return {"current_weapon": index, "changed": changed, "clears_slow_movement": changed,
		"loses_charge_on_new_weapon": changed, "auto_zooms_out": zooms}


## Candidate records use detached snake_case words. The three optional flags
## have the same defaults as the C# positional record constructor.
static func candidate(source: Variant) -> Dictionary:
	if not source is Dictionary: return Store.transport("weapon")
	var result: Dictionary = {}
	for key: String in ["identity", "active_word", "burst_counter", "burst_size", "ready_at_time_float_bits",
			"minimum_range_float_bits", "maximum_range_float_bits", "minimum_target_height_float_bits", "maximum_target_height_float_bits"]:
		if not Values.is_int32(source.get(key)): return Store.transport(key)
		result[key] = source[key]
	if not _uint32(source.get("target_mask")): return Store.transport("targetMask")
	result.target_mask = source.target_mask
	for key: String in ["has_current_mode", "uses_ballistic_arc", "has_projectile_definition"]:
		var flag: Variant = source.get(key, key != "uses_ballistic_arc")
		if typeof(flag) != TYPE_BOOL: return Store.transport(key)
		result[key] = flag
	return Values.success(result)


static func select(weapons: Variant, spawner_count: Variant, previous: Variant,
		owner_position: Variant, target_position: Variant, target_mask: Variant,
		terrain_height_float_bits: Variant, water_height_float_bits: Variant, now_float_bits: Variant) -> Dictionary:
	if weapons == null: return Store.null_argument("weapons")
	if not Values.is_int32(spawner_count): return Store.transport("spawnerCount")
	if spawner_count != 0:
		return Values.failure("NotSupportedException", "Unit spawner selection is not admitted by this weapon-only route.")
	if not weapons is Array: return Store.transport("weapons")
	var entries: Array[Dictionary] = []
	for input: Variant in weapons:
		var admitted: Dictionary = candidate(input)
		if not admitted.ok: return admitted
		var weapon: Dictionary = admitted.value
		if not weapon.has_current_mode or weapon.uses_ballistic_arc or not weapon.has_projectile_definition:
			return Values.failure("NotSupportedException", "Unit selection requires a current mode and nonballistic projectile definition.")
		entries.append(weapon)
	var prior: Dictionary = _previous(previous)
	if not prior.ok: return prior
	for weapon: Dictionary in entries:
		if weapon.burst_counter != 0 and weapon.burst_counter < weapon.burst_size: return prior
	if target_position == null: return prior
	var positions: Dictionary = _positions(owner_position, target_position)
	if not positions.ok: return positions
	if not _uint32(target_mask): return Store.transport("targetMask")
	for word: Variant in [terrain_height_float_bits, water_height_float_bits, now_float_bits]:
		if not Values.is_int32(word): return Store.transport("floatBits")
	var c := Arithmetic.new()
	var distance: float = _distance(c, positions.value.owner, positions.value.target)
	var now: float = c.read(now_float_bits)
	var selected: Dictionary = {"weapon_identity": null, "spawner_identity": null}
	var best_score: float = -1.0
	for weapon: Dictionary in entries:
		var scored: Variant = _score(c, weapon, positions.value.target, target_mask, distance,
			terrain_height_float_bits, water_height_float_bits, now)
		if not c.error.is_empty(): return c.finish()
		if scored != null and scored > best_score:
			best_score = scored
			selected = {"weapon_identity": weapon.identity, "spawner_identity": null}
	return c.finish(selected)


static func raw_distance_bits(owner_position: Variant, target_position: Variant) -> Dictionary:
	var positions: Dictionary = _positions(owner_position, target_position)
	if not positions.ok: return positions
	var c := Arithmetic.new()
	var result: float = _distance(c, positions.value.owner, positions.value.target)
	return c.finish(Store.bits(result))


static func score_bits(weapon: Variant, target: Variant, target_mask: Variant, distance_float_bits: Variant,
		terrain_height_float_bits: Variant, water_height_float_bits: Variant, now_float_bits: Variant) -> Dictionary:
	var admitted: Dictionary = candidate(weapon)
	if not admitted.ok: return admitted
	var point: Dictionary = Actor.Laws.vector(target, "target")
	if not point.ok: return point
	if not _uint32(target_mask): return Store.transport("targetMask")
	for word: Variant in [distance_float_bits, terrain_height_float_bits, water_height_float_bits, now_float_bits]:
		if not Values.is_int32(word): return Store.transport("floatBits")
	var c := Arithmetic.new()
	# Direct Score's distance/now are already floats; unlike raw record reads,
	# the unchanged C# method does not reject their NaN/infinity arguments.
	var result: Variant = _score(c, admitted.value, point.value, target_mask, Float24.read_word(distance_float_bits),
		terrain_height_float_bits, water_height_float_bits, Float24.read_word(now_float_bits))
	return c.finish(null if result == null else Store.bits(result))


static func _distance(c: Arithmetic, owner: Dictionary, target: Dictionary) -> float:
	var x: float = c.sub(c.read(target.x), c.read(owner.x))
	var y: float = c.sub(c.read(target.y), c.read(owner.y))
	var z: float = c.store(c.sub(c.read(target.z), c.read(owner.z)))
	var xy: float = c.add(c.mul(x, x), c.mul(y, y))
	return c.store(c.sqrt24(c.add(xy, c.mul(z, z))))


static func _score(c: Arithmetic, weapon: Dictionary, target: Dictionary, target_mask: int,
		distance: float, terrain_bits: int, water_bits: int, now: float) -> Variant:
	if weapon.active_word == 0 or (weapon.target_mask & target_mask) == 0: return null
	var height: float = c.sub(minf(c.read(terrain_bits), c.read(water_bits)), c.read(target.z))
	if not (height > c.read(weapon.minimum_target_height_float_bits)) or not (height < c.read(weapon.maximum_target_height_float_bits)):
		return null
	var score: float = 2000000.0 if (weapon.target_mask & target_mask & 0x80000) != 0 else 0.0
	var minimum: float = c.read(weapon.minimum_range_float_bits)
	var maximum: float = c.read(weapon.maximum_range_float_bits)
	if minimum > distance: score = c.add(c.sub(minimum, distance), score)
	elif maximum < distance: score = c.add(c.sub(distance, maximum), score)
	else: score = c.add(score, 1000000.0)
	var stored: float = c.store(score)
	if now > c.read(weapon.ready_at_time_float_bits): stored = c.store(c.add(stored, 1000000.0))
	return stored


static func _positions(owner: Variant, target: Variant) -> Dictionary:
	var a: Dictionary = Actor.Laws.vector(owner, "owner")
	if not a.ok: return a
	var b: Dictionary = Actor.Laws.vector(target, "target")
	if not b.ok: return b
	return Values.success({"owner": a.value, "target": b.value})


static func _previous(previous: Variant) -> Dictionary:
	if not previous is Dictionary: return Store.transport("previous")
	for key: String in ["weapon_identity", "spawner_identity"]:
		if not previous.has(key) or (previous[key] != null and not Values.is_int32(previous[key])):
			return Store.transport("previous")
	return Values.success({"weapon_identity": previous.weapon_identity, "spawner_identity": previous.spawner_identity})


static func _uint32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffffffff
