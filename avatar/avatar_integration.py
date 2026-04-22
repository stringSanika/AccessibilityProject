"""
ISL Pipeline — Phase 4: Avatar Integration
Reads motion_sequence.json and drives a Blender-rigged avatar to perform
ISL signs in sequence.

TWO USAGE MODES:

  Mode A — Inside Blender (bpy available):
    Open Blender → Scripting workspace → Run this file.
    The avatar in the active scene will animate.

  Mode B — Standalone preview (no Blender):
    Run from terminal:  python avatar_integration.py
    Prints a timeline of the motion sequence for debugging.
    Also generates avatar_timeline.json for inspection.

Requirements (Mode A):
  - Blender 3.x or 4.x with Python scripting enabled
  - A .blend file with a rigged humanoid avatar loaded
  - Bone names matching BONE_MAP below (edit to match your rig)

Requirements (Mode B / standalone):
  - No extra dependencies beyond Python stdlib + json
"""

import json
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR       = Path(__file__).parent
INPUT_PATH     = BASE_DIR.parent / "motion" / "motion_sequence.json"
TIMELINE_PATH  = BASE_DIR / "avatar_timeline.json"

# ── Rig bone name map ──────────────────────────────────────────────────────────
# Edit these to match the actual bone names in your .blend rig.
# Common naming conventions: Mixamo uses "mixamorig:RightHand" etc.

BONE_MAP = {
    # Spine / head
    "spine":            "mixamorig:Spine",
    "neck":             "mixamorig:Neck",
    "head":             "mixamorig:Head",

    # Right arm (dominant hand for ISL)
    "r_shoulder":       "mixamorig:RightShoulder",
    "r_upper_arm":      "mixamorig:RightArm",
    "r_forearm":        "mixamorig:RightForeArm",
    "r_hand":           "mixamorig:RightHand",

    # Right hand fingers
    "r_thumb_1":        "mixamorig:RightHandThumb1",
    "r_thumb_2":        "mixamorig:RightHandThumb2",
    "r_index_1":        "mixamorig:RightHandIndex1",
    "r_index_2":        "mixamorig:RightHandIndex2",
    "r_middle_1":       "mixamorig:RightHandMiddle1",
    "r_middle_2":       "mixamorig:RightHandMiddle2",
    "r_ring_1":         "mixamorig:RightHandRing1",
    "r_pinky_1":        "mixamorig:RightHandPinky1",

    # Left arm (non-dominant / support hand)
    "l_shoulder":       "mixamorig:LeftShoulder",
    "l_upper_arm":      "mixamorig:LeftArm",
    "l_forearm":        "mixamorig:LeftForeArm",
    "l_hand":           "mixamorig:LeftHand",
}

# ── Keyframe timing ────────────────────────────────────────────────────────────

FPS = 24   # Blender scene FPS — match your .blend setting

def seconds_to_frame(seconds: float, fps: int = FPS) -> int:
    return int(seconds * fps)

# ── Hand shape presets ─────────────────────────────────────────────────────────
# Each preset is a dict of {bone_key: (rx, ry, rz)} Euler rotations in degrees.
# These are placeholder values — calibrate with your actual rig in Blender.
# Positive X = curl finger inward, Negative X = extend.

HAND_SHAPES: dict[str, dict[str, tuple]] = {
    "rest": {
        "r_index_1": (0, 0, 0), "r_middle_1": (0, 0, 0),
        "r_ring_1":  (0, 0, 0), "r_pinky_1":  (0, 0, 0),
        "r_thumb_1": (0, 0, 0),
    },
    "flat_b": {
        "r_index_1": (-5, 0, 0),  "r_middle_1": (-5, 0, 0),
        "r_ring_1":  (-5, 0, 0),  "r_pinky_1":  (-5, 0, 0),
        "r_thumb_1": (30, 0, 0),
    },
    "index_1": {
        "r_index_1": (0, 0, 0),   "r_middle_1": (80, 0, 0),
        "r_ring_1":  (80, 0, 0),  "r_pinky_1":  (80, 0, 0),
        "r_thumb_1": (40, 0, 0),
    },
    "open_5": {
        "r_index_1": (-10, 0, 0), "r_middle_1": (-10, 0, 0),
        "r_ring_1":  (-10, 0, 0), "r_pinky_1":  (-10, 0, 0),
        "r_thumb_1": (-10, 0, 0),
    },
    "s_fist": {
        "r_index_1": (90, 0, 0),  "r_middle_1": (90, 0, 0),
        "r_ring_1":  (90, 0, 0),  "r_pinky_1":  (90, 0, 0),
        "r_thumb_1": (40, 0, 20),
    },
    "bent_5": {
        "r_index_1": (45, 0, 0),  "r_middle_1": (45, 0, 0),
        "r_ring_1":  (45, 0, 0),  "r_pinky_1":  (45, 0, 0),
        "r_thumb_1": (20, 0, 0),
    },
    "v_hand": {
        "r_index_1": (0, 0, 0),   "r_middle_1": (0, 0, 0),
        "r_ring_1":  (85, 0, 0),  "r_pinky_1":  (85, 0, 0),
        "r_thumb_1": (40, 0, 0),
    },
    "fingerspell": {   # placeholder — fingerspell handled per-letter in real impl
        "r_index_1": (0, 0, 0),   "r_middle_1": (0, 0, 0),
        "r_ring_1":  (0, 0, 0),   "r_pinky_1":  (0, 0, 0),
        "r_thumb_1": (0, 0, 0),
    },
}

# ── Blender mode (bpy) ─────────────────────────────────────────────────────────

def apply_hand_shape_blender(armature, shape_name: str, frame: int) -> None:
    """
    Set finger bone rotations for the given hand shape and insert keyframes.
    Call this from inside Blender with bpy available.
    """
    import bpy
    import mathutils

    shape = HAND_SHAPES.get(shape_name, HAND_SHAPES["rest"])
    pose  = armature.pose

    for bone_key, (rx, ry, rz) in shape.items():
        bone_name = BONE_MAP.get(bone_key)
        if bone_name and bone_name in pose.bones:
            bone = pose.bones[bone_name]
            bone.rotation_mode = "XYZ"
            import math
            bone.rotation_euler = mathutils.Euler(
                (math.radians(rx), math.radians(ry), math.radians(rz)), "XYZ"
            )
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)


def run_in_blender(motion_data: list[dict]) -> None:
    """
    Drive the avatar inside Blender.
    Expects the active object in the scene to be the rigged armature.
    """
    import bpy

    scene    = bpy.context.scene
    scene.render.fps = FPS
    armature = bpy.context.active_object

    if armature is None or armature.type != "ARMATURE":
        print("[AVATAR] ERROR: Select the armature object before running.")
        return

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")

    current_frame = 1

    for segment in motion_data:
        print(f"[AVATAR] Segment {segment['id']}: {segment['gloss']}")

        for sign in segment["motion"]:
            shape     = sign.get("hand_shape", "rest")
            duration  = sign.get("duration",   0.5)
            frames    = seconds_to_frame(duration)

            # Set pose at start of sign
            apply_hand_shape_blender(armature, shape, current_frame)

            # Hold pose, then return to rest
            current_frame += frames
            apply_hand_shape_blender(armature, "rest", current_frame)

    scene.frame_end = current_frame
    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"[AVATAR] Animation complete — {current_frame} frames ({current_frame/FPS:.1f}s)")

# ── Standalone preview mode ────────────────────────────────────────────────────

def preview_timeline(motion_data: list[dict]) -> None:
    """
    Print a readable timeline and save avatar_timeline.json.
    Use this to verify motion output before opening Blender.
    """
    timeline = []
    t = 0.0

    print("\n[AVATAR] Motion timeline preview")
    print(f"{'Time':>8}  {'Token':20}  {'Shape':18}  {'Movement':30}  {'Dur':>5}")
    print("─" * 90)

    for segment in motion_data:
        print(f"\n  ── Segment {segment['id']}: \"{segment['clean']}\"")
        print(f"     Gloss: {segment['gloss']}")

        for sign in segment["motion"]:
            token    = sign.get("token",      "?")
            shape    = sign.get("hand_shape", "?")
            movement = sign.get("movement",   "?")
            dur      = sign.get("duration",   0.0)
            location = sign.get("location",   "?")
            nm       = sign.get("non_manual", "")

            print(f"  {t:>7.2f}s  {token:20}  {shape:18}  {movement:30}  {dur:>5.2f}s")

            timeline.append({
                "time":       round(t, 2),
                "token":      token,
                "hand_shape": shape,
                "movement":   movement,
                "location":   location,
                "duration":   dur,
                "non_manual": nm,
                "frame":      seconds_to_frame(t),
            })
            t += dur

    total = round(t, 2)
    print(f"\n  Total animation duration: {total}s  ({seconds_to_frame(total)} frames @ {FPS}fps)")

    TIMELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE_PATH.write_text(
        json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[AVATAR] Saved: {TIMELINE_PATH}")

# ── Entry point ────────────────────────────────────────────────────────────────

def load_motion_data(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"motion_sequence.json not found at {path}\n"
            "Run motion/motion_mapper.py first."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    motion_data = load_motion_data(INPUT_PATH)

    # Detect whether we're running inside Blender
    try:
        import bpy   # noqa: F401
        print("[AVATAR] Blender detected — running in animation mode")
        run_in_blender(motion_data)
    except ImportError:
        print("[AVATAR] Running in standalone preview mode (no Blender)")
        preview_timeline(motion_data)
        print("[AVATAR] Phase 4 preview complete")
