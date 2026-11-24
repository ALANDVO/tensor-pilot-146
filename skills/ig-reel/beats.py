#!/usr/bin/env python3
"""
Fixed beats.py - Beat counter for Instagram Reel hook scoring.

Fix: Proper name detection now correctly tracks sentence boundaries across lines.
A capitalised word at the start of a line is NOT counted as a proper name
if the previous line ended with ., !, or ?.
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


def count_concrete(line, prev_ended_with_sentence=False):
    """Count the number of concrete markers in a line.
    
    Args:
        line: The text line to analyze
        prev_ended_with_sentence: If True, the previous line ended with ., !, or ?
            This affects proper name detection - a capitalised word at the start
            of this line following a sentence ending should NOT be counted.
    
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
    # If the previous line ended with a sentence, we need to be more careful:
    # a capitalised word at the start of this line should not be counted as a proper name
    has_proper_name = False
    if PROPER_RE.search(line):
        # Additional check: if prev line ended with sentence and this line starts
        # with a capitalised word, we need to verify it's not just a sentence start
        matches = PROPER_RE.findall(line)
        for m in matches:
            # Check if this match is at the start of the line and prev line ended with sentence
            if prev_ended_with_sentence and m == line.lstrip()[0:len(m)]:
                # It's a capitalised word at start of line after sentence ending - skip
                continue
            has_proper_name = True
            break
    
    if has_proper_name:
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
    
    # Track whether the previous line ended with sentence-ending punctuation
    prev_ended_with_sentence = False
    
    for i, line in enumerate(lines, 1):
        concrete = count_concrete(line, prev_ended_with_sentence)
        concrete_total += concrete
        beat_data.append({
            "beat": i,
            "line": line,
            "concrete": concrete,
            "concrete_markers": [m for m in _find_markers(line) if m]
        })
        
        # Update: did this line end with ., !, or ?
        # Check if the stripped line ends with ., !, or ?
        stripped = line.rstrip()
        prev_ended_with_sentence = stripped.endswith(('.', '!', '?'))
    
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
    
    if WORD_RE.search(line):
        markers.append("number_word")
    
    # Proper names: use the same lookbehind, but detect_beats already handles
    # sentence boundary tracking, so we just find them here for display
    proper_matches = PROPER_RE.findall(line)
    for m in proper_matches:
        # Avoid duplicates if already counted
        if m not in markers:
            markers.append("proper_name")
    
    return markers


def main():
    """Main entry point: read from stdin or file argument."""
    if len(sys.argv) < 2:
        print("Usage: beats.py <file> [--hook HOOK]")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--hook":
        if len(sys.argv) < 3:
            print("Usage: beats.py --hook HOOK_TEXT")
            sys.exit(1)
        hook_text = sys.argv[2]
        result = detect_beats(hook_text)
        print(f"Specificity: {result['specificity']}")
        print(f"Concrete markers: {result['concrete_markers']}/{result['total_lines']}")
        for beat in result['beats']:
            print(f"Beat {beat['beat']}: \"{beat['line']}\" -> concrete={beat['concrete']} [{', '.join(beat['concrete_markers'])}]")
    else:
        try:
            with open(arg, 'r') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {arg}")
            sys.exit(1)
        
        result = detect_beats(text)
        print(f"Specificity: {result['specificity']}")
        print(f"Concrete markers: {result['concrete_markers']}/{result['total_lines']}")
        for beat in result['beats']:
            print(f"Beat {beat['beat']}: \"{beat['line']}\" -> concrete={beat['concrete']} [{', '.join(beat['concrete_markers'])}]")


if __name__ == "__main__":
    main()
