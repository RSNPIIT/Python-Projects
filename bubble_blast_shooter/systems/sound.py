"""Bubble Blast Shooter - Procedural Audio with NumPy"""
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
        self.sounds["shoot"] = self._create_shoot_whoosh()
        self.sounds["bounce"] = self._create_wall_clink()
        self.sounds["snap"] = self._create_bubble_snap()
        self.sounds["pop"] = self._create_bubble_pop()
        self.sounds["avalanche"] = self._create_avalanche_chime()
        self.sounds["victory"] = self._create_victory_fanfare()
        self.sounds["game_over"] = self._create_defeat_sound()

    def _create_shoot_whoosh(self) -> pygame.mixer.Sound:
        """Pneumatic bubble launch swoosh."""
        duration = 0.12
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Rising frequency sweep: 240Hz -> 680Hz
        freq = 240.0 + 440.0 * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 22)
        return self._to_sound(wave * 0.7)

    def _create_wall_clink(self) -> pygame.mixer.Sound:
        """Crisp rubber wall ricochet clink."""
        duration = 0.06
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 920.0 * t) * np.exp(-t * 60)
        return self._to_sound(wave * 0.45)

    def _create_bubble_snap(self) -> pygame.mixer.Sound:
        """Suction snap when bubble locks into the grid."""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 600.0 - 280.0 * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 35)
        return self._to_sound(wave * 0.6)

    def _create_bubble_pop(self) -> pygame.mixer.Sound:
        """Juicy balloon/bubble match pop."""
        duration = 0.11
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 450.0 + 850.0 * (1.0 - np.exp(-t * 45))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        body = np.sin(phase) * np.exp(-t * 30)
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 70) * 0.35
        signal = (body + noise) * 0.75
        return self._to_sound(signal)

    def _create_avalanche_chime(self) -> pygame.mixer.Sound:
        """Cascading chime when disconnected orphan clusters fall."""
        duration = 0.35
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        c1 = np.sin(2 * np.pi * 523.25 * t) * np.exp(-t * 8)
        c2 = np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 9)
        c3 = np.sin(2 * np.pi * 783.99 * t) * np.exp(-t * 10)
        signal = (c1 + c2 + c3) * 0.45
        return self._to_sound(signal)

    def _create_victory_fanfare(self) -> pygame.mixer.Sound:
        """Major triad triumphant fanfare."""
        duration = 0.6
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        f1 = np.sin(2 * np.pi * 523.25 * t) * np.exp(-t * 4.5)
        f2 = np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 5.5) * 0.8
        f3 = np.sin(2 * np.pi * 1046.50 * t) * np.exp(-t * 6.5) * 0.7
        signal = (f1 + f2 + f3) * 0.5
        return self._to_sound(signal)

    def _create_defeat_sound(self) -> pygame.mixer.Sound:
        """Downward sliding tone on defeat."""
        duration = 0.5
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 320.0 * np.exp(-t * 3.0)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 4)
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
