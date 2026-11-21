"""Block Blast - Procedural Sound Generator with NumPy & Pygame"""
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
        except Exception as e:
            self.enabled = False

    def _synthesize_all_sounds(self):
        self.sounds["shoot"] = self._create_rocket_whoosh()
        self.sounds["hit"] = self._create_impact_click()
        self.sounds["explode"] = self._create_explosion()
        self.sounds["powerup"] = self._create_powerup_chime()
        self.sounds["warning"] = self._create_warning_buzz()
        self.sounds["game_over"] = self._create_game_over()

    def _create_rocket_whoosh(self) -> pygame.mixer.Sound:
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Pitch sliding down rapidly from 850Hz to 280Hz
        freq = 850.0 * np.exp(-t * 15)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        body = np.sin(phase) * np.exp(-t * 22)
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 40) * 0.25
        signal = (body + noise) * 0.55
        return self._to_sound(signal)

    def _create_impact_click(self) -> pygame.mixer.Sound:
        duration = 0.04
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 920.0 * t) * np.exp(-t * 80)
        return self._to_sound(wave * 0.45)

    def _create_explosion(self) -> pygame.mixer.Sound:
        duration = 0.28
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Heavy sub-bass frequency decay
        freq = 140.0 * np.exp(-t * 10)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        sub = np.sin(phase) * np.exp(-t * 7)
        # Textured crunch noise
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 12) * 0.7
        signal = (sub + noise) * 0.8
        return self._to_sound(signal)

    def _create_powerup_chime(self) -> pygame.mixer.Sound:
        duration = 0.22
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Rising melodic arpeggio
        t1 = t[t < 0.11]
        t2 = t[t >= 0.11] - 0.11
        w1 = np.sin(2 * np.pi * 587.3 * t1) * np.exp(-t1 * 12)  # D5
        w2 = np.sin(2 * np.pi * 880.0 * t2) * np.exp(-t2 * 12)  # A5
        signal = np.concatenate([w1, w2]) * 0.6
        return self._to_sound(signal)

    def _create_warning_buzz(self) -> pygame.mixer.Sound:
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 420.0 * t) * (1.0 + 0.5 * np.sin(2 * np.pi * 30 * t)) * np.exp(-t * 8)
        return self._to_sound(wave * 0.5)

    def _create_game_over(self) -> pygame.mixer.Sound:
        duration = 0.5
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 340.0 * np.exp(-t * 4)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 5)
        return self._to_sound(wave * 0.65)

    def _to_sound(self, signal: np.ndarray) -> pygame.mixer.Sound:
        signal = np.clip(signal, -1.0, 1.0)
        pcm = (signal * 32767).astype(np.int16)
        stereo = np.column_stack((pcm, pcm))
        return pygame.sndarray.make_sound(stereo)

    def play(self, sound_name: str):
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            self.sounds[sound_name].play()
        except Exception:
            pass
