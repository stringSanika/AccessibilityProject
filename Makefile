# ── ISL Pipeline Makefile ─────────────────────────────────────────────────────
# Usage:
#   make audio    → phase 1: extract audio from lecture.mp4
#   make asr      → phase 2: transcribe with Whisper
#   make gloss    → phase 3: convert to ISL gloss
#   make motion   → phase 4: map to motion descriptors
#   make scrape   → phase 5a: scrape ISLRTC website for sign URLs
#   make pose     → phase 5b: extract ISL poses from ISLRTC videos
#   make serve    → start local no-cache server
#   make avatar   → open avatar_3d.html in browser
#   make demo     → open demo_viewer.html in browser
#   make status   → show which output files exist
#   make clean    → remove lecture files (keeps ISL videos & pose data)
#   make clean-all → remove everything including ISL videos (full reset)
#
# Normal workflow (first time):
#   make audio && make asr && make gloss && make motion
#   make scrape   ← only needed once, finds ISL video URLs
#   make pose     ← only needed once, downloads & extracts signs
#   make serve
#
# After changing lecture.mp4:
#   make clean && make audio && make asr && make gloss && make motion && make serve

PYTHON  = python3
BROWSER = open   # Mac; change to 'xdg-open' on Linux, 'start' on Windows
PORT    = 8000

# ── Default: full pipeline ─────────────────────────────────────────────────────

all: audio asr gloss motion serve avatar

# ── Phase 1: Audio extraction ──────────────────────────────────────────────────

audio:
	@echo ""
	@echo "── Phase 1: Extracting audio ────────────────────────────────"
	ffmpeg -i asr/lecture.mp4 -ar 16000 -ac 1 asr/audio.wav -y
	@echo "✓ Done → asr/audio.wav"

# ── Phase 2: ASR transcription ─────────────────────────────────────────────────

asr: asr/audio.wav
	@echo ""
	@echo "── Phase 2: Transcribing with Whisper ───────────────────────"
	$(PYTHON) asr/asr_isl.py
	@echo "✓ Done → asr/segments.json"

# ── Phase 3: Gloss conversion ──────────────────────────────────────────────────

gloss: asr/segments.json
	@echo ""
	@echo "── Phase 3: Converting to ISL gloss ─────────────────────────"
	$(PYTHON) nlp/gloss_converter.py
	@echo "✓ Done → nlp/gloss_output.json"

# ── Phase 4: Motion mapping ────────────────────────────────────────────────────

motion: nlp/gloss_output.json
	@echo ""
	@echo "── Phase 4: Mapping to motion descriptors ───────────────────"
	$(PYTHON) motion/motion_mapper.py
	@echo "✓ Done → motion/motion_sequence.json"

# ── Phase 5: ISL pose extraction ──────────────────────────────────────────────

pose:
	@echo ""
	@echo "── Phase 5: Extracting ISL poses from ISLRTC videos ─────────"
	$(PYTHON) pose/mediapipe_extractor.py
	@echo "── Updating motion library ──────────────────────────────────"
	$(PYTHON) pose/update_motion_library.py
	@echo "── Updating avatar_3d.html SIGNS ────────────────────────────"
	$(PYTHON) pose/update_avatar.py
	@echo "── Regenerating motion_sequence.json ────────────────────────"
	$(PYTHON) motion/motion_mapper.py
	@echo "✓ Done → motion_mapper.py + avatar_3d.html updated with verified ISL signs"

# ── Phase 5b: Scrape ISLRTC dictionary for more sign URLs ─────────────────────

scrape:
	@echo ""
	@echo "── Scraping ISLRTC dictionary for ISL sign URLs ─────────────"
	$(PYTHON) pose/scrape_islrtc.py
	@echo "── Updating ISLRTC_SIGNS in mediapipe_extractor.py ──────────"
	$(PYTHON) pose/update_islrtc_signs.py
	@echo "✓ Done → re-run: make pose"



serve:
	@echo ""
	@echo "── Starting local server on port $(PORT) (cache disabled) ──"
	@echo "   Open: http://localhost:$(PORT)/avatar/avatar_3d.html"
	@echo "   Open: http://localhost:$(PORT)/demo_viewer.html"
	@echo "   Press Ctrl+C to stop"
	$(PYTHON) serve.py $(PORT)

# ── Open in browser ────────────────────────────────────────────────────────────

avatar:
	@echo "── Opening avatar_3d.html ───────────────────────────────────"
	$(BROWSER) http://localhost:$(PORT)/avatar/avatar_3d.html

demo:
	@echo "── Opening demo_viewer.html ─────────────────────────────────"
	$(BROWSER) http://localhost:$(PORT)/demo_viewer.html

# ── Status ─────────────────────────────────────────────────────────────────────

status:
	@echo ""
	@echo "── Pipeline output files ────────────────────────────────────"
	@test -f asr/audio.wav              && echo "  ✓ asr/audio.wav"             || echo "  ✗ asr/audio.wav"
	@test -f asr/segments.json          && echo "  ✓ asr/segments.json"         || echo "  ✗ asr/segments.json"
	@test -f nlp/gloss_output.json      && echo "  ✓ nlp/gloss_output.json"     || echo "  ✗ nlp/gloss_output.json"
	@test -f motion/motion_sequence.json && echo "  ✓ motion/motion_sequence.json" || echo "  ✗ motion/motion_sequence.json"
	@test -f pose/extracted_signs.json  && echo "  ✓ pose/extracted_signs.json" || echo "  ✗ pose/extracted_signs.json"
	@echo ""

# ── Clean (lecture files only — preserves ISL videos & pose data) ──────────────
# Use this normally — keeps downloaded ISL videos so make pose is fast next time

clean:
	@echo "── Removing lecture pipeline files ──────────────────────────"
	rm -f asr/audio.wav
	rm -f asr/segments.json
	rm -f asr/segments.txt
	rm -f asr/transcript.txt
	rm -f nlp/gloss_output.json
	rm -f nlp/gloss_output.txt
	rm -f motion/motion_sequence.json
	rm -f avatar/avatar_timeline.json
	@echo "✓ Clean — lecture files removed (ISL videos & pose data preserved)"
	@echo "  Tip: use 'make clean-all' to also remove ISL videos"

# ── Clean-all (removes everything including ISL videos) ────────────────────────
# Only use if you want to re-download all ISL videos from scratch

clean-all:
	@echo "── Removing ALL generated files including ISL data ──────────"
	rm -f asr/audio.wav
	rm -f asr/segments.json
	rm -f asr/segments.txt
	rm -f asr/transcript.txt
	rm -f nlp/gloss_output.json
	rm -f nlp/gloss_output.txt
	rm -f motion/motion_sequence.json
	rm -f avatar/avatar_timeline.json
	rm -f pose/extracted_signs.json
	rm -f pose/islrtc_urls.json
	rm -f pose/hand_landmarker.task
	rm -f pose/pose_landmarker.task
	rm -rf pose/videos/
	rm -rf pose/backups/
	@echo "✓ Clean-all — everything removed"

.PHONY: all audio asr gloss motion pose scrape serve avatar demo status clean clean-all run