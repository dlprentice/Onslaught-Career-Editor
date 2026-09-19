# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Existing deterministic look curve and released analogue normalization.
## LookAxisResponse.cs retains the 1,001 exact permille samples derived from
## references/Onslaught/Player.cpp:334-355. No runtime tan or interpolation.
## RetailAnalogueControls.cs owns the measured PCController/DoMappings evidence:
## signed axes multiply the stored 0x3a83126f reciprocal, never divide by 1000;
## right Y recenters by 32768 and scales by exactly 2^-15. This preserves the
## existing PC53-then-float contract; the separately documented PC64 tie question
## remains open. No unproven 0.36 dead zone or physical device mapping is added.

const Float32 = preload("res://Core/retail_float24.gd")
const AXIS_SCALE_BITS: int = 0x3a83126f
const RIGHT_Y_CENTRE_BITS: int = 0x47000000
const RIGHT_Y_SCALE_BITS: int = 0x38000000
const DIGITAL_THRESHOLD_BITS: int = 0x3f666666
const INITIAL_REPEAT_DELAY_BITS: int = 0x3f000000
const REPEAT_DELAY_BITS: int = 0x3df5c28f
const ABSENT_PAD_AXIS_BITS: int = 0
const LOOK_CURVE: Array[int] = [
	0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 9,
	9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18,
	19, 19, 20, 20, 21, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28,
	28, 29, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34, 35, 35, 36, 36, 36, 37,
	37, 38, 38, 39, 39, 40, 40, 41, 41, 42, 42, 43, 43, 44, 44, 45, 45, 45, 46, 46,
	47, 47, 48, 48, 49, 49, 50, 50, 51, 51, 52, 52, 53, 53, 54, 54, 54, 55, 55, 56,
	56, 57, 57, 58, 58, 59, 59, 60, 60, 61, 61, 62, 62, 63, 63, 64, 64, 64, 65, 65,
	66, 66, 67, 67, 68, 68, 69, 69, 70, 70, 71, 71, 72, 72, 73, 73, 74, 74, 75, 75,
	76, 76, 77, 77, 78, 78, 78, 79, 79, 80, 80, 81, 81, 82, 82, 83, 83, 84, 84, 85,
	85, 86, 86, 87, 87, 88, 88, 89, 89, 90, 90, 91, 91, 92, 92, 93, 93, 94, 94, 95,
	95, 96, 96, 97, 97, 98, 98, 99, 99, 100, 100, 101, 101, 102, 102, 103, 103, 104, 104, 105,
	105, 106, 106, 107, 107, 108, 108, 109, 109, 110, 110, 111, 111, 112, 112, 113, 113, 114, 114, 115,
	115, 116, 116, 117, 117, 118, 118, 119, 119, 120, 120, 121, 121, 122, 122, 123, 123, 124, 124, 125,
	125, 126, 126, 127, 127, 128, 128, 129, 130, 130, 131, 131, 132, 132, 133, 133, 134, 134, 135, 135,
	136, 136, 137, 137, 138, 138, 139, 139, 140, 141, 141, 142, 142, 143, 143, 144, 144, 145, 145, 146,
	146, 147, 147, 148, 148, 149, 150, 150, 151, 151, 152, 152, 153, 153, 154, 154, 155, 155, 156, 157,
	157, 158, 158, 159, 159, 160, 160, 161, 161, 162, 163, 163, 164, 164, 165, 165, 166, 166, 167, 167,
	168, 169, 169, 170, 170, 171, 171, 172, 173, 173, 174, 174, 175, 175, 176, 176, 177, 178, 178, 179,
	179, 180, 180, 181, 182, 182, 183, 183, 184, 184, 185, 186, 186, 187, 187, 188, 188, 189, 190, 190,
	191, 191, 192, 192, 193, 194, 194, 195, 195, 196, 197, 197, 198, 198, 199, 199, 200, 201, 201, 202,
	202, 203, 204, 204, 205, 205, 206, 207, 207, 208, 208, 209, 210, 210, 211, 211, 212, 213, 213, 214,
	214, 215, 216, 216, 217, 217, 218, 219, 219, 220, 221, 221, 222, 222, 223, 224, 224, 225, 226, 226,
	227, 227, 228, 229, 229, 230, 231, 231, 232, 232, 233, 234, 234, 235, 236, 236, 237, 238, 238, 239,
	239, 240, 241, 241, 242, 243, 243, 244, 245, 245, 246, 247, 247, 248, 249, 249, 250, 251, 251, 252,
	252, 253, 254, 254, 255, 256, 256, 257, 258, 259, 259, 260, 261, 261, 262, 263, 263, 264, 265, 265,
	266, 267, 267, 268, 269, 269, 270, 271, 271, 272, 273, 274, 274, 275, 276, 276, 277, 278, 278, 279,
	280, 281, 281, 282, 283, 283, 284, 285, 286, 286, 287, 288, 288, 289, 290, 291, 291, 292, 293, 294,
	294, 295, 296, 297, 297, 298, 299, 299, 300, 301, 302, 302, 303, 304, 305, 305, 306, 307, 308, 309,
	309, 310, 311, 312, 312, 313, 314, 315, 315, 316, 317, 318, 319, 319, 320, 321, 322, 322, 323, 324,
	325, 326, 326, 327, 328, 329, 330, 330, 331, 332, 333, 334, 334, 335, 336, 337, 338, 339, 339, 340,
	341, 342, 343, 343, 344, 345, 346, 347, 348, 348, 349, 350, 351, 352, 353, 354, 354, 355, 356, 357,
	358, 359, 360, 360, 361, 362, 363, 364, 365, 366, 367, 367, 368, 369, 370, 371, 372, 373, 374, 375,
	375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 386, 387, 388, 389, 390, 391, 392, 393,
	394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 404, 405, 406, 407, 408, 409, 410, 411, 412,
	413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 428, 429, 430, 431, 432, 433,
	434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 447, 448, 449, 450, 451, 452, 453, 454,
	455, 456, 457, 459, 460, 461, 462, 463, 464, 465, 466, 468, 469, 470, 471, 472, 473, 475, 476, 477,
	478, 479, 480, 482, 483, 484, 485, 486, 488, 489, 490, 491, 492, 494, 495, 496, 497, 498, 500, 501,
	502, 503, 505, 506, 507, 508, 510, 511, 512, 514, 515, 516, 517, 519, 520, 521, 523, 524, 525, 527,
	528, 529, 531, 532, 533, 535, 536, 537, 539, 540, 541, 543, 544, 546, 547, 548, 550, 551, 552, 554,
	555, 557, 558, 560, 561, 562, 564, 565, 567, 568, 570, 571, 573, 574, 576, 577, 579, 580, 582, 583,
	585, 586, 588, 589, 591, 592, 594, 595, 597, 599, 600, 602, 603, 605, 607, 608, 610, 611, 613, 615,
	616, 618, 620, 621, 623, 625, 626, 628, 630, 631, 633, 635, 636, 638, 640, 642, 643, 645, 647, 649,
	650, 652, 654, 656, 658, 659, 661, 663, 665, 667, 668, 670, 672, 674, 676, 678, 680, 682, 683, 685,
	687, 689, 691, 693, 695, 697, 699, 701, 703, 705, 707, 709, 711, 713, 715, 717, 719, 721, 723, 725,
	727, 730, 732, 734, 736, 738, 740, 742, 745, 747, 749, 751, 753, 756, 758, 760, 762, 765, 767, 769,
	771, 774, 776, 778, 781, 783, 785, 788, 790, 793, 795, 797, 800, 802, 805, 807, 810, 812, 815, 817,
	820, 822, 825, 828, 830, 833, 835, 838, 841, 843, 846, 849, 851, 854, 857, 859, 862, 865, 868, 871,
	873, 876, 879, 882, 885, 888, 891, 894, 896, 899, 902, 905, 908, 911, 914, 918, 921, 924, 927, 930,
	933, 936, 939, 943, 946, 949, 952, 956, 959, 962, 966, 969, 972, 976, 979, 983, 986, 989, 993, 996,
	1000,
]


static func apply_look_permille(input: Variant) -> Dictionary:
	if not _i32(input):
		return _bad_type("Look input must be an Int32.")
	# Math.Abs(Int32.MinValue) throws before clamping in the existing owner.
	if input == -2147483648:
		return {"ok": false, "error_type": "OverflowException", "error": "Int32 minimum has no positive Int32 magnitude."}
	var magnitude: int = mini(absi(input), 1000)
	return {"ok": true, "value": -LOOK_CURVE[magnitude] if input < 0 else LOOK_CURVE[magnitude]}


static func normalize_left_x(raw_axis: Variant) -> Dictionary:
	return _signed_axis(raw_axis)


static func normalize_left_y(raw_axis: Variant) -> Dictionary:
	return _signed_axis(raw_axis)


static func normalize_right_x(raw_axis: Variant) -> Dictionary:
	return _signed_axis(raw_axis)


static func normalize_right_y(raw_axis: Variant) -> Dictionary:
	if not _i32(raw_axis):
		return _bad_type("Raw axis must be an Int32.")
	return {"ok": true, "bits": Float32.store_word((float(raw_axis) - 32768.0) * Float32.read_word(RIGHT_Y_SCALE_BITS))}


static func mapping_gates(axis_bits: Variant) -> Dictionary:
	if typeof(axis_bits) != TYPE_INT or axis_bits < 0 or axis_bits > 0xffffffff:
		return _bad_type("Axis value must be a raw UInt32 float word.")
	var value: float = Float32.read_word(axis_bits)
	var threshold: float = Float32.read_word(DIGITAL_THRESHOLD_BITS)
	# Comparisons are strict; signed zeros and NaNs fire no arm.
	return {"ok": true, "value": {"plus_fires": value > 0.0, "minus_fires": value < 0.0,
		"plus_repeat_arms": value > threshold, "minus_repeat_arms": value < -threshold}}


static func _signed_axis(raw_axis: Variant) -> Dictionary:
	if not _i32(raw_axis):
		return _bad_type("Raw axis must be an Int32.")
	return {"ok": true, "bits": Float32.store_word(float(raw_axis) * Float32.read_word(AXIS_SCALE_BITS))}


static func _i32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _bad_type(message: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "error": message}
