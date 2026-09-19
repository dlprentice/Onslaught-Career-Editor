# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure career stores from RetailCareerProgress.cs and
## RetailCareerUpdateGoodieStates.cs. Returned arrays are detached; writes are
## explicit operations and remain valid with release-build assertions disabled.


class Slots extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _words: Array[int] = []

	func _init() -> void:
		_words.resize(32)
		_words.fill(0)


	func words() -> Array[int]:
		return _words.duplicate()


	func set_slot(slot: int, value: int) -> void:
		# Retain the released 256-slot guard despite 1024 stored bits.
		if slot < 0 or slot >= 256:
			return
		var word: int = slot >> 5
		var mask: int = Values.mask_for(slot)
		_words[word] = Values.int32(_words[word] | mask if value == 1 else _words[word] & ~mask)


	func get_slot(slot: int) -> int:
		if slot < 0 or slot >= 256:
			return 0
		return 1 if (_words[slot >> 5] & Values.mask_for(slot)) != 0 else 0


	func copy_words(source: Variant) -> Dictionary:
		var admitted: Dictionary = Values.words(source, 32, "words")
		if not admitted.ok:
			return admitted
		_words.assign(admitted.value)
		return Values.success()


class Counters extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _new_goodie_count: int = 0
	var _first_goodie: int = 0
	var _killed_things: Array[int] = [0, 0, 0, 0, 0]

	func new_goodie_count() -> int:
		return _new_goodie_count


	func first_goodie() -> int:
		return _first_goodie


	func killed_things() -> Array[int]:
		return _killed_things.duplicate()


	func set_latch(name: String, value: Variant) -> Dictionary:
		if not Values.is_int32(value):
			return Values.failure("ArgumentException", "Counter latch requires an int32 value.", name)
		match name:
			"new_goodie_count": _new_goodie_count = value
			"first_goodie": _first_goodie = value
			_: return Values.failure("ArgumentException", "Unknown counter latch.", name)
		return Values.success()


	func get_and_reset_goodie_new_count() -> int:
		var value: int = _new_goodie_count
		_new_goodie_count = 0
		return value


	func get_and_reset_first_goodie() -> int:
		var value: int = _first_goodie
		_first_goodie = 0
		return value


	func update_things_killed(world_finished: int, source: Variant) -> Dictionary:
		var admitted: Dictionary = Values.words(source, 5, "thingsKilledThisLevel")
		if not admitted.ok:
			return admitted
		# The null/count checks precede the unscored-world skip in C#.
		if world_finished != 100:
			for index: int in range(5):
				_killed_things[index] = Values.int32(_killed_things[index] + admitted.value[index])
		return Values.success()


	func snapshot() -> Dictionary:
		return {"new_goodie_count": _new_goodie_count, "first_goodie": _first_goodie, "killed_things": killed_things()}


class Goodies extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _states: Array[int] = []

	func _init() -> void:
		_states.resize(300)
		_states.fill(0)


	func states() -> Array[int]:
		return _states.duplicate()


	func state(index: int) -> Dictionary:
		if index < 0 or index >= 300:
			return Values.failure("IndexOutOfRangeException", "Goodie index is outside its array.")
		return Values.success(_states[index])


	func set_state(index: int, value: int) -> Dictionary:
		if index < 0 or index >= 300:
			return Values.failure("IndexOutOfRangeException", "Goodie index is outside its array.")
		if not Values.is_int32(value):
			return Values.failure("ArgumentException", "Goodie state requires an int32 value.")
		_states[index] = value
		return Values.success()


	func set_new_if_not_done(index: int) -> Dictionary:
		if index < 0 or index >= 300:
			return Values.failure("IndexOutOfRangeException", "Goodie index is outside its array.")
		if _states[index] <= 1:
			_states[index] = 2
		return Values.success()


	func count_goodies() -> int:
		var count: int = 0
		for value: int in _states:
			if value >= 2:
				count += 1
		return count
