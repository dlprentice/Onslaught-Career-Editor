extends RefCounted
## The caller supplies bytes read from its own copy of the real tracked baseline.
## All mutations below affect memory only; this test never creates a save file.

const Codec = preload("../domain/career_save.gd")


static func run(original: PackedByteArray) -> Array[String]:
	var failures: Array[String] = []
	var untouched: PackedByteArray = original.duplicate()
	var opened: Dictionary = Codec.inspect(original)
	_check(opened.ok, "The owned real baseline must be recognized.", failures)
	if not opened.ok:
		return failures
	_check(opened.size == 10004 and opened.version == 0x4BD1, "Exact baseline size and version word.", failures)
	_check(opened.kills.size() == 5 and opened.nodes.size() == 100, "Expected inspection record counts.", failures)
	_check(opened.goodies.size() == 300 and opened.goodie_census.reserved == 67, "Reserved Goodie slots remain distinguishable.", failures)
	var same: Dictionary = Codec.compare(original, original.duplicate())
	_check(same.equal and same.changed_bytes == 0 and same.ranges.is_empty(), "No-edit round trip is byte-for-byte identical.", failures)
	for category: int in range(5):
		for target: int in [0, 1, 0x00FFFFFF]:
			if target == opened.kills[category]:
				continue
			var result: Dictionary = Codec.preview(original, {category: target})
			_check(result.ok, "Category %d accepts boundary %d." % [category, target], failures)
			if not result.ok:
				continue
			var output: PackedByteArray = result.bytes
			_check(output.size() == 10004, "Preview preserves exact file length.", failures)
			var first: int = 0x23F6 + category * 4
			# Literal offsets and independent byte arithmetic do not reuse the codec's decoder.
			var decoded: int = int(output[first]) | (int(output[first + 1]) << 8) | (int(output[first + 2]) << 16)
			_check(decoded == target, "Independent intended count check for category %d." % category, failures)
			var allowed: bool = true
			var changed: int = 0
			for offset: int in range(original.size()):
				if original[offset] != output[offset]:
					changed += 1
					if offset < first or offset >= first + 3:
						allowed = false
			_check(allowed and changed > 0 and changed <= 3, "Every unselected/unknown byte survives, including the packed high byte.", failures)
			_check(result.changes.size() == changed, "Preview describes the actual byte diff.", failures)
			_check(Codec.inspect(output).kills[category] == target, "Result reinspection agrees with the independent check.", failures)
			output[0] ^= 0x01
			_check(original == untouched, "Mutating returned output cannot mutate the original.", failures)

	var all_selected: Dictionary = {}
	for category: int in range(5):
		all_selected[category] = (int(opened.kills[category]) + 257) & 0xFFFFFF
	var combined: Dictionary = Codec.preview(original, all_selected)
	_check(combined.ok and combined.selected.size() == 5, "All five explicit category selections compose.", failures)
	if combined.ok:
		var output: PackedByteArray = combined.bytes
		var all_allowed: bool = true
		for offset: int in range(original.size()):
			if original[offset] != output[offset] and (offset < 0x23F6 or offset >= 0x240A or (offset - 0x23F6) % 4 == 3):
				all_allowed = false
		_check(all_allowed, "Combined edits preserve every byte outside the selected low 24-bit fields.", failures)
		for category: int in range(5):
			var first: int = 0x23F6 + category * 4
			var decoded: int = int(output[first]) | (int(output[first + 1]) << 8) | (int(output[first + 2]) << 16)
			_check(decoded == all_selected[category], "Combined selection applies every intended count.", failures)

	for selection: Dictionary in [{}, {-1: 1}, {5: 1}, {"0": 1}, {0: -1}, {0: 0x01000000}, {0: 1.5}, {0: true}, {0: opened.kills[0]}]:
		_check(not Codec.preview(original, selection).ok, "Invalid or unchanged selection is refused: %s" % str(selection), failures)
	var mixed_unchanged: Dictionary = {0: opened.kills[0], 1: (int(opened.kills[1]) + 1) & 0xFFFFFF}
	_check(not Codec.preview(original, mixed_unchanged).ok, "An unchanged explicit selection is not silently ignored in a mixed plan.", failures)
	var wrong_version: PackedByteArray = original.duplicate()
	wrong_version[0] ^= 1
	_check(not Codec.inspect(wrong_version).ok and not Codec.preview(wrong_version, {0: 1}).ok, "Bad version is refused before inspection/preview.", failures)
	var short_bytes: PackedByteArray = original.slice(0, original.size() - 1)
	var long_bytes: PackedByteArray = original.duplicate()
	long_bytes.append(0)
	for malformed: PackedByteArray in [PackedByteArray(), short_bytes, long_bytes]:
		_check(not Codec.inspect(malformed).ok and not Codec.preview(malformed, {0: 1}).ok, "Incorrect lengths cannot be edited.", failures)
	var changed_header: PackedByteArray = original.duplicate()
	changed_header[2] ^= 0x80
	_check(Codec.inspect(changed_header).ok, "Only the 16-bit version is magic; career header bytes are not magic.", failures)
	var tail_diff: Dictionary = Codec.compare(original, short_bytes)
	_check(not tail_diff.equal and not tail_diff.same_length and tail_diff.changed_bytes == 1, "Comparison counts a missing trailing byte.", failures)
	_check(tail_diff.changes[0].offset == 10003 and tail_diff.changes[0].after == -1, "Missing bytes use an explicit sentinel, not an invented zero.", failures)

	# Alter an owned in-memory baseline to exercise mixed known/unknown state handling.
	var mixed_links: PackedByteArray = original.duplicate()
	for index: int in range(200):
		mixed_links.encode_u32(0x1906 + index * 8 + 4, 0xFFFFFFFF)
	for index: int in range(4):
		mixed_links.encode_u32(0x1906 + index * 8, [0, 1, 2, 99][index])
		mixed_links.encode_u32(0x1906 + index * 8 + 4, index)
	var census: Dictionary = Codec.inspect(mixed_links).link_census
	_check(census.used == 4 and census.locked == 1 and census.complete == 1 and census.broken == 1 and census.unknown == 1, "Broken/unknown links are not counted as complete, and destination zero is used.", failures)
	var mixed_goodies: PackedByteArray = original.duplicate()
	mixed_goodies.encode_u32(0x1F46 + 232 * 4, 99)
	mixed_goodies.encode_u32(0x1F46 + 233 * 4, 2)
	var goodie_info: Dictionary = Codec.inspect(mixed_goodies)
	_check(goodie_info.goodies[232].label == "unknown" and goodie_info.goodies[233].label == "reserved", "Reserved slots are never presented as earned/unlocked.", failures)
	var unusual_values: PackedByteArray = original.duplicate()
	unusual_values.encode_u32(0x0006 + 0x3C, 0x7FC00000)
	unusual_values.encode_u32(0x248E, 0x7F800000)
	var unusual_info: Dictionary = Codec.inspect(unusual_values)
	_check(not unusual_info.nodes[0].rank_known and not unusual_info.volumes.sound.finite, "Unmapped rank and nonfinite stored volume remain visible as unsupported values.", failures)
	_check(original == untouched, "Inspection, previews and malformed-input checks never mutate the baseline.", failures)
	return failures


static func _check(condition: bool, message: String, failures: Array[String]) -> void:
	if not condition:
		failures.append(message)
