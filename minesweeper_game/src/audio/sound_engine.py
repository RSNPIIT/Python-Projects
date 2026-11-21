"""
sound_engine.py - Procedural 8-bit Sound Synthesizer & Asynchronous Audio Player.
Generates retro WAV sound effects at runtime with zero external dependencies,
playing them via afplay on macOS or system audio.
"""

import math
import os
import struct
import subprocess
import threading
import wave
from typing import Dict, Optional


class SoundEngine:
    """Procedurally synthesizes and plays arcade Minesweeper sound effects."""

    def __init__(self, asset_dir: str):
        self.asset_dir = asset_dir
        self.sounds_dir = os.path.join(asset_dir, "sounds")
        os.makedirs(self.sounds_dir, exist_ok=True)
        self.enabled = True
        self.sample_rate = 22050

        # Synthesize sound assets on initial startup
        self._generate_all_sounds()

    def _write_wav(self, filename: str, samples: list):
        filepath = os.path.join(self.sounds_dir, filename)
        if os.path.exists(filepath):
            return filepath

        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)

            # Pack samples into 16-bit signed PCM
            raw_data = bytearray()
            for s in samples:
                val = max(-32767, min(32767, int(s * 32767.0)))
                raw_data.extend(struct.pack("<h", val))

            wav_file.writeframes(raw_data)
        return filepath

    def _generate_all_sounds(self):
        # 1. Click: sharp subtle click (25ms)
        samples = []
        n_samples = int(self.sample_rate * 0.025)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = (1.0 - i / n_samples) ** 2
            freq = 1200.0 - (i / n_samples) * 600.0
            samples.append(env * 0.4 * math.sin(2 * math.pi * freq * t))
        self._write_wav("click.wav", samples)

        # 2. Flag: bright chime (60ms)
        samples = []
        n_samples = int(self.sample_rate * 0.06)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 40.0)
            samples.append(env * 0.5 * math.sin(2 * math.pi * 987.77 * t))
        self._write_wav("flag.wav", samples)

        # 3. Unflag: descending blip (40ms)
        samples = []
        n_samples = int(self.sample_rate * 0.04)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 50.0)
            freq = 800.0 - (i / n_samples) * 350.0
            samples.append(env * 0.4 * math.sin(2 * math.pi * freq * t))
        self._write_wav("unflag.wav", samples)

        # 4. Cascade: water drop pop (35ms)
        samples = []
        n_samples = int(self.sample_rate * 0.035)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = math.sin(math.pi * i / n_samples) ** 0.5
            freq = 450.0 + (i / n_samples) * 350.0
            samples.append(env * 0.35 * math.sin(2 * math.pi * freq * t))
        self._write_wav("cascade.wav", samples)

        # 5. Chord: two-tone harmonic blip (70ms)
        samples = []
        n_samples = int(self.sample_rate * 0.07)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 30.0)
            s1 = math.sin(2 * math.pi * 523.25 * t)  # C5
            s2 = math.sin(2 * math.pi * 659.25 * t)  # E5
            samples.append(env * 0.4 * (0.6 * s1 + 0.4 * s2))
        self._write_wav("chord.wav", samples)

        # 6. Explode: noise rumble and impact (350ms)
        samples = []
        n_samples = int(self.sample_rate * 0.35)
        import random
        rnd = random.Random(42)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = (1.0 - i / n_samples) ** 1.8
            noise = (rnd.random() * 2.0 - 1.0) * 0.6
            sub_bass = math.sin(2 * math.pi * (140.0 - t * 200.0) * t) * 0.4
            samples.append(env * (noise + sub_bass) * 0.8)
        self._write_wav("explode.wav", samples)

        # 7. Win Fanfare: arpeggio victory jingle (450ms)
        samples = []
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        note_duration = 0.10
        for idx, freq in enumerate(notes):
            n_samples = int(self.sample_rate * note_duration)
            for i in range(n_samples):
                t = i / self.sample_rate
                env = math.exp(-t * 15.0)
                samples.append(env * 0.45 * math.sin(2 * math.pi * freq * t))
        self._write_wav("win.wav", samples)

        # 8. Shield: energy bounce zap (200ms)
        samples = []
        n_samples = int(self.sample_rate * 0.20)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 12.0)
            freq = 400.0 + 800.0 * math.sin(2 * math.pi * 15.0 * t)
            samples.append(env * 0.45 * math.sin(2 * math.pi * freq * t))
        self._write_wav("shield.wav", samples)

        # 9. Clock tick (15ms)
        samples = []
        n_samples = int(self.sample_rate * 0.015)
        for i in range(n_samples):
            t = i / self.sample_rate
            env = (1.0 - i / n_samples)
            samples.append(env * 0.25 * math.sin(2 * math.pi * 1800.0 * t))
        self._write_wav("tick.wav", samples)

    def play(self, sound_name: str) -> None:
        """Plays sound asynchronously in background thread without interrupting game."""
        if not self.enabled:
            return

        def _play_worker():
            wav_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
            if os.path.exists(wav_path):
                try:
                    subprocess.run(
                        ["afplay", wav_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False
                    )
                except Exception:
                    pass

        threading.Thread(target=_play_worker, daemon=True).start()

    def toggle_sound(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled
