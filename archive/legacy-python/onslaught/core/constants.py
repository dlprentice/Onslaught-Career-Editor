"""
Onslaught Career Editor - Shared Constants
Extracted from patcher.py and BES format documentation
"""

# BES File Format Constants
BES_FILE_SIZE = 10004

# IMPORTANT: "true dword view"
# - The file begins with a 16-bit version word at offset 0x0000.
# - CCareer bytes are copied from/to `source+2` / `dest+2` in BEA.exe, so all CCareer dwords
#   are aligned to offsets where (file_offset % 4 == 2).
# - If you view the file at 4-byte aligned offsets (file_offset % 4 == 0), many values *look*
#   like "shift-16", but that is just a misaligned view of the same bytes.
BES_VERSION_WORD = 0x4BD1

# Legacy/debug: 32-bit "dword view" at file offset 0x0000 (version word + first 2 bytes of CCareer)
# Do NOT validate saves by comparing this value; only validate `BES_VERSION_WORD`.
BES_VERSION_STAMP_DWORD_VIEW = 0x00004BD1

# CCareer mapping: file_off = CAREER_BASE + mem_off
CAREER_BASE = 0x0002  # file offset where the CCareer memory dump begins

# CCareer offsets (in-memory) from BEA.exe
CCAREER_NEW_GOODIE_COUNT = 0x0000   # Increments when unlocking goodies (see Cutscene_UnlockGoodie_* in BEA.exe)
CCAREER_NODE_BASE = 0x0004          # CCareerNode[100] × 64 bytes
CCAREER_LINK_BASE = 0x1904          # CCareerNodeLink[200] × 8 bytes
CCAREER_GOODIE_BASE = 0x1F44        # CGoodie[300] × 4 bytes
CCAREER_KILLS_BASE = 0x23F4         # Kill counters[5] × 4 bytes
CCAREER_TECH_SLOTS_BASE = 0x2408    # mSlots[32] × 4 bytes
CCAREER_CAREER_IN_PROGRESS = 0x2488
CCAREER_SOUND_VOLUME = 0x248C
CCAREER_MUSIC_VOLUME = 0x2490
CCAREER_GOD_MODE_ENABLED = 0x2494   # God mode toggle state (g_bGodModeEnabled in Ghidra)
# Steam UI has two invert-Y toggles plus controller vibration:
# - Walker mode invert Y axis (string id 0x38): CCareer+0x24A4/0x24A8 (P1/P2)
# - Flight mode invert Y axis (string id 0x39): CCareer+0x249C/0x24A0 (P1/P2)
# - Controller vibration: CCareer+0x24AC/0x24B0 (P1/P2)
CCAREER_FLIGHT_INVERT_Y_P1 = 0x249C
CCAREER_FLIGHT_INVERT_Y_P2 = 0x24A0
CCAREER_WALKER_INVERT_Y_P1 = 0x24A4
CCAREER_WALKER_INVERT_Y_P2 = 0x24A8
CCAREER_VIBRATION_P1 = 0x24AC
CCAREER_VIBRATION_P2 = 0x24B0
CCAREER_CONTROLLER_CONFIG_P1 = 0x24B4
CCAREER_CONTROLLER_CONFIG_P2 = 0x24B8

# Offsets in BES file
OFFSET_VERSION = 0x0000
OFFSET_NEW_GOODIE_COUNT = CAREER_BASE + CCAREER_NEW_GOODIE_COUNT
OFFSET_NODES = CAREER_BASE + CCAREER_NODE_BASE
OFFSET_LINKS = CAREER_BASE + CCAREER_LINK_BASE
OFFSET_GOODIES = CAREER_BASE + CCAREER_GOODIE_BASE
OFFSET_KILLS = CAREER_BASE + CCAREER_KILLS_BASE
OFFSET_SLOTS = CAREER_BASE + CCAREER_TECH_SLOTS_BASE
OFFSET_CAREER_IN_PROGRESS = CAREER_BASE + CCAREER_CAREER_IN_PROGRESS
OFFSET_SOUND_VOLUME = CAREER_BASE + CCAREER_SOUND_VOLUME
OFFSET_MUSIC_VOLUME = CAREER_BASE + CCAREER_MUSIC_VOLUME
OFFSET_GOD_MODE_ENABLED = CAREER_BASE + CCAREER_GOD_MODE_ENABLED
OFFSET_INVERT_Y_P1 = CAREER_BASE + CCAREER_WALKER_INVERT_Y_P1
OFFSET_INVERT_Y_P2 = CAREER_BASE + CCAREER_WALKER_INVERT_Y_P2
OFFSET_INVERT_FLIGHT_P1 = CAREER_BASE + CCAREER_FLIGHT_INVERT_Y_P1
OFFSET_INVERT_FLIGHT_P2 = CAREER_BASE + CCAREER_FLIGHT_INVERT_Y_P2
OFFSET_VIBRATION_P1 = CAREER_BASE + CCAREER_VIBRATION_P1
OFFSET_VIBRATION_P2 = CAREER_BASE + CCAREER_VIBRATION_P2
OFFSET_CONTROLLER_CONFIG_P1 = CAREER_BASE + CCAREER_CONTROLLER_CONFIG_P1
OFFSET_CONTROLLER_CONFIG_P2 = CAREER_BASE + CCAREER_CONTROLLER_CONFIG_P2

# Fixed CCareer block ends at 0x24BC bytes (copied after header), so options begin at:
OFFSET_OPTIONS_ENTRIES = CAREER_BASE + 0x24BC  # 0x24BE

# Fixed tail snapshot size (OptionsTail)
OPTIONS_TAIL_SIZE = 0x56
OFFSET_OPTIONS_TAIL = BES_FILE_SIZE - OPTIONS_TAIL_SIZE

# Mystery regions (bytes we intentionally do not interpret/modify yet)
OFFSET_MYSTERY_HEADER_START = CAREER_BASE
OFFSET_MYSTERY_HEADER_END = CAREER_BASE + 0x0004

# Structure sizes
NODE_SIZE = 64
LINK_SIZE = 8
GOODIE_SIZE = 4

# Counts
NUM_LEVELS = 43
MAX_NODES = 100
MAX_LINKS = 200
MAX_GOODIES = 300
# Retail goodies gallery can surface slot 232 (FMV 33) in addition to 0..231.
GOODIE_DISPLAYABLE_COUNT = 233
MAX_SLOTS = 32
NUM_KILL_CATEGORIES = 5

# Rank values (true dword view: raw float bits at node+0x3C)
RANK_FLOAT_BITS = {
    'S': 0x3F800000,     # 1.0f
    'A': 0x3F4CCCCD,     # 0.8f
    'B': 0x3F19999A,     # 0.6f
    'C': 0x3EB33333,     # 0.35f
    'D': 0x3E19999A,     # 0.15f
    'E': 0x00000000,     # 0.0f
    'NONE': 0xBF800000,  # -1.0f (never completed)
}

# Back-compat name used by older code paths (prefer RANK_FLOAT_BITS)
RANK_VALUES = RANK_FLOAT_BITS

# Goodie states (true dword view: raw ints 0/1/2/3)
GOODIE_UNKNOWN = 0
GOODIE_INSTRUCTIONS_SHOWN = 1
GOODIE_NEW = 2  # Gold badge
GOODIE_OLD = 3  # Blue badge

# Kill categories
KILL_CATEGORIES = [
    'Aircraft',
    'Vehicles',
    'Emplacements',
    'Infantry',
    'Mechs',
]

# Kill thresholds for goodie unlocks
KILL_THRESHOLDS = {
    'Aircraft': [25, 50, 75, 100],
    'Vehicles': [100, 200, 300, 400],
    'Emplacements': [25, 50],  # 75 appears only in combined unlocks (not a standalone threshold)
    'Infantry': [40, 80, 160],
    'Mechs': [20, 40, 80],
}

# Level structure from Career.cpp (node index -> mWorldNumber)
LEVEL_STRUCTURE = [
    (0, 100), (1, 110), (2, 200), (3, 211), (4, 212),
    (5, 221), (6, 222), (7, 231), (8, 232), (9, 300),
    (10, 311), (11, 312), (12, 321), (13, 322), (14, 331),
    (15, 332), (16, 400), (17, 411), (18, 412), (19, 421),
    (20, 422), (21, 431), (22, 432), (23, 500), (24, 511),
    (25, 512), (26, 521), (27, 522), (28, 523), (29, 524),
    (30, 600), (31, 611), (32, 612), (33, 621), (34, 622),
    (35, 700), (36, 710), (37, 720), (38, 731), (39, 732),
    (40, 741), (41, 742), (42, 800),
]

# Application info
APP_NAME = "Onslaught Career Editor"
APP_VERSION = "2.0.0"
APP_AUTHOR = "BEA Community"
