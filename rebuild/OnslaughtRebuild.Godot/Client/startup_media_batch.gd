# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Production replacement for RetailStartupSequence.LoadVerifiedMediaBatch.
## Receipt admission belongs solely to startup_media_index; this adapter owns
## the same ordered batch dictionaries and absolute presentation paths.

const Media = preload("res://Client/startup_media_index.gd")
const SCHEMA: String = "onslaught-startup-verified-batch.v1"


static func load_verified_media_batch(media_root: Variant) -> Dictionary:
	var loaded: Dictionary = Media.load_cache(media_root)
	if not loaded.ok:
		return loaded
	var media: RefCounted = loaded.value
	var clips: Dictionary = {}
	var frames: Dictionary = {}
	var audio: Dictionary = {}
	var admitted_clips: Dictionary = media.clips()
	for cue: int in admitted_clips:
		var clip: Dictionary = admitted_clips[cue]
		clips[cue] = {"frame_count": clip.frame_count, "fps_numerator": clip.fps_numerator,
			"fps_denominator": clip.fps_denominator, "width": clip.width, "height": clip.height}
		var paths := PackedStringArray()
		for frame: int in range(clip.frame_count):
			var relative: Dictionary = media.frame_relative_path(cue, frame)
			if not relative.ok:
				return relative
			var path: Dictionary = _batch_path(media.root_path(), relative.value)
			if not path.ok:
				return path
			paths.append(path.value)
		frames[cue] = paths
	var admitted_audio: Dictionary = media.clip_audio()
	for cue: int in admitted_audio:
		var track: Dictionary = admitted_audio[cue]
		var relative: Dictionary = media.audio_relative_path(cue)
		if not relative.ok:
			return relative
		var path: Dictionary = _batch_path(media.root_path(), relative.value)
		if not path.ok:
			return path
		audio[cue] = {"path": path.value, "sample_rate": track.sample_rate, "channels": track.channels}
	var splash: String = ""
	if media.splash_relative_path() != null:
		var path: Dictionary = _batch_path(media.root_path(), media.splash_relative_path())
		if not path.ok:
			return path
		splash = path.value
	var unavailable: Variant = media.unavailable()
	if unavailable != null and typeof(unavailable) != TYPE_STRING:
		return _unsupported_text(unavailable, "The startup batch unavailable field requires a native String.")
	return {"ok": true, "value": {"schema": SCHEMA, "clips": clips, "frame_paths": frames,
		"audio": audio, "splash_path": splash, "unavailable": "" if unavailable == null else unavailable}}


static func _batch_path(root: Variant, relative: Variant) -> Dictionary:
	var path: Dictionary = get_full_path(Media.combine_path(root, relative))
	if path.ok and typeof(path.value) != TYPE_STRING:
		return _unsupported_text(path.value, "The startup batch path requires a native String.")
	return path


## Path.GetFullPath on Unix is lexical: only '/' separates names, dot segments
## collapse above the root, symlinks are not resolved, and a final '/' survives.
## This independent component-stack implementation is checked against .NET
## outputs, including raw UTF-16. Do not replace it with String.simplify_path:
## Godot also treats '\\' as a separator on Linux and would change file identity.
## current_directory is an explicit test seam; production uses the process CWD.
static func get_full_path(path: Variant, current_directory: Variant = null) -> Dictionary:
	if path == null:
		return _failure("ArgumentNullException", "Path must not be null.")
	var encoded: Dictionary = Media.text_units(path)
	if not encoded.ok:
		return encoded
	var units: PackedInt32Array = encoded.value
	if units.is_empty() or units.has(0):
		return _failure("ArgumentException", "Path is empty or contains NUL.")
	if OS.get_name() == "Windows":
		return _failure("UnsupportedPlatform", "Windows full-path rules require a separately validated native implementation.")
	if units[0] != 47:
		var base: Variant = current_directory
		if base == null:
			var directory := DirAccess.open(".")
			if directory == null:
				return _failure("IOException", "Cannot resolve the process current directory.")
			base = directory.get_current_dir()
		var base_units: Dictionary = Media.text_units(base)
		if not base_units.ok:
			return base_units
		var prefix: PackedInt32Array = base_units.value
		if prefix.is_empty() or prefix[0] != 47 or prefix.has(0):
			return _failure("ArgumentException", "Current directory must be an absolute Unix path.")
		if prefix[-1] != 47:
			prefix.append(47)
		prefix.append_array(units)
		units = prefix
	var trailing_separator: bool = units[-1] == 47
	var parts: Array[PackedInt32Array] = []
	var start: int = 0
	for end: int in range(units.size() + 1):
		if end < units.size() and units[end] != 47:
			continue
		var part: PackedInt32Array = units.slice(start, end)
		start = end + 1
		if part.is_empty() or part == PackedInt32Array([46]):
			continue
		if part == PackedInt32Array([46, 46]):
			if not parts.is_empty():
				parts.pop_back()
			continue
		parts.append(part)
	var result := PackedInt32Array([47])
	for index: int in range(parts.size()):
		if index > 0:
			result.append(47)
		result.append_array(parts[index])
	if trailing_separator and not parts.is_empty():
		result.append(47)
	return Media.text_from_units(result)


static func _unsupported_text(value: Variant, message: String) -> Dictionary:
	var failure: Dictionary = _failure("UnsupportedString", message)
	failure["text_units"] = Media.text_units(value).value
	return failure


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
