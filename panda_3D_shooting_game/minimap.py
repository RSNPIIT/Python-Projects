"""
minimap.py - Real-time tactical 2D HUD radar / minimap.
Displays player position, heading arrow, enemy blips, explosive barrels,
and ammo/health pickups. Supports compact corner mode and expanded tactical map (M key).
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
        
        # State
        self.is_expanded = False
        self.radar_radius = 50.0  # World units visible in radar
        
        # Root node in aspect2d
        self.root = aspect2d.attach_new_node("minimap_root")
        
        # Compact mode: Top right corner
        self.compact_pos = Vec3(1.05, 0, 0.68)
        self.compact_scale = 0.26
        
        # Expanded mode: Center screen
        self.expanded_pos = Vec3(0, 0, 0)
        self.expanded_scale = 0.75
        
        self.root.set_pos(self.compact_pos)
        self.root.set_scale(self.compact_scale)
        
        # Blip nodes
        self.blip_root = self.root.attach_new_node("blip_root")
        self.player_arrow = None
        
        self.build_radar_frame()
        self.build_player_indicator()

    def build_radar_frame(self):
        # Dark circular background backing
        cm = CardMaker("radar_bg")
        cm.set_frame(-1.0, 1.0, -1.0, 1.0)
        bg = self.root.attach_new_node(cm.generate())
        bg.set_color(Vec4(0.04, 0.08, 0.12, 0.78))
        bg.set_transparency(True)
        bg.set_bin("fixed", 10)
        
        # Circular radar rings and compass crosshairs
        lines = LineSegs()
        lines.set_color(Vec4(0.1, 0.7, 0.9, 0.6))
        lines.set_thickness(1.5)
        
        # Outer ring
        segments = 36
        for i in range(segments + 1):
            ang = (i / segments) * 2 * math.pi
            x = math.cos(ang)
            y = math.sin(ang)
            if i == 0:
                lines.move_to(x, y, 0)
            else:
                lines.draw_to(x, y, 0)
                
        # Inner range rings (50% and 75%)
        for r in [0.5, 0.75]:
            for i in range(segments + 1):
                ang = (i / segments) * 2 * math.pi
                x = r * math.cos(ang)
                y = r * math.sin(ang)
                if i == 0:
                    lines.move_to(x, y, 0)
                else:
                    lines.draw_to(x, y, 0)
                    
        # Crosshair lines
        lines.move_to(-1.0, 0, 0); lines.draw_to(1.0, 0, 0)
        lines.move_to(0, -1.0, 0); lines.draw_to(0, 1.0, 0)
        
        frame = self.root.attach_new_node(lines.create())
        frame.set_bin("fixed", 11)

    def build_player_indicator(self):
        # Bright cyan/green tactical arrow at center of radar
        lines = LineSegs()
        lines.set_color(Vec4(0.0, 1.0, 0.6, 1.0))
        lines.set_thickness(2.5)
        # Arrow pointing up (+Y on 2D)
        lines.move_to(0, 0.12, 0)
        lines.draw_to(-0.06, -0.08, 0)
        lines.draw_to(0, -0.03, 0)
        lines.draw_to(0.06, -0.08, 0)
        lines.draw_to(0, 0.12, 0)
        
        self.player_arrow = self.root.attach_new_node(lines.create())
        self.player_arrow.set_bin("fixed", 15)

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
        # Clear old dynamic blips
        for child in self.blip_root.get_children():
            child.remove_node()
            
        p_pos = self.player.get_pos()
        p_yaw = self.player.get_yaw()
        
        # Player arrow points in direction of player's heading
        # In radar, forward is +Y, right is +X.
        # We rotate the arrow so North is up, or rotate radar with player.
        # Rotating player arrow relative to world:
        self.player_arrow.set_r(-p_yaw)
        
        lines = LineSegs()
        lines.set_thickness(4.0)
        
        # Draw dynamic barrels (Orange/Yellow blips)
        for barrel in self.map_manager.barrels:
            if not barrel.is_destroyed:
                b_pos = barrel.get_pos()
                dx = (b_pos.x - p_pos.x) / self.radar_radius
                dy = (b_pos.y - p_pos.y) / self.radar_radius
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= 0.95:
                    lines.set_color(Vec4(1.0, 0.65, 0.0, 0.9))
                    lines.move_to(dx - 0.02, dy, 0)
                    lines.draw_to(dx + 0.02, dy, 0)
                    lines.move_to(dx, dy - 0.02, 0)
                    lines.draw_to(dx, dy + 0.02, 0)
                    
        # Draw pickups (Green/Cyan blips)
        for pickup in self.map_manager.pickups:
            if pickup.is_active:
                pk_pos = pickup.get_pos()
                dx = (pk_pos.x - p_pos.x) / self.radar_radius
                dy = (pk_pos.y - p_pos.y) / self.radar_radius
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= 0.95:
                    c = Vec4(0.2, 1.0, 0.4, 0.9) if pickup.kind == 'health' else Vec4(0.2, 0.8, 1.0, 0.9)
                    lines.set_color(c)
                    lines.move_to(dx - 0.025, dy, 0)
                    lines.draw_to(dx + 0.025, dy, 0)
                    lines.move_to(dx, dy - 0.025, 0)
                    lines.draw_to(dx, dy + 0.025, 0)
                    
        # Draw enemies (Red blips)
        for enemy in self.enemy_manager.enemies:
            if enemy.is_alive:
                e_pos = enemy.get_pos()
                dx = (e_pos.x - p_pos.x) / self.radar_radius
                dy = (e_pos.y - p_pos.y) / self.radar_radius
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= 0.95:
                    lines.set_color(Vec4(1.0, 0.15, 0.15, 1.0))
                    # Draw a solid red square/diamond
                    lines.move_to(dx, dy + 0.035, 0)
                    lines.draw_to(dx + 0.035, dy, 0)
                    lines.draw_to(dx, dy - 0.035, 0)
                    lines.draw_to(dx - 0.035, dy, 0)
                    lines.draw_to(dx, dy + 0.035, 0)

        # Draw dynamic moving platforms (Cyan blip)
        for plat in self.map_manager.moving_platforms:
            pl_pos = plat.get_pos()
            dx = (pl_pos.x - p_pos.x) / self.radar_radius
            dy = (pl_pos.y - p_pos.y) / self.radar_radius
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= 0.95:
                lines.set_color(Vec4(0.0, 0.9, 1.0, 0.8))
                lines.move_to(dx - 0.03, dy - 0.03, 0)
                lines.draw_to(dx + 0.03, dy - 0.03, 0)
                lines.draw_to(dx + 0.03, dy + 0.03, 0)
                lines.draw_to(dx - 0.03, dy + 0.03, 0)
                lines.draw_to(dx - 0.03, dy - 0.03, 0)
                
        geom = lines.create()
        blip_node = self.blip_root.attach_new_node(geom)
        blip_node.set_bin("fixed", 14)

    def cleanup(self):
        self.root.remove_node()
