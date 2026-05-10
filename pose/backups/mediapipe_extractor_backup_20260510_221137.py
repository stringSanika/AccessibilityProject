"""
ISL Pipeline — Phase 5: MediaPipe Full Pose Extractor (Tasks API version)
Works with MediaPipe >= 0.10 (Tasks API only — no mp.solutions needed)

Extracts:
  1. Finger extension values  → from HandLandmarker
  2. Arm rotation angles      → from PoseLandmarker (shoulder/elbow/wrist)

Usage:
  python pose/mediapipe_extractor.py
"""

import cv2, json, numpy as np, subprocess, sys, urllib.request
from pathlib import Path

BASE_DIR    = Path(__file__).parent
VIDEOS_DIR  = BASE_DIR / "videos"
OUTPUT_JSON = BASE_DIR / "extracted_signs.json"
VIDEOS_DIR.mkdir(exist_ok=True)

HAND_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)
HAND_MODEL = BASE_DIR / "hand_landmarker.task"
POSE_MODEL = BASE_DIR / "pose_landmarker.task"

# ── ISLRTC URLs ────────────────────────────────────────────────────────────────
ISLRTC_SIGNS = {
    "HELLO":    "https://youtu.be/yBQA3coUjH0?si=vJ13mTh-C2aDtrVw",
    "GOODBYE":  "https://youtu.be/O6YJgD20e2g?si=wNwpkFtr_PfXJ3vK",
    "KNOW":     "https://youtu.be/jTBahbE4_OY?si=AYvd_B4eEOGi9_mi",
    "LEARN":    "https://youtu.be/MAZVS8doD6E?si=9Vgitd-MmDnbTq4X",
    "TEACH":    "https://youtu.be/Brqv7-rpdTQ?si=zE07WH7KBImbp7Oi",
    "HAVE":     "https://youtu.be/RorIn-P_3DI?si=qKbfd_gfjqj3ZVv0",
    "WORK":     "https://youtu.be/FlZ8Xekr-JA?si=klMpsgApkg6ukHtP",
    "GOOD":     "https://youtu.be/aQEJlg8RhXQ?si=JfPtJBqoPP5kM-2s",
    "BAD":      "https://youtu.be/l8lwU4wIOz4?si=mPPj4bAcDJW8OPzh",
    "NOT":      "https://youtu.be/BEEOC2ZXhsg?si=C4Un2ass4vPHQuEP",
    "I":        "https://youtu.be/1f6OchgCQrE?si=Nq3Gx_GL967-IaWn",
    "YOU":      "https://youtu.be/QE4UkDB3MyE?si=MW6wuUIQ1vk6s2sQ",
    "EXCITED":  "https://youtu.be/fe3uPTqXfxQ?si=_9daI3IRj4vFEH_8",
}

# MediaPipe Pose landmark indices (body landmarks)
R_SHOULDER, R_ELBOW, R_WRIST = 12, 14, 16
L_SHOULDER, L_ELBOW, L_WRIST = 11, 13, 15

# MediaPipe Hand landmark indices
WRIST=0; THUMB_MCP=2; THUMB_TIP=4
INDEX_MCP=5;  INDEX_TIP=8
MIDDLE_MCP=9; MIDDLE_TIP=12
RING_MCP=13;  RING_TIP=16
PINKY_MCP=17; PINKY_TIP=20

# ── Download helpers ───────────────────────────────────────────────────────────

def download_model(url, path):
    if path.exists():
        return
    print(f"  [DOWNLOAD] Model {path.name}...")
    urllib.request.urlretrieve(url, str(path))
    print(f"  [OK] {path.name}")

def download_video(sign_name, url):
    out = VIDEOS_DIR / f"{sign_name.lower()}.mp4"
    if out.exists():
        print(f"  [SKIP] {out.name} already downloaded")
        return out
    print(f"  [DOWNLOAD] {sign_name} ← {url}")
    r = subprocess.run(["yt-dlp", "-f", "mp4", "-o", str(out), url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERROR] {r.stderr[:200]}")
        return None
    print(f"  [OK] {out.name}")
    return out

# ── Finger extension ───────────────────────────────────────────────────────────

def finger_ext(tip, mcp, wrist):
    """Multi-method finger extension: handles all camera angles."""
    t = np.array([tip.x, tip.y, tip.z])
    m = np.array([mcp.x, mcp.y, mcp.z])
    w = np.array([wrist.x, wrist.y, wrist.z])
    r1 = float(np.clip((np.linalg.norm(t-w)/(np.linalg.norm(m-w)+1e-6)-1)/1.5, 0,1))
    r2 = float(np.clip((wrist.z - tip.z)/0.08, 0, 1))
    r3 = float(np.clip((np.linalg.norm(t[:2]-w[:2])/(np.linalg.norm(m[:2]-w[:2])+1e-6)-1)/1.2, 0,1))
    return max(r1, r2, r3)

# ── Arm angle extraction from Pose ────────────────────────────────────────────

def extract_arm_angles(landmarks, side='R'):
    """
    Convert shoulder/elbow/wrist positions → Three.js arm rotation values.

    KEY FORMULA (corrected):
    - elevation = arccos(u[1] / |u|): angle of upper arm from "straight down"
      MediaPipe y increases downward, so y component of arm vector = cos(elevation_from_down)
      elevation=0 → arm straight down → Three.js x=0
      elevation=PI → arm straight up  → Three.js x≈-2.5
    - Three.js upperArm.rotation.x = -elevation * 0.75
    """
    if side == 'R':
        sh, el, wr = landmarks[R_SHOULDER], landmarks[R_ELBOW], landmarks[R_WRIST]
        s = 1
    else:
        sh, el, wr = landmarks[L_SHOULDER], landmarks[L_ELBOW], landmarks[L_WRIST]
        s = -1

    u = np.array([el.x-sh.x, el.y-sh.y, el.z-sh.z])  # shoulder→elbow
    f = np.array([wr.x-el.x, wr.y-el.y, wr.z-el.z])  # elbow→wrist

    # ── upperArm.rotation.x ───────────────────────────────────────────────────
    # Elevation of arm from straight-down (MediaPipe: y increases downward)
    n_u = max(np.linalg.norm(u), 1e-6)
    cos_e = np.clip(u[1] / n_u, -1, 1)   # u[1]/|u| = cos(angle from down)
    elevation = np.arccos(cos_e)           # 0=arm down, PI=arm up

    # Forward boost: arm pointing toward camera (sh.z > el.z) → more "raised"
    fwd_boost = max(sh.z - el.z, 0) * 4.0
    elevation = min(elevation + fwd_boost * 0.3, np.pi)

    ux = float(np.clip(-elevation * 1.0, -2.8, 0.0))

    # ── upperArm.rotation.z ───────────────────────────────────────────────────
    # Arm lateral angle (how far out from body)
    body_w = max(abs(landmarks[R_SHOULDER].x - landmarks[L_SHOULDER].x), 0.15)
    # For right arm: arm going outward = el.x < sh.x (signer faces camera, x flipped)
    lat = abs((el.x - sh.x) / body_w)
    uz = float(np.clip(-lat * 0.8, -1.1, 0.0)) * s

    # ── foreArm.rotation.x ────────────────────────────────────────────────────
    # Elbow bend angle between upper arm and forearm vectors
    n_f = max(np.linalg.norm(f), 1e-6)
    cos_b = np.clip(np.dot(u, f) / (n_u * n_f), -1, 1)
    bend = np.arccos(cos_b)               # 0=straight arm, PI=fully folded
    fx = float(np.clip(-bend * 0.85, -2.5, 0.0))

    # ── hand.rotation.z ───────────────────────────────────────────────────────
    # Wrist rotation from forearm direction in horizontal plane
    hz = float(np.clip(
        s * np.arctan2(-f[0]*s, max(abs(f[2]), 0.01)) * 0.3,
        -1.5, 1.5
    ))

    return {
        "upperArm_x": round(ux, 3),
        "upperArm_z": round(uz, 3),
        "foreArm_x":  round(fx, 3),
        "hand_z":     round(hz, 3),
    }

def compute_palm_angles(lm_list, s):
    """
    Compute Three.js hand rotation from palm orientation.
    Uses cross product of hand vectors to find which way the palm faces.

    MediaPipe right hand, palm facing camera → normal.z > 0
    hand.rotation.y = arccos(normal.z): 0=palm faces camera, PI=back of hand
    hand.rotation.z = lateral wrist rotation (inward/outward)
    """
    w  = np.array([lm_list[0].x,  lm_list[0].y,  lm_list[0].z])   # wrist
    i5 = np.array([lm_list[5].x,  lm_list[5].y,  lm_list[5].z])   # index MCP
    p17= np.array([lm_list[17].x, lm_list[17].y, lm_list[17].z])  # pinky MCP
    i8 = np.array([lm_list[8].x,  lm_list[8].y,  lm_list[8].z])   # index tip

    v1 = i5  - w   # wrist → index knuckle (radial direction)
    v2 = p17 - w   # wrist → pinky knuckle (ulnar direction)

    # Palm normal: for right hand palm facing camera, n.z > 0
    n = np.cross(v1, v2)
    nl = np.linalg.norm(n)
    if nl < 1e-6:
        return 0.0, 0.0
    n = n / nl

    # hand.rotation.y: palm flip
    # n.z=+1 (palm facing camera) → hand_y = 0
    # n.z=-1 (back to camera)    → hand_y = PI
    hand_y = float(np.arccos(np.clip(n[2], -1, 1))) * s

    # hand.rotation.z: wrist rotation (inward = toward body center)
    # index tip x relative to wrist x tells us pointing direction
    point_dir = (i8[0] - w[0]) * s   # negative = pointing toward body center
    hand_z = float(np.clip(-point_dir * 8.0, -2.5, 2.5))

    return round(hand_y, 3), round(hand_z, 3)


def wrist_y_to_location(y):
    if y < 0.22: return "raised"
    if y < 0.35: return "forehead"
    if y < 0.44: return "temple"
    if y < 0.52: return "chin"
    if y < 0.62: return "chest"
    if y < 0.72: return "neutral"
    return "wrist"

# ── Main extraction ────────────────────────────────────────────────────────────

def extract_sign(video_path, sign_name):
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision

    download_model(HAND_MODEL_URL, HAND_MODEL)
    download_model(POSE_MODEL_URL, POSE_MODEL)

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"  [INFO] {total} frames @ {fps:.1f}fps")

    pose_data = []
    hand_data = []

    # ── Run Pose ──────────────────────────────────────────────────────────────
    pose_opts = mp_vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(POSE_MODEL)),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    with mp_vision.PoseLandmarker.create_from_options(pose_opts) as det:
        fi = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts     = int(fi * 1000 / fps)
            result = det.detect_for_video(mp_img, ts)
            if result.pose_landmarks:
                lm = result.pose_landmarks[0]
                try:
                    r_ang = extract_arm_angles(lm, 'R')
                    l_ang = extract_arm_angles(lm, 'L')
                    pose_data.append({
                        "r_angles": r_ang,
                        "l_angles": l_ang,
                        "r_wrist_y": round(lm[R_WRIST].y, 3),
                    })
                except Exception as e:
                    pass
            fi += 1
    print(f"  [POSE]  {len(pose_data)} frames detected")

    # ── Run Hands ─────────────────────────────────────────────────────────────
    hand_opts = mp_vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(HAND_MODEL)),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    with mp_vision.HandLandmarker.create_from_options(hand_opts) as det:
        fi = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts     = int(fi * 1000 / fps)
            result = det.detect_for_video(mp_img, ts)
            if result.hand_landmarks and result.handedness:
                for lm_list, handed in zip(result.hand_landmarks, result.handedness):
                    lm    = lm_list
                    hand  = handed[0].category_name
                    score = handed[0].score
                    if score < 0.6: continue
                    s_hand = 1 if hand == "Right" else -1
                    hy, hz = compute_palm_angles(lm, s_hand)
                    hand_data.append({
                        "hand": hand,
                        "wrist_y": round(lm[WRIST].y, 3),
                        "fingers": [
                            round(finger_ext(lm[THUMB_TIP],  lm[THUMB_MCP],  lm[WRIST]), 2),
                            round(finger_ext(lm[INDEX_TIP],  lm[INDEX_MCP],  lm[WRIST]), 2),
                            round(finger_ext(lm[MIDDLE_TIP], lm[MIDDLE_MCP], lm[WRIST]), 2),
                            round(finger_ext(lm[RING_TIP],   lm[RING_MCP],   lm[WRIST]), 2),
                            round(finger_ext(lm[PINKY_TIP],  lm[PINKY_MCP],  lm[WRIST]), 2),
                        ],
                        "hand_y": hy,
                        "hand_z": hz,
                    })
            fi += 1
    cap.release()
    print(f"  [HANDS] {len(hand_data)} frames detected")

    return _summarise(sign_name, pose_data, hand_data)

def _stable(lst, key_fn):
    if not lst: return None
    n = len(lst); s = lst[n//4:3*n//4] if n>4 else lst
    return np.mean([key_fn(x) for x in s], axis=0).tolist()

def _summarise(sign_name, pose_data, hand_data):
    r_h = [f for f in hand_data if f["hand"]=="Right"]
    l_h = [f for f in hand_data if f["hand"]=="Left"]

    def avg_f(lst):
        if not lst: return [0.5]*5
        n=len(lst); s=lst[n//4:3*n//4] if n>4 else lst
        return np.mean([x["fingers"] for x in s],axis=0).round(2).tolist()

    r_fingers = avg_f(r_h)
    l_fingers = avg_f(l_h) if l_h else [0.5]*5

    # ── Palm orientation from HandLandmarker ──────────────────────────────────
    def avg_palm(lst, key):
        if not lst: return 0.0
        n=len(lst); s=lst[n//4:3*n//4] if n>4 else lst
        vals = [f.get(key, 0.0) for f in s if key in f]
        return float(np.mean(vals)) if vals else 0.0

    r_hand_y = round(avg_palm(r_h, "hand_y"), 3)
    r_hand_z = round(avg_palm(r_h, "hand_z"), 3)
    l_hand_y = round(avg_palm(l_h, "hand_y"), 3) if l_h else 0.0
    l_hand_z = round(avg_palm(l_h, "hand_z"), 3) if l_h else 0.0

    if pose_data:
        n = len(pose_data)

        # ── Use PEAK frames (highest arm elevation) not middle-50% by time ──
        # This captures the canonical sign position, not the average of
        # transitions in and out of the sign.
        #
        # Sort by absolute upperArm_x (more negative = arm raised higher)
        by_elevation = sorted(pose_data, key=lambda f: abs(f["r_angles"]["upperArm_x"]),
                              reverse=True)
        # Use top 30% most elevated frames (peak of the sign gesture)
        peak = by_elevation[:max(3, n // 3)]

        r_ang = {k: round(float(np.mean([f["r_angles"][k] for f in peak])),3)
                 for k in ["upperArm_x","upperArm_z","foreArm_x","hand_z"]}
        l_ang = {k: round(float(np.mean([f["l_angles"][k] for f in peak])),3)
                 for k in ["upperArm_x","upperArm_z","foreArm_x","hand_z"]}

        # Override hand_z with palm orientation from HandLandmarker (more accurate)
        # Also add hand_y (palm flip) from HandLandmarker
        r_ang["hand_z"] = r_hand_z
        r_ang["hand_y"] = r_hand_y
        l_ang["hand_z"] = l_hand_z
        l_ang["hand_y"] = l_hand_y

        # Location from middle frames (more stable for wrist height)
        mid = pose_data[n//4:3*n//4] if n>4 else pose_data
        r_wy  = float(np.mean([f["r_wrist_y"] for f in mid]))
        r_loc = wrist_y_to_location(r_wy)
    else:
        r_ang = None; l_ang = None
        r_wy  = float(np.mean([f["wrist_y"] for f in r_h])) if r_h else 0.6
        r_loc = wrist_y_to_location(r_wy)

    result = {
        "sign":        sign_name.upper(),
        "r_fingers":   r_fingers,
        "l_fingers":   l_fingers,
        "r_location":  r_loc,
        "l_location":  "neutral",
        "r_angles":    r_ang,
        "l_angles":    l_ang,
        "source":      "ISLRTC_pose_verified",
        "pose_frames": len(pose_data),
        "hand_frames": len(hand_data),
    }
    print(f"  [RESULT] {sign_name:10s}  R:{r_fingers}  loc={r_loc}")
    if r_ang:
        print(f"  [ANGLES] uArm(x={r_ang['upperArm_x']:.2f},z={r_ang['upperArm_z']:.2f}) "
              f"fArm(x={r_ang['foreArm_x']:.2f}) hand_z={r_ang['hand_z']:.2f}")
    return result

# ── Entry point ────────────────────────────────────────────────────────────────

def run():
    print("[PHASE 5] ISL Pose Extraction — MediaPipe Tasks API (Pose + Hands)\n")
    results = {}

    if OUTPUT_JSON.exists():
        old = json.loads(OUTPUT_JSON.read_text())
        for r in old:
            results[r["sign"]] = r
        print(f"[INFO] {len(results)} existing signs loaded\n")

    for sign_name, url in ISLRTC_SIGNS.items():
        up = sign_name.upper()
        print(f"── {up} {'─'*(38-len(up))}")
        if up in results and results[up].get("r_angles"):
            print(f"  [SKIP] Already extracted with pose data")
            print()
            continue
        vp = download_video(sign_name, url)
        if vp is None or not vp.exists():
            print(f"  [SKIP] Download failed\n")
            continue
        data = extract_sign(vp, sign_name)
        if data:
            results[up] = data
        print()

    out = list(results.values())
    OUTPUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"[PHASE 5] Saved {len(out)} signs → {OUTPUT_JSON}")
    print("[PHASE 5] Now run: python pose/update_avatar.py")

if __name__ == "__main__":
    run()