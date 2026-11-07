"""
hud.py - Modern Tactical AAA Sci-Fi FPS HUD:
Glassmorphism cyber panels, segmented health/shield gauges,
dynamic precision crosshairs, tactical ammo cards, deploy shield alerts,
and high-tech rangefinder sniper scope overlay.
"""

import math
from panda3d.core import (
    NodePath, Vec3, Vec4, LineSegs, CardMaker, TextNode
)

class HUD:
    def __init__(self, aspect2d, render2d):
        self.aspect2d = aspect2d
        self.render2d = render2d
        
        self.root = aspect2d.attach_new_node("hud_root")
        
        # Crosshair state
        self.crosshair_root = self.root.attach_new_node("crosshair_root")
        self.crosshair_lines = None
        
        # Hitmarker state
        self.hitmarker_root = self.root.attach_new_node("hitmarker_root")
        self.hitmarker_timer = 0.0
        self.is_kill_hit = False
        
        # Sniper Scope Overlay root
        self.scope_root = render2d.attach_new_node("sniper_scope_root")
        self.scope_root.hide()
        
        # Damage vignette flash
        self.damage_flash_root = render2d.attach_new_node("damage_flash_root")
        self.damage_flash_timer = 0.0
        
        # Nodes
        self.ammo_text_node = None
        self.ammo_np = None
        self.weapon_name_node = None
        self.weapon_name_np = None
        self.firemode_node = None
        self.firemode_np = None
        
        self.health_text_node = None
        self.health_np = None
        self.wave_text_node = None
        self.wave_np = None
        self.weapon_slot_nodes = []
        self.shield_alert_node = None
        self.shield_alert_np = None
        
        self.hp_bar_fill = None
        self.shield_bar_fill = None
        
        self.build_hud_elements()
        self.build_sniper_scope()
        self.build_damage_flash()

    def build_hud_elements(self):
        # ==============================================================================
        # 1. HEALTH & ARMOR SHIELD PANEL (Bottom-Left)
        # ==============================================================================
        # Angled glassmorphic frame backing
        cm_bg = CardMaker("hp_panel_bg")
        cm_bg.set_frame(-0.02, 0.54, -0.02, 0.14)
        bg = self.root.attach_new_node(cm_bg.generate())
        bg.set_pos(-1.26, 0, -0.92)
        bg.set_color(Vec4(0.04, 0.07, 0.10, 0.82))
        bg.set_transparency(True)
        
        # Glowing border line
        lines = LineSegs()
        lines.set_color(Vec4(0.1, 0.8, 1.0, 0.8))
        lines.set_thickness(2.0)
        lines.move_to(-1.26, 0, -0.78)
        lines.draw_to(-0.72, 0, -0.78)
        lines.draw_to(-0.70, 0, -0.92)
        lines.draw_to(-1.26, 0, -0.92)
        lines.draw_to(-1.26, 0, -0.78)
        self.root.attach_new_node(lines.create())
        
        # Shield bar (Cyan neon)
        cm_sh = CardMaker("shield_fill")
        cm_sh.set_frame(0, 0.48, 0, 0.022)
        self.shield_bar_fill = self.root.attach_new_node(cm_sh.generate())
        self.shield_bar_fill.set_pos(-1.23, 0, -0.835)
        self.shield_bar_fill.set_color(Vec4(0.0, 0.85, 1.0, 1.0))
        
        # Health bar (Emerald green)
        cm_hp = CardMaker("hp_fill")
        cm_hp.set_frame(0, 0.48, 0, 0.032)
        self.hp_bar_fill = self.root.attach_new_node(cm_hp.generate())
        self.hp_bar_fill.set_pos(-1.23, 0, -0.875)
        self.hp_bar_fill.set_color(Vec4(0.15, 0.95, 0.4, 1.0))
        
        # Digital readout
        self.health_text_node = TextNode("health_readout")
        self.health_text_node.set_text("VITALS: 100%  |  ARMOR: 100%")
        self.health_text_node.set_text_color(0.9, 0.95, 1.0, 0.95)
        self.health_np = self.root.attach_new_node(self.health_text_node)
        self.health_np.set_pos(-1.23, 0, -0.805)
        self.health_np.set_scale(0.038)

        # ==============================================================================
        # 2. WEAPON & AMMO STATUS CARD (Bottom-Right)
        # ==============================================================================
        cm_wbg = CardMaker("ammo_panel_bg")
        cm_wbg.set_frame(-0.52, 0.02, -0.02, 0.14)
        wbg = self.root.attach_new_node(cm_wbg.generate())
        wbg.set_pos(1.26, 0, -0.92)
        wbg.set_color(Vec4(0.04, 0.07, 0.10, 0.82))
        wbg.set_transparency(True)
        
        # Border
        w_lines = LineSegs()
        w_lines.set_color(Vec4(0.0, 0.85, 1.0, 0.8))
        w_lines.set_thickness(2.0)
        w_lines.move_to(0.74, 0, -0.92)
        w_lines.draw_to(0.76, 0, -0.78)
        w_lines.draw_to(1.26, 0, -0.78)
        w_lines.draw_to(1.26, 0, -0.92)
        w_lines.draw_to(0.74, 0, -0.92)
        self.root.attach_new_node(w_lines.create())
        
        # Weapon Name & Firemode
        self.weapon_name_node = TextNode("wpn_name")
        self.weapon_name_node.set_align(TextNode.A_right)
        self.weapon_name_node.set_text("M4A1 TACTICAL")
        self.weapon_name_node.set_text_color(0.95, 0.95, 1.0, 1.0)
        self.weapon_name_np = self.root.attach_new_node(self.weapon_name_node)
        self.weapon_name_np.set_pos(1.23, 0, -0.81)
        self.weapon_name_np.set_scale(0.038)
        
        # Large Numeric Ammo
        self.ammo_text_node = TextNode("ammo_digits")
        self.ammo_text_node.set_align(TextNode.A_right)
        self.ammo_text_node.set_text("30 / 150")
        self.ammo_text_node.set_text_color(0.1, 0.9, 1.0, 1.0)
        self.ammo_np = self.root.attach_new_node(self.ammo_text_node)
        self.ammo_np.set_pos(1.23, 0, -0.875)
        self.ammo_np.set_scale(0.058)

        # ==============================================================================
        # 3. TACTICAL COMBAT BANNER (Top-Center)
        # ==============================================================================
        self.wave_text_node = TextNode("wave_banner")
        self.wave_text_node.set_align(TextNode.A_center)
        self.wave_text_node.set_text("// COMBAT ZONE: ACTIVE  |  WAVE 1  |  HOSTILES: 6 //")
        self.wave_text_node.set_text_color(1.0, 0.85, 0.15, 0.95)
        self.wave_np = self.root.attach_new_node(self.wave_text_node)
        self.wave_np.set_pos(0, 0, 0.90)
        self.wave_np.set_scale(0.044)

        # Persistent weapon selector makes the 1-4 / scroll-wheel controls visible.
        slot_names = ("RIFLE", "SHOTGUN", "SNIPER", "PISTOL")
        for index, short_name in enumerate(slot_names):
            slot = TextNode(f"weapon_slot_{index + 1}")
            slot.set_align(TextNode.A_center)
            slot.set_text(f"[{index + 1}] {short_name}")
            slot_np = self.root.attach_new_node(slot)
            slot_np.set_pos((-0.54 + index * 0.36), 0, -0.72)
            slot_np.set_scale(0.025)
            self.weapon_slot_nodes.append(slot)

        # Deploy Shield Alert
        self.shield_alert_node = TextNode("shield_alert")
        self.shield_alert_node.set_align(TextNode.A_center)
        self.shield_alert_node.set_text("[ TACTICAL DEPLOY SHIELD ACTIVE: 3.5s ]")
        self.shield_alert_node.set_text_color(0.1, 0.9, 1.0, 1.0)
        self.shield_alert_np = self.root.attach_new_node(self.shield_alert_node)
        self.shield_alert_np.set_pos(0, 0, 0.76)
        self.shield_alert_np.set_scale(0.046)

    def build_sniper_scope(self):
        """Constructs modern high-tech digital sniper optic overlay."""
        # Dark vignette masks covering 4 corners
        cm = CardMaker("scope_mask")
        cm.set_frame(-1.0, 1.0, -1.0, 1.0)
        mask = self.scope_root.attach_new_node(cm.generate())
        mask.set_color(Vec4(0.02, 0.03, 0.04, 0.75))
        mask.set_transparency(True)
        
        # High precision mil-dot crosshairs
        lines = LineSegs()
        lines.set_color(Vec4(0.05, 0.95, 0.45, 0.9)) # High-tech night green
        lines.set_thickness(1.8)
        
        # Center scope ring
        segments = 64
        r = 0.70
        for i in range(segments + 1):
            ang = (i / segments) * 2 * math.pi
            x = math.cos(ang) * r
            y = math.sin(ang) * r
            if i == 0: lines.move_to(x, y, 0)
            else: lines.draw_to(x, y, 0)
            
        # Crosshair lines
        lines.move_to(-r, 0, 0); lines.draw_to(r, 0, 0)
        lines.move_to(0, -r, 0); lines.draw_to(0, r, 0)
        
        # Mil-dot graduation markers
        for d in [-0.5, -0.35, -0.2, 0.2, 0.35, 0.5]:
            lines.move_to(d, -0.015, 0); lines.draw_to(d, 0.015, 0)
            lines.move_to(-0.015, d, 0); lines.draw_to(0.015, d, 0)
            
        # Center precision dot
        lines.set_color(Vec4(1.0, 0.1, 0.1, 1.0))
        lines.set_thickness(4.0)
        lines.move_to(-0.003, 0, 0); lines.draw_to(0.003, 0, 0)
        
        self.scope_root.attach_new_node(lines.create())
        
        # Rangefinder Telemetry readout
        tele_text = TextNode("scope_telemetry")
        tele_text.set_text("OPTICAL ZOOM: 12X\nRANGE: 48.5m  |  ELEV: +0.2°\nTARGET TRACK: LOCKED")
        tele_text.set_text_color(0.1, 0.95, 0.45, 0.9)
        t_np = self.scope_root.attach_new_node(tele_text)
        t_np.set_pos(-0.55, 0, -0.48)
        t_np.set_scale(0.036)

    def build_damage_flash(self):
        cm = CardMaker("dmg_flash")
        cm.set_frame(-1.0, 1.0, -1.0, 1.0)
        self.flash_np = self.damage_flash_root.attach_new_node(cm.generate())
        self.flash_np.set_color(Vec4(0.9, 0.0, 0.0, 0.0))
        self.flash_np.set_transparency(True)

    def trigger_hitmarker(self, is_kill=False):
        self.hitmarker_timer = 0.14
        self.is_kill_hit = is_kill

    def trigger_damage_flash(self):
        self.damage_flash_timer = 0.35

    def update_crosshair(self, spread_factor, is_ads, is_sniper_scoped):
        if is_sniper_scoped:
            self.crosshair_root.hide()
            self.scope_root.show()
            return
        else:
            self.scope_root.hide()
            self.crosshair_root.show()
            
        if self.crosshair_lines:
            self.crosshair_lines.remove_node()
            
        gap = max(0.009, spread_factor * 0.35)
        length = 0.016
        
        lines = LineSegs()
        lines.set_thickness(2.2)
        c = Vec4(0.1, 0.9, 1.0, 0.85) if not is_ads else Vec4(0.1, 1.0, 0.35, 0.95)
        lines.set_color(c)
        
        lines.move_to(0, 0, gap); lines.draw_to(0, 0, gap + length)
        lines.move_to(0, 0, -gap); lines.draw_to(0, 0, -gap - length)
        lines.move_to(-gap, 0, 0); lines.draw_to(-gap - length, 0, 0)
        lines.move_to(gap, 0, 0); lines.draw_to(gap + length, 0, 0)
        
        if is_ads:
            lines.set_thickness(3.5)
            lines.move_to(-0.002, 0, 0); lines.draw_to(0.002, 0, 0)
            
        self.crosshair_lines = self.crosshair_root.attach_new_node(lines.create())

    def update_hitmarker(self, dt):
        for child in self.hitmarker_root.get_children():
            child.remove_node()
            
        if self.hitmarker_timer > 0:
            self.hitmarker_timer -= dt
            lines = LineSegs()
            lines.set_thickness(2.8)
            c = Vec4(1.0, 0.1, 0.1, 1.0) if self.is_kill_hit else Vec4(1.0, 1.0, 1.0, 1.0)
            lines.set_color(c)
            
            d1 = 0.012
            d2 = 0.026
            lines.move_to(d1, 0, d1); lines.draw_to(d2, 0, d2)
            lines.move_to(-d1, 0, d1); lines.draw_to(-d2, 0, d2)
            lines.move_to(d1, 0, -d1); lines.draw_to(d2, 0, -d2)
            lines.move_to(-d1, 0, -d1); lines.draw_to(-d2, 0, -d2)
            
            self.hitmarker_root.attach_new_node(lines.create())

    def update(self, dt, player, enemy_manager, current_weapon):
        self.update_hitmarker(dt)
        
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            alpha = (self.damage_flash_timer / 0.35) * 0.45
            self.flash_np.set_color(Vec4(0.9, 0.0, 0.0, alpha))
        else:
            self.flash_np.set_color(Vec4(0.9, 0.0, 0.0, 0.0))
            
        # Vitals & Shield Gauges
        hp_ratio = max(0.0, min(1.0, player.health / player.max_health))
        sh_ratio = max(0.0, min(1.0, player.shield / player.max_shield))
        self.hp_bar_fill.set_scale(hp_ratio, 1.0, 1.0)
        self.shield_bar_fill.set_scale(sh_ratio, 1.0, 1.0)
        self.health_text_node.set_text(f"VITALS: {int(player.health)}%  |  ARMOR: {int(player.shield)}%")
        
        # Deploy shield alert banner
        if player.has_spawn_shield():
            self.shield_alert_np.show()
            self.shield_alert_node.set_text(f"[ // TACTICAL DEPLOY SHIELD ACTIVE: {player.spawn_shield_timer:.1f}s // ]")
        else:
            self.shield_alert_np.hide()
            
        # Weapon details
        inspect_badge = " [INSPECTING]" if current_weapon.is_inspecting else ""
        reload_badge = " [RELOADING...]" if current_weapon.is_reloading else ""
        self.weapon_name_node.set_text(f"{current_weapon.name.upper()}{inspect_badge}{reload_badge}")
        self.ammo_text_node.set_text(f"{current_weapon.current_ammo} / {current_weapon.reserve_ammo}")
        for index, slot in enumerate(self.weapon_slot_nodes):
            if index == player.current_weapon_idx:
                slot.set_text_color(0.15, 0.92, 1.0, 1.0)
            else:
                slot.set_text_color(0.58, 0.68, 0.74, 0.82)
        
        # Wave banner
        alive = enemy_manager.get_alive_count()
        score = enemy_manager.enemies_killed * 100
        self.wave_text_node.set_text(
            f"// WAVE {enemy_manager.wave_number}  |  HOSTILES LEFT: {alive}  |  SCORE: {score} //"
        )
        
        # Crosshair
        is_scoped = current_weapon.has_scope and current_weapon.ads_progress > 0.85
        spread = current_weapon.spread
        if player.is_sprinting: spread *= 1.8
        elif player.is_moving: spread *= 1.25
        self.update_crosshair(spread, current_weapon.ads_progress > 0.5, is_scoped)

    def cleanup(self):
        self.root.remove_node()
        self.scope_root.remove_node()
        self.damage_flash_root.remove_node()
