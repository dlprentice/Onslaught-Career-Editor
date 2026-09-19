# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Read-only port of RetailStartupMediaIndex.cs. Decoded media stays outside
## res://; loading never repairs, imports, decodes, or writes a cache. The PNG
## check is the original envelope guard, not a second PNG decoder or CRC check.
## Text is a String when losslessly representable, otherwise a PackedInt32Array
## of UTF-16 units. This preserves NUL through JSON, formatting, comparisons,
## callback delivery and diagnostics; raw paths never enter a Godot String API.
## Linux literal-backslash paths require /usr/bin/{stat,cat,timeout} (GNU
## coreutils). They use direct argv and read-only binary pipes, never a shell.
## Other platforms' literal-path fallback is explicitly unsupported/unverified.

const StrictJson = preload("res://Core/strict_json.gd")
const Formatter = preload("res://Client/invariant_int32_format.gd")
const SCHEMA: String = "onslaught-startup-media.v4"
const READ_BLOCK: int = 1048576
const CUE_NAMES: Array[String] = ["LostToysLogo", "OpeningMontage", "Splash", "Level100IntroCutscene"]


class LiteralPipe extends RefCounted:
	# One owned timeout process supervises one coreutils reader. Pipes are
	# nonblocking; stderr is discarded in bounded pieces and is never printed.
	const PIECE: int = 65536
	var output: FileAccess
	var errors: FileAccess
	var pid: int
	var deadline: int
	var exit_code: int = -1
	var ended: bool = false
	var closed: bool = false
	var failure: Dictionary = {}

	func _init(job: Dictionary) -> void:
		output = job.stdio
		errors = job.stderr
		pid = job.pid
		deadline = Time.get_ticks_usec() + 17000000

	func _poll() -> void:
		if closed:
			return
		var available: int = errors.get_length()
		if available > 0:
			errors.get_buffer(mini(available, PIECE))
		if not ended and not OS.is_process_running(pid):
			ended = true
			exit_code = OS.get_process_exit_code(pid)
		if not ended and Time.get_ticks_usec() >= deadline and failure.is_empty():
			failure = {"ok": false, "error_type": "IOException", "error": "Literal-path helper exceeded its deadline."}

	func read_bytes(wanted: int) -> PackedByteArray:
		var bytes := PackedByteArray()
		while not closed and bytes.size() < wanted and failure.is_empty():
			_poll()
			var available: int = output.get_length()
			if available > 0:
				var chunk: PackedByteArray = output.get_buffer(mini(mini(available, PIECE), wanted - bytes.size()))
				if chunk.is_empty():
					failure = {"ok": false, "error_type": "IOException", "error": "Literal-path pipe read failed."}
					break
				bytes.append_array(chunk)
			elif ended:
				break
			else:
				OS.delay_usec(1000)
		return bytes

	func collect(limit: int) -> Dictionary:
		var bytes: PackedByteArray = read_bytes(limit + 1)
		if bytes.size() > limit:
			failure = {"ok": false, "error_type": "IOException", "error": "Literal-path metadata exceeded its output bound."}
		var result: Dictionary = finish(false)
		if not result.ok:
			return result
		return {"ok": true, "value": bytes, "exit_code": exit_code}

	func finish(require_success: bool) -> Dictionary:
		if not closed:
			# Closing a partial cat read delivers a broken pipe to that owned
			# reader. timeout also bounds blocked filesystem IO to 15s + 1s.
			output.close()
			while not ended and Time.get_ticks_usec() < deadline:
				_poll()
				if not ended:
					OS.delay_usec(1000)
			if not ended:
				# timeout's group-kill deadline has elapsed. Only its recorded
				# child pid can be killed here; no name/pattern/global cleanup.
				OS.kill(pid)
				var reap_deadline: int = Time.get_ticks_usec() + 1000000
				while OS.is_process_running(pid) and Time.get_ticks_usec() < reap_deadline:
					OS.delay_usec(1000)
				ended = not OS.is_process_running(pid)
				exit_code = OS.get_process_exit_code(pid) if ended else -1
				failure = {"ok": false, "error_type": "IOException", "error": "Literal-path helper required deadline cleanup."}
			errors.close()
			closed = true
		if not failure.is_empty():
			return failure
		if exit_code in [125, 126, 127]:
			return {"ok": false, "error_type": "MissingDependency", "error": "The literal-path coreutils helper could not execute.", "exit_code": exit_code}
		if require_success and exit_code != 0:
			return {"ok": false, "error_type": "IOException", "error": "The literal-path reader failed.", "exit_code": exit_code}
		return {"ok": true}

	func _notification(what: int) -> void:
		if what == NOTIFICATION_PREDELETE and not closed:
			finish(false)


class LiteralReadStream extends RefCounted:
	var process: LiteralPipe
	var length: int
	var position: int = 0
	var failure: Dictionary = {}

	func _init(pipe: LiteralPipe, byte_length: int) -> void:
		process = pipe
		length = byte_length

	func get_length() -> int:
		return length

	func get_position() -> int:
		return position

	func get_buffer(wanted: int) -> PackedByteArray:
		if not failure.is_empty():
			return PackedByteArray()
		var bytes: PackedByteArray = process.read_bytes(wanted)
		position += bytes.size()
		return bytes

	func seek(target: int) -> void:
		# The original PNG envelope parser only seeks forward over chunk data.
		if target < position:
			failure = {"ok": false, "error_type": "InvalidOperationException", "error": "Literal-path reader cannot seek backwards."}
			return
		while position < target:
			var wanted: int = mini(65536, target - position)
			if get_buffer(wanted).size() != wanted:
				failure = {"ok": false, "error_type": "IOException", "error": "Incomplete literal-path stream."}
				return

	func finish(require_success: bool) -> Dictionary:
		var result: Dictionary = process.finish(require_success)
		return failure if not failure.is_empty() else result


class Index extends RefCounted:
	var _root: Variant = ""
	var _splash: Variant = null
	var _unavailable: Variant = null
	var _clips: Dictionary = {}
	var _formats: Dictionary = {}
	var _audio: Dictionary = {}
	var _audio_paths: Dictionary = {}
	var _frame_path: Callable
	var _audio_path: Callable

	func _init(frame_path: Callable, audio_path: Callable) -> void:
		_frame_path = frame_path
		_audio_path = audio_path

	func root_path() -> Variant:
		return _root

	func has_splash() -> bool:
		return _splash != null

	func splash_relative_path() -> Variant:
		return _splash

	func unavailable() -> Variant:
		return _unavailable

	func clips() -> Dictionary:
		return _clips.duplicate(true)

	func clip_audio() -> Dictionary:
		return _audio.duplicate(true)

	func frame_relative_path(cue: Variant, frame_index: Variant) -> Dictionary:
		return _frame_path.call(self, cue, frame_index)

	func audio_relative_path(cue: Variant) -> Dictionary:
		return _audio_path.call(self, cue)


static func _new_index() -> Index:
	# Explicit stateless callables avoid an outer-class/global-class lookup and
	# do not capture the Index, which would form a reference cycle.
	return Index.new(_index_frame_relative_path, _index_audio_relative_path)


static func _index_frame_relative_path(index: Index, cue: Variant, frame_index: Variant) -> Dictionary:
	if not _int32(cue) or not _int32(frame_index):
		return _failure("ArgumentException", "Cue and frame index must be signed int32 values.")
	if not index._formats.has(cue):
		return _failure("InvalidOperationException", "Startup media has no decoded clip for " + _cue_name(cue) + ".")
	if not index._clips.has(cue) or frame_index < 0 or frame_index >= index._clips[cue].frame_count:
		return _failure("ArgumentOutOfRangeException", "Frame index outside the decoded range.")
	return _format_frame(index._formats[cue], frame_index + 1)


static func _index_audio_relative_path(index: Index, cue: Variant) -> Dictionary:
	if not _int32(cue):
		return _failure("ArgumentException", "Cue must be a signed int32 value.")
	if not index._audio_paths.has(cue):
		return _failure("InvalidOperationException", "Startup media has no decoded audio track for " + _cue_name(cue) + ".")
	return _ok(index._audio_paths[cue])


static func missing(reason: Variant) -> Index:
	var index: Index = _new_index()
	index._unavailable = reason
	return index


static func load_cache(root: Variant) -> Dictionary:
	return load_index(root, _native_exists, _native_exists)


## Missing/unusable media is a successful Index with unavailable()!=null.
## Errors are explicit only at points where C# Load throws, or when a formatter
## reports an unsupported conversion feature. Such a feature is never called
## a corrupt receipt and never silently drops an otherwise admitted clip.
## A custom file_exists(String) needs raw_file_exists(PackedInt32Array) if it
## must observe a path containing NUL or an unpaired UTF-16 surrogate. Without
## that callback, RawPathCallbackRequired explicitly reports the intact units.
## load_cache supplies File.Exists-equivalent handling, including false for NUL.
static func load_index(root: Variant, file_exists: Variant, raw_file_exists: Variant = null) -> Dictionary:
	if file_exists == null:
		return _failure("ArgumentNullException", "fileExists must not be null.")
	if typeof(file_exists) != TYPE_CALLABLE or not file_exists.is_valid():
		return _failure("ArgumentException", "fileExists must be a valid Callable.")
	if root == null or (_valid_text(root) and _white_space(root)):
		return _ok(missing("No startup media cache directory was configured."))
	if not _valid_text(root):
		return _failure("ArgumentException", "Startup media root must be a String or UTF-16 units.")
	if raw_file_exists != null and (typeof(raw_file_exists) != TYPE_CALLABLE or not raw_file_exists.is_valid()):
		return _failure("ArgumentException", "raw_file_exists must be a valid Callable.")
	var manifest: Variant = combine_path(root, "startup-media.json")
	var exists: Dictionary = _exists(file_exists, manifest, raw_file_exists)
	if not exists.ok:
		return exists
	if not exists.value:
		return _ok(missing(_concat_text(["No startup media index at ", manifest, ". Run `python ./rebuild/tools/materialize_retail_assets.py --startup-media`."])))
	var read: Dictionary = _read_manifest(manifest)
	if not read.ok:
		if read.get("error_type") in ["MissingDependency", "UnsupportedPlatform"]:
			return read
		return _ok(missing(_concat_text(["Startup media index at ", manifest, " is unreadable: ", read.error])))
	var document: StrictJson.Value = read.value
	var schema: StrictJson.Value = document.member("schema")
	if document.kind != "object" or schema == null or schema.kind != "string":
		return _wrong_schema(manifest)
	var schema_text: Dictionary = _json_string(schema)
	if not schema_text.ok:
		return schema_text
	if _units(schema_text.value) != _units(SCHEMA):
		return _wrong_schema(manifest)
	var index: Index = _new_index()
	index._root = _carrier(_units(root))
	var splash: Dictionary = _read_splash(document, root, file_exists, raw_file_exists)
	if not splash.ok:
		return splash
	index._splash = splash.value
	var clips: StrictJson.Value = document.member("clips")
	if clips != null and clips.kind == "object":
		# Preserve property order/duplicate names. A malformed later occurrence
		# does not erase a prior admitted clip or its independently admitted audio.
		for member: Dictionary in clips.members:
			var cue: Dictionary = _parse_cue(member.name)
			if not cue.ok:
				return cue # JsonProperty.Name decoding is outside C#'s clip catch.
			if cue.value == null:
				continue
			var result: Dictionary = _read_clip(index, cue.value, member.value, root, file_exists, raw_file_exists)
			if not result.ok and not _clip_catches(str(result.get("error_type"))):
				return result
	if index._clips.is_empty() and index._splash == null:
		return _ok(missing(_concat_text(["Startup media index at ", manifest, " listed no usable clip or still."])))
	return _ok(index)


static func _read_clip(index: Index, cue: int, source: StrictJson.Value, root: Variant, exists: Callable, raw_exists: Variant) -> Dictionary:
	var numbers: Dictionary = {}
	for key: String in ["frameCount", "fpsNumerator", "fpsDenominator", "width", "height"]:
		var result: Dictionary = _json_integer(source, key)
		if not result.ok:
			return result
		numbers[key] = result.value
	var format: Dictionary = _json_property_string(source, "framePathFormat")
	if not format.ok:
		return format
	var receipt: Dictionary = _json_property_string(source, "framesSha256")
	if not receipt.ok:
		return receipt
	if numbers.frameCount <= 0 or numbers.fpsNumerator <= 0 or numbers.fpsDenominator <= 0 \
			or numbers.width <= 0 or numbers.height <= 0 or format.value.is_empty() or _utf16_length(receipt.value) != 64:
		return _ok()
	var paths: Array = []
	for frame: int in range(1, int(numbers.frameCount) + 1):
		var relative: Dictionary = _format_frame(format.value, frame)
		if not relative.ok:
			return relative
		var path: Variant = combine_path(root, relative.value)
		var available: Dictionary = _exists(exists, path, raw_exists)
		if not available.ok:
			return available
		if not available.value:
			return _ok()
		paths.append(path)
	# Open first, then last; do not reject every raw path early. C# performs all
	# existence callbacks before either envelope check, and short-circuits here.
	for edge: Variant in [paths[0], paths[-1]]:
		var envelope: Dictionary = has_expected_png_envelope(edge, numbers.width, numbers.height)
		if not envelope.ok:
			return envelope
		if not envelope.value:
			return _ok()
	var digest: Dictionary = compute_frame_set_sha256(paths)
	if not digest.ok:
		return digest
	if not _hash_equal(digest.value, receipt.value):
		return _ok()
	index._clips[cue] = {"frame_count": numbers.frameCount, "fps_numerator": numbers.fpsNumerator,
		"fps_denominator": numbers.fpsDenominator, "width": numbers.width, "height": numbers.height}
	index._formats[cue] = format.value
	return _read_audio(index, cue, source, root, exists, raw_exists)


static func _read_audio(index: Index, cue: int, clip: StrictJson.Value, root: Variant, exists: Callable, raw_exists: Variant) -> Dictionary:
	var audio: StrictJson.Value = clip.member("audio")
	if audio == null or audio.kind != "object":
		return _ok()
	var numbers: Dictionary = {}
	for key: String in ["track", "sampleRate", "channels", "bitsPerSample", "sampleFrameCount"]:
		var result: Dictionary = _json_integer(audio, key, key == "sampleFrameCount")
		if not result.ok:
			return _ok() # This field-reading catch drops audio only.
		numbers[key] = result.value
	var relative: Dictionary = _json_property_string(audio, "path")
	var receipt: Dictionary = _json_property_string(audio, "outputSha256")
	if not relative.ok or not receipt.ok:
		return _ok()
	if numbers.track < 0 or numbers.sampleRate <= 0 or numbers.channels <= 0 or numbers.bitsPerSample != 16 \
			or numbers.sampleFrameCount <= 0 or relative.value.is_empty() or _utf16_length(receipt.value) != 64:
		return _ok()
	var path: Variant = combine_path(root, relative.value)
	var available: Dictionary = _exists(exists, path, raw_exists)
	if not available.ok:
		return available
	if not available.value:
		return _ok()
	var actual: Dictionary = read_pcm_wav_format(path)
	if not actual.ok:
		return _ok() if actual.error_type in ["IOException", "UnauthorizedAccessException", "InvalidDataException"] else actual
	var expected: Dictionary = {"sample_rate": numbers.sampleRate, "channels": numbers.channels,
		"bits_per_sample": numbers.bitsPerSample, "sample_frame_count": numbers.sampleFrameCount}
	if not actual.ok or actual.value != expected:
		return _ok()
	var hash_matches: Dictionary = _has_sha256(path, receipt.value)
	if not hash_matches.ok:
		return hash_matches
	if not hash_matches.value:
		return _ok()
	expected["track"] = numbers.track
	index._audio[cue] = expected
	index._audio_paths[cue] = relative.value
	return _ok()


static func _read_splash(document: StrictJson.Value, root: Variant, exists: Callable, raw_exists: Variant) -> Dictionary:
	var stills: StrictJson.Value = document.member("stills")
	if stills == null or stills.kind != "object":
		return _ok()
	var splash: StrictJson.Value = stills.member("Splash")
	if splash == null or splash.kind != "object":
		return _ok()
	var path_value: StrictJson.Value = splash.member("path")
	var hash_value: StrictJson.Value = splash.member("outputSha256")
	if path_value == null or path_value.kind != "string" or hash_value == null or hash_value.kind != "string":
		return _ok()
	var relative: Dictionary = _json_string(path_value)
	var receipt: Dictionary = _json_string(hash_value)
	if not relative.ok:
		return relative
	if not receipt.ok:
		return receipt
	if _white_space(relative.value) or _utf16_length(receipt.value) != 64:
		return _ok()
	var path: Variant = combine_path(root, relative.value)
	var available: Dictionary = _exists(exists, path, raw_exists)
	if not available.ok:
		return available
	if not available.value:
		return _ok()
	var envelope: Dictionary = has_expected_png_envelope(path, 512, 512)
	if not envelope.ok:
		return envelope
	if envelope.value:
		var hash_matches: Dictionary = _has_sha256(path, receipt.value)
		if not hash_matches.ok:
			return hash_matches
		if hash_matches.value:
			return _ok(relative.value)
	return _ok()


static func has_expected_png_envelope(path: Variant, width: int, height: int) -> Dictionary:
	var opened: Dictionary = _open_read(path)
	if not opened.ok:
		return _ok(false) if opened.error_type in ["IOException", "UnauthorizedAccessException"] else opened
	var file: RefCounted = opened.value
	var valid: bool = _png_stream(file, width, height)
	var closed: Dictionary = _close_read(file, valid)
	if not closed.ok:
		return _ok(false) if closed.error_type in ["IOException", "UnauthorizedAccessException"] else closed
	return _ok(valid)


static func _png_stream(file: RefCounted, width: int, height: int) -> bool:
	if file.get_buffer(8) != PackedByteArray([0x89, 80, 78, 71, 13, 10, 26, 10]):
		return false
	var first: bool = true
	var saw_header: bool = false
	var saw_payload: bool = false
	for _chunk: int in range(4096):
		var header: PackedByteArray = file.get_buffer(8)
		if header.size() != 8:
			return false
		var length: int = _big_u32(header, 0)
		var kind: PackedByteArray = header.slice(4, 8)
		if file.get_position() + length + 4 > file.get_length():
			return false
		if kind == "IHDR".to_ascii_buffer():
			if not first or length != 13:
				return false
			var payload: PackedByteArray = file.get_buffer(13)
			if payload.size() != 13 or _big_u32(payload, 0) != (width & 0xffffffff) or _big_u32(payload, 4) != (height & 0xffffffff):
				return false
			saw_header = true
		else:
			file.seek(file.get_position() + length)
		if file.get_buffer(4).size() != 4:
			return false
		if kind == "IDAT".to_ascii_buffer() and length > 0:
			saw_payload = true
		if kind == "IEND".to_ascii_buffer():
			return length == 0 and saw_header and saw_payload and file.get_position() == file.get_length()
		first = false
	return false


@warning_ignore("integer_division")
static func read_pcm_wav_format(path: Variant) -> Dictionary:
	var opened: Dictionary = _open_read(path)
	if not opened.ok:
		return opened
	var file: RefCounted = opened.value
	var length: int = file.get_length()
	var header: PackedByteArray = file.get_buffer(44)
	var closed: Dictionary = _close_read(file, false)
	if not closed.ok:
		return closed
	if header.size() != 44 or header.slice(0, 4) != "RIFF".to_ascii_buffer() \
			or header.slice(8, 12) != "WAVE".to_ascii_buffer() or header.slice(12, 16) != "fmt ".to_ascii_buffer() \
			or header.slice(36, 40) != "data".to_ascii_buffer():
		return _failure("InvalidDataException", "Not a canonical PCM header.")
	var riff_size: int = header.decode_u32(4)
	var format_size: int = header.decode_u32(16)
	var audio_format: int = header.decode_u16(20)
	var channels: int = header.decode_u16(22)
	var rate: int = header.decode_u32(24)
	var byte_rate: int = header.decode_u32(28)
	var align: int = header.decode_u16(32)
	var bits: int = header.decode_u16(34)
	var data_size: int = header.decode_u32(40)
	if format_size != 16 or audio_format != 1 or channels == 0 or rate == 0 or bits == 0 or bits % 8 != 0 \
			or align != channels * (bits / 8) or byte_rate != ((rate * align) & 0xffffffff) \
			or riff_size != length - 8 or data_size != length - 44 or data_size == 0 or data_size % align != 0:
		return _failure("InvalidDataException", "PCM dimensions or length disagree.")
	return _ok({"sample_rate": _signed32(rate), "channels": channels,
		"bits_per_sample": bits, "sample_frame_count": data_size / align})


static func compute_frame_set_sha256(paths: Array) -> Dictionary:
	var digest := HashingContext.new()
	if digest.start(HashingContext.HASH_SHA256) != OK:
		return _failure("InvalidOperationException", "Cannot initialize SHA256.")
	var domain: PackedByteArray = "onslaught-startup-frame-set.v1".to_ascii_buffer()
	domain.append(0)
	digest.update(domain)
	for path: Variant in paths:
		var opened: Dictionary = _open_read(path)
		if not opened.ok:
			return opened
		var file: RefCounted = opened.value
		digest.update(_ascii_replacement(_file_name(path)))
		digest.update(PackedByteArray([0]))
		digest.update(str(file.get_length()).to_ascii_buffer())
		digest.update(PackedByteArray([0]))
		var read: Dictionary = _append_stream(digest, file)
		var closed: Dictionary = _close_read(file, true)
		if not read.ok:
			return read
		if not closed.ok:
			return closed
	return _ok(digest.finish().hex_encode().to_upper())


static func compute_file_sha256(path: Variant) -> Dictionary:
	var digest := HashingContext.new()
	if digest.start(HashingContext.HASH_SHA256) != OK:
		return _failure("InvalidOperationException", "Cannot initialize SHA256.")
	var opened: Dictionary = _open_read(path)
	if not opened.ok:
		return opened
	var file: RefCounted = opened.value
	var result: Dictionary = _append_stream(digest, file)
	var closed: Dictionary = _close_read(file, true)
	if not result.ok:
		return result
	if not closed.ok:
		return closed
	return _ok(digest.finish().hex_encode().to_upper())


## A native PNG/WAV buffer decoder can consume the admitted file without
## routing its literal Linux name back through Godot's normalizing path API.
static func read_file_bytes_exact(path: Variant) -> Dictionary:
	var opened: Dictionary = _open_read(path)
	if not opened.ok:
		return opened
	var file: RefCounted = opened.value
	var bytes := PackedByteArray()
	var complete: bool = true
	if file is LiteralReadStream:
		while true:
			var block: PackedByteArray = file.get_buffer(READ_BLOCK)
			if block.is_empty():
				break
			bytes.append_array(block)
	else:
		var length: int = file.get_length()
		bytes = file.get_buffer(length)
		complete = bytes.size() == length
	var closed: Dictionary = _close_read(file, true)
	if not closed.ok:
		return closed
	return _ok(bytes) if complete else _failure("IOException", "Incomplete media byte read.")


static func _has_sha256(path: Variant, expected: Variant) -> Dictionary:
	var result: Dictionary = compute_file_sha256(path)
	if not result.ok:
		return _ok(false) if result.error_type in ["IOException", "UnauthorizedAccessException"] else result
	return _ok(_hash_equal(result.value, expected))


static func _append_stream(digest: HashingContext, file: RefCounted) -> Dictionary:
	if file is LiteralReadStream:
		# Like Stream.CopyTo, inventory reads continue to EOF. The earlier stat
		# length belongs to the receipt prefix; it is not a byte-read cutoff.
		while true:
			var block: PackedByteArray = file.get_buffer(READ_BLOCK)
			if block.is_empty():
				return _ok() # finish(true) separately verifies the child exit.
			if digest.update(block) != OK:
				return _failure("IOException", "Incomplete media byte inventory.")
	while file.get_position() < file.get_length():
		var wanted: int = mini(READ_BLOCK, file.get_length() - file.get_position())
		var block: PackedByteArray = file.get_buffer(wanted)
		if block.size() != wanted or digest.update(block) != OK:
			return _failure("IOException", "Incomplete media byte inventory.")
	return _ok()


## Both arguments are admitted text carriers (String or UTF-16 units).
static func combine_path(root: Variant, relative: Variant) -> Variant:
	# Path.Combine does not normalize, confine, or reinterpret backslashes on
	# Unix. Retain that behavior; receipt verification is not a path sanitizer.
	var windows: bool = OS.get_name() == "Windows"
	var left: PackedInt32Array = _units(root)
	var right: PackedInt32Array = _units(relative)
	if left.is_empty() or _rooted(right, windows):
		return _carrier(right)
	if right.is_empty():
		return _carrier(left)
	if left[-1] != 47 and not (windows and left[-1] in [92, 58]):
		left.append(92 if windows else 47)
	left.append_array(right)
	return _carrier(left)


static func _rooted(path: PackedInt32Array, windows: bool) -> bool:
	return not path.is_empty() and (path[0] == 47 or (windows and (path[0] == 92 or
		(path.size() >= 2 and path[1] == 58 and ((path[0] >= 65 and path[0] <= 90) or (path[0] >= 97 and path[0] <= 122))))))


static func _file_name(path: Variant) -> PackedInt32Array:
	var units: PackedInt32Array = _units(path)
	var separator: int = units.rfind(47)
	if OS.get_name() == "Windows":
		separator = maxi(separator, units.rfind(92))
		if separator < 0 and units.size() >= 2 and units[1] == 58:
			separator = 1
	return units.slice(separator + 1)


static func _ascii_replacement(value: PackedInt32Array) -> PackedByteArray:
	var bytes := PackedByteArray()
	for code: int in value:
		bytes.append(code if code < 128 else 63)
	return bytes


static func _json_integer(value: StrictJson.Value, key: String, wide: bool = false) -> Dictionary:
	if value.kind != "object":
		return _failure("InvalidOperationException", "JSON property owner is not an object.")
	var field: StrictJson.Value = value.member(key)
	if field == null:
		return _failure("KeyNotFoundException", "Missing property: " + key)
	if field.kind != "number":
		return _failure("InvalidOperationException", "Expected numeric property: " + key)
	var result: Dictionary = field.as_int64() if wide else field.as_int32()
	return result if result.ok else _failure("FormatException", str(result.error))


static func _json_property_string(value: StrictJson.Value, key: String) -> Dictionary:
	if value.kind != "object":
		return _failure("InvalidOperationException", "JSON property owner is not an object.")
	var field: StrictJson.Value = value.member(key)
	if field == null:
		return _failure("KeyNotFoundException", "Missing property: " + key)
	if field.kind == "null":
		return _ok("")
	return _json_string(field)


static func _json_string(value: StrictJson.Value) -> Dictionary:
	# JsonElement.GetString permits NUL, but rejects an unpaired JSON surrogate.
	# Validate through utf8_bytes without passing its bytes into a native String.
	var text: Dictionary = value.utf8_bytes()
	if not text.ok:
		return _failure("InvalidOperationException", str(text.error))
	return _ok(_carrier(value.string_units))


static func _parse_cue(value: StrictJson.Value) -> Dictionary:
	var decoded: Dictionary = _json_string(value)
	if not decoded.ok:
		return decoded
	var text: PackedInt32Array = _trim_white_space(_units(decoded.value), false)
	if text.is_empty():
		return _ok()
	if text[0] in [43, 45] or (text[0] >= 48 and text[0] <= 57):
		var number: Dictionary = _enum_number(text)
		if number.ok:
			return number
	var combined: int = 0
	var start: int = 0
	for end: int in range(text.size() + 1):
		if end < text.size() and text[end] != 44:
			continue
		var name: PackedInt32Array = _trim_white_space(text.slice(start, end))
		var matched: int = -1
		for index: int in range(CUE_NAMES.size()):
			if name == _units(CUE_NAMES[index]):
				matched = index
				break
		if matched < 0:
			return _ok()
		combined |= matched
		start = end + 1
	return _ok(combined)


static func _enum_number(text: PackedInt32Array) -> Dictionary:
	var negative: bool = text[0] == 45
	var start: int = 1 if negative or text[0] == 43 else 0
	if start == text.size():
		return {"ok": false}
	var result: int = 0
	var cursor: int = start
	while cursor < text.size() and text[cursor] >= 48 and text[cursor] <= 57:
		var digit: int = text[cursor] - 48
		result = result * 10 + digit
		if result > (2147483648 if negative else 2147483647):
			return {"ok": false}
		cursor += 1
	if cursor == start:
		return {"ok": false}
	# Enum's numeric path uses Number's ASCII trailing whitespace and legacy
	# trailing-NUL allowance. Its named path instead trims Char.IsWhiteSpace.
	while cursor < text.size() and (text[cursor] == 32 or (text[cursor] >= 9 and text[cursor] <= 13)):
		cursor += 1
	while cursor < text.size() and text[cursor] == 0:
		cursor += 1
	if cursor != text.size():
		return {"ok": false}
	return _ok(-result if negative else result)


static func _exists(callback: Callable, path: Variant, raw_callback: Variant) -> Dictionary:
	var result: Variant
	if typeof(path) == TYPE_STRING:
		result = callback.call(path)
	elif raw_callback == null:
		var failure: Dictionary = _failure("RawPathCallbackRequired", "fileExists needs the raw UTF-16 callback for this path.")
		failure["path_units"] = _units(path)
		return failure
	else:
		result = raw_callback.call(_units(path))
	if typeof(result) == TYPE_BOOL:
		return _ok(result)
	# A test/host can propagate the same exception category explicitly. A
	# missing callback return (including runtime abort) cannot look like false.
	if result is Dictionary and result.get("ok") == false and result.has("error_type"):
		return result
	return _failure("CallbackError", "fileExists did not return a bool or explicit failure.")


static func _native_exists(path: Variant) -> Variant:
	var result: Dictionary = file_exists_exact(path)
	return result.value if result.ok else result


static func _clip_catches(kind: String) -> bool:
	return kind in ["InvalidOperationException", "FormatException", "OverflowException", "KeyNotFoundException", "IOException", "UnauthorizedAccessException"]


static func _wrong_schema(manifest: Variant) -> Dictionary:
	return _ok(missing(_concat_text(["Startup media index at ", manifest, " is not schema '", SCHEMA, "'."])))


static func _hash_equal(actual: String, expected: Variant) -> bool:
	var left: PackedInt32Array = _units(actual.to_upper())
	var right: PackedInt32Array = _units(expected)
	if left.size() != right.size():
		return false
	for index: int in range(left.size()):
		var code: int = right[index]
		if code >= 97 and code <= 122:
			code -= 32
		if code != left[index]:
			return false
	return true


static func _big_u32(bytes: PackedByteArray, at: int) -> int:
	return (int(bytes[at]) << 24) | (int(bytes[at + 1]) << 16) | (int(bytes[at + 2]) << 8) | int(bytes[at + 3])


static func _signed32(value: int) -> int:
	return value - 0x100000000 if value >= 0x80000000 else value


static func _int32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _cue_name(value: int) -> String:
	return CUE_NAMES[value] if value >= 0 and value < CUE_NAMES.size() else str(value)


static func _utf16_length(value: Variant) -> int:
	return _units(value).size()


static func _white(code: int) -> bool:
	return (code >= 9 and code <= 13) or code in [32, 133, 160, 5760, 8232, 8233, 8239, 8287, 12288] or (code >= 8192 and code <= 8202)


static func _white_space(text: Variant) -> bool:
	for code: int in _units(text):
		if not _white(code):
			return false
	return true


static func _trim_white_space(text: PackedInt32Array, trim_end: bool = true) -> PackedInt32Array:
	var start: int = 0
	var end: int = text.size()
	while start < end and _white(text[start]):
		start += 1
	while trim_end and end > start and _white(text[end - 1]):
		end -= 1
	return text.slice(start, end)


## Explicit transport helpers. Native consumers can distinguish a raw carrier
## from a normal String without attempting a lossy native conversion.
static func text_units(value: Variant) -> Dictionary:
	if not _valid_text(value):
		return _failure("ArgumentException", "Expected a String or UTF-16 code units in [0,65535].")
	return _ok(_units(value))


static func text_from_units(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_PACKED_INT32_ARRAY or not _valid_text(value):
		return _failure("ArgumentException", "Expected UTF-16 code units in [0,65535].")
	return _ok(_carrier(value))


static func _valid_text(value: Variant) -> bool:
	if typeof(value) == TYPE_STRING:
		return true
	if typeof(value) != TYPE_PACKED_INT32_ARRAY:
		return false
	for code: int in value:
		if code < 0 or code > 0xffff:
			return false
	return true


# Inner text helpers receive admitted carriers only; public entry points reject
# other Variant types explicitly before reaching them.
static func _units(value: Variant) -> PackedInt32Array:
	if typeof(value) == TYPE_PACKED_INT32_ARRAY:
		return value.duplicate()
	var text: String = value
	var result := PackedInt32Array()
	for index: int in range(text.length()):
		var code: int = text.unicode_at(index)
		if code <= 0xffff:
			result.append(code)
		else:
			code -= 0x10000
			result.append(0xd800 | (code >> 10))
			result.append(0xdc00 | (code & 0x3ff))
	return result


static func _carrier(units: PackedInt32Array) -> Variant:
	if units.has(0):
		return units.duplicate()
	# Godot treats a leading FEFF as a BOM during UTF-8 decoding. The prefix
	# makes every JSON/path unit ordinary text, then is removed exactly once.
	var bytes := PackedByteArray([65])
	var cursor: int = 0
	while cursor < units.size():
		var code: int = units[cursor]
		cursor += 1
		if code >= 0xd800 and code <= 0xdbff:
			if cursor == units.size() or units[cursor] < 0xdc00 or units[cursor] > 0xdfff:
				return units.duplicate()
			code = 0x10000 + ((code - 0xd800) << 10) + units[cursor] - 0xdc00
			cursor += 1
		elif code >= 0xdc00 and code <= 0xdfff:
			return units.duplicate()
		_utf8_append(bytes, code)
	return bytes.get_string_from_utf8().substr(1)


static func _concat_text(parts: Array) -> Variant:
	var units := PackedInt32Array()
	for part: Variant in parts:
		units.append_array(_units(part))
	return _carrier(units)


static func _format_frame(template: Variant, frame: int) -> Dictionary:
	var result: Dictionary = Formatter.format_composite_units(_units(template), frame)
	return _ok(_carrier(result.value)) if result.ok else result


static func _io_path(path: Variant) -> Dictionary:
	if not _valid_text(path):
		return _failure("ArgumentException", "Expected a String or UTF-16 path.")
	var units: PackedInt32Array = _units(path)
	if units.is_empty() or units.has(0):
		var error: Dictionary = _failure("ArgumentException", "Path is empty or contains a NUL character.")
		error["path_units"] = units
		return error
	# JSON strings already reject unpaired surrogates. A caller-supplied root
	# can still contain one: .NET's Unix path encoding uses replacement UTF-8.
	# Keep the original units for callback/state identity, replacing only at IO.
	var bytes := PackedByteArray([65])
	var cursor: int = 0
	while cursor < units.size():
		var code: int = units[cursor]
		cursor += 1
		if code >= 0xd800 and code <= 0xdbff:
			if cursor < units.size() and units[cursor] >= 0xdc00 and units[cursor] <= 0xdfff:
				code = 0x10000 + ((code - 0xd800) << 10) + units[cursor] - 0xdc00
				cursor += 1
			else:
				code = 0xfffd
		elif code >= 0xdc00 and code <= 0xdfff:
			code = 0xfffd
		_utf8_append(bytes, code)
	return _ok(bytes.get_string_from_utf8().substr(1))


## File.Exists-compatible entry used by load_cache and focused filesystem
## comparisons. A literal backslash is never tested through Godot's path
## normalization, even when a different slash-normalized file happens to exist.
static func file_exists_exact(path: Variant) -> Dictionary:
	if not _valid_text(path):
		return _failure("ArgumentException", "Expected a String or UTF-16 path.")
	var native: Dictionary = _io_path(path)
	if not native.ok:
		return _ok(false) # File.Exists returns false for empty/NUL paths.
	if not _requires_literal_io(native.value):
		return _ok(FileAccess.file_exists(native.value))
	var info: Dictionary = _literal_stat(native.value)
	if not info.ok:
		return info
	return _ok(info.value.exists and (info.value.mode & 0xf000) != 0x4000)


static func _requires_literal_io(path: String) -> bool:
	# Engine pin 8898c2b3d, core/io/file_access.cpp:235: fix_path replaces
	# backslashes for ACCESS_FILESYSTEM too; Linux treats them as filename bytes.
	return OS.get_name() != "Windows" and path.contains("\\")


static func _start_literal(tool_name: String, arguments: PackedStringArray) -> Dictionary:
	if OS.get_name() != "Linux":
		return _failure("UnsupportedPlatform", "Literal-backslash filesystem IO is currently supported on Linux only.")
	var helper: String = "/usr/bin/" + tool_name
	for path: String in ["/usr/bin/timeout", helper]:
		if not FileAccess.file_exists(path):
			return _failure("MissingDependency", "Literal-backslash paths require GNU coreutils at " + path + ".")
	var argv := PackedStringArray(["--signal=TERM", "--kill-after=1s", "15s", helper])
	argv.append_array(arguments)
	var job: Dictionary = OS.execute_with_pipe("/usr/bin/timeout", argv, false)
	if job.is_empty() or not job.has("stdio") or not job.has("stderr") or not job.has("pid"):
		return _failure("MissingDependency", "Cannot start the literal-path coreutils reader.")
	return _ok(LiteralPipe.new(job))


static func _literal_stat(path: String) -> Dictionary:
	var started: Dictionary = _start_literal("stat", PackedStringArray(["--dereference", "--printf=%f %s", "--", path]))
	if not started.ok:
		return started
	var pipe: LiteralPipe = started.value
	var collected: Dictionary = pipe.collect(128)
	if not collected.ok:
		return collected
	if collected.exit_code == 1:
		return _ok({"exists": false, "mode": 0, "length": 0})
	if collected.exit_code != 0:
		return _failure("IOException", "Cannot inspect the literal-path file.")
	var data: PackedByteArray = collected.value
	for code: int in data:
		if not (code >= 48 and code <= 57) and not (code >= 97 and code <= 102) and code != 32:
			return _failure("IOException", "Unexpected literal-path metadata.")
	var parts: PackedStringArray = data.get_string_from_ascii().split(" ", true)
	if parts.size() != 2 or parts[0].is_empty() or parts[0].length() > 8 or parts[1].is_empty():
		return _failure("IOException", "Unexpected literal-path metadata fields.")
	var parsed: Dictionary = StrictJson.parse_bytes(parts[1].to_ascii_buffer())
	if not parsed.ok:
		return _failure("IOException", "Invalid literal-path file size.")
	var length: Dictionary = parsed.value.as_int64()
	if not length.ok or length.value < 0:
		return _failure("IOException", "Literal-path file size is outside signed int64.")
	return _ok({"exists": true, "mode": parts[0].hex_to_int(), "length": length.value})


static func _open_read(path: Variant) -> Dictionary:
	var native: Dictionary = _io_path(path)
	if not native.ok:
		return native
	if not _requires_literal_io(native.value):
		var file := FileAccess.open(native.value, FileAccess.READ)
		return _ok(file) if file != null else _failure("IOException", "Cannot read media file.")
	var info: Dictionary = _literal_stat(native.value)
	if not info.ok:
		return info
	if not info.value.exists or (info.value.mode & 0xf000) != 0x8000:
		return _failure("IOException", "Literal-path media is not a regular file.")
	var started: Dictionary = _start_literal("cat", PackedStringArray(["--", native.value]))
	if not started.ok:
		return started
	return _ok(LiteralReadStream.new(started.value, info.value.length))


static func _close_read(file: RefCounted, require_success: bool) -> Dictionary:
	if file is LiteralReadStream:
		return file.finish(require_success)
	file.close()
	return _ok()


static func _read_manifest(path: Variant) -> Dictionary:
	var opened: Dictionary = _open_read(path)
	if not opened.ok:
		return opened
	var file: RefCounted = opened.value
	var bytes: PackedByteArray = file.get_buffer(file.get_length())
	var closed: Dictionary = _close_read(file, true)
	if not closed.ok:
		return closed
	# File.ReadAllText detects Unicode BOMs and uses replacement fallback. Do
	# that before strict JSON parsing, rather than accepting Godot's JSON grammar.
	return StrictJson.parse_bytes(_file_text_utf8(bytes), false)


static func _file_text_utf8(bytes: PackedByteArray) -> PackedByteArray:
	var output := PackedByteArray()
	var cursor: int = 0
	var unit_size: int = 1
	var big_endian: bool = false
	if bytes.size() >= 4 and (bytes.slice(0, 4) == PackedByteArray([0, 0, 254, 255]) or bytes.slice(0, 4) == PackedByteArray([255, 254, 0, 0])):
		unit_size = 4
		big_endian = bytes[0] == 0
		cursor = 4
	elif bytes.size() >= 2 and (bytes.slice(0, 2) == PackedByteArray([254, 255]) or bytes.slice(0, 2) == PackedByteArray([255, 254])):
		unit_size = 2
		big_endian = bytes[0] == 254
		cursor = 2
	elif bytes.size() >= 3 and bytes.slice(0, 3) == PackedByteArray([239, 187, 191]):
		cursor = 3
	while cursor < bytes.size():
		var code: int
		if unit_size == 1:
			code = bytes[cursor]
			cursor += 1
			if code >= 128:
				var continuation: int = 1 if code >= 194 and code <= 223 else 2 if code >= 224 and code <= 239 else 3 if code >= 240 and code <= 244 else 0
				if continuation == 0:
					code = 0xfffd
				else:
					var lead: int = code
					code &= 0x1f if continuation == 1 else 0xf if continuation == 2 else 7
					for index: int in range(continuation):
						if cursor == bytes.size() or bytes[cursor] < 128 or bytes[cursor] > 191 \
								or (index == 0 and ((lead == 224 and bytes[cursor] < 160) or (lead == 237 and bytes[cursor] >= 160) or (lead == 240 and bytes[cursor] < 144) or (lead == 244 and bytes[cursor] >= 144))):
							code = 0xfffd
							break
						code = (code << 6) | (bytes[cursor] & 63)
						cursor += 1
		else:
			if cursor + unit_size > bytes.size():
				_utf8_append(output, 0xfffd)
				break
			code = 0
			for index: int in range(unit_size):
				code |= int(bytes[cursor + index]) << (8 * (unit_size - 1 - index if big_endian else index))
			cursor += unit_size
			if unit_size == 2 and code >= 0xd800 and code <= 0xdbff:
				var low: int = -1
				if cursor + 2 <= bytes.size():
					low = (int(bytes[cursor]) << 8) | bytes[cursor + 1] if big_endian else int(bytes[cursor]) | (int(bytes[cursor + 1]) << 8)
				if low >= 0xdc00 and low <= 0xdfff:
					code = 0x10000 + ((code - 0xd800) << 10) + low - 0xdc00
					cursor += 2
				else:
					code = 0xfffd
			elif code > 0x10ffff or (code >= 0xd800 and code <= 0xdfff):
				code = 0xfffd
		_utf8_append(output, code)
	return output


static func _utf8_append(bytes: PackedByteArray, code: int) -> void:
	if code < 0x80:
		bytes.append(code)
	elif code < 0x800:
		bytes.append(0xc0 | (code >> 6))
		bytes.append(0x80 | (code & 63))
	elif code < 0x10000:
		bytes.append(0xe0 | (code >> 12))
		bytes.append(0x80 | ((code >> 6) & 63))
		bytes.append(0x80 | (code & 63))
	else:
		bytes.append(0xf0 | (code >> 18))
		bytes.append(0x80 | ((code >> 12) & 63))
		bytes.append(0x80 | ((code >> 6) & 63))
		bytes.append(0x80 | (code & 63))


static func _ok(value: Variant = null) -> Dictionary:
	return {"ok": true, "value": value}


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
