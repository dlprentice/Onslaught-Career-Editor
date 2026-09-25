# SPDX-License-Identifier: MIT
@tool
extends RefCounted
## Single-precision cosine compatibility for the pinned Linux x86-64 FMA path.
## The range reduction, polynomial and coefficients are adapted from Arm's
## optimized-routines, commit 56e3bf05c19c4e28e1f5edd9093c712f16c5c32a (v23.01):
## https://github.com/ARM-software/optimized-routines/blob/56e3bf05c19c4e28e1f5edd9093c712f16c5c32a/math/cosf.c
## https://github.com/ARM-software/optimized-routines/blob/56e3bf05c19c4e28e1f5edd9093c712f16c5c32a/math/sincosf.h
## https://github.com/ARM-software/optimized-routines/blob/56e3bf05c19c4e28e1f5edd9093c712f16c5c32a/math/sincosf_data.c
## Upstream offers MIT OR Apache-2.0 WITH LLVM-exception; this adaptation uses MIT.
## cosf.c/sincosf.h: Copyright (c) 2018-2021, Arm Limited.
## sincosf_data.c: Copyright (c) 2018-2019, Arm Limited.
## Upstream MIT license, preserved verbatim:
## Copyright (c) 1999-2022, Arm Limited.
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##
## Changes: typed GDScript/raw-word interface, explicit unsigned wrap, and exact
## integer product/sum rounding for the fused double operations observed in the
## installed glibc 2.44 __cosf_fma. The integer FMA implementation below is original
## code; it imports no GPL helper, native library or fitted-output lookup table.
## This matches the retained host expression, not a newly claimed retail law or
## universally correctly-rounded cosine. No rounding-mode/errno state is owned.
## Editor-safe pure functions: no scene, input, filesystem or clock owner.

const INV_PIO4: Array[int] = [
	0xa2, 0xa2f9, 0xa2f983, 0xa2f9836e, 0xf9836e4e, 0x836e4e44,
	0x6e4e4415, 0x4e441529, 0x441529fc, 0x1529fc27, 0x29fc2757, 0xfc2757d1,
	0x2757d1f5, 0x57d1f534, 0xd1f534dd, 0xf534ddc0, 0x34ddc0db, 0xddc0db62,
	0xc0db6295, 0xdb629599, 0x6295993c, 0x95993c43, 0x993c4390, 0x3c439041]
const SIGNS: Array[float] = [1.0, -1.0, -1.0, 1.0]
const LIMB_BITS: int = 26
const LIMB_MASK: int = (1 << LIMB_BITS) - 1
const FRACTION_MASK: int = 0x000fffffffffffff
const SIGN64: int = -9223372036854775807 - 1
static var _hpi_inv: float = _double(0x41645f306dc9c883)
static var _hpi: float = _double(0x3ff921fb54442d18)
static var _pi63: float = _double(0x3c1921fb54442d18)
static var _c1: float = -_double(0x3fdffffffd0c621c)
static var _c2: float = _double(0x3fa55553e1068f19)
static var _c3: float = -_double(0x3f56c087e89a359d)
static var _c4: float = _double(0x3ef99343027bf8c3)
static var _s1: float = -_double(0x3fc555545995a603)
static var _s2: float = _double(0x3f81107605230bc4)
static var _s3: float = -_double(0x3f2994eb3774cf24)


static func cos_bits(word: Variant) -> Dictionary:
	if typeof(word) != TYPE_INT or word < -0x80000000 or word > 0x7fffffff:
		return {"ok": false, "error_type": "ArgumentException", "error": "Cosine requires a signed Int32 binary32 word."}
	var raw: int = word & 0xffffffff
	var magnitude: int = raw & 0x7fffffff
	if magnitude >= 0x7f800000:
		# __math_invalidf preserves/quietens NaN payloads; either infinity
		# produces the x86 invalid-operation negative canonical quiet NaN.
		return {"ok": true, "bits": _signed32(0xffc00000 if magnitude == 0x7f800000 else raw | 0x00400000)}
	var top: int = magnitude >> 20
	if top < 0x398: return {"ok": true, "bits": 0x3f800000}
	var x: float = _single(word)
	if top < 0x3f4:
		return {"ok": true, "bits": _word32(_polynomial(x, x * x, 1.0, 1))}
	var quadrant: int
	var table_sign: float
	var sine_sign: float
	if top < 0x42f:
		var scaled: float = x * _hpi_inv
		quadrant = (int(scaled) + 0x800000) >> 24
		x = _fma(-float(quadrant), _hpi, x)
		sine_sign = SIGNS[quadrant & 3]
		table_sign = -1.0 if (quadrant & 2) != 0 else 1.0
	else:
		var reduced: Dictionary = _reduce_large(raw)
		x = reduced.value
		quadrant = reduced.quadrant
		var signed_quadrant: int = quadrant + (raw >> 31)
		sine_sign = SIGNS[signed_quadrant & 3]
		table_sign = -1.0 if (signed_quadrant & 2) != 0 else 1.0
	return {"ok": true, "bits": _word32(_polynomial(x * sine_sign, x * x, table_sign, quadrant ^ 1))}


static func cosine(number: float) -> Dictionary:
	var result: Dictionary = cos_bits(_word32(number))
	if result.ok: result.value = _single(result.bits)
	return result


static func _polynomial(x: float, x2: float, sign: float, quadrant: int) -> float:
	if (quadrant & 1) == 0:
		var x3: float = x * x2
		var s1: float = _fma(x2, _s3, _s2)
		var x7: float = x3 * x2
		var s: float = _fma(x3, _s1, x)
		return _fma(x7, s1, s)
	var x4: float = x2 * x2
	var c2: float = _fma(x2, _c4 * sign, _c3 * sign)
	var c1: float = _fma(x2, _c1 * sign, sign)
	var x6: float = x4 * x2
	var c: float = _fma(x4, _c2 * sign, c1)
	return _fma(x6, c2, c)


static func _reduce_large(raw: int) -> Dictionary:
	var table: int = (raw >> 26) & 15
	var shift: int = (raw >> 23) & 7
	var significand: int = ((raw & 0xffffff) | 0x800000) << shift
	var low: int = significand * INV_PIO4[table]
	var middle: int = significand * INV_PIO4[table + 4]
	var high: int = significand * INV_PIO4[table + 8]
	# Each product fits signed64; the subsequent shifts/addition deliberately
	# wrap at 64 bits, matching the upstream unsigned 2.62 representation.
	var remainder: int = (high >> 32) | (low << 32)
	remainder += middle
	var quadrant: int = ((remainder + (1 << 61)) >> 62) & 3
	remainder -= quadrant << 62
	return {"value": float(remainder) * _pi63, "quadrant": quadrant}


## Internal finite binary64 FMA used only by the cosine reduction/polynomial.
## The exact integers are aligned, added/subtracted, and rounded once, ties
## to even. This avoids double rounding from a compensated floating residual.
## Its test seam compares directly against Math.FusedMultiplyAdd raw words.
static func _fma(a: float, b: float, c: float) -> float:
	if a == 0.0 or b == 0.0: return a * b + c
	if c == 0.0: return a * b
	var aa: Dictionary = _parts(a)
	var bb: Dictionary = _parts(b)
	var cc: Dictionary = _parts(c)
	var exponent: int = mini(aa.exponent + bb.exponent, cc.exponent)
	var product: Array[int] = _shift(_multiply(_limbs(aa.mantissa), _limbs(bb.mantissa)), aa.exponent + bb.exponent - exponent)
	var addend: Array[int] = _shift(_limbs(cc.mantissa), cc.exponent - exponent)
	var negative: bool = aa.negative != bb.negative
	var magnitude: Array[int]
	if negative == cc.negative:
		magnitude = _add(product, addend)
	else:
		var compare: int = _compare(product, addend)
		if compare == 0: return 0.0
		magnitude = _subtract(product, addend) if compare > 0 else _subtract(addend, product)
		if compare < 0: negative = cc.negative
	return _rounded_double(magnitude, exponent, negative)


static func _parts(number: float) -> Dictionary:
	var bits: int = PackedFloat64Array([number]).to_byte_array().decode_s64(0)
	var exponent: int = (bits >> 52) & 0x7ff
	return {"negative": bits < 0, "mantissa": (bits & FRACTION_MASK) | ((1 << 52) if exponent != 0 else 0),
		"exponent": exponent - 1075 if exponent != 0 else -1074}


static func _limbs(value: int) -> Array[int]:
	var result: Array[int] = []
	while value != 0:
		result.append(value & LIMB_MASK)
		value >>= LIMB_BITS
	return result


static func _multiply(a: Array[int], b: Array[int]) -> Array[int]:
	var result: Array[int] = []
	result.resize(a.size() + b.size())
	result.fill(0)
	for i: int in range(a.size()):
		var carry: int = 0
		for j: int in range(b.size()):
			var value: int = a[i] * b[j] + result[i + j] + carry
			result[i + j] = value & LIMB_MASK
			carry = value >> LIMB_BITS
		result[i + b.size()] = carry
	return _trim(result)


@warning_ignore("integer_division")
static func _shift(value: Array[int], bits: int) -> Array[int]:
	var result: Array[int] = []
	result.resize(bits / LIMB_BITS)
	result.fill(0)
	var carry: int = 0
	for digit: int in value:
		var combined: int = (digit << (bits % LIMB_BITS)) | carry
		result.append(combined & LIMB_MASK)
		carry = combined >> LIMB_BITS
	if carry != 0: result.append(carry)
	return result


static func _add(a: Array[int], b: Array[int]) -> Array[int]:
	var result: Array[int] = []
	var carry: int = 0
	for i: int in range(maxi(a.size(), b.size())):
		var value: int = (a[i] if i < a.size() else 0) + (b[i] if i < b.size() else 0) + carry
		result.append(value & LIMB_MASK)
		carry = value >> LIMB_BITS
	if carry != 0: result.append(carry)
	return result


static func _subtract(a: Array[int], b: Array[int]) -> Array[int]:
	var result: Array[int] = []
	var borrow: int = 0
	for i: int in range(a.size()):
		var value: int = a[i] - (b[i] if i < b.size() else 0) - borrow
		borrow = 1 if value < 0 else 0
		result.append(value & LIMB_MASK)
	return _trim(result)


static func _compare(a: Array[int], b: Array[int]) -> int:
	if a.size() != b.size(): return 1 if a.size() > b.size() else -1
	for i: int in range(a.size() - 1, -1, -1):
		if a[i] != b[i]: return 1 if a[i] > b[i] else -1
	return 0


static func _trim(value: Array[int]) -> Array[int]:
	while not value.is_empty() and value[-1] == 0: value.pop_back()
	return value


static func _bit_length(value: Array[int]) -> int:
	if value.is_empty(): return 0
	var high: int = value[-1]
	var result: int = (value.size() - 1) * LIMB_BITS
	while high != 0:
		high >>= 1
		result += 1
	return result


@warning_ignore("integer_division")
static func _bit(value: Array[int], index: int) -> int:
	return (value[index / LIMB_BITS] >> (index % LIMB_BITS)) & 1 if index >= 0 and index < value.size() * LIMB_BITS else 0


static func _round_integer(value: Array[int], shift: int) -> int:
	var result: int = 0
	for i: int in range(_bit_length(value) - 1, maxi(shift, 0) - 1, -1): result = (result << 1) | _bit(value, i)
	if shift <= 0: return result << -shift
	if _bit(value, shift - 1) == 0: return result
	var sticky: bool = false
	for i: int in range(shift - 1):
		if _bit(value, i) != 0: sticky = true; break
	return result + (1 if sticky or (result & 1) != 0 else 0)


static func _rounded_double(value: Array[int], scale: int, negative: bool) -> float:
	var length: int = _bit_length(value)
	var exponent: int = scale + length - 1
	var sign_word: int = SIGN64 if negative else 0
	if exponent < -1022:
		return _double(sign_word | _round_integer(value, -1074 - scale))
	var mantissa: int = _round_integer(value, length - 53)
	if mantissa == (1 << 53):
		mantissa >>= 1
		exponent += 1
	if exponent > 1023: return _double(sign_word | 0x7ff0000000000000)
	return _double(sign_word | ((exponent + 1023) << 52) | (mantissa & FRACTION_MASK))


static func _double(word: int) -> float:
	return PackedInt64Array([word]).to_byte_array().decode_double(0)


static func _single(word: int) -> float:
	return PackedInt32Array([word]).to_byte_array().decode_float(0)


static func _word32(value: float) -> int:
	return PackedFloat32Array([value]).to_byte_array().decode_s32(0)


static func _signed32(word: int) -> int:
	return word - 0x100000000 if (word & 0x80000000) != 0 else word
