"""
enemy.py - Balanced and intelligent Tactical AI bots:
Assault Grunt, Close-Quarter Rusher, and Precision Laser Sniper.
Features reaction delays, obstacle line-of-sight awareness, balanced accuracy,
3D tactical chassis models, and death animations.
"""

import math
import random
from panda3d.core import (
    NodePath, Vec3, Vec4, LineSegs
)
from mesh_builder import make_cube, make_cylinder

class Enemy:
    def __init__(self, render, pos, enemy_type="grunt", particle_mgr=None, sound_mgr=None, start_time=0.0):
        self.render = render
        self.enemy_type = enemy_type
        self.particle_mgr = particle_mgr
        self.sound_mgr = sound_mgr
        
        self.is_alive = True
        self.death_timer = 0.0
        self.hit_flash_timer = 0.0
        
        # Reaction delay so enemies do not shoot the player on frame 1
        self.spawn_delay = 1.8
        self.has_sighted_player = False
        
        # Archetype stats
        if enemy_type == "rusher":
            self.max_health = 60.0
            self.speed = 7.2
            self.damage = 14.0
            self.attack_range = 8.0
            self.fire_rate = 1.2
            self.base_accuracy = 0.40
            self.color_theme = Vec4(0.85, 0.25, 0.1, 1.0) # Crimson
        elif enemy_type == "sniper":
            self.max_health = 50.0
            self.speed = 3.5
            self.damage = 38.0
            self.attack_range = 45.0
            self.fire_rate = 3.2
            self.base_accuracy = 0.85
            self.color_theme = Vec4(0.15, 0.45, 0.75, 1.0) # Deep Navy Cyan
        else: # "grunt"
            self.max_health = 75.0
            self.speed = 4.8
            self.damage = 10.0
            self.attack_range = 25.0
            self.fire_rate = 0.45
            self.base_accuracy = 0.35
            self.color_theme = Vec4(0.28, 0.32, 0.36, 1.0) # Carbon Slate
            
        self.health = self.max_health
        self.last_attack_time = start_time + self.spawn_delay
        self.laser_aim_timer = 0.0
        self.aim_duration = 1.6
        
        # Root node
        self.root = render.attach_new_node(f"enemy_{enemy_type}")
        self.root.set_pos(pos)
        
        # Model parts
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
        pelvis = make_cube(0.5, 0.35, 0.25, Vec4(0.15, 0.15, 0.18, 1.0))
        pelvis.reparent_to(self.body_root)
        pelvis.set_pos(0, 0, 0.9)
        
        # Torso / Armor Chestplate
        torso = make_cube(0.65, 0.4, 0.7, self.color_theme)
        torso.reparent_to(self.body_root)
        torso.set_pos(0, 0, 1.4)
        
        # Glowing Energy Visor
        visor_c = Vec4(1.0, 0.2, 0.1, 1.0) if self.enemy_type != "sniper" else Vec4(0.1, 0.9, 1.0, 1.0)
        self.head = make_cube(0.35, 0.35, 0.35, Vec4(0.18, 0.20, 0.22, 1.0))
        self.head.reparent_to(self.body_root)
        self.head.set_pos(0, 0, 1.95)
        
        visor = make_cube(0.33, 0.38, 0.08, visor_c)
        visor.reparent_to(self.head)
        visor.set_pos(0, 0.01, 0.02)
        
        # Limbs
        leg_c = Vec4(0.14, 0.14, 0.16, 1.0)
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
        
        # Weapon
        gun = make_cube(0.08, 0.6, 0.12, Vec4(0.08, 0.08, 0.1, 1.0))
        gun.reparent_to(self.right_arm)
        gun.set_pos(0.02, 0.25, -0.45)
        
        self.right_arm.set_p(55)
        self.left_arm.set_p(45)
        self.left_arm.set_h(25)

    def build_health_bar(self):
        bg = make_cube(0.8, 0.02, 0.1, Vec4(0.05, 0.05, 0.08, 0.85))
        bg.reparent_to(self.hp_bar_root)
        self.hp_bar_fill = make_cube(0.78, 0.025, 0.08, Vec4(0.2, 0.95, 0.3, 1.0))
        self.hp_bar_fill.reparent_to(self.hp_bar_root)

    def get_pos(self):
        return self.root.get_pos()

    def take_damage(self, dmg):
        if not self.is_alive:
            return
        self.health -= dmg
        self.hit_flash_timer = 0.08
        self.body_root.set_color_scale(2.0, 0.4, 0.4, 1.0)
        
        ratio = max(0.0, self.health / self.max_health)
        self.hp_bar_fill.set_scale(ratio, 1.0, 1.0)
        self.hp_bar_fill.set_pos(-(1.0 - ratio) * 0.39, 0, 0)
        
        # Change color to orange/red as health drops
        if ratio < 0.3:
            self.hp_bar_fill.set_color(Vec4(0.95, 0.1, 0.1, 1.0))
        elif ratio < 0.6:
            self.hp_bar_fill.set_color(Vec4(0.95, 0.7, 0.1, 1.0))
            
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
            
        if self.particle_mgr:
            self.particle_mgr.spawn_impact_sparks(self.get_pos() + Vec3(0, 0, 1.2), Vec3(0, 0, 1), 16)

    def update(self, dt, current_time, player, map_manager):
        if not self.is_alive:
            self.death_timer += dt
            self.body_root.set_p(min(90.0, self.death_timer * 150.0))
            self.body_root.set_z(-min(0.8, self.death_timer * 1.5))
            if self.death_timer > 2.0:
                self.root.remove_node()
                return False
            return True

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            if self.hit_flash_timer <= 0:
                self.body_root.clear_color_scale()

        # Face towards player
        p_pos = player.get_pos()
        my_pos = self.get_pos()
        self.hp_bar_root.look_at(player.camera)
        
        to_player = p_pos - my_pos
        to_player.z = 0
        dist = to_player.length()
        
        if dist > 0.1:
            to_player.normalize()
            target_angle = math.degrees(math.atan2(-to_player.x, to_player.y))
            self.root.set_h(target_angle)
            
        # Check Line of Sight (LOS)
        eye_pos = my_pos + Vec3(0, 0, 1.6)
        target_pos = p_pos + Vec3(0, 0, 1.2)
        has_los = map_manager.has_line_of_sight(eye_pos, target_pos)

        # Spawn delay reaction timer
        if self.spawn_delay > 0:
            self.spawn_delay -= dt
            return True

        # Movement logic
        is_walking = False
        should_approach = False
        
        if self.enemy_type == "rusher":
            should_approach = dist > 2.5
        elif self.enemy_type == "sniper":
            should_approach = (dist > 35.0) or (not has_los)
            if dist < 12.0 and has_los:
                step = -to_player * self.speed * dt
                new_pos = map_manager.check_collision(my_pos, my_pos + step)
                self.root.set_pos(new_pos)
                is_walking = True
        else: # Grunt
            should_approach = (dist > 15.0) or (not has_los)
            
        if should_approach:
            step = to_player * self.speed * dt
            new_pos = map_manager.check_collision(my_pos, my_pos + step)
            self.root.set_pos(new_pos)
            is_walking = True

        # Walking animation
        if is_walking:
            swing = math.sin(current_time * (self.speed * 1.8)) * 30.0
            self.left_leg.set_p(swing)
            self.right_leg.set_p(-swing)
        else:
            self.left_leg.set_p(0)
            self.right_leg.set_p(0)

        # Attack logic only if has Line of Sight!
        if has_los and not player.has_spawn_shield():
            if self.enemy_type == "sniper":
                self.update_sniper_attack(dt, current_time, dist, player, eye_pos, target_pos)
            else:
                self.update_regular_attack(current_time, dist, player, eye_pos)
        else:
            if self.laser_line:
                self.laser_line.remove_node()
                self.laser_line = None
            self.laser_aim_timer = 0.0

        return True

    def update_regular_attack(self, current_time, dist, player, eye_pos):
        if dist <= self.attack_range:
            if current_time - self.last_attack_time >= self.fire_rate:
                self.last_attack_time = current_time
                
                # Accuracy falloff with distance
                accuracy = self.base_accuracy * max(0.25, 1.0 - (dist / self.attack_range) * 0.5)
                hit_player = random.random() < accuracy
                
                if hit_player:
                    player.take_damage(self.damage)
                    tracer_target = player.get_pos() + Vec3(0, 0, random.uniform(0.8, 1.5))
                else:
                    # Miss shot that whizzes past player
                    offset_x = random.choice([-1.5, 1.5]) * random.uniform(0.8, 2.0)
                    tracer_target = player.get_pos() + Vec3(offset_x, random.uniform(-1, 1), random.uniform(0.5, 2.2))
                    
                if self.particle_mgr:
                    c = Vec4(1.0, 0.35, 0.1, 1.0) if self.enemy_type == "rusher" else Vec4(1.0, 0.85, 0.2, 1.0)
                    self.particle_mgr.spawn_tracer(eye_pos, tracer_target, color=c)
                    
                if self.sound_mgr:
                    snd_key = 'shotgun' if self.enemy_type == "rusher" else 'ar'
                    if snd_key in self.sound_mgr:
                        self.sound_mgr[snd_key].play()

    def update_sniper_attack(self, dt, current_time, dist, player, eye_pos, target_pos):
        if dist <= self.attack_range:
            self.laser_aim_timer += dt
            
            # Draw visible warning red targeting laser
            if self.laser_line:
                self.laser_line.remove_node()
                
            lines = LineSegs()
            lines.set_color(Vec4(1.0, 0.05, 0.05, 0.85))
            lines.set_thickness(2.5)
            lines.move_to(eye_pos)
            lines.draw_to(target_pos)
            self.laser_line = self.render.attach_new_node(lines.create())
            
            if self.laser_aim_timer >= self.aim_duration:
                self.laser_aim_timer = 0.0
                if self.laser_line:
                    self.laser_line.remove_node()
                    self.laser_line = None
                    
                hit = random.random() < self.base_accuracy
                if hit:
                    player.take_damage(self.damage)
                    
                if self.sound_mgr and 'sniper' in self.sound_mgr:
                    self.sound_mgr['sniper'].play()
                if self.particle_mgr:
                    self.particle_mgr.spawn_tracer(eye_pos, target_pos, color=Vec4(0.1, 0.9, 1.0, 1.0), speed=280.0)
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

    def start_wave(self, wave_num, spawn_points, current_time=0.0):
        self.wave_number = wave_num
        self.wave_active = True
        
        for e in self.enemies:
            if not e.is_alive and e.root:
                e.root.remove_node()
        self.enemies.clear()
        
        # Wave composition
        total_enemies = 3 + wave_num * 2
        
        if self.sound_mgr and 'voice_wave' in self.sound_mgr:
            self.sound_mgr['voice_wave'].play()
            
        for i in range(total_enemies):
            sp = random.choice(spawn_points) + Vec3(random.uniform(-2, 2), random.uniform(-2, 2), 0)
            
            r = random.random()
            if wave_num >= 3 and r < 0.25:
                etype = "sniper"
            elif r < 0.55:
                etype = "rusher"
            else:
                etype = "grunt"
                
            enemy = Enemy(self.render, sp, etype, self.particle_mgr, self.sound_mgr, start_time=current_time)
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
        
        if self.wave_active and alive_count == 0:
            self.wave_active = False
            self.wave_complete_timer = 3.5
            if self.sound_mgr and 'voice_kill' in self.sound_mgr:
                self.sound_mgr['voice_kill'].play()
                
        if not self.wave_active and self.wave_complete_timer > 0:
            self.wave_complete_timer -= dt
            if self.wave_complete_timer <= 0:
                self.start_wave(self.wave_number + 1, map_manager.spawn_points, current_time=current_time)

    def get_alive_count(self):
        return sum(1 for e in self.enemies if e.is_alive)

    def cleanup(self):
        for e in self.enemies:
            if e.laser_line:
                e.laser_line.remove_node()
            e.root.remove_node()
        self.enemies.clear()
