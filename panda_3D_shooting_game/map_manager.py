"""
map_manager.py - Dynamic map generation, multiple maps (Cyber Compound & Desert Outpost),
moving elevators/platforms, shootable explosive barrels, and rotating pickups.
"""

import math
import random
from panda3d.core import (
    NodePath, Vec3, Vec4, PointLight, DirectionalLight, AmbientLight
)
from mesh_builder import make_cube, make_cylinder, make_ramp

# ==============================================================================
# DYNAMIC MAP ELEMENT: EXPLOSIVE BARREL
# ==============================================================================
class ExplosiveBarrel:
    def __init__(self, render, pos, particle_mgr, sound_mgr):
        self.render = render
        self.pos = Vec3(pos)
        self.particle_mgr = particle_mgr
        self.sound_mgr = sound_mgr
        self.health = 35.0
        self.is_destroyed = False
        self.radius = 1.0
        self.blast_radius = 8.5
        self.blast_damage = 120.0
        
        self.root = render.attach_new_node("explosive_barrel")
        self.root.set_pos(self.pos)
        
        # Red Drum with yellow hazard rings
        drum = make_cylinder(0.55, 1.4, 14, Vec4(0.85, 0.15, 0.1, 1.0))
        drum.reparent_to(self.root)
        drum.set_pos(0, 0, 0.7)
        
        # Hazard stripes
        stripe = make_cylinder(0.57, 0.25, 14, Vec4(1.0, 0.8, 0.0, 1.0))
        stripe.reparent_to(self.root)
        stripe.set_pos(0, 0, 0.7)
        
        # Top rim
        cap = make_cylinder(0.56, 0.08, 14, Vec4(0.1, 0.1, 0.1, 1.0))
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
        
        # Audio & Particles
        self.particle_mgr.spawn_explosion_effect(self.get_pos(), self.blast_radius)
        if self.sound_mgr and 'explosion' in self.sound_mgr:
            self.sound_mgr['explosion'].play()
            
        # Blast damage to nearby enemies
        b_pos = self.get_pos()
        for enemy in all_enemies:
            if enemy.is_alive:
                dist = (enemy.get_pos() - b_pos).length()
                if dist <= self.blast_radius:
                    falloff = max(0.2, 1.0 - (dist / self.blast_radius))
                    enemy.take_damage(self.blast_damage * falloff)
                    
        # Blast damage to player
        p_dist = (player.get_pos() - b_pos).length()
        if p_dist <= self.blast_radius:
            falloff = max(0.2, 1.0 - (p_dist / self.blast_radius))
            player.take_damage(self.blast_damage * falloff * 0.7)
            
        self.root.remove_node()


# ==============================================================================
# DYNAMIC MAP ELEMENT: MOVING PLATFORM / ELEVATOR
# ==============================================================================
class MovingPlatform:
    def __init__(self, render, start_pos, end_pos, size=(3.5, 3.5, 0.4), speed=0.8):
        self.render = render
        self.start_pos = Vec3(start_pos)
        self.end_pos = Vec3(end_pos)
        self.size = size
        self.speed = speed
        self.t = 0.0
        
        self.root = render.attach_new_node("moving_platform")
        self.root.set_pos(self.start_pos)
        
        # Steel grating platform
        plat = make_cube(size[0], size[1], size[2], Vec4(0.25, 0.35, 0.45, 1.0))
        plat.reparent_to(self.root)
        plat.set_pos(0, 0, size[2] * 0.5)
        
        # Glowing safety edge markers
        edge = make_cube(size[0] + 0.1, size[1] + 0.1, 0.05, Vec4(0.0, 0.9, 1.0, 1.0))
        edge.reparent_to(self.root)
        edge.set_pos(0, 0, size[2] * 0.5)
        
        self.current_vel = Vec3(0, 0, 0)
        self.last_pos = Vec3(self.start_pos)

    def get_pos(self):
        return self.root.get_pos()

    def update(self, dt):
        self.t += dt * self.speed
        # Smooth sine oscillation between start and end
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
            abs(p_pos.z - (pos.z + hz)) < 0.35):
            return True
        return False


# ==============================================================================
# DYNAMIC MAP ELEMENT: PICKUP CRATE (HEALTH / AMMO)
# ==============================================================================
class PickupCrate:
    def __init__(self, render, pos, kind="health", sound_mgr=None):
        self.render = render
        self.pos = Vec3(pos)
        self.kind = kind  # "health" or "ammo"
        self.sound_mgr = sound_mgr
        self.is_active = True
        self.respawn_timer = 0.0
        self.respawn_duration = 15.0
        
        self.root = render.attach_new_node(f"pickup_{kind}")
        self.root.set_pos(self.pos)
        
        color = Vec4(0.1, 0.9, 0.3, 1.0) if kind == "health" else Vec4(0.2, 0.7, 1.0, 1.0)
        crate = make_cube(0.8, 0.8, 0.8, color)
        crate.reparent_to(self.root)
        
        # Emissive cross or ammo badge
        badge_c = Vec4(1, 1, 1, 1)
        badge = make_cube(0.3, 0.82, 0.3, badge_c)
        badge.reparent_to(self.root)

    def get_pos(self):
        return self.root.get_pos()

    def update(self, dt, current_time, player):
        if not self.is_active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.is_active = True
                self.root.show()
            return
            
        # Float & Spin animation
        self.root.set_h(current_time * 65.0)
        self.root.set_z(self.pos.z + math.sin(current_time * 3.0) * 0.15)
        
        # Player pickup check
        dist = (player.get_pos() - self.root.get_pos()).length()
        if dist < 1.6:
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
        self.obstacles = []  # list of (min_x, max_x, min_y, max_y, min_z, max_z) for collision
        self.spawn_points = []
        self.lights = []
        self.searchlight = None
        self.searchlight_angle = 0.0
        self.current_map_name = ""

    def add_box_obstacle(self, x, y, z, dx, dy, dz, color=Vec4(0.5, 0.5, 0.5, 1.0)):
        box = make_cube(dx, dy, dz, color)
        box.reparent_to(self.map_root)
        box.set_pos(x, y, z + dz * 0.5)
        
        # Register obstacle bounding box
        hx, hy, hz = dx * 0.5, dy * 0.5, dz
        self.obstacles.append({
            'min_x': x - hx, 'max_x': x + hx,
            'min_y': y - hy, 'max_y': y + hy,
            'min_z': z, 'max_z': z + hz
        })
        return box

    def add_ramp_obstacle(self, x, y, z, dx, dy, dz, hpr=(0, 0, 0), color=Vec4(0.4, 0.45, 0.5, 1.0)):
        ramp = make_ramp(dx, dy, dz, color)
        ramp.reparent_to(self.map_root)
        ramp.set_pos(x, y, z)
        ramp.set_hpr(*hpr)
        # Simplified AABB for ramp base
        hx, hy = dx * 0.5, dy * 0.5
        self.obstacles.append({
            'min_x': x - hx, 'max_x': x + hx,
            'min_y': y - hy, 'max_y': y + hy,
            'min_z': z, 'max_z': z + dz * 0.5
        })
        return ramp

    def load_map(self, map_id=1):
        """Loads Map 1: Sector 7 Cyber Facility or Map 2: Desert Outpost."""
        self.cleanup()
        self.map_root = self.render.attach_new_node("map_root")
        
        if map_id == 1:
            self.build_cyber_facility()
        else:
            self.build_desert_outpost()

    def build_cyber_facility(self):
        self.current_map_name = "Sector 7 - Cyber Facility"
        
        # Floor (Large Dark High-Tech Arena 90x90)
        floor = make_cube(90.0, 90.0, 1.0, Vec4(0.12, 0.14, 0.17, 1.0))
        floor.reparent_to(self.map_root)
        floor.set_pos(0, 0, -0.5)
        
        # Perimeter Walls
        w_col = Vec4(0.18, 0.2, 0.24, 1.0)
        self.add_box_obstacle(0, 45, 0, 90, 2.0, 8.0, w_col)    # North
        self.add_box_obstacle(0, -45, 0, 90, 2.0, 8.0, w_col)   # South
        self.add_box_obstacle(45, 0, 0, 2.0, 90, 8.0, w_col)    # East
        self.add_box_obstacle(-45, 0, 0, 2.0, 90, 8.0, w_col)   # West
        
        # Shipping Containers (Cover elements with sci-fi colors)
        c_blue = Vec4(0.1, 0.35, 0.6, 1.0)
        c_red = Vec4(0.65, 0.15, 0.15, 1.0)
        c_orange = Vec4(0.7, 0.4, 0.1, 1.0)
        
        self.add_box_obstacle(-14, 12, 0, 4.0, 9.0, 3.5, c_blue)
        self.add_box_obstacle(16, -14, 0, 9.0, 4.0, 3.5, c_red)
        self.add_box_obstacle(-20, -18, 0, 4.0, 8.0, 3.5, c_orange)
        self.add_box_obstacle(22, 18, 0, 8.0, 4.0, 3.5, c_blue)
        
        # Central Raised Bunker / Fortress Catwalk
        bunker_col = Vec4(0.2, 0.22, 0.26, 1.0)
        self.add_box_obstacle(0, 0, 0, 14.0, 14.0, 2.5, bunker_col)
        # Ramps to catwalk
        self.add_ramp_obstacle(0, -10, 0, 4.0, 6.0, 2.5, (0, 0, 0), bunker_col)
        self.add_ramp_obstacle(0, 10, 0, 4.0, 6.0, 2.5, (180, 0, 0), bunker_col)
        
        # High sniper towers in corners
        tower_col = Vec4(0.15, 0.18, 0.22, 1.0)
        self.add_box_obstacle(-32, 32, 0, 7.0, 7.0, 5.0, tower_col)
        self.add_box_obstacle(32, -32, 0, 7.0, 7.0, 5.0, tower_col)
        
        # Moving Elevator Platform: lifts between ground and high catwalk!
        elevator = MovingPlatform(self.map_root, Vec3(-32, 22, 0), Vec3(-32, 22, 5.0), size=(3.5, 3.5, 0.3), speed=0.9)
        self.moving_platforms.append(elevator)
        
        # Moving Shuttle Platform across courtyard
        shuttle = MovingPlatform(self.map_root, Vec3(-10, -2, 2.6), Vec3(10, -2, 2.6), size=(3.0, 3.0, 0.3), speed=0.7)
        self.moving_platforms.append(shuttle)
        
        # Explosive Barrels placed at tactical positions
        barrel_positions = [
            Vec3(-11, 10, 0), Vec3(-11, 14, 0),
            Vec3(13, -12, 0), Vec3(20, -12, 0),
            Vec3(0, 0, 2.5),  # On central bunker!
            Vec3(20, 22, 0), Vec3(-22, -22, 0),
            Vec3(30, -26, 0)
        ]
        for pos in barrel_positions:
            self.barrels.append(ExplosiveBarrel(self.map_root, pos, self.particle_mgr, self.sound_mgr))
            
        # Pickups (Health & Ammo)
        self.pickups.append(PickupCrate(self.map_root, Vec3(-18, 8, 0.8), "health", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(18, -8, 0.8), "health", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(0, 0, 3.5), "ammo", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(-32, 32, 5.8), "ammo", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(32, -32, 5.8), "health", self.sound_mgr))
        
        # Enemy spawn points
        self.spawn_points = [
            Vec3(-35, 35, 0.5), Vec3(35, 35, 0.5),
            Vec3(-35, -35, 0.5), Vec3(35, -35, 0.5),
            Vec3(0, 38, 0.5), Vec3(0, -38, 0.5),
            Vec3(38, 0, 0.5), Vec3(-38, 0, 0.5)
        ]
        
        # Map Lighting (Sci-fi moody cyber theme)
        amb = AmbientLight('cyber_amb')
        amb.set_color(Vec4(0.25, 0.28, 0.35, 1.0))
        amb_np = self.map_root.attach_new_node(amb)
        self.render.set_light(amb_np)
        self.lights.append(amb_np)
        
        sun = DirectionalLight('cyber_sun')
        sun.set_color(Vec4(0.65, 0.7, 0.8, 1.0))
        sun_np = self.map_root.attach_new_node(sun)
        sun_np.set_hpr(-45, -55, 0)
        self.render.set_light(sun_np)
        self.lights.append(sun_np)
        
        # Dynamic Rotating Security Spotlight
        search_l = PointLight('searchlight')
        search_l.set_color(Vec4(0.2, 0.9, 1.0, 1.0))
        search_l.set_attenuation(Vec3(0.3, 0.02, 0.005))
        self.searchlight = self.map_root.attach_new_node(search_l)
        self.searchlight.set_pos(0, 0, 8.0)
        self.render.set_light(self.searchlight)
        self.lights.append(self.searchlight)

    def build_desert_outpost(self):
        self.current_map_name = "Ruins of Oasis - Desert Outpost"
        
        # Warm Sand Floor
        floor = make_cube(90.0, 90.0, 1.0, Vec4(0.76, 0.65, 0.45, 1.0))
        floor.reparent_to(self.map_root)
        floor.set_pos(0, 0, -0.5)
        
        # Sandstone Fortress Walls
        sand_wall = Vec4(0.68, 0.56, 0.38, 1.0)
        self.add_box_obstacle(0, 45, 0, 90, 2.5, 9.0, sand_wall)
        self.add_box_obstacle(0, -45, 0, 90, 2.5, 9.0, sand_wall)
        self.add_box_obstacle(45, 0, 0, 2.5, 90, 9.0, sand_wall)
        self.add_box_obstacle(-45, 0, 0, 2.5, 90, 9.0, sand_wall)
        
        # Sandstone Pillars and Ancient Ruin Blocks
        pillar_col = Vec4(0.62, 0.50, 0.35, 1.0)
        for px in [-22, -10, 10, 22]:
            for py in [-22, 22]:
                self.add_box_obstacle(px, py, 0, 3.2, 3.2, 6.0, pillar_col)
                
        # Raised Courtyard Platform
        self.add_box_obstacle(0, 0, 0, 18.0, 18.0, 2.0, sand_wall)
        self.add_ramp_obstacle(-12, 0, 0, 4.0, 6.0, 2.0, (-90, 0, 0), sand_wall)
        self.add_ramp_obstacle(12, 0, 0, 4.0, 6.0, 2.0, (90, 0, 0), sand_wall)
        
        # Floating Hover Platform crossing the desert courtyard
        hover_plat = MovingPlatform(self.map_root, Vec3(-22, 0, 2.2), Vec3(22, 0, 2.2), size=(4.0, 4.0, 0.4), speed=0.6)
        self.moving_platforms.append(hover_plat)
        
        # Barrels
        barrel_positions = [
            Vec3(-18, -12, 0), Vec3(-18, 12, 0),
            Vec3(18, -12, 0), Vec3(18, 12, 0),
            Vec3(0, 0, 2.0), Vec3(0, 24, 0), Vec3(0, -24, 0)
        ]
        for pos in barrel_positions:
            self.barrels.append(ExplosiveBarrel(self.map_root, pos, self.particle_mgr, self.sound_mgr))
            
        # Pickups
        self.pickups.append(PickupCrate(self.map_root, Vec3(0, 0, 3.0), "health", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(-22, -22, 1.0), "ammo", self.sound_mgr))
        self.pickups.append(PickupCrate(self.map_root, Vec3(22, 22, 1.0), "ammo", self.sound_mgr))
        
        self.spawn_points = [
            Vec3(-35, 35, 0.5), Vec3(35, 35, 0.5),
            Vec3(-35, -35, 0.5), Vec3(35, -35, 0.5),
            Vec3(0, 35, 0.5), Vec3(0, -35, 0.5)
        ]
        
        # Desert Sun & Sky Ambient
        amb = AmbientLight('desert_amb')
        amb.set_color(Vec4(0.42, 0.38, 0.34, 1.0))
        amb_np = self.map_root.attach_new_node(amb)
        self.render.set_light(amb_np)
        self.lights.append(amb_np)
        
        sun = DirectionalLight('desert_sun')
        sun.set_color(Vec4(0.95, 0.88, 0.75, 1.0))
        sun_np = self.map_root.attach_new_node(sun)
        sun_np.set_hpr(30, -60, 0)
        self.render.set_light(sun_np)
        self.lights.append(sun_np)

    def update(self, dt, current_time, player):
        # Update moving platforms
        for plat in self.moving_platforms:
            plat.update(dt)
            # If player is riding on platform, carry player with velocity
            if plat.is_player_on_top(player.get_pos()):
                player.apply_platform_motion(plat.current_vel * dt, plat.get_pos().z + plat.size[2])
                
        # Update pickups
        for pk in self.pickups:
            pk.update(dt, current_time, player)
            
        # Update rotating searchlight if active
        if self.searchlight:
            self.searchlight_angle += dt * 45.0
            rad = math.radians(self.searchlight_angle)
            self.searchlight.set_pos(math.cos(rad) * 16.0, math.sin(rad) * 16.0, 7.5)

    def check_collision(self, old_pos, new_pos, radius=0.6, height=1.8):
        """AABB obstacle collision resolution."""
        res_pos = Vec3(new_pos)
        
        for obs in self.obstacles:
            # Check vertical overlap
            if res_pos.z + height < obs['min_z'] or res_pos.z > obs['max_z']:
                continue
                
            # Check horizontal bounding box with radius padding
            min_x = obs['min_x'] - radius
            max_x = obs['max_x'] + radius
            min_y = obs['min_y'] - radius
            max_y = obs['max_y'] + radius
            
            if min_x <= res_pos.x <= max_x and min_y <= res_pos.y <= max_y:
                # Collision detected, push out along shortest axis
                dx_min = abs(res_pos.x - min_x)
                dx_max = abs(res_pos.x - max_x)
                dy_min = abs(res_pos.y - min_y)
                dy_max = abs(res_pos.y - max_y)
                
                min_dist = min(dx_min, dx_max, dy_min, dy_max)
                if min_dist == dx_min:
                    res_pos.x = min_x
                elif min_dist == dx_max:
                    res_pos.x = max_x
                elif min_dist == dy_min:
                    res_pos.y = min_y
                else:
                    res_pos.y = max_y
                    
        return res_pos

    def cleanup(self):
        for l in self.lights:
            self.render.clear_light(l)
            l.remove_node()
        self.lights.clear()
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
