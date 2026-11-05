"""Audio synthesis and playback.

The game ships without external audio files.  Every sound is generated from
scratch into small 16-bit mono WAV files and cached in assets/audio.
"""

from __future__ import annotations

import math
import random
import time
import wave
from pathlib import Path

import raylib as rl

from .config import AUDIO_DIR, clamp

SAMPLE_RATE = 22050
TAU = math.tau

SfxSpec = tuple[float, float]  # duration seconds, base gain

SOUNDS: dict[str, str] = {
    "pulse": "shoot_pulse.wav",
    "scatter": "shoot_scatter.wav",
    "lance": "shoot_lance.wav",
    "hit": "hit.wav",
    "kill": "enemy_die.wav",
    "hurt": "player_hurt.wav",
    "pickup": "pickup.wav",
    "dash": "dash.wav",
    "shield": "shield.wav",
    "nova": "nova.wav",
    "ui_move": "ui_move.wav",
    "ui_click": "ui_click.wav",
    "portal": "portal.wav",
    "complete": "level_complete.wav",
    "game_over": "game_over.wav",
    "boss": "boss_roar.wav",
    "denied": "denied.wav",
    "enemy_shot": "enemy_shot.wav",
    "boss_shot": "boss_shot.wav",
}

MUSIC_DRIVE = "music_drive.wav"
MUSIC_BOSS = "music_boss.wav"


def _write_wav(path: Path, samples: list[float]) -> None:
    data = bytearray()
    for value in samples:
        value = max(-1.0, min(1.0, value))
        number = int(value * 32767)
        data += number.to_bytes(2, "little", signed=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(bytes(data))


def _sine(freq: float, t: float) -> float:
    return math.sin(TAU * freq * t)


def _saw(freq: float, t: float) -> float:
    phase = (freq * t) % 1.0
    return phase * 2.0 - 1.0


def _square(freq: float, t: float) -> float:
    return 1.0 if (freq * t) % 1.0 < 0.5 else -1.0


def _soft_clip(value: float) -> float:
    return math.tanh(value * 1.35)


def _envelope(t: float, duration: float, attack: float, release: float) -> float:
    if t < attack:
        return t / max(attack, 1e-5)
    if t > duration - release:
        return max(0.0, (duration - t) / max(release, 1e-5))
    return 1.0


def _mix(buffer: list[float], start: int, samples: list[float], gain: float = 1.0) -> None:
    if start < 0:
        start = 0
    needed = start + len(samples)
    if needed > len(buffer):
        buffer.extend([0.0] * (needed - len(buffer)))
    for index in range(start, needed):
        buffer[index] += samples[index - start] * gain


def _noise_burst(duration: float, gain: float, cutoff: float, seed: int) -> list[float]:
    rng = random.Random(seed)
    count = int(duration * SAMPLE_RATE)
    raw: list[float] = []
    previous = 0.0
    for _ in range(count):
        previous = previous * cutoff + rng.uniform(-1.0, 1.0) * (1.0 - cutoff)
        raw.append(previous)
    return [value * gain for value in raw]


def _tone_sweep(
    duration: float,
    start_freq: float,
    end_freq: float,
    gain: float,
    kind: str = "sine",
    attack: float = 0.005,
    release: float = 0.08,
    vibrato: float = 0.0,
) -> list[float]:
    count = int(duration * SAMPLE_RATE)
    out: list[float] = []
    phase = 0.0
    for index in range(count):
        t = index / SAMPLE_RATE
        progress = t / max(duration, 1e-5)
        freq = start_freq + (end_freq - start_freq) * progress
        if vibrato:
            freq += math.sin(TAU * 18.0 * t) * vibrato
        phase += freq / SAMPLE_RATE
        if kind == "sine":
            raw = math.sin(TAU * phase)
        elif kind == "saw":
            raw = (phase % 1.0) * 2.0 - 1.0
        elif kind == "square":
            raw = 1.0 if phase % 1.0 < 0.5 else -1.0
        else:
            raw = math.sin(TAU * phase) * 0.7 + math.sin(TAU * phase * 2.01) * 0.3
        env = _envelope(t, duration, attack, release)
        out.append(raw * env * gain)
    return out


def _build_sfx() -> dict[str, list[float]]:
    sounds: dict[str, list[float]] = {}
    sounds["pulse"] = []
    pulse = _tone_sweep(0.13, 980, 260, 0.52, "square", 0.002, 0.08)
    noise = _noise_burst(0.13, 0.24, 0.55, 11)
    for i, value in enumerate(pulse):
        sounds["pulse"].append(value + noise[i] * 0.5)

    scatter = _tone_sweep(0.32, 240, 55, 0.72, "saw", 0.002, 0.25)
    noise = _noise_burst(0.32, 0.7, 0.72, 22)
    sounds["scatter"] = []
    for i, value in enumerate(scatter):
        sounds["scatter"].append(value + noise[i] * (1.0 - i / len(scatter)) * 0.9)

    charge = _tone_sweep(0.34, 180, 1450, 0.38, "saw", 0.02, 0.02, 12)
    boom = _tone_sweep(0.42, 110, 38, 0.85, "sine", 0.005, 0.30)
    sparkle = _noise_burst(0.42, 0.28, 0.35, 33)
    lance: list[float] = []
    for i in range(int(0.55 * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 5.0)
        left = charge[i] if i < len(charge) else 0.0
        right = boom[i] if i < len(boom) else 0.0
        dust = sparkle[i] if i < len(sparkle) else 0.0
        lance.append((left * 0.7 + right * 0.6 + dust * 0.4) * env)
    sounds["lance"] = lance

    click = _noise_burst(0.055, 0.28, 0.7, 44)
    tick = _tone_sweep(0.055, 2200, 900, 0.22, "sine", 0.001, 0.04)
    sounds["hit"] = [a + b for a, b in zip(click, tick)]

    die = _tone_sweep(0.48, 330, 48, 0.55, "saw", 0.005, 0.35)
    noise = _noise_burst(0.48, 0.55, 0.4, 55)
    sounds["kill"] = [a * (1 - i / len(die)) + b * 0.8 for i, (a, b) in enumerate(zip(die, noise))]

    hurt = _tone_sweep(0.22, 130, 55, 0.85, "sine", 0.002, 0.15)
    grit = _noise_burst(0.22, 0.42, 0.3, 66)
    sounds["hurt"] = [a + b * 0.6 for a, b in zip(hurt, grit)]

    pickup: list[float] = []
    for i, freq in enumerate((660, 880, 1320)):
        note = _tone_sweep(0.18, freq, freq * 1.01, 0.32, "sine", 0.005, 0.12)
        _mix(pickup, int(i * 0.06 * SAMPLE_RATE), note)
    sparkle = _noise_burst(0.32, 0.08, 0.2, 77)
    _mix(pickup, 0, sparkle)
    sounds["pickup"] = pickup

    dash = _noise_burst(0.3, 0.5, 0.62, 88)
    sweep = _tone_sweep(0.3, 420, 90, 0.22, "saw", 0.01, 0.24)
    sounds["dash"] = [a + b for a, b in zip(dash, sweep)]

    sounds["shield"] = []
    hum = _tone_sweep(0.55, 180, 620, 0.33, "sine", 0.06, 0.2, 5)
    shimmer = _noise_burst(0.55, 0.15, 0.12, 99)
    for i, (a, b) in enumerate(zip(hum, shimmer)):
        sounds["shield"].append(a * (0.6 + 0.4 * math.sin(i / SAMPLE_RATE * TAU * 8)) + b)

    nova: list[float] = []
    boom = _tone_sweep(1.1, 90, 30, 0.95, "sine", 0.002, 0.9)
    noise = _noise_burst(1.1, 0.6, 0.77, 111)
    for i, (a, b) in enumerate(zip(boom, noise)):
        t = i / SAMPLE_RATE
        nova.append(a * math.exp(-t * 2.2) + b * math.exp(-t * 4.0) * 0.7)
    sounds["nova"] = nova

    sounds["ui_move"] = _tone_sweep(0.06, 600, 760, 0.28, "sine", 0.002, 0.04)
    sounds["ui_click"] = []
    click_a = _tone_sweep(0.12, 880, 440, 0.36, "square", 0.002, 0.09)
    click_b = _noise_burst(0.12, 0.15, 0.6, 121)
    for a, b in zip(click_a, click_b):
        sounds["ui_click"].append(a + b)

    portal = []
    for i in range(int(0.8 * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        env = min(1.0, t / 0.1) * max(0.0, (0.8 - t) / 0.3)
        portal.append(
            env
            * (
                math.sin(TAU * (140 + t * 240) * t) * 0.28
                + math.sin(TAU * (280 + t * 380) * t) * 0.16
                + math.sin(TAU * 55 * t) * 0.2
            )
        )
    sounds["portal"] = portal

    complete: list[float] = []
    for i, freq in enumerate((523.25, 659.25, 783.99, 1046.5)):
        note = _tone_sweep(0.55, freq, freq, 0.35, "sine", 0.01, 0.3)
        _mix(complete, int(i * 0.11 * SAMPLE_RATE), note)
    pad = _tone_sweep(1.0, 261.63, 261.63, 0.2, "sine", 0.2, 0.4)
    _mix(complete, 0, pad)
    sounds["complete"] = complete

    game_over: list[float] = []
    for i, freq in enumerate((330.0, 277.18, 220.0, 164.81)):
        note = _tone_sweep(0.55, freq, freq * 0.98, 0.4, "saw", 0.01, 0.35)
        _mix(game_over, int(i * 0.22 * SAMPLE_RATE), note)
    sounds["game_over"] = game_over

    roar = _tone_sweep(1.1, 75, 48, 0.8, "saw", 0.03, 0.65, 8)
    noise = _noise_burst(1.1, 0.45, 0.8, 133)
    sounds["boss"] = [a * 1.0 + b * 0.8 for a, b in zip(roar, noise)]

    denied = []
    for i in range(int(0.14 * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        denied.append(math.sin(TAU * 150 * t) * 0.28 * (1 - t / 0.14))
    sounds["denied"] = denied

    enemy_shot = _tone_sweep(0.16, 740, 220, 0.25, "square", 0.002, 0.12, 18)
    fizz = _noise_burst(0.16, 0.12, 0.4, 144)
    sounds["enemy_shot"] = [a + b for a, b in zip(enemy_shot, fizz)]

    boss_shot = _tone_sweep(0.28, 280, 70, 0.42, "saw", 0.004, 0.2, 9)
    fizz = _noise_burst(0.28, 0.25, 0.6, 155)
    sounds["boss_shot"] = [a + b for a, b in zip(boss_shot, fizz)]

    return sounds


# ---------------------------------------------------------------------------
# Music
# ---------------------------------------------------------------------------
NOTE_FREQS = {
    "A1": 55.00,
    "C2": 65.41,
    "D2": 73.42,
    "E2": 82.41,
    "F2": 87.31,
    "G2": 98.00,
    "A2": 110.00,
    "Bb2": 116.54,
    "C3": 130.81,
    "D3": 146.83,
    "E3": 164.81,
    "F3": 174.61,
    "G3": 196.00,
    "A3": 220.00,
    "Bb3": 233.08,
    "B3": 246.94,
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "Bb4": 466.16,
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
    "F5": 698.46,
    "G5": 783.99,
    "A5": 880.0,
}


def _note(name: str) -> float:
    return NOTE_FREQS[name]


def _pad_note(freq: float, duration: float, gain: float, detune: float = 0.0) -> list[float]:
    count = int(duration * SAMPLE_RATE)
    out: list[float] = []
    for index in range(count):
        t = index / SAMPLE_RATE
        attack = min(1.0, t / 0.22)
        release = min(1.0, max(0.0, (duration - t) / 0.35))
        env = attack * release
        raw = (
            math.sin(TAU * (freq + detune) * t) * 0.55
            + math.sin(TAU * (freq * 2.0 + detune) * t) * 0.2
            + math.sin(TAU * (freq * 0.5) * t) * 0.25
            + math.sin(TAU * (freq * 1.003) * t) * 0.3
        )
        out.append(raw * env * gain)
    return out


def _bass_note(freq: float, duration: float, gain: float) -> list[float]:
    count = int(duration * SAMPLE_RATE)
    out: list[float] = []
    for index in range(count):
        t = index / SAMPLE_RATE
        env = min(1.0, t / 0.012) * math.exp(-t * 2.6)
        raw = math.sin(TAU * freq * t) * 0.7 + math.sin(TAU * freq * 2.0 * t) * 0.2 + _saw(freq, t) * 0.12
        out.append(raw * env * gain)
    return out


def _pluck(freq: float, duration: float, gain: float) -> list[float]:
    count = int(duration * SAMPLE_RATE)
    out: list[float] = []
    for index in range(count):
        t = index / SAMPLE_RATE
        env = math.exp(-t * 8.0)
        raw = math.sin(TAU * freq * t) + math.sin(TAU * freq * 2.0 * t) * 0.4 + math.sin(TAU * freq * 3.01 * t) * 0.16
        out.append(raw * env * gain)
    return out


def _kick(gain: float = 0.9) -> list[float]:
    duration = 0.34
    count = int(duration * SAMPLE_RATE)
    out = []
    phase = 0.0
    for index in range(count):
        t = index / SAMPLE_RATE
        freq = 135 * math.exp(-t * 22) + 42
        phase += freq / SAMPLE_RATE
        env = math.exp(-t * 8.0)
        out.append(math.sin(TAU * phase) * env * gain)
    return out


def _snare(gain: float = 0.7, seed: int = 0) -> list[float]:
    duration = 0.26
    count = int(duration * SAMPLE_RATE)
    rng = random.Random(seed)
    out = []
    previous = 0.0
    for index in range(count):
        t = index / SAMPLE_RATE
        env = math.exp(-t * 14.0)
        previous = previous * 0.2 + rng.uniform(-1, 1) * 0.8
        tone = math.sin(TAU * 180 * t) * 0.35
        out.append((previous + tone) * env * gain)
    return out


def _hat(gain: float = 0.25, seed: int = 0) -> list[float]:
    duration = 0.07
    count = int(duration * SAMPLE_RATE)
    rng = random.Random(seed)
    out = []
    previous = 0.0
    for index in range(count):
        t = index / SAMPLE_RATE
        env = math.exp(-t * 48.0)
        current = rng.uniform(-1, 1)
        high = current - previous
        previous = current
        out.append(high * env * gain)
    return out


def _reverb_tail(buffer: list[float], delay: float = 0.19, gain: float = 0.19) -> None:
    offset = int(delay * SAMPLE_RATE)
    for index in range(offset, len(buffer)):
        buffer[index] += buffer[index - offset] * gain


def _music_drive() -> list[float]:
    bpm = 104.0
    beat = 60.0 / bpm
    bar = beat * 4
    bars = 8
    duration = bar * bars
    total = int(duration * SAMPLE_RATE) + 1
    buffer = [0.0] * total
    chords = [
        ("A2", ["A3", "C4", "E4"]),
        ("F2", ["F3", "A3", "C4"]),
        ("C3", ["C4", "E4", "G4"]),
        ("G2", ["G3", "B3", "D4"]),
    ]
    for bar_index in range(bars):
        root, triad = chords[(bar_index // 2) % len(chords)]
        start = bar_index * bar
        _mix(buffer, int(start * SAMPLE_RATE), _pad_note(_note(triad[0]), bar * 2.0, 0.14, -0.8))
        _mix(buffer, int(start * SAMPLE_RATE), _pad_note(_note(triad[1]), bar * 2.0, 0.10, 0.7))
        _mix(buffer, int(start * SAMPLE_RATE), _pad_note(_note(triad[2]), bar * 2.0, 0.09, 1.2))
        # octave shimmer
        _mix(buffer, int((start + bar) * SAMPLE_RATE), _pad_note(_note(triad[0]) * 2, bar, 0.05, 0.4))

        for eighth in range(8):
            note_name = root if eighth % 4 != 3 else triad[1]
            freq = _note(note_name) * (2.0 if eighth % 4 == 2 else 1.0)
            _mix(buffer, int((start + eighth * beat * 0.5) * SAMPLE_RATE), _bass_note(freq, beat * 0.46, 0.38))

        arp_notes = [triad[0], triad[1], triad[2], triad[0], triad[2], triad[1], triad[0], triad[2]]
        for sixteenth in range(16):
            note_name = arp_notes[sixteenth % len(arp_notes)]
            freq = _note(note_name) * (2.0 if sixteenth % 8 >= 4 else 1.0)
            _mix(
                buffer,
                int((start + sixteenth * beat * 0.25) * SAMPLE_RATE),
                _pluck(freq, beat * 0.7, 0.085 if sixteenth % 4 else 0.12),
            )

        for beat_index in range(4):
            if beat_index in (0, 2):
                _mix(buffer, int((start + beat_index * beat) * SAMPLE_RATE), _kick(0.85))
            else:
                _mix(buffer, int((start + beat_index * beat) * SAMPLE_RATE), _snare(0.52, bar_index * 4 + beat_index))
            _mix(buffer, int((start + beat_index * beat + beat * 0.5) * SAMPLE_RATE), _hat(0.18, bar_index * 8 + beat_index))
            for sub in range(2):
                _mix(
                    buffer,
                    int((start + beat_index * beat + sub * beat * 0.25) * SAMPLE_RATE),
                    _hat(0.07, bar_index * 19 + beat_index * 3 + sub),
                )
    _reverb_tail(buffer, 0.235, 0.18)
    return [math.tanh(value * 0.9) for value in buffer]


def _music_boss() -> list[float]:
    bpm = 126.0
    beat = 60.0 / bpm
    bar = beat * 4
    bars = 8
    duration = bar * bars
    total = int(duration * SAMPLE_RATE) + 1
    buffer = [0.0] * total
    chords = [
        ("D2", ["D3", "F3", "A3"]),
        ("Bb2", ["Bb3", "D4", "F4"]),
        ("F2", ["F3", "A3", "C4"]),
        ("A2", ["A3", "C4", "E4"]),
    ]
    rng = random.Random(404)
    for bar_index in range(bars):
        root, triad = chords[(bar_index // 2) % len(chords)]
        start = bar_index * bar
        _mix(buffer, int(start * SAMPLE_RATE), _pad_note(_note(triad[0]) / 2, bar * 2, 0.18, -1.2))
        _mix(buffer, int(start * SAMPLE_RATE), _pad_note(_note(triad[1]), bar * 2, 0.09, 1.0))
        _mix(buffer, int(start * SAMPLE_RATE), _pad_note(_note(triad[2]), bar * 2, 0.08, -0.6))
        for eighth in range(8):
            freq = _note(root) * (2.0 if eighth % 4 == 2 else 1.0)
            _mix(buffer, int((start + eighth * beat * 0.5) * SAMPLE_RATE), _bass_note(freq, beat * 0.42, 0.5))
        for sixteenth in range(16):
            if sixteenth % 4 == 0 or (sixteenth + bar_index) % 3 == 0:
                note_name = triad[(sixteenth // 2) % len(triad)]
                freq = _note(note_name) * (2.0 if (sixteenth // 8) % 2 else 1.0)
                _mix(buffer, int((start + sixteenth * beat * 0.25) * SAMPLE_RATE), _pluck(freq, beat * 0.55, 0.075))
        for beat_index in range(4):
            if beat_index in (0, 2):
                _mix(buffer, int((start + beat_index * beat) * SAMPLE_RATE), _kick(1.0))
            else:
                _mix(buffer, int((start + beat_index * beat) * SAMPLE_RATE), _snare(0.7, bar_index * 11 + beat_index))
            for sub in range(4):
                _mix(
                    buffer,
                    int((start + beat_index * beat + sub * beat * 0.25) * SAMPLE_RATE),
                    _hat(0.11 if sub % 2 else 0.17, bar_index * 31 + beat_index * 7 + sub),
                )
        # Industrial metallic hit every other bar.
        if bar_index % 2 == 0:
            metal = _tone_sweep(0.6, 290, 170, 0.22, "saw", 0.005, 0.5, 25)
            _mix(buffer, int(start * SAMPLE_RATE), metal)
    _reverb_tail(buffer, 0.18, 0.12)
    return [math.tanh(value * 1.15) for value in buffer]


def _build_music() -> dict[str, list[float]]:
    return {MUSIC_DRIVE: _music_drive(), MUSIC_BOSS: _music_boss()}


def ensure_audio_assets(verbose: bool = False) -> None:
    """Generate any missing WAV assets.  Safe to call every launch."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    def needs(name: str) -> bool:
        path = AUDIO_DIR / name
        return (not path.exists()) or path.stat().st_size <= 44

    wanted = set(SOUNDS.values()) | {MUSIC_DRIVE, MUSIC_BOSS}
    if not any(needs(name) for name in wanted):
        return
    start = time.perf_counter()
    if verbose:
        print("Generating procedural audio...")
    if any(needs(name) for name in SOUNDS.values()):
        for name, samples in _build_sfx().items():
            _write_wav(AUDIO_DIR / SOUNDS[name], samples)
    if needs(MUSIC_DRIVE) or needs(MUSIC_BOSS):
        for name, samples in _build_music().items():
            _write_wav(AUDIO_DIR / name, samples)
    if verbose:
        print(f"Audio generated in {time.perf_counter() - start:.1f}s")


# ---------------------------------------------------------------------------
# Runtime playback
# ---------------------------------------------------------------------------
class AudioManager:
    def __init__(self) -> None:
        self.ready = False
        self.sounds: dict[str, object] = {}
        self.music: dict[str, object] = {}
        self.current_music_key: str | None = None
        self.current_music = None
        self.muted = False
        self.master_volume = 0.78
        self.music_volume = 0.33
        self.sfx_volume = 0.82
        self.music_pitch = 1.0

    def init(self) -> None:
        ensure_audio_assets()
        try:
            rl.InitAudioDevice()
            self.ready = bool(rl.IsAudioDeviceReady())
        except Exception:
            self.ready = False
        if not self.ready:
            return
        rl.SetMasterVolume(self.master_volume)
        try:
            for key, filename in SOUNDS.items():
                path = AUDIO_DIR / filename
                if path.exists():
                    sound = rl.LoadSound(str(path).encode("utf-8"))
                    self.sounds[key] = sound
            for key in (MUSIC_DRIVE, MUSIC_BOSS):
                path = AUDIO_DIR / key
                if path.exists():
                    self.music[key] = rl.LoadMusicStream(str(path).encode("utf-8"))
            for sound in self.sounds.values():
                try:
                    rl.SetSoundVolume(sound, self.sfx_volume)
                except Exception:
                    pass
        except Exception:
            self.ready = False

    def play(self, key: str, volume: float = 1.0) -> None:
        if not self.ready or self.muted:
            return
        sound = self.sounds.get(key)
        if sound is not None:
            try:
                rl.SetSoundVolume(sound, self.sfx_volume * clamp(volume, 0, 2.0))
                rl.PlaySound(sound)
            except Exception:
                pass

    def start_music(self, boss: bool = False) -> None:
        if not self.ready:
            return
        key = MUSIC_BOSS if boss else MUSIC_DRIVE
        if self.current_music_key == key and self.current_music:
            return
        if self.current_music:
            try:
                rl.StopMusicStream(self.current_music)
            except Exception:
                pass
        self.current_music_key = key
        self.current_music = self.music.get(key)
        if self.current_music:
            try:
                rl.SetMusicVolume(self.current_music, self.music_volume)
                rl.SetMusicPitch(self.current_music, self.music_pitch)
                if self.muted:
                    rl.PauseMusicStream(self.current_music)
                else:
                    rl.PlayMusicStream(self.current_music)
            except Exception:
                self.current_music = None

    def set_music_pitch(self, pitch: float) -> None:
        self.music_pitch = clamp(pitch, 0.5, 1.5)
        if self.ready and self.current_music:
            try:
                rl.SetMusicPitch(self.current_music, self.music_pitch)
            except Exception:
                pass

    def update(self) -> None:
        if not self.ready or not self.current_music or self.muted:
            return
        try:
            rl.UpdateMusicStream(self.current_music)
            if not rl.IsMusicStreamPlaying(self.current_music):
                rl.PlayMusicStream(self.current_music)
        except Exception:
            pass

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        if not self.ready:
            return self.muted
        try:
            if self.muted:
                rl.SetMasterVolume(0.0)
                if self.current_music:
                    rl.PauseMusicStream(self.current_music)
            else:
                rl.SetMasterVolume(self.master_volume)
                if self.current_music:
                    rl.ResumeMusicStream(self.current_music)
        except Exception:
            pass
        return self.muted

    def stop_music(self) -> None:
        if self.current_music:
            try:
                rl.StopMusicStream(self.current_music)
            except Exception:
                pass
        self.current_music = None
        self.current_music_key = None

    def shutdown(self) -> None:
        if not self.ready:
            return
        try:
            self.stop_music()
            for sound in self.sounds.values():
                rl.UnloadSound(sound)
            for music in self.music.values():
                rl.UnloadMusicStream(music)
        finally:
            self.sounds.clear()
            self.music.clear()
            try:
                rl.CloseAudioDevice()
            except Exception:
                pass
            self.ready = False
