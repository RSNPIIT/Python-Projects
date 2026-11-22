"""Kapman Game - Procedural Audio Generator with NumPy"""
import numpy as np
import pygame

class SoundManager:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.chomp_toggle = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            self._synthesize_all_sounds()
        except Exception:
            self.enabled = False

    def _synthesize_all_sounds(self):
        self.sounds["chomp_a"] = self._create_chomp_tone(pitch_up=True)
        self.sounds["chomp_b"] = self._create_chomp_tone(pitch_up=False)
        self.sounds["energizer"] = self._create_energizer_tone()
        self.sounds["eat_ghost"] = self._create_ghost_eaten_chime()
        self.sounds["death"] = self._create_death_sound()
        self.sounds["bonus"] = self._create_bonus_chime()
        self.sounds["victory"] = self._create_victory_fanfare()

    def play_chomp(self):
        if not self.enabled:
            return
        snd_name = "chomp_a" if self.chomp_toggle else "chomp_b"
        self.chomp_toggle = not self.chomp_toggle
        self.play(snd_name)

    def _create_chomp_tone(self, pitch_up: bool) -> pygame.mixer.Sound:
        """Classic waka-waka pill chomp."""
        duration = 0.06
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        f_start = 380.0 if pitch_up else 520.0
        f_end = 560.0 if pitch_up else 340.0
        freq = np.linspace(f_start, f_end, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 30)
        return self._to_sound(wave * 0.45)

    def _create_energizer_tone(self) -> pygame.mixer.Sound:
        """Low mystical power pulse when grabbing solar orb."""
        duration = 0.18
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 180.0 * t) * (1.0 + 0.3 * np.sin(2 * np.pi * 25.0 * t))
        wave *= np.exp(-t * 12)
        return self._to_sound(wave * 0.6)

    def _create_ghost_eaten_chime(self) -> pygame.mixer.Sound:
        """Triumphant ascending two-tone mummy capture chime."""
        duration = 0.22
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        t1 = t[t < 0.11]
        t2 = t[t >= 0.11] - 0.11
        w1 = np.sin(2 * np.pi * 587.33 * t1) * np.exp(-t1 * 12)
        w2 = np.sin(2 * np.pi * 880.00 * t2) * np.exp(-t2 * 12)
        wave = np.concatenate([w1, w2]) * 0.65
        return self._to_sound(wave)

    def _create_death_sound(self) -> pygame.mixer.Sound:
        """Descending chromatic collapse on ghost capture."""
        duration = 0.55
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 480.0 * np.exp(-t * 4.0)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * (1.0 - t / duration)
        return self._to_sound(wave * 0.6)

    def _create_bonus_chime(self) -> pygame.mixer.Sound:
        """Sparkling high treasure collect chime."""
        duration = 0.25
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        f1 = np.sin(2 * np.pi * 783.99 * t) * np.exp(-t * 10)
        f2 = np.sin(2 * np.pi * 1046.50 * t) * np.exp(-t * 12) * 0.8
        f3 = np.sin(2 * np.pi * 1318.51 * t) * np.exp(-t * 14) * 0.6
        return self._to_sound((f1 + f2 + f3) * 0.5)

    def _create_victory_fanfare(self) -> pygame.mixer.Sound:
        """Triumphant level clear fanfare."""
        duration = 0.65
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        f1 = np.sin(2 * np.pi * 523.25 * t) * np.exp(-t * 5)
        f2 = np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 6) * 0.8
        f3 = np.sin(2 * np.pi * 783.99 * t) * np.exp(-t * 7) * 0.7
        f4 = np.sin(2 * np.pi * 1046.50 * t) * np.exp(-t * 8) * 0.6
        return self._to_sound((f1 + f2 + f3 + f4) * 0.45)

    def _to_sound(self, signal: np.ndarray) -> pygame.mixer.Sound:
        signal = np.clip(signal, -1.0, 1.0)
        pcm = (signal * 32767).astype(np.int16)
        stereo = np.column_stack((pcm, pcm))
        return pygame.sndarray.make_sound(stereo)

    def play(self, name: str):
        if not self.enabled or name not in self.sounds:
            return
        try:
            self.sounds[name].play()
        except Exception:
            pass
