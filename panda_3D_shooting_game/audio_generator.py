"""
audio_generator.py - Procedural audio generation for Panda3D Modern Shooter Game.
Uses standard Python library (wave, math, struct, random) to synthesize high-quality
gunshots, bullet impacts, mechanical gun clicks, reloads, inspect movements,
explosions, footsteps, and tactical radio/voice beeps and callouts.
"""

import os
import wave
import struct
import math
import random

SAMPLE_RATE = 44100

def ensure_sound_dir(target_dir):
    os.makedirs(target_dir, exist_ok=True)

def write_wav(filepath, samples, sample_rate=SAMPLE_RATE):
    """Write float samples (-1.0 to 1.0) to 16-bit PCM WAV."""
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        packed_data = bytearray()
        for s in samples:
            # Clamp between -1.0 and 1.0
            clamped = max(-1.0, min(1.0, s))
            int_val = int(clamped * 32767.0)
            packed_data.extend(struct.pack('<h', int_val))
        wav_file.writeframes(packed_data)

def gen_pistol_shot():
    duration = 0.35
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Fast exponential decay
        env = math.exp(-18.0 * t)
        # Low punch + crack
        freq = 150.0 * math.exp(-30.0 * t) + 40.0
        punch = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2.0 - 1.0) * math.exp(-25.0 * t)
        # High transient crack
        crack = math.sin(2 * math.pi * 1200.0 * t) * math.exp(-60.0 * t)
        sample = (0.5 * punch + 0.35 * noise + 0.3 * crack) * env
        samples.append(sample)
    return samples

def gen_ar_shot():
    duration = 0.45
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-12.0 * t)
        freq = 220.0 * math.exp(-22.0 * t) + 55.0
        punch = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2.0 - 1.0) * math.exp(-18.0 * t)
        # Gun metallic echo
        echo = 0.2 * math.sin(2 * math.pi * 650.0 * t) * math.exp(-15.0 * t)
        sample = (0.6 * punch + 0.45 * noise + echo) * env * 1.1
        samples.append(sample)
    return samples

def gen_shotgun_shot():
    duration = 0.65
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-9.0 * t)
        freq = 90.0 * math.exp(-15.0 * t) + 35.0
        sub_bass = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2.0 - 1.0) * math.exp(-11.0 * t)
        grit = math.sin(2 * math.pi * 320.0 * t) * math.exp(-20.0 * t)
        sample = (0.75 * sub_bass + 0.6 * noise + 0.35 * grit) * env
        samples.append(sample)
    return samples

def gen_sniper_shot():
    duration = 0.95
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-5.5 * t)
        freq = 180.0 * math.exp(-12.0 * t) + 40.0
        crack = math.sin(2 * math.pi * 2400.0 * t) * math.exp(-70.0 * t)
        boom = math.sin(2 * math.pi * freq * t) * math.exp(-7.0 * t)
        rumble = (random.random() * 2.0 - 1.0) * math.exp(-6.0 * t)
        sample = (0.45 * crack + 0.8 * boom + 0.45 * rumble) * env
        samples.append(sample)
    return samples

def gen_reload_sound():
    duration = 0.8
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Mag eject at 0.15s, mag insert at 0.55s
        click1 = 0.0
        click2 = 0.0
        if 0.12 < t < 0.22:
            dt = t - 0.12
            click1 = math.sin(2 * math.pi * 900.0 * dt) * math.exp(-40.0 * dt) + (random.random() - 0.5) * 0.3
        if 0.50 < t < 0.65:
            dt = t - 0.50
            click2 = math.sin(2 * math.pi * 1400.0 * dt) * math.exp(-45.0 * dt) + (random.random() - 0.5) * 0.4
        foley = (random.random() - 0.5) * 0.05 * math.exp(-3.0 * t)
        samples.append(click1 * 0.7 + click2 * 0.8 + foley)
    return samples

def gen_inspect_sound():
    duration = 1.1
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Cloth rustle + delicate metallic clicks as weapon tilts and examines
        rustle = (random.random() - 0.5) * 0.08 * math.sin(math.pi * t / duration)
        click = 0.0
        # subtle chamber check click at t=0.35 and return click at t=0.75
        if 0.32 < t < 0.42:
            dt = t - 0.32
            click = 0.35 * math.sin(2 * math.pi * 1100.0 * dt) * math.exp(-50.0 * dt)
        elif 0.72 < t < 0.82:
            dt = t - 0.72
            click = 0.3 * math.sin(2 * math.pi * 850.0 * dt) * math.exp(-40.0 * dt)
        samples.append(rustle + click)
    return samples

def gen_hitmarker():
    duration = 0.08
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Crisp high pitch click
        env = math.exp(-60.0 * t)
        sample = (math.sin(2 * math.pi * 2100.0 * t) * 0.7 + math.sin(2 * math.pi * 4200.0 * t) * 0.3) * env
        samples.append(sample * 0.6)
    return samples

def gen_explosion():
    duration = 1.4
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-3.2 * t)
        # Deep subwoofer blast
        sub = math.sin(2 * math.pi * 45.0 * t) * math.exp(-2.5 * t)
        # Noise blast
        noise = (random.random() * 2.0 - 1.0) * math.exp(-4.5 * t)
        # Resonant debris
        res = math.sin(2 * math.pi * 110.0 * (1.0 + t)) * math.exp(-4.0 * t) * 0.4
        sample = (0.7 * sub + 0.6 * noise + res) * env
        samples.append(sample)
    return samples

def gen_footstep():
    duration = 0.18
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-28.0 * t)
        thud = math.sin(2 * math.pi * 80.0 * t) * 0.6
        crunch = (random.random() - 0.5) * 0.35
        samples.append((thud + crunch) * env * 0.45)
    return samples

def gen_pickup():
    duration = 0.25
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Two rising cheerful chimes
        freq = 523.25 if t < 0.12 else 783.99 # C5 to G5
        env = math.exp(-15.0 * (t % 0.12))
        tone = math.sin(2 * math.pi * freq * t) * 0.5
        harmonic = math.sin(2 * math.pi * (freq * 2) * t) * 0.2
        samples.append((tone + harmonic) * env * 0.7)
    return samples

def gen_voice_callout(phrase="kill"):
    """
    Tactical radio chirps / robotic vocal tones representing tactical chatter.
    'kill' -> double confirmation beep
    'wave' -> alarm siren pulses
    'reload' -> radio static burst + low dual beep
    'hit' -> robot hurt grunt
    """
    duration = 0.5 if phrase != "wave" else 0.8
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    
    if phrase == "kill":
        # Positive tactical ping-ping
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            p = 0.0
            if t < 0.15:
                p = math.sin(2 * math.pi * 880.0 * t) * math.exp(-20.0 * t)
            elif 0.18 < t < 0.35:
                dt = t - 0.18
                p = math.sin(2 * math.pi * 1174.66 * dt) * math.exp(-20.0 * dt)
            static = (random.random() - 0.5) * 0.04 * math.exp(-4.0 * t)
            samples.append((p * 0.6 + static))
    elif phrase == "wave":
        # Wave incoming alert siren
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 400.0 + 350.0 * math.sin(2 * math.pi * 5.0 * t)
            tone = math.sin(2 * math.pi * freq * t) * 0.45
            chirp = (random.random() - 0.5) * 0.08
            samples.append((tone + chirp) * (1.0 - t / duration))
    elif phrase == "reload":
        # Radio burst
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            noise = (random.random() - 0.5) * 0.3 * math.exp(-10.0 * t)
            tone = math.sin(2 * math.pi * 440.0 * t) * 0.3 * math.exp(-8.0 * t)
            samples.append(noise + tone)
    else:
        # Enemy grunt / death
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = math.exp(-6.0 * t)
            freq = 160.0 * math.exp(-8.0 * t) + 60.0
            grunt = math.sin(2 * math.pi * freq * t) * 0.7
            noise = (random.random() - 0.5) * 0.3
            samples.append((grunt + noise) * env * 0.5)
            
    return samples

def gen_ui_click():
    duration = 0.05
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-80.0 * t)
        sample = math.sin(2 * math.pi * 1800.0 * t) * env * 0.4
        samples.append(sample)
    return samples

def gen_ui_hover():
    duration = 0.03
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-100.0 * t)
        sample = math.sin(2 * math.pi * 1200.0 * t) * env * 0.25
        samples.append(sample)
    return samples

def generate_all_sounds(target_dir):
    """Generates all game sounds into target_dir."""
    ensure_sound_dir(target_dir)
    sounds = {
        "pistol.wav": gen_pistol_shot(),
        "ar.wav": gen_ar_shot(),
        "shotgun.wav": gen_shotgun_shot(),
        "sniper.wav": gen_sniper_shot(),
        "reload.wav": gen_reload_sound(),
        "inspect.wav": gen_inspect_sound(),
        "hitmarker.wav": gen_hitmarker(),
        "explosion.wav": gen_explosion(),
        "footstep.wav": gen_footstep(),
        "pickup.wav": gen_pickup(),
        "voice_kill.wav": gen_voice_callout("kill"),
        "voice_wave.wav": gen_voice_callout("wave"),
        "voice_reload.wav": gen_voice_callout("reload"),
        "enemy_death.wav": gen_voice_callout("death"),
        "ui_click.wav": gen_ui_click(),
        "ui_hover.wav": gen_ui_hover(),
    }
    
    for filename, data in sounds.items():
        path = os.path.join(target_dir, filename)
        write_wav(path, data)
    print(f"Generated {len(sounds)} audio assets in {target_dir}")

if __name__ == "__main__":
    generate_all_sounds("sounds")
