#!/usr/bin/env python3
"""make_video.py <film.mp4> <word-timings.json> <out.mp4> [timing scale] : short stage version of the film.

The parts are found by the spoken words, the cuts are placed in the quietest moment between two sentences.
Needs numpy and the compiled build/cut (swiftc -O build/cut.swift -o build/cut).
"""
import json
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

film, timings, out = sys.argv[1:4]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
words = json.load(open(timings))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
plain = [norm(w["text"]) for w in words]
PARTS = [("so how does", "now its the seventh"), ("heres a day", "to plan ahead"), ("so does it pay", "thats why")]
FADE = 0.36

with tempfile.TemporaryDirectory() as tmp:
    wav = str(Path(tmp) / "voice.wav")
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", film, wav], check=True)
    with wave.open(wav) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32768
rms = np.sqrt(np.convolve(x * x, np.ones(160) / 160, "same"))[::160]  # one value per 10 ms
quiet = rms < 0.01


def pause(phrase):
    q = phrase.split()
    hits = [i for i in range(len(plain)) if plain[i:i + len(q)] == q]
    if len(hits) != 1:
        raise SystemExit("phrase found %d times: %s" % (len(hits), phrase))
    t = int(words[hits[0]]["start"] * scale * 100)
    runs, start = [], None
    lo = max(0, t - 120)
    for i in range(lo, min(len(quiet), t + 80)):
        if quiet[i] and start is None:
            start = i
        if not quiet[i] and start is not None:
            runs.append((start, i))
            start = None
    runs = [r for r in runs if r[1] - r[0] >= 12]
    if not runs:
        raise SystemExit("no pause before: %s" % phrase)
    best = min(runs, key=lambda r: abs(r[1] - t) - 0.5 * (r[1] - r[0]))
    return best[0] / 100, best[1] / 100


args = []
settle = 0.0
for a, b in PARTS:
    pa, pb = pause(a), pause(b)
    first = max(pa[0] + 0.02, pa[1] - FADE)
    last = min(pb[1] - 0.02, pb[0] + FADE)
    if b == PARTS[-1][1]:
        last = pb[0] + 0.22  # let the last word finish, TAIL freezes the picture before the next slide moves in
    print("%-24s pause %.2f-%.2f | %-24s pause %.2f-%.2f | keep %.2f-%.2f" % (a, *pa, b, *pb, first, last))
    if a == "so does it pay":
        settle = pa[1] + 1.8 - first
    args += ["%.3f" % first, "%.3f" % last]
subprocess.run([str(Path(__file__).with_name("cut")), film, out, "7000000", "1920", "1080", *args], check=True,
               env={"HOLD": "%d:%.3f" % (len(PARTS) - 1, settle), "TAIL": "0.28"})
