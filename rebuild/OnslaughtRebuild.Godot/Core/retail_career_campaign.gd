# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Actual pure career update consumed by RetailFrontendSession. The order is
## RetailCareerCampaign.ApplyUpdate/ReCalcLinks and UpdateGoodieStates, including
## partial writes before an error. Unsupported world500 remains an explicit
## error; a graph row never claims that its world has a playable reconstruction.

const Values = preload("res://Core/retail_career_values.gd")
const Nodes = preload("res://Core/retail_career_nodes.gd")
const Progress = preload("res://Core/retail_career_progress.gd")
const ROOT_WORLD_NUMBER: int = 100
# RetailWorldCatalog.cs, from pinned GPL Career.cpp level_structure[43][5].
const WORLD_ROWS: Array = [
	[100, 1, -1, 110, -1], [110, 2, -1, -1, -1], [200, 3, 4, 211, 212],
	[211, 5, 6, 231, 232], [212, 5, 6, 231, 232], [221, 7, 8, -1, -1],
	[222, 7, 8, -1, -1], [231, 9, -1, -1, -1], [232, 9, -1, -1, -1],
	[300, 10, 11, 311, 312], [311, 12, 13, 321, 322], [312, 12, 13, 321, 322],
	[321, 14, 15, -1, -1], [322, 14, 15, -1, -1], [331, 16, -1, -1, -1],
	[332, 16, -1, -1, -1], [400, 17, 18, 411, 412], [411, 19, 20, 431, 432],
	[412, 19, 20, 431, 432], [421, 21, 22, -1, -1], [422, 21, 22, -1, -1],
	[431, 23, -1, -1, -1], [432, 23, -1, -1, -1], [500, 24, 25, -1, -1],
	[511, 26, 27, -1, -1], [512, 28, 29, -1, -1], [521, 30, -1, -1, -1],
	[522, 30, -1, -1, -1], [523, 30, -1, -1, -1], [524, 30, -1, -1, -1],
	[600, 31, 32, -1, -1], [611, 33, 34, 621, 622], [612, 33, 34, 621, 622],
	[621, 35, -1, -1, -1], [622, 35, -1, -1, -1], [700, 36, -1, -1, -1],
	[710, 37, -1, 720, -1], [720, 38, 39, 731, 732], [731, 40, -1, -1, -1],
	[732, 41, -1, -1, -1], [741, -1, -1, -1, -1], [742, 42, -1, -1, -1],
	[800, -1, -1, -1, -1],
]


class Campaign extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	const Nodes = preload("res://Core/retail_career_nodes.gd")
	const Progress = preload("res://Core/retail_career_progress.gd")
	var _nodes := Nodes.Table.new()
	var _links: Array[Nodes.Link] = []
	var _counters := Progress.Counters.new()
	var _slots := Progress.Slots.new()
	var _goodies := Progress.Goodies.new()
	var _career_in_progress: int = 0

	func nodes() -> Nodes.Table:
		return _nodes


	func links() -> Array[Nodes.Link]:
		return _links.duplicate()


	func append_link(link: Nodes.Link) -> void:
		# List<RetailCareerNodeLink> can contain null or repeated identities.
		# Keep both: competing-parent comparison is reference identity, not data.
		_links.append(link)


	func counters() -> Progress.Counters:
		return _counters


	func slots() -> Progress.Slots:
		return _slots


	func goodies() -> Progress.Goodies:
		return _goodies


	func career_in_progress() -> int:
		return _career_in_progress


	func get_link(index: int) -> Nodes.Link:
		return _links[index] if index >= 0 and index < _links.size() else null


	func snapshot() -> Dictionary:
		var link_values: Array = []
		for link: Nodes.Link in _links:
			link_values.append(null if link == null else link.snapshot())
		return {"nodes": _nodes.snapshot(), "links": link_values, "counters": _counters.snapshot(),
			"slots": _slots.words(), "goodies": _goodies.states(), "career_in_progress": _career_in_progress}


	func is_world_selectable(world_number: int) -> Dictionary:
		var index: int = -1
		for row_index: int in range(WORLD_ROWS.size()):
			if WORLD_ROWS[row_index][0] == world_number:
				index = row_index
				break
		if index < 0:
			return Values.success(false)
		if world_number == 100:
			return Values.success(true)
		for link: Nodes.Link in _links:
			if link == null:
				return Values.failure("NullReferenceException", "Selection encountered a null career link.")
			if link.to_node() == index and link.link_type() != 0:
				return Values.success(true)
		return Values.success(false)


	## snapshot has scalar final_state/world_finished/ranking and nullable lists
	## secondary_statuses/things_killed/slot_words/base_things_left. Admission of
	## list contents stays at the source's actual use point, preserving failures.
	func apply_update(snapshot_value: Dictionary) -> Dictionary:
		for key: String in ["final_state", "world_finished"]:
			if not Values.is_int32(snapshot_value.get(key)):
				return Values.failure("ArgumentException", "Snapshot scalar requires int32.", key)
		if typeof(snapshot_value.get("ranking")) not in [TYPE_INT, TYPE_FLOAT]:
			return Values.failure("ArgumentException", "Snapshot ranking requires float32.", "ranking")
		if snapshot_value.final_state != 5:
			return update_goodie_states()
		var result: Dictionary
		if snapshot_value.get("slot_words") != null:
			result = _slots.copy_words(snapshot_value.slot_words)
			if not result.ok:
				return result
		result = _counters.update_things_killed(snapshot_value.world_finished, snapshot_value.get("things_killed"))
		if not result.ok:
			return result
		var node: Nodes.CareerNode = _nodes.find(snapshot_value.world_finished)
		if node == null:
			return Values.success()
		var ranking: float = Values.float32(float(snapshot_value.ranking))
		if ranking > float(node.field("ranking")):
			node.set_field("ranking", ranking)
		node.set_field("complete", 1)
		_career_in_progress = 1
		result = recalc_links(snapshot_value.world_finished, snapshot_value.get("secondary_statuses"), snapshot_value.get("base_things_left"))
		if not result.ok:
			return result
		return update_goodie_states()


	func recalc_links(world_finished: int, secondary_statuses: Variant, base_things_left: Variant = null) -> Dictionary:
		if world_finished == 500:
			return Values.failure("InvalidOperationException", "World 500's slot-gated child-link arm is not this owner.")
		var finished: Nodes.CareerNode = _nodes.find(world_finished)
		if finished == null:
			return Values.success()
		if base_things_left != null and world_finished == 100:
			var destination: Nodes.CareerNode = _nodes.find(110)
			if destination != null:
				var copied: Dictionary = update_base_world_exists_stuff_for_node(destination, base_things_left)
				if not copied.ok:
					return copied
		var verdict: Dictionary = Values.secondary_verdict(secondary_statuses)
		if not verdict.ok:
			return verdict
		_try_complete_child(get_link(finished.field("lower_link")), false, verdict.value.result)
		_try_complete_child(get_link(finished.field("higher_link")), true, verdict.value.result)
		return Values.success()


	static func update_base_world_exists_stuff_for_node(node: Nodes.CareerNode, source: Variant) -> Dictionary:
		if node == null:
			return Values.failure("ArgumentNullException", "Destination node must not be null.", "node")
		var admitted: Dictionary = Values.words(source, -1, "baseThingsLeft")
		if not admitted.ok:
			return admitted
		for offset: int in range(288):
			node.set_base_thing_exist_to(offset, admitted.value[offset] if offset < admitted.value.size() else 0)
		return Values.success()


	func _try_complete_child(link: Nodes.Link, is_higher: bool, verdict: bool) -> void:
		if link == null or link.link_type() == 1:
			return
		if is_higher and not verdict:
			return
		link.set_field("link_type", 1)
		var to_node: Nodes.CareerNode = _nodes.at(link.to_node())
		if to_node == null:
			return
		for node: Nodes.CareerNode in _nodes.nodes():
			_mark_if_competing(get_link(node.field("lower_link")), link, to_node)
			_mark_if_competing(get_link(node.field("higher_link")), link, to_node)


	func _mark_if_competing(candidate: Nodes.Link, completed: Nodes.Link, to_node: Nodes.CareerNode) -> void:
		if candidate == null or candidate == completed or candidate.link_type() != 1:
			return
		if _nodes.at(candidate.to_node()) == to_node:
			candidate.set_field("link_type", 2)


	func update_goodie_states() -> Dictionary:
		var previously_new: int = _goodies.count_goodies()
		var zero_was_not_done: bool = _goodies.state(0).value <= 1
		var complete100: Dictionary = _nodes.complete_flag_of(100)
		if not complete100.ok:
			return complete100
		if complete100.value == 1:
			_goodies.set_new_if_not_done(0)
			_goodies.set_new_if_not_done(8)
		var complete110: Dictionary = _nodes.complete_flag_of(110)
		if not complete110.ok:
			return complete110
		if complete110.value == 1:
			_goodies.set_new_if_not_done(14)
		var grade100: Dictionary = _nodes.grade_byte_for_world(100)
		if not grade100.ok:
			return grade100
		for entry: Array in [[67, 78], [66, 121], [65, 164]]:
			if Values.grade_is_at_least(grade100.value, entry[0]):
				_goodies.set_new_if_not_done(entry[1])
		var grade110: Dictionary = _nodes.grade_byte_for_world(110)
		if not grade110.ok:
			return grade110
		if Values.grade_is_at_least(grade110.value, 67):
			_goodies.set_new_if_not_done(1)
			_goodies.set_new_if_not_done(79)
		_counters.set_latch("new_goodie_count", Values.int32(_counters.new_goodie_count() + _goodies.count_goodies() - previously_new))
		if zero_was_not_done and _goodies.state(0).value > 1:
			_counters.set_latch("first_goodie", 1)
		return Values.success()


static func create_cold_training_slice() -> Campaign:
	var career := Campaign.new()
	var training: Nodes.CareerNode = career.nodes().add(100, 0).value
	var next: Nodes.CareerNode = career.nodes().add(110, 0).value
	for destination: int in [1, -1, -1, -1]:
		var link := Nodes.Link.new()
		link.set_field("to_node", destination)
		career.append_link(link)
	training.set_field("lower_link", 0)
	training.set_field("higher_link", 1)
	next.set_field("lower_link", 2)
	next.set_field("higher_link", 3)
	return career


static func world_nodes() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for index: int in range(WORLD_ROWS.size()):
		var row: Array = WORLD_ROWS[index]
		result.append({"index": index, "world_number": row[0], "lower_child_index": row[1],
			"higher_child_index": row[2], "primary_base_world": row[3], "secondary_base_world": row[4]})
	return result


static func find_world(world_number: int) -> Variant:
	for node: Dictionary in world_nodes():
		if node.world_number == world_number:
			return node
	return null


static func lower_child_world(world_number: int) -> Variant:
	var node: Variant = find_world(world_number)
	return WORLD_ROWS[node.lower_child_index][0] if node != null and node.lower_child_index >= 0 else null


static func higher_child_world(world_number: int) -> Variant:
	var node: Variant = find_world(world_number)
	return WORLD_ROWS[node.higher_child_index][0] if node != null and node.higher_child_index >= 0 else null


static func is_world_later(current_world: int, dies_on_world: int) -> bool:
	var current: Variant = find_world(current_world)
	var dies: Variant = find_world(dies_on_world)
	if current == null or dies == null or current.index == dies.index:
		return false
	return _later(dies.index, current.index, {})


static func _later(dies_index: int, current_index: int, visited: Dictionary) -> bool:
	if dies_index == current_index:
		return true
	if visited.has(dies_index):
		return false
	visited[dies_index] = true
	var row: Array = WORLD_ROWS[dies_index]
	return (row[1] >= 0 and _later(row[1], current_index, visited)) \
		or (row[2] >= 0 and _later(row[2], current_index, visited))
