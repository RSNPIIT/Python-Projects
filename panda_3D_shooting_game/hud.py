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
        self.crosshair_key = None
        
        # Hitmarker state
        self.hitmarker_root = self.root.attach_new_node("hitmarker_root")
        self.hitmarker_timer = 0.0
        self.is_kill_hit = False
        self.hitmarker_path = None
        self.display_health_ratio = 1.0
        self.display_shield_ratio = 1.0
        self.weapon_slot_mix = [1.0, 0.0, 0.0, 0.0]
        
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
        bg.set_color(Vec4(0.008, 0.022, 0.038, 0.76))
        bg.set_transparency(True)
        
        # Glowing border line
        lines = LineSegs()
        lines.set_color(Vec4(0.05, 0.58, 0.72, 0.72))
        lines.set_thickness(1.2)
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
        self.health_text_node.set_text("HEALTH  100  /  SHIELD  50")
        self.health_text_node.set_text_color(0.81, 0.91, 0.94, 0.98)
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
        wbg.set_color(Vec4(0.008, 0.022, 0.038, 0.76))
        wbg.set_transparency(True)
        
        # Border
        w_lines = LineSegs()
        w_lines.set_color(Vec4(0.05, 0.58, 0.72, 0.72))
        w_lines.set_thickness(1.2)
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
        self.wave_text_node.set_text("WAVE 01  /  HOSTILES 06  /  SCORE 00000")
        self.wave_text_node.set_text_color(0.78, 0.91, 0.94, 1.0)
        self.wave_np = self.root.attach_new_node(self.wave_text_node)
        self.wave_np.set_pos(0, 0, 0.91)
        self.wave_np.set_scale(0.032)
        wave_cm = CardMaker("wave_panel")
        wave_cm.set_frame(-0.72, 0.72, -0.055, 0.055)
        wave_bg = self.root.attach_new_node(wave_cm.generate())
        wave_bg.set_pos(0, 0.01, 0.91)
        wave_bg.set_color(Vec4(0.008, 0.022, 0.038, 0.68))
        wave_bg.set_transparency(True)
        wave_bg.set_depth_test(False)
        wave_bg.set_depth_write(False)
        wave_bg.set_bin("fixed", 0)

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
        if self.hitmarker_path:
            self.hitmarker_path.remove_node()

        lines = LineSegs()
        lines.set_thickness(2.8)
        lines.set_color(Vec4(1.0, 0.1, 0.1, 1.0) if is_kill else Vec4(1.0, 1.0, 1.0, 1.0))
        d1, d2 = 0.012, 0.026
        lines.move_to(d1, 0, d1); lines.draw_to(d2, 0, d2)
        lines.move_to(-d1, 0, d1); lines.draw_to(-d2, 0, d2)
        lines.move_to(d1, 0, -d1); lines.draw_to(d2, 0, -d2)
        lines.move_to(-d1, 0, -d1); lines.draw_to(-d2, 0, -d2)
        self.hitmarker_path = self.hitmarker_root.attach_new_node(lines.create())
        self.hitmarker_path.set_transparency(True)
        self.hitmarker_path.set_scale(1.35)

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
            
        key = (round(spread_factor, 4), bool(is_ads))
        if key == self.crosshair_key:
            return
        self.crosshair_key = key

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
        if not self.hitmarker_path:
            return
        self.hitmarker_timer = max(0.0, self.hitmarker_timer - dt)
        alpha = self.hitmarker_timer / 0.14
        self.hitmarker_path.set_color_scale(1.0, 1.0, 1.0, alpha)
        self.hitmarker_path.set_scale(1.0 + alpha * 0.35)
        if self.hitmarker_timer <= 0.0:
            self.hitmarker_path.remove_node()
            self.hitmarker_path = None

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
        bar_ease = min(1.0, dt * 9.0)
        self.display_health_ratio += (hp_ratio - self.display_health_ratio) * bar_ease
        self.display_shield_ratio += (sh_ratio - self.display_shield_ratio) * bar_ease
        self.hp_bar_fill.set_scale(self.display_health_ratio, 1.0, 1.0)
        self.shield_bar_fill.set_scale(self.display_shield_ratio, 1.0, 1.0)
        self.health_text_node.set_text(f"HEALTH  {int(player.health):03d}  /  SHIELD  {int(player.shield):02d}")
        
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
        ammo_ratio = current_weapon.current_ammo / max(1, current_weapon.mag_size)
        if ammo_ratio <= 0.15:
            self.ammo_text_node.set_text_color(1.0, 0.3, 0.24, 1.0)
        elif ammo_ratio <= 0.35:
            self.ammo_text_node.set_text_color(1.0, 0.7, 0.28, 1.0)
        else:
            self.ammo_text_node.set_text_color(0.14, 0.88, 0.98, 1.0)
        for index, slot in enumerate(self.weapon_slot_nodes):
            target = 1.0 if index == player.current_weapon_idx else 0.0
            self.weapon_slot_mix[index] += (target - self.weapon_slot_mix[index]) * min(1.0, dt * 12.0)
            mix = self.weapon_slot_mix[index]
            slot.set_text_color(0.58 * (1.0 - mix) + 0.15 * mix, 0.68 * (1.0 - mix) + 0.92 * mix, 0.74 * (1.0 - mix) + mix, 0.82 * (1.0 - mix) + 0.18 * mix)
        
        # Wave banner
        alive = enemy_manager.get_alive_count()
        score = enemy_manager.enemies_killed * 100
        self.wave_text_node.set_text(
            f"WAVE {enemy_manager.wave_number:02d}  /  HOSTILES {alive:02d}  /  SCORE {score:05d}"
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
