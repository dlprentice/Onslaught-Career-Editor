# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends RefCounted
## Production HUD textures, fonts and released portrait/noise masks.
## Recipes are public; decoded private images never enter a stored property.
## FirstFlightHud.cs (pre-port) is the behavior reference. Mask evidence:
## local-lab/PORTRAIT-BATTLELINE-FIELD-2026-07-26.md, sections 1–2.
const Aya = preload("res://Scenes/Shared/retail_aya_texture.gd")
const BitmapFont = preload("res://Scenes/Shared/retail_bitmap_font.gd")
const F32 = preload("res://Scenes/Shared/retail_float32.gd")
const MESSAGE_NOISE_PHASE_COUNT: int = 16
const RECIPES: Dictionary = {
	"bar-line": [16, 64, 0],
	"battleline-marker": [16, 16, 1],
	"battleline-outline": [128, 128, 0],
	"circle-darkener": [128, 128, 1],
	"circle-mask": [128, 128, 1],
	"compass-objective-marker": [16, 16, 1],
	"crosshair-dot": [64, 64, 1],
	"crosshair-enemy": [64, 64, 1],
	"crosshair-friend": [64, 64, 1],
	"crosshair-outline": [64, 64, 1],
	"crosshair-predictor": [64, 64, 1],
	"crosshair-primary": [64, 64, 1],
	"crosshair-secondary": [128, 128, 1],
	"damage-flash": [128, 32, 0],
	"font-13ps": [256, 256, 2],
	"font-22": [512, 512, 2],
	"forseti-icon": [64, 64, 1],
	"guns-darken": [128, 128, 1],
	"guns-front": [128, 128, 0],
	"guns-outline": [128, 128, 0],
	"guns-side": [128, 128, 0],
	"guns-top": [128, 128, 0],
	"kramer-portrait": [128, 128, 1],
	"kramer-portrait-ee": [128, 128, 1],
	"kramer-portrait-mm": [128, 128, 1],
	"kramer-portrait-oo": [128, 128, 1],
	"message-noise": [128, 128, 0],
	"objective-inner-centre": [64, 128, 1],
	"objective-inner-left": [64, 128, 1],
	"objective-inner-right": [64, 128, 1],
	"objective-left": [128, 128, 1],
	"objective-right": [128, 128, 1],
	"offscreen-arrow": [32, 32, 1],
	"radar-outline": [128, 128, 0],
	"radio-north": [32, 32, 1],
	"radio-view": [128, 128, 1],
	"scanner-blob-large": [16, 16, 1],
	"scanner-blob-medium": [16, 16, 1],
	"scanner-blob-repair-pad": [16, 16, 1],
	"scanner-blob-small": [16, 16, 1],
	"screen-marker": [64, 64, 0],
	"target-sighted": [64, 64, 1],
	"tatiana-portrait": [128, 128, 1],
	"tatiana-portrait-ee": [128, 128, 1],
	"tatiana-portrait-mm": [128, 128, 1],
	"tatiana-portrait-oo": [128, 128, 1],
	"technician-portrait": [128, 128, 1],
	"technician-portrait-ee": [128, 128, 1],
	"technician-portrait-mm": [128, 128, 1],
	"technician-portrait-oo": [128, 128, 1],
	"threat-flash": [32, 32, 0],
	"weapon-fill": [128, 128, 1],
	"weapon-outline": [128, 128, 0],
	"weapon-plasma-cannon": [64, 64, 1],
	"weapon-vulcan-cannon": [64, 64, 1],
}
var pages: Dictionary = {}
var portraits: Array = []
var noise_phases: Array[Texture2D] = []
var dial: PackedByteArray
var small_font: BitmapFont
var large_font: BitmapFont
var small_widths: PackedInt32Array
var large_widths: PackedInt32Array
var ready: bool = false

func initialize() -> Dictionary:
	if ready:
		return {"ok": true}
	# Build into temporary owners so a failed read cannot publish partial state.
	var loaded: Dictionary = {}
	var loader := Aya.new()
	for name: String in RECIPES:
		var recipe: Array = RECIPES[name]
		var texture: Texture2D = loader.load_texture("res://Assets/Hud/%s.texture.aya" % name,
			int(recipe[0]), int(recipe[1]), int(recipe[2]))
		if texture == null:
			return {"ok": false, "error": loader.error_message}
		loaded[name] = texture
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes("res://Assets/Hud/dial.raw")
	if bytes.size() != 8192:
		return {"ok": false, "error": "Released HUD dial.raw must contain 8192 bytes."}
	for name: String in ["font-13ps", "font-22"]:
		var image: Image = _readable(loaded[name])
		if image == null:
			return {"ok": false, "error": "HUD font cannot be decompressed."}
		# Retail alphatest >= 8/255 after modulation. BitmapFont CPU widths use the
		# exact full-alpha pre-cut; the layer shader remains the final gate.
		for y: int in range(image.get_height()):
			for x: int in range(image.get_width()):
				var pixel: Color = image.get_pixel(x, y)
				if pixel.a > 0.0 and pixel.a < F32.value(8.0 / 255.0):
					pixel.a = 0.0
					image.set_pixel(x, y, pixel)
		loaded[name] = ImageTexture.create_from_image(image)
	var mask: Image = _readable(loaded["circle-mask"])
	var noise: Image = _readable(loaded["message-noise"])
	if mask == null or noise == null:
		return {"ok": false, "error": "HUD circle/noise cannot be decompressed."}
	var masked_portraits: Array = []
	for speaker: String in ["tatiana", "technician", "kramer"]:
		var poses: Array[Texture2D] = []
		for suffix: String in ["-oo", "-ee", "-mm", ""]:
			var portrait: Image = _readable(loaded[speaker + "-portrait" + suffix])
			if portrait == null:
				return {"ok": false, "error": "HUD portrait cannot be decompressed."}
			portrait.resize(96, 96, Image.INTERPOLATE_BILINEAR)
			var result: Image = Image.create_empty(128, 128, false, Image.FORMAT_RGBA8)
			for y: int in range(128):
				for x: int in range(128):
					var pixel: Color = portrait.get_pixel(x - 16, y - 16) if x >= 16 and x < 112 and y >= 16 and y < 112 else Color(0, 0, 0, 0)
					pixel.a = F32.value(pixel.a * F32.value(1.0 - mask.get_pixel(x, y).a))
					result.set_pixel(x, y, pixel)
			poses.append(ImageTexture.create_from_image(result))
		masked_portraits.append(poses)
	var phases: Array[Texture2D] = []
	for phase: int in range(MESSAGE_NOISE_PHASE_COUNT):
		var rolled: Image = Image.create_empty(128, 128, false, Image.FORMAT_RGBA8)
		var shift_x: int = phase * 8
		var shift_y: int = ((phase * 5) % MESSAGE_NOISE_PHASE_COUNT) * 8
		for y: int in range(128):
			for x: int in range(128):
				var pixel: Color = noise.get_pixel((x + shift_x) % 128, (y + shift_y) % 128)
				pixel.a = F32.value(1.0 - mask.get_pixel(x, y).a)
				rolled.set_pixel(x, y, pixel)
		phases.append(ImageTexture.create_from_image(rolled))
	pages = loaded
	portraits = masked_portraits
	noise_phases = phases
	dial = bytes
	small_font = BitmapFont.new(pages["font-13ps"], 16)
	large_font = BitmapFont.new(pages["font-22"], 32)
	# Shared atlas measurement, with the HUD's released small-space exception.
	small_widths = small_font._widths.duplicate()
	small_widths[0] = 7
	large_widths = large_font._widths.duplicate()
	ready = true
	return {"ok": true}

static func _readable(texture: Texture2D) -> Image:
	var image: Image = texture.get_image()
	if image.is_compressed() and image.decompress() != OK:
		return null
	if image.get_format() != Image.FORMAT_RGBA8:
		image.convert(Image.FORMAT_RGBA8)
	return image
