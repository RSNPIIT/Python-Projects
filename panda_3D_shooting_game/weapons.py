"""
weapons.py - Weapon classes, procedural 3D viewmodels, recoil mechanics,
aim-down-sights (ADS), and gun inspect animations.
"""

import math
import random
import os
from panda3d.core import (
    NodePath, Vec3, Vec4, PointLight, AudioSound, Texture, Filename
)
from mesh_builder import make_cube, make_cylinder

class Weapon:
    def __init__(self, name, app, camera):
        self.name = name
        self.app = app
        self.camera = camera
        
        # Load weapon texture
        tex_path = os.path.join(os.path.dirname(__file__), "textures", "gun_metal.png")
        self.gun_tex = None
        if os.path.exists(tex_path):
            self.gun_tex = Texture()
            self.gun_tex.read(Filename(tex_path))
        
        # Weapon stats
        self.damage = 25
        self.mag_size = 30
        self.current_ammo = 30
        self.reserve_ammo = 120
        self.fire_rate = 0.1  # seconds between shots
        self.last_fire_time = -1.0
        self.is_automatic = True
        self.pellets = 1
        self.spread = 0.02
        self.range = 200.0
        
        # Recoil configuration
        self.recoil_kick_z = 0.04
        self.recoil_kick_y = -0.06
        self.recoil_pitch = 2.5
        self.cam_recoil_pitch = 1.2
        self.cam_recoil_yaw = 0.4
        
        # ADS configuration
        self.ads_fov = 48.0
        self.hip_fov = 65.0
        self.is_aiming = False
        self.ads_progress = 0.0  # 0.0 = hip, 1.0 = ADS
        self.has_scope = False
        
        # Inspect configuration
        self.is_inspecting = False
        self.inspect_timer = 0.0
        self.inspect_duration = 1.6
        
        # Reload configuration
        self.is_reloading = False
        self.reload_timer = 0.0
        self.reload_duration = 1.8
        
        # Offsets relative to camera
        self.hip_pos = Vec3(0.24, 0.52, -0.22)
        self.hip_hpr = Vec3(0, 0, 0)
        self.ads_pos = Vec3(0.0, 0.45, -0.16)
        self.ads_hpr = Vec3(0, 0, 0)
        
        # Recoil spring state
        self.recoil_offset_pos = Vec3(0, 0, 0)
        self.recoil_offset_hpr = Vec3(0, 0, 0)
        
        # Viewmodel root
        self.root = NodePath(f'{name}_root')
        self.root.reparent_to(self.camera)
        self.root.set_pos(self.hip_pos)
        self.root.set_hpr(self.hip_hpr)
        
        # Muzzle flash
        self.muzzle_node = None
        self.muzzle_light = None
        self.muzzle_flash_timer = 0.0
        
        # Sounds
        self.shoot_sound = None
        self.reload_sound = None
        self.inspect_sound = None
        
        self.build_model()
        self.init_muzzle_flash()

    def build_model(self):
        """Override in subclasses to assemble 3D geometry."""
        pass

    def init_muzzle_flash(self):
        """Point light and flash billboard at muzzle."""
        if not self.muzzle_node:
            self.muzzle_node = self.root.attach_new_node("muzzle_pos")
            self.muzzle_node.set_pos(0, 0.6, 0.05)
            
        # Emissive quad for visual flash
        self.flash_mesh = make_cube(0.09, 0.09, 0.09, Vec4(1.0, 0.9, 0.3, 1.0))
        self.flash_mesh.reparent_to(self.muzzle_node)
        self.flash_mesh.hide()
        
        plight = PointLight(f'{self.name}_flash_light')
        plight.set_color(Vec4(1.0, 0.8, 0.2, 1.0))
        plight.set_attenuation(Vec3(0.4, 0.1, 0.05))
        self.muzzle_light = self.muzzle_node.attach_new_node(plight)

    def trigger_muzzle_flash(self):
        self.flash_mesh.show()
        # Randomize flash rotation
        self.flash_mesh.set_hpr(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))
        self.app.render.set_light(self.muzzle_light)
        self.muzzle_flash_timer = 0.06

    def start_inspect(self):
        """Initiates weapon inspect animation if not reloading or shooting."""
        if self.is_reloading or self.is_aiming:
            return
        self.is_inspecting = True
        self.inspect_timer = 0.0
        if self.inspect_sound:
            self.inspect_sound.play()

    def cancel_inspect(self):
        if self.is_inspecting:
            self.is_inspecting = False
            self.inspect_timer = 0.0

    def start_reload(self):
        if self.is_reloading or self.current_ammo >= self.mag_size or self.reserve_ammo <= 0:
            return False
        self.cancel_inspect()
        self.is_reloading = True
        self.reload_timer = 0.0
        if self.reload_sound:
            self.reload_sound.play()
        return True

    def finish_reload(self):
        needed = self.mag_size - self.current_ammo
        take = min(needed, self.reserve_ammo)
        self.current_ammo += take
        self.reserve_ammo -= take
        self.is_reloading = False
        self.reload_timer = 0.0

    def can_fire(self, current_time):
        if self.is_reloading:
            return False
        if current_time - self.last_fire_time < self.fire_rate:
            return False
        if self.current_ammo <= 0:
            return False
        return True

    def fire(self, current_time):
        if not self.can_fire(current_time):
            if self.current_ammo <= 0 and not self.is_reloading:
                self.start_reload()
            return None
            
        self.cancel_inspect()
        self.last_fire_time = current_time
        self.current_ammo -= 1
        
        # Audio
        if self.shoot_sound:
            self.shoot_sound.stop()
            self.shoot_sound.play()
            
        # Visual flash
        self.trigger_muzzle_flash()
        
        # Recoil impulse on viewmodel
        self.recoil_offset_pos.y += self.recoil_kick_y
        self.recoil_offset_pos.z += self.recoil_kick_z
        self.recoil_offset_hpr.y += self.recoil_pitch
        self.recoil_offset_hpr.x += random.uniform(-0.5, 0.5)
        
        # Camera recoil kick returned to player
        cam_kick_pitch = self.cam_recoil_pitch * random.uniform(0.8, 1.2)
        cam_kick_yaw = (random.random() * 2.0 - 1.0) * self.cam_recoil_yaw
        
        return {
            'damage': self.damage,
            'pellets': self.pellets,
            'spread': self.spread if not self.is_aiming else (self.spread * 0.4),
            'range': self.range,
            'cam_kick': (cam_kick_pitch, cam_kick_yaw),
            'muzzle_pos': self.muzzle_node.get_pos(self.app.render)
        }

    def update(self, dt, current_time, is_moving, is_sprinting):
        # Update muzzle flash timer
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= dt
            if self.muzzle_flash_timer <= 0:
                self.flash_mesh.hide()
                self.app.render.clear_light(self.muzzle_light)

        # Update Reloading
        if self.is_reloading:
            self.reload_timer += dt
            if self.reload_timer >= self.reload_duration:
                self.finish_reload()
                
        # ADS interpolation
        target_ads = 1.0 if (self.is_aiming and not self.is_reloading) else 0.0
        self.ads_progress += (target_ads - self.ads_progress) * min(1.0, dt * 14.0)

        # Base pos & hpr between hip and ADS
        cur_pos = self.hip_pos * (1.0 - self.ads_progress) + self.ads_pos * self.ads_progress
        cur_hpr = self.hip_hpr * (1.0 - self.ads_progress) + self.ads_hpr * self.ads_progress

        # Reload animation dip & tilt
        if self.is_reloading:
            progress = self.reload_timer / self.reload_duration
            reload_dip = math.sin(progress * math.pi) * 0.18
            cur_pos.z -= reload_dip
            cur_hpr.y -= reload_dip * 40.0
            cur_hpr.z += math.sin(progress * math.pi * 2.0) * 12.0

        # Gun Inspect Animation
        if self.is_inspecting:
            self.inspect_timer += dt
            t = self.inspect_timer / self.inspect_duration
            if t >= 1.0:
                self.is_inspecting = False
            else:
                # Smooth inspect motion curve
                phase = math.sin(t * math.pi)
                # Weapon rotates 45 deg sideways, tilts up to examine chamber
                cur_hpr.x += math.sin(t * math.pi * 1.5) * 35.0
                cur_hpr.y += phase * 18.0
                cur_hpr.z += math.sin(t * math.pi * 1.2) * -38.0
                # Slight shift inwards toward chest
                cur_pos.x -= phase * 0.08
                cur_pos.y += phase * 0.05
                cur_pos.z += phase * 0.06

        # Walk/Sprint sway & bobbing (only if not ADS or reduced in ADS)
        bob_factor = 0.2 if self.ads_progress > 0.5 else 1.0
        if is_moving:
            bob_speed = 14.0 if is_sprinting else 9.0
            bob_amp = 0.022 if is_sprinting else 0.012
            cur_pos.x += math.cos(current_time * (bob_speed * 0.5)) * bob_amp * 1.5 * bob_factor
            cur_pos.z += abs(math.sin(current_time * bob_speed)) * bob_amp * bob_factor
            cur_hpr.z += math.cos(current_time * (bob_speed * 0.5)) * 2.2 * bob_factor
        else:
            # Idle breathing sway
            cur_pos.y += math.sin(current_time * 2.0) * 0.003
            cur_pos.z += math.cos(current_time * 1.5) * 0.003

        # Spring recovery for recoil
        self.recoil_offset_pos *= math.exp(-18.0 * dt)
        self.recoil_offset_hpr *= math.exp(-20.0 * dt)
        
        final_pos = cur_pos + self.recoil_offset_pos
        final_hpr = cur_hpr + self.recoil_offset_hpr
        
        self.root.set_pos(final_pos)
        self.root.set_hpr(final_hpr)

    def show(self):
        self.root.show()

    def hide(self):
        self.cancel_inspect()
        if self.muzzle_light:
            self.app.render.clear_light(self.muzzle_light)
        if self.flash_mesh:
            self.flash_mesh.hide()
        self.root.hide()


# ==============================================================================
# WEAPON 1: PISTOL (USP Tactical)
# ==============================================================================
class Pistol(Weapon):
    def __init__(self, app, camera):
        super().__init__("Pistol", app, camera)
        self.damage = 32
        self.mag_size = 12
        self.current_ammo = 12
        self.reserve_ammo = 48
        self.fire_rate = 0.18
        self.is_automatic = False
        self.spread = 0.012
        self.recoil_kick_z = 0.03
        self.recoil_kick_y = -0.04
        self.recoil_pitch = 4.0
        self.cam_recoil_pitch = 1.0
        self.cam_recoil_yaw = 0.3
        self.ads_pos = Vec3(0.0, 0.42, -0.15)

    def build_model(self):
        # Frame & Grip (Matte Black)
        grip = make_cube(0.045, 0.08, 0.12, Vec4(0.15, 0.15, 0.16, 1.0))
        grip.reparent_to(self.root)
        grip.set_pos(0, 0.0, -0.06)
        grip.set_p(-12)
        
        # Slide (Steel Grey)
        slide = make_cube(0.05, 0.22, 0.055, Vec4(0.3, 0.32, 0.34, 1.0))
        slide.reparent_to(self.root)
        slide.set_pos(0, 0.05, 0.02)
        if self.gun_tex:
            slide.set_texture(self.gun_tex)
        
        # Barrel tip
        barrel = make_cylinder(0.012, 0.06, 10, Vec4(0.1, 0.1, 0.1, 1.0))
        barrel.reparent_to(self.root)
        barrel.set_pos(0, 0.17, 0.02)
        barrel.set_p(90)
        
        # Sights (Tritium dots)
        front_sight = make_cube(0.008, 0.012, 0.012, Vec4(0.2, 0.9, 0.2, 1.0))
        front_sight.reparent_to(self.root)
        front_sight.set_pos(0, 0.15, 0.052)
        
        rear_sight = make_cube(0.035, 0.012, 0.012, Vec4(0.2, 0.2, 0.2, 1.0))
        rear_sight.reparent_to(self.root)
        rear_sight.set_pos(0, -0.05, 0.052)
        
        self.muzzle_node = self.root.attach_new_node("muzzle_pos")
        self.muzzle_node.set_pos(0, 0.21, 0.02)


# ==============================================================================
# WEAPON 2: ASSAULT RIFLE (M4A1 Tactical)
# ==============================================================================
class AssaultRifle(Weapon):
    def __init__(self, app, camera):
        super().__init__("Assault Rifle", app, camera)
        self.damage = 28
        self.mag_size = 30
        self.current_ammo = 30
        self.reserve_ammo = 150
        self.fire_rate = 0.10  # 600 RPM
        self.is_automatic = True
        self.spread = 0.018
        self.recoil_kick_z = 0.022
        self.recoil_kick_y = -0.05
        self.recoil_pitch = 2.0
        self.cam_recoil_pitch = 0.9
        self.cam_recoil_yaw = 0.35
        self.ads_pos = Vec3(0.0, 0.44, -0.16)

    def build_model(self):
        # Receiver (Tactical Olive / Dark Charcoal)
        rec = make_cube(0.06, 0.28, 0.075, Vec4(0.2, 0.22, 0.24, 1.0))
        rec.reparent_to(self.root)
        rec.set_pos(0, 0.02, 0.0)
        if self.gun_tex:
            rec.set_texture(self.gun_tex)
        
        # Handguard / Barrel shroud
        hg = make_cube(0.055, 0.25, 0.065, Vec4(0.25, 0.27, 0.25, 1.0))
        hg.reparent_to(self.root)
        hg.set_pos(0, 0.26, 0.0)
        
        # Barrel + Flash Hider
        barrel = make_cylinder(0.015, 0.22, 10, Vec4(0.12, 0.12, 0.14, 1.0))
        barrel.reparent_to(self.root)
        barrel.set_pos(0, 0.42, 0.005)
        barrel.set_p(90)
        
        # Stock (Tactical Adjustable)
        stock = make_cube(0.05, 0.22, 0.09, Vec4(0.15, 0.15, 0.16, 1.0))
        stock.reparent_to(self.root)
        stock.set_pos(0, -0.22, -0.01)
        
        # Curved Magazine
        mag = make_cube(0.038, 0.08, 0.18, Vec4(0.12, 0.12, 0.13, 1.0))
        mag.reparent_to(self.root)
        mag.set_pos(0, 0.08, -0.11)
        mag.set_p(15)
        
        # Pistol Grip
        pgrip = make_cube(0.04, 0.07, 0.13, Vec4(0.16, 0.16, 0.18, 1.0))
        pgrip.reparent_to(self.root)
        pgrip.set_pos(0, -0.07, -0.09)
        pgrip.set_p(-20)
        
        # Holosight Optic
        sight_base = make_cube(0.045, 0.1, 0.04, Vec4(0.1, 0.1, 0.1, 1.0))
        sight_base.reparent_to(self.root)
        sight_base.set_pos(0, 0.04, 0.055)
        
        # Holo Reticle Glow Dot
        reticle = make_cube(0.008, 0.008, 0.008, Vec4(0.1, 1.0, 0.3, 1.0))
        reticle.reparent_to(sight_base)
        reticle.set_pos(0, 0.02, 0.02)
        
        self.muzzle_node = self.root.attach_new_node("muzzle_pos")
        self.muzzle_node.set_pos(0, 0.54, 0.005)


# ==============================================================================
# WEAPON 3: SHOTGUN (SPAS-12 Pump Action)
# ==============================================================================
class Shotgun(Weapon):
    def __init__(self, app, camera):
        super().__init__("Shotgun", app, camera)
        self.damage = 18  # 18 * 8 pellets = 144 max close damage!
        self.mag_size = 8
        self.current_ammo = 8
        self.reserve_ammo = 32
        self.fire_rate = 0.75  # Pump delay
        self.is_automatic = False
        self.pellets = 8
        self.spread = 0.065
        self.recoil_kick_z = 0.08
        self.recoil_kick_y = -0.12
        self.recoil_pitch = 6.5
        self.cam_recoil_pitch = 2.4
        self.cam_recoil_yaw = 0.6
        self.ads_pos = Vec3(0.0, 0.44, -0.15)

    def build_model(self):
        # Heavy Receiver
        rec = make_cube(0.07, 0.28, 0.08, Vec4(0.18, 0.18, 0.2, 1.0))
        rec.reparent_to(self.root)
        rec.set_pos(0, -0.02, 0.0)
        if self.gun_tex:
            rec.set_texture(self.gun_tex)
        
        # Top Barrel
        top_barrel = make_cylinder(0.022, 0.45, 12, Vec4(0.28, 0.28, 0.3, 1.0))
        top_barrel.reparent_to(self.root)
        top_barrel.set_pos(0, 0.32, 0.025)
        top_barrel.set_p(90)
        
        # Underbarrel Mag Tube
        mag_tube = make_cylinder(0.018, 0.42, 10, Vec4(0.22, 0.22, 0.24, 1.0))
        mag_tube.reparent_to(self.root)
        mag_tube.set_pos(0, 0.31, -0.018)
        mag_tube.set_p(90)
        
        # Pump Slide (Ribbed black composite)
        pump = make_cube(0.075, 0.16, 0.075, Vec4(0.1, 0.1, 0.1, 1.0))
        pump.reparent_to(self.root)
        pump.set_pos(0, 0.28, 0.005)
        
        # Folding Stock / Grip
        grip = make_cube(0.045, 0.07, 0.14, Vec4(0.12, 0.12, 0.14, 1.0))
        grip.reparent_to(self.root)
        grip.set_pos(0, -0.12, -0.08)
        grip.set_p(-25)
        
        self.muzzle_node = self.root.attach_new_node("muzzle_pos")
        self.muzzle_node.set_pos(0, 0.56, 0.025)


# ==============================================================================
# WEAPON 4: SNIPER RIFLE (AWM Heavy Bolt-Action)
# ==============================================================================
class SniperRifle(Weapon):
    def __init__(self, app, camera):
        super().__init__("Sniper Rifle", app, camera)
        self.damage = 110  # One shot kill on grunts!
        self.mag_size = 5
        self.current_ammo = 5
        self.reserve_ammo = 20
        self.fire_rate = 1.35  # Bolt cycle
        self.is_automatic = False
        self.spread = 0.001  # Extreme precision
        self.recoil_kick_z = 0.09
        self.recoil_kick_y = -0.15
        self.recoil_pitch = 8.0
        self.cam_recoil_pitch = 3.2
        self.cam_recoil_yaw = 0.2
        self.ads_pos = Vec3(0.0, 0.36, -0.155)
        self.ads_fov = 14.0  # High zoom scope!
        self.has_scope = True

    def build_model(self):
        # Long Precision Chassis (Arctic Camo / Forest Green)
        chassis = make_cube(0.065, 0.55, 0.085, Vec4(0.22, 0.32, 0.26, 1.0))
        chassis.reparent_to(self.root)
        chassis.set_pos(0, 0.05, -0.01)
        if self.gun_tex:
            chassis.set_texture(self.gun_tex)
        
        # Long Heavy Fluted Barrel
        barrel = make_cylinder(0.018, 0.62, 12, Vec4(0.15, 0.15, 0.17, 1.0))
        barrel.reparent_to(self.root)
        barrel.set_pos(0, 0.58, 0.02)
        barrel.set_p(90)
        
        # Muzzle Brake
        brake = make_cube(0.045, 0.07, 0.04, Vec4(0.1, 0.1, 0.1, 1.0))
        brake.reparent_to(self.root)
        brake.set_pos(0, 0.90, 0.02)
        
        # Large High-Power Optical Scope
        scope_tube = make_cylinder(0.028, 0.26, 14, Vec4(0.12, 0.12, 0.14, 1.0))
        scope_tube.reparent_to(self.root)
        scope_tube.set_pos(0, 0.04, 0.075)
        scope_tube.set_p(90)
        
        # Scope Bells (Front & Rear lenses)
        front_bell = make_cylinder(0.038, 0.06, 14, Vec4(0.1, 0.1, 0.12, 1.0))
        front_bell.reparent_to(self.root)
        front_bell.set_pos(0, 0.17, 0.075)
        front_bell.set_p(90)
        
        rear_bell = make_cylinder(0.034, 0.05, 14, Vec4(0.1, 0.1, 0.12, 1.0))
        rear_bell.reparent_to(self.root)
        rear_bell.set_pos(0, -0.09, 0.075)
        rear_bell.set_p(90)
        
        # Scope Lens Reflection (Coated cyan-blue glass)
        lens = make_cylinder(0.032, 0.01, 12, Vec4(0.2, 0.6, 0.9, 0.8))
        lens.reparent_to(self.root)
        lens.set_pos(0, -0.115, 0.075)
        lens.set_p(90)
        
        # Bolt Handle
        bolt = make_cube(0.05, 0.015, 0.015, Vec4(0.3, 0.3, 0.32, 1.0))
        bolt.reparent_to(self.root)
        bolt.set_pos(0.05, -0.06, 0.04)
        
        # Thumbhole Stock
        stock = make_cube(0.055, 0.26, 0.11, Vec4(0.2, 0.28, 0.23, 1.0))
        stock.reparent_to(self.root)
        stock.set_pos(0, -0.32, -0.02)
        
        self.muzzle_node = self.root.attach_new_node("muzzle_pos")
        self.muzzle_node.set_pos(0, 0.94, 0.02)

    def update(self, dt, current_time, is_moving, is_sprinting):
        super().update(dt, current_time, is_moving, is_sprinting)
        # When fully scoped in, hide the viewmodel so only the 2D tactical scope overlay is visible
        if self.ads_progress > 0.88:
            self.root.hide()
        else:
            self.root.show()
