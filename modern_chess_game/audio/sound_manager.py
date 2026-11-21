"""Modern Chess Game - Procedural Sound Generator using NumPy & Pygame"""
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
            print(f"[SoundManager] Audio initialization disabled: {e}")
            self.enabled = False

    def _synthesize_all_sounds(self):
        """Generate procedural tactile sound effects directly via NumPy."""
        self.sounds["move"] = self._create_wood_thud()
        self.sounds["capture"] = self._create_capture_snap()
        self.sounds["castle"] = self._create_castle_slide()
        self.sounds["check"] = self._create_check_bell()
        self.sounds["game_over"] = self._create_game_over_chime()

    def _create_wood_thud(self) -> pygame.mixer.Sound:
        """Procedural tactile wooden piece drop sound."""
        duration = 0.09
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Wood resonance frequency ~280Hz with quick pitch drop
        freq = 320.0 * np.exp(-t * 25)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        body = np.sin(phase) * np.exp(-t * 35)

        # Subtle noise transient at the start (contact click)
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 120) * 0.4
        signal = (body + noise) * 0.75
        return self._numpy_to_sound(signal)

    def _create_capture_snap(self) -> pygame.mixer.Sound:
        """Crisp piece capture impact sound."""
        duration = 0.12
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Higher initial transient snapping from 650Hz down to 180Hz
        freq = 650.0 * np.exp(-t * 30)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        body = np.sin(phase) * np.exp(-t * 28)

        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 90) * 0.6
        signal = (body + noise) * 0.85
        return self._numpy_to_sound(signal)

    def _create_castle_slide(self) -> pygame.mixer.Sound:
        """Double slide sound for castling."""
        duration = 0.22
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # First thump at t=0
        s1 = np.sin(2 * np.pi * 260 * t) * np.exp(-t * 40)
        # Second thump at t=0.10
        t2 = np.maximum(0, t - 0.09)
        s2 = np.sin(2 * np.pi * 320 * t2) * np.exp(-t2 * 40) * (t >= 0.09)
        signal = (s1 + s2) * 0.7
        return self._numpy_to_sound(signal)

    def _create_check_bell(self) -> pygame.mixer.Sound:
        """Harmonic bell ping for check."""
        duration = 0.35
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Two harmonic frequencies ringing: 587.3 Hz (D5) & 880.0 Hz (A5)
        bell1 = np.sin(2 * np.pi * 587.3 * t) * np.exp(-t * 10)
        bell2 = np.sin(2 * np.pi * 880.0 * t) * np.exp(-t * 14) * 0.5
        signal = (bell1 + bell2) * 0.6
        return self._numpy_to_sound(signal)

    def _create_game_over_chime(self) -> pygame.mixer.Sound:
        """Resolution chord for game completion."""
        duration = 0.6
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        f1 = np.sin(2 * np.pi * 440.0 * t) * np.exp(-t * 6)
        f2 = np.sin(2 * np.pi * 554.37 * t) * np.exp(-t * 7) * 0.8
        f3 = np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 8) * 0.7
        signal = (f1 + f2 + f3) * 0.4
        return self._numpy_to_sound(signal)

    def _numpy_to_sound(self, signal: np.ndarray) -> pygame.mixer.Sound:
        # Normalize and convert to 16-bit stereo PCM
        signal = np.clip(signal, -1.0, 1.0)
        pcm_mono = (signal * 32767).astype(np.int16)
        # Duplicate to stereo (channels=2)
        pcm_stereo = np.column_stack((pcm_mono, pcm_mono))
        return pygame.sndarray.make_sound(pcm_stereo)

    def play(self, sound_name: str):
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            self.sounds[sound_name].play()
        except Exception:
            pass
