"""
ISL Pipeline — Phase 5: Avatar SIGNS Updater
Reads extracted_signs.json and patches the SIGNS dict in avatar_3d.html
with verified ISL finger positions from ISLRTC videos.

Usage:
  python pose/update_avatar.py

Run AFTER:
  python pose/mediapipe_extractor.py
Run BEFORE:
  make serve / make avatar
"""

import json
import re
import shutil
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR    = Path(__file__).parent
INPUT_JSON  = BASE_DIR / "extracted_signs.json"
AVATAR_HTML = BASE_DIR.parent / "avatar" / "avatar_3d.html"
BACKUP_DIR  = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# ── Known-good fallback signs ──────────────────────────────────────────────────
# When MediaPipe extraction gives near-zero values (e.g. finger pointing
# toward signer's body — not at camera), use these verified defaults.
# These were confirmed by watching ISLRTC videos manually.

KNOWN_GOOD_FALLBACKS = {
    # Pronouns — pointing gestures are hard for MediaPipe
    "I":    {"r_fingers": [0.3, 1.0, 0.1, 0.1, 0.1], "r_location": "self",
             "l_fingers": [0.5, 0.5, 0.5, 0.5, 0.5], "l_location": "neutral"},
    "YOU":  {"r_fingers": [0.3, 1.0, 0.1, 0.1, 0.1], "r_location": "forward",
             "l_fingers": [0.5, 0.5, 0.5, 0.5, 0.5], "l_location": "neutral"},
    "WE":   {"r_fingers": [0.3, 1.0, 0.1, 0.1, 0.1], "r_location": "chest",
             "l_fingers": [0.5, 0.5, 0.5, 0.5, 0.5], "l_location": "neutral"},
    "HE":   {"r_fingers": [0.3, 1.0, 0.1, 0.1, 0.1], "r_location": "forward",
             "l_fingers": [0.5, 0.5, 0.5, 0.5, 0.5], "l_location": "neutral"},
    "SHE":  {"r_fingers": [0.3, 1.0, 0.1, 0.1, 0.1], "r_location": "forward",
             "l_fingers": [0.5, 0.5, 0.5, 0.5, 0.5], "l_location": "neutral"},
    "MY":   {"r_fingers": [0.9, 1.0, 1.0, 1.0, 1.0], "r_location": "chest",
             "l_fingers": [0.5, 0.5, 0.5, 0.5, 0.5], "l_location": "neutral"},
    "YOUR": {"r_fingers": [0.9, 1.0, 1.0, 1.0, 1.0], "r_location": "forward",
             "l_fingers": [0.5, 0.5, 0.5, 0.5, 0.5], "l_location": "neutral"},
}

EXTRACTION_CONFIDENCE_THRESHOLD = 0.20  # if max finger value below this → use fallback


def apply_fallback_if_needed(sign_data: dict) -> dict:
    """
    If extracted finger values are all near-zero (extraction failed),
    apply a known-good fallback for that sign if one exists.
    """
    sign   = sign_data["sign"].upper()
    r_fing = sign_data["r_fingers"]
    max_v  = max(r_fing)

    if max_v < EXTRACTION_CONFIDENCE_THRESHOLD and sign in KNOWN_GOOD_FALLBACKS:
        fb = KNOWN_GOOD_FALLBACKS[sign]
        print(f"  [FALLBACK] {sign:12s} max={max_v:.2f} < {EXTRACTION_CONFIDENCE_THRESHOLD} "
              f"→ using known-good values")
        return {
            **sign_data,
            "r_fingers":  fb["r_fingers"],
            "r_location": fb["r_location"],
            "l_fingers":  fb["l_fingers"],
            "l_location": fb["l_location"],
            "source":     "ISLRTC_manual_fallback",
        }
    return sign_data


# Maps the hand shape name from motion_mapper to [thumb,index,middle,ring,pinky]
# values used in the SIGNS dict of avatar_3d.html

SHAPE_TO_FINGERS = {
    "open_5":    [1,   1,   1,   1,   1  ],
    "flat_b":    [0.5, 1,   1,   1,   1  ],
    "index_1":   [0.3, 1,   0.1, 0.1, 0.1],
    "v_hand":    [0.3, 1,   1,   0.1, 0.1],
    "s_fist":    [0.1, 0.1, 0.1, 0.1, 0.1],
    "a_hand":    [0.5, 0.1, 0.1, 0.1, 0.1],
    "bent_5":    [0.6, 0.5, 0.5, 0.5, 0.5],
    "bent_b":    [0.5, 0.6, 0.6, 0.6, 0.5],
    "y_hand":    [1,   0.1, 0.1, 0.1, 1  ],
    "u_hand":    [0.3, 1,   1,   0.1, 0.1],
    "c_hand":    [0.6, 0.6, 0.6, 0.6, 0.6],
    "flat_o":    [0.4, 0.4, 0.4, 0.4, 0.4],
    "x_hook":    [0.3, 0.3, 0.1, 0.1, 0.1],
    "f_hand":    [0.3, 0.3, 1,   1,   1  ],
    "fingerspell":[1,  1,   1,   1,   1  ],
    "default":   [0.9, 1,   1,   1,   1  ],
}

# ── Location → arm pose name ────────────────────────────────────────────────────

LOCATION_TO_POSE = {
    "raised":   "raised",
    "forehead": "forehead",
    "temple":   "temple",
    "chin":     "chin",
    "mouth":    "mouth",
    "chest":    "chest",
    "self":     "self",       # pointing toward own body
    "neutral":  "neutral",
    "forward":  "forward",
    "wrist":    "wrist",
    "shoulder": "shoulder",
    "sides":    "sides",
}

# ── Hand shape classifier (same as update_motion_library.py) ───────────────────

def classify_hand_shape(fingers: list[float]) -> str:
    t, i, m, r, p = fingers
    avg = sum(fingers) / 5
    mx  = max(fingers)

    def ext(v): return v > max(0.35, avg * 0.85)
    T = ext(t); I = ext(i); M = ext(m); R = ext(r); P = ext(p)
    extended_count = sum([T, I, M, R, P])

    if extended_count == 5 or avg > 0.70:
        return "open_5"
    if extended_count == 0 or mx < 0.25:
        return "s_fist"
    if i == mx and i > (m * 1.3) and i > (r * 1.3):
        if p > (i * 0.7) and not M and not R:
            return "y_hand"
        return "index_1"
    if T and P and not I and not M and not R:
        return "y_hand"
    if I and M and not R and not P:
        return "v_hand"
    if I and M and R and P and not T:
        return "flat_b"
    if I and M and R and P and T:
        return "open_5"
    if extended_count <= 1:
        return "a_hand" if T else "s_fist"
    if 0.30 < avg < 0.60:
        return "bent_5"
    if extended_count >= 3:
        return "flat_b"
    return "open_5" if avg > 0.55 else "s_fist"


def fingers_to_js(fingers: list) -> str:
    """Convert [0.9, 1, 1, 1, 1] to '.9,1,1,1,1' (JS compact format)."""
    parts = []
    for v in fingers:
        if v == 1:
            parts.append("1")
        elif v == 0:
            parts.append("0")
        else:
            # Remove leading zero: 0.9 → .9
            s = f"{v:.1f}"
            if s.startswith("0."):
                s = s[1:]
            parts.append(s)
    return ",".join(parts)


def build_signs_entry(sign_name: str, sign_data: dict) -> str:
    """
    Build the JS SIGNS entry string for avatar_3d.html.

    Format:
      NAME:     [[rF],'rPose', [lF],'lPose', headTilt],
    """
    r_fingers  = sign_data["r_fingers"]
    l_fingers  = sign_data["l_fingers"]
    r_location = sign_data["r_location"]
    l_location = sign_data["l_location"]

    r_pose = LOCATION_TO_POSE.get(r_location, "neutral")
    l_pose = LOCATION_TO_POSE.get(l_location, "neutral")

    r_js = fingers_to_js(r_fingers)
    l_js = fingers_to_js(l_fingers)

    # Pad sign name for alignment
    padded = f"{sign_name}:"
    padding = max(1, 11 - len(padded))

    return (
        f"  {padded}{' ' * padding}"
        f"[[{r_js}],'{r_pose}', "
        f"[{l_js}],'{l_pose}',  0],"
        f"  // ISLRTC verified"
    )


# ── Patch avatar_3d.html ───────────────────────────────────────────────────────

def patch_avatar_html(signs: list[dict]) -> None:
    """Update SIGNS entries in avatar_3d.html, using real arm angles when available."""

    if not AVATAR_HTML.exists():
        print(f"[ERROR] avatar_3d.html not found at {AVATAR_HTML}")
        return

    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"avatar_3d_backup_{ts}.html"
    shutil.copy(AVATAR_HTML, backup)
    print(f"[BACKUP] {backup.name}")

    content = AVATAR_HTML.read_text(encoding="utf-8")

    # First: ensure the custom_pose() function exists in the JS
    # This lets us use extracted arm angles directly instead of named poses
    if "function custom_pose" not in content:
        content = inject_custom_pose_function(content)

    patched = 0

    for sign_data in signs:
        sign_data = apply_fallback_if_needed(sign_data)
        sign_name = sign_data["sign"].upper()
        r_angles  = sign_data.get("r_angles")
        l_angles  = sign_data.get("l_angles")

        if r_angles:
            # Use real extracted arm angles → much more accurate
            new_entry = build_signs_entry_with_angles(sign_name, sign_data)
        else:
            # Fallback to location-based pose name
            new_entry = build_signs_entry(sign_name, sign_data)

        pattern = (
            rf'  "?{re.escape(sign_name)}"?\s*:'
            rf'\s*\[\[.*?\].*?\],.*?(?://[^\n]*)?\n'
        )
        match = re.search(pattern, content)

        if match:
            content = content[:match.start()] + new_entry + "\n" + content[match.end():]
            src = "angles" if r_angles else "pose"
            print(f"  [UPDATED] {sign_name:15s} → [{src}]  loc={sign_data['r_location']}")
            patched += 1
        else:
            print(f"  [NOT FOUND] {sign_name}")

    AVATAR_HTML.write_text(content, encoding="utf-8")
    print(f"\n[AVATAR] Patched {patched}/{len(signs)} signs in avatar_3d.html")


def inject_custom_pose_function(content: str) -> str:
    """
    Inject a custom_pose() JS function into avatar_3d.html.
    This allows SIGNS entries to specify exact arm rotations instead of
    named poses like 'chest' or 'forward'.

    The function is added right before setArmPose().
    """
    injection = """
// custom_pose: apply exact arm angles extracted from ISLRTC Pose data
// Called when a SIGNS entry uses 'custom' as the pose name
// and passes angles via the 7th/8th element of the SIGNS array
function apply_custom_angles(armRig, angles, s) {
  if (!angles) return;
  armRig.upperArm.rotation.x = angles[0];
  armRig.upperArm.rotation.z = s * angles[1];
  armRig.foreArm.rotation.x  = angles[2];
  armRig.hand.rotation.z     = angles[3];
}

"""
    # Insert before setArmPose function
    insert_at = content.find("function setArmPose")
    if insert_at == -1:
        return content
    return content[:insert_at] + injection + content[insert_at:]


def build_signs_entry_with_angles(sign_name: str, sign_data: dict) -> str:
    """
    Build SIGNS entry using real extracted arm angles.
    Format: NAME: [[rF],'custom',[lF],'custom', headTilt, rAngles, lAngles]
    where rAngles = [upperArm_x, upperArm_z, foreArm_x, hand_z]
    """
    r_fingers = sign_data["r_fingers"]
    l_fingers = sign_data["l_fingers"]
    r_angles  = sign_data["r_angles"]
    l_angles  = sign_data.get("l_angles") or {"upperArm_x":0,"upperArm_z":0,"foreArm_x":0,"hand_z":0}

    r_js = fingers_to_js(r_fingers)
    l_js = fingers_to_js(l_fingers)

    # [upperArm_x, upperArm_z, foreArm_x, hand_z, hand_y]
    # hand_y = palm flip angle (0=palm toward camera, PI=back of hand)
    r_ang = [r_angles["upperArm_x"], r_angles["upperArm_z"],
             r_angles["foreArm_x"],  r_angles.get("hand_z", 0),
             r_angles.get("hand_y", 0)]
    l_ang = [l_angles["upperArm_x"], l_angles["upperArm_z"],
             l_angles["foreArm_x"],  l_angles.get("hand_z", 0),
             l_angles.get("hand_y", 0)]

    padded  = f"{sign_name}:"
    padding = max(1, 11 - len(padded))

    return (
        f"  {padded}{' ' * padding}"
        f"[[{r_js}],'custom', [{l_js}],'custom',  0, "
        f"{r_ang}, {l_ang}],"
        f"  // ISLRTC pose+palm verified"
    )


# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print("[PHASE 5] Updating avatar_3d.html SIGNS with verified ISL data\n")

    if not INPUT_JSON.exists():
        print("[ERROR] extracted_signs.json not found.")
        print("  Run pose/mediapipe_extractor.py first.")
        return

    with open(INPUT_JSON, encoding="utf-8") as f:
        signs = json.load(f)

    print(f"[INFO] {len(signs)} verified signs to apply\n")

    # Print summary table
    print(f"  {'SIGN':<12} {'R_FINGERS':<38} {'SHAPE':<12} {'LOC'}")
    print(f"  {'-'*75}")
    for s in signs:
        s2    = apply_fallback_if_needed(s)
        shape = classify_hand_shape(s2["r_fingers"])
        src   = " ← FALLBACK" if s2.get("source") == "ISLRTC_manual_fallback" else ""
        print(f"  {s2['sign']:<12} {str(s2['r_fingers']):<38} {shape:<12} {s2['r_location']}{src}")

    print()
    patch_avatar_html(signs)


if __name__ == "__main__":
    run()