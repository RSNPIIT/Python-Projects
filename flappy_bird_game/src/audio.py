"""
audio.py - Procedural 8-bit Arcade Sound Synthesizer & SoundManager for KFlapper.
Synthesizes retro audio in-memory with zero external file dependencies.
"""

import io
import math
import os
import random
import struct
import wave
import pygame


class SoundManager:
    """Generates, manages, and plays crisp retro sound effects."""

    def __init__(self, asset_dir: str):
        self.asset_dir = asset_dir
        self.sounds_dir = os.path.join(asset_dir, "sounds")
        os.makedirs(self.sounds_dir, exist_ok=True)
        self.sample_rate = 22050
        self.muted = False
        self.sounds = {}

        self._init_sounds()

    def _generate_wav_bytes(self, samples: list) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)  # Mono
            w.setsampwidth(2)  # 16-bit
            w.setframerate(self.sample_rate)

            raw = bytearray()
            for s in samples:
                val = max(-32767, min(32767, int(s * 32767.0)))
                raw.extend(struct.pack("<h", val))
            w.writeframes(raw)
        return buf.getvalue()

    def _init_sounds(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except Exception:
            return

        # 1. Flap: quick wing flap whoosh (75ms)
        n = int(self.sample_rate * 0.075)
        samples = []
        for i in range(n):
            t = i / self.sample_rate
            env = math.sin(math.pi * i / n) ** 0.8
            freq = 520.0 - (i / n) * 260.0
            noise = (random.random() * 2 - 1) * 0.2
            tone = math.sin(2 * math.pi * freq * t) * 0.8
            samples.append(env * 0.5 * (tone + noise))
        self._register_sound("flap", samples)

        # 2. Point: crystal two-tone arcade chime (140ms)
        n = int(self.sample_rate * 0.14)
        samples = []
        n_half = n // 2
        for i in range(n):
            t = i / self.sample_rate
            if i < n_half:
                env = math.exp(-t * 22.0)
                freq = 987.77  # B5
            else:
                t2 = (i - n_half) / self.sample_rate
                env = math.exp(-t2 * 20.0)
                freq = 1318.51  # E6
            samples.append(env * 0.5 * math.sin(2 * math.pi * freq * t))
        self._register_sound("point", samples)

        # 3. Hit: crunchy pipe crash thud (110ms)
        n = int(self.sample_rate * 0.11)
        samples = []
        rnd = random.Random(1337)
        for i in range(n):
            t = i / self.sample_rate
            env = (1.0 - i / n) ** 2.2
            noise = (rnd.random() * 2 - 1) * 0.65
            sub = math.sin(2 * math.pi * (180.0 - t * 300.0) * t) * 0.5
            samples.append(env * 0.65 * (noise + sub))
        self._register_sound("hit", samples)

        # 4. Die: pitch drop slide (260ms)
        n = int(self.sample_rate * 0.26)
        samples = []
        for i in range(n):
            t = i / self.sample_rate
            env = (1.0 - i / n) ** 1.3
            freq = 460.0 - (i / n) * 350.0
            samples.append(env * 0.55 * math.sin(2 * math.pi * freq * t))
        self._register_sound("die", samples)

        # 5. Swoosh: smooth UI whoosh (100ms)
        n = int(self.sample_rate * 0.10)
        samples = []
        for i in range(n):
            t = i / self.sample_rate
            env = math.sin(math.pi * i / n)
            freq = 320.0 + (i / n) * 380.0
            noise = (random.random() * 2 - 1) * 0.35
            samples.append(env * 0.4 * (math.sin(2 * math.pi * freq * t) * 0.65 + noise))
        self._register_sound("swoosh", samples)

        # 6. Medal: celebratory victory fanfare (360ms)
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        note_dur = 0.09
        samples = []
        for note_f in notes:
            sub_n = int(self.sample_rate * note_dur)
            for i in range(sub_n):
                t = i / self.sample_rate
                env = math.exp(-t * 16.0)
                samples.append(env * 0.45 * math.sin(2 * math.pi * note_f * t))
        self._register_sound("medal", samples)

    def _register_sound(self, name: str, samples: list):
        try:
            wav_data = self._generate_wav_bytes(samples)
            # Also persist to assets/sounds
            fpath = os.path.join(self.sounds_dir, f"{name}.wav")
            with open(fpath, "wb") as f:
                f.write(wav_data)

            sound = pygame.mixer.Sound(io.BytesIO(wav_data))
            sound.set_volume(0.65)
            self.sounds[name] = sound
        except Exception:
            pass

    def play(self, sound_name: str):
        if self.muted or sound_name not in self.sounds:
            return
        try:
            self.sounds[sound_name].play()
        except Exception:
            pass

    def play_flap(self):
        self.play("flap")

    def play_point(self):
        self.play("point")

    def play_hit(self):
        self.play("hit")

    def play_die(self):
        self.play("die")

    def play_swoosh(self):
        self.play("swoosh")

    def play_medal(self):
        self.play("medal")

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        return self.muted
