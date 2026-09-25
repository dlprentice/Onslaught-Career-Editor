# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure numeric/objective laws consumed by the frontend career update. Ports
## RetailCareerProgress/Grades, RetailEndLevelObjectives, the already admitted
## ForLevel100Won snapshot, and Client/RetailDebriefingProjection. This does not
## infer a first-play score or implement the separate score-time rewrite.

const INT_MIN: int = -2147483648
const INT_MAX: int = 2147483647
const OBJECTIVE_COUNT: int = 10


static func success(value: Variant = null) -> Dictionary:
	return {"ok": true, "value": value}


static func failure(kind: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}


static func is_int32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= INT_MIN and value <= INT_MAX


static func int32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word > INT_MAX else word


static func float32(value: float) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.decode_float(0)


static func float32_word(value: float) -> int:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.decode_u32(0)


static func signed_byte(value: int) -> int:
	var byte: int = value & 255
	return byte - 256 if byte >= 128 else byte


static func mask_for(index: int) -> int:
	return int32(1 << (index & 31))


## Admission for a C# IReadOnlyList<int>; null/count checks precede iteration.
## Call this at the source's use point, never before an earlier state mutation.
static func words(value: Variant, count: int, parameter: String) -> Dictionary:
	if value == null:
		return failure("ArgumentNullException", "Integer words must not be null.", parameter)
	if typeof(value) not in [TYPE_ARRAY, TYPE_PACKED_INT32_ARRAY, TYPE_PACKED_INT64_ARRAY]:
		return failure("ArgumentException", "Integer words require an array.", parameter)
	if count >= 0 and value.size() != count:
		return failure("ArgumentException", "Integer word count differs from the source contract.", parameter)
	var result: Array[int] = []
	for word: Variant in value:
		if not is_int32(word):
			return failure("ArgumentException", "Integer words must fit signed int32.", parameter)
		result.append(word)
	return success(result)


static func grade_byte_from_ranking(ranking: float) -> int:
	var stored: float = float32(ranking)
	# Retail's C3-only comparison takes its perfect-grade arm for NaN too.
	if stored == 1.0 or is_nan(stored):
		return 83
	if stored <= 0.0:
		return 69
	var quarters: float = floor(stored * 4.0)
	var low_byte: int = 0
	# x87's integer-indefinite low byte is zero, including positive infinity.
	if is_finite(quarters) and quarters >= -9223372036854775808.0 \
			and quarters < 9223372036854775808.0:
		low_byte = int(quarters) & 255
	return (68 - low_byte) & 255


static func grade_is_at_least(held: int, required: int) -> bool:
	var left: int = signed_byte(held)
	var right: int = signed_byte(required)
	if left == 83:
		return true
	if right == 83:
		return false
	return left <= right


static func secondary_verdict(statuses: Variant) -> Dictionary:
	var admitted: Dictionary = words(statuses, OBJECTIVE_COUNT, "secondaryObjectiveStatuses")
	if not admitted.ok:
		return admitted
	var result: bool = true
	var any_set: bool = false
	for status: int in admitted.value:
		if status != 1 and status != 2:
			continue
		any_set = true
		if status == 2:
			result = false
	return success({"result": result if any_set else false, "any_objective_set": any_set})


static func for_level100_won(ranking: float = 1.0, things_killed: Variant = null) -> Dictionary:
	var slots: Array[int] = []
	slots.resize(32)
	slots.fill(0)
	for index: int in [63, 64, 65, 66]:
		slots[index >> 5] = int32(slots[index >> 5] | mask_for(index))
	var primary: Array[int] = []
	primary.resize(10)
	primary.fill(0)
	for index: int in range(4):
		primary[index] = 1
	var secondary: Array[int] = []
	secondary.resize(10)
	secondary.fill(0)
	var base_things: Array[int] = []
	base_things.resize(288)
	base_things.fill(0)
	for index: int in range(35):
		base_things[index] = 1
	# ForLevel100Won accepts a supplied list without validating its count. The
	# consumer validates it later, after the slot overwrite, even for world100.
	return {"world_finished": 100, "final_state": 5, "ranking": float32(ranking),
		"secondary_statuses": secondary, "things_killed": [0, 0, 0, 0, 0] if things_killed == null else things_killed.duplicate(),
		"slot_words": slots, "primary_statuses": primary, "base_things_left": base_things}


static func summarize_objectives(statuses: Variant, parameter: String) -> Dictionary:
	var admitted: Dictionary = words(statuses, OBJECTIVE_COUNT, parameter)
	if not admitted.ok:
		return admitted
	var summary: int = 0
	for status: int in admitted.value:
		if status == 0:
			continue
		if status == 1:
			if summary == 0:
				summary = 1
		else:
			summary = 2
	return success(summary)


static func debriefing(snapshot: Dictionary, new_goodie_count: int, first_goodie_flag: int) -> Dictionary:
	var primary: Dictionary = summarize_objectives(snapshot.primary_statuses, "PrimaryStatuses")
	if not primary.ok:
		return primary
	var secondary: Dictionary = summarize_objectives(snapshot.secondary_statuses, "SecondaryStatuses")
	if not secondary.ok:
		return secondary
	if snapshot.world_finished == 500 and snapshot.final_state == 5:
		primary.value = 1
	return success({"world_finished": snapshot.world_finished,
		"mission_status": 1 if snapshot.final_state == 4 else (2 if snapshot.final_state == 5 else 0),
		"primary_objectives": primary.value, "secondary_objectives": secondary.value,
		"grade_byte": grade_byte_from_ranking(snapshot.ranking) if snapshot.final_state == 5 else null,
		"new_goodie_count": mini(new_goodie_count, 99), "first_goodie": first_goodie_flag != 0})
