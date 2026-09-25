# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Runs the production GDScript kernels against the existing C# and native
## fixtures exported by TestSupport/GdscriptParityOracle.cs. No asset inputs.

const Float24 = preload("res://Core/retail_float24.gd")
const Euler = preload("res://Core/retail_unit_euler.gd")
const RandomStream = preload("res://Core/released_random.gd")
const Wide = preload("res://Core/wide_integer.gd")
const Writer = preload("res://Core/canonical_binary_writer.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[category] = int(counts.get(category, 0)) + 1
	if actual != expected:
		failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func ints(values: Array) -> Array[int]:
	var result: Array[int] = []
	for value: Variant in values:
		result.append(int(value))
	return result


func words(values: Array) -> PackedInt64Array:
	return PackedInt64Array(ints(values))


func double_hex(value: float) -> String:
	var bytes := PackedByteArray()
	bytes.resize(8)
	bytes.encode_double(0, value)
	return bytes.hex_encode()


func check_arithmetic(rows: Array) -> void:
	for index: int in range(rows.size()):
		var row: Dictionary = rows[index]
		var a: float = str(row.operands[0]).hex_decode().decode_double(0)
		var b: float = str(row.operands[1]).hex_decode().decode_double(0) if row.operands.size() > 1 else 0.0
		var result: Float24.Result
		match row.operation:
			"Round": result = Float24.try_round(a)
			"Add": result = Float24.try_add(a, b)
			"Subtract": result = Float24.try_subtract(a, b)
			"Multiply": result = Float24.try_multiply(a, b)
			"Divide": result = Float24.try_divide(a, b)
			"Sqrt": result = Float24.try_sqrt(a)
		check("arithmetic_admission", str(index), not result.ok, row.error)
		if result.ok and not row.error:
			check("arithmetic_bits", str(index), double_hex(result.value), row.result)
	check("arithmetic_admission", "finite_over_infinity", double_hex(Float24.try_divide(1.0, -INF).value), "0000000000000080")
	check("arithmetic_admission", "bad_float_store", Float24.try_store_float32(1e100).ok, false)
	check("arithmetic_admission", "nonfinite_float_store", Float24.try_store_float32(NAN).ok, false)
	completed.append("arithmetic")


func check_euler(vectors: Dictionary) -> void:
	for category: String in ["eulers", "nativeBasis"]:
		for index: int in range(vectors[category].size()):
			var row: Dictionary = vectors[category][index]
			var result: Euler.Result = Euler.build_basis(words(row.words))
			check(category, str(index) + ":admitted", result.ok, true)
			check(category, str(index), result.words, words(row.expected))
			if category == "nativeBasis":
				var signed_words := PackedInt64Array()
				for value: int in words(row.words):
					signed_words.append(value - 0x100000000 if value >= 0x80000000 else value)
				check("signed_word_aliases", str(index), Euler.build_basis(signed_words).words, result.words)
	for category: String in ["smooth", "nativeSmooth"]:
		for index: int in range(vectors[category].size()):
			var row: Dictionary = vectors[category][index]
			var result: Euler.Result = Euler.smooth(words(row.current), words(row.desired), words(row.rate), float(row.multiplier))
			check(category, str(index) + ":admitted", result.ok, true)
			check(category, str(index), result.words, words(row.expected))
	var zero := PackedInt64Array([0, 0, 0])
	var negative_zero := PackedInt64Array([0x80000000, 0x80000000, 0x80000000])
	var one := PackedInt64Array([0x3f800000, 0x3f800000, 0x3f800000])
	var invalid_rate := PackedInt64Array([0x7fc00001, 0xbf800000, 0x7f800000])
	check("euler_admission", "equal_skips_invalid_rate", Euler.smooth(negative_zero, zero, invalid_rate, 1.0).words, negative_zero)
	check("euler_admission", "active_invalid_rate", Euler.smooth(zero, one, invalid_rate, 1.0).ok, false)
	check("euler_admission", "active_negative_rate", Euler.smooth(zero, one, PackedInt64Array([0xbf800000, 0, 0]), 1.0).ok, false)
	check("euler_admission", "missing_axis", Euler.build_basis(PackedInt64Array([0, 0])).ok, false)
	check("euler_admission", "nonfinite_angle", Euler.build_basis(invalid_rate).ok, false)
	for multiplier: float in [0.0, -1.0, INF, NAN, 1e-100, 1e100]:
		check("euler_admission", "multiplier:" + str(multiplier), Euler.smooth(zero, one, one, multiplier).ok, false)
	var maximum := PackedInt64Array([0x7f7fffff, 0x7f7fffff, 0x7f7fffff])
	check("euler_admission", "output_float_overflow", Euler.smooth(zero, maximum, maximum, Float24.read_word(0x7f7fffff)).ok, false)
	# A cap can overflow while a much smaller computed step remains admitted.
	check("euler_admission", "unused_infinite_cap", Euler.smooth(zero, one, maximum, 2.0).ok, true)
	completed.append("euler")


func check_rng(vectors: Dictionary) -> void:
	for row: Dictionary in vectors.rng:
		var stream = RandomStream.new()
		check("rng_admission", "restore", stream.restore_seed(int(row.seed)).ok, true)
		for index: int in range(row.values.size()):
			var value: int = stream.next()
			check("rng", str(row.seed) + ":" + str(index), [value, stream.get_seed()], [int(row.values[index].value), int(row.values[index].seed)])
	for row: Dictionary in vectors.scaledRng:
		var stream = RandomStream.new()
		stream.restore_seed(int(row.seed))
		var result: Dictionary = stream.next_signed_unit_scaled(int(row.scale))
		check("rng_scaled", str(row.seed) + ":" + str(row.scale), result.ok, not row.error)
		check("rng_scaled", "seed_after", stream.get_seed(), int(row.seedAfter))
		if result.ok and not row.error:
			check("rng_scaled", "value", result.value, int(row.value))
	var stream = RandomStream.new()
	for invalid: Variant in [null, 1.5, "1", 2147483648, -2147483649]:
		check("rng_admission", "invalid_restore", stream.restore_seed(invalid).ok, false)
		check("rng_admission", "invalid_scale", stream.next_signed_unit_scaled(invalid).ok, false)
		check("rng_admission", "invalid_does_not_draw", stream.get_seed(), 123456)
	for invalid: String in ["", "-", "+1", " 1", "1.0", "2147483648", "-2147483649", "999999999999999999999999999999999"]:
		check("rng_admission", "invalid_text", stream.restore_seed_decimal(invalid).ok, false)
		check("rng_admission", "invalid_text_keeps_seed", stream.get_seed(), 123456)
	check("rng_admission", "minimum_seed", stream.restore_seed_decimal("-2147483648").ok, true)
	check("rng_admission", "minimum_seed_exact", stream.get_seed(), -2147483648)
	completed.append("rng")


func check_wide(vectors: Dictionary) -> void:
	for index: int in range(vectors.wide.size()):
		var row: Dictionary = vectors.wide[index]
		var a: Array = Wide.from_decimal(row.left).value
		var b: Array = Wide.from_decimal(row.right).value
		check("wide_parse", str(index) + ":a", a, ints(row.a))
		check("wide_parse", str(index) + ":b", b, ints(row.b))
		check("wide_compare", str(index), Wide.compare(a, b).value, int(row.compare))
		check("wide_add", str(index), Wide.add(a, b).value, ints(row.sum))
		check("wide_multiply", str(index), Wide.multiply(a, b).value, ints(row.product))
		var difference: Dictionary = Wide.subtract(a, b)
		check("wide_subtract", str(index) + ":admission", difference.ok, int(row.compare) >= 0)
		if difference.ok:
			check("wide_subtract", str(index), difference.value, ints(row.difference))
		var divided: Dictionary = Wide.divmod(a, b)
		check("wide_divide", str(index) + ":admission", divided.ok, row.right != "0")
		if divided.ok:
			check("wide_divide", str(index) + ":quotient", divided.quotient, ints(row.quotient))
			check("wide_divide", str(index) + ":remainder", divided.remainder, ints(row.remainder))
		check("wide_no_mutation", str(index), [a, b], [ints(row.a), ints(row.b)])
	for index: int in range(vectors.big.size()):
		var row: Dictionary = vectors.big[index]
		var a: Array = Wide.from_decimal(row.a).value
		var numerator: Array = Wide.multiply(Wide.multiply(a, a).value, Wide.from_int64(1000000).value).value
		var denominator: Array = Wide.multiply(Wide.from_decimal(row.normal2).value, Wide.from_decimal(row.velocity2).value).value
		check("contact_ratio", str(index) + ":product", numerator, ints(row.product))
		check("contact_ratio", str(index), Wide.divide_round_nearest_to_int64(numerator, denominator).value, int(row.result))
	for invalid: Variant in [[], [0, 0], [-1], [32768], [1.5], null, "1"]:
		check("wide_admission", "invalid_limbs", Wide.add(invalid, [0]).ok, false)
	for invalid: Variant in ["", "-1", "+1", "1.0", " 1", null, 1]:
		check("wide_admission", "invalid_decimal", Wide.from_decimal(invalid).ok, false)
	check("wide_admission", "int64_max", Wide.to_int64(Wide.from_decimal("9223372036854775807").value).value, 9223372036854775807)
	check("wide_admission", "int64_overflow", Wide.to_int64(Wide.from_decimal("9223372036854775808").value).ok, false)
	check("wide_admission", "rounded_overflow", Wide.divide_round_nearest_to_int64(Wide.from_decimal("18446744073709551615").value, [2]).ok, false)
	check("wide_admission", "rounding_half", Wide.divide_round_nearest_to_int64([1], [2]).value, 1)
	completed.append("wide")


func check_binary(row: Dictionary) -> void:
	var writer = Writer.new()
	writer.write_bool(true)
	writer.write_bool(false)
	writer.write_i32(-2147483648)
	writer.write_u32(0xffffffff)
	writer.write_i64(-9223372036854775807 - 1)
	writer.write_u64_words(0xfffffffb, 0xffffffff)
	writer.write_float32(Float24.read_word(0x80000000))
	writer.write_float64(1.25)
	writer.write_string(row.label)
	var result: Dictionary = writer.finish()
	check("binary", "admitted", result.ok, true)
	var bytes: PackedByteArray = result.bytes
	check("binary", "exact_bytes", bytes.hex_encode(), row.hex)
	var hasher := HashingContext.new()
	check("binary", "hash_init", hasher.start(HashingContext.HASH_SHA256), OK)
	check("binary", "hash_update", hasher.update(bytes), OK)
	check("binary", "exact_sha256", hasher.finish().hex_encode(), row.sha256)
	bytes[0] = 255
	check("binary", "snapshot_isolation", writer.finish().bytes.hex_encode(), row.hex)
	for method: String in ["write_u8", "write_u32", "write_i32"]:
		var refused = Writer.new()
		refused.write_bool(true)
		check("binary_admission", method, refused.call(method, 0x100000000), false)
		check("binary_admission", method + ":terminal", refused.write_bool(false), false)
		check("binary_admission", method + ":no_partial", refused.finish().has("bytes"), false)
	for method: String in ["write_u8", "write_u32", "write_i32", "write_i64", "write_u64_words"]:
		for invalid: Variant in [1.5, 1.0, "1", null, true]:
			var refused = Writer.new()
			var accepted: bool = refused.call(method, invalid, 0) if method == "write_u64_words" else refused.call(method, invalid)
			check("binary_admission", method + ":no_coercion", accepted, false)
			check("binary_admission", method + ":terminal", refused.write_bool(true), false)
			check("binary_admission", method + ":no_partial", refused.finish().has("bytes"), false)
	var refused = Writer.new()
	check("binary_admission", "high_word_no_coercion", refused.write_u64_words(0, 1.5), false)
	completed.append("binary")


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("Expected fixture path and owned result path.")
		quit(2)
		return
	var vectors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	check("fixture_admission", "schema", int(vectors.get("schema", 0)), 1)
	for category: String in ["arithmetic", "eulers", "nativeBasis", "smooth", "nativeSmooth", "rng", "scaledRng", "wide", "big"]:
		check("fixture_admission", category, vectors.has(category) and not vectors.get(category, []).is_empty(), true)
	if failures.is_empty():
		check_arithmetic(vectors.arithmetic)
		check_euler(vectors)
		check_rng(vectors)
		check_wide(vectors)
		check_binary(vectors.binary)
	var report: Dictionary = {"schema": 1, "engine": Engine.get_version_info().string,
		"failure_count": failures.size(), "counts": counts, "failures": failures, "completed": completed,
		"scope": "Production GDScript numerical modules; bounded C# comparison and existing native fixtures. No full simulation or cross-host parity claim."}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		push_error("Cannot write numerical check result.")
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
