"""2048 Game - Procedural Audio Generator with NumPy"""
import math
import numpy as np
import pygame

class SoundManager:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            self._synthesize_all_sounds()
        except Exception:
            self.enabled = False

    def toggle_sound(self) -> bool:
        """Toggles sound on/off."""
        self.enabled = not self.enabled
        return self.enabled

    def play(self, name: str):
        if not self.enabled or name not in self.sounds:
            return
        try:
            self.sounds[name].play()
        except Exception:
            pass

    def play_merge(self, value: int):
        """Plays a musical chime whose pitch scales with the merged tile value."""
        if not self.enabled:
            return
        sound_key = f"merge_{value}"
        if sound_key not in self.sounds:
            self.sounds[sound_key] = self._create_merge_tone(value)
        self.play(sound_key)

    def _to_sound(self, mono_samples: np.ndarray) -> pygame.mixer.Sound:
        """Converts float numpy array (-1.0 to 1.0) to 16-bit stereo pygame Sound."""
        clamped = np.clip(mono_samples, -1.0, 1.0)
        int16 = (clamped * 32767).astype(np.int16)
        stereo = np.column_stack((int16, int16))
        return pygame.sndarray.make_sound(stereo)

    def _synthesize_all_sounds(self):
        self.sounds["slide"] = self._create_slide_swoosh()
        self.sounds["spawn"] = self._create_spawn_tap()
        self.sounds["victory"] = self._create_victory_fanfare()
        self.sounds["game_over"] = self._create_game_over_chime()
        self.sounds["click"] = self._create_button_click()
        self.sounds["undo"] = self._create_undo_chime()

        # Pre-synthesize common merge tones
        for val in [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]:
            self.sounds[f"merge_{val}"] = self._create_merge_tone(val)

    def _create_slide_swoosh(self) -> pygame.mixer.Sound:
        """Subtle soft sliding whoosh."""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # White noise band-passed with exponential decay
        noise = np.random.uniform(-1.0, 1.0, len(t))
        envelope = np.sin(np.pi * (t / duration)) ** 2
        f = np.linspace(250, 180, len(t))
        tone = np.sin(2 * np.pi * f * t) * 0.4 + noise * 0.15
        wave = tone * envelope * 0.25
        return self._to_sound(wave)

    def _create_spawn_tap(self) -> pygame.mixer.Sound:
        """Crisp gentle spawn tap."""
        duration = 0.04
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 520.0 * t) * np.exp(-t * 60) * 0.2
        return self._to_sound(wave)

    def _create_merge_tone(self, value: int) -> pygame.mixer.Sound:
        """Harmonic musical bell chime scaling in pitch by tier."""
        # Tier exponent: 4 -> 1, 8 -> 2, 16 -> 3, ..., 2048 -> 10
        tier = max(1, int(round(math.log2(value))) - 1)
        # Pentatonic scale semitones: C, D, E, G, A
        pentatonic = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28]
        semitones = pentatonic[min(tier - 1, len(pentatonic) - 1)]
        freq = 329.63 * (2.0 ** (semitones / 12.0))  # Base E4

        duration = 0.18 + min(0.12, tier * 0.015)
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Fundamental + subtle octave overtone
        f1 = np.sin(2 * np.pi * freq * t) * np.exp(-t * 14.0)
        f2 = np.sin(2 * np.pi * (freq * 2.0) * t) * np.exp(-t * 22.0) * 0.35
        wave = (f1 + f2) * 0.45
        return self._to_sound(wave)

    def _create_victory_fanfare(self) -> pygame.mixer.Sound:
        """Triumphant ascending arpeggio when hitting 2048."""
        notes = [523.25, 659.25, 783.99, 1046.50, 1318.51]  # C5, E5, G5, C6, E6
        note_dur = 0.10
        total_samples = int(self.sample_rate * (note_dur * len(notes) + 0.3))
        wave = np.zeros(total_samples)

        for i, f in enumerate(notes):
            start = int(i * note_dur * self.sample_rate)
            t = np.linspace(0, 0.4, int(self.sample_rate * 0.4), False)
            tone = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * (f * 2) * t)) * np.exp(-t * 8.0)
            end = min(total_samples, start + len(tone))
            wave[start:end] += tone[:end - start] * 0.4

        return self._to_sound(wave)

    def _create_game_over_chime(self) -> pygame.mixer.Sound:
        """Melancholy descending tone."""
        duration = 0.45
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = np.linspace(340.0, 180.0, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * (1.0 - t / duration) * np.exp(-t * 3.0) * 0.45
        return self._to_sound(wave)

    def _create_button_click(self) -> pygame.mixer.Sound:
        """Subtle mechanical click."""
        duration = 0.03
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 900.0 * t) * np.exp(-t * 120.0) * 0.25
        return self._to_sound(wave)

    def _create_undo_chime(self) -> pygame.mixer.Sound:
        """Rewind soft descending tick."""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * np.linspace(600, 300, len(t)) * t) * np.exp(-t * 25.0) * 0.3
        return self._to_sound(wave)
