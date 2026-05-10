"""
ISL Pipeline — Phase 3: Motion Mapping
Reads gloss_output.json, maps each gloss token to a motion descriptor
that the avatar renderer can play back.

Input:  nlp/gloss_output.json
Output: motion/motion_sequence.json

Each motion descriptor contains:
  hand_shape  — handshape name (ASL/ISL Stokoe-style label)
  movement    — primary movement type
  location    — body location reference
  duration    — seconds to hold/execute the sign
  non_manual  — facial expression / mouth pattern cue (optional)
"""

import json
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR    = Path(__file__).parent
INPUT_PATH  = BASE_DIR.parent / "nlp" / "gloss_output.json"
OUTPUT_PATH = BASE_DIR / "motion_sequence.json"

# ── Motion library ─────────────────────────────────────────────────────────────
# Each entry: gloss token → motion descriptor dict
# hand_shape  : shape of dominant hand
# movement    : primary movement
# location    : where the sign is made relative to body
# duration    : seconds (float)
# non_manual  : eyebrow / mouth cue for avatar (optional)
#
# Extend this dictionary as you record/model more signs.
# Unknown tokens fall back to FINGERSPELL.

MOTION_LIBRARY: dict[str, dict] = {

    # ── Greetings ──────────────────────────────────────────────────────────────
    # HELLO — ISLRTC MediaPipe verified (R fingers: [0.62, 0.72, 0.83, 0.83, 0.73])
    "HELLO": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # GOODBYE — ISLRTC MediaPipe verified (R fingers: [0.64, 0.61, 0.67, 0.65, 0.55])
    "GOODBYE": {
        "hand_shape": "bent_5",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # THANK — ISLRTC MediaPipe verified (R fingers: [0.6, 0.88, 0.99, 1.0, 0.96])
    "THANK": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },

    # I — ISLRTC MediaPipe verified (R fingers: [0.08, 0.06, 0.05, 0.05, 0.05])
    "I": {
        "hand_shape": "s_fist",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # YOU — ISLRTC MediaPipe verified (R fingers: [0.25, 0.41, 0.4, 0.34, 0.72])
    "YOU": {
        "hand_shape": "index_1",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # WE — ISLRTC MediaPipe verified (R fingers: [0.41, 0.43, 0.45, 0.45, 0.45])
    "WE": {
        "hand_shape": "a_hand",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "HE": {
        "hand_shape": "index_1",
        "movement":   "point_side",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "SHE": {
        "hand_shape": "index_1",
        "movement":   "point_side",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # THEY — ISLRTC MediaPipe verified (R fingers: [0.19, 0.5, 0.23, 0.14, 0.12])
    "THEY": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "MY":  {
        "hand_shape": "flat_b",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "YOUR": {
        "hand_shape": "flat_b",
        "movement":   "push_forward",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # OUR — ISLRTC MediaPipe verified (R fingers: [0.38, 0.21, 0.18, 0.16, 0.17])
    "OUR": {
        "hand_shape": "s_fist",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "HIS": {
        "hand_shape": "flat_b",
        "movement":   "push_side",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "HER": {
        "hand_shape": "flat_b",
        "movement":   "push_side",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },

    # GO — ISLRTC MediaPipe verified (R fingers: [0.77, 0.76, 0.71, 0.65, 0.57])
    "GO": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # COME — ISLRTC MediaPipe verified (R fingers: [0.57, 0.4, 0.36, 0.47, 0.7])
    "COME": {
        "hand_shape": "y_hand",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "EXPLAIN": {
        "hand_shape": "open_5",
        "movement":   "alternating_forward",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "mouth_open_e",
    },
    # UNDERSTAND — ISLRTC MediaPipe verified (R fingers: [0.37, 0.49, 0.17, 0.14, 0.15])
    "UNDERSTAND": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # LEARN — ISLRTC MediaPipe verified (R fingers: [0.66, 0.37, 0.41, 0.39, 0.29])
    "LEARN": {
        "hand_shape": "a_hand",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # TEACH — ISLRTC MediaPipe verified (R fingers: [0.51, 0.71, 0.87, 0.81, 0.67])
    "TEACH": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # KNOW — ISLRTC MediaPipe verified (R fingers: [0.49, 0.37, 0.37, 0.44, 0.46])
    "KNOW": {
        "hand_shape": "a_hand",
        "movement":   "tap_temple",
        "location":   "temple",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # THINK — ISLRTC MediaPipe verified (R fingers: [0.4, 0.56, 0.15, 0.11, 0.1])
    "THINK": {
        "hand_shape": "index_1",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "SHOW": {
        "hand_shape": "index_1",
        "movement":   "point_flat_hand",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    # HAVE — ISLRTC MediaPipe verified (R fingers: [0.75, 0.82, 0.93, 1.0, 1.0])
    "HAVE": {
        "hand_shape": "open_5",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # WANT — ISLRTC MediaPipe verified (R fingers: [0.66, 0.96, 0.95, 0.94, 0.87])
    "WANT": {
        "hand_shape": "open_5",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "NEED": {
        "hand_shape": "x_hook",
        "movement":   "downward_bend",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
    },
    "USE": {
        "hand_shape": "u_hand",
        "movement":   "circle_wrist",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "HELP": {
        "hand_shape": "flat_b",
        "movement":   "lift_fist",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "smile",
    },
    # WORK — ISLRTC MediaPipe verified (R fingers: [0.57, 0.72, 0.86, 0.92, 0.85])
    "WORK": {
        "hand_shape": "open_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # WRITE — ISLRTC MediaPipe verified (R fingers: [0.5, 0.27, 0.21, 0.15, 0.13])
    "WRITE": {
        "hand_shape": "a_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "WRITTEN": {
        "hand_shape": "modified_x",
        "movement":   "scribble_palm",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "READ": {
        "hand_shape": "v_hand",
        "movement":   "scan_palm_down",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    # CALL — ISLRTC MediaPipe verified (R fingers: [0.7, 0.4, 0.37, 0.32, 0.28])
    "CALL": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "STOP": {
        "hand_shape": "flat_b",
        "movement":   "chop_palm",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "furrowed_brows",
    },
    "START": {
        "hand_shape": "index_1",
        "movement":   "twist_between_fingers",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # TAKE — ISLRTC MediaPipe verified (R fingers: [0.49, 0.65, 0.86, 0.75, 0.45])
    "TAKE": {
        "hand_shape": "bent_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "TAKING": {
        "hand_shape": "claw_5",
        "movement":   "grasp_pull_inward",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # TALK — ISLRTC MediaPipe verified (R fingers: [0.6, 0.66, 0.8, 0.27, 0.23])
    "TALK": {
        "hand_shape": "v_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "COVER": {
        "hand_shape": "flat_b",
        "movement":   "cover_palm",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "COVERED": {
        "hand_shape": "flat_b",
        "movement":   "cover_palm",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # MAKE — ISLRTC MediaPipe verified (R fingers: [0.3, 0.45, 0.38, 0.33, 0.47])
    "MAKE": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "BECOME": {
        "hand_shape": "open_b",
        "movement":   "rotate_meet",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "IMAGINE": {
        "hand_shape": "index_1",
        "movement":   "temple_circle_open",
        "location":   "temple",
        "duration":   0.9,
        "non_manual": "raised_brows",
    },
    "DEMONSTRATE": {
        "hand_shape": "flat_b",
        "movement":   "show_bilateral_forward",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    # STUDY — ISLRTC MediaPipe verified (R fingers: [0.61, 0.84, 0.99, 1.0, 0.92])
    "STUDY": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "FEEL": {
        "hand_shape": "open_5",
        "movement":   "chest_upward",
        "location":   "chest",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "FELT": {
        "hand_shape": "open_5",
        "movement":   "chest_upward",
        "location":   "chest",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "MOVE": {
        "hand_shape": "flat_b",
        "movement":   "arc_side_shift",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "MOVED": {
        "hand_shape": "flat_b",
        "movement":   "arc_side_shift",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "BRING": {
        "hand_shape": "flat_5",
        "movement":   "bilateral_inward",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "BROUGHT": {
        "hand_shape": "flat_5",
        "movement":   "bilateral_inward",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "RECORD": {
        "hand_shape": "r_hand",
        "movement":   "circle_palm",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "RECORDED": {
        "hand_shape": "r_hand",
        "movement":   "circle_palm",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "EVOLVE": {
        "hand_shape": "bent_5",
        "movement":   "bilateral_unfold",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "raised_brows",
    },
    "EVOLVED": {
        "hand_shape": "bent_5",
        "movement":   "bilateral_unfold",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "raised_brows",
    },
    # ENJOY — ISLRTC MediaPipe verified (R fingers: [0.5, 0.58, 0.75, 0.8, 0.65])
    "ENJOY": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "ENJOYED": {
        "hand_shape": "open_5",
        "movement":   "chest_circle_bilateral",
        "location":   "chest",
        "duration":   0.8,
        "non_manual": "smile",
    },
    "FINISH": {
        "hand_shape": "open_5",
        "movement":   "bilateral_flip_down",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # FINISHED — ISLRTC MediaPipe verified (R fingers: [0.58, 0.58, 0.69, 0.71, 0.72])
    "FINISHED": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # DO — ISLRTC MediaPipe verified (R fingers: [0.62, 0.27, 0.2, 0.14, 0.12])
    "DO": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },

    # ── Common nouns ───────────────────────────────────────────────────────────
    "NETWORK": {
        "hand_shape": "open_5",
        "movement":   "fingertips_touch_circle",
        "location":   "neutral_space",
        "duration":   1.1,
        "non_manual": "neutral",
    },
    "LANGUAGE": {
        "hand_shape": "l_hand",
        "movement":   "arc_bilateral",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "COMPUTER": {
        "hand_shape": "c_hand",
        "movement":   "forearm_brush",
        "location":   "forearm",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "CLASS": {
        "hand_shape": "c_hand",
        "movement":   "arc_bilateral",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    # STUDENT — ISLRTC MediaPipe verified (R fingers: [0.52, 0.55, 0.68, 0.82, 0.81])
    "STUDENT": {
        "hand_shape": "bent_5",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "STUDENTS": {
        "hand_shape": "flat_o",
        "movement":   "forehead_to_flat_sweep",
        "location":   "forehead",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "TEACHER": {
        "hand_shape": "flat_o",
        "movement":   "forward_double_to_agent",
        "location":   "forehead",
        "duration":   1.1,
        "non_manual": "neutral",
    },
    # TODAY — ISLRTC MediaPipe verified (R fingers: [0.49, 0.43, 0.29, 0.27, 0.4])
    "TODAY": {
        "hand_shape": "a_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "HOME": {
        "hand_shape": "flat_o",
        "movement":   "cheek_to_cheek",
        "location":   "cheek",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    # COURSE — ISLRTC MediaPipe verified (R fingers: [0.42, 0.59, 0.7, 0.84, 0.93])
    "COURSE": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "COURSES": {
        "hand_shape": "c_hand",
        "movement":   "palm_slide_down_sweep",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "BOOK": {
        "hand_shape": "flat_b",
        "movement":   "book_open_bilateral",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "FIELD": {
        "hand_shape": "f_hand",
        "movement":   "bilateral_flat_sweep",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "TOPICS": {
        "hand_shape": "index_1",
        "movement":   "bilateral_list_down",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # MODEL — ISLRTC MediaPipe verified (R fingers: [0.6, 0.63, 0.54, 0.51, 0.48])
    "MODEL": {
        "hand_shape": "index_1",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "LECTURE": {
        "hand_shape": "l_hand",
        "movement":   "forward_arc",
        "location":   "mouth",
        "duration":   0.8,
        "non_manual": "mouth_open",
    },
    "LECTURES": {
        "hand_shape": "l_hand",
        "movement":   "forward_arc_sweep",
        "location":   "mouth",
        "duration":   0.9,
        "non_manual": "mouth_open",
    },
    # MACHINE — ISLRTC MediaPipe verified (R fingers: [0.5, 0.44, 0.5, 0.55, 0.51])
    "MACHINE": {
        "hand_shape": "a_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # PROGRAM — ISLRTC MediaPipe verified (R fingers: [0.6, 0.27, 0.2, 0.18, 0.2])
    "PROGRAM": {
        "hand_shape": "a_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # TIME — ISLRTC MediaPipe verified (R fingers: [0.41, 0.32, 0.26, 0.21, 0.21])
    "TIME": {
        "hand_shape": "a_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "TIMES": {
        "hand_shape": "index_1",
        "movement":   "tap_wrist_double",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # WEEK — ISLRTC MediaPipe verified (R fingers: [0.51, 0.4, 0.55, 0.52, 0.48])
    "WEEK": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # YEAR — ISLRTC MediaPipe verified (R fingers: [0.17, 0.52, 0.19, 0.12, 0.07])
    "YEAR": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "YEARS": {
        "hand_shape": "s_fist",
        "movement":   "circle_forward_double",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "SEMESTER": {
        "hand_shape": "s_fist",
        "movement":   "bilateral_arc_flat",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    # NAME — ISLRTC MediaPipe verified (R fingers: [0.04, 0.13, 0.07, 0.06, 0.04])
    "NAME": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "NEWSPAPER": {
        "hand_shape": "open_5",
        "movement":   "pinch_sweep_palm",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "NEWSPAPERS": {
        "hand_shape": "open_5",
        "movement":   "pinch_sweep_palm",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    # HISTORY — ISLRTC MediaPipe verified (R fingers: [0.53, 0.53, 0.55, 0.52, 0.48])
    "HISTORY": {
        "hand_shape": "a_hand",
        "movement":   "tap_temple",
        "location":   "temple",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "SUBJECT": {
        "hand_shape": "s_fist",
        "movement":   "bilateral_arc_chest",
        "location":   "chest",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    # PART — ISLRTC MediaPipe verified (R fingers: [0.61, 0.53, 0.64, 0.71, 0.68])
    "PART": {
        "hand_shape": "bent_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # DEPTH — ISLRTC MediaPipe verified (R fingers: [0.44, 0.64, 0.2, 0.13, 0.13])
    "DEPTH": {
        "hand_shape": "index_1",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # LEVEL — ISLRTC MediaPipe verified (R fingers: [0.54, 0.41, 0.41, 0.41, 0.36])
    "LEVEL": {
        "hand_shape": "a_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "CONTENT": {
        "hand_shape": "c_hand",
        "movement":   "chest_circle",
        "location":   "chest",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "PHILOSOPHY": {
        "hand_shape": "p_hand",
        "movement":   "bilateral_circle_slow",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    # INTERVIEW — ISLRTC MediaPipe verified (R fingers: [0.54, 0.09, 0.14, 0.12, 0.75])
    "INTERVIEW": {
        "hand_shape": "index_1",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "CONCEPT": {
        "hand_shape": "c_hand",
        "movement":   "temple_to_forward",
        "location":   "temple",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "CONCEPTS": {
        "hand_shape": "c_hand",
        "movement":   "temple_to_forward_sweep",
        "location":   "temple",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "TECHNIQUE": {
        "hand_shape": "t_hand",
        "movement":   "fingertip_arc_forward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "TECHNIQUES": {
        "hand_shape": "t_hand",
        "movement":   "fingertip_arc_sweep",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "STORY": {
        "hand_shape": "f_hand",
        "movement":   "bilateral_link_chain",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "STORIES": {
        "hand_shape": "f_hand",
        "movement":   "bilateral_link_chain",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "BEHAVIOR": {
        "hand_shape": "b_hand",
        "movement":   "bilateral_arc_downward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "CHAPTER": {
        "hand_shape": "c_hand",
        "movement":   "palm_slice_down",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "CHAPTERS": {
        "hand_shape": "c_hand",
        "movement":   "palm_slice_down_multiple",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    # POLICY — ISLRTC MediaPipe verified (R fingers: [0.44, 0.62, 0.21, 0.15, 0.16])
    "POLICY": {
        "hand_shape": "index_1",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # VIDEO — ISLRTC MediaPipe verified (R fingers: [0.35, 0.11, 0.07, 0.07, 0.08])
    "VIDEO": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # FACT — ISLRTC MediaPipe verified (R fingers: [0.49, 0.66, 0.87, 0.88, 0.84])
    "FACT": {
        "hand_shape": "flat_b",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # BIBLE — ISLRTC MediaPipe verified (R fingers: [0.48, 0.47, 0.54, 0.6, 0.63])
    "BIBLE": {
        "hand_shape": "s_fist",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "INTRODUCTION": {
        "hand_shape": "index_1",
        "movement":   "bilateral_meet_forward",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "MEMBER": {
        "hand_shape": "m_hand",
        "movement":   "tap_shoulder",
        "location":   "shoulder",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # PRIME — ISLRTC MediaPipe verified (R fingers: [0.42, 0.72, 0.82, 0.85, 0.83])
    "PRIME": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # MINISTER — ISLRTC MediaPipe verified (R fingers: [0.53, 0.26, 0.2, 0.14, 0.13])
    "MINISTER": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # UNIVERSITY — ISLRTC MediaPipe verified (R fingers: [0.64, 0.72, 0.52, 0.46, 0.4])
    "UNIVERSITY": {
        "hand_shape": "index_1",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "FACULTY": {
        "hand_shape": "f_hand",
        "movement":   "bilateral_arc_wide",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    # PROFESSOR — ISLRTC MediaPipe verified (R fingers: [0.56, 0.83, 0.85, 0.8, 0.69])
    "PROFESSOR": {
        "hand_shape": "open_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # RESEARCHER — ISLRTC MediaPipe verified (R fingers: [0.55, 0.48, 0.39, 0.28, 0.25])
    "RESEARCHER": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # YOGA — ISLRTC MediaPipe verified (R fingers: [0.58, 0.59, 0.7, 0.72, 0.61])
    "YOGA": {
        "hand_shape": "open_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "PRIMATE": {
        "hand_shape": "p_hand",
        "movement":   "bilateral_arc_body",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "MONKEY": {
        "hand_shape": "claw_5",
        "movement":   "armpit_scratch_bilateral",
        "location":   "sides",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "MONKEY'S": {
        "hand_shape": "claw_5",
        "movement":   "armpit_scratch_bilateral",
        "location":   "sides",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    # HUMAN — ISLRTC MediaPipe verified (R fingers: [0.53, 0.62, 0.7, 0.73, 0.65])
    "HUMAN": {
        "hand_shape": "flat_b",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "HUMANS": {
        "hand_shape": "h_hand",
        "movement":   "bilateral_upright_sweep",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },

    # ── Question words ─────────────────────────────────────────────────────────
    "WHAT": {
        "hand_shape": "open_5",
        "movement":   "side_to_side_palms_up",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
    },
    # WHERE — ISLRTC MediaPipe verified (R fingers: [0.53, 0.51, 0.59, 0.58, 0.54])
    "WHERE": {
        "hand_shape": "s_fist",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # WHEN — ISLRTC MediaPipe verified (R fingers: [0.49, 0.68, 0.79, 0.81, 0.73])
    "WHEN": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "WHY": {
        "hand_shape": "bent_middle",
        "movement":   "forehead_outward",
        "location":   "forehead",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
    },
    "WHO": {
        "hand_shape": "l_hand",
        "movement":   "circle_lips",
        "location":   "lips",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
    },
    # HOW — ISLRTC MediaPipe verified (R fingers: [0.52, 0.55, 0.64, 0.63, 0.57])
    "HOW": {
        "hand_shape": "bent_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # WHICH — ISLRTC MediaPipe verified (R fingers: [0.57, 0.61, 0.71, 0.69, 0.66])
    "WHICH": {
        "hand_shape": "open_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },

    # NOT — ISLRTC MediaPipe verified (R fingers: [0.58, 0.62, 0.56, 0.6, 1.0])
    "NOT": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # GOOD — ISLRTC MediaPipe verified (R fingers: [0.64, 0.29, 0.75, 0.8, 0.69])
    "GOOD": {
        "hand_shape": "bent_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # BAD — ISLRTC MediaPipe verified (R fingers: [0.75, 0.59, 0.78, 0.81, 0.78])
    "BAD": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "NEW": {
        "hand_shape": "flat_b",
        "movement":   "brush_palm_upward",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "raised_brows",
    },
    # MODERN — ISLRTC MediaPipe verified (R fingers: [0.55, 0.62, 0.56, 0.65, 0.66])
    "MODERN": {
        "hand_shape": "flat_b",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # TRADITIONAL — ISLRTC MediaPipe verified (R fingers: [0.36, 0.78, 0.82, 0.68, 0.39])
    "TRADITIONAL": {
        "hand_shape": "bent_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "INTERESTING": {
        "hand_shape": "bent_5",
        "movement":   "chest_pull_outward",
        "location":   "chest",
        "duration":   0.8,
        "non_manual": "raised_brows",
    },
    # EXTREMELY — ISLRTC MediaPipe verified (R fingers: [0.5, 0.58, 0.55, 0.56, 0.51])
    "EXTREMELY": {
        "hand_shape": "s_fist",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "OBVIOUSLY": {
        "hand_shape": "open_5",
        "movement":   "palms_forward_open",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "raised_brows",
    },
    # EVERYTHING — ISLRTC MediaPipe verified (R fingers: [0.42, 0.56, 0.73, 0.82, 0.86])
    "EVERYTHING": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "POPULAR": {
        "hand_shape": "p_hand",
        "movement":   "bilateral_wide_open",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "raised_brows",
    },
    "FANTASTIC": {
        "hand_shape": "f_hand",
        "movement":   "bilateral_arc_upward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "smile",
    },
    "TYPICAL": {
        "hand_shape": "t_hand",
        "movement":   "bilateral_roll_down",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # ALMOST — ISLRTC MediaPipe verified (R fingers: [0.59, 0.48, 0.44, 0.9, 1.0])
    "ALMOST": {
        "hand_shape": "bent_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "REALLY": {
        "hand_shape": "r_hand",
        "movement":   "forward_emphasis_double",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "raised_brows",
    },
    "PARTICULAR": {
        "hand_shape": "p_hand",
        "movement":   "index_point_down_single",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "VARIOUS": {
        "hand_shape": "v_hand",
        "movement":   "sweep_side_bilateral",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "CERTAIN": {
        "hand_shape": "c_hand",
        "movement":   "bilateral_firm_hold",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # FULL — ISLRTC MediaPipe verified (R fingers: [0.43, 0.71, 0.86, 0.31, 0.24])
    "FULL": {
        "hand_shape": "v_hand",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "ONLY": {
        "hand_shape": "index_1",
        "movement":   "twist_single_downward",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "MUCH": {
        "hand_shape": "bent_5",
        "movement":   "pull_apart_bilateral",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "puffed_cheeks",
    },
    "ALSO": {
        "hand_shape": "a_hand",
        "movement":   "brush_side_outward",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # WELL — ISLRTC MediaPipe verified (R fingers: [0.4, 0.77, 0.74, 0.54, 0.39])
    "WELL": {
        "hand_shape": "v_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # SOME — ISLRTC MediaPipe verified (R fingers: [0.68, 1.0, 1.0, 1.0, 1.0])
    "SOME": {
        "hand_shape": "open_5",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # BOTH — ISLRTC MediaPipe verified (R fingers: [0.38, 0.96, 1.0, 0.4, 0.41])
    "BOTH": {
        "hand_shape": "v_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # ABLE — ISLRTC MediaPipe verified (R fingers: [0.77, 0.32, 0.29, 0.25, 0.17])
    "ABLE": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # INTELLIGENT — ISLRTC MediaPipe verified (R fingers: [0.52, 0.64, 0.71, 0.67, 0.57])
    "INTELLIGENT": {
        "hand_shape": "flat_b",
        "movement":   "tap_forehead",
        "location":   "forehead",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "INTELLIGENCE": {
        "hand_shape": "index_1",
        "movement":   "temple_forward_arc",
        "location":   "temple",
        "duration":   0.9,
        "non_manual": "raised_brows",
    },
    "ARTIFICIAL": {
        "hand_shape": "a_hand",
        "movement":   "bilateral_shape_construct",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    # UNDERGRADUATE — ISLRTC MediaPipe verified (R fingers: [0.44, 0.53, 0.53, 0.52, 0.5])
    "UNDERGRADUATE": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "INTRODUCTORY": {
        "hand_shape": "index_1",
        "movement":   "bilateral_meet_sweep",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },

    # AND — ISLRTC MediaPipe verified (R fingers: [0.31, 0.33, 0.36, 0.37, 0.33])
    "AND": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "BUT": {
        "hand_shape": "index_1",
        "movement":   "cross_index_fingers",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "OR": {
        "hand_shape": "l_hand",
        "movement":   "side_to_side_alternate",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "raised_brows",
    },
    "THEN": {
        "hand_shape": "index_1",
        "movement":   "arc_forward_sequential",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "BECAUSE": {
        "hand_shape": "index_1",
        "movement":   "forehead_to_forward_flick",
        "location":   "forehead",
        "duration":   0.7,
        "non_manual": "raised_brows",
    },
    "FORTH": {
        "hand_shape": "flat_b",
        "movement":   "forward_sweep_outward",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },

    # THIS — ISLRTC MediaPipe verified (R fingers: [0.38, 0.37, 0.32, 0.39, 0.67])
    "THIS": {
        "hand_shape": "index_1",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # THAT — ISLRTC MediaPipe verified (R fingers: [0.48, 0.23, 0.23, 0.26, 0.32])
    "THAT": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # IT — ISLRTC MediaPipe verified (R fingers: [0.49, 0.61, 0.67, 0.7, 0.64])
    "IT": {
        "hand_shape": "flat_b",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "THESE": {
        "hand_shape": "index_1",
        "movement":   "sweep_near_bilateral",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    # THERE — ISLRTC MediaPipe verified (R fingers: [0.31, 0.5, 0.33, 0.2, 0.16])
    "THERE": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # HERE — ISLRTC MediaPipe verified (R fingers: [0.83, 1.0, 0.99, 0.96, 0.74])
    "HERE": {
        "hand_shape": "open_5",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "EVERYONE": {
        "hand_shape": "open_5",
        "movement":   "sweep_all_arc",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "raised_brows",
    },

    # ── Auxiliary / modal verbs ────────────────────────────────────────────────
    "WILL": {
        "hand_shape": "index_1",
        "movement":   "forward_cheek_push",
        "location":   "cheek",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "WOULD": {
        "hand_shape": "bent_b",
        "movement":   "forward_arc_soft",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # CAN — ISLRTC MediaPipe verified (R fingers: [0.42, 0.41, 0.52, 0.68, 0.67])
    "CAN": {
        "hand_shape": "s_fist",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "COULD": {
        "hand_shape": "s_fist",
        "movement":   "bilateral_downward_soft",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "HAS": {
        "hand_shape": "bent_b",
        "movement":   "press_chest_tap",
        "location":   "chest",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "BEEN": {
        "hand_shape": "flat_b",
        "movement":   "arc_backward_shoulder",
        "location":   "shoulder",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # MAY — ISLRTC MediaPipe verified (R fingers: [0.47, 0.42, 0.26, 0.19, 0.18])
    "MAY": {
        "hand_shape": "a_hand",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "YEAH": {
        "hand_shape": "s_fist",
        "movement":   "nod_downward",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "nod",
    },

    # ── Prepositions ───────────────────────────────────────────────────────────
    "OF": {
        "hand_shape": "f_hand",
        "movement":   "o_to_f_rotate",
        "location":   "neutral_space",
        "duration":   0.3,
        "non_manual": "neutral",
    },
    # IN — ISLRTC MediaPipe verified (R fingers: [0.64, 0.94, 1.0, 1.0, 0.95])
    "IN": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "FOR": {
        "hand_shape": "index_1",
        "movement":   "temple_twist_forward",
        "location":   "temple",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # FROM — ISLRTC MediaPipe verified (R fingers: [0.56, 0.41, 0.52, 0.71, 0.87])
    "FROM": {
        "hand_shape": "bent_5",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # AT — ISLRTC MediaPipe verified (R fingers: [0.55, 0.64, 0.67, 0.68, 0.61])
    "AT": {
        "hand_shape": "flat_b",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "ON": {
        "hand_shape": "flat_b",
        "movement":   "place_on_hand",
        "location":   "neutral_space",
        "duration":   0.3,
        "non_manual": "neutral",
    },
    "INTO": {
        "hand_shape": "flat_o",
        "movement":   "insert_forward",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    "ABOUT": {
        "hand_shape": "index_1",
        "movement":   "circle_palm_around",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "AS": {
        "hand_shape": "a_hand",
        "movement":   "bilateral_parallel_hold",
        "location":   "neutral_space",
        "duration":   0.3,
        "non_manual": "neutral",
    },
    "UNTIL": {
        "hand_shape": "index_1",
        "movement":   "arc_to_contact_stop",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # SINCE — ISLRTC MediaPipe verified (R fingers: [0.6, 0.71, 0.78, 0.79, 0.73])
    "SINCE": {
        "hand_shape": "open_5",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # AFTER — ISLRTC MediaPipe verified (R fingers: [0.59, 0.74, 0.8, 0.78, 0.63])
    "AFTER": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # OUT — ISLRTC MediaPipe verified (R fingers: [0.51, 0.73, 0.92, 0.96, 0.97])
    "OUT": {
        "hand_shape": "flat_b",
        "movement":   "tap_temple",
        "location":   "temple",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # BACK — ISLRTC MediaPipe verified (R fingers: [0.57, 0.5, 0.44, 0.49, 0.39])
    "BACK": {
        "hand_shape": "a_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },

    # ── Quantities / numbers ───────────────────────────────────────────────────
    "MORE": {
        "hand_shape": "flat_o",
        "movement":   "fingertips_tap_together",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # MANY — ISLRTC MediaPipe verified (R fingers: [0.65, 0.94, 0.95, 0.94, 0.74])
    "MANY": {
        "hand_shape": "open_5",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # SEVERAL — ISLRTC MediaPipe verified (R fingers: [0.47, 0.7, 0.73, 0.67, 0.57])
    "SEVERAL": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    # LOT — ISLRTC MediaPipe verified (R fingers: [0.51, 0.64, 0.67, 0.72, 0.73])
    "LOT": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "ALL": {
        "hand_shape": "open_5",
        "movement":   "sweep_bilateral_full",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # ONE — ISLRTC MediaPipe verified (R fingers: [0.2, 0.68, 0.27, 0.16, 0.12])
    "ONE": {
        "hand_shape": "index_1",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "FIVE": {
        "hand_shape": "open_5",
        "movement":   "upright_palm_hold",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    # SIX — ISLRTC MediaPipe verified (R fingers: [0.62, 0.72, 0.18, 0.13, 0.12])
    "SIX": {
        "hand_shape": "index_1",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "PERCENT": {
        "hand_shape": "p_hand",
        "movement":   "circle_descent_arc",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "SPECIFIC": {
        "hand_shape": "s_fist",
        "movement":   "index_point_down_tap",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },

    # ── Academic / AI terms ────────────────────────────────────────────────────
    "COMPUTATIONAL": {
        "hand_shape": "c_hand",
        "movement":   "bilateral_process_rotate",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "PROBABILISTIC": {
        "hand_shape": "p_hand",
        "movement":   "undulating_forward_wave",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "STATISTICAL": {
        "hand_shape": "s_fist",
        "movement":   "column_count_bilateral",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "NEURAL": {
        "hand_shape": "bent_5",
        "movement":   "bilateral_wave",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "ALGORITHM": {
        "hand_shape": "a_hand",
        "movement":   "layered_sequence_down",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "DATA": {
        "hand_shape": "d_hand",
        "movement":   "downward_arc_bilateral",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "TRAIN": {
        "hand_shape": "a_hand",
        "movement":   "knuckle_brush_forward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },

    # HOPE — ISLRTC MediaPipe verified (R fingers: [0.4, 0.66, 0.73, 0.21, 0.2])
    "HOPE": {
        "hand_shape": "v_hand",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    # EXCITED — ISLRTC MediaPipe verified (R fingers: [0.51, 0.74, 0.85, 0.8, 0.71])
    "EXCITED": {
        "hand_shape": "flat_b",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    # FUN — ISLRTC MediaPipe verified (R fingers: [0.27, 0.49, 0.41, 0.41, 0.32])
    "FUN": {
        "hand_shape": "s_fist",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "ENGAGING": {
        "hand_shape": "bent_5",
        "movement":   "bilateral_pull_in_chest",
        "location":   "chest",
        "duration":   0.8,
        "non_manual": "raised_brows",
    },
    "IMAGINE": {
        "hand_shape": "index_1",
        "movement":   "temple_circle_open",
        "location":   "temple",
        "duration":   0.9,
        "non_manual": "raised_brows",
    },

    # ── Proper nouns — kept as fingerspell intentionally ───────────────────────
    "AI": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "IIT": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "NPTEL": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.5,
        "non_manual": "neutral",
    },
    "DELHI": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.5,
        "non_manual": "neutral",
    },
    "PHD": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "GOOGLE": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.8,
        "non_manual": "neutral",
    },
    "BERKELEY": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   2.4,
        "non_manual": "neutral",
    },
    "WASHINGTON": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   3.0,
        "non_manual": "neutral",
    },
    "SEATTLE": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   2.1,
        "non_manual": "neutral",
    },
    "STUART": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.8,
        "non_manual": "neutral",
    },
    "RUSSELL": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   2.1,
        "non_manual": "neutral",
    },
    "PETER": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.5,
        "non_manual": "neutral",
    },
    "NOVICH": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.8,
        "non_manual": "neutral",
    },
    "MOSSAM": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.8,
        "non_manual": "neutral",
    },
    "MODI": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.2,
        "non_manual": "neutral",
    },
    "NITHYA": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.8,
        "non_manual": "neutral",
    },
    "2013": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.2,
        "non_manual": "neutral",
    },
    "2007": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   1.2,
        "non_manual": "neutral",
    },
    # 12 — ISLRTC MediaPipe verified (R fingers: [0.4, 0.74, 0.57, 0.3, 0.23])
    "12": {
        "hand_shape": "v_hand",
        "movement":   "forward_arc",
        "location":   "neutral",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "50": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "ROUNDEDNESS": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   3.3,
        "non_manual": "neutral",
    },
    "FINESSE": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   2.1,
        "non_manual": "neutral",
    },
    "DETOURS": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
        "duration":   2.1,
        "non_manual": "neutral",
    },

    # ── Transition / pause ─────────────────────────────────────────────────────
    "PAUSE": {
        "hand_shape": "rest",
        "movement":   "neutral_hold",
        "location":   "sides",
        "duration":   0.4,
        "non_manual": "neutral",
    },
}

# Fallback for unknown tokens — fingerspell placeholder
FINGERSPELL_TEMPLATE = {
    "hand_shape": "fingerspell",
    "movement":   "fingerspell_sequence",
    "location":   "neutral_space",
    "duration":   0.3,     # per letter; caller multiplies by len(word)
    "non_manual": "neutral",
}

# ── Mapping logic ──────────────────────────────────────────────────────────────

def map_token(token: str) -> dict:
    """
    Look up a single gloss token in the motion library.
    Unknown tokens get fingerspelled with duration scaled to word length.
    """
    if token in MOTION_LIBRARY:
        return {"token": token, **MOTION_LIBRARY[token]}

    # Fingerspell unknown word
    descriptor = dict(FINGERSPELL_TEMPLATE)
    descriptor["token"]    = token
    descriptor["duration"] = round(len(token) * 0.3, 2)   # ~0.3s per letter
    descriptor["note"]     = "fingerspelled — add to MOTION_LIBRARY when sign is recorded"
    return descriptor


def map_gloss_string(gloss: str) -> list[dict]:
    """Convert a gloss string like 'NEURAL NETWORK I EXPLAIN' to a motion sequence."""
    tokens = gloss.strip().split()
    if not tokens:
        return []

    sequence = []
    for token in tokens:
        descriptor = map_token(token)
        sequence.append(descriptor)

    # Insert short pause between signs for natural timing
    with_pauses = []
    for i, sign in enumerate(sequence):
        with_pauses.append(sign)
        if i < len(sequence) - 1:
            with_pauses.append({
                "token":      "PAUSE",
                **MOTION_LIBRARY["PAUSE"],
            })

    return with_pauses


def total_duration(sequence: list[dict]) -> float:
    return round(sum(s["duration"] for s in sequence), 2)

# ── Main ───────────────────────────────────────────────────────────────────────

def map_all(input_path: Path) -> list[dict]:
    if not input_path.exists():
        raise FileNotFoundError(
            f"gloss_output.json not found at {input_path}\n"
            "Run nlp/gloss_converter.py first."
        )

    with open(input_path, encoding="utf-8") as f:
        gloss_records = json.load(f)

    results = []
    for record in gloss_records:
        sequence = map_gloss_string(record["gloss"])
        results.append({
            "id":            record["id"],
            "start":         record["start"],
            "end":           record["end"],
            "clean":         record["clean"],
            "gloss":         record["gloss"],
            "motion":        sequence,
            "total_duration": total_duration(sequence),
        })

    return results


def save_output(results: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[MOTION] Saved: {OUTPUT_PATH}  ({len(results)} segments)")

    print(f"\n[MOTION] Sample (first segment):")
    if results:
        r = results[0]
        print(f"  Gloss    : {r['gloss']}")
        print(f"  Duration : {r['total_duration']}s")
        print(f"  Signs    : {len(r['motion'])} descriptors")
        for sign in r["motion"][:4]:
            print(f"    {sign['token']:20s}  {sign['hand_shape']:15s}  {sign['movement']}")


if __name__ == "__main__":
    print("[MOTION] Starting motion mapping…")
    results = map_all(INPUT_PATH)
    save_output(results)
    print("[MOTION] Phase 3 complete — motion_sequence.json ready for avatar")