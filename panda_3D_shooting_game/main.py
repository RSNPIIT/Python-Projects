"""
main.py - Main entry point for Modern Shooter Game in Panda3D.
Initializes ShowBase, manages game states (Menu, Playing, Paused, Game Over),
audio, wave progression, and map selection.
"""

import sys
import os
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Vec3, Vec4, TextNode, CardMaker,
    loadPrcFileData, ClockObject
)

# Set Panda3D configuration before ShowBase
loadPrcFileData("", "window-title CYBER OPS: Modern Panda3D FPS")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video true")
loadPrcFileData("", "show-frame-rate-meter true")
# Bypass buggy OpenAL Soft on macOS to prevent AudioOutputUnitStart segmentation fault
loadPrcFileData("", "audio-library-name null")

from audio_generator import generate_all_sounds
from texture_generator import generate_textures
from sound_manager import load_sound_catalog
from particles import ParticleManager
from map_manager import MapManager
from enemy import EnemyManager
from player import Player
from hud import HUD
from minimap import Minimap

class CyberOpsGame(ShowBase):
    def __init__(self):
        super().__init__()
        
        # Textures check
        tex_dir = os.path.join(os.path.dirname(__file__), "textures")
        if not os.path.exists(tex_dir) or len(os.listdir(tex_dir)) < 5:
            generate_textures(tex_dir)
            
        # Audio directory check
        sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
        if not os.path.exists(sound_dir) or len(os.listdir(sound_dir)) < 5:
            print("Generating game audio assets...")
            generate_all_sounds(sound_dir)
            
        self.sound_mgr = load_sound_catalog(sound_dir)
        
        # Game State: 'MENU', 'PLAYING', 'PAUSED', 'GAME_OVER'
        self.game_state = 'MENU'
        self.selected_map_id = 1
        self.mouse_locked = False
        
        # Managers
        self.particle_mgr = ParticleManager(self.render)
        self.map_manager = MapManager(self.render, self.particle_mgr, self.sound_mgr)
        self.enemy_manager = EnemyManager(self.render, self.particle_mgr, self.sound_mgr)
        self.player = None
        self.hud = None
        self.minimap = None
        
        # Menus root in aspect2d
        self.menu_root = self.aspect2d.attach_new_node("menu_root")
        self.pause_root = self.aspect2d.attach_new_node("pause_root")
        self.game_over_root = self.aspect2d.attach_new_node("game_over_root")
        
        self.pause_root.hide()
        self.game_over_root.hide()
        
        self.build_main_menu()
        self.build_pause_menu()
        self.build_game_over_menu()
        
        # Global hotkeys
        self.accept('escape', self.handle_escape)
        self.accept('p', self.handle_escape)
        self.accept('1', self.handle_menu_key, [1])
        self.accept('2', self.handle_menu_key, [2])
        self.accept('enter', self.handle_enter)
        self.accept('q', self.handle_q_key)
        
        # Start game update loop
        self.taskMgr.add(self.game_loop, "game_loop")

    def handle_q_key(self):
        if self.game_state in ('MENU', 'PAUSED', 'GAME_OVER'):
            self.quit_game()

    def lock_mouse(self):
        if self.win is None:
            self.mouse_locked = True
            return
        props = WindowProperties()
        props.set_cursor_hidden(True)
        props.set_mouse_mode(WindowProperties.M_relative)
        props.set_foreground(True)
        self.win.request_properties(props)
        self.mouse_locked = True
        
        cx = self.win.get_x_size() // 2
        cy = self.win.get_y_size() // 2
        self.win.move_pointer(0, cx, cy)

    def unlock_mouse(self):
        if self.win is None:
            self.mouse_locked = False
            return
        props = WindowProperties()
        props.set_cursor_hidden(False)
        props.set_mouse_mode(WindowProperties.M_absolute)
        self.win.request_properties(props)
        self.mouse_locked = False

    def build_main_menu(self):
        # Dark sleek tactical background
        cm = CardMaker("menu_bg")
        cm.set_frame(-2.0, 2.0, -2.0, 2.0)
        bg = self.menu_root.attach_new_node(cm.generate())
        bg.set_color(Vec4(0.04, 0.06, 0.09, 0.95))
        bg.set_transparency(True)
        
        # Title
        t = TextNode("title")
        t.set_text("CYBER OPS: VANGUARD")
        t.set_align(TextNode.A_center)
        t.set_text_color(0.1, 0.85, 1.0, 1.0)
        np_t = self.menu_root.attach_new_node(t)
        np_t.set_pos(0, 0, 0.55)
        np_t.set_scale(0.11)
        
        # Subtitle
        st = TextNode("subtitle")
        st.set_text("MODERN 3D TACTICAL FPS")
        st.set_align(TextNode.A_center)
        st.set_text_color(0.8, 0.85, 0.9, 0.85)
        np_st = self.menu_root.attach_new_node(st)
        np_st.set_pos(0, 0, 0.42)
        np_st.set_scale(0.048)
        
        # Map options
        maps_text = TextNode("maps_text")
        maps_text.set_align(TextNode.A_center)
        maps_text.set_text(
            "SELECT DEPLOYMENT ZONE:\n\n"
            "[ 1 ] Sector 7 - Cyber Facility\n"
            "(Elevators, High Catwalks, Night Security Searchlight)\n\n"
            "[ 2 ] Ruins of Oasis - Desert Outpost\n"
            "(Sandstone Fort, Moving Hover Platform, Courtyard)\n\n"
            "--------------------------------------------------\n"
            "Press [ENTER] to Deploy Operator\n"
            "Press [Q] to Exit Game"
        )
        maps_text.set_text_color(0.9, 0.95, 1.0, 0.95)
        np_m = self.menu_root.attach_new_node(maps_text)
        np_m.set_pos(0, 0, 0.15)
        np_m.set_scale(0.042)
        
        # Controls reminder box
        ctrl_text = TextNode("ctrl_text")
        ctrl_text.set_align(TextNode.A_center)
        ctrl_text.set_text(
            "CONTROLS:\n"
            "WASD: Movement  |  Shift: Sprint  |  C / Ctrl: Crouch  |  Space: Jump\n"
            "Left Click: Fire  |  Right Click: Aim Down Sights (Sniper Scope)\n"
            "1-4 / Scroll: Switch Guns  |  F: Gun Inspect Animation  |  R: Reload  |  M: Tactical Radar"
        )
        ctrl_text.set_text_color(0.3, 0.9, 0.6, 0.85)
        np_c = self.menu_root.attach_new_node(ctrl_text)
        np_c.set_pos(0, 0, -0.62)
        np_c.set_scale(0.034)

    def build_pause_menu(self):
        cm = CardMaker("pause_bg")
        cm.set_frame(-2.0, 2.0, -2.0, 2.0)
        bg = self.pause_root.attach_new_node(cm.generate())
        bg.set_color(Vec4(0.03, 0.05, 0.08, 0.88))
        bg.set_transparency(True)
        
        t = TextNode("pause_title")
        t.set_text("MISSION PAUSED")
        t.set_align(TextNode.A_center)
        t.set_text_color(1.0, 0.8, 0.1, 1.0)
        np_t = self.pause_root.attach_new_node(t)
        np_t.set_pos(0, 0, 0.35)
        np_t.set_scale(0.09)
        
        opts = TextNode("pause_opts")
        opts.set_align(TextNode.A_center)
        opts.set_text(
            "Press [ESC] / [P] to Resume\n\n"
            "Press [R] to Restart Mission\n\n"
            "Press [M] to Return to Map Selection\n\n"
            "Press [Q] to Quit Game"
        )
        opts.set_text_color(1, 1, 1, 0.9)
        np_o = self.pause_root.attach_new_node(opts)
        np_o.set_pos(0, 0, -0.05)
        np_o.set_scale(0.045)

    def build_game_over_menu(self):
        cm = CardMaker("over_bg")
        cm.set_frame(-2.0, 2.0, -2.0, 2.0)
        bg = self.game_over_root.attach_new_node(cm.generate())
        bg.set_color(Vec4(0.18, 0.02, 0.02, 0.92))
        bg.set_transparency(True)
        
        t = TextNode("over_title")
        t.set_text("OPERATOR DOWN - MISSION FAILED")
        t.set_align(TextNode.A_center)
        t.set_text_color(1.0, 0.15, 0.15, 1.0)
        np_t = self.game_over_root.attach_new_node(t)
        np_t.set_pos(0, 0, 0.35)
        np_t.set_scale(0.08)
        
        self.over_stats_text = TextNode("over_stats")
        self.over_stats_text.set_align(TextNode.A_center)
        self.over_stats_text.set_text(
            "WAVES SURVIVED: 0\n"
            "HOSTILES ELIMINATED: 0\n"
            "TOTAL COMBAT SCORE: 0\n\n"
            "Press [ENTER] to Redeploy\n"
            "Press [Q] to Quit to Desktop"
        )
        self.over_stats_text.set_text_color(1, 1, 1, 0.95)
        np_s = self.game_over_root.attach_new_node(self.over_stats_text)
        np_s.set_pos(0, 0, -0.08)
        np_s.set_scale(0.046)

    def handle_menu_key(self, key):
        if self.game_state == 'MENU':
            self.selected_map_id = key
            print(f"Selected Map: {key}")
            self.start_game(self.selected_map_id)

    def handle_enter(self):
        if self.game_state == 'MENU':
            self.start_game(self.selected_map_id)
        elif self.game_state == 'GAME_OVER':
            self.start_game(self.selected_map_id)

    def handle_escape(self):
        if self.game_state == 'PLAYING':
            self.game_state = 'PAUSED'
            self.pause_root.show()
            self.unlock_mouse()
        elif self.game_state == 'PAUSED':
            self.game_state = 'PLAYING'
            self.pause_root.hide()
            self.lock_mouse()

    def return_to_menu(self):
        self.game_state = 'MENU'
        self.pause_root.hide()
        self.game_over_root.hide()
        self.menu_root.show()
        self.unlock_mouse()
        if self.hud:
            self.hud.cleanup()
        if self.minimap:
            self.minimap.cleanup()
        self.particle_mgr.cleanup()
        self.enemy_manager.cleanup()
        self.map_manager.cleanup()

    def start_game(self, map_id=1):
        print(f"Starting mission on Map {map_id}...")
        self.menu_root.hide()
        self.pause_root.hide()
        self.game_over_root.hide()
        
        # Cleanup any old run
        if self.hud:
            self.hud.cleanup()
        if self.minimap:
            self.minimap.cleanup()
        self.particle_mgr.cleanup()
        self.enemy_manager.cleanup()
        self.map_manager.cleanup()
        
        # Load map
        self.selected_map_id = map_id
        self.map_manager.load_map(map_id)
        
        # Initialize Player in safe staging cover
        spawn_pos = Vec3(0, -24, 0)
        self.player = Player(self, spawn_pos)
        
        # Initialize HUD & Minimap
        self.hud = HUD(self.aspect2d, self.render2d)
        self.minimap = Minimap(self.aspect2d, self.player, self.map_manager, self.enemy_manager)
        
        # Start initial wave with current time for reaction delay
        current_time = ClockObject.get_global_clock().get_real_time()
        self.enemy_manager.start_wave(1, self.map_manager.spawn_points, current_time=current_time)
        
        self.game_state = 'PLAYING'
        self.lock_mouse()

    def game_loop(self, task):
        dt = ClockObject.get_global_clock().get_dt()
        # Clamp dt to prevent frame lag leaps
        dt = min(0.05, max(0.001, dt))
        current_time = ClockObject.get_global_clock().get_real_time()
        
        if self.game_state == 'PLAYING':
            # Check player health
            if not self.player.is_alive:
                self.game_state = 'GAME_OVER'
                self.unlock_mouse()
                score = self.enemy_manager.enemies_killed * 100
                self.over_stats_text.set_text(
                    f"WAVES SURVIVED: {self.enemy_manager.wave_number}\n"
                    f"HOSTILES ELIMINATED: {self.enemy_manager.enemies_killed}\n"
                    f"TOTAL COMBAT SCORE: {score}\n\n"
                    "Press [ENTER] to Redeploy\n"
                    "Press [Q] to Quit to Desktop"
                )
                self.game_over_root.show()
                return task.cont

            # Update core modules
            self.player.update(dt, current_time, self.map_manager, self.enemy_manager, self.particle_mgr)
            self.map_manager.update(dt, current_time, self.player)
            self.enemy_manager.update(dt, current_time, self.player, self.map_manager)
            self.particle_mgr.update(dt)
            self.hud.update(dt, self.player, self.enemy_manager, self.player.get_current_weapon())
            self.minimap.update()
            
        elif self.game_state == 'PAUSED':
            # Check restart key inside pause menu
            pass

        return task.cont

    def quit_game(self):
        print("Exiting CYBER OPS...")
        if hasattr(self, 'sound_mgr') and self.sound_mgr:
            for s in self.sound_mgr.values():
                s.stop()
        sys.exit(0)

if __name__ == "__main__":
    game = CyberOpsGame()
    game.run()
