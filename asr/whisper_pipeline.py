import ffmpeg
import whisper
from pathlib import Path

BASE_DIR = Path(__file__).parent  # directory of whisper_pipeline.py
VIDEO_PATH = BASE_DIR / "lecture.mp4"
AUDIO_PATH = BASE_DIR / "audio.wav"

ffmpeg.input(str(VIDEO_PATH)).output(str(AUDIO_PATH)).run()

model = whisper.load_model("base")
result = model.transcribe(str(AUDIO_PATH))

# print(result["text"])

# Save full transcript
with open("transcript.txt", "w") as f:
    f.write(result["text"])

# Save sentence-like segments (VERY IMPORTANT for sign language)
with open("segments.txt", "w") as f:
    for seg in result["segments"]:
        f.write(seg["text"].strip() + "\n")

print("Saved transcript.txt and segments.txt")