"""
sound_manager.py - Pygame Mixer Audio Manager for Reimagined Tetris.
Caches synthesized sound effects and handles volume mixing.
"""

import pygame
from src.audio.synth import SoundSynthesizer


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.master_volume = 0.8
        self.sfx_volume = 0.8
        self.sounds = {}
        self.combo_cache = {}

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[SoundManager] Mixer initialization warning: {e}")
                self.enabled = False
                return

        self._init_sounds()

    def _init_sounds(self):
        try:
            self.sounds['move'] = SoundSynthesizer.gen_move()
            self.sounds['rotate'] = SoundSynthesizer.gen_rotate()
            self.sounds['soft_drop'] = SoundSynthesizer.gen_soft_drop()
            self.sounds['hard_drop'] = SoundSynthesizer.gen_hard_drop()
            self.sounds['lock'] = SoundSynthesizer.gen_lock()
            self.sounds['hold'] = SoundSynthesizer.gen_hold()
            self.sounds['line_clear_1'] = SoundSynthesizer.gen_line_clear(1)
            self.sounds['line_clear_2'] = SoundSynthesizer.gen_line_clear(2)
            self.sounds['line_clear_3'] = SoundSynthesizer.gen_line_clear(3)
            self.sounds['tetris'] = SoundSynthesizer.gen_tetris()
            self.sounds['tspin'] = SoundSynthesizer.gen_tspin()
            self.sounds['levelup'] = SoundSynthesizer.gen_levelup()
            self.sounds['gameover'] = SoundSynthesizer.gen_gameover()
            self.sounds['ui_click'] = SoundSynthesizer.gen_ui_click()
            self.sounds['ui_hover'] = SoundSynthesizer.gen_ui_hover()

            for i in range(1, 15):
                self.combo_cache[i] = SoundSynthesizer.gen_combo(i)

            self.apply_volume()
        except Exception as e:
            print(f"[SoundManager] Sound generation warning: {e}")
            self.enabled = False

    def set_volume(self, master=None, sfx=None):
        if master is not None:
            self.master_volume = max(0.0, min(1.0, master))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, sfx))
        self.apply_volume()

    def apply_volume(self):
        vol = self.master_volume * self.sfx_volume if self.enabled else 0.0
        for snd in self.sounds.values():
            if snd:
                snd.set_volume(vol)
        for snd in self.combo_cache.values():
            if snd:
                snd.set_volume(vol)

    def play(self, name, combo_count=None):
        if not self.enabled or self.master_volume <= 0.0 or self.sfx_volume <= 0.0:
            return

        if combo_count is not None and combo_count > 0:
            idx = min(combo_count, 14)
            snd = self.combo_cache.get(idx)
            if snd:
                snd.play()
            return

        snd = self.sounds.get(name)
        if snd:
            snd.play()

    def play_line_clear(self, count):
        if count >= 4:
            self.play('tetris')
        elif count in (1, 2, 3):
            self.play(f'line_clear_{count}')
        else:
            self.play('line_clear_1')
