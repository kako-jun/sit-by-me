#!/usr/bin/env python3
"""Render deterministic electronic SE parameter files to mono WAV and Ogg Vorbis."""
import json
import math
import random
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

RATE = 44100
ROOT = Path(__file__).resolve().parent.parent


def render(spec):
    rng = random.Random(spec['seed'])
    duration = spec['duration']
    n = round(RATE * duration)
    phase = 0.0
    previous = 0.0
    samples = []
    for i in range(n):
        t = i / RATE
        progress = t / duration
        frequency = spec['frequency'] * (spec['end_frequency'] / spec['frequency']) ** progress
        phase = (phase + frequency / RATE) % 1
        shape = spec['wave']
        tone = {'square': lambda: 1.0 if phase < 0.5 else -1.0,
                'triangle': lambda: 1 - 4 * abs(phase - 0.5),
                'saw': lambda: 2 * phase - 1,
                'noise': lambda: rng.uniform(-1, 1)}[shape]()
        # Simple one-pole low-pass to soften the high harmonics.
        previous += spec['filter'] * (tone - previous)
        attack = min(1.0, t / spec['attack']) if spec['attack'] else 1.0
        release = min(1.0, (duration - t) / spec['release'])
        envelope = attack * release * math.exp(-spec['decay'] * progress)
        value = max(-1.0, min(1.0, previous * envelope * spec['gain']))
        samples.append(struct.pack('<h', round(value * 32767)))
    return b''.join(samples)


def main():
    files = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / 'assets/se/params').glob('*.json'))
    out = ROOT / 'assets/sounds/se'
    out.mkdir(parents=True, exist_ok=True)
    for path in files:
        spec = json.loads(path.read_text())
        with tempfile.TemporaryDirectory() as temp:
            wav = Path(temp) / 'sound.wav'
            with wave.open(str(wav), 'wb') as audio:
                audio.setparams ( (1, 2, RATE, 0, 'NONE', 'not compressed') )
                audio.writeframes(render(spec))
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(wav), '-c:a', 'libvorbis', '-q:a', '4', str(out / (path.stem + '.ogg'))], check=True)
        print(out / (path.stem + '.ogg'))


if __name__ == '__main__':
    main()
