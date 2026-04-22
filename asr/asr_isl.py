"""
ISL Pipeline — Phase 1: Streaming ASR
Transcribes lecture audio and outputs cleaned, structured segments
ready for Phase 2 gloss conversion.

Output files:
  transcript.txt   — raw full transcript (for WER evaluation)
  segments.json    — structured segments with timing + cleaned text
  segments.txt     — plain-text segments (one per line, for quick inspection)
"""

import json
import re
import whisper
import librosa
import numpy as np
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent
AUDIO_PATH = BASE_DIR / "audio.wav"
MODEL_SIZE = "base"   # options: tiny, base, small, medium, large
LANGUAGE   = "en"

# Filler words to strip before gloss conversion
FILLERS = {
    "uh", "um", "uh-huh", "hmm", "hm", "ah", "er", "err",
    "like", "you know", "i mean", "right", "okay", "ok",
    "so", "basically", "actually", "literally",
}

# ── Text cleaning ─────────────────────────────────────────────────────────────

def remove_fillers(text: str) -> str:
    """Remove spoken filler words from transcribed text."""
    pattern = r"\b(" + "|".join(re.escape(f) for f in FILLERS) + r")\b[,.]?\s*"
    return re.sub(pattern, " ", text, flags=re.IGNORECASE).strip()


def clean_text(text: str) -> str:
    """
    Full cleaning pipeline for a single segment:
      1. Lowercase
      2. Strip leading/trailing whitespace
      3. Remove filler words
      4. Collapse multiple spaces
      5. Strip trailing punctuation (sign language doesn't need it)
    """
    text = text.lower().strip()
    text = remove_fillers(text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.rstrip(".,;:!?")
    return text.strip()


def segment_to_record(seg: dict) -> dict:
    """
    Convert a Whisper segment dict to a structured record for the gloss pipeline.

    Returns:
        {
            "id":        int   — segment index
            "start":     float — start time in seconds
            "end":       float — end time in seconds
            "raw":       str   — original transcribed text
            "clean":     str   — lowercased, filler-stripped text
            "word_count":int   — number of words (for gloss complexity estimate)
        }
    """
    raw   = seg["text"].strip()
    clean = clean_text(raw)
    return {
        "id":         seg["id"],
        "start":      round(seg["start"], 2),
        "end":        round(seg["end"],   2),
        "raw":        raw,
        "clean":      clean,
        "word_count": len(clean.split()),
    }

# ── Main ──────────────────────────────────────────────────────────────────────

def transcribe(audio_path: Path, model_size: str = MODEL_SIZE) -> dict:
    """Load audio with librosa, transcribe with Whisper, return raw result."""
    print(f"[ASR] Loading audio: {audio_path}")
    audio, _ = librosa.load(str(audio_path), sr=16000)

    print(f"[ASR] Loading Whisper model: {model_size}")
    model  = whisper.load_model(model_size)

    print("[ASR] Transcribing…")
    result = model.transcribe(audio, language=LANGUAGE, fp16=False)
    print(f"[ASR] Done — {len(result['segments'])} segments detected")
    return result


def save_outputs(result: dict, base_dir: Path) -> None:
    """Write transcript.txt, segments.json, and segments.txt."""

    # 1. Raw full transcript — used for WER evaluation
    transcript_path = base_dir / "transcript.txt"
    transcript_path.write_text(result["text"], encoding="utf-8")
    print(f"[ASR] Saved: {transcript_path}")

    # 2. Structured segments — primary feed for Phase 2 (gloss conversion)
    records = [segment_to_record(seg) for seg in result["segments"]]

    segments_json = base_dir / "segments.json"
    segments_json.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[ASR] Saved: {segments_json}  ({len(records)} segments)")

    # 3. Plain-text segments — quick human inspection
    segments_txt = base_dir / "segments.txt"
    lines = [
        f"[{r['start']:>7.2f}s – {r['end']:>7.2f}s]  {r['clean']}"
        for r in records
    ]
    segments_txt.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ASR] Saved: {segments_txt}")

    # 4. Summary to stdout
    total_words = sum(r["word_count"] for r in records)
    duration    = records[-1]["end"] if records else 0
    print(f"\n[ASR] Summary")
    print(f"       Duration  : {duration:.1f}s")
    print(f"       Segments  : {len(records)}")
    print(f"       Words     : {total_words}")
    print(f"\n[ASR] Sample output (first 3 segments):")
    for r in records[:3]:
        print(f"  [{r['start']}s]  raw  : {r['raw']}")
        print(f"           clean: {r['clean']}")
        print()


if __name__ == "__main__":
    result = transcribe(AUDIO_PATH)
    save_outputs(result, BASE_DIR)
    print("[ASR] Phase 1 complete — segments.json ready for gloss conversion")