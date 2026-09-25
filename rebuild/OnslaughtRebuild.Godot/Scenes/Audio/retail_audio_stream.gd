# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Public recipe, private decoded stream. Loading is explicit and runtime-only;
## saving a scene/resource serializes identities, never converted retail bytes.
enum Codec { PCM_WAV, OGG }
@export_file var source_path: String = ""
@export var codec: Codec = Codec.PCM_WAV
@export var looping: bool = false
var _decoded: AudioStream


func _validate_property(property: Dictionary) -> void:
	if property.name in ["source_path", "codec", "looping"]:
		property.usage = int(property.usage) | PROPERTY_USAGE_READ_ONLY


func load_stream() -> Dictionary:
	if Engine.is_editor_hint():
		return _failure("Editor inspection does not decode or play audio.")
	if _decoded != null:
		return {"ok": true, "value": _decoded}
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(source_path) if FileAccess.file_exists(source_path) else PackedByteArray()
	if codec == Codec.OGG:
		var stream: AudioStreamOggVorbis = null if bytes.is_empty() else AudioStreamOggVorbis.load_from_buffer(bytes)
		if stream == null:
			return _failure("Released Ogg stream is missing or invalid: " + source_path)
		stream.loop = looping
		_decoded = stream
	else:
		# Exact Level100Audio.LoadPcmWav envelope; no generalized WAV decoder or
		# stricter RIFF/byte-rate/even-length rule is substituted during this port.
		if bytes.size() < 44 or bytes.slice(0, 4) != "RIFF".to_ascii_buffer() \
				or bytes.slice(8, 12) != "WAVE".to_ascii_buffer() or bytes.slice(12, 16) != "fmt ".to_ascii_buffer() \
				or bytes.decode_u32(16) != 16 or bytes.decode_u16(20) != 1 or bytes.decode_u16(22) != 1 \
				or bytes.decode_u32(24) != 44100 or bytes.decode_u16(34) != 16 or bytes.slice(36, 40) != "data".to_ascii_buffer():
			return _failure("Curated audio '%s' is not 44.1 kHz mono 16-bit PCM WAV." % source_path)
		if bytes.decode_u32(40) != bytes.size() - 44:
			return _failure("Curated audio '%s' has invalid WAV framing." % source_path)
		var stream := AudioStreamWAV.new()
		stream.format = AudioStreamWAV.FORMAT_16_BITS
		stream.mix_rate = 44100
		stream.stereo = false
		stream.data = bytes.slice(44)
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD if looping else AudioStreamWAV.LOOP_DISABLED
		stream.loop_begin = 0
		@warning_ignore("integer_division")
		var frames: int = (bytes.size() - 44) / 2
		stream.loop_end = frames if looping else 0
		_decoded = stream
	return {"ok": true, "value": _decoded}


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
