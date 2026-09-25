# SPDX-License-Identifier: GPL-3.0-or-later
@tool
class_name RetailAyaTextureLoader
extends RefCounted

enum Compression { DXT1, DXT2, RGBA8 }
const MAXIMUM_SOURCE_BYTES: int = 2 * 1024 * 1024
const MAXIMUM_DDS_BYTES: int = 8 * 1024 * 1024
const STREAM_BUFFER_BYTES: int = 65536
const DDS_HEADER_BYTES: int = 128
const DDSD_MIPMAPCOUNT: int = 0x20000
const DDSC2_CUBEMAP: int = 0x200
const DDSC2_VOLUME: int = 0x200000
# Managed Image.Format spellings from the pinned GodotSharp 4.8 dev6 API, in
# native enum order. Unknown cast values retain their decimal spelling.
const FORMAT_NAMES: Array[String] = ["L8", "La8", "R8", "Rg8", "Rgb8", "Rgba8", "Rgba4444", "Rgb565",
    "Rf", "Rgf", "Rgbf", "Rgbaf", "Rh", "Rgh", "Rgbh", "Rgbah", "Rgbe9995", "Dxt1", "Dxt3", "Dxt5",
    "RgtcR", "RgtcRg", "BptcRgba", "BptcRgbf", "BptcRgbfu", "Etc", "Etc2R11", "Etc2R11S",
    "Etc2Rg11", "Etc2Rg11S", "Etc2Rgb8", "Etc2Rgba8", "Etc2Rgb8A1", "Etc2RaAsRg", "Dxt5RaAsRg",
    "Astc4X4", "Astc4X4Hdr", "Astc8X8", "Astc8X8Hdr", "R16", "Rg16", "Rgb16", "Rgba16",
    "R16I", "Rg16I", "Rgb16I", "Rgba16I", "Astc6X6", "Astc6X6Hdr", "Max"]
const DECODE_ERROR_NAMES: Dictionary = {OK: "Ok", FAILED: "Failed", ERR_UNAVAILABLE: "Unavailable",
    ERR_OUT_OF_MEMORY: "OutOfMemory", ERR_FILE_UNRECOGNIZED: "FileUnrecognized", ERR_FILE_CORRUPT: "FileCorrupt",
    ERR_INVALID_DATA: "InvalidData", ERR_INVALID_PARAMETER: "InvalidParameter", ERR_PARSE_ERROR: "ParseError"}

var error_message: String = ""

func load_texture(resource_path: String, expected_width: int, expected_height: int,
        compression: Compression = Compression.DXT2, target_format: int = -1, mip_count: int = -1) -> Texture2D:
    error_message = ""
    var file: FileAccess = FileAccess.open(resource_path, FileAccess.READ)
    if file == null:
        return _fail_texture("Curated texture '%s' is missing." % resource_path)
    if file.get_length() == 0 or file.get_length() > MAXIMUM_SOURCE_BYTES:
        file.close()
        return _fail_texture("Curated texture is empty or exceeds the source limit.")
    var source: PackedByteArray = file.get_buffer(file.get_length())
    file.close()
    var image: Image = decode_image(source, expected_width, expected_height, compression, target_format, mip_count)
    return ImageTexture.create_from_image(image) if image != null else null

## Checked import boundary for the original CuratedAyaTextureLoader.Load at
## 09f0c08b. Its nullable C# arguments differ from the strict recipe API's -1
## sentinels, and its dimension check deliberately follows the Godot decode.
func load_texture_checked(resource_path: String, expected_width: int, expected_height: int,
        compression: int = Compression.DXT2, target_format: Variant = null, mip_count: Variant = null) -> Dictionary:
    error_message = ""
    if target_format != null and (typeof(target_format) != TYPE_INT or target_format < -0x80000000 or target_format > 0x7fffffff):
        return _fail_checked("Curated texture target format requires an Int32 enum value or null.")
    if mip_count != null and (typeof(mip_count) != TYPE_INT or mip_count < -0x80000000 or mip_count > 0x7fffffff):
        return _fail_checked("Curated texture mip count requires an Int32 value or null.")
    var file: FileAccess = FileAccess.open(resource_path, FileAccess.READ)
    if file == null:
        return _fail_checked("Curated texture '%s' is missing or exceeds the source limit." % resource_path)
    var source_length: int = file.get_length()
    if source_length == 0 or source_length > MAXIMUM_SOURCE_BYTES:
        file.close()
        return _fail_checked("Curated texture '%s' is missing or exceeds the source limit." % resource_path)
    var source: PackedByteArray = file.get_buffer(source_length)
    file.close()
    if source.is_empty() or source.size() > MAXIMUM_SOURCE_BYTES:
        return _fail_checked("Curated texture '%s' is missing or exceeds the source limit." % resource_path)
    var dds: PackedByteArray = inflate_aya(source)
    if not error_message.is_empty():
        return _fail_checked(error_message)
    var image: Image = _decode_dds(dds, expected_width, expected_height, compression,
        target_format, mip_count, true, resource_path)
    return _fail_checked(error_message) if image == null else {"ok": true, "value": ImageTexture.create_from_image(image)}

func decode_image(source: PackedByteArray, expected_width: int, expected_height: int,
        compression: Compression = Compression.DXT2, target_format: int = -1, mip_count: int = -1) -> Image:
    var dds: PackedByteArray = inflate_aya(source)
    if not error_message.is_empty():
        return null
    return _decode_dds(dds, expected_width, expected_height, compression,
        target_format if target_format >= 0 else null, mip_count if mip_count >= 0 else null, false, "")

func _decode_dds(dds: PackedByteArray, expected_width: int, expected_height: int, compression: int,
        target_format: Variant, mip_count: Variant, checked_import: bool, resource_path: String) -> Image:
    if dds.size() < 128 or dds.slice(0, 4) != "DDS ".to_ascii_buffer():
        return _fail_image("Curated texture is not an AYA-wrapped DDS image.")
    var expected_pixel_format: bool = false
    match compression:
        Compression.DXT1:
            expected_pixel_format = dds.slice(84, 88) == "DXT1".to_ascii_buffer()
        Compression.DXT2:
            expected_pixel_format = dds.slice(84, 88) == "DXT2".to_ascii_buffer()
        Compression.RGBA8:
            expected_pixel_format = dds.decode_u32(80) == 0x41 and dds.decode_u32(84) == 0 and \
                dds.decode_u32(88) == 32 and dds.decode_u32(92) == 0x00ff0000 and \
                dds.decode_u32(96) == 0x0000ff00 and dds.decode_u32(100) == 0x000000ff and \
                dds.decode_u32(104) == 0xff000000
    if not expected_pixel_format:
        if checked_import:
            var name: String = ["Dxt1", "Dxt2", "Rgba8"][compression] if compression >= 0 and compression <= 2 else str(compression)
            return _fail_image("Curated texture does not match the expected %s DDS pixel format." % name)
        return _fail_image("Curated texture does not match the expected DDS pixel format.")
    if mip_count != null and dds.decode_u32(28) != ((int(mip_count) & 0xffffffff) if checked_import else int(mip_count)):
        if checked_import:
            return _fail_image("Curated texture '%s' does not contain the expected %d DDS mip levels." % [resource_path, mip_count])
        return _fail_image("Curated texture does not contain the expected DDS mip levels.")
    # Existing recipe callers retain their stricter header-first allocation
    # guard. The checked C# import contract instead decodes before this check.
    if not checked_import and (expected_width <= 0 or expected_height <= 0 or dds.decode_u32(16) != expected_width or dds.decode_u32(12) != expected_height):
        return _fail_image("Curated texture does not contain the expected DDS dimensions.")
    # Godot's loader fills a short surface from uninitialized memory instead of
    # failing, so a payload shorter than its read is refused before decoding.
    var available: int = dds.size() - DDS_HEADER_BYTES
    if available < dds_payload_bytes(dds, compression, available):
        return _fail_image("Curated texture has truncated DDS pixel data.")
    var image := Image.new()
    var result: Error = image.load_dds_from_buffer(dds)
    if result != OK or image.is_empty():
        if checked_import:
            return _fail_image("Godot could not decode curated texture '%s' (%s)." % [resource_path, DECODE_ERROR_NAMES.get(result, str(result))])
        return _fail_image("Godot could not decode the curated DDS image.")
    if image.get_width() != expected_width or image.get_height() != expected_height:
        if checked_import:
            return _fail_image("Curated texture '%s' decoded as %dx%d, expected %dx%d." %
                [resource_path, image.get_width(), image.get_height(), expected_width, expected_height])
        return _fail_image("Decoded curated texture dimensions differ from their contract.")
    if target_format != null and image.get_format() != target_format:
        if image.is_compressed() and image.decompress() != OK:
            if checked_import:
                return _fail_image("Curated texture '%s' could not be decompressed for %s upload." % [resource_path, _format_name(target_format)])
            return _fail_image("Curated texture could not be decompressed for upload.")
        image.convert(int(target_format))
    if target_format != null and image.get_format() != target_format:
        if checked_import:
            return _fail_image("Curated texture '%s' could not be converted to %s." % [resource_path, _format_name(target_format)])
        return _fail_image("Curated texture could not be converted to its required format.")
    return image

static func _format_name(value: int) -> String:
    return FORMAT_NAMES[value] if value >= 0 and value < FORMAT_NAMES.size() else str(value)

## Payload bytes the pinned loader (modules/dds/texture_loader_dds.cpp at
## 8898c2b3d) reads after the header for the three admitted layouts, including
## its cubemap faces and volume slices. Results above `limit` return limit + 1.
static func dds_payload_bytes(dds: PackedByteArray, compression: int, limit: int) -> int:
    var flags: int = dds.decode_u32(8)
    var mipmaps: int = dds.decode_u32(28) if (flags & DDSD_MIPMAPCOUNT) != 0 else 1
    var caps_2: int = dds.decode_u32(112)
    var width: int = dds.decode_u32(16)
    var height: int = dds.decode_u32(12)
    var block: int = 4 if compression == Compression.RGBA8 else (8 if compression == Compression.DXT1 else 16)
    var compressed: bool = compression != Compression.RGBA8
    if (caps_2 & DDSC2_CUBEMAP) != 0:
        return mini(6 * _dds_layer_bytes(width, height, mipmaps, block, compressed, limit), limit + 1)
    if (caps_2 & DDSC2_VOLUME) == 0:
        return _dds_layer_bytes(width, height, mipmaps, block, compressed, limit)
    var depth: int = dds.decode_u32(24)
    var total: int = 0
    for _mip: int in range(mipmaps):
        if depth > limit:
            return limit + 1
        total += depth * _dds_layer_bytes(width, height, 1, block, compressed, limit)
        if total > limit:
            return limit + 1
        width = maxi(1, width >> 1)
        height = maxi(1, height >> 1)
        depth = maxi(1, depth >> 1)
    return total

static func _dds_layer_bytes(width: int, height: int, mipmaps: int, block: int, compressed: bool, limit: int) -> int:
    if width > limit or height > limit:
        return limit + 1
    var w: int = width
    var h: int = height
    var size: int = width * height * block
    if compressed:
        # The loader pads by the remainder, not to a multiple of four.
        w += w % 4
        h += h % 4
        size = maxi(1, (w + 3) >> 2) * maxi(1, (h + 3) >> 2) * block
    var level: int = 1
    while level < mipmaps and size <= limit:
        w = maxi(1, w >> 1)
        h = maxi(1, h >> 1)
        size += (maxi(1, (w + 3) >> 2) * maxi(1, (h + 3) >> 2) if compressed else w * h) * block
        level += 1
    return mini(size, limit + 1)

func inflate_aya(source: PackedByteArray) -> PackedByteArray:
    error_message = ""
    if source.is_empty() or source.size() > MAXIMUM_SOURCE_BYTES:
        return _fail_bytes("Curated texture is empty or exceeds the source limit.")
    var output := PackedByteArray()
    var position: int = 0
    while position < source.size():
        if source.size() - position < 4:
            return _fail_bytes("Curated texture has a truncated AYA record header.")
        var declared_length: int = source.decode_u32(position)
        position += 4
        if declared_length == 0 or declared_length > 0x7fffffff or declared_length > source.size() - position:
            return _fail_bytes("Curated texture has invalid AYA record framing.")
        var record: PackedByteArray = _inflate_record(source.slice(position, position + declared_length), MAXIMUM_DDS_BYTES - output.size())
        if not error_message.is_empty():
            return PackedByteArray()
        output.append_array(record)
        position += declared_length
    return output

func _inflate_record(compressed: PackedByteArray, remaining_limit: int) -> PackedByteArray:
    var stream := StreamPeerGZIP.new()
    if stream.start_decompression(true, STREAM_BUFFER_BYTES) != OK:
        return _fail_bytes("Cannot initialize the curated zlib decoder.")
    var output := PackedByteArray()
    var consumed: int = 0
    while consumed < compressed.size():
        # StreamPeerGZIP reports zlib's actual consumed byte count. Unlike a
        # convenience decompressor, this lets us refuse a valid stream followed
        # by unconsumed data inside the declared AYA record.
        var written: Array = stream.put_partial_data(compressed.slice(consumed))
        if int(written[0]) != OK:
            return _fail_bytes("Curated texture contains an invalid zlib stream.")
        consumed += int(written[1])
        var available: int = stream.get_available_bytes()
        if output.size() + available > remaining_limit:
            return _fail_bytes("Curated texture exceeds the decoded DDS limit.")
        if available > 0:
            var read: Array = stream.get_data(available)
            if int(read[0]) != OK:
                return _fail_bytes("Cannot read the decoded curated texture.")
            output.append_array(read[1])
        if int(written[1]) == 0 and available == 0:
            return _fail_bytes("Curated texture AYA record contains trailing compressed data.")
    # The public stream API does not expose Z_STREAM_END. At a completed stream
    # a probe byte is left untouched; an incomplete stream consumes it or fails.
    # Drain any output that was buffered internally, without accepting that byte.
    while true:
        var probe: Array = stream.put_partial_data(PackedByteArray([0]))
        if int(probe[0]) != OK or int(probe[1]) != 0:
            return _fail_bytes("Curated texture has a truncated zlib stream.")
        var available: int = stream.get_available_bytes()
        if output.size() + available > remaining_limit:
            return _fail_bytes("Curated texture exceeds the decoded DDS limit.")
        if available == 0:
            break
        var read: Array = stream.get_data(available)
        if int(read[0]) != OK:
            return _fail_bytes("Cannot read the decoded curated texture.")
        output.append_array(read[1])
    stream.clear()
    return output

func _fail_bytes(message: String) -> PackedByteArray:
    error_message = message
    return PackedByteArray()

func _fail_image(message: String) -> Image:
    error_message = message
    return null

func _fail_texture(message: String) -> Texture2D:
    error_message = message
    return null

func _fail_checked(message: String) -> Dictionary:
    error_message = message
    return {"ok": false, "error_type": "InvalidDataException", "error": message}
