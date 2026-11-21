"""Archer Bubble Blast - Procedural Audio Generator with NumPy"""
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

    def _synthesize_all_sounds(self):
        self.sounds["shoot"] = self._create_arrow_twang()
        self.sounds["pop"] = self._create_bubble_pop()
        self.sounds["bounce"] = self._create_bubble_bounce()
        self.sounds["powerup"] = self._create_powerup_chime()
        self.sounds["hurt"] = self._create_hurt_sound()
        self.sounds["victory"] = self._create_victory_fanfare()
        self.sounds["game_over"] = self._create_defeat_sound()

    def _create_arrow_twang(self) -> pygame.mixer.Sound:
        """Bowstring release twang and rising arrow whistle."""
        duration = 0.12
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # String twang (damped 420Hz) + rising arrow whistle (700Hz -> 1400Hz)
        twang = np.sin(2 * np.pi * 380.0 * t) * np.exp(-t * 40)
        freq = 700.0 + 700.0 * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        whistle = np.sin(phase) * np.exp(-t * 18) * 0.6
        signal = (twang * 0.7 + whistle) * 0.75
        return self._to_sound(signal)

    def _create_bubble_pop(self) -> pygame.mixer.Sound:
        """Juicy balloon/bubble burst."""
        duration = 0.09
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 400.0 + 950.0 * (1.0 - np.exp(-t * 55))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        body = np.sin(phase) * np.exp(-t * 40)
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 90) * 0.4
        signal = (body + noise) * 0.8
        return self._to_sound(signal)

    def _create_bubble_bounce(self) -> pygame.mixer.Sound:
        """Rubbery floor impact thud."""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 160.0 * t) * np.exp(-t * 35)
        return self._to_sound(wave * 0.4)

    def _create_powerup_chime(self) -> pygame.mixer.Sound:
        duration = 0.22
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        t1 = t[t < 0.11]
        t2 = t[t >= 0.11] - 0.11
        w1 = np.sin(2 * np.pi * 587.33 * t1) * np.exp(-t1 * 14)
        w2 = np.sin(2 * np.pi * 880.00 * t2) * np.exp(-t2 * 14)
        signal = np.concatenate([w1, w2]) * 0.65
        return self._to_sound(signal)

    def _create_hurt_sound(self) -> pygame.mixer.Sound:
        duration = 0.18
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 140.0 * t) * (np.random.rand(len(t)) * 1.5 - 0.75) * np.exp(-t * 15)
        return self._to_sound(wave * 0.7)

    def _create_victory_fanfare(self) -> pygame.mixer.Sound:
        duration = 0.65
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        f1 = np.sin(2 * np.pi * 523.25 * t) * np.exp(-t * 5)
        f2 = np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 6) * 0.8
        f3 = np.sin(2 * np.pi * 783.99 * t) * np.exp(-t * 7) * 0.7
        signal = (f1 + f2 + f3) * 0.5
        return self._to_sound(signal)

    def _create_defeat_sound(self) -> pygame.mixer.Sound:
        duration = 0.5
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 300.0 * np.exp(-t * 3.5)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 5)
        return self._to_sound(wave * 0.6)

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
