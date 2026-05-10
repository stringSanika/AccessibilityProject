"""
ISL Pipeline — ISLRTC Dictionary Scraper
Scrapes https://divyangjan.depwd.gov.in/islrtc/ to find YouTube video URLs
for all words needed in the lecture gloss.

Run this on your Mac (not blocked like server requests):
  python pose/scrape_islrtc.py

Output: pose/islrtc_urls.json  — paste into mediapipe_extractor.py ISLRTC_SIGNS

Requirements:
  pip install requests beautifulsoup4
"""

import json, time, re, sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing requirements...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "requests", "beautifulsoup4", "--break-system-packages"],
                   capture_output=True)
    import requests
    from bs4 import BeautifulSoup

BASE      = "https://divyangjan.depwd.gov.in/islrtc"
OUT_FILE  = Path(__file__).parent / "islrtc_urls.json"
GLOSS_FILE = Path(__file__).parent.parent / "nlp" / "gloss_output.json"

# ── Words to find ──────────────────────────────────────────────────────────────
# Words that appear in your lecture gloss but don't have ISL signs yet.
# Add/remove as needed. Words with ~~ mean "use sign for the base word".

WORD_ALIASES = {
    # Verb forms → base sign
    "TAKING":  "TAKE",   "TAKEN":    "TAKE",
    "COVERED": "COVER",  "COVERING": "COVER",
    "TALKING": "TALK",   "TALKED":   "TALK",
    "WRITTEN": "WRITE",  "WRITES":   "WRITE",
    "GETTING": "GET",    "GOING":    "GO",
    "MAKING":  "MAKE",   "COMING":   "COME",
    "BECOMES": "BECOME", "BECAME":   "BECOME",
    "STUDIED": "STUDY",  "STUDIES":  "STUDY",
    "COURSES": "COURSE", "YEARS":    "YEAR",
    "TOPICS":  "TOPIC",  "MODELS":   "MODEL",
    "HUMANS":  "HUMAN",  "STUDENTS": "STUDENT",
    "HOPING":  "HOPE",   "THINKS":   "THINK",
    "FOLLOWS": "FOLLOW", "FOLLOWS":  "FOLLOW",
}

# Words that don't have ISL signs (proper nouns, rare technical terms)
# → will use fingerspelling automatically
FINGERSPELL_ONLY = {
    "MOSSAM", "NOVICH", "SEATTLE", "BERKELEY", "MODI", "NITHYA", "NPTEL",
    "GOOGLE", "RUSSELL", "STUART", "PETER", "WELLKNOWN", "ROUNDEDNESS",
    "FINESSE", "PROBABILISTIC", "STATISTICALLY", "COMPUTATIONALLY",
    "REINFORCEMENT", "PHENOMENAL", "BREADTH", "FACETS", "BRANCHES",
    "DETOURS", "SUBSEQUENT", "ORIENTED", "INTRODUCTORY", "FUNDAMENTAL",
    "IIT", "PHD", "AI",  # AI is fingerspelled or has a specific sign
}

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
})

# ── Step 1: Load all words from gloss_output.json ─────────────────────────────

def get_needed_words():
    """Get all unique words from the lecture gloss."""
    already_have = {
        "HELLO","GOODBYE","KNOW","LEARN","TEACH","HAVE","WORK",
        "GOOD","BAD","NOT","I","YOU","EXCITED"
    }
    if not GLOSS_FILE.exists():
        print("[WARN] gloss_output.json not found — using hardcoded word list")
        return get_hardcoded_words()

    words = set()
    data  = json.loads(GLOSS_FILE.read_text())
    for seg in data:
        for w in seg["gloss"].split():
            words.add(w.upper())

    # Resolve aliases
    resolved = set()
    for w in words:
        if w in WORD_ALIASES:
            resolved.add(WORD_ALIASES[w])
        elif w not in FINGERSPELL_ONLY and w not in already_have:
            resolved.add(w)

    return sorted(resolved - already_have)


def get_hardcoded_words():
    """Fallback list if gloss_output.json not found."""
    return sorted([
        "WE","AND","WILL","OF","THAT","COURSE","IN","IT","ABOUT","COVER",
        "THIS","AS","MACHINE","FOR","WHAT","TALK","FROM","BUT","CAN",
        "TAKE","AT","HOW","WELL","VARIOUS","TRADITIONAL","THEY","STUDY",
        "PARTICULAR","NOW","MODEL","MANY","HOPE","GO","FIELD","ALSO",
        "ABLE","WHERE","WANT","VIEW","TYPICAL","TOPIC","SUBJECT","SOME",
        "SIX","SEVERAL","NAME","THINK","THERE","THEN","OR","MORE","MAY",
        "LOT","BOOK","WHICH","BEEN","BOTH","MY","UNIVERSITY","YEAR",
        "SEMESTER","PROFESSOR","STUDENT","FOLLOW","MEAN","UNDERSTAND",
        "LEVEL","PEOPLE","WORLD","TIME","WEEK","FACT","PART","ONE","ALL",
        "MUCH","TWO","GET","USE","DO","MAKE","COME","EVEN","BECOME",
        "SUCH","LONG","FULL","HISTORY","PHILOSOPHY","WRITE","SEARCH",
        "PERCENT","HUMAN","LANGUAGE","INTELLIGENCE","REPRESENT",
        "INTRODUCE","MODERN","APPROACH","INTEREST",
    ])

# ── Step 2: Scrape letter page for word→ID mapping ────────────────────────────

def scrape_letter(letter: str) -> dict[str, int]:
    """Fetch all word→id mappings for a given letter."""
    url  = f"{BASE}/listpage.php?type={letter}"
    try:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"  [ERROR] Letter {letter}: {e}")
        return {}

    soup = BeautifulSoup(r.text, "html.parser")
    mapping = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        m    = re.search(r"id=(\d+)&search=([^&\"]+)", href)
        if not m:
            continue
        word_id   = int(m.group(1))
        word_text = m.group(2).strip()
        # Normalize: first word only, uppercase
        first_word = word_text.split(",")[0].split("(")[0].strip().upper()
        if first_word and first_word not in mapping:
            mapping[first_word] = word_id
        # Also store full phrase for multi-word matches
        mapping[word_text.upper()] = word_id

    return mapping

# ── Step 3: Fetch YouTube URL for a word ID ────────────────────────────────────

def get_youtube_url(word_id: int, word: str) -> str | None:
    """Fetch the word's page and extract YouTube embed URL."""
    url = f"{BASE}/search.php?type=list&id={word_id}&search={word}"
    try:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"    [ERROR] id={word_id}: {e}")
        return None

    m = re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", r.text)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    return None

# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print("[ISLRTC SCRAPER] Finding YouTube URLs for ISL signs")
    print(f"[INFO] Website: {BASE}")
    print()

    # Load existing results
    existing = {}
    if OUT_FILE.exists():
        existing = json.loads(OUT_FILE.read_text())
        print(f"[INFO] {len(existing)} URLs already found in {OUT_FILE.name}\n")

    needed = get_needed_words()
    print(f"[INFO] {len(needed)} words to look up\n")

    # Build letter→word mapping by scanning relevant letter pages
    letters_needed = set(w[0] for w in needed if w not in existing)
    print(f"[INFO] Scanning {len(letters_needed)} letter pages: {sorted(letters_needed)}\n")

    letter_maps = {}
    for letter in sorted(letters_needed):
        print(f"  Scanning {letter}...", end=" ", flush=True)
        m = scrape_letter(letter)
        letter_maps[letter] = m
        print(f"{len(m)} entries")
        time.sleep(0.5)

    print()

    # Match words → IDs → YouTube URLs
    results    = dict(existing)
    not_found  = []

    for word in needed:
        if word in results:
            print(f"  [SKIP] {word:20s} already found: {results[word]}")
            continue

        letter  = word[0]
        lmap    = letter_maps.get(letter, {})

        # Try exact match first, then partial
        word_id = lmap.get(word)
        if not word_id:
            # Try "WORD, ..." pattern (e.g. "FOLLOW" might be "FOLLOW, PURSUE")
            for key, vid in lmap.items():
                if key.startswith(word + " ") or key.startswith(word + ","):
                    word_id = vid
                    break

        if not word_id:
            print(f"  [MISS] {word:20s} not in dictionary → fingerspell")
            not_found.append(word)
            continue

        print(f"  [{word}] id={word_id}...", end=" ", flush=True)
        yt_url = get_youtube_url(word_id, word)
        if yt_url:
            print(f"✓ {yt_url}")
            results[word] = yt_url
        else:
            print("✗ no video")
            not_found.append(word)

        OUT_FILE.write_text(json.dumps(results, indent=2))
        time.sleep(0.4)

    print(f"\n{'='*60}")
    print(f"[DONE] Found: {len(results)} URLs  |  Missing: {len(not_found)}")
    if not_found:
        print(f"[INFO] These will use fingerspelling: {', '.join(not_found)}")

    # Print ready-to-paste ISLRTC_SIGNS dict
    print(f"\n{'='*60}")
    print("Copy this into pose/mediapipe_extractor.py ISLRTC_SIGNS dict:")
    print(f"{'='*60}")
    for word, url in sorted(results.items()):
        print(f'    "{word}":{"":>12} "{url}",')

    print(f"\n[INFO] Full results saved to {OUT_FILE}")


if __name__ == "__main__":
    run()