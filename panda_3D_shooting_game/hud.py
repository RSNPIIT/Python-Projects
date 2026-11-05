"""
hud.py - Modern tactical FPS HUD:
Dynamic crosshairs, hitmarkers, health & shield gauges, weapon & ammo counters,
wave banner, damage flash vignettes, and high-precision sniper scope overlay.
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
        self.current_spread = 0.02
        
        # Hitmarker state
        self.hitmarker_root = self.root.attach_new_node("hitmarker_root")
        self.hitmarker_timer = 0.0
        self.is_kill_hit = False
        
        # Sniper Scope Overlay root (in render2d for exact screen coverage)
        self.scope_root = render2d.attach_new_node("sniper_scope_root")
        self.scope_root.hide()
        
        # Damage vignette flash
        self.damage_flash_root = render2d.attach_new_node("damage_flash_root")
        self.damage_flash_timer = 0.0
        
        # Text nodes
        self.ammo_text_node = None
        self.ammo_np = None
        self.health_text_node = None
        self.health_np = None
        self.wave_text_node = None
        self.wave_np = None
        self.prompt_np = None
        
        # Health & shield visual bar nodes
        self.hp_bar_fill = None
        self.shield_bar_fill = None
        
        self.build_hud_elements()
        self.build_sniper_scope()
        self.build_damage_flash()

    def build_hud_elements(self):
        # 1. Health & Shield Panel (Bottom-Left)
        # Background bar backing
        cm = CardMaker("hp_bg")
        cm.set_frame(-0.02, 0.52, -0.02, 0.09)
        bg = self.root.attach_new_node(cm.generate())
        bg.set_pos(-1.25, 0, -0.88)
        bg.set_color(Vec4(0.05, 0.08, 0.12, 0.8))
        bg.set_transparency(True)
        
        # Health bar (Red/Green)
        cm_hp = CardMaker("hp_bar")
        cm_hp.set_frame(0, 0.5, 0, 0.035)
        self.hp_bar_fill = self.root.attach_new_node(cm_hp.generate())
        self.hp_bar_fill.set_pos(-1.24, 0, -0.835)
        self.hp_bar_fill.set_color(Vec4(0.15, 0.9, 0.35, 1.0))
        
        # Shield bar (Cyan)
        cm_sh = CardMaker("shield_bar")
        cm_sh.set_frame(0, 0.5, 0, 0.02)
        self.shield_bar_fill = self.root.attach_new_node(cm_sh.generate())
        self.shield_bar_fill.set_pos(-1.24, 0, -0.865)
        self.shield_bar_fill.set_color(Vec4(0.1, 0.75, 1.0, 1.0))
        
        # Health & Shield Text readout
        self.health_text_node = TextNode("health_text")
        self.health_text_node.set_text("HP: 100  |  SHIELD: 50")
        self.health_text_node.set_text_color(1, 1, 1, 0.95)
        self.health_np = self.root.attach_new_node(self.health_text_node)
        self.health_np.set_pos(-1.24, 0, -0.78)
        self.health_np.set_scale(0.042)

        # 2. Ammo & Weapon Panel (Bottom-Right)
        self.ammo_text_node = TextNode("ammo_text")
        self.ammo_text_node.set_align(TextNode.A_right)
        self.ammo_text_node.set_text("30 / 150\nASSAULT RIFLE")
        self.ammo_text_node.set_text_color(0.2, 0.9, 1.0, 0.95)
        self.ammo_np = self.root.attach_new_node(self.ammo_text_node)
        self.ammo_np.set_pos(1.25, 0, -0.84)
        self.ammo_np.set_scale(0.052)

        # 3. Wave / Enemies Remaining Banner (Top-Center)
        self.wave_text_node = TextNode("wave_text")
        self.wave_text_node.set_align(TextNode.A_center)
        self.wave_text_node.set_text("WAVE 1  |  ENEMIES: 6  |  SCORE: 0")
        self.wave_text_node.set_text_color(1.0, 0.85, 0.2, 0.95)
        self.wave_np = self.root.attach_new_node(self.wave_text_node)
        self.wave_np.set_pos(0, 0, 0.88)
        self.wave_np.set_scale(0.048)

        # 4. Controls / Inspect prompt (Bottom-Center subtle hint)
        prompt_node = TextNode("prompt_text")
        prompt_node.set_align(TextNode.A_center)
        prompt_node.set_text("[1-4] Weapons  |  [F] Inspect Gun  |  [R] Reload  |  [M] Radar  |  [Shift] Sprint")
        prompt_node.set_text_color(0.7, 0.75, 0.8, 0.6)
        self.prompt_np = self.root.attach_new_node(prompt_node)
        self.prompt_np.set_pos(0, 0, -0.94)
        self.prompt_np.set_scale(0.032)

    def build_sniper_scope(self):
        """Constructs full-screen sniper scope reticle and dark vignette edges."""
        # Top, bottom, left, right black masks
        cm = CardMaker("scope_mask")
        cm.set_frame(-1.0, 1.0, -1.0, 1.0)
        
        # Center circle reticle with crosshairs
        lines = LineSegs()
        lines.set_color(Vec4(0.05, 0.05, 0.05, 0.95))
        lines.set_thickness(2.0)
        
        # Outer scope circle
        segments = 64
        r = 0.72
        for i in range(segments + 1):
            ang = (i / segments) * 2 * math.pi
            x = math.cos(ang) * r
            y = math.sin(ang) * r
            if i == 0:
                lines.move_to(x, y, 0)
            else:
                lines.draw_to(x, y, 0)
                
        # Precision Mil-Dot crosshair lines
        lines.set_color(Vec4(0.1, 0.1, 0.1, 0.9))
        lines.set_thickness(1.5)
        lines.move_to(-r, 0, 0); lines.draw_to(r, 0, 0)
        lines.move_to(0, -r, 0); lines.draw_to(0, r, 0)
        
        # Mil-dot graduation ticks
        for d in [-0.4, -0.2, 0.2, 0.4]:
            lines.move_to(d, -0.02, 0); lines.draw_to(d, 0.02, 0)
            lines.move_to(-0.02, d, 0); lines.draw_to(0.02, d, 0)
            
        # Center precision red dot
        lines.set_color(Vec4(1.0, 0.1, 0.1, 1.0))
        lines.set_thickness(4.0)
        lines.move_to(-0.005, 0, 0); lines.draw_to(0.005, 0, 0)
        
        scope_geom = lines.create()
        self.scope_root.attach_new_node(scope_geom)
        
        # Scope info text
        zoom_text = TextNode("zoom_info")
        zoom_text.set_text("10x OPTICAL ZOOM\nRANGEFINDER ACTIVE")
        zoom_text.set_text_color(0.2, 0.8, 1.0, 0.8)
        z_np = self.scope_root.attach_new_node(zoom_text)
        z_np.set_pos(-0.55, 0, -0.5)
        z_np.set_scale(0.035)

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
            
        gap = max(0.008, spread_factor * 0.4)
        length = 0.018
        
        lines = LineSegs()
        lines.set_thickness(2.0)
        
        # Bright tactical cyan/white crosshairs
        c = Vec4(0.2, 1.0, 0.7, 0.85) if not is_ads else Vec4(0.1, 1.0, 0.3, 0.95)
        lines.set_color(c)
        
        # Top
        lines.move_to(0, 0, gap); lines.draw_to(0, 0, gap + length)
        # Bottom
        lines.move_to(0, 0, -gap); lines.draw_to(0, 0, -gap - length)
        # Left
        lines.move_to(-gap, 0, 0); lines.draw_to(-gap - length, 0, 0)
        # Right
        lines.move_to(gap, 0, 0); lines.draw_to(gap + length, 0, 0)
        
        # Center dot if ADS
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
            lines.set_thickness(2.5)
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
        # Update hitmarker & damage flash
        self.update_hitmarker(dt)
        
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            alpha = (self.damage_flash_timer / 0.35) * 0.4
            self.flash_np.set_color(Vec4(0.9, 0.0, 0.0, alpha))
        else:
            self.flash_np.set_color(Vec4(0.9, 0.0, 0.0, 0.0))
            
        # Update HP & Shield bar scale
        hp_ratio = max(0.0, min(1.0, player.health / player.max_health))
        sh_ratio = max(0.0, min(1.0, player.shield / player.max_shield))
        self.hp_bar_fill.set_scale(hp_ratio, 1.0, 1.0)
        self.shield_bar_fill.set_scale(sh_ratio, 1.0, 1.0)
        self.health_text_node.set_text(f"HP: {int(player.health)}/{int(player.max_health)}   |   SHIELD: {int(player.shield)}/{int(player.max_shield)}")
        
        # Update Ammo & Weapon
        inspect_status = " [INSPECTING]" if current_weapon.is_inspecting else ""
        reload_status = " [RELOADING...]" if current_weapon.is_reloading else ""
        self.ammo_text_node.set_text(
            f"{current_weapon.current_ammo} / {current_weapon.reserve_ammo}\n"
            f"{current_weapon.name.upper()}{inspect_status}{reload_status}"
        )
        
        # Update Wave & Enemies Banner
        alive_enemies = enemy_manager.get_alive_count()
        score = enemy_manager.enemies_killed * 100
        self.wave_text_node.set_text(
            f"WAVE {enemy_manager.wave_number}  |  ENEMIES LEFT: {alive_enemies}  |  SCORE: {score}"
        )
        
        # Update Crosshair
        is_scoped = current_weapon.has_scope and current_weapon.ads_progress > 0.85
        spread = current_weapon.spread
        if player.is_sprinting:
            spread *= 2.0
        elif player.is_moving:
            spread *= 1.3
        self.update_crosshair(spread, current_weapon.ads_progress > 0.5, is_scoped)

    def cleanup(self):
        self.root.remove_node()
        self.scope_root.remove_node()
        self.damage_flash_root.remove_node()
