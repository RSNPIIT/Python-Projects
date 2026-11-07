"""
map_manager.py - High-fidelity dynamic map generation with PBR-style textures,
atmospheric volumetric fog, axis-independent sliding collision, line-of-sight raycasts,
shootable explosive hazard drums, moving elevators, and pickups.
"""

import os
import math
import random
from panda3d.core import (
    NodePath, Vec3, Vec4, PointLight, DirectionalLight, AmbientLight,
    Spotlight, Fog, Texture, TextureStage, Filename, Material
)
from mesh_builder import make_cube, make_cylinder, make_ramp

# ==============================================================================
# DYNAMIC MAP ELEMENT: EXPLOSIVE BARREL
# ==============================================================================
class ExplosiveBarrel:
    def __init__(self, render, pos, particle_mgr, sound_mgr, barrel_tex=None):
        self.render = render
        self.pos = Vec3(pos)
        self.particle_mgr = particle_mgr
        self.sound_mgr = sound_mgr
        self.health = 35.0
        self.is_destroyed = False
        self.radius = 0.8
        self.blast_radius = 9.0
        self.blast_damage = 110.0
        
        self.root = render.attach_new_node("explosive_barrel")
        self.root.set_pos(self.pos)
        
        # Heavy Red Drum with hazard stripes
        drum = make_cylinder(0.55, 1.4, 16, Vec4(1, 1, 1, 1))
        drum.reparent_to(self.root)
        drum.set_pos(0, 0, 0.7)
        if barrel_tex:
            drum.set_texture(barrel_tex)
        else:
            drum.set_color(Vec4(0.85, 0.15, 0.1, 1.0))
        
        # Top Rim & Cap
        cap = make_cylinder(0.57, 0.08, 16, Vec4(0.15, 0.15, 0.16, 1.0))
        cap.reparent_to(self.root)
        cap.set_pos(0, 0, 1.38)

    def get_pos(self):
        return self.root.get_pos()

    def take_damage(self, dmg, all_enemies, player):
        if self.is_destroyed:
            return
        self.health -= dmg
        if self.health <= 0:
            self.explode(all_enemies, player)

    def explode(self, all_enemies, player):
        if self.is_destroyed:
            return
        self.is_destroyed = True
        
        # Audio & Fireball particles
        self.particle_mgr.spawn_explosion_effect(self.get_pos(), self.blast_radius)
        if self.sound_mgr and 'explosion' in self.sound_mgr:
            self.sound_mgr['explosion'].play()
            
        b_pos = self.get_pos()
        for enemy in all_enemies:
            if enemy.is_alive:
                dist = (enemy.get_pos() - b_pos).length()
                if dist <= self.blast_radius:
                    falloff = max(0.2, 1.0 - (dist / self.blast_radius))
                    enemy.take_damage(self.blast_damage * falloff)
                    
        p_dist = (player.get_pos() - b_pos).length()
        if p_dist <= self.blast_radius:
            falloff = max(0.2, 1.0 - (p_dist / self.blast_radius))
            player.take_damage(self.blast_damage * falloff * 0.7)
            
        self.root.remove_node()


# ==============================================================================
# DYNAMIC MAP ELEMENT: MOVING PLATFORM / ELEVATOR
# ==============================================================================
class MovingPlatform:
    def __init__(self, render, start_pos, end_pos, size=(3.5, 3.5, 0.4), speed=0.8, tex=None):
        self.render = render
        self.start_pos = Vec3(start_pos)
        self.end_pos = Vec3(end_pos)
        self.size = size
        self.speed = speed
        self.t = 0.0
        
        self.root = render.attach_new_node("moving_platform")
        self.root.set_pos(self.start_pos)
        
        plat = make_cube(size[0], size[1], size[2], Vec4(0.8, 0.85, 0.9, 1.0), uv_scale=(2.0, 2.0))
        plat.reparent_to(self.root)
        plat.set_pos(0, 0, size[2] * 0.5)
        if tex:
            plat.set_texture(tex)
            
        # Glowing neon warning border
        edge = make_cube(size[0] + 0.12, size[1] + 0.12, 0.06, Vec4(0.0, 0.9, 1.0, 1.0))
        edge.reparent_to(self.root)
        edge.set_pos(0, 0, size[2] * 0.5)
        
        self.current_vel = Vec3(0, 0, 0)
        self.last_pos = Vec3(self.start_pos)

    def get_pos(self):
        return self.root.get_pos()

    def update(self, dt):
        self.t += dt * self.speed
        alpha = (math.sin(self.t) + 1.0) * 0.5
        new_pos = self.start_pos * (1.0 - alpha) + self.end_pos * alpha
        self.current_vel = (new_pos - self.last_pos) / max(0.001, dt)
        self.last_pos = Vec3(new_pos)
        self.root.set_pos(new_pos)

    def is_player_on_top(self, p_pos):
        pos = self.get_pos()
        hx, hy, hz = self.size[0] * 0.5, self.size[1] * 0.5, self.size[2]
        if (pos.x - hx <= p_pos.x <= pos.x + hx and
            pos.y - hy <= p_pos.y <= pos.y + hy and
            abs(p_pos.z - (pos.z + hz)) < 0.4):
            return True
        return False


# ==============================================================================
# DYNAMIC MAP ELEMENT: PICKUP CRATE
# ==============================================================================
class PickupCrate:
    def __init__(self, render, pos, kind="health", sound_mgr=None):
        self.render = render
        self.pos = Vec3(pos)
        self.kind = kind
        self.sound_mgr = sound_mgr
        self.is_active = True
        self.respawn_timer = 0.0
        self.respawn_duration = 15.0
        
        self.root = render.attach_new_node(f"pickup_{kind}")
        self.root.set_pos(self.pos)
        
        # High-tech glowing supply crate
        color = Vec4(0.1, 1.0, 0.4, 0.9) if kind == "health" else Vec4(0.0, 0.85, 1.0, 0.9)
        crate = make_cube(0.7, 0.7, 0.7, color)
        crate.reparent_to(self.root)
        
        # Emissive ring
        ring = make_cube(0.85, 0.85, 0.1, Vec4(1.0, 1.0, 1.0, 0.95))
        ring.reparent_to(self.root)

    def get_pos(self):
        return self.root.get_pos()

    def update(self, dt, current_time, player):
        if not self.is_active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.is_active = True
                self.root.show()
            return
            
        self.root.set_h(current_time * 75.0)
        self.root.set_z(self.pos.z + math.sin(current_time * 3.5) * 0.15)
        
        dist = (player.get_pos() - self.root.get_pos()).length()
        if dist < 1.7:
            collected = False
            if self.kind == "health" and player.health < player.max_health:
                player.heal(50)
                collected = True
            elif self.kind == "ammo":
                player.add_ammo()
                collected = True
                
            if collected:
                self.is_active = False
                self.respawn_timer = self.respawn_duration
                self.root.hide()
                if self.sound_mgr and 'pickup' in self.sound_mgr:
                    self.sound_mgr['pickup'].play()


# ==============================================================================
# MAP MANAGER
# ==============================================================================
class MapManager:
    def __init__(self, render, particle_mgr, sound_mgr):
        self.render = render
        self.particle_mgr = particle_mgr
        self.sound_mgr = sound_mgr
        
        self.map_root = render.attach_new_node("map_root")
        self.barrels = []
        self.moving_platforms = []
        self.pickups = []
        self.obstacles = []  # list of AABB dicts
        self.spawn_points = []
        self.lights = []
        self.accent_lights = []
        self.fog = None
        self.searchlight = None
        self.searchlight_angle = 0.0
        self.current_map_name = ""
        
        # Load textures
        self.tex_dir = os.path.join(os.path.dirname(__file__), "textures")
        self.textures = self.load_textures()

    def load_textures(self):
        texs = {}
        names = ["floor_metal.png", "container.png", "cyber_wall.png", "sandstone.png", "barrel_tex.png", "gun_metal.png"]
        for n in names:
            p = os.path.join(self.tex_dir, n)
            if os.path.exists(p):
                t = Texture()
                t.read(Filename(p))
                t.set_minfilter(Texture.FT_linear_mipmap_linear)
                t.set_magfilter(Texture.FT_linear)
                t.set_anisotropic_degree(8)
                t.set_wrap_u(Texture.WM_repeat)
                t.set_wrap_v(Texture.WM_repeat)
                texs[n.split('.')[0]] = t
        return texs

    def apply_surface(self, node, roughness, metallic=0.0, emission=None):
        """Give procedural meshes useful PBR material values."""
        material = Material(f"{node.get_name()}_surface")
        material.set_roughness(roughness)
        material.set_metallic(metallic)
        if emission is not None:
            material.set_emission(emission)
        node.set_material(material, 1)

    def add_accent_fixture(self, name, pos, color, phase=0.0):
        """Add a small emissive marker and a gently pulsing local light."""
        marker = make_cube(0.14, 0.22, 0.82, color)
        marker.reparent_to(self.map_root)
        marker.set_pos(pos)
        marker.set_color_scale(1.25, 1.25, 1.25, 1.0)
        self.apply_surface(marker, roughness=0.28, metallic=0.0, emission=color * 0.65)

        light = PointLight(f"{name}_light")
        light.set_color(color)
        light.set_attenuation(Vec3(1.0, 0.035, 0.004))
        light_np = self.map_root.attach_new_node(light)
        light_np.set_pos(pos)
        self.render.set_light(light_np)
        self.lights.append(light_np)
        self.accent_lights.append({"node": light_np, "color": Vec4(color), "phase": phase})

    def add_searchlight(self, color, height=8.0):
        """Create a moving spot that sweeps across the arena."""
        light = Spotlight("arena_searchlight")
        light.set_color(color)
        light.set_attenuation(Vec3(1.0, 0.012, 0.001))
        light.get_lens().set_fov(58.0)
        light.get_lens().set_near_far(1.0, 70.0)
        self.searchlight = self.map_root.attach_new_node(light)
        self.searchlight_height = height
        self.searchlight.set_pos(0, 0, height)
        self.searchlight.look_at(0, 0, 0)
        self.render.set_light(self.searchlight)
        self.lights.append(self.searchlight)

    def add_box_obstacle(self, x, y, z, dx, dy, dz, color=Vec4(1, 1, 1, 1), tex=None, uv_scale=(1.0, 1.0)):
        box = make_cube(dx, dy, dz, color, uv_scale=uv_scale)
        box.reparent_to(self.map_root)
        box.set_pos(x, y, z + dz * 0.5)
        cyber = self.current_map_name.startswith("Sector 7")
        self.apply_surface(box, roughness=0.58 if cyber else 0.88, metallic=0.28 if cyber else 0.0)
        if tex:
            box.set_texture(tex)
            
        hx, hy, hz = dx * 0.5, dy * 0.5, dz
        self.obstacles.append({
            'min_x': x - hx, 'max_x': x + hx,
            'min_y': y - hy, 'max_y': y + hy,
            'min_z': z, 'max_z': z + hz
        })
        return box

    def add_ramp_obstacle(self, x, y, z, dx, dy, dz, hpr=(0, 0, 0), color=Vec4(0.4, 0.45, 0.5, 1.0), tex=None):
        ramp = make_ramp(dx, dy, dz, color)
        ramp.reparent_to(self.map_root)
        ramp.set_pos(x, y, z)
        ramp.set_hpr(*hpr)
        cyber = self.current_map_name.startswith("Sector 7")
        self.apply_surface(ramp, roughness=0.58 if cyber else 0.88, metallic=0.22 if cyber else 0.0)
        if tex:
            ramp.set_texture(tex)
            
        hx, hy = dx * 0.5, dy * 0.5
        self.obstacles.append({
            'min_x': x - hx, 'max_x': x + hx,
            'min_y': y - hy, 'max_y': y + hy,
            'min_z': z, 'max_z': z + dz * 0.5
        })
        return ramp

    def load_map(self, map_id=1):
        self.cleanup()
        self.map_root = self.render.attach_new_node("map_root")
        if map_id == 1:
            self.build_cyber_facility()
        else:
            self.build_desert_outpost()

    def build_cyber_facility(self):
        self.current_map_name = "Sector 7 - Cyber Facility"
        
        # Deep nocturnal cyber volumetric fog
        self.fog = Fog('cyber_fog')
        self.fog.set_color(Vec4(0.04, 0.07, 0.11, 1.0))
        self.fog.set_exp_density(0.016)
        self.render.set_fog(self.fog)
        
        # Floor (Large Dark High-Tech Arena 90x90 with metal grating texture)
        floor = make_cube(90.0, 90.0, 1.0, Vec4(0.85, 0.9, 1.0, 1.0), uv_scale=(14.0, 14.0))
        floor.reparent_to(self.map_root)
        floor.set_pos(0, 0, -0.5)
        self.apply_surface(floor, roughness=0.3, metallic=0.68)
        if "floor_metal" in self.textures:
            floor.set_texture(self.textures["floor_metal"])
            
        # Perimeter Walls (Cyber high-tech panels)
        wall_tex = self.textures.get("cyber_wall")
        w_col = Vec4(0.9, 0.92, 0.95, 1.0)
        self.add_box_obstacle(0, 45, 0, 90, 2.5, 8.0, w_col, wall_tex, (16.0, 3.0))   # North
        self.add_box_obstacle(0, -45, 0, 90, 2.5, 8.0, w_col, wall_tex, (16.0, 3.0))  # South
        self.add_box_obstacle(45, 0, 0, 2.5, 90, 8.0, w_col, wall_tex, (3.0, 16.0))   # East
        self.add_box_obstacle(-45, 0, 0, 2.5, 90, 8.0, w_col, wall_tex, (3.0, 16.0))  # West
        
        # Shipping Containers with corrugated textures
        c_tex = self.textures.get("container")
        self.add_box_obstacle(-14, 12, 0, 4.0, 9.0, 3.5, Vec4(0.2, 0.5, 0.9, 1.0), c_tex, (2.0, 3.0))
        self.add_box_obstacle(16, -12, 0, 9.0, 4.0, 3.5, Vec4(0.9, 0.3, 0.2, 1.0), c_tex, (3.0, 2.0))
        self.add_box_obstacle(-20, -16, 0, 4.0, 8.0, 3.5, Vec4(0.9, 0.6, 0.1, 1.0), c_tex, (2.0, 3.0))
        self.add_box_obstacle(22, 18, 0, 8.0, 4.0, 3.5, Vec4(0.2, 0.8, 0.6, 1.0), c_tex, (3.0, 2.0))
        
        # Central Raised Bunker / Fortress Catwalk
        self.add_box_obstacle(0, 0, 0, 14.0, 14.0, 2.5, w_col, wall_tex, (4.0, 4.0))
        self.add_ramp_obstacle(0, -9.5, 0, 4.0, 5.0, 2.5, (0, 0, 0), w_col, wall_tex)
        self.add_ramp_obstacle(0, 9.5, 0, 4.0, 5.0, 2.5, (180, 0, 0), w_col, wall_tex)
        
        # Sniper towers in corners
        self.add_box_obstacle(-32, 32, 0, 7.0, 7.0, 5.0, w_col, wall_tex, (2.5, 2.5))
        self.add_box_obstacle(32, -32, 0, 7.0, 7.0, 5.0, w_col, wall_tex, (2.5, 2.5))
        
        # Working Elevator & Shuttle
        elevator = MovingPlatform(self.map_root, Vec3(-32, 22, 0), Vec3(-32, 22, 5.0), size=(3.5, 3.5, 0.3), speed=0.9, tex=self.textures.get("floor_metal"))
        self.moving_platforms.append(elevator)
        
        shuttle = MovingPlatform(self.map_root, Vec3(-10, -2, 2.6), Vec3(10, -2, 2.6), size=(3.0, 3.0, 0.3), speed=0.7, tex=self.textures.get("floor_metal"))
        self.moving_platforms.append(shuttle)
        
        # Explosive Barrels with hazard drum texture
        b_tex = self.textures.get("barrel_tex")
        barrel_positions = [
            Vec3(-11, 10, 0), Vec3(-11, 14, 0),
            Vec3(13, -10, 0), Vec3(20, -10, 0),
            Vec3(0, 0, 2.5),
            Vec3(20, 22, 0), Vec3(-22, -22, 0)
        ]
        for pos in barrel_positions:
            self.barrels.append(ExplosiveBarrel(self.map_root, pos, self.particle_mgr, self.sound_mgr, b_tex))
            
        # Pickups
        self.pickups.append(PickupCrate(self.map_root, Vec3(-18, 8, 0.8), "health", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(18, -6, 0.8), "health", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(0, 0, 3.4), "ammo", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(-32, 32, 5.8), "ammo", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(32, -32, 5.8), "health", self.sound_mgr))
        
        # Safe enemy spawn points (Far from player starting position at 0, -26)
        self.spawn_points = [
            Vec3(-35, 35, 0.5), Vec3(35, 35, 0.5),
            Vec3(-35, -35, 0.5), Vec3(35, -35, 0.5),
            Vec3(0, 38, 0.5), Vec3(38, 0, 0.5), Vec3(-38, 0, 0.5)
        ]
        
        # Moody Sci-Fi Lighting
        amb = AmbientLight('cyber_amb')
        amb.set_color(Vec4(0.22, 0.25, 0.34, 1.0))
        amb_np = self.map_root.attach_new_node(amb)
        self.render.set_light(amb_np)
        self.lights.append(amb_np)
        
        sun = DirectionalLight('cyber_sun')
        sun.set_color(Vec4(0.78, 0.88, 1.0, 1.0))
        sun.set_shadow_caster(True, 2048, 2048)
        sun.get_lens().set_film_size(105.0, 105.0)
        sun.get_lens().set_near_far(1.0, 180.0)
        sun_np = self.map_root.attach_new_node(sun)
        sun_np.set_hpr(-50, -55, 0)
        self.render.set_light(sun_np)
        self.lights.append(sun_np)
        
        self.add_searchlight(Vec4(0.22, 0.76, 1.0, 1.0), height=11.0)
        self.add_accent_fixture("cyan_beacon", Vec3(-14, 12, 4.1), Vec4(0.08, 0.5, 0.9, 1.0), 0.0)
        self.add_accent_fixture("amber_beacon", Vec3(16, -12, 4.1), Vec4(1.0, 0.34, 0.08, 1.0), 2.1)
        self.add_accent_fixture("mint_beacon", Vec3(22, 18, 4.1), Vec4(0.12, 0.85, 0.62, 1.0), 4.2)

    def build_desert_outpost(self):
        self.current_map_name = "Ruins of Oasis - Desert Outpost"
        
        # Golden dust haze volumetric fog
        self.fog = Fog('desert_fog')
        self.fog.set_color(Vec4(0.72, 0.62, 0.48, 1.0))
        self.fog.set_exp_density(0.012)
        self.render.set_fog(self.fog)
        
        sand_tex = self.textures.get("sandstone")
        
        # Sandstone Floor
        floor = make_cube(90.0, 90.0, 1.0, Vec4(0.95, 0.9, 0.85, 1.0), uv_scale=(14.0, 14.0))
        floor.reparent_to(self.map_root)
        floor.set_pos(0, 0, -0.5)
        self.apply_surface(floor, roughness=0.92, metallic=0.0)
        if sand_tex:
            floor.set_texture(sand_tex)
            
        # Fortress Walls
        col = Vec4(0.9, 0.88, 0.82, 1.0)
        self.add_box_obstacle(0, 45, 0, 90, 2.5, 9.0, col, sand_tex, (16.0, 3.0))
        self.add_box_obstacle(0, -45, 0, 90, 2.5, 9.0, col, sand_tex, (16.0, 3.0))
        self.add_box_obstacle(45, 0, 0, 2.5, 90, 9.0, col, sand_tex, (3.0, 16.0))
        self.add_box_obstacle(-45, 0, 0, 2.5, 90, 9.0, col, sand_tex, (3.0, 16.0))
        
        # Ancient Ruin Pillars
        for px in [-22, -10, 10, 22]:
            for py in [-22, 22]:
                self.add_box_obstacle(px, py, 0, 3.2, 3.2, 6.0, col, sand_tex, (2.0, 3.0))
                
        # Raised Courtyard
        self.add_box_obstacle(0, 0, 0, 18.0, 18.0, 2.0, col, sand_tex, (4.0, 4.0))
        self.add_ramp_obstacle(-11.5, 0, 0, 4.0, 5.0, 2.0, (-90, 0, 0), col, sand_tex)
        self.add_ramp_obstacle(11.5, 0, 0, 4.0, 5.0, 2.0, (90, 0, 0), col, sand_tex)
        
        # Moving Platform
        hover_plat = MovingPlatform(self.map_root, Vec3(-22, 0, 2.2), Vec3(22, 0, 2.2), size=(4.0, 4.0, 0.4), speed=0.6, tex=sand_tex)
        self.moving_platforms.append(hover_plat)
        
        # Barrels
        b_tex = self.textures.get("barrel_tex")
        barrel_positions = [
            Vec3(-18, -12, 0), Vec3(-18, 12, 0),
            Vec3(18, -12, 0), Vec3(18, 12, 0),
            Vec3(0, 0, 2.0), Vec3(0, 24, 0)
        ]
        for pos in barrel_positions:
            self.barrels.append(ExplosiveBarrel(self.map_root, pos, self.particle_mgr, self.sound_mgr, b_tex))
            
        # Pickups
        self.pickups.append(PickupCrate(self.map_root, Vec3(0, 0, 3.0), "health", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(-22, -22, 1.0), "ammo", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(22, 22, 1.0), "ammo", self.sound_mgr))
        
        self.spawn_points = [
            Vec3(-35, 35, 0.5), Vec3(35, 35, 0.5),
            Vec3(-35, -35, 0.5), Vec3(35, -35, 0.5),
            Vec3(0, 36, 0.5)
        ]
        
        # Desert Sunlight
        amb = AmbientLight('desert_amb')
        amb.set_color(Vec4(0.34, 0.31, 0.27, 1.0))
        amb_np = self.map_root.attach_new_node(amb)
        self.render.set_light(amb_np)
        self.lights.append(amb_np)
        
        sun = DirectionalLight('desert_sun')
        sun.set_color(Vec4(1.0, 0.84, 0.66, 1.0))
        sun.set_shadow_caster(True, 2048, 2048)
        sun.get_lens().set_film_size(105.0, 105.0)
        sun.get_lens().set_near_far(1.0, 180.0)
        sun_np = self.map_root.attach_new_node(sun)
        sun_np.set_hpr(30, -60, 0)
        self.render.set_light(sun_np)
        self.lights.append(sun_np)

        self.add_searchlight(Vec4(1.0, 0.62, 0.28, 1.0), height=12.0)
        self.add_accent_fixture("amber_beacon", Vec3(-22, 22, 6.4), Vec4(1.0, 0.48, 0.15, 1.0), 0.8)
        self.add_accent_fixture("gold_beacon", Vec3(22, -22, 6.4), Vec4(1.0, 0.74, 0.3, 1.0), 3.4)

    def update(self, dt, current_time, player):
        self.animate_environment(dt, current_time)
        for plat in self.moving_platforms:
            plat.update(dt)
            if plat.is_player_on_top(player.get_pos()):
                player.apply_platform_motion(plat.current_vel * dt, plat.get_pos().z + plat.size[2])
                
        for pk in self.pickups:
            pk.update(dt, current_time, player)
            
    def animate_environment(self, dt, current_time):
        if self.searchlight:
            self.searchlight_angle += dt * 24.0
            rad = math.radians(self.searchlight_angle)
            self.searchlight.set_pos(math.cos(rad) * 20.0, math.sin(rad) * 20.0, self.searchlight_height)
            self.searchlight.look_at(0, 0, 1.0)

        for accent in self.accent_lights:
            pulse = 0.82 + 0.18 * (0.5 + 0.5 * math.sin(current_time * 2.2 + accent["phase"]))
            base = accent["color"]
            accent["node"].node().set_color(Vec4(base.x * pulse, base.y * pulse, base.z * pulse, base.w))

    def _is_colliding(self, pos, radius, height):
        for obs in self.obstacles:
            if pos.z + height <= obs['min_z'] or pos.z >= obs['max_z']:
                continue
            if (obs['min_x'] - radius <= pos.x <= obs['max_x'] + radius and
                obs['min_y'] - radius <= pos.y <= obs['max_y'] + radius):
                return True
        return False

    def check_collision(self, old_pos, new_pos, radius=0.45, height=1.7):
        """Axis-independent sliding collision. Allows buttery-smooth sliding along walls."""
        # 1. Test X movement first
        test_x = Vec3(new_pos.x, old_pos.y, old_pos.z)
        if self._is_colliding(test_x, radius, height):
            final_x = old_pos.x
        else:
            final_x = new_pos.x
            
        # 2. Test Y movement with resolved X
        test_y = Vec3(final_x, new_pos.y, old_pos.z)
        if self._is_colliding(test_y, radius, height):
            final_y = old_pos.y
        else:
            final_y = new_pos.y
            
        return Vec3(final_x, final_y, new_pos.z)

    def has_line_of_sight(self, p1, p2):
        """Ray-AABB test to ensure enemies cannot shoot through walls or obstacles."""
        ray_dir = p2 - p1
        ray_len = ray_dir.length()
        if ray_len < 0.1:
            return True
        ray_dir.normalize()
        
        # Step through ray at 1.0 unit intervals
        steps = int(ray_len)
        for i in range(1, steps):
            pt = p1 + ray_dir * i
            for obs in self.obstacles:
                if (obs['min_z'] <= pt.z <= obs['max_z'] and
                    obs['min_x'] <= pt.x <= obs['max_x'] and
                    obs['min_y'] <= pt.y <= obs['max_y']):
                    return False
        return True

    def cleanup(self):
        if self.fog:
            self.render.clear_fog()
            self.fog = None
        for l in self.lights:
            self.render.clear_light(l)
            l.remove_node()
        self.lights.clear()
        self.accent_lights.clear()
        self.searchlight = None
        
        for b in self.barrels:
            if not b.is_destroyed:
                b.root.remove_node()
        self.barrels.clear()
        
        for p in self.moving_platforms:
            p.root.remove_node()
        self.moving_platforms.clear()
        
        for pk in self.pickups:
            pk.root.remove_node()
        self.pickups.clear()
        
        self.obstacles.clear()
        self.spawn_points.clear()
        self.map_root.remove_node()
