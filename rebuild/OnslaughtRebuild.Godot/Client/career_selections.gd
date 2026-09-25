# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Explicitly selected career bytes for the frontend. Recognizes only
## --career-save=<path>, reads those named files in argument order and performs
## no directory or installed-save discovery. It never writes. Each file becomes
## one frontend descriptor row: no slot, the file name without its extension,
## and the career's two read-only facts.

const CareerSave = preload("res://Core/retail_career_save.gd")
const PREFIX: String = "--career-save="


static func read_explicit_selections(arguments: PackedStringArray) -> Dictionary:
	var descriptors: Array[Dictionary] = []
	for argument: String in arguments:
		if not argument.begins_with(PREFIX):
			continue
		var selected: String = argument.substr(PREFIX.length())
		if selected.strip_edges().is_empty():
			return {"ok": false, "error_type": "ArgumentException",
				"error": "--career-save requires an explicitly selected file path."}
		var bytes: PackedByteArray = FileAccess.get_file_as_bytes(selected)
		if bytes.is_empty() and FileAccess.get_open_error() != OK:
			return {"ok": false, "error_type": "IOException",
				"error": "Could not read the selected career file %s: %s" % [selected, error_string(FileAccess.get_open_error())]}
		var career: Dictionary = CareerSave.read(bytes)
		if not career.ok:
			return career
		descriptors.append({"slot_number": null, "name": selected.get_file().get_basename(),
			"career": career.value.project()})
	return {"ok": true, "value": descriptors}
