# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Filesystem-free reader of the supported released PC career container.
## Port of RetailCareerSaveCodec.cs; layout provenance remains in
## reverse-engineering/save-file/save-format.md and RetailCareerRecordLayout.
## This module never discovers, opens, writes or serializes a save. Unknown
## bytes belong to the immutable read owner, not a reconstructed container.

const Campaign = preload("res://Core/retail_career_campaign.gd")
const Values = preload("res://Core/retail_career_values.gd")
const SUPPORTED_VERSION_WORD: int = 0x4bd1
const SUPPORTED_CONTAINER_LENGTH: int = 10004
const NODE_ARRAY_OFFSET: int = 0x0002 + 0x0004
const NODE_STRIDE: int = 64
const LINK_ARRAY_OFFSET: int = 0x0002 + 0x1904
const LINK_STRIDE: int = 8
const GOODIE_ARRAY_OFFSET: int = 0x0002 + 0x1f44
const GOODIE_COUNT: int = 300
const CAREER_IN_PROGRESS_OFFSET: int = 0x0002 + 0x2488


class Save extends RefCounted:
	var _bytes: PackedByteArray
	var _facts: Dictionary

	func _init(bytes: PackedByteArray, facts: Dictionary) -> void:
		_bytes = bytes.duplicate()
		_facts = facts.duplicate(true)

	## Detached exact bytes, including reserved fields and the unknown tail.
	func container_bytes() -> PackedByteArray:
		return _bytes.duplicate()

	func snapshot() -> Dictionary:
		return _facts.duplicate(true)

	func progression_summary() -> Dictionary:
		return {"career_in_progress": _facts.career_in_progress,
			"completed_world_count": _facts.completed_world_count,
			"unlocked_goodie_count": _facts.unlocked_goodie_count,
			"suggested_world_number": _facts.suggested_world_number}

	## The frontend receives only its two read-only facts. The Save owner retains
	## original bytes; loading a menu descriptor cannot become a save write.
	func project() -> Dictionary:
		return {"suggested_world_number": _facts.suggested_world_number,
			"selectable_world_numbers": _facts.selectable_world_numbers.duplicate()}

	func is_world_selectable(world_number: Variant) -> Dictionary:
		if not Values.is_int32(world_number):
			return {"ok": false, "error_type": "ArgumentException", "error": "World number must be an Int32."}
		return {"ok": true, "value": world_number in _facts.selectable_world_numbers}


static func read(source: Variant) -> Dictionary:
	if typeof(source) != TYPE_PACKED_BYTE_ARRAY:
		return {"ok": false, "error_type": "ArgumentException", "error": "Career source must be a PackedByteArray."}
	var bytes: PackedByteArray = source
	if bytes.size() != SUPPORTED_CONTAINER_LENGTH:
		return _failure("Unsupported career length %d; expected 10,004 bytes." % bytes.size())
	var version: int = bytes.decode_u16(0)
	if version != SUPPORTED_VERSION_WORD:
		return _failure("Unsupported career version 0x%04X; expected 0x%04X." % [version, SUPPORTED_VERSION_WORD])
	var world_nodes: Array[Dictionary] = Campaign.world_nodes()
	# All campaign links are admitted before the first node, in source order.
	for index: int in range(world_nodes.size() * 2):
		var offset: int = LINK_ARRAY_OFFSET + index * LINK_STRIDE
		var link_type: int = bytes.decode_s32(offset)
		if link_type < 0 or link_type > 2:
			return _failure("Malformed campaign link state %d at link %d." % [link_type, index])
		@warning_ignore("integer_division")
		var owner: Dictionary = world_nodes[index / 2]
		var expected: int = owner.lower_child_index if (index & 1) == 0 else owner.higher_child_index
		var destination: int = bytes.decode_s32(offset + 4)
		if destination != expected:
			return _failure("Malformed campaign link %d: destination %d, expected %d." % [index, destination, expected])
	var nodes: Array[Dictionary] = []
	var completed: int = 0
	for index: int in range(world_nodes.size()):
		var offset: int = NODE_ARRAY_OFFSET + index * NODE_STRIDE
		var world_number: int = bytes.decode_s32(offset + 0x10)
		var expected: int = world_nodes[index].world_number
		if world_number != expected:
			return _failure("Malformed campaign node %d: world %d, expected %d." % [index, world_number, expected])
		var lower: int = bytes.decode_s32(offset + 0x08)
		var higher: int = bytes.decode_s32(offset + 0x0c)
		if lower != index * 2 or higher != index * 2 + 1:
			return _failure("Malformed campaign node %d link indices: %d/%d." % [index, lower, higher])
		var complete: int = bytes.decode_s32(offset + 0x04)
		# Float words are preserved even when grade comparisons encounter NaN.
		var ranking_bits: int = bytes.decode_u32(offset + 0x3c)
		var grade: int = Values.grade_byte_from_ranking(bytes.decode_float(offset + 0x3c)) if complete == 1 else 69
		if complete == 1:
			completed += 1
		nodes.append({"index": index, "world_number": world_number, "complete": complete,
			"lower_link": lower, "higher_link": higher, "num_attempts": bytes.decode_s32(offset + 0x38),
			"ranking_bits": ranking_bits, "grade": grade})
	var unlocked: int = 0
	for index: int in range(GOODIE_COUNT):
		if bytes.decode_s32(GOODIE_ARRAY_OFFSET + index * 4) >= 2:
			unlocked += 1
	var selectable: Array[int] = []
	for node: Dictionary in world_nodes:
		if node.index == 0 or _has_complete_incoming_link(bytes, node.index, world_nodes.size() * 2):
			selectable.append(node.world_number)
	return {"ok": true, "value": Save.new(bytes, {"version_word": version, "container_length": bytes.size(),
		"career_in_progress": bytes.decode_s32(CAREER_IN_PROGRESS_OFFSET), "campaign_nodes": nodes,
		"completed_world_count": completed, "unlocked_goodie_count": unlocked,
		"selectable_world_numbers": selectable, "suggested_world_number": selectable[-1]})}


static func _has_complete_incoming_link(bytes: PackedByteArray, node_index: int, used_count: int) -> bool:
	for index: int in range(used_count):
		var offset: int = LINK_ARRAY_OFFSET + index * LINK_STRIDE
		if bytes.decode_s32(offset + 4) == node_index and bytes.decode_s32(offset) == 1:
			return true
	return false


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "RetailCareerSaveFormatException", "error": message}
