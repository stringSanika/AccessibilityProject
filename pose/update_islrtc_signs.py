"""
ISL Pipeline — Update ISLRTC_SIGNS from scraped URLs
Reads pose/islrtc_urls.json and patches the ISLRTC_SIGNS dict
in pose/mediapipe_extractor.py automatically.

Usage:
  python pose/update_islrtc_signs.py

Run AFTER: python pose/scrape_islrtc.py
Run BEFORE: make pose
"""

import json, re, shutil
from pathlib import Path
from datetime import datetime

BASE_DIR     = Path(__file__).parent
URLS_FILE    = BASE_DIR / "islrtc_urls.json"
EXTRACTOR    = BASE_DIR / "mediapipe_extractor.py"
BACKUP_DIR   = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

def run():
    if not URLS_FILE.exists():
        print("[ERROR] pose/islrtc_urls.json not found")
        print("  Run: python pose/scrape_islrtc.py first")
        return

    urls   = json.loads(URLS_FILE.read_text())
    print(f"[INFO] {len(urls)} URLs loaded from {URLS_FILE.name}")

    content = EXTRACTOR.read_text()

    # Find the ISLRTC_SIGNS dict block
    start = content.find("ISLRTC_SIGNS = {")
    end   = content.find("\n}", start) + 2
    if start == -1 or end < 2:
        print("[ERROR] Could not find ISLRTC_SIGNS dict in mediapipe_extractor.py")
        return

    old_block = content[start:end]

    # Parse existing entries to preserve them
    existing = {}
    for m in re.finditer(r'"(\w+)":\s*"(https://[^"]+)"', old_block):
        existing[m.group(1)] = m.group(2)

    print(f"[INFO] {len(existing)} existing entries in ISLRTC_SIGNS")

    # Merge: existing + new URLs
    merged = {**existing, **urls}
    print(f"[INFO] {len(merged)} total after merge")

    # Build new dict block
    lines = ["ISLRTC_SIGNS = {"]
    for word, url in sorted(merged.items()):
        lines.append(f'    "{word}":{" " * max(1, 15-len(word))}"{url}",')
    lines.append("}")
    new_block = "\n".join(lines)

    # Backup original
    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"mediapipe_extractor_backup_{ts}.py"
    shutil.copy(EXTRACTOR, backup)
    print(f"[BACKUP] {backup.name}")

    # Patch
    new_content = content[:start] + new_block + content[end:]
    EXTRACTOR.write_text(new_content)

    print(f"[DONE] Updated {EXTRACTOR.name} with {len(merged)} signs")
    print(f"[NEXT] Run: make pose")

if __name__ == "__main__":
    run()