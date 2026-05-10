"""
ISL Pipeline — Phase 5: Live Sign Visualiser
Shows MediaPipe hand landmarks overlaid on video while extracting.
Useful for verifying extraction quality before patching motion_mapper.py

Usage:
  python pose/visualise_extraction.py pose/videos/hello.mp4
"""

import cv2
import sys
import numpy as np
from pathlib import Path

WRIST      = 0
THUMB_MCP  = 2;  THUMB_TIP  = 4
INDEX_MCP  = 5;  INDEX_TIP  = 8
MIDDLE_MCP = 9;  MIDDLE_TIP = 12
RING_MCP   = 13; RING_TIP   = 16
PINKY_MCP  = 17; PINKY_TIP  = 20


def ext(tip, mcp, wrist):
    t = np.array([tip.x, tip.y, tip.z])
    m = np.array([mcp.x, mcp.y, mcp.z])
    w = np.array([wrist.x, wrist.y, wrist.z])
    r = np.linalg.norm(t - w) / (np.linalg.norm(m - w) + 1e-6)
    return float(np.clip((r - 1.0) / 1.5, 0.0, 1.0))


def draw_hand_info(frame, lm, hand_label):
    fingers = [
        ext(lm[THUMB_TIP],  lm[THUMB_MCP],  lm[WRIST]),
        ext(lm[INDEX_TIP],  lm[INDEX_MCP],  lm[WRIST]),
        ext(lm[MIDDLE_TIP], lm[MIDDLE_MCP], lm[WRIST]),
        ext(lm[RING_TIP],   lm[RING_MCP],   lm[WRIST]),
        ext(lm[PINKY_TIP],  lm[PINKY_MCP],  lm[WRIST]),
    ]
    names = ["T", "I", "M", "R", "P"]
    y_off = 30 if hand_label == "Right" else 160
    cv2.putText(frame, f"{hand_label} hand:", (10, y_off),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    for j, (name, val) in enumerate(zip(names, fingers)):
        bar_w = int(val * 100)
        cv2.rectangle(frame, (10, y_off + 15 + j * 22),
                      (10 + bar_w, y_off + 30 + j * 22), (0, 200, 100), -1)
        cv2.putText(frame, f"{name}:{val:.2f}",
                    (115, y_off + 28 + j * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return fingers


def draw_connections(frame, lm, h, w):
    """Draw hand skeleton manually."""
    connections = [
        (0,1),(1,2),(2,3),(3,4),           # thumb
        (0,5),(5,6),(6,7),(7,8),           # index
        (0,9),(9,10),(10,11),(11,12),      # middle
        (0,13),(13,14),(14,15),(15,16),    # ring
        (0,17),(17,18),(18,19),(19,20),    # pinky
        (5,9),(9,13),(13,17),              # palm
    ]
    pts = [(int(lm[i].x * w), int(lm[i].y * h)) for i in range(21)]
    for a, b in connections:
        cv2.line(frame, pts[a], pts[b], (0, 200, 100), 2)
    for pt in pts:
        cv2.circle(frame, pt, 4, (0, 255, 150), -1)


def run(video_path: str):
    try:
        import mediapipe as mp
    except ImportError:
        print("Run: pip install mediapipe opencv-python")
        sys.exit(1)

    model_path = Path(__file__).parent / "hand_landmarker.task"
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # ── New Tasks API ─────────────────────────────────────────────────────────
    try:
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision
        import urllib.request

        if not model_path.exists():
            print("Downloading hand landmark model (~8MB)...")
            urllib.request.urlretrieve(
                "https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
                str(model_path)
            )

        options = mp_vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

        frame_idx = 0
        with mp_vision.HandLandmarker.create_from_options(options) as det:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                ts     = int(frame_idx * 1000 / fps)
                result = det.detect_for_video(mp_img, ts)

                if result.hand_landmarks and result.handedness:
                    for lm_list, handed in zip(result.hand_landmarks, result.handedness):
                        label = handed[0].category_name
                        draw_connections(frame, lm_list, h, w)
                        draw_hand_info(frame, lm_list, label)

                cv2.imshow("ISL Pose Extractor (new API) — press Q to quit", frame)
                if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
                    break
                frame_idx += 1

    except (AttributeError, ImportError):
        # ── Legacy API fallback ────────────────────────────────────────────────
        mp_hands   = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        mp_styles  = mp.solutions.drawing_styles

        with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.65) as hands:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(rgb)

                if result.multi_hand_landmarks and result.multi_handedness:
                    for lm_set, handedness in zip(
                        result.multi_hand_landmarks, result.multi_handedness
                    ):
                        lm    = lm_set.landmark
                        label = handedness.classification[0].label
                        mp_drawing.draw_landmarks(
                            frame, lm_set, mp_hands.HAND_CONNECTIONS,
                            mp_styles.get_default_hand_landmarks_style(),
                            mp_styles.get_default_hand_connections_style()
                        )
                        draw_hand_info(frame, lm, label)

                cv2.imshow("ISL Pose Extractor (legacy) — press Q to quit", frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pose/visualise_extraction.py pose/videos/hello.mp4")
        sys.exit(1)
    run(sys.argv[1])