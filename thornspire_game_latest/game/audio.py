"""All sound is synthesized at startup with numpy; no audio files are shipped."""

from __future__ import annotations

import math

import numpy as np
import pygame

SR = 44100


def _t(dur: float) -> np.ndarray:
    return np.arange(int(SR * dur), dtype=np.float64) / SR


def _env(n: int, attack: float = 0.004, decay: float = 0.2,
         curve: float = 1.0) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / SR
    a = np.clip(t / max(1e-5, attack), 0.0, 1.0)
    d = np.exp(-t / max(1e-4, decay))
    if curve != 1.0:
        d = d ** curve
    return a * d


def _sine(freq, dur: float) -> np.ndarray:
    t = _t(dur)
    if np.isscalar(freq):
        phase = 2 * np.pi * float(freq) * t
    else:
        phase = 2 * np.pi * np.cumsum(freq[: len(t)]) / SR
    return np.sin(phase)


def _tri(freq, dur: float) -> np.ndarray:
    t = _t(dur)
    if np.isscalar(freq):
        phase = np.mod(float(freq) * t, 1.0)
    else:
        phase = np.mod(np.cumsum(freq[: len(t)]) / SR, 1.0)
    return 2.0 * np.abs(2.0 * phase - 1.0) - 1.0


def _soft_noise(dur: float, smooth: int = 24, seed: int = 1) -> np.ndarray:
    n = int(SR * dur)
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    if smooth > 1:
        kernel = np.ones(smooth) / smooth
        x = np.convolve(x, kernel, mode="same")
    return x


def _note(midi: float) -> float:
    return 440.0 * 2.0 ** ((midi - 69.0) / 12.0)


def _put(canvas: np.ndarray, start: float, sound: np.ndarray, gain: float = 1.0) -> None:
    i = int(start * SR)
    if i >= len(canvas) or len(sound) == 0:
        return
    n = min(len(sound), len(canvas) - i)
    canvas[i:i + n] += sound[:n] * gain


def _stereo(mono: np.ndarray, pan: float = 0.0) -> pygame.mixer.Sound:
    mono = np.asarray(mono, dtype=np.float64)
    peak = np.max(np.abs(mono)) or 1.0
    mono = mono / peak * 0.82
    left = mono * (1.0 - max(0.0, pan) * 0.55)
    right = mono * (1.0 - max(0.0, -pan) * 0.55)
    data = np.stack([left, right], axis=1)
    data = np.clip(data * 32767.0, -32768, 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.ascontiguousarray(data))


def _sfx_jump():
    dur = 0.17
    f = np.linspace(300, 620, int(SR * dur)) ** 1.05
    wave = _sine(f, dur) + 0.22 * _sine(f * 2, dur)
    return wave * _env(int(SR * dur), 0.004, 0.075) * 0.55


def _sfx_land():
    t = _t(0.12)
    f = np.linspace(140, 80, len(t))
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26)
    noise = _soft_noise(0.12, 30, 9) * np.exp(-t * 40) * 0.25
    return (thud * 0.6 + noise) * 0.7


def _sfx_coin():
    n = int(SR * 0.16)
    out = np.zeros(n)
    a = np.sin(2 * np.pi * 1046.5 * _t(0.09)) * _env(int(SR * 0.09), 0.002, 0.035)
    b = np.sin(2 * np.pi * 1568.0 * _t(0.12)) * _env(int(SR * 0.12), 0.002, 0.05)
    _put(out, 0.0, a, 0.55)
    _put(out, 0.055, b, 0.45)
    return out


def _sfx_gem():
    n = int(SR * 0.75)
    out = np.zeros(n)
    notes = [880, 1108.7, 1318.5, 1760]
    for i, f in enumerate(notes):
        dur = 0.55 - i * 0.06
        t = _t(dur)
        tone = (np.sin(2 * np.pi * f * t) * 0.6
                + np.sin(2 * np.pi * f * 2.003 * t) * 0.18
                + np.sin(2 * np.pi * f * 0.5 * t) * 0.12)
        tone *= _env(int(SR * dur), 0.003, 0.16)
        _put(out, i * 0.065, tone, 0.42)
    return out


def _sfx_heart():
    n = int(SR * 0.42)
    out = np.zeros(n)
    for i, f in enumerate((523.25, 783.99)):
        t = _t(0.3)
        tone = np.sin(2 * np.pi * f * t) * _env(int(SR * 0.3), 0.01, 0.09)
        _put(out, i * 0.09, tone, 0.4)
    return out


def _sfx_armor():
    n = int(SR * 0.6)
    out = np.zeros(n)
    for i, f in enumerate((659.25, 987.77, 1318.5)):
        t = _t(0.5)
        tone = (np.sin(2 * np.pi * f * t) * 0.5
                + np.sin(2 * np.pi * f * 2.01 * t) * 0.16)
        tone *= _env(int(SR * 0.5), 0.004, 0.16)
        _put(out, i * 0.055, tone, 0.32)
    return out


def _sfx_shield():
    n = int(SR * 0.55)
    t = _t(0.55)
    noise = _soft_noise(0.55, 6, 31) * np.exp(-t * 14) * 0.35
    # metallic partials sliding down
    f1 = np.linspace(1900, 900, n)
    f2 = np.linspace(2600, 1200, n)
    metal = (np.sin(2 * np.pi * np.cumsum(f1) / SR)
             + 0.5 * np.sin(2 * np.pi * np.cumsum(f2) / SR)) * np.exp(-t * 8) * 0.22
    thump = np.sin(2 * np.pi * np.linspace(100, 60, n) * t) * np.exp(-t * 12) * 0.2
    return noise + metal + thump


def _sfx_chrono():
    n = int(SR * 0.55)
    out = np.zeros(n)
    for i, f in enumerate((1318.5, 1760.0, 2093.0)):
        t = _t(0.4)
        tone = np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 6 * t) * 1.2)
        tone *= _env(int(SR * 0.4), 0.005, 0.12)
        _put(out, i * 0.06, tone, 0.3)
    return out


def _sfx_hurt():
    n = int(SR * 0.4)
    t = _t(0.4)
    f = np.linspace(150, 55, n)
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 0.7
    noise = _soft_noise(0.4, 12, 3) * np.exp(-t * 12) * 0.4
    return thud + noise


def _sfx_death():
    n = int(SR * 1.4)
    out = np.zeros(n)
    for i, f in enumerate((392.0, 311.1, 246.9, 196.0)):
        t = _t(0.6)
        tone = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 0.5 * t))
        tone *= _env(int(SR * 0.6), 0.008, 0.22)
        _put(out, i * 0.13, tone, 0.36)
    noise = _soft_noise(1.4, 9, 11) * np.linspace(0.35, 0.0, n) ** 1.7
    return out + noise * 0.5


def _sfx_dash():
    n = int(SR * 0.24)
    t = _t(0.24)
    noise = _soft_noise(0.24, 8, 21)
    noise2 = _soft_noise(0.24, 60, 22)
    whoosh = (noise - noise2 * 1.2) * np.exp(-t * 11) * 0.7
    f = np.linspace(180, 520, n)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.18
    return whoosh + body


def _sfx_checkpoint():
    n = int(SR * 1.2)
    out = np.zeros(n)
    for i, f in enumerate((392.0, 523.25, 659.25, 783.99)):
        t = _t(1.0)
        tone = (np.sin(2 * np.pi * f * t) * 0.45
                + np.sin(2 * np.pi * f * 2.0 * t) * 0.1)
        tone *= _env(int(SR * 1.0), 0.05, 0.42)
        _put(out, i * 0.08, tone, 0.32)
    return out


def _sfx_select():
    t = _t(0.07)
    return np.sin(2 * np.pi * 880 * t) * _env(len(t), 0.002, 0.02) * 0.35


def _sfx_loop():
    n = int(SR * 1.1)
    out = np.zeros(n)
    for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        t = _t(0.8)
        tone = np.sin(2 * np.pi * f * t) * _env(int(SR * 0.8), 0.01, 0.28)
        _put(out, i * 0.09, tone, 0.3)
    return out


def _build_music() -> pygame.mixer.Sound:
    bpm = 72.0
    beat = 60.0 / bpm
    bar = beat * 4
    bars = 4
    total = bar * bars
    n = int(SR * total)
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(17)

    chords = [
        (57, 60, 64, 67),   # Am
        (53, 57, 60, 64),   # Fmaj7
        (48, 52, 55, 59),   # Cmaj7
        (55, 59, 62, 67),   # G
    ]

    def place(x, start, gain=1.0, pan=0.0):
        i = int(start * SR)
        if i >= n:
            return
        m = min(len(x), n - i)
        L[i:i + m] += x[:m] * gain * (1.0 - max(0.0, pan) * 0.45)
        R[i:i + m] += x[:m] * gain * (1.0 - max(0.0, -pan) * 0.45)

    for b, chord in enumerate(chords):
        start = b * bar
        # pad: four sustained, detuned voices
        for j, midi in enumerate(chord):
            f = _note(midi - 12)
            t = _t(bar - 0.02)
            env = np.minimum(1.0, t / 0.7) * np.minimum(1.0, (bar - 0.02 - t) / 0.9)
            env = np.clip(env, 0, 1) ** 1.2
            tone = (np.sin(2 * np.pi * f * t)
                    + 0.55 * np.sin(2 * np.pi * f * 1.0035 * t + 0.4)
                    + 0.18 * np.sin(2 * np.pi * f * 2.0 * t))
            place(tone * env, start, 0.028, pan=(j - 1.5) * 0.35)
        # bass plucks on beats 1 and 3
        root = _note(chord[0] - 24)
        for beat_i in (0, 2):
            t = _t(beat * 1.6)
            env = np.exp(-t * 2.3) * np.minimum(1.0, t / 0.01)
            tone = np.sin(2 * np.pi * root * t) + 0.2 * np.sin(2 * np.pi * root * 2 * t)
            place(tone * env, start + beat_i * beat, 0.10, pan=0.0)
        # arpeggio
        arp_notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[3] + 12,
                     chord[1] + 24, chord[2] + 12, chord[3] + 12, chord[1] + 12]
        for k in range(8):
            f = _note(arp_notes[k % len(arp_notes)])
            t = _t(0.55)
            env = np.exp(-t * 5.5) * np.minimum(1.0, t / 0.005)
            tone = (np.sin(2 * np.pi * f * t) * 0.55
                    + np.sin(2 * np.pi * f * 2.0 * t) * 0.12
                    + np.sin(2 * np.pi * f * 3.01 * t) * 0.05)
            place(tone * env, start + k * beat / 2, 0.052, pan=0.35 if k % 2 else -0.35)
        # heartbeat
        for beat_i in (0, 2):
            t = _t(0.3)
            f = np.linspace(70, 45, len(t))
            thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
            place(thump, start + beat_i * beat, 0.12, pan=0.0)
        # airy brush
        brush = _soft_noise(0.25, 80, seed=30 + b) * np.exp(-_t(0.25) * 8)
        place(brush, start + beat * 1.5, 0.02, pan=0.3)

    # airy global wind
    wind = _soft_noise(total, 240, 77) * 0.035
    L += wind
    R += np.roll(wind, int(0.013 * SR)) * 0.9

    # simple wrapped reverb
    for delay, gain in ((0.19, 0.22), (0.37, 0.14), (0.61, 0.09)):
        d = int(delay * SR)
        L += np.roll(L, d) * gain
        R += np.roll(R, d + int(0.007 * SR)) * gain

    stereo = np.stack([L, R], axis=1)
    peak = np.max(np.abs(stereo)) or 1.0
    stereo = stereo / peak * 0.62
    data = np.clip(stereo * 32767.0, -32768, 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.ascontiguousarray(data))


class Audio:
    MUSIC_VOLUME = 0.5
    SFX_VOLUME = 0.55

    def __init__(self, muted: bool = False) -> None:
        self.enabled = False
        self.muted = muted
        self.sfx: dict[str, pygame.mixer.Sound] = {}
        self.music = None
        self.music_channel = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SR, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)
            pygame.mixer.set_reserved(1)
            self.enabled = True
            self._build_all()
            self.music = _build_music()
            self.music_channel = pygame.mixer.Channel(0)
            self.music_channel.set_volume(0.0 if self.muted else self.MUSIC_VOLUME)
            self.music_channel.play(self.music, loops=-1)
        except Exception as exc:  # pragma: no cover - headless/no-audio machines
            self.enabled = False
            print(f"[audio] disabled: {exc}")

    def _build_all(self) -> None:
        builders = {
            "jump": (_sfx_jump, 0.4),
            "land": (_sfx_land, 0.35),
            "coin": (_sfx_coin, 0.5),
            "gem": (_sfx_gem, 0.6),
            "heart": (_sfx_heart, 0.55),
            "chrono": (_sfx_chrono, 0.55),
            "hurt": (_sfx_hurt, 0.55),
            "death": (_sfx_death, 0.6),
            "dash": (_sfx_dash, 0.5),
            "checkpoint": (_sfx_checkpoint, 0.6),
            "select": (_sfx_select, 0.5),
            "loop": (_sfx_loop, 0.6),
            "armor": (_sfx_armor, 0.55),
            "shield": (_sfx_shield, 0.6),
        }
        for name, (fn, vol) in builders.items():
            try:
                snd = _stereo(fn())
                snd.set_volume(vol)
                self.sfx[name] = snd
            except Exception as exc:  # pragma: no cover
                print(f"[audio] could not build {name}: {exc}")

    # ------------------------------------------------------------------
    def play(self, name: str) -> None:
        if not self.enabled or self.muted:
            return
        snd = self.sfx.get(name)
        if snd is not None:
            snd.play()

    def toggle_mute(self) -> bool:
        self.set_muted(not self.muted)
        return self.muted

    def set_muted(self, value: bool) -> None:
        self.muted = bool(value)
        if self.music_channel is not None:
            self.music_channel.set_volume(0.0 if self.muted else self.MUSIC_VOLUME)

    def stop(self) -> None:
        if self.enabled:
            pygame.mixer.stop()
