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
    WindowProperties, Vec3, Vec4, TextNode, CardMaker, LineSegs,
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
        self.preview_map_id = map_id
        self.play_ui_sound('ui_click')
        self.refresh_map_cards()

    def cycle_sensitivity(self):
        self.sens_idx = (self.sens_idx + 1) % len(self.sens_options)
        label, mult = self.sens_options[self.sens_idx]
        self.play_ui_sound('ui_click')
        if hasattr(self, 'sens_value_node'):
            self.sens_value_node.set_text(label)
        if self.player:
            self.player.sens_multiplier = mult

    def _ui_panel(self, parent, name, x, z, width, height, color):
        cm = CardMaker(name)
        cm.set_frame(-width * 0.5, width * 0.5, -height * 0.5, height * 0.5)
        panel = parent.attach_new_node(cm.generate())
        panel.set_pos(x, 0, z)
        panel.set_color(color)
        if color.w < 1.0:
            panel.set_transparency(True)
        panel.set_depth_test(False)
        panel.set_depth_write(False)
        return panel

    def _ui_label(self, parent, name, text, x, z, scale, color, align=TextNode.A_left):
        node = TextNode(name)
        node.set_text(text)
        node.set_align(align)
        node.set_text_color(*color)
        np = parent.attach_new_node(node)
        np.set_pos(x, -0.012, z)
        np.set_scale(scale)
        np.set_depth_test(False)
        np.set_depth_write(False)
        return node, np

    def _ui_line(self, parent, name, points, color, thickness=1.2):
        lines = LineSegs(name)
        lines.set_thickness(thickness)
        lines.set_color(color)
        for index, (x, z) in enumerate(points):
            if index == 0:
                lines.move_to(x, -0.01, z)
            else:
                lines.draw_to(x, -0.01, z)
        path = parent.attach_new_node(lines.create())
        path.set_depth_test(False)
        path.set_depth_write(False)
        return path

    def _ui_button(self, parent, name, x, z, width, height, command, extra_args=None):
        button = DirectButton(
            parent=parent,
            text="",
            pos=(x, 0.01, z),
            frameSize=(-width * 0.5, width * 0.5, -height * 0.5, height * 0.5),
            frameColor=(0.0, 0.0, 0.0, 0.0),
            relief=0,
            borderWidth=(0.0, 0.0),
            command=command,
            extraArgs=extra_args or [],
            text_scale=0.01,
        )
        return button

    def preview_map(self, map_id, play_sound=True):
        if self.game_state != 'MENU':
            return
        if play_sound and getattr(self, 'preview_map_id', None) != map_id:
            self.play_ui_sound('ui_hover')
        self.preview_map_id = map_id
        self.refresh_map_cards()

    def refresh_map_cards(self):
        if not hasattr(self, 'map_cards'):
            return
        map_copy = {
            1: (
                "SECTOR 7",
                "CYBER FACILITY  /  NIGHT OPERATIONS",
                "Tight industrial lanes. Elevators and catwalks\ncreate shifting routes through the facility.",
                "THREAT LEVEL  /  ELEVATED",
                "ENVIRONMENT  /  LOW VISIBILITY",
            ),
            2: (
                "RUINS OF OASIS",
                "DESERT OUTPOST  /  OPEN TERRAIN",
                "A sandstone stronghold with exposed crossings,\nraised ruins and a moving hover platform.",
                "THREAT LEVEL  /  HIGH",
                "ENVIRONMENT  /  DUST HAZE",
            ),
        }
        title, subtitle, body, threat, conditions = map_copy[self.preview_map_id]
        self.brief_title_node.set_text(title)
        self.brief_subtitle_node.set_text(subtitle)
        self.brief_body_node.set_text(body)
        self.brief_threat_node.set_text(threat)
        self.brief_condition_node.set_text(conditions)
        for map_id, card in self.map_cards.items():
            active = map_id == self.preview_map_id
            card['target'] = 1.0 if active else 0.0
            card['status'].set_text("SELECTED  /  READY" if map_id == self.selected_map_id else "PREVIEW  /  CLICK TO SELECT")
            status_color = (0.2, 0.95, 0.72, 1.0) if map_id == self.selected_map_id else (0.56, 0.68, 0.74, 0.88)
            card['status'].set_text_color(*status_color)

    # ==============================================================================
    # 1. Tactical deployment menu
    # ==============================================================================
    def build_main_menu(self):
        self.preview_map_id = self.selected_map_id
        self.map_cards = {}

        # Leave the arena visible, with clear left and right reading zones.
        self._ui_panel(self.menu_root, "menu_scrim", 0.0, 0.0, 3.56, 2.0, Vec4(0.008, 0.018, 0.03, 0.26))
        self._ui_panel(self.menu_root, "menu_left_rail", -1.04, 0.0, 1.48, 1.97, Vec4(0.008, 0.022, 0.04, 0.88))
        self._ui_panel(self.menu_root, "menu_brief_panel", 1.04, 0.035, 1.38, 1.49, Vec4(0.008, 0.022, 0.04, 0.77))
        self._ui_line(self.menu_root, "menu_rail_edge", [(-0.30, -0.98), (-0.30, 0.98)], Vec4(0.0, 0.72, 0.88, 0.55), 1.1)

        self._ui_panel(self.menu_root, "brand_mark", -1.60, 0.84, 0.055, 0.055, Vec4(0.0, 0.88, 1.0, 1.0))
        self._ui_label(self.menu_root, "brand_name", "CYBER OPS  /  VANGUARD", -1.53, 0.825, 0.027, (0.67, 0.88, 0.94, 1.0))
        self._ui_label(self.menu_root, "system_status", "TACTICAL NETWORK  //  ONLINE", 1.66, 0.84, 0.022, (0.23, 0.91, 0.72, 1.0), TextNode.A_right)

        self._ui_label(self.menu_root, "menu_title", "CYBER OPS", -1.61, 0.61, 0.105, (0.93, 0.98, 1.0, 1.0))
        self._ui_label(self.menu_root, "menu_subtitle", "VANGUARD RESPONSE UNIT", -1.59, 0.535, 0.027, (0.13, 0.82, 0.96, 1.0))
        self._ui_line(self.menu_root, "menu_title_rule", [(-1.60, 0.485), (-0.43, 0.485)], Vec4(0.08, 0.43, 0.55, 0.8), 1.2)
        self._ui_label(self.menu_root, "operation_label", "SELECT OPERATION", -1.58, 0.34, 0.033, (0.89, 0.94, 0.97, 1.0))
        self._ui_label(self.menu_root, "operation_count", "02 AVAILABLE", -0.42, 0.34, 0.021, (0.47, 0.63, 0.70, 1.0), TextNode.A_right)

        card_specs = [
            (1, -0.98, 0.12, "01  /  SECTOR 7", "CYBER FACILITY  •  NIGHT OPERATIONS"),
            (2, -0.98, -0.15, "02  /  RUINS OF OASIS", "DESERT OUTPOST  •  OPEN TERRAIN"),
        ]
        for map_id, x, z, title, subtitle in card_specs:
            panel = self._ui_panel(self.menu_root, f"mission_card_{map_id}", x, z, 1.28, 0.22, Vec4(0.018, 0.045, 0.075, 0.88))
            stripe = self._ui_panel(self.menu_root, f"mission_stripe_{map_id}", -1.595, z, 0.035, 0.22, Vec4(0.13, 0.25, 0.34, 0.9))
            border = self._ui_line(self.menu_root, f"mission_border_{map_id}", [(-1.62, z - 0.11), (-0.34, z - 0.11), (-0.34, z + 0.11), (-1.62, z + 0.11), (-1.62, z - 0.11)], Vec4(0.16, 0.28, 0.36, 0.75), 1.0)
            self._ui_label(self.menu_root, f"mission_title_{map_id}", title, -1.52, z + 0.025, 0.031, (0.91, 0.97, 1.0, 1.0))
            self._ui_label(self.menu_root, f"mission_subtitle_{map_id}", subtitle, -1.51, z - 0.052, 0.019, (0.60, 0.73, 0.78, 1.0))
            status_node, _ = self._ui_label(self.menu_root, f"mission_status_{map_id}", "", -0.43, z + 0.07, 0.016, (0.55, 0.68, 0.74, 0.88), TextNode.A_right)
            card = {"panel": panel, "stripe": stripe, "border": border, "status": status_node}
            card['mix'] = 1.0 if map_id == self.preview_map_id else 0.0
            card['target'] = card['mix']
            self.map_cards[map_id] = card
            button = self._ui_button(self.menu_root, f"mission_target_{map_id}", x, z, 1.28, 0.22, self.select_map, [map_id])
            button.bind('enter', lambda _event, selected=map_id: self.preview_map(selected))
            button.bind('exit', lambda _event: self.preview_map(self.selected_map_id, play_sound=False))
            if map_id == 1:
                self.btn_map1 = button
            else:
                self.btn_map2 = button

        self.deploy_panel = self._ui_panel(self.menu_root, "deploy_panel", -0.98, -0.48, 1.28, 0.15, Vec4(0.015, 0.26, 0.34, 0.98))
        self.deploy_accent = self._ui_panel(self.menu_root, "deploy_accent", -1.59, -0.48, 0.035, 0.15, Vec4(0.0, 0.86, 1.0, 1.0))
        self._ui_label(self.menu_root, "deploy_label", "DEPLOY OPERATOR", -0.98, -0.494, 0.037, (0.95, 0.99, 1.0, 1.0), TextNode.A_center)
        self.btn_deploy = self._ui_button(self.menu_root, "deploy_target", -0.98, -0.48, 1.28, 0.15, self.start_game_button)
        self.btn_deploy.bind('enter', lambda _event: self.play_ui_sound('ui_hover'))

        self._ui_label(self.menu_root, "sensitivity_label", "AIM SENSITIVITY", -1.52, -0.662, 0.019, (0.48, 0.65, 0.72, 1.0))
        sens_label, _ = self.sens_options[self.sens_idx]
        self.sens_value_node, _ = self._ui_label(self.menu_root, "sensitivity_value", sens_label, -0.43, -0.662, 0.021, (0.16, 0.83, 0.96, 1.0), TextNode.A_right)
        self._ui_line(self.menu_root, "settings_rule", [(-1.58, -0.695), (-0.39, -0.695)], Vec4(0.15, 0.27, 0.34, 0.7), 0.8)
        self.btn_sens = self._ui_button(self.menu_root, "sensitivity_target", -0.98, -0.666, 1.22, 0.075, self.cycle_sensitivity)
        self.btn_sens.bind('enter', lambda _event: self.play_ui_sound('ui_hover'))

        self._ui_label(self.menu_root, "exit_label", "Q   EXIT TO DESKTOP", -1.52, -0.79, 0.021, (0.77, 0.39, 0.42, 0.95))
        self.btn_exit = self._ui_button(self.menu_root, "exit_target", -0.98, -0.79, 1.22, 0.085, self.quit_game)
        self.btn_exit.bind('enter', lambda _event: self.play_ui_sound('ui_hover'))

        self._ui_label(self.menu_root, "brief_kicker", "FIELD INTELLIGENCE  /  01", 0.43, 0.65, 0.022, (0.16, 0.84, 0.96, 1.0))
        self.brief_title_node, _ = self._ui_label(self.menu_root, "brief_title", "", 0.43, 0.49, 0.064, (0.94, 0.98, 1.0, 1.0))
        self.brief_subtitle_node, _ = self._ui_label(self.menu_root, "brief_subtitle", "", 0.44, 0.415, 0.019, (0.52, 0.76, 0.83, 1.0))
        self.brief_body_node, _ = self._ui_label(self.menu_root, "brief_body", "", 0.44, 0.315, 0.024, (0.77, 0.85, 0.88, 1.0))

        # A compact tactical schematic gives the briefing panel a useful focal point.
        self._ui_panel(self.menu_root, "schematic_panel", 1.04, 0.0, 1.10, 0.46, Vec4(0.012, 0.035, 0.055, 0.95))
        self._ui_line(self.menu_root, "schematic_border", [(0.49, -0.23), (1.59, -0.23), (1.59, 0.23), (0.49, 0.23), (0.49, -0.23)], Vec4(0.08, 0.31, 0.39, 0.9), 1.0)
        for gx in (0.70, 0.91, 1.12, 1.33, 1.54):
            self._ui_line(self.menu_root, f"schematic_v_{gx}", [(gx, -0.21), (gx, 0.21)], Vec4(0.10, 0.24, 0.30, 0.62), 0.6)
        for gz in (-0.16, -0.055, 0.055, 0.16):
            self._ui_line(self.menu_root, f"schematic_h_{gz}", [(0.51, gz), (1.57, gz)], Vec4(0.10, 0.24, 0.30, 0.62), 0.6)
        self._ui_line(self.menu_root, "schematic_route", [(0.59, -0.16), (0.80, -0.16), (0.80, 0.04), (1.12, 0.04), (1.12, 0.15), (1.47, 0.15)], Vec4(0.05, 0.88, 0.95, 0.95), 2.0)
        for index, (x, z) in enumerate(((0.59, -0.16), (0.80, 0.04), (1.12, 0.15), (1.47, 0.15))):
            marker_color = Vec4(1.0, 0.32, 0.24, 1.0) if index in (1, 3) else Vec4(0.2, 0.94, 0.75, 1.0)
            self._ui_panel(self.menu_root, f"schematic_marker_{index}", x, z, 0.035, 0.035, marker_color)
        self.brief_threat_node, _ = self._ui_label(self.menu_root, "brief_threat", "", 0.44, -0.34, 0.021, (1.0, 0.62, 0.3, 1.0))
        self.brief_condition_node, _ = self._ui_label(self.menu_root, "brief_condition", "", 0.44, -0.43, 0.021, (0.59, 0.73, 0.78, 1.0))
        self._ui_label(self.menu_root, "brief_hint", "SURVIVE THE WAVES  /  RESUPPLY IN FIELD", 0.44, -0.55, 0.017, (0.32, 0.54, 0.62, 0.95))
        self.refresh_map_cards()

        self._ui_panel(self.menu_root, "control_bar", 0.0, -0.92, 3.34, 0.13, Vec4(0.006, 0.018, 0.03, 0.94))
        self._ui_line(self.menu_root, "control_bar_top", [(-1.67, -0.855), (1.67, -0.855)], Vec4(0.03, 0.56, 0.68, 0.75), 1.0)
        self._ui_label(
            self.menu_root,
            "control_summary",
            "WASD MOVE     SHIFT SPRINT     MOUSE AIM / FIRE     1–4 OR SCROLL SWITCH WEAPON     R RELOAD     ESC PAUSE",
            -1.56,
            -0.94,
            0.022,
            (0.64, 0.78, 0.82, 1.0),
        )
        self.menu_fade = 0.0
        self.menu_root.set_alpha_scale(0.0)

    # ==============================================================================
    # 2. Pause overlay
    # ==============================================================================
    def build_pause_menu(self):
        self._ui_panel(self.pause_root, "pause_scrim", 0.0, 0.0, 3.56, 2.0, Vec4(0.005, 0.012, 0.022, 0.82))
        self._ui_panel(self.pause_root, "pause_card", 0.0, 0.02, 1.32, 1.42, Vec4(0.012, 0.034, 0.055, 0.98))
        self._ui_line(self.pause_root, "pause_card_outline", [(-0.66, -0.69), (0.66, -0.69), (0.66, 0.73), (-0.66, 0.73), (-0.66, -0.69)], Vec4(0.04, 0.52, 0.64, 0.9), 1.2)
        self._ui_label(self.pause_root, "pause_kicker", "TACTICAL NETWORK  /  HOLD", 0.0, 0.59, 0.022, (0.14, 0.82, 0.94, 1.0), TextNode.A_center)
        self._ui_label(self.pause_root, "pause_title", "MISSION PAUSED", 0.0, 0.42, 0.058, (0.94, 0.98, 1.0, 1.0), TextNode.A_center)
        self._ui_line(self.pause_root, "pause_rule", [(-0.48, 0.34), (0.48, 0.34)], Vec4(0.11, 0.34, 0.42, 0.9), 1.0)

        actions = [
            ("RESUME COMBAT", 0.20, self.handle_escape, Vec4(0.014, 0.27, 0.35, 0.95), (0.92, 0.98, 1.0, 1.0)),
            ("RESTART MISSION", 0.00, self.restart_mission, Vec4(0.025, 0.075, 0.11, 0.95), (0.78, 0.88, 0.91, 1.0)),
            ("RETURN TO LOBBY", -0.20, self.return_to_menu, Vec4(0.025, 0.075, 0.11, 0.95), (0.78, 0.88, 0.91, 1.0)),
            ("QUIT TO DESKTOP", -0.40, self.quit_game, Vec4(0.12, 0.035, 0.045, 0.95), (1.0, 0.55, 0.54, 1.0)),
        ]
        targets = []
        for label, z, command, color, text_color in actions:
            self._ui_panel(self.pause_root, f"pause_action_{label}", 0.0, z, 0.98, 0.145, color)
            self._ui_label(self.pause_root, f"pause_label_{label}", label, 0.0, z - 0.012, 0.027, text_color, TextNode.A_center)
            target = self._ui_button(self.pause_root, f"pause_target_{label}", 0.0, z, 0.98, 0.145, command)
            target.bind('enter', lambda _event: self.play_ui_sound('ui_hover'))
            targets.append(target)
        self.btn_resume, self.btn_restart, self.btn_lobby, self.btn_pause_quit = targets

    # ==============================================================================
    # 3. Mission failed overlay
    # ==============================================================================
    def build_game_over_menu(self):
        self._ui_panel(self.game_over_root, "over_scrim", 0.0, 0.0, 3.56, 2.0, Vec4(0.025, 0.006, 0.014, 0.84))
        self._ui_panel(self.game_over_root, "over_card", 0.0, 0.0, 1.46, 1.34, Vec4(0.035, 0.018, 0.03, 0.98))
        self._ui_line(self.game_over_root, "over_outline", [(-0.73, -0.67), (0.73, -0.67), (0.73, 0.67), (-0.73, 0.67), (-0.73, -0.67)], Vec4(0.8, 0.16, 0.2, 0.95), 1.2)
        self._ui_label(self.game_over_root, "over_kicker", "COMMS LOST  /  OPERATOR DOWN", 0.0, 0.52, 0.022, (1.0, 0.38, 0.35, 1.0), TextNode.A_center)
        self._ui_label(self.game_over_root, "over_title", "MISSION FAILED", 0.0, 0.35, 0.062, (1.0, 0.86, 0.86, 1.0), TextNode.A_center)
        self.over_stats_text, _ = self._ui_label(
            self.game_over_root,
            "over_stats",
            "WAVES SURVIVED  /  0\nHOSTILES ELIMINATED  /  0\nCOMBAT SCORE  /  0",
            0.0,
            0.07,
            0.031,
            (0.8, 0.86, 0.89, 1.0),
            TextNode.A_center,
        )

        self._ui_panel(self.game_over_root, "redeploy_panel", 0.0, -0.27, 1.08, 0.15, Vec4(0.015, 0.27, 0.35, 0.98))
        self._ui_label(self.game_over_root, "redeploy_label", "REDEPLOY OPERATOR", 0.0, -0.282, 0.027, (0.94, 0.99, 1.0, 1.0), TextNode.A_center)
        self.btn_redeploy = self._ui_button(self.game_over_root, "redeploy_target", 0.0, -0.27, 1.08, 0.15, self.start_game_button)
        self.btn_redeploy.bind('enter', lambda _event: self.play_ui_sound('ui_hover'))
        self._ui_label(self.game_over_root, "over_lobby_label", "RETURN TO LOBBY", 0.0, -0.50, 0.025, (0.66, 0.77, 0.82, 1.0), TextNode.A_center)
        self.btn_over_lobby = self._ui_button(self.game_over_root, "over_lobby_target", 0.0, -0.50, 1.08, 0.12, self.return_to_menu)
        self.btn_over_lobby.bind('enter', lambda _event: self.play_ui_sound('ui_hover'))

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
            self.pause_fade = 0.0
            self.pause_root.set_alpha_scale(0.0)
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
        self.menu_fade = 0.0
        self.menu_root.set_alpha_scale(0.0)
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
            self.menu_fade = min(1.0, self.menu_fade + dt * 2.4)
            self.menu_root.set_alpha_scale(self.menu_fade)
            for card in self.map_cards.values():
                card['mix'] += (card['target'] - card['mix']) * min(1.0, dt * 10.0)
                mix = card['mix']
                card['panel'].set_color(Vec4(0.018 + 0.007 * mix, 0.045 + 0.145 * mix, 0.075 + 0.175 * mix, 0.88 + 0.08 * mix))
                card['stripe'].set_color(Vec4(0.13 * (1.0 - mix), 0.25 * (1.0 - mix) + 0.88 * mix, 0.34 * (1.0 - mix) + mix, 0.9 + 0.1 * mix))
                card['border'].set_color(Vec4(0.16 * (1.0 - mix), 0.28 * (1.0 - mix) + 0.78 * mix, 0.36 * (1.0 - mix) + 0.94 * mix, 0.75 + 0.2 * mix))
            self.menu_cam_angle += dt * 10.0
            rad = math.radians(self.menu_cam_angle)
            cam_x = math.cos(rad) * 22.0
            cam_y = math.sin(rad) * 22.0
            if self.camera is not None:
                self.camera.set_pos(cam_x, cam_y, 6.0)
                self.camera.look_at(0, 0, 1.8)
            
            # Animate deploy button pulse glow
            if hasattr(self, 'deploy_panel'):
                pulse = (math.sin(current_time * 5.0) + 1.0) * 0.5
                self.deploy_panel.set_color(Vec4(0.012, 0.20 + pulse * 0.12, 0.27 + pulse * 0.16, 0.98))
                self.deploy_accent.set_color(Vec4(0.0, 0.62 + pulse * 0.36, 1.0, 1.0))

        elif self.game_state == 'PAUSED':
            self.map_manager.animate_environment(dt, current_time)
            self.pause_fade = min(1.0, self.pause_fade + dt * 3.0)
            self.pause_root.set_alpha_scale(self.pause_fade)

        elif self.game_state == 'GAME_OVER':
            self.game_over_fade = min(1.0, self.game_over_fade + dt * 2.4)
            self.game_over_root.set_alpha_scale(self.game_over_fade)

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
                self.game_over_fade = 0.0
                self.game_over_root.set_alpha_scale(0.0)
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
