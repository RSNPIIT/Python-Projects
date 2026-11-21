"""
synth.py - Procedural 8-bit & Synthwave Audio Synthesizer for Reimagined Tetris.
Generates rich, clean stereo waveforms (sine, square, saw, noise, FM) using NumPy.
"""

import numpy as np
import pygame


class SoundSynthesizer:
    SAMPLE_RATE = 44100

    @classmethod
    def _to_pygame_sound(cls, samples_left, samples_right=None):
        if samples_right is None:
            samples_right = samples_left
        samples_left = np.clip(samples_left, -1.0, 1.0)
        samples_right = np.clip(samples_right, -1.0, 1.0)
        int_l = (samples_left * 32767).astype(np.int16)
        int_r = (samples_right * 32767).astype(np.int16)
        stereo = np.column_stack((int_l, int_r))
        return pygame.sndarray.make_sound(stereo)

    @classmethod
    def gen_move(cls):
        # Snappy high-frequency blip
        duration = 0.04
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        freq = np.linspace(420, 680, len(t))
        wave = np.sin(2 * np.pi * freq * t)
        env = np.exp(-t * 90)
        samples = wave * env * 0.35
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_rotate(cls):
        # Smooth futuristic frequency sweep
        duration = 0.075
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        freq = 320 + 380 * np.sin(np.pi * t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / cls.SAMPLE_RATE
        wave = 0.7 * np.sin(phase) + 0.3 * np.sin(2 * phase)
        env = np.sin(np.pi * t / duration)
        samples = wave * env * 0.40
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_soft_drop(cls):
        # Subtle gentle click
        duration = 0.035
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        wave = np.sin(2 * np.pi * 260 * t)
        env = np.exp(-t * 120)
        samples = wave * env * 0.22
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_hard_drop(cls):
        # Punchy sub-bass drop thud + click
        duration = 0.16
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        freq = 160 * np.exp(-t * 18) + 40
        phase = 2 * np.pi * np.cumsum(freq) / cls.SAMPLE_RATE
        sub = np.sin(phase)
        noise = np.random.uniform(-0.15, 0.15, len(t)) * np.exp(-t * 60)
        env = np.exp(-t * 14)
        samples = (sub * 0.75 + noise * 0.25) * env * 0.70
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_lock(cls):
        # Solid mechanical snap
        duration = 0.08
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        freq = 240 * np.exp(-t * 25) + 60
        phase = 2 * np.pi * np.cumsum(freq) / cls.SAMPLE_RATE
        click = np.sin(phase) + 0.2 * np.random.uniform(-1, 1, len(t))
        env = np.exp(-t * 35)
        samples = click * env * 0.45
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_hold(cls):
        # Dual-tone harmonic whoosh
        duration = 0.11
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        tone1 = np.sin(2 * np.pi * 520 * t)
        tone2 = np.sin(2 * np.pi * 780 * t)
        env = np.sin(np.pi * t / duration)
        samples = (tone1 * 0.5 + tone2 * 0.5) * env * 0.42
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_line_clear(cls, lines=1):
        # Melodic multi-note triad ping based on lines cleared
        duration = 0.22
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        base_freqs = [440, 554, 659, 880]  # A major triad
        count = min(lines, 4)
        wave = np.zeros_like(t)
        for i in range(count):
            offset_t = t - i * 0.035
            mask = offset_t >= 0
            f = base_freqs[i]
            part = np.sin(2 * np.pi * f * offset_t[mask]) * np.exp(-offset_t[mask] * 12)
            wave[mask] += part * 0.4
        samples = wave * 0.65
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_tetris(cls):
        # Epic 4-line Tetris fanfare with stereo sweep
        duration = 0.55
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        chord_freqs = [523.25, 659.25, 783.99, 1046.50]  # C Major
        wave_l = np.zeros_like(t)
        wave_r = np.zeros_like(t)
        for idx, f in enumerate(chord_freqs):
            delay = idx * 0.06
            active_mask = t >= delay
            t_sub = t[active_mask] - delay
            sub_wave = (
                0.6 * np.sin(2 * np.pi * f * t_sub)
                + 0.25 * np.sin(4 * np.pi * f * t_sub)
                + 0.15 * np.sin(6 * np.pi * f * t_sub)
            ) * np.exp(-t_sub * 4.5)
            pan = (idx / 3.0)  # Stereo spread
            wave_l[active_mask] += sub_wave * (1.0 - pan * 0.6)
            wave_r[active_mask] += sub_wave * (0.4 + pan * 0.6)
        samples_l = wave_l * 0.45
        samples_r = wave_r * 0.45
        return cls._to_pygame_sound(samples_l, samples_r)

    @classmethod
    def gen_tspin(cls):
        # Sci-fi resonant warp
        duration = 0.28
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        mod = 80 * np.sin(2 * np.pi * 32 * t)
        freq = 380 + mod
        phase = 2 * np.pi * np.cumsum(freq) / cls.SAMPLE_RATE
        wave = np.sin(phase) + 0.3 * np.sin(2 * phase)
        env = np.sin(np.pi * t / duration)
        samples = wave * env * 0.55
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_combo(cls, count=1):
        # Ascending pitch scale based on combo count
        duration = 0.14
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        base_f = 400 + min(count, 12) * 55
        wave = np.sin(2 * np.pi * base_f * t) + 0.35 * np.sin(4 * np.pi * base_f * t)
        env = np.exp(-t * 15)
        samples = wave * env * 0.45
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_levelup(cls):
        # Retro arpeggio flourish
        duration = 0.45
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        arp = [330, 440, 554, 659, 880]
        wave = np.zeros_like(t)
        note_dur = 0.08
        for i, f in enumerate(arp):
            start = i * note_dur
            mask = (t >= start) & (t < start + note_dur * 1.5)
            t_sub = t[mask] - start
            part = np.sin(2 * np.pi * f * t_sub) * np.exp(-t_sub * 10)
            wave[mask] += part * 0.5
        samples = wave * 0.6
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_gameover(cls):
        # Dramatic descending bass synth
        duration = 0.65
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        freq = 300 * np.exp(-t * 3.5) + 40
        phase = 2 * np.pi * np.cumsum(freq) / cls.SAMPLE_RATE
        wave = np.sin(phase) + 0.35 * np.sin(3 * phase)
        env = np.exp(-t * 2.5)
        samples = wave * env * 0.65
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_ui_click(cls):
        duration = 0.04
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        wave = np.sin(2 * np.pi * 880 * t)
        env = np.exp(-t * 90)
        samples = wave * env * 0.3
        return cls._to_pygame_sound(samples)

    @classmethod
    def gen_ui_hover(cls):
        duration = 0.03
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), False)
        wave = np.sin(2 * np.pi * 600 * t)
        env = np.exp(-t * 110)
        samples = wave * env * 0.18
        return cls._to_pygame_sound(samples)
