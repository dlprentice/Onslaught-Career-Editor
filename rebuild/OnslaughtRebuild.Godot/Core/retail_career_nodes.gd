# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure mutable node/link owners from RetailCareerNodes.cs and
## RetailCareerReCalcLinks.cs. No Godot scene Node, save bytes or IO is involved.

const Values = preload("res://Core/retail_career_values.gd")


class CareerNode extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	const INTEGER_FIELDS: Array[String] = ["is_start_of_new_island", "complete", "lower_link", "higher_link", "world_number", "num_attempts"]
	var _fields: Dictionary = {"is_start_of_new_island": 0}
	var _base_words: Array[int] = []

	func _init() -> void:
		blank()


	func blank() -> void:
		# Blank deliberately leaves IsStartOfNewIsland unchanged.
		_fields.merge({"lower_link": -1, "higher_link": -1, "world_number": 0,
			"complete": 0, "num_attempts": 0, "ranking": -1.0}, true)
		_base_words.resize(9)
		_base_words.fill(-1)


	func field(name: String) -> Variant:
		return _fields.get(name)


	func set_field(name: String, value: Variant) -> Dictionary:
		if name == "ranking":
			if typeof(value) not in [TYPE_FLOAT, TYPE_INT]:
				return Values.failure("ArgumentException", "Ranking requires a float32 value.", name)
			_fields[name] = Values.float32(float(value))
		elif name in INTEGER_FIELDS and Values.is_int32(value):
			_fields[name] = value
		else:
			return Values.failure("ArgumentException", "Unknown field or non-int32 node value.", name)
		return Values.success()


	func base_words() -> Array[int]:
		return _base_words.duplicate()


	func snapshot() -> Dictionary:
		var result: Dictionary = _fields.duplicate()
		result.base_words = base_words()
		return result


	func does_base_thing_exist(offset: int) -> Dictionary:
		var word: int = offset >> 5
		if word < 0 or word >= 9:
			return Values.failure("ArgumentOutOfRangeException", "Core refuses an out-of-record base-thing read.", "offset")
		return Values.success(1 if (_base_words[word] & Values.mask_for(offset)) != 0 else 0)


	func set_base_thing_exist_to(offset: int, value: int) -> Dictionary:
		var word: int = offset >> 5
		if word < 0 or word >= 9:
			return Values.failure("ArgumentOutOfRangeException", "Core refuses an out-of-record base-thing write.", "offset")
		var mask: int = Values.mask_for(offset)
		_base_words[word] = Values.int32(_base_words[word] | mask if value == 1 else _base_words[word] & ~mask)
		return Values.success()


class Table extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _nodes: Array[CareerNode] = []

	func node_count() -> int:
		return _nodes.size()


	## Returns a detached list of the live node owners, like the C# table view.
	## Use snapshot() for detached values that cannot mutate the campaign.
	func nodes() -> Array[CareerNode]:
		return _nodes.duplicate()


	func add(world_number: int, complete: int) -> Dictionary:
		if not Values.is_int32(world_number) or not Values.is_int32(complete):
			return Values.failure("ArgumentException", "Node fields require int32 values.")
		if _nodes.size() >= 100:
			return Values.failure("InvalidOperationException", "MAX_NODES is 100.")
		var node := CareerNode.new()
		node.set_field("world_number", world_number)
		node.set_field("complete", complete)
		_nodes.append(node)
		return Values.success(node)


	func find(world_number: int) -> CareerNode:
		for node: CareerNode in _nodes:
			if node.field("world_number") == world_number:
				return node
		return null


	func at(index: int) -> CareerNode:
		return _nodes[index] if index >= 0 and index < _nodes.size() else null


	func complete_flag_of(world_number: int) -> Dictionary:
		var node: CareerNode = find(world_number)
		if node == null:
			return Values.failure("InvalidOperationException", "World is absent from the node table.")
		return Values.success(node.field("complete"))


	func grade_byte_for_world(world_number: int) -> Dictionary:
		var node: CareerNode = find(world_number)
		if node == null:
			return Values.failure("InvalidOperationException", "World is absent from the node table.")
		return Values.success(Values.grade_byte_from_ranking(node.field("ranking")) if node.field("complete") == 1 else 69)


	func snapshot() -> Array[Dictionary]:
		var result: Array[Dictionary] = []
		for node: CareerNode in _nodes:
			result.append(node.snapshot())
		return result


class Link extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _link_type: int = 0
	var _to_node: int = -1

	func link_type() -> int:
		return _link_type


	func to_node() -> int:
		return _to_node


	func set_field(name: String, value: Variant) -> Dictionary:
		if not Values.is_int32(value):
			return Values.failure("ArgumentException", "Link fields require int32 values.", name)
		match name:
			"link_type": _link_type = value
			"to_node": _to_node = value
			_: return Values.failure("ArgumentException", "Unknown link field.", name)
		return Values.success()


	func snapshot() -> Dictionary:
		return {"link_type": _link_type, "to_node": _to_node}
