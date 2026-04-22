"""
ISL Pipeline — Phase 2: Gloss Conversion
Reads segments.json from ASR, converts cleaned English text to ISL gloss.

Input:  asr/segments.json
Output: nlp/gloss_output.json
        nlp/gloss_output.txt  (quick inspection)

ISL grammar rules applied:
  - Drop: am, is, are, was, were, the, a, an, to (infinitive marker)
  - Reorder: Object-Subject-Verb (OSV) where detectable
  - Negate: move NOT to end  → "I do not understand" → "UNDERSTAND I NOT"
  - Question: WH-word moves to end → "where are you going" → "YOU GO WHERE"
"""

import json
import re
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR    = Path(__file__).parent
INPUT_PATH  = BASE_DIR.parent / "asr" / "segments.json"
OUTPUT_JSON = BASE_DIR / "gloss_output.json"
OUTPUT_TXT  = BASE_DIR / "gloss_output.txt"

# ── Grammar rules ──────────────────────────────────────────────────────────────

# Words dropped in ISL (articles, aux verbs, infinitive marker)
DROP_WORDS = {
    "am", "is", "are", "was", "were", "be",
    "the", "a", "an",
    "do", "does", "did",
    "to",       # infinitive "to" only — kept when it means direction
    "very",     # ISL uses intensity via repetition, not adverbs
}

# Negation words → replaced with NOT, moved to end
NEGATION_WORDS = {"not", "never", "no", "don't", "doesn't", "didn't", "cannot", "can't"}

# WH question words → moved to end in ISL
WH_WORDS = {"what", "where", "when", "why", "who", "which", "how"}

# Simple pronoun map
PRONOUN_MAP = {
    "i": "I", "me": "I", "my": "MY", "mine": "MY",
    "you": "YOU", "your": "YOUR",
    "he": "HE", "him": "HE", "his": "HIS",
    "she": "SHE", "her": "HER",
    "we": "WE", "us": "WE", "our": "OUR",
    "they": "THEY", "them": "THEY", "their": "THEIR",
    "it": "IT", "its": "ITS",
}

# Common verb simplifications (strip tense for gloss)
VERB_MAP = {
    "going": "GO", "went": "GO", "goes": "GO",
    "coming": "COME", "came": "COME", "comes": "COME",
    "explaining": "EXPLAIN", "explained": "EXPLAIN", "explains": "EXPLAIN",
    "understanding": "UNDERSTAND", "understood": "UNDERSTAND",
    "learning": "LEARN", "learned": "LEARN",
    "teaching": "TEACH", "taught": "TEACH",
    "looking": "LOOK", "looked": "LOOK",
    "talking": "TALK", "talked": "TALK",
    "saying": "SAY", "said": "SAY",
    "doing": "DO", "done": "DO",
    "having": "HAVE", "had": "HAVE",
    "using": "USE", "used": "USE",
    "called": "CALL", "calling": "CALL",
    "known": "KNOW", "knowing": "KNOW",
    "shown": "SHOW", "showing": "SHOW",
    "working": "WORK", "worked": "WORK",
    "running": "RUN", "ran": "RUN",
    "writing": "WRITE", "wrote": "WRITE",
    "reading": "READ",
    "helping": "HELP", "helped": "HELP",
    "starting": "START", "started": "START",
    "stopping": "STOP", "stopped": "STOP",
    "opening": "OPEN", "opened": "OPEN",
    "closing": "CLOSE", "closed": "CLOSE",
}

# ── Core conversion ────────────────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    """Split cleaned text into word tokens, strip punctuation."""
    text = re.sub(r"[^\w\s']", "", text.lower())
    return [w.strip("'") for w in text.split() if w.strip("'")]


def to_gloss_token(word: str) -> str | None:
    """
    Convert a single word to its ISL gloss token.
    Returns None if the word should be dropped.
    """
    if word in DROP_WORDS:
        return None
    if word in NEGATION_WORDS:
        return "NOT"    # caller handles moving this to end
    if word in PRONOUN_MAP:
        return PRONOUN_MAP[word]
    if word in VERB_MAP:
        return VERB_MAP[word]
    # Default: uppercase the word as-is (noun / unknown)
    return word.upper()


def reorder_osv(tokens: list[str]) -> list[str]:
    """
    Very simplified OSV reorder heuristic for ISL.
    Real ISL grammar is complex; this handles the most common classroom patterns:
      Subject-Verb-Object → Object-Subject-Verb
      "I explain neural networks" → "NEURAL NETWORKS I EXPLAIN"
    Heuristic: if first token is a pronoun (subject) and last tokens look like
    a noun phrase, swap them around the verb.
    """
    pronouns = set(PRONOUN_MAP.values())
    if not tokens:
        return tokens
    if tokens[0] in pronouns and len(tokens) >= 3:
        subject = tokens[0]
        verb    = tokens[1] if len(tokens) > 1 else None
        obj     = tokens[2:] if len(tokens) > 2 else []
        if verb and obj:
            return obj + [subject, verb]
    return tokens


def convert_sentence(text: str) -> str:
    """
    Full pipeline for one cleaned sentence → ISL gloss string.

    Steps:
      1. Tokenize
      2. Detect negation / WH-question
      3. Map each token to gloss (drop articles, aux verbs, etc.)
      4. Apply OSV reorder (unless WH or negation changes structure)
      5. Append NOT / WH-word at end per ISL grammar
    """
    words = tokenize(text)
    if not words:
        return ""

    is_question  = words[-1] == "?" or words[0] in WH_WORDS
    wh_word      = words[0].upper() if words[0] in WH_WORDS else None
    has_negation = any(w in NEGATION_WORDS for w in words)

    gloss_tokens = []
    not_pending  = False

    for word in words:
        if word in NEGATION_WORDS:
            not_pending = True
            continue
        if word in WH_WORDS and wh_word:
            continue    # WH-word appended at end
        token = to_gloss_token(word)
        if token is not None:
            gloss_tokens.append(token)

    # Reorder to OSV (skip if WH-question — different structure)
    if not wh_word:
        gloss_tokens = reorder_osv(gloss_tokens)

    # Append NOT at end (ISL negation pattern)
    if not_pending:
        gloss_tokens.append("NOT")

    # Append WH-word at end (ISL question pattern)
    if wh_word:
        gloss_tokens.append(wh_word)

    return " ".join(gloss_tokens)

# ── Main ───────────────────────────────────────────────────────────────────────

def convert_all(input_path: Path) -> list[dict]:
    """Load segments.json, convert each segment, return enriched records."""
    if not input_path.exists():
        raise FileNotFoundError(
            f"segments.json not found at {input_path}\n"
            "Run asr/asr_isl.py first to generate it."
        )

    with open(input_path, encoding="utf-8") as f:
        segments = json.load(f)

    results = []
    for seg in segments:
        gloss = convert_sentence(seg["clean"])
        results.append({
            "id":         seg["id"],
            "start":      seg["start"],
            "end":        seg["end"],
            "clean":      seg["clean"],
            "gloss":      gloss,
            "word_count": seg["word_count"],
        })

    return results


def save_outputs(records: list[dict]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_JSON.write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[NLP] Saved: {OUTPUT_JSON}  ({len(records)} segments)")

    lines = [
        f"[{r['start']:>7.2f}s]  {r['clean']}\n"
        f"           → {r['gloss']}"
        for r in records
    ]
    OUTPUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[NLP] Saved: {OUTPUT_TXT}")

    print(f"\n[NLP] Sample conversions (first 3):")
    for r in records[:3]:
        print(f"  English : {r['clean']}")
        print(f"  ISL     : {r['gloss']}")
        print()


if __name__ == "__main__":
    print("[NLP] Starting gloss conversion…")
    records = convert_all(INPUT_PATH)
    save_outputs(records)
    print("[NLP] Phase 2 complete — gloss_output.json ready for motion mapper")
