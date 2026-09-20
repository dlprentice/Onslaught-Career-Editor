# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure RetailWeaponStores.cs / RetailWeaponStoreReadouts port. Float arrays
## retain raw signed32 words, including signaling NaNs until an operation reads
## them. The fixed buffers are reference objects: retrieving a buffer does not
## copy its state. snapshot() deliberately returns detached transport data.
## Source comments retain the pristine 74154bfa… x87 FISTP/RN evidence and the
## distinction between raw heat/overheat words and normalized booleans.
const Values = preload("res://Core/retail_career_values.gd")
const Float24 = preload("res://Core/retail_float24.gd")
const STORE_COUNT: int = 6
const FULL_AMMO_PERCENTAGE_FLOAT_BITS: int = 0x3f800000


## A fixed C# int[] or float[] carrier. Word writes validate before mutation;
## no resize/replacement API is exposed. Both raw float and integer arrays use
## signed words so merely inspecting a signaling NaN does not quiet it.
class Words extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _words: Array[int] = []

	func _init(count: int, initial_word: int = 0) -> void:
		_words.resize(count)
		_words.fill(initial_word)

	func size() -> int:
		return _words.size()

	func get_word(index: Variant) -> Dictionary:
		var admitted: Dictionary = _index(index)
		return Values.success(_words[index]) if admitted.ok else admitted

	func set_word(index: Variant, word: Variant) -> Dictionary:
		var admitted: Dictionary = _index(index)
		if not admitted.ok: return admitted
		if not Values.is_int32(word):
			return Values.failure("ArgumentException", "A stored word must fit signed int32.", "word")
		_words[index] = word
		return Values.success()

	func snapshot() -> Array[int]:
		return _words.duplicate()

	func _index(index: Variant) -> Dictionary:
		if not Values.is_int32(index):
			return Values.failure("ArgumentException", "An index must fit signed int32.", "index")
		if index < 0 or index >= _words.size():
			return Values.failure("IndexOutOfRangeException", "Index was outside the bounds of the array.")
		return Values.success()


class Stores extends RefCounted:
	var _value := Words.new(6)
	var _overheat := Words.new(6)
	var _heat := Words.new(6)
	var _configuration := Words.new(6)

	func store_value() -> Words: return _value
	func store_overheat() -> Words: return _overheat
	func store_heat() -> Words: return _heat
	func configuration_store_value() -> Words: return _configuration

	func snapshot() -> Dictionary:
		return {"store_value": _value.snapshot(), "store_overheat": _overheat.snapshot(),
			"store_heat": _heat.snapshot(), "configuration_store_value": _configuration.snapshot()}


## Detached raw-word transport admission, separate from the source readouts.
static func from_snapshot(snapshot: Variant) -> Dictionary:
	if not snapshot is Dictionary: return transport("snapshot")
	var admitted: Dictionary = {}
	for key: String in ["store_value", "store_overheat", "store_heat", "configuration_store_value"]:
		var words: Dictionary = Values.words(snapshot.get(key), STORE_COUNT, key)
		if not words.ok: return words
		admitted[key] = words.value
	var stores := Stores.new()
	for index: int in range(STORE_COUNT):
		stores.store_value().set_word(index, admitted.store_value[index])
		stores.store_overheat().set_word(index, admitted.store_overheat[index])
		stores.store_heat().set_word(index, admitted.store_heat[index])
		stores.configuration_store_value().set_word(index, admitted.configuration_store_value[index])
	return Values.success(stores)


static func ammo_percentage_bits(stores: Variant, ammo_store: Variant) -> Dictionary:
	var admitted: Dictionary = require_stores(stores)
	if not admitted.ok: return admitted
	if ammo_store == null: return Values.success(0)
	var value: Dictionary = stores.store_value().get_word(ammo_store)
	if not value.ok: return value
	var capacity: Dictionary = stores.configuration_store_value().get_word(ammo_store)
	if not capacity.ok: return capacity
	var quotient: float = divide_ieee(Float24.read_word(value.value), Float24.read_word(capacity.value))
	return Values.success(FULL_AMMO_PERCENTAGE_FLOAT_BITS if quotient > 1.0 else bits(quotient))


static func ammo_count(stores: Variant, ammo_store: Variant) -> Dictionary:
	var admitted: Dictionary = require_stores(stores)
	if not admitted.ok: return admitted
	if ammo_store == null: return Values.success(0)
	var heat: Dictionary = stores.store_heat().get_word(ammo_store)
	if not heat.ok: return heat
	if heat.value != 0: return Values.success(0)
	var value: Dictionary = stores.store_value().get_word(ammo_store)
	if not value.ok: return value
	return Values.success(_low_dword_of_fistp(Float24.read_word(value.value)))


static func is_energy_weapon(stores: Variant, ammo_store: Variant) -> Dictionary:
	var admitted: Dictionary = require_stores(stores)
	if not admitted.ok: return admitted
	return Values.success(0) if ammo_store == null else stores.store_heat().get_word(ammo_store)


static func is_weapon_overheated(stores: Variant, ammo_store: Variant) -> Dictionary:
	var admitted: Dictionary = require_stores(stores)
	if not admitted.ok: return admitted
	return Values.success(0) if ammo_store == null else stores.store_overheat().get_word(ammo_store)


static func require_stores(stores: Variant) -> Dictionary:
	if stores == null: return null_argument("stores")
	return Values.success() if stores is Stores else transport("stores")


static func null_argument(parameter: String) -> Dictionary:
	return Values.failure("ArgumentNullException", "Value cannot be null.", parameter)


static func transport(parameter: String) -> Dictionary:
	return Values.failure("ArgumentException", "The raw weapon-state transport has the wrong type or width.", parameter)


static func bits(value: float) -> int:
	return Values.int32(Float24.store_word(value))


## GDScript's zero-divisor diagnostic is not the source's IEEE division.
## A NaN numerator remains NaN; an invalid zero/zero operation produces the
## signed indefinite NaN observed by the unchanged managed reference owner.
static func divide_ieee(numerator: float, denominator: float) -> float:
	if denominator != 0.0: return numerator / denominator
	if is_nan(numerator): return numerator
	if numerator == 0.0: return Float24.read_word(0xffc00000)
	var negative: bool = ((bits(numerator) ^ bits(denominator)) & 0x80000000) != 0
	return -INF if negative else INF


static func _low_dword_of_fistp(value: float) -> int:
	if not is_finite(value): return 0
	var integral: float = floor(value) if value >= 0.0 else ceil(value)
	var fraction: float = value - integral
	if absf(fraction) > 0.5 or (absf(fraction) == 0.5 and fmod(integral, 2.0) != 0.0):
		integral += 1.0 if value > 0.0 else -1.0
	if integral < -9223372036854775808.0 or integral >= 9223372036854775808.0: return 0
	return Values.int32(int(integral))
