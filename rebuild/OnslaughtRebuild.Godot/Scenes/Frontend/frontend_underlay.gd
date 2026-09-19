# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Shared FEBack production recipe. Read-only materialized input; decoded frames
## are transient. C# frontend and native Options consume this same frame batch.
## Existing gain/phase provenance remains beside RetailFrontendFlow's references.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const FRAME_BYTES: int = 128 * 128 * 3
const CLEAR := Color(31.0 / 255.0, 31.0 / 255.0, 63.0 / 255.0, 1.0)
const DARKENER := Color(0.0, 0.0, 0.0, 62.0 / 255.0)
@export_file("*.rgb") var source_path: String = "res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb"
var _frames: Array[Texture2D] = []
var _loaded_path: String = ""


func load_frames(maximum_frames: int = 2147483647) -> Dictionary:
	if maximum_frames < 0:
		return {"ok": false, "error": "FEBack maximum frame count must be nonnegative."}
	if _loaded_path != source_path:
		_frames.clear()
		_loaded_path = source_path
	if not FileAccess.file_exists(source_path):
		return {"ok": true, "frames": [], "missing": true}
	var strip: PackedByteArray = FileAccess.get_file_as_bytes(source_path)
	if strip.is_empty() or strip.size() % FRAME_BYTES != 0:
		return {"ok": false, "error": "FEBack strip length is not a positive multiple of its RGB frame size."}
	var count: int = mini(strip.size() / FRAME_BYTES, maximum_frames)
	# A byte lookup retains C#'s float product/add before double Round-to-even.
	# It avoids repeating that arithmetic for every pixel of the full strip.
	var tables: Array[PackedByteArray] = composite_tables()
	for frame_index: int in range(_frames.size(), count):
		var pixels: PackedByteArray = strip.slice(frame_index * FRAME_BYTES, (frame_index + 1) * FRAME_BYTES)
		for index: int in range(0, pixels.size(), 3):
			pixels[index] = tables[0][pixels[index]]
			pixels[index + 1] = tables[1][pixels[index + 1]]
			pixels[index + 2] = tables[2][pixels[index + 2]]
		_frames.append(ImageTexture.create_from_image(Image.create_from_data(128, 128, false, Image.FORMAT_RGB8, pixels)))
	return {"ok": true, "frames": _frames.slice(0, count), "missing": false}


static func composite_tables() -> Array[PackedByteArray]:
	var tables: Array[PackedByteArray] = []
	var fill: Array[int] = [23, 23, 48]
	var gain: Array[float] = [F.value(0.2610), F.value(0.2590), F.value(0.2420)]
	for channel: int in range(3):
		var table := PackedByteArray()
		table.resize(256)
		for value: int in range(256):
			var composed: float = F.value(fill[channel] + F.value(gain[channel] * value))
			table[value] = int(clampf(F.round_even(composed), 0.0, 255.0))
		tables.append(table)
	return tables


static func frame_index(seconds: float, count: int) -> int:
	if count <= 0:
		return 0
	var rounded: float = F.round_even(seconds * 30.0)
	# Preserve the pinned x64 checked-independent floating-to-Int64 conversion.
	var index: int = -9223372036854775808 if not is_finite(rounded) or rounded >= 9223372036854775808.0 or rounded < -9223372036854775808.0 else int(rounded)
	index -= 3
	return 0 if index <= 0 else index % count
