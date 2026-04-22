import whisper
import librosa
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent
AUDIO_PATH = BASE_DIR / "audio.wav"

# Load audio using librosa (no ffmpeg needed)
audio, sr = librosa.load(str(AUDIO_PATH), sr=16000)

# Load Whisper model and transcribe
model = whisper.load_model("base")
result = model.transcribe(audio, language="en", fp16=False)

# Save full transcript
with open(BASE_DIR / "transcript.txt", "w") as f:
    f.write(result["text"])

# Save sentence-like segments (VERY IMPORTANT for sign language)
with open(BASE_DIR / "segments.txt", "w") as f:
    for seg in result["segments"]:
        f.write(seg["text"].strip() + "\n")

print("Saved transcript.txt and segments.txt")
