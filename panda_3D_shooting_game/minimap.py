"""
minimap.py - Real-time tactical 2D HUD radar / minimap with rotating sweep beam.
Displays cardinal headings, rotating sweep line, player orientation,
enemy hostiles, explosive barrels, and tactical supply drops.
"""

import math
from panda3d.core import (
    NodePath, Vec3, Vec4, LineSegs, CardMaker, TextNode
)

class Minimap:
    def __init__(self, aspect2d, player, map_manager, enemy_manager):
        self.aspect2d = aspect2d
        self.player = player
        self.map_manager = map_manager
        self.enemy_manager = enemy_manager
        
        self.is_expanded = False
        self.radar_radius = 50.0
        self.sweep_angle = 0.0
        
        self.root = aspect2d.attach_new_node("minimap_root")
        self.compact_pos = Vec3(1.06, 0, 0.68)
        self.compact_scale = 0.25
        
        self.expanded_pos = Vec3(0, 0, 0)
        self.expanded_scale = 0.72
        
        self.root.set_pos(self.compact_pos)
        self.root.set_scale(self.compact_scale)
        
        self.blip_root = self.root.attach_new_node("blip_root")
        self.player_arrow = None
        self.sweep_line = None
        
        self.build_radar_frame()
        self.build_player_indicator()

    def build_radar_frame(self):
        cm = CardMaker("radar_bg")
        cm.set_frame(-1.0, 1.0, -1.0, 1.0)
        bg = self.root.attach_new_node(cm.generate())
        bg.set_color(Vec4(0.03, 0.06, 0.09, 0.85))
        bg.set_transparency(True)
        bg.set_bin("fixed", 10)
        
        lines = LineSegs()
        lines.set_color(Vec4(0.0, 0.85, 1.0, 0.6))
        lines.set_thickness(1.8)
        
        segments = 40
        # Outer Ring
        for i in range(segments + 1):
            ang = (i / segments) * 2 * math.pi
            x = math.cos(ang)
            y = math.sin(ang)
            if i == 0: lines.move_to(x, y, 0)
            else: lines.draw_to(x, y, 0)
            
        # Inner Range Rings (33% and 66%)
        lines.set_color(Vec4(0.0, 0.7, 0.9, 0.35))
        for r in [0.35, 0.70]:
            for i in range(segments + 1):
                ang = (i / segments) * 2 * math.pi
                x = r * math.cos(ang)
                y = r * math.sin(ang)
                if i == 0: lines.move_to(x, y, 0)
                else: lines.draw_to(x, y, 0)
                
        # Axis lines
        lines.move_to(-0.95, 0, 0); lines.draw_to(0.95, 0, 0)
        lines.move_to(0, -0.95, 0); lines.draw_to(0, 0.95, 0)
        
        frame = self.root.attach_new_node(lines.create())
        frame.set_bin("fixed", 11)
        
        # North indicator
        n_text = TextNode("north_tag")
        n_text.set_text("N")
        n_text.set_align(TextNode.A_center)
        n_text.set_text_color(0.1, 0.9, 1.0, 0.9)
        np_n = self.root.attach_new_node(n_text)
        np_n.set_pos(0, 0, 0.82)
        np_n.set_scale(0.11)
        np_n.set_bin("fixed", 12)

    def build_player_indicator(self):
        lines = LineSegs()
        lines.set_color(Vec4(0.0, 1.0, 0.5, 1.0))
        lines.set_thickness(2.8)
        lines.move_to(0, 0.12, 0)
        lines.draw_to(-0.06, -0.08, 0)
        lines.draw_to(0, -0.03, 0)
        lines.draw_to(0.06, -0.08, 0)
        lines.draw_to(0, 0.12, 0)
        
        self.player_arrow = self.root.attach_new_node(lines.create())
        self.player_arrow.set_bin("fixed", 16)

    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.root.set_pos(self.expanded_pos)
            self.root.set_scale(self.expanded_scale)
            self.radar_radius = 90.0
        else:
            self.root.set_pos(self.compact_pos)
            self.root.set_scale(self.compact_scale)
            self.radar_radius = 50.0

    def update(self):
        for child in self.blip_root.get_children():
            child.remove_node()
            
        p_pos = self.player.get_pos()
        p_yaw = self.player.get_yaw()
        self.player_arrow.set_r(-p_yaw)
        
        # Rotating Radar Sweep Beam Line
        self.sweep_angle = (self.sweep_angle + 120.0 * 0.016) % 360.0
        rad = math.radians(self.sweep_angle)
        sweep_lines = LineSegs()
        sweep_lines.set_color(Vec4(0.0, 0.9, 1.0, 0.45))
        sweep_lines.set_thickness(1.5)
        sweep_lines.move_to(0, 0, 0)
        sweep_lines.draw_to(math.cos(rad) * 0.95, math.sin(rad) * 0.95, 0)
        self.blip_root.attach_new_node(sweep_lines.create()).set_bin("fixed", 13)
        
        lines = LineSegs()
        lines.set_thickness(4.0)
        
        # Barrels (Orange blips)
        for barrel in self.map_manager.barrels:
            if not barrel.is_destroyed:
                b_pos = barrel.get_pos()
                dx = (b_pos.x - p_pos.x) / self.radar_radius
                dy = (b_pos.y - p_pos.y) / self.radar_radius
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= 0.95:
                    lines.set_color(Vec4(1.0, 0.65, 0.0, 0.9))
                    lines.move_to(dx - 0.02, dy, 0); lines.draw_to(dx + 0.02, dy, 0)
                    lines.move_to(dx, dy - 0.02, 0); lines.draw_to(dx, dy + 0.02, 0)
                    
        # Pickups (Green/Cyan blips)
        for pickup in self.map_manager.pickups:
            if pickup.is_active:
                pk_pos = pickup.get_pos()
                dx = (pk_pos.x - p_pos.x) / self.radar_radius
                dy = (pk_pos.y - p_pos.y) / self.radar_radius
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= 0.95:
                    c = Vec4(0.2, 1.0, 0.4, 0.95) if pickup.kind == 'health' else Vec4(0.0, 0.85, 1.0, 0.95)
                    lines.set_color(c)
                    lines.move_to(dx - 0.025, dy, 0); lines.draw_to(dx + 0.025, dy, 0)
                    lines.move_to(dx, dy - 0.025, 0); lines.draw_to(dx, dy + 0.025, 0)
                    
        # Enemies (Glowing Red blips)
        for enemy in self.enemy_manager.enemies:
            if enemy.is_alive:
                e_pos = enemy.get_pos()
                dx = (e_pos.x - p_pos.x) / self.radar_radius
                dy = (e_pos.y - p_pos.y) / self.radar_radius
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= 0.95:
                    lines.set_color(Vec4(1.0, 0.15, 0.15, 1.0))
                    lines.move_to(dx, dy + 0.035, 0)
                    lines.draw_to(dx + 0.035, dy, 0)
                    lines.draw_to(dx, dy - 0.035, 0)
                    lines.draw_to(dx - 0.035, dy, 0)
                    lines.draw_to(dx, dy + 0.035, 0)

        # Platforms (Cyan blip)
        for plat in self.map_manager.moving_platforms:
            pl_pos = plat.get_pos()
            dx = (pl_pos.x - p_pos.x) / self.radar_radius
            dy = (pl_pos.y - p_pos.y) / self.radar_radius
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= 0.95:
                lines.set_color(Vec4(0.0, 0.9, 1.0, 0.85))
                lines.move_to(dx - 0.03, dy - 0.03, 0); lines.draw_to(dx + 0.03, dy - 0.03, 0)
                lines.draw_to(dx + 0.03, dy + 0.03, 0); lines.draw_to(dx - 0.03, dy + 0.03, 0)
                lines.draw_to(dx - 0.03, dy - 0.03, 0)
                
        self.blip_root.attach_new_node(lines.create()).set_bin("fixed", 15)

    def cleanup(self):
        self.root.remove_node()
