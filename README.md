# Accessibility-Project — Real-Time Lecture to ISL Translator

> Converts live lecture audio into **Indian Sign Language (ISL)** using a modular pipeline of speech recognition, linguistic transformation, and avatar-based sign rendering,  making academic lectures accessible to Deaf and hard-of-hearing students.

---

## Pipeline Overview

```
Lecture Video (MP4)
       │
       ▼
  FFmpeg (audio extraction)
       │
       ▼
  Whisper ASR  ──────────────────────► segments.json
  (speech → timestamped text)          (text + timestamps)
       │
       ▼
  Gloss Converter ───────────────────► gloss_output.json
  (English → ISL gloss)                (OSV reordered gloss)
  Rule-based + ISL grammar rules
       │
       ▼
  Motion Mapper ─────────────────────► motion_sequence.json
  (gloss → hand shape descriptors)     (hand shape + movement + location)
       │
       ▼
  Avatar Renderer
  (3D browser avatar / Blender)
```

Each stage communicates only through JSON -- **loosely coupled**, so any component can be upgraded independently.

---

## Features

- **Real-time capable** : 3-5 second latency window per segment
- **ISL grammar rules** : OSV reordering, auxiliary verb dropping, negation and WH-word placement
- **Motion library** : 50+ ISL signs mapped to hand shape descriptors
- **3D browser avatar** : Three.js avatar with finger bone animation, no installation needed
- **Modular architecture** : swap ASR, NLP, or avatar layer independently

---

## Project Structure

```
Accessibility-Project/
├── asr/
│   ├── asr_isl.py              # Whisper ASR -- audio → segments.json
│   ├── audio.wav               # Extracted lecture audio
│   └── lecture.mp4             # Source lecture video
│
├── nlp/
│   └── gloss_converter.py      # English → ISL gloss converter
│
├── motion/
│   └── motion_mapper.py        # Gloss → motion descriptor mapper
│
├── avatar/
│   ├── avatar_integration.py   # Blender Python API integration
│   └── avatar_3d.html          # Browser 3D avatar (Three.js)
│
├── demo_viewer.html            # Full pipeline demo viewer
└── README.md
```

---

## Setup

### Requirements

```bash
Python 3.9+
pip install openai-whisper librosa numpy
```

FFmpeg must be installed separately:
- Windows: https://ffmpeg.org/download.html
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### Run the pipeline

```bash
# Step 1 — Extract audio from lecture video (FFmpeg)
ffmpeg -i asr/lecture.mp4 -ar 16000 -ac 1 asr/audio.wav

# Step 2 — Transcribe audio with Whisper
cd asr
python asr_isl.py

# Step 3 — Convert to ISL gloss
cd ../nlp
python gloss_converter.py

# Step 4 — Map to motion descriptors
cd ../motion
python motion_mapper.py

# Step 5 — Open demo in browser
# Open demo_viewer.html or avatar/avatar_3d.html
# Load nlp/gloss_output.json when prompted
```

---

## How It Works

### 1. ASR -- `asr/asr_isl.py`
Uses **OpenAI Whisper** (base model) to transcribe lecture audio into timestamped segments. Audio is resampled to 16kHz mono using librosa before inference. Filler words (uh, um, like) are stripped and output is saved as structured JSON.

**Evaluation metric:** Word Error Rate (WER)

### 2. Gloss Conversion -- `nlp/gloss_converter.py`
Converts cleaned English text to ISL gloss notation using rule-based linguistic transformation:

| Rule | Example |
|------|---------|
| OSV reordering | "I explain neural networks" → `NEURAL NETWORKS I EXPLAIN` |
| Drop aux verbs | "am, is, are, do, does" → dropped |
| Drop articles | "the, a, an" → dropped |
| NOT to end | "I do not know" → `KNOW I NOT` |
| WH-word to end | "Where are you going?" → `YOU GO WHERE` |

**Evaluation metric:** BLEU score against human-annotated ISL gloss

### 3. Motion Mapping -- `motion/motion_mapper.py`
Maps each gloss token to a structured motion descriptor:

```json
{
  "token": "KNOW",
  "hand_shape": "flat_b",
  "movement": "tap_temple",
  "location": "temple",
  "duration": 0.6,
  "non_manual": "neutral"
}
```

Library covers 50+ common ISL signs. Unknown tokens fall back to fingerspelling.

### 4. Avatar Rendering
Two rendering modes:

**Browser (Three.js)** -- `avatar/avatar_3d.html`
Full upper body 3D avatar with articulated finger bones. Runs in any browser, no installation needed. Load `gloss_output.json` to drive the animation.

**Blender** -- `avatar/avatar_integration.py`
Drives a Mixamo-rigged armature using the Blender Python API. Run from Blender's Scripting workspace with a rigged `.blend` file loaded.

---

## Limitations & Future Work

| Limitation | Planned Fix |
|------------|-------------|
| Rule-based gloss conversion | Replace with Seq2Seq transformer trained on English-ISL corpus |
| Whisper struggles with Indian accents | Fine-tune on Indian English academic speech / integrate Bhashini ASR |
| ~50 signs in motion library | Expand with pose estimation from ISL video corpus |
| No non-manual marker animation | Add facial expression blend shapes to avatar |
| Single speaker | Multi-speaker diarization |

---

## Tech Stack

| Component | Tool |
|-----------|------|
| Audio extraction | FFmpeg |
| Speech recognition | OpenAI Whisper |
| Audio processing | librosa |
| NLP / gloss conversion | Python, rule-based |
| 3D avatar | Three.js (WebGL) |
| Blender integration | Blender Python API |

---

## Supervisor

Built under **Prof. PVM Rao**, Department of Design & Department of Mechanical Engineering, IIT Delhi.

---

## Author

**Vaishnavi Rai**
B.Tech CSE, IIT Delhi (3rd year)
[cs1230657@iitd.ac.in](mailto:cs1230657@iitd.ac.in)

**Avani Komalkar**
B.Tech CSE, IIT Delhi (3rd year)
[cs5230325@iitd.ac.in](mailto:cs5230325@iitd.ac.in)
