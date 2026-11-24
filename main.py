#!/usr/bin/env python3
"""One Emoji, One Dream Vacation - exactly one emoji, the most evocative.

Pure Python 3.13 standard library. The program writes one emoji to
/output/entry.txt. No network, no model call, fully deterministic: the
same code always writes the same bytes.

The entry: U+1F30B VOLCANO
    🌋

Why this emoji, judged against the brief's criteria in order:

1. It plainly lands on a dream vacation: a volcano is a faraway place,
   the kind of trip people save for years to take - Hawaii, Iceland,
   Bromo at sunrise. It names a destination, not a mood.
2. Vivid at a glance, like a postcard: a smoking, lava-lit peak is a
   whole landscape in one glyph - fire, mountain and sky together.
   A stranger sees the place before reading a word.
3. Personal and specific rather than generic: it points at one
   particular dream - standing at the edge of the Earth - instead of
   "any holiday". A beach or a plane could be anyone's trip; a
   volcano is a chosen one.
4. A spark of surprise: nobody's default holiday emoji is a volcano.
   It is fresh and a little daring, which is exactly what makes a
   stranger stop scrolling and start pricing flights.
5. Reads instantly across cultures and screens: bold orange-red
   against a dark peak, clear even at small size, no explanation
   needed - and it is one single codepoint, so it cannot render
   differently across platforms the way ZWJ or variation-selector
   sequences can.

Candidates weighed and set aside:

- U+1F3D6 BEACH WITH UMBRELLA: the most obvious dream-vacation
  glyph, but also the most generic - it is every holiday, so it is
  no-one's in particular, and it loses on criteria 3 and 4.
- U+2708 AIRPLANE: the journey, not the place; it says "travel" but
  shows no destination, so it loses on criterion 2.
- U+1F30C MILKY WAY: dreamy and specific (a dark-sky night), but it
  reads as a sky, not a trip - the vacation itself is only implied.
- U+1F5FB MOUNT FUJI: iconic and specific, but one mountain in one
  country; the volcano is the same postcard feeling with a wider
  dream behind it, and a more vivid, fiery read at small size.

Validation: before writing, the program asserts the entry is exactly
one Unicode character (one grapheme cluster, one codepoint), in
category So (Symbol, other - an emoji symbol), and not whitespace,
so a bad constant can never reach the output file.

Newline decision: the gate checks that entry.txt is UTF-8 text of
1 to 8 characters, not only white space. A trailing newline would
make the file 2 characters and still pass the gate, but the task is
"exactly one emoji and nothing else", so the file is written with NO
trailing newline: exactly 1 character, 4 bytes of UTF-8, nothing
else.

Usage: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import unicodedata

EMOJI = "🌋"  # U+1F30B VOLCANO


def validate_emoji(value):
    """Check the entry is exactly one non-whitespace emoji character."""
    assert isinstance(value, str), "entry must be a str"
    assert len(value) == 1, f"entry must be exactly 1 character, got {len(value)}"
    assert not value.isspace(), "entry must not be whitespace"
    assert unicodedata.category(value) == "So", (
        f"entry must be an emoji symbol (category So), "
        f"got {unicodedata.category(value)}"
    )
    assert len(value.encode("utf-8")) == 4, "entry must be 4 bytes of UTF-8"


def _write_all(f, data):
    """Write every byte, looping over partial writes."""
    view = memoryview(data)
    while view:
        n = f.write(view)
        if n is None or n == 0:
            raise OSError("short write while writing entry")
        view = view[n:]


def _clean_output_dir(out_dir):
    """Remove the CONTENTS of the output dir, never the dir itself.

    The grader mounts the output folder, so the folder must stay.
    Stale files from a previous run must not survive.
    """
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            for sub in os.listdir(path):
                os.remove(os.path.join(path, sub))
            os.rmdir(path)
        else:
            os.remove(path)


def main():
    validate_emoji(EMOJI)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    _clean_output_dir(out_dir)
    data = EMOJI.encode("utf-8")
    tmp = os.path.join(out_dir, ".entry.txt.tmp")
    final = os.path.join(out_dir, "entry.txt")
    # Stale temp from a crashed earlier run: remove, retry once.
    for attempt in range(2):
        try:
            with open(tmp, "wb") as f:
                _write_all(f, data)
                f.flush()
                os.fsync(f.fileno())
            break
        except OSError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            if attempt == 1:
                raise
    os.chmod(tmp, 0o644)
    os.replace(tmp, final)
    os.chmod(final, 0o644)


if __name__ == "__main__":
    main()
