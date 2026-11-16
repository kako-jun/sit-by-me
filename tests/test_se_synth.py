"""Check the provisional sound registry and reproducible synthesized samples."""
import json
import math
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import se_synth


class SoundAssetsTests(unittest.TestCase):
    def test_manifest_recipes_and_audio_are_in_sync(self):
        sound_dir = ROOT / 'assets/sounds/se'
        manifest = json.loads((sound_dir / 'manifest.json').read_text())
        recipes = {p.stem: p for p in (ROOT / 'assets/se/params').glob('*.json')}
        self.assertEqual(set(manifest), set(recipes))
        for name, filename in manifest.items():
            with self.subTest(name=name):
                self.assertEqual(filename, name + '.ogg')
                self.assertTrue((sound_dir / filename).is_file())
                self.assertGreater((sound_dir / filename).stat().st_size, 0)

    def test_recipes_render_deterministically_with_audible_headroom(self):
        for path in sorted((ROOT / 'assets/se/params').glob('*.json')):
            with self.subTest(recipe=path.name):
                recipe = json.loads(path.read_text())
                rendered = se_synth.render(recipe)
                self.assertEqual(rendered, se_synth.render(recipe))
                self.assertEqual(len(rendered), round(recipe['duration'] * se_synth.RATE) * 2)
                samples = struct.unpack(f'<{len(rendered) // 2}h', rendered)
                self.assertGreater(max(map(abs, samples)), 0)
                self.assertLess(max(map(abs, samples)), 32767)

    def test_ogg_decodes_to_the_regenerated_recipe(self):
        for path in sorted((ROOT / 'assets/se/params').glob('*.json')):
            with self.subTest(recipe=path.name), tempfile.TemporaryDirectory() as directory:
                wav = Path(directory) / 'source.wav'
                encoded = Path(directory) / 'rendered.ogg'
                recipe = json.loads(path.read_text())
                with wave.open(str(wav), 'wb') as output:
                    output.setparams((1, 2, se_synth.RATE, 0, 'NONE', 'not compressed'))
                    output.writeframes(se_synth.render(recipe))
                subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(wav), '-c:a', 'libvorbis', '-q:a', '4', str(encoded)], check=True)
                def decode(file):
                    return subprocess.check_output(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(file), '-f', 's16le', '-acodec', 'pcm_s16le', '-'])
                reference = decode(encoded)
                actual = decode(ROOT / 'assets/sounds/se' / (path.stem + '.ogg'))
                self.assertEqual(len(reference), len(actual))
                expected_samples = struct.unpack(f'<{len(reference) // 2}h', reference)
                actual_samples = struct.unpack(f'<{len(actual) // 2}h', actual)
                dot = sum(a * b for a, b in zip(expected_samples, actual_samples))
                norm = math.sqrt(sum(a * a for a in expected_samples) * sum(b * b for b in actual_samples))
                self.assertGreater(dot / norm, 0.99)
