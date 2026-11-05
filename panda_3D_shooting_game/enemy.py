"""
enemy.py - Random Enemy AI system with distinct classes:
Assault Grunt, Fast Striker, and Laser-aiming Sniper.
Features 3D procedural robotic humanoid models, walking animations,
hit reactions, laser targeting lines, and audio callouts.
"""

import math
import random
from panda3d.core import (
    NodePath, Vec3, Vec4, LineSegs
)
from mesh_builder import make_cube, make_cylinder

class Enemy:
    def __init__(self, render, pos, enemy_type="grunt", particle_mgr=None, sound_mgr=None):
        self.render = render
        self.enemy_type = enemy_type
        self.particle_mgr = particle_mgr
        self.sound_mgr = sound_mgr
        
        self.is_alive = True
        self.death_timer = 0.0
        self.hit_flash_timer = 0.0
        
        # Stats based on archetype
        if enemy_type == "rusher":
            self.max_health = 65.0
            self.speed = 8.5
            self.damage = 18.0
            self.attack_range = 6.0
            self.fire_rate = 1.0
            self.color_theme = Vec4(0.85, 0.25, 0.1, 1.0) # Bright Crimson
        elif enemy_type == "sniper":
            self.max_health = 55.0
            self.speed = 3.8
            self.damage = 45.0
            self.attack_range = 45.0
            self.fire_rate = 2.6
            self.color_theme = Vec4(0.15, 0.45, 0.75, 1.0) # Deep Cyan
        else: # "grunt"
            self.max_health = 85.0
            self.speed = 5.5
            self.damage = 12.0
            self.attack_range = 22.0
            self.fire_rate = 0.28
            self.color_theme = Vec4(0.4, 0.42, 0.45, 1.0) # Steel Grey
            
        self.health = self.max_health
        self.last_attack_time = 0.0
        self.laser_aim_timer = 0.0
        self.aim_duration = 1.2
        
        # Root node
        self.root = render.attach_new_node(f"enemy_{enemy_type}")
        self.root.set_pos(pos)
        
        # Model parts for animation
        self.body_root = self.root.attach_new_node("body_root")
        self.left_leg = None
        self.right_leg = None
        self.left_arm = None
        self.right_arm = None
        self.head = None
        self.laser_line = None
        
        # Health bar 3D billboard
        self.hp_bar_root = self.root.attach_new_node("hp_bar_root")
        self.hp_bar_root.set_pos(0, 0, 2.3)
        self.hp_bar_fill = None
        
        self.build_model()
        self.build_health_bar()

    def build_model(self):
        # Pelvis / Lower body
        pelvis = make_cube(0.5, 0.35, 0.25, Vec4(0.2, 0.2, 0.22, 1.0))
        pelvis.reparent_to(self.body_root)
        pelvis.set_pos(0, 0, 0.9)
        
        # Torso / Armor Chestplate
        torso = make_cube(0.65, 0.4, 0.7, self.color_theme)
        torso.reparent_to(self.body_root)
        torso.set_pos(0, 0, 1.4)
        
        # Glowing Core / Power reactor on chest
        core_c = Vec4(1.0, 0.2, 0.2, 1.0) if self.enemy_type != "sniper" else Vec4(0.1, 0.9, 1.0, 1.0)
        core = make_cube(0.2, 0.42, 0.2, core_c)
        core.reparent_to(self.body_root)
        core.set_pos(0, 0.01, 1.45)
        
        # Head with Visor
        self.head = make_cube(0.35, 0.35, 0.35, Vec4(0.2, 0.22, 0.25, 1.0))
        self.head.reparent_to(self.body_root)
        self.head.set_pos(0, 0, 1.95)
        
        # Visor strip
        visor = make_cube(0.32, 0.37, 0.08, core_c)
        visor.reparent_to(self.head)
        visor.set_pos(0, 0.01, 0.02)
        
        # Legs
        leg_c = Vec4(0.18, 0.18, 0.2, 1.0)
        self.left_leg = self.body_root.attach_new_node("left_leg")
        self.left_leg.set_pos(-0.18, 0, 0.9)
        l_mesh = make_cube(0.18, 0.2, 0.85, leg_c)
        l_mesh.reparent_to(self.left_leg)
        l_mesh.set_pos(0, 0, -0.42)
        
        self.right_leg = self.body_root.attach_new_node("right_leg")
        self.right_leg.set_pos(0.18, 0, 0.9)
        r_mesh = make_cube(0.18, 0.2, 0.85, leg_c)
        r_mesh.reparent_to(self.right_leg)
        r_mesh.set_pos(0, 0, -0.42)
        
        # Arms
        self.left_arm = self.body_root.attach_new_node("left_arm")
        self.left_arm.set_pos(-0.42, 0, 1.65)
        l_arm_mesh = make_cube(0.16, 0.18, 0.7, self.color_theme)
        l_arm_mesh.reparent_to(self.left_arm)
        l_arm_mesh.set_pos(0, 0.05, -0.3)
        
        self.right_arm = self.body_root.attach_new_node("right_arm")
        self.right_arm.set_pos(0.42, 0, 1.65)
        r_arm_mesh = make_cube(0.16, 0.18, 0.7, self.color_theme)
        r_arm_mesh.reparent_to(self.right_arm)
        r_arm_mesh.set_pos(0, 0.05, -0.3)
        
        # Gun in Right Arm
        gun_c = Vec4(0.1, 0.1, 0.12, 1.0)
        gun = make_cube(0.1, 0.55, 0.12, gun_c)
        gun.reparent_to(self.right_arm)
        gun.set_pos(0.02, 0.25, -0.45)
        
        # Aim arms forward
        self.right_arm.set_p(55)
        self.left_arm.set_p(45)
        self.left_arm.set_h(25)

    def build_health_bar(self):
        # Health bar background
        bg = make_cube(0.8, 0.02, 0.1, Vec4(0.1, 0.1, 0.1, 0.8))
        bg.reparent_to(self.hp_bar_root)
        
        # Health bar fill (green)
        self.hp_bar_fill = make_cube(0.78, 0.025, 0.08, Vec4(0.2, 0.9, 0.2, 1.0))
        self.hp_bar_fill.reparent_to(self.hp_bar_root)

    def get_pos(self):
        return self.root.get_pos()

    def take_damage(self, dmg):
        if not self.is_alive:
            return
        self.health -= dmg
        self.hit_flash_timer = 0.08
        self.body_root.set_color_scale(1.8, 0.5, 0.5, 1.0)
        
        # Update HP Bar
        ratio = max(0.0, self.health / self.max_health)
        self.hp_bar_fill.set_scale(ratio, 1.0, 1.0)
        self.hp_bar_fill.set_pos(-(1.0 - ratio) * 0.39, 0, 0)
        
        if self.health <= 0:
            self.die()

    def die(self):
        if not self.is_alive:
            return
        self.is_alive = False
        self.death_timer = 0.0
        self.hp_bar_root.hide()
        
        if self.laser_line:
            self.laser_line.remove_node()
            self.laser_line = None
            
        if self.sound_mgr and 'enemy_death' in self.sound_mgr:
            self.sound_mgr['enemy_death'].play()
            
        # Spawn hit spark burst
        if self.particle_mgr:
            self.particle_mgr.spawn_impact_sparks(self.get_pos() + Vec3(0, 0, 1.2), Vec3(0, 0, 1), 16)

    def update(self, dt, current_time, player, map_manager):
        # If dead, run collapse animation then remove
        if not self.is_alive:
            self.death_timer += dt
            # Collapse backwards
            self.body_root.set_p(min(90.0, self.death_timer * 150.0))
            self.body_root.set_z(-min(0.8, self.death_timer * 1.5))
            if self.death_timer > 2.0:
                self.root.remove_node()
                return False  # signal to remove from manager
            return True

        # Restore color flash after hit
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            if self.hit_flash_timer <= 0:
                self.body_root.clear_color_scale()

        # Face towards player
        p_pos = player.get_pos()
        my_pos = self.get_pos()
        
        # Billboarding health bar to look at camera
        self.hp_bar_root.look_at(player.camera)
        
        to_player = p_pos - my_pos
        to_player.z = 0
        dist = to_player.length()
        
        if dist > 0.1:
            to_player.normalize()
            # Calculate heading angle
            target_angle = math.degrees(math.atan2(-to_player.x, to_player.y))
            self.root.set_h(target_angle)
            
        # Movement logic
        is_walking = False
        should_approach = False
        
        if self.enemy_type == "rusher":
            should_approach = dist > 2.2
        elif self.enemy_type == "sniper":
            should_approach = dist > 32.0
            # If too close, retreat slightly
            if dist < 12.0:
                step = -to_player * self.speed * dt
                new_pos = map_manager.check_collision(my_pos, my_pos + step)
                self.root.set_pos(new_pos)
                is_walking = True
        else: # Grunt
            should_approach = dist > 14.0
            
        if should_approach:
            step = to_player * self.speed * dt
            new_pos = map_manager.check_collision(my_pos, my_pos + step)
            self.root.set_pos(new_pos)
            is_walking = True

        # Walk animation (Leg swinging)
        if is_walking:
            swing = math.sin(current_time * (self.speed * 1.8)) * 32.0
            self.left_leg.set_p(swing)
            self.right_leg.set_p(-swing)
        else:
            self.left_leg.set_p(0)
            self.right_leg.set_p(0)

        # Attack logic
        if self.enemy_type == "sniper":
            self.update_sniper_attack(dt, current_time, dist, player)
        else:
            self.update_regular_attack(current_time, dist, player)

        return True

    def update_regular_attack(self, current_time, dist, player):
        if dist <= self.attack_range:
            if current_time - self.last_attack_time >= self.fire_rate:
                self.last_attack_time = current_time
                # Attack player
                accuracy = 0.85 if self.enemy_type == "grunt" else 0.70
                if random.random() < accuracy:
                    player.take_damage(self.damage)
                    
                # Audio & Tracer
                muzzle_world = self.get_pos() + Vec3(0, 0, 1.4)
                target_pos = player.get_pos() + Vec3(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 1.2)
                if self.particle_mgr:
                    c = Vec4(1.0, 0.3, 0.1, 1.0) if self.enemy_type == "rusher" else Vec4(1.0, 0.8, 0.2, 1.0)
                    self.particle_mgr.spawn_tracer(muzzle_world, target_pos, color=c)
                    
                if self.sound_mgr:
                    snd_key = 'shotgun' if self.enemy_type == "rusher" else 'ar'
                    if snd_key in self.sound_mgr:
                        self.sound_mgr[snd_key].play()

    def update_sniper_attack(self, dt, current_time, dist, player):
        if dist <= self.attack_range:
            # Laser line aiming before shooting
            self.laser_aim_timer += dt
            muzzle_world = self.get_pos() + Vec3(0, 0, 1.6)
            player_chest = player.get_pos() + Vec3(0, 0, 1.2)
            
            # Draw / update red warning laser
            if self.laser_line:
                self.laser_line.remove_node()
                
            lines = LineSegs()
            lines.set_color(Vec4(1.0, 0.05, 0.05, 0.85))
            lines.set_thickness(2.0)
            lines.move_to(muzzle_world)
            lines.draw_to(player_chest)
            self.laser_line = self.render.attach_new_node(lines.create())
            
            if self.laser_aim_timer >= self.aim_duration:
                # FIRE SNIPER SHOT!
                self.laser_aim_timer = 0.0
                if self.laser_line:
                    self.laser_line.remove_node()
                    self.laser_line = None
                    
                player.take_damage(self.damage)
                if self.sound_mgr and 'sniper' in self.sound_mgr:
                    self.sound_mgr['sniper'].play()
                if self.particle_mgr:
                    self.particle_mgr.spawn_tracer(muzzle_world, player_chest, color=Vec4(0.2, 0.8, 1.0, 1.0), speed=250.0)
        else:
            self.laser_aim_timer = 0.0
            if self.laser_line:
                self.laser_line.remove_node()
                self.laser_line = None


# ==============================================================================
# ENEMY MANAGER / WAVE SPAWNER
# ==============================================================================
class EnemyManager:
    def __init__(self, render, particle_mgr, sound_mgr):
        self.render = render
        self.particle_mgr = particle_mgr
        self.sound_mgr = sound_mgr
        self.enemies = []
        self.wave_number = 1
        self.enemies_killed = 0
        self.wave_active = False
        self.wave_complete_timer = 0.0

    def start_wave(self, wave_num, spawn_points):
        self.wave_number = wave_num
        self.wave_active = True
        
        # Clear any remaining dead
        for e in self.enemies:
            if not e.is_alive and e.root:
                e.root.remove_node()
        self.enemies.clear()
        
        # Calculate wave composition
        # Base count + extra each wave
        total_enemies = 4 + wave_num * 2
        
        # Audio voice callout for wave
        if self.sound_mgr and 'voice_wave' in self.sound_mgr:
            self.sound_mgr['voice_wave'].play()
            
        for i in range(total_enemies):
            sp = random.choice(spawn_points) + Vec3(random.uniform(-3, 3), random.uniform(-3, 3), 0)
            
            # Select enemy archetype
            r = random.random()
            if wave_num >= 3 and r < 0.25:
                etype = "sniper"
            elif r < 0.55:
                etype = "rusher"
            else:
                etype = "grunt"
                
            enemy = Enemy(self.render, sp, etype, self.particle_mgr, self.sound_mgr)
            self.enemies.append(enemy)

    def update(self, dt, current_time, player, map_manager):
        alive_count = 0
        remaining_enemies = []
        
        for e in self.enemies:
            keep = e.update(dt, current_time, player, map_manager)
            if keep:
                remaining_enemies.append(e)
            if e.is_alive:
                alive_count += 1
                
        self.enemies = remaining_enemies
        
        # Check wave end
        if self.wave_active and alive_count == 0:
            self.wave_active = False
            self.wave_complete_timer = 3.0
            if self.sound_mgr and 'voice_kill' in self.sound_mgr:
                self.sound_mgr['voice_kill'].play()
                
        if not self.wave_active and self.wave_complete_timer > 0:
            self.wave_complete_timer -= dt
            if self.wave_complete_timer <= 0:
                # Next wave!
                self.start_wave(self.wave_number + 1, map_manager.spawn_points)

    def get_alive_count(self):
        return sum(1 for e in self.enemies if e.is_alive)

    def cleanup(self):
        for e in self.enemies:
            if e.laser_line:
                e.laser_line.remove_node()
            e.root.remove_node()
        self.enemies.clear()
