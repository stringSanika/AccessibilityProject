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
    "HELLO": {
        "hand_shape": "flat_b",
        "movement":   "wave_outward",
        "location":   "forehead",
        "duration":   1.0,
        "non_manual": "smile",
    },
    "GOODBYE": {
        "hand_shape": "open_b",
        "movement":   "wave_side",
        "location":   "neutral_space",
        "duration":   1.2,
        "non_manual": "neutral",
    },
    "THANK": {
        "hand_shape": "flat_b",
        "movement":   "forward_arc",
        "location":   "chin",
        "duration":   0.9,
        "non_manual": "smile",
    },

    # ── Pronouns ───────────────────────────────────────────────────────────────
    "I": {
        "hand_shape": "index_1",
        "movement":   "point_self",
        "location":   "chest",
        "duration":   0.5,
        "non_manual": "neutral",
    },
    "YOU": {
        "hand_shape": "index_1",
        "movement":   "point_forward",
        "location":   "neutral_space",
        "duration":   0.5,
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
    "LEARN": {
        "hand_shape": "bent_5",
        "movement":   "forehead_to_flat",
        "location":   "forehead",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "TEACH": {
        "hand_shape": "flat_o",
        "movement":   "forward_double",
        "location":   "forehead",
        "duration":   1.0,
        "non_manual": "neutral",
    },
    "KNOW": {
        "hand_shape": "flat_b",
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
    "HAVE": {
        "hand_shape": "bent_b",
        "movement":   "press_chest",
        "location":   "chest",
        "duration":   0.6,
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
    "WORK": {
        "hand_shape": "s_fist",
        "movement":   "tap_wrists",
        "location":   "neutral_space",
        "duration":   0.9,
        "non_manual": "neutral",
    },
    "WRITE": {
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

    # ── Modifiers ──────────────────────────────────────────────────────────────
    "NOT": {
        "hand_shape": "a_hand",
        "movement":   "thumb_under_chin_forward",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "head_shake",
    },
    "GOOD": {
        "hand_shape": "flat_b",
        "movement":   "chin_forward_down",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "smile",
    },
    "BAD": {
        "hand_shape": "flat_b",
        "movement":   "chin_flip_down",
        "location":   "chin",
        "duration":   0.7,
        "non_manual": "furrowed_brows",
    },
    "NEW": {
        "hand_shape": "flat_b",
        "movement":   "brush_palm_upward",
        "location":   "neutral_space",
        "duration":   0.7,
        "non_manual": "raised_brows",
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
