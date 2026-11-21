#!/usr/bin/env python3
"""
beats.py - Beat counter for Instagram Reel hook scoring.

Counts "concrete" markers in a text script/beat-sheet.
A beat is concrete if it contains:
  - A digit (0-9)
  - A spoken number word (one, two, three, four, five, six, seven, eight, nine, ten,
    eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen,
    twenty, thirty, forty, fifty, sixty, seventy, eighty, ninety)
  - A proper name (capitalised word NOT starting a sentence after .!?)

SPECIFICITY = concrete_markers / total_lines
"""

import sys
import re

# Spoken number words and their values
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
    "ninety": 90,
}

# Regex for digit detection
DIGIT_RE = re.compile(r'\d')

# Regex for spoken number words (word boundary to avoid partial matches)
WORD_RE = re.compile(r'\b(' + '|'.join(NUMBER_WORDS.keys()) + r')\b', re.IGNORECASE)

# Regex for proper name: capitalised word that does NOT follow .!? followed by space
# Uses negative lookbehind same as detect.py
PROPER_RE = re.compile(r'(?<![.!?]\s)([A-Z][a-zA-Z0-9]+)')


def count_concrete(line):
    """Count the number of concrete markers in a line.
    
    Returns the count of concrete markers found:
    - Digits
    - Spoken number words
    - Proper names (capitalised words not after sentence endings)
    """
    count = 0
    
    # Check for digits
    if DIGIT_RE.search(line):
        count += 1
    
    # Check for spoken number words (case-insensitive)
    if WORD_RE.search(line):
        count += 1
    
    # Check for proper names (capitalised words not after .!?)
    # The lookbehind (?<![.!?]\s) ensures we don't count a capitalised word
    # that starts a new sentence after a period/exclamation/question
    if PROPER_RE.search(line):
        count += 1
    
    return count


def detect_beats(text):
    """Detect beats from input text, one per line.
    
    Returns a dict with beat numbers, concrete counts, and specificity.
    """
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    
    if not lines:
        return {"beats": [], "specificity": 0.0, "concrete_markers": 0, "total_lines": 0}
    
    beat_data = []
    concrete_total = 0
    
    for i, line in enumerate(lines, 1):
        concrete = count_concrete(line)
        concrete_total += concrete
        beat_data.append({
            "beat": i,
            "line": line,
            "concrete": concrete,
            "concrete_markers": [m for m in _find_markers(line) if m]
        })
    
    specificity = concrete_total / len(lines) if lines else 0.0
    
    return {
        "beats": beat_data,
        "specificity": round(specificity, 2),
        "concrete_markers": concrete_total,
        "total_lines": len(lines),
    }


def _find_markers(line):
    """Find which concrete markers are present in a line."""
    markers = []
    if DIGIT_RE.search(line):
        markers.append("digit")
    m = WORD_RE.search(line)
    if m:
        markers.append(f"number_word:{m.group(1).lower()}")
    if PROPER_RE.search(line):
        markers.append("proper_name")
    return markers


def main():
    """Main entry point: read from stdin or file argument."""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    
    result = detect_beats(text)
    
    # Output format
    print(f"Specificity: {result['specificity']}")
    print(f"Concrete markers: {result['concrete_markers']}/{result['total_lines']}")
    print()
    
    for beat in result['beats']:
        markers = ", ".join(beat['concrete_markers']) if beat['concrete_markers'] else "none"
        print(f"Beat {beat['beat']}: \"{beat['line']}\" -> concrete={beat['concrete']} [{markers}]")


if __name__ == "__main__":
    main()
