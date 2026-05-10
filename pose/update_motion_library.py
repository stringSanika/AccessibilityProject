"""
ISL Pipeline — Phase 5: Motion Library Updater
Reads extracted_signs.json and patches motion_mapper.py with verified ISL descriptors.

Usage:
  python update_motion_library.py

This script:
  1. Reads extracted_signs.json (output of mediapipe_extractor.py)
  2. Maps finger extension values → hand shape name
  3. Updates the corresponding entry in motion_mapper.py
  4. Saves a backup of the original motion_mapper.py
"""

import json
import shutil
import re
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR        = Path(__file__).parent
INPUT_JSON      = BASE_DIR / "extracted_signs.json"
MOTION_MAPPER   = BASE_DIR.parent / "motion" / "motion_mapper.py"
BACKUP_DIR      = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# ── Finger extension → hand shape name ────────────────────────────────────────
# Maps [thumb, index, middle, ring, pinky] extension pattern → Stokoe hand shape
# Extension: 0.0 = closed/curled, 1.0 = fully extended

def classify_hand_shape(fingers: list[float]) -> str:
    """
    Classify 5 finger extension values into a named ISL hand shape.

    fingers = [thumb, index, middle, ring, pinky]
    Each value: 0.0 (closed) → 1.0 (extended)
    """
    t, i, m, r, p = fingers
    threshold      = 0.55   # above this = "extended"

    # Booleans
    T = t > threshold
    I = i > threshold
    M = m > threshold
    R = r > threshold
    P = p > threshold

    extended_count = sum([T, I, M, R, P])

    # ── Classify ──────────────────────────────────────────────────────────────
    if extended_count == 5:
        return "open_5"                      # All fingers extended

    if extended_count == 0:
        if t > 0.4:
            return "a_hand"                  # Fist with thumb up/side
        return "s_fist"                      # Tight fist

    if I and not M and not R and not P:
        return "index_1"                     # Index only

    if I and M and not R and not P:
        return "v_hand"                      # Index + middle (V / peace)

    if I and M and R and P and not T:
        return "flat_b"                      # 4 fingers extended, thumb in

    if I and M and R and P and T:
        return "open_5"                      # All 5

    if T and not I and not M and not R and P:
        return "y_hand"                      # Thumb + pinky

    if T and not I and not M and not R and not P:
        return "a_hand"                      # Thumb only

    if not T and not I and not M and not R and P:
        return "index_1"                     # Pinky only (rare)

    if I and M and not R and not P and T:
        return "u_hand"                      # Index + middle + thumb

    if not I and not M and not R and not P:
        return "s_fist"                      # All curled

    if extended_count >= 3 and extended_count <= 4:
        avg = sum(fingers) / 5
        if avg > 0.45:
            return "bent_5"                  # Partially open
        return "flat_b"

    if extended_count == 1 and I:
        return "index_1"

    # Default fallback
    return "open_5" if extended_count >= 3 else "s_fist"


# ── Motion descriptor builder ──────────────────────────────────────────────────

# Maps location name → movement description
LOCATION_MOVEMENT_MAP = {
    "raised":   ("wave_down",           1.0),
    "forehead": ("tap_forehead",        0.7),
    "temple":   ("tap_temple",          0.6),
    "chin":     ("forward_arc",         0.7),
    "mouth":    ("mouth_forward",       0.7),
    "chest":    ("press_chest",         0.6),
    "neutral":  ("forward_arc",         0.6),
    "wrist":    ("tap_wrist",           0.5),
    "shoulder": ("tap_shoulder",        0.6),
}

def build_motion_entry(sign_data: dict) -> dict:
    """Convert extracted sign data into a motion_mapper.py entry."""
    r_fingers  = sign_data["r_fingers"]
    r_location = sign_data["r_location"]

    hand_shape          = classify_hand_shape(r_fingers)
    movement, duration  = LOCATION_MOVEMENT_MAP.get(r_location, ("forward_arc", 0.6))

    return {
        "hand_shape": hand_shape,
        "movement":   movement,
        "location":   r_location,
        "duration":   duration,
        "non_manual": "neutral",
        "_source":    "ISLRTC_mediapipe_verified",
        "_r_fingers": r_fingers,
    }


# ── Patch motion_mapper.py ─────────────────────────────────────────────────────

def patch_motion_mapper(signs: list[dict]) -> None:
    """Update MOTION_LIBRARY entries in motion_mapper.py."""

    if not MOTION_MAPPER.exists():
        print(f"[ERROR] motion_mapper.py not found at {MOTION_MAPPER}")
        return

    # Backup original
    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"motion_mapper_backup_{ts}.py"
    shutil.copy(MOTION_MAPPER, backup)
    print(f"[BACKUP] Saved original → {backup}")

    content = MOTION_MAPPER.read_text(encoding="utf-8")
    patched = 0

    for sign_data in signs:
        sign_name = sign_data["sign"].upper()
        entry     = build_motion_entry(sign_data)

        # Build the new entry string (same style as original)
        new_block = (
            f'    # {sign_name} — ISLRTC MediaPipe verified '
            f'(R fingers: {entry["_r_fingers"]})\n'
            f'    "{sign_name}": {{\n'
            f'        "hand_shape": "{entry["hand_shape"]}",\n'
            f'        "movement":   "{entry["movement"]}",\n'
            f'        "location":   "{entry["location"]}",\n'
            f'        "duration":   {entry["duration"]},\n'
            f'        "non_manual": "neutral",\n'
            f'    }},'
        )

        # Find existing entry and replace it
        pattern = (
            rf'(    # [^\n]*\n)?'
            rf'    "{re.escape(sign_name)}": \{{[^}}]+\}},'
        )
        match = re.search(pattern, content, re.DOTALL)

        if match:
            content = content[:match.start()] + new_block + content[match.end():]
            print(f"  [UPDATED] {sign_name:15s} → hand_shape={entry['hand_shape']:12s} loc={entry['location']}")
            patched += 1
        else:
            print(f"  [NOT FOUND] {sign_name} — not in MOTION_LIBRARY, skipping")

    MOTION_MAPPER.write_text(content, encoding="utf-8")
    print(f"\n[UPDATE] Patched {patched}/{len(signs)} signs in motion_mapper.py")
    print("[UPDATE] Re-run: python motion/motion_mapper.py  to regenerate motion_sequence.json")


# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print("[PHASE 5] Updating motion_mapper.py with verified ISL data\n")

    if not INPUT_JSON.exists():
        print(f"[ERROR] extracted_signs.json not found.")
        print("  Run mediapipe_extractor.py first.")
        return

    with open(INPUT_JSON, encoding="utf-8") as f:
        signs = json.load(f)

    print(f"[INFO] {len(signs)} verified signs loaded from extracted_signs.json\n")

    # Print summary table
    print(f"  {'SIGN':<15} {'R_FINGERS':<35} {'SHAPE':<12} {'LOCATION'}")
    print(f"  {'-'*75}")
    for s in signs:
        shape = classify_hand_shape(s["r_fingers"])
        print(f"  {s['sign']:<15} {str(s['r_fingers']):<35} {shape:<12} {s['r_location']}")

    print()
    patch_motion_mapper(signs)


if __name__ == "__main__":
    run()