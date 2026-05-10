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
    "THANK": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.9,
        "non_manual": "smile",
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
    "WE": {
        "hand_shape": "index_1",
        "movement":   "arc_inclusive",
        "location":   "chest",
        "duration":   0.7,
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
    "THEY": {
        "hand_shape": "index_1",
        "movement":   "sweep_side",
        "location":   "neutral_space",
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
    "OUR": {
        "hand_shape": "flat_b",
        "movement":   "arc_chest_bilateral",
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

    # ── Common verbs ───────────────────────────────────────────────────────────
    "GO": {
        "hand_shape": "index_1",
        "movement":   "arc_forward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "COME": {
        "hand_shape": "index_1",
        "movement":   "arc_inward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "EXPLAIN": {
        "hand_shape": "open_5",
        "movement":   "alternating_forward",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "mouth_open_e",
    },
    "UNDERSTAND": {
        "hand_shape": "index_1",
        "movement":   "flick_up_forehead",
        "location":   "forehead",
        "duration":   0.7,
        "non_manual": "raised_brows",
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
    "THINK": {
        "hand_shape": "index_1",
        "movement":   "circle_temple",
        "location":   "temple",
        "duration":   0.7,
        "non_manual": "squint",
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
    "WANT": {
        "hand_shape": "bent_5",
        "movement":   "pull_inward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "puffed_cheeks",
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
    "WRITE": {
        "hand_shape": "modified_x",
        "movement":   "scribble_palm",
        "location":   "neutral_space",
        "duration":   1.0,
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
    "CALL": {
        "hand_shape": "y_hand",
        "movement":   "thumb_ear_pinky_mouth",
        "location":   "ear",
        "duration":   0.8,
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
    "TAKE": {
        "hand_shape": "claw_5",
        "movement":   "grasp_pull_inward",
        "location":   "neutral_space",
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
    "TALK": {
        "hand_shape": "index_1",
        "movement":   "mouth_forward_bilateral",
        "location":   "mouth",
        "duration":   0.7,
        "non_manual": "mouth_open",
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
    "MAKE": {
        "hand_shape": "s_fist",
        "movement":   "rotate_fists",
        "location":   "neutral_space",
        "duration":   0.7,
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
    "STUDY": {
        "hand_shape": "v_hand",
        "movement":   "scan_palm_down",
        "location":   "neutral_space",
        "duration":   0.9,
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
    "ENJOY": {
        "hand_shape": "open_5",
        "movement":   "chest_circle_bilateral",
        "location":   "chest",
        "duration":   0.8,
        "non_manual": "smile",
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
    "FINISHED": {
        "hand_shape": "open_5",
        "movement":   "bilateral_flip_down",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "DO": {
        "hand_shape": "s_fist",
        "movement":   "bilateral_side_sweep",
        "location":   "neutral_space",
        "duration":   0.5,
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
    "STUDENT": {
        "hand_shape": "flat_o",
        "movement":   "forehead_to_flat",
        "location":   "forehead",
        "duration":   1.0,
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
    "TODAY": {
        "hand_shape": "y_hand",
        "movement":   "downward_double",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "HOME": {
        "hand_shape": "flat_o",
        "movement":   "cheek_to_cheek",
        "location":   "cheek",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "COURSE": {
        "hand_shape": "c_hand",
        "movement":   "palm_slide_down",
        "location":   "neutral_space",
        "duration":   0.7,
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
    "MODEL": {
        "hand_shape": "m_hand",
        "movement":   "shape_bilateral",
        "location":   "neutral_space",
        "duration":   0.8,
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
    "MACHINE": {
        "hand_shape": "bent_5",
        "movement":   "bilateral_gear_rotate",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "PROGRAM": {
        "hand_shape": "p_hand",
        "movement":   "bilateral_flat_alternate",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "TIME": {
        "hand_shape": "index_1",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "TIMES": {
        "hand_shape": "index_1",
        "movement":   "tap_wrist_double",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "WEEK": {
        "hand_shape": "index_1",
        "movement":   "sweep_palm_side",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "YEAR": {
        "hand_shape": "s_fist",
        "movement":   "circle_forward_full",
        "location":   "neutral_space",
        "duration":   0.8,
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
    "NAME": {
        "hand_shape": "h_hand",
        "movement":   "tap_cross_fingers",
        "location":   "neutral_space",
        "duration":   0.5,
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
    "HISTORY": {
        "hand_shape": "h_hand",
        "movement":   "backward_arc_descend",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "SUBJECT": {
        "hand_shape": "s_fist",
        "movement":   "bilateral_arc_chest",
        "location":   "chest",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "PART": {
        "hand_shape": "flat_b",
        "movement":   "chop_partial_side",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "DEPTH": {
        "hand_shape": "flat_b",
        "movement":   "downward_level_deep",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
    },
    "LEVEL": {
        "hand_shape": "flat_b",
        "movement":   "bilateral_level_flat",
        "location":   "neutral_space",
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
    "INTERVIEW": {
        "hand_shape": "v_hand",
        "movement":   "bilateral_forward_alternate",
        "location":   "neutral_space",
        "duration":   0.9,
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
    "POLICY": {
        "hand_shape": "p_hand",
        "movement":   "flat_slide_forward",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "VIDEO": {
        "hand_shape": "v_hand",
        "movement":   "bilateral_flicker",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "FACT": {
        "hand_shape": "f_hand",
        "movement":   "palm_flat_down",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "BIBLE": {
        "hand_shape": "flat_b",
        "movement":   "book_open_tap",
        "location":   "neutral_space",
        "duration":   0.8,
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
    "PRIME": {
        "hand_shape": "p_hand",
        "movement":   "upward_emphasis",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "MINISTER": {
        "hand_shape": "m_hand",
        "movement":   "shoulder_bilateral_tap",
        "location":   "shoulder",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "UNIVERSITY": {
        "hand_shape": "u_hand",
        "movement":   "circle_upward",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "FACULTY": {
        "hand_shape": "f_hand",
        "movement":   "bilateral_arc_wide",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "neutral",
    },
    "PROFESSOR": {
        "hand_shape": "p_hand",
        "movement":   "forward_double_arc",
        "location":   "forehead",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "RESEARCHER": {
        "hand_shape": "r_hand",
        "movement":   "search_arc_forward",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "YOGA": {
        "hand_shape": "y_hand",
        "movement":   "bilateral_balance",
        "location":   "neutral_space",
        "duration":   0.9,
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
    "HUMAN": {
        "hand_shape": "h_hand",
        "movement":   "bilateral_upright_body",
        "location":   "neutral_space",
        "duration":   0.7,
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
    "WHERE": {
        "hand_shape": "index_1",
        "movement":   "side_to_side",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
    },
    "WHEN": {
        "hand_shape": "index_1",
        "movement":   "circle_index",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
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
    "HOW": {
        "hand_shape": "bent_b",
        "movement":   "knuckles_rotate_up",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "furrowed_brows",
    },
    "WHICH": {
        "hand_shape": "a_hand",
        "movement":   "alternate_side_palms",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
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
    "MODERN": {
        "hand_shape": "m_hand",
        "movement":   "forward_arc_rise",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "raised_brows",
    },
    "TRADITIONAL": {
        "hand_shape": "t_hand",
        "movement":   "bilateral_roll_backward",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "INTERESTING": {
        "hand_shape": "bent_5",
        "movement":   "chest_pull_outward",
        "location":   "chest",
        "duration":   0.8,
        "non_manual": "raised_brows",
    },
    "EXTREMELY": {
        "hand_shape": "x_hook",
        "movement":   "thrust_forward_sharp",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "puffed_cheeks",
    },
    "OBVIOUSLY": {
        "hand_shape": "open_5",
        "movement":   "palms_forward_open",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "raised_brows",
    },
    "EVERYTHING": {
        "hand_shape": "open_5",
        "movement":   "sweep_bilateral_all",
        "location":   "neutral_space",
        "duration":   0.8,
        "non_manual": "raised_brows",
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
    "ALMOST": {
        "hand_shape": "flat_b",
        "movement":   "near_miss_upward",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "squint",
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
    "FULL": {
        "hand_shape": "flat_b",
        "movement":   "sweep_over_flat_hand",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "puffed_cheeks",
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
    "WELL": {
        "hand_shape": "open_5",
        "movement":   "palms_up_float",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "raised_brows",
    },
    "SOME": {
        "hand_shape": "flat_b",
        "movement":   "partial_sweep_palm",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "BOTH": {
        "hand_shape": "v_hand",
        "movement":   "bilateral_tap_together",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "ABLE": {
        "hand_shape": "a_hand",
        "movement":   "bilateral_downward_firm",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "INTELLIGENT": {
        "hand_shape": "index_1",
        "movement":   "temple_forward_flick",
        "location":   "temple",
        "duration":   0.7,
        "non_manual": "raised_brows",
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
    "UNDERGRADUATE": {
        "hand_shape": "u_hand",
        "movement":   "bilateral_arc_under",
        "location":   "neutral_space",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "INTRODUCTORY": {
        "hand_shape": "index_1",
        "movement":   "bilateral_meet_sweep",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },

    # ── Conjunctions / connectors ──────────────────────────────────────────────
    "AND": {
        "hand_shape": "open_5",
        "movement":   "fingers_close_together",
        "location":   "neutral_space",
        "duration":   0.4,
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

    # ── Determiners / pointers ─────────────────────────────────────────────────
    "THIS": {
        "hand_shape": "index_1",
        "movement":   "point_down_near",
        "location":   "neutral_space",
        "duration":   0.3,
        "non_manual": "neutral",
    },
    "THAT": {
        "hand_shape": "index_1",
        "movement":   "point_forward_far",
        "location":   "neutral_space",
        "duration":   0.3,
        "non_manual": "neutral",
    },
    "IT": {
        "hand_shape": "index_1",
        "movement":   "point_neutral",
        "location":   "neutral_space",
        "duration":   0.3,
        "non_manual": "neutral",
    },
    "THESE": {
        "hand_shape": "index_1",
        "movement":   "sweep_near_bilateral",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    "THERE": {
        "hand_shape": "index_1",
        "movement":   "point_away_side",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    "HERE": {
        "hand_shape": "index_1",
        "movement":   "point_down_current",
        "location":   "neutral_space",
        "duration":   0.4,
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
    "CAN": {
        "hand_shape": "s_fist",
        "movement":   "bilateral_downward_firm",
        "location":   "neutral_space",
        "duration":   0.5,
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
    "MAY": {
        "hand_shape": "open_5",
        "movement":   "palms_up_alternate",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "raised_brows",
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
    "IN": {
        "hand_shape": "flat_o",
        "movement":   "insert_into_c_hand",
        "location":   "neutral_space",
        "duration":   0.3,
        "non_manual": "neutral",
    },
    "FOR": {
        "hand_shape": "index_1",
        "movement":   "temple_twist_forward",
        "location":   "temple",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "FROM": {
        "hand_shape": "index_1",
        "movement":   "pull_inward_arc",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "AT": {
        "hand_shape": "flat_b",
        "movement":   "tap_palm_once",
        "location":   "neutral_space",
        "duration":   0.3,
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
    "SINCE": {
        "hand_shape": "index_1",
        "movement":   "backward_to_forward_arc",
        "location":   "shoulder",
        "duration":   0.6,
        "non_manual": "neutral",
    },
    "AFTER": {
        "hand_shape": "flat_b",
        "movement":   "arc_forward_over",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "OUT": {
        "hand_shape": "flat_o",
        "movement":   "open_outward_spread",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    "BACK": {
        "hand_shape": "flat_b",
        "movement":   "backward_tap_shoulder",
        "location":   "shoulder",
        "duration":   0.5,
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
    "MANY": {
        "hand_shape": "flat_o",
        "movement":   "open_spread_bilateral",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "raised_brows",
    },
    "SEVERAL": {
        "hand_shape": "open_5",
        "movement":   "fingers_spread_count",
        "location":   "neutral_space",
        "duration":   0.5,
        "non_manual": "raised_brows",
    },
    "LOT": {
        "hand_shape": "l_hand",
        "movement":   "bilateral_wide_arc",
        "location":   "neutral_space",
        "duration":   0.6,
        "non_manual": "puffed_cheeks",
    },
    "ALL": {
        "hand_shape": "open_5",
        "movement":   "sweep_bilateral_full",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "neutral",
    },
    "ONE": {
        "hand_shape": "index_1",
        "movement":   "single_upright_hold",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    "FIVE": {
        "hand_shape": "open_5",
        "movement":   "upright_palm_hold",
        "location":   "neutral_space",
        "duration":   0.4,
        "non_manual": "neutral",
    },
    "SIX": {
        "hand_shape": "y_hand",
        "movement":   "tap_chin_once",
        "location":   "chin",
        "duration":   0.4,
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

    # ── Emotions / states ──────────────────────────────────────────────────────
    "HOPE": {
        "hand_shape": "index_1",
        "movement":   "forehead_to_forward_arc",
        "location":   "forehead",
        "duration":   0.7,
        "non_manual": "raised_brows",
    },
    # EXCITED — ISLRTC MediaPipe verified (R fingers: [0.51, 0.74, 0.85, 0.8, 0.71])
    "EXCITED": {
        "hand_shape": "flat_b",
        "movement":   "tap_wrist",
        "location":   "wrist",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "FUN": {
        "hand_shape": "u_hand",
        "movement":   "nose_to_chin_arc",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "smile",
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
    "12": {
        "hand_shape": "fingerspell",
        "movement":   "fingerspell_sequence",
        "location":   "neutral_space",
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