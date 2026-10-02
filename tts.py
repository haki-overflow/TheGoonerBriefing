import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

VOICE = "bm_george"  # British male. Others to try: bm_lewis, bf_emma
SPEED = 1.0

text = Path("episodes/script.txt").read_text().strip()
kokoro = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")

# split into short chunks so the voice model never gets too much at once
sentences = re.split(r"(?<=[.!?])\s+", text)
chunks, current = [], ""
for s in sentences:
    if current and len(current) + len(s) > 300:
        chunks.append(current)
        current = s
    else:
        current = f"{current} {s}".strip()
if current:
    chunks.append(current)

pieces, sample_rate = [], 24000
for i, chunk in enumerate(chunks, 1):
    print(f"Speaking part {i} of {len(chunks)}")
    samples, sample_rate = kokoro.create(chunk, voice=VOICE, speed=SPEED, lang="en-gb")
    pieces.append(samples)
    pieces.append(np.zeros(int(sample_rate * 0.25), dtype=samples.dtype))  # short pause

audio = np.concatenate(pieces)
sf.write("episodes/episode.wav", audio, sample_rate)
subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-i", "episodes/episode.wav", "episodes/episode.mp3"],
    check=True,
)
print(f"Done: episodes/episode.mp3 ({len(audio) / sample_rate:.0f} seconds)")