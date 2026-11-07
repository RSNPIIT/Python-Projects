"""
main.py - Main entry point for Modern Shooter Game in Panda3D.
Features a live 3D animated background lobby, interactive DirectGui buttons,
simplepbr shader pipeline integration, dynamic 360-degree aiming,
wave progression, and comprehensive game state management.
"""

import sys
import os
import math
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from panda3d.core import (
    WindowProperties, Vec3, Vec4, TextNode, CardMaker,
    loadPrcFileData, ClockObject
)

# Set Panda3D configuration before ShowBase
loadPrcFileData("", "window-title CYBER OPS: Modern Panda3D FPS")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video true")
# Keep the presentation clean; the game has no debug overlay by default.
loadPrcFileData("", "show-frame-rate-meter false")
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
        if not os.path.exists(sound_dir) or len(os.listdir(sound_dir)) < 10:
            print("Generating game audio assets...")
            generate_all_sounds(sound_dir)
            
        self.sound_mgr = load_sound_catalog(sound_dir)
        
        # Initialize SimplePBR shaders if window is available
        self.pbr_pipeline = None
        if self.win is not None:
            try:
                import simplepbr
                self.pbr_pipeline = simplepbr.init(
                    enable_fog=True,
                    enable_shadows=True,
                    max_lights=8,
                    msaa_samples=4,
                )
                print("SimplePBR lighting, shadows, and 4x MSAA active!")
            except Exception as e:
                print("PBR shader info:", e)
        
        # Game State: 'MENU', 'PLAYING', 'PAUSED', 'GAME_OVER'
        self.game_state = 'MENU'
        self.selected_map_id = 1
        self.mouse_locked = False
        
        # Sensitivity options for Trackpad & Mouse: (Label, Multiplier)
        self.sens_options = [
            ("NORMAL (1.0x)", 1.0),
            ("HIGH / TRACKPAD (1.8x)", 1.8),
            ("ULTRA (2.6x)", 2.6),
            ("LOW (0.6x)", 0.6)
        ]
        self.sens_idx = 1  # Default to High/Trackpad friendly!
        
        # Managers
        self.particle_mgr = ParticleManager(self.render)
        self.map_manager = MapManager(self.render, self.particle_mgr, self.sound_mgr)
        self.enemy_manager = EnemyManager(self.render, self.particle_mgr, self.sound_mgr)
        self.player = None
        self.hud = None
        self.minimap = None
        
        # Menu animation state
        self.menu_cam_angle = 0.0
        
        # Root nodes in aspect2d
        self.menu_root = self.aspect2d.attach_new_node("menu_root")
        self.pause_root = self.aspect2d.attach_new_node("pause_root")
        self.game_over_root = self.aspect2d.attach_new_node("game_over_root")
        
        self.pause_root.hide()
        self.game_over_root.hide()
        
        # Build 3D background lobby
        self.map_manager.load_map(1)
        
        self.build_main_menu()
        self.build_pause_menu()
        self.build_game_over_menu()
        
        # Global hotkeys
        self.accept('escape', self.handle_escape)
        self.accept('p', self.handle_escape)
        self.accept('enter', self.handle_enter)
        self.accept('1', self.select_map, [1])
        self.accept('2', self.select_map, [2])
        self.accept('q', self.handle_q_key)
        
        # Click anywhere to capture
        self.accept('mouse1', self.on_global_click)
        
        # Start game update loop
        self.taskMgr.add(self.game_loop, "game_loop")

    def play_ui_sound(self, sound_name):
        if self.sound_mgr and sound_name in self.sound_mgr:
            self.sound_mgr[sound_name].play()

    def handle_q_key(self):
        if self.game_state in ('MENU', 'PAUSED', 'GAME_OVER'):
            self.quit_game()

    def on_global_click(self):
        if self.game_state == 'PLAYING' and not self.mouse_locked:
            self.lock_mouse()

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
        if self.player:
            self.player.last_mouse_x = cx
            self.player.last_mouse_y = cy

    def unlock_mouse(self):
        if self.win is None:
            self.mouse_locked = False
            return
        props = WindowProperties()
        props.set_cursor_hidden(False)
        props.set_mouse_mode(WindowProperties.M_absolute)
        self.win.request_properties(props)
        self.mouse_locked = False

    def select_map(self, map_id):
        if self.game_state != 'MENU':
            return
        self.selected_map_id = map_id
        self.play_ui_sound('ui_click')
        
        # Update button highlights
        if hasattr(self, 'btn_map1') and hasattr(self, 'btn_map2'):
            if map_id == 1:
                self.btn_map1['frameColor'] = (0.05, 0.45, 0.65, 0.95)
                self.btn_map2['frameColor'] = (0.08, 0.12, 0.18, 0.8)
                self.btn_map1['text'] = "[ ACTIVE ] SECTOR 7 // CYBER FACILITY\nElevators • Catwalks • Night Ops"
                self.btn_map2['text'] = "[ 02 ] RUINS OF OASIS // DESERT OUTPOST\nSandstone Fort • Hover Shuttle • Courtyard"
            else:
                self.btn_map1['frameColor'] = (0.08, 0.12, 0.18, 0.8)
                self.btn_map2['frameColor'] = (0.65, 0.45, 0.1, 0.95)
                self.btn_map1['text'] = "[ 01 ] SECTOR 7 // CYBER FACILITY\nElevators • Catwalks • Night Ops"
                self.btn_map2['text'] = "[ ACTIVE ] RUINS OF OASIS // DESERT OUTPOST\nSandstone Fort • Hover Shuttle • Courtyard"

    def cycle_sensitivity(self):
        self.sens_idx = (self.sens_idx + 1) % len(self.sens_options)
        label, mult = self.sens_options[self.sens_idx]
        self.play_ui_sound('ui_click')
        if hasattr(self, 'btn_sens'):
            self.btn_sens['text'] = f"AIM SENSITIVITY: [ {label} ]"
        if self.player:
            self.player.sens_multiplier = mult

    # ==============================================================================
    # 1. AAA ANIMATED MAIN MENU WITH INTERACTIVE BUTTONS
    # ==============================================================================
    def build_main_menu(self):
        # Subtle dark gradient vignette backing (translucent so 3D background shines through!)
        cm = CardMaker("menu_vignette")
        cm.set_frame(-2.0, 2.0, -2.0, 2.0)
        vignette = self.menu_root.attach_new_node(cm.generate())
        vignette.set_color(Vec4(0.02, 0.04, 0.07, 0.65))
        vignette.set_transparency(True)
        
        # Header Title
        t = TextNode("title")
        t.set_text("CYBER OPS // VANGUARD")
        t.set_align(TextNode.A_center)
        t.set_text_color(0.1, 0.9, 1.0, 1.0)
        np_t = self.menu_root.attach_new_node(t)
        np_t.set_pos(0, 0, 0.68)
        np_t.set_scale(0.095)
        
        # Subtitle
        self.menu_subtitle = TextNode("subtitle")
        self.menu_subtitle.set_text("TACTICAL 3D ENGAGEMENT SYSTEM")
        self.menu_subtitle.set_align(TextNode.A_center)
        self.menu_subtitle.set_text_color(0.8, 0.9, 1.0, 0.9)
        self.np_sub = self.menu_root.attach_new_node(self.menu_subtitle)
        self.np_sub.set_pos(0, 0, 0.58)
        self.np_sub.set_scale(0.042)
        
        # Interactive Map 1 Button
        self.btn_map1 = DirectButton(
            parent=self.menu_root,
            text="[ ACTIVE ] SECTOR 7 // CYBER FACILITY\nElevators • Catwalks • Night Ops",
            scale=0.038,
            pos=(-0.45, 0, 0.32),
            pad=(0.4, 0.3),
            frameColor=(0.05, 0.45, 0.65, 0.95),
            text_fg=(1, 1, 1, 1),
            text_scale=0.9,
            relief=1,
            borderWidth=(0.04, 0.04),
            command=self.select_map,
            extraArgs=[1]
        )
        self.btn_map1.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Interactive Map 2 Button
        self.btn_map2 = DirectButton(
            parent=self.menu_root,
            text="[ 02 ] RUINS OF OASIS // DESERT OUTPOST\nSandstone Fort • Hover Shuttle • Courtyard",
            scale=0.038,
            pos=(0.45, 0, 0.32),
            pad=(0.4, 0.3),
            frameColor=(0.08, 0.12, 0.18, 0.8),
            text_fg=(0.9, 0.9, 0.9, 0.9),
            text_scale=0.9,
            relief=1,
            borderWidth=(0.04, 0.04),
            command=self.select_map,
            extraArgs=[2]
        )
        self.btn_map2.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Deploy Operator Button (Big Glowing Center Button)
        self.btn_deploy = DirectButton(
            parent=self.menu_root,
            text=">>  DEPLOY OPERATOR  <<",
            scale=0.055,
            pos=(0, 0, 0.08),
            pad=(0.6, 0.35),
            frameColor=(0.0, 0.75, 1.0, 0.9),
            text_fg=(0.02, 0.05, 0.1, 1.0),
            relief=1,
            borderWidth=(0.05, 0.05),
            command=self.start_game_button
        )
        self.btn_deploy.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Aim Sensitivity Button (Cycles sensitivity for trackpad/mouse)
        sens_label, _ = self.sens_options[self.sens_idx]
        self.btn_sens = DirectButton(
            parent=self.menu_root,
            text=f"AIM SENSITIVITY: [ {sens_label} ]",
            scale=0.038,
            pos=(0, 0, -0.12),
            pad=(0.5, 0.25),
            frameColor=(0.1, 0.15, 0.22, 0.85),
            text_fg=(0.2, 0.9, 1.0, 1.0),
            relief=1,
            borderWidth=(0.03, 0.03),
            command=self.cycle_sensitivity
        )
        self.btn_sens.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Exit Button
        self.btn_exit = DirectButton(
            parent=self.menu_root,
            text="EXIT TO DESKTOP",
            scale=0.034,
            pos=(0, 0, -0.28),
            pad=(0.4, 0.2),
            frameColor=(0.18, 0.08, 0.08, 0.85),
            text_fg=(1.0, 0.4, 0.4, 0.95),
            relief=1,
            borderWidth=(0.03, 0.03),
            command=self.quit_game
        )
        self.btn_exit.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Controls Cheat-Sheet Card (Bottom)
        cm_c = CardMaker("ctrl_card")
        cm_c.set_frame(-1.15, 1.15, -0.20, 0.08)
        c_np = self.menu_root.attach_new_node(cm_c.generate())
        c_np.set_pos(0, 0, -0.68)
        c_np.set_color(Vec4(0.04, 0.07, 0.11, 0.85))
        c_np.set_transparency(True)
        
        ctrl_text = TextNode("ctrl_summary")
        ctrl_text.set_align(TextNode.A_center)
        ctrl_text.set_text(
            "OPERATOR CONTROLS:\n"
            "WASD: Movement  |  Shift: Sprint  |  C / Ctrl: Crouch  |  Space: Jump\n"
            "Mouse / Trackpad: 360° Aim  |  Arrow Keys or Q/E: 360° Keyboard Aim\n"
            "Left Click: Fire  |  Right Click: ADS / Sniper Scope  |  1-4: Switch  |  F: Inspect  |  R: Reload"
        )
        ctrl_text.set_text_color(0.2, 0.9, 0.6, 0.95)
        np_c = self.menu_root.attach_new_node(ctrl_text)
        np_c.set_pos(0, 0, -0.68)
        np_c.set_scale(0.032)

    # ==============================================================================
    # 2. INTERACTIVE PAUSE MENU
    # ==============================================================================
    def build_pause_menu(self):
        cm = CardMaker("pause_bg")
        cm.set_frame(-2.0, 2.0, -2.0, 2.0)
        bg = self.pause_root.attach_new_node(cm.generate())
        bg.set_color(Vec4(0.03, 0.05, 0.08, 0.88))
        bg.set_transparency(True)
        
        t = TextNode("pause_title")
        t.set_text("// MISSION PAUSED //")
        t.set_align(TextNode.A_center)
        t.set_text_color(1.0, 0.85, 0.1, 1.0)
        np_t = self.pause_root.attach_new_node(t)
        np_t.set_pos(0, 0, 0.42)
        np_t.set_scale(0.08)
        
        # Resume Button
        self.btn_resume = DirectButton(
            parent=self.pause_root,
            text="RESUME COMBAT",
            scale=0.045,
            pos=(0, 0, 0.18),
            pad=(0.5, 0.25),
            frameColor=(0.0, 0.75, 1.0, 0.9),
            text_fg=(0.02, 0.05, 0.1, 1.0),
            relief=1,
            command=self.handle_escape
        )
        self.btn_resume.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Restart Button
        self.btn_restart = DirectButton(
            parent=self.pause_root,
            text="RESTART MISSION",
            scale=0.042,
            pos=(0, 0, 0.02),
            pad=(0.4, 0.2),
            frameColor=(0.1, 0.15, 0.22, 0.85),
            text_fg=(1, 1, 1, 1),
            relief=1,
            command=self.restart_mission
        )
        self.btn_restart.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Return to Lobby
        self.btn_lobby = DirectButton(
            parent=self.pause_root,
            text="RETURN TO MAIN MENU",
            scale=0.042,
            pos=(0, 0, -0.14),
            pad=(0.4, 0.2),
            frameColor=(0.1, 0.15, 0.22, 0.85),
            text_fg=(1, 1, 1, 1),
            relief=1,
            command=self.return_to_menu
        )
        self.btn_lobby.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Quit Button
        self.btn_pause_quit = DirectButton(
            parent=self.pause_root,
            text="QUIT TO DESKTOP",
            scale=0.038,
            pos=(0, 0, -0.30),
            pad=(0.4, 0.2),
            frameColor=(0.2, 0.08, 0.08, 0.85),
            text_fg=(1.0, 0.4, 0.4, 0.95),
            relief=1,
            command=self.quit_game
        )
        self.btn_pause_quit.bind('enter', lambda e: self.play_ui_sound('ui_hover'))

    # ==============================================================================
    # 3. INTERACTIVE GAME OVER MENU
    # ==============================================================================
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
        np_t.set_pos(0, 0, 0.42)
        np_t.set_scale(0.075)
        
        self.over_stats_text = TextNode("over_stats")
        self.over_stats_text.set_align(TextNode.A_center)
        self.over_stats_text.set_text("WAVES SURVIVED: 0\nHOSTILES ELIMINATED: 0\nTOTAL COMBAT SCORE: 0")
        self.over_stats_text.set_text_color(1, 1, 1, 0.95)
        np_s = self.game_over_root.attach_new_node(self.over_stats_text)
        np_s.set_pos(0, 0, 0.15)
        np_s.set_scale(0.046)
        
        # Redeploy Button
        self.btn_redeploy = DirectButton(
            parent=self.game_over_root,
            text=">>  REDEPLOY OPERATOR  <<",
            scale=0.048,
            pos=(0, 0, -0.12),
            pad=(0.5, 0.25),
            frameColor=(0.0, 0.75, 1.0, 0.9),
            text_fg=(0.02, 0.05, 0.1, 1.0),
            relief=1,
            command=self.start_game_button
        )
        self.btn_redeploy.bind('enter', lambda e: self.play_ui_sound('ui_hover'))
        
        # Return to Lobby
        self.btn_over_lobby = DirectButton(
            parent=self.game_over_root,
            text="RETURN TO MAIN MENU",
            scale=0.042,
            pos=(0, 0, -0.28),
            pad=(0.4, 0.2),
            frameColor=(0.1, 0.15, 0.22, 0.85),
            text_fg=(1, 1, 1, 1),
            relief=1,
            command=self.return_to_menu
        )
        self.btn_over_lobby.bind('enter', lambda e: self.play_ui_sound('ui_hover'))

    def start_game_button(self):
        self.play_ui_sound('ui_click')
        self.start_game(self.selected_map_id)

    def restart_mission(self):
        self.play_ui_sound('ui_click')
        self.start_game(self.selected_map_id)

    def handle_enter(self):
        if self.game_state in ('MENU', 'GAME_OVER'):
            self.start_game(self.selected_map_id)

    def handle_escape(self):
        if self.game_state == 'PLAYING':
            self.game_state = 'PAUSED'
            self.pause_root.show()
            self.unlock_mouse()
            self.play_ui_sound('ui_click')
        elif self.game_state == 'PAUSED':
            self.game_state = 'PLAYING'
            self.pause_root.hide()
            self.lock_mouse()
            self.play_ui_sound('ui_click')

    def return_to_menu(self):
        self.game_state = 'MENU'
        self.pause_root.hide()
        self.game_over_root.hide()
        self.menu_root.show()
        self.unlock_mouse()
        self.play_ui_sound('ui_click')

        if self.player:
            self.player.cleanup()
            self.player = None
        
        if self.hud:
            self.hud.cleanup()
            self.hud = None
        if self.minimap:
            self.minimap.cleanup()
            self.minimap = None
        self.particle_mgr.cleanup()
        self.enemy_manager.cleanup()
        self.map_manager.cleanup()
        
        # Load showcase background
        self.map_manager.load_map(self.selected_map_id)

    def start_game(self, map_id=1):
        print(f"Starting mission on Map {map_id}...")
        self.menu_root.hide()
        self.pause_root.hide()
        self.game_over_root.hide()

        if self.player:
            self.player.cleanup()
            self.player = None
        
        if self.hud:
            self.hud.cleanup()
        if self.minimap:
            self.minimap.cleanup()
        self.particle_mgr.cleanup()
        self.enemy_manager.cleanup()
        self.map_manager.cleanup()
        
        self.selected_map_id = map_id
        self.map_manager.load_map(map_id)
        
        # Initialize Player in safe staging cover
        spawn_pos = Vec3(0, -24, 0)
        self.player = Player(self, spawn_pos)
        
        # Apply selected sensitivity multiplier
        _, sens_mult = self.sens_options[self.sens_idx]
        self.player.sens_multiplier = sens_mult
        
        self.hud = HUD(self.aspect2d, self.render2d)
        self.minimap = Minimap(self.aspect2d, self.player, self.map_manager, self.enemy_manager)
        
        current_time = ClockObject.get_global_clock().get_real_time()
        self.enemy_manager.start_wave(1, self.map_manager.spawn_points, current_time=current_time)
        
        self.game_state = 'PLAYING'
        self.lock_mouse()

    def game_loop(self, task):
        dt = ClockObject.get_global_clock().get_dt()
        dt = min(0.05, max(0.001, dt))
        current_time = ClockObject.get_global_clock().get_real_time()
        
        if self.game_state == 'MENU':
            # 3D Cinematic Lobby Orbit Camera
            self.map_manager.animate_environment(dt, current_time)
            self.menu_cam_angle += dt * 10.0
            rad = math.radians(self.menu_cam_angle)
            cam_x = math.cos(rad) * 22.0
            cam_y = math.sin(rad) * 22.0
            if self.camera is not None:
                self.camera.set_pos(cam_x, cam_y, 6.0)
                self.camera.look_at(0, 0, 1.8)
            
            # Animate deploy button pulse glow
            if hasattr(self, 'btn_deploy'):
                pulse = (math.sin(current_time * 5.0) + 1.0) * 0.5
                c_val = 0.65 + pulse * 0.35
                self.btn_deploy['frameColor'] = (0.0, c_val, 1.0, 0.95)

        elif self.game_state == 'PLAYING':
            if not self.player.is_alive:
                self.game_state = 'GAME_OVER'
                self.unlock_mouse()
                score = self.enemy_manager.enemies_killed * 100
                self.over_stats_text.set_text(
                    f"WAVES SURVIVED: {self.enemy_manager.wave_number}\n"
                    f"HOSTILES ELIMINATED: {self.enemy_manager.enemies_killed}\n"
                    f"TOTAL COMBAT SCORE: {score}"
                )
                self.player.cleanup()
                self.player = None
                self.game_over_root.show()
                return task.cont

            self.player.update(dt, current_time, self.map_manager, self.enemy_manager, self.particle_mgr)
            self.map_manager.update(dt, current_time, self.player)
            self.enemy_manager.update(dt, current_time, self.player, self.map_manager)
            self.particle_mgr.update(dt)
            self.hud.update(dt, self.player, self.enemy_manager, self.player.get_current_weapon())
            self.minimap.update()

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
