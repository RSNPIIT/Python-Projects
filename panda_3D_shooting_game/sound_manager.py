"""
sound_manager.py - Native audio playback system.
Bypasses buggy OpenAL Soft on macOS to eliminate segmentation faults,
providing low-latency, crash-proof audio playback via macOS native afplay
and Linux/Windows fallbacks.
"""

import os
import sys
import subprocess
import shutil

class SoundEffect:
    def __init__(self, filepath):
        self.filepath = os.path.abspath(filepath)
        self.volume = 0.8
        self.procs = []

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))

    def play(self):
        if not os.path.exists(self.filepath):
            return
            
        # Clean finished processes
        self.procs = [p for p in self.procs if p.poll() is None]
        
        # Prune oldest if too many concurrent instances
        if len(self.procs) >= 4:
            old = self.procs.pop(0)
            try:
                old.terminate()
            except Exception:
                pass
                
        try:
            if sys.platform == 'darwin' and os.path.exists('/usr/bin/afplay'):
                p = subprocess.Popen(
                    ['/usr/bin/afplay', '-v', str(self.volume), self.filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.procs.append(p)
            elif shutil.which('paplay'):
                p = subprocess.Popen(
                    ['paplay', self.filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.procs.append(p)
            elif shutil.which('aplay'):
                p = subprocess.Popen(
                    ['aplay', '-q', self.filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.procs.append(p)
        except Exception:
            pass

    def stop(self):
        for p in self.procs:
            if p.poll() is None:
                try:
                    p.terminate()
                except Exception:
                    pass
        self.procs.clear()

def load_sound_catalog(sound_dir):
    """Loads all game sound effects using native SoundEffect instances."""
    sound_files = {
        'pistol': 'pistol.wav',
        'ar': 'ar.wav',
        'shotgun': 'shotgun.wav',
        'sniper': 'sniper.wav',
        'reload': 'reload.wav',
        'inspect': 'inspect.wav',
        'hitmarker': 'hitmarker.wav',
        'explosion': 'explosion.wav',
        'footstep': 'footstep.wav',
        'pickup': 'pickup.wav',
        'voice_kill': 'voice_kill.wav',
        'voice_wave': 'voice_wave.wav',
        'voice_reload': 'voice_reload.wav',
        'enemy_death': 'enemy_death.wav',
        'ui_click': 'ui_click.wav',
        'ui_hover': 'ui_hover.wav'
    }
    sounds = {}
    for key, fname in sound_files.items():
        fpath = os.path.join(sound_dir, fname)
        if os.path.exists(fpath):
            snd = SoundEffect(fpath)
            snd.set_volume(0.85)
            sounds[key] = snd
    return sounds
