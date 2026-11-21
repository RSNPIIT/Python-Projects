"""Bubble Blast - Procedural Sound Synthesis with NumPy & Pygame"""
import numpy as np
import pygame

class SoundManager:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.chain_sounds: list[pygame.mixer.Sound] = []

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            self._synthesize_all_sounds()
        except Exception:
            self.enabled = False

    def _synthesize_all_sounds(self):
        self.sounds["pop"] = self._create_pop()
        self.sounds["advance"] = self._create_bloop()
        self.sounds["victory"] = self._create_victory_chime()
        self.sounds["game_over"] = self._create_defeat_tone()
        self.sounds["tap"] = self._create_tap()

        # Chain combo tones (ascending pentatonic scale)
        base_freqs = [392.0, 440.0, 493.88, 587.33, 659.25, 783.99, 880.0, 987.77, 1046.50]
        for f in base_freqs:
            self.chain_sounds.append(self._create_chain_ping(f))

    def _create_pop(self) -> pygame.mixer.Sound:
        """Crisp liquid bubble pop."""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Fast upward sweep then damp
        freq = 320.0 + 800.0 * (1.0 - np.exp(-t * 60))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 45)
        # Add high pop snap
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 90) * 0.35
        signal = (wave + noise) * 0.7
        return self._to_sound(signal)

    def _create_bloop(self) -> pygame.mixer.Sound:
        """Juicy water droplet bloop."""
        duration = 0.10
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 300.0 + 350.0 * np.sin(np.pi * t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 28)
        return self._to_sound(wave * 0.6)

    def _create_tap(self) -> pygame.mixer.Sound:
        duration = 0.04
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 550 * t) * np.exp(-t * 70)
        return self._to_sound(wave * 0.5)

    def _create_chain_ping(self, base_freq: float) -> pygame.mixer.Sound:
        duration = 0.16
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        w1 = np.sin(2 * np.pi * base_freq * t) * np.exp(-t * 18)
        w2 = np.sin(2 * np.pi * base_freq * 2.0 * t) * np.exp(-t * 25) * 0.4
        return self._to_sound((w1 + w2) * 0.65)

    def _create_victory_chime(self) -> pygame.mixer.Sound:
        duration = 0.6
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # C major triad arpeggio
        f1 = np.sin(2 * np.pi * 523.25 * t) * np.exp(-t * 6)
        f2 = np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 7) * 0.8
        f3 = np.sin(2 * np.pi * 783.99 * t) * np.exp(-t * 8) * 0.7
        return self._to_sound((f1 + f2 + f3) * 0.45)

    def _create_defeat_tone(self) -> pygame.mixer.Sound:
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = 280.0 * np.exp(-t * 4)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase) * np.exp(-t * 6)
        return self._to_sound(wave * 0.5)

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

    def play_combo_chain(self, combo_index: int):
        if not self.enabled or not self.chain_sounds:
            return
        idx = min(len(self.chain_sounds) - 1, combo_index)
        try:
            self.chain_sounds[idx].play()
        except Exception:
            pass
