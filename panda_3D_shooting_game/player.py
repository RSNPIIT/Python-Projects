"""
player.py - High-precision FPS controller:
WASD movement with smooth wall-sliding physics, tactical spawn protection shield,
mouse look with angle clamping, weapon viewmodels, recoil springs, and raycast hit registration.
"""

import math
import random
from panda3d.core import (
    NodePath, Vec3, Vec4, WindowProperties
)
from weapons import Pistol, AssaultRifle, Shotgun, SniperRifle

class Player:
    def __init__(self, app, start_pos=(0, -24, 0)):
        self.app = app
        if app.camera is not None:
            self.camera = app.camera
        else:
            self.camera = app.render.attach_new_node("player_cam")
        
        # Position and Orientation
        self.pos = Vec3(start_pos)
        self.yaw = 0.0
        self.pitch = 0.0
        self.mouse_sens = 0.35
        self.sens_multiplier = 1.0
        self.last_mouse_x = None
        self.last_mouse_y = None
        
        # Camera recoil offsets
        self.recoil_cam_pitch = 0.0
        self.recoil_cam_yaw = 0.0
        
        # Movement speeds
        self.walk_speed = 7.5
        self.sprint_speed = 13.0
        self.crouch_speed = 4.2
        self.jump_velocity = 8.5
        self.gravity = -24.0
        
        # State
        self.vel = Vec3(0, 0, 0)
        self.is_grounded = True
        self.is_sprinting = False
        self.is_crouching = False
        self.is_moving = False
        
        # Dimensions
        self.stand_height = 1.65
        self.crouch_height = 1.05
        self.current_height = self.stand_height
        self.radius = 0.45
        
        # Health, Shield & Spawn Protection
        self.max_health = 100.0
        self.health = 100.0
        self.max_shield = 50.0
        self.shield = 50.0
        self.shield_recharge_timer = 0.0
        self.shield_recharge_delay = 4.0
        self.is_alive = True
        self.spawn_shield_timer = 3.5  # 3.5s deploy protection!
        
        # Audio cadence for footsteps
        self.footstep_timer = 0.0
        
        # Key states
        self.keys = {
            'forward': False, 'backward': False,
            'left': False, 'right': False,
            'turn_left': False, 'turn_right': False,
            'sprint': False, 'crouch': False,
            'jump': False, 'fire': False, 'ads': False
        }
        
        # Arsenal
        self.weapons = [
            AssaultRifle(app, self.camera),
            Shotgun(app, self.camera),
            SniperRifle(app, self.camera),
            Pistol(app, self.camera)
        ]
        self.current_weapon_idx = 0
        self.init_weapon_sounds()
        
        for i, w in enumerate(self.weapons):
            if i == self.current_weapon_idx:
                w.show()
            else:
                w.hide()
                
        self.setup_inputs()

    def has_spawn_shield(self):
        return self.spawn_shield_timer > 0.0

    def init_weapon_sounds(self):
        sm = self.app.sound_mgr
        if not sm:
            return
        self.weapons[0].shoot_sound = sm.get('ar')
        self.weapons[1].shoot_sound = sm.get('shotgun')
        self.weapons[2].shoot_sound = sm.get('sniper')
        self.weapons[3].shoot_sound = sm.get('pistol')
        
        for w in self.weapons:
            w.reload_sound = sm.get('reload')
            w.inspect_sound = sm.get('inspect')

    def setup_inputs(self):
        # Movement
        self.app.accept('w', self.set_key, ['forward', True])
        self.app.accept('w-up', self.set_key, ['forward', False])
        self.app.accept('s', self.set_key, ['backward', True])
        self.app.accept('s-up', self.set_key, ['backward', False])
        self.app.accept('a', self.set_key, ['left', True])
        self.app.accept('a-up', self.set_key, ['left', False])
        self.app.accept('d', self.set_key, ['right', True])
        self.app.accept('d-up', self.set_key, ['right', False])
        
        # 360-Degree Aim / Turning Keys (Arrow keys and Q/E during combat)
        self.app.accept('arrow_left', self.set_key, ['turn_left', True])
        self.app.accept('arrow_left-up', self.set_key, ['turn_left', False])
        self.app.accept('arrow_right', self.set_key, ['turn_right', True])
        self.app.accept('arrow_right-up', self.set_key, ['turn_right', False])
        self.app.accept('q', self.set_key, ['turn_left', True])
        self.app.accept('q-up', self.set_key, ['turn_left', False])
        self.app.accept('e', self.set_key, ['turn_right', True])
        self.app.accept('e-up', self.set_key, ['turn_right', False])
        
        # Actions
        self.app.accept('shift', self.set_key, ['sprint', True])
        self.app.accept('shift-up', self.set_key, ['sprint', False])
        self.app.accept('control', self.set_key, ['crouch', True])
        self.app.accept('control-up', self.set_key, ['crouch', False])
        self.app.accept('c', self.toggle_crouch)
        self.app.accept('space', self.jump)
        
        # Mouse
        self.app.accept('mouse1', self.on_mouse_down)
        self.app.accept('mouse1-up', self.set_key, ['fire', False])
        self.app.accept('mouse3', self.set_key, ['ads', True])
        self.app.accept('mouse3-up', self.set_key, ['ads', False])
        
        # Weapon switching
        self.app.accept('1', self.switch_weapon, [0])
        self.app.accept('2', self.switch_weapon, [1])
        self.app.accept('3', self.switch_weapon, [2])
        self.app.accept('4', self.switch_weapon, [3])
        self.app.accept('wheel_up', self.next_weapon)
        self.app.accept('wheel_down', self.prev_weapon)
        
        # Reload & Inspect
        self.app.accept('r', self.reload_weapon)
        self.app.accept('f', self.inspect_weapon)
        self.app.accept('m', self.toggle_minimap)

    def on_mouse_down(self):
        if not self.app.mouse_locked:
            self.app.lock_mouse()
        self.keys['fire'] = True

    def set_key(self, key, value):
        self.keys[key] = value

    def toggle_crouch(self):
        self.is_crouching = not self.is_crouching

    def jump(self):
        if self.is_grounded:
            self.vel.z = self.jump_velocity
            self.is_grounded = False

    def switch_weapon(self, index):
        if index == self.current_weapon_idx or index < 0 or index >= len(self.weapons):
            return
        self.weapons[self.current_weapon_idx].hide()
        self.current_weapon_idx = index
        self.weapons[self.current_weapon_idx].show()

    def next_weapon(self):
        self.switch_weapon((self.current_weapon_idx + 1) % len(self.weapons))

    def prev_weapon(self):
        self.switch_weapon((self.current_weapon_idx - 1) % len(self.weapons))

    def reload_weapon(self):
        if self.app.game_state != 'PLAYING':
            if self.app.game_state == 'PAUSED':
                self.app.start_game(self.app.selected_map_id)
            return
        weapon = self.weapons[self.current_weapon_idx]
        weapon.start_reload()

    def inspect_weapon(self):
        if self.app.game_state != 'PLAYING':
            return
        weapon = self.weapons[self.current_weapon_idx]
        weapon.start_inspect()

    def toggle_minimap(self):
        if self.app.game_state != 'PLAYING':
            if self.app.game_state == 'PAUSED':
                self.app.return_to_menu()
            return
        if hasattr(self.app, 'minimap') and self.app.minimap:
            self.app.minimap.toggle_expand()

    def get_current_weapon(self):
        return self.weapons[self.current_weapon_idx]

    def get_pos(self):
        return self.pos

    def get_yaw(self):
        return self.yaw

    def apply_platform_motion(self, d_pos, target_ground_z):
        self.pos += d_pos
        self.pos.z = target_ground_z
        self.vel.z = 0
        self.is_grounded = True

    def take_damage(self, amount):
        if not self.is_alive or self.has_spawn_shield():
            return
            
        self.shield_recharge_timer = 0.0
        
        # Shield absorbs first
        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0
                
        if amount > 0:
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                self.is_alive = False
                
        self.recoil_cam_pitch += random.uniform(-1.2, 2.0)
        self.recoil_cam_yaw += random.uniform(-1.5, 1.5)
        if hasattr(self.app, 'hud') and self.app.hud:
            self.app.hud.trigger_damage_flash()

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def add_ammo(self):
        for w in self.weapons:
            w.reserve_ammo = min(w.reserve_ammo + w.mag_size * 2, w.mag_size * 5)

    def update_mouse(self):
        if not self.app.mouse_locked or self.app.win is None:
            return
            
        md = self.app.win.get_pointer(0)
        cx = self.app.win.get_x_size() // 2
        cy = self.app.win.get_y_size() // 2
        
        cur_x = md.get_x()
        cur_y = md.get_y()
        
        if self.last_mouse_x is None:
            self.last_mouse_x = cur_x
            self.last_mouse_y = cur_y
            return
            
        dx = cur_x - self.last_mouse_x
        dy = cur_y - self.last_mouse_y
        self.last_mouse_x = cur_x
        self.last_mouse_y = cur_y
        
        # Periodic re-centering when pointer drifts away from center
        if abs(cur_x - cx) > 120 or abs(cur_y - cy) > 120:
            self.app.win.move_pointer(0, cx, cy)
            self.last_mouse_x = cx
            self.last_mouse_y = cy
            
        if dx != 0 or dy != 0:
            weapon = self.get_current_weapon()
            aim_sens = self.mouse_sens * self.sens_multiplier * (0.35 if weapon.ads_progress > 0.5 else 1.0)
            if weapon.has_scope and weapon.ads_progress > 0.85:
                aim_sens *= 0.30
                
            self.yaw -= dx * aim_sens
            self.pitch -= dy * aim_sens
            self.pitch = max(-85.0, min(85.0, self.pitch))

    def update_shooting(self, current_time, map_manager, enemy_manager, particle_mgr):
        weapon = self.get_current_weapon()
        weapon.is_aiming = self.keys['ads']
        
        should_fire = False
        if weapon.is_automatic:
            should_fire = self.keys['fire']
        else:
            if self.keys['fire'] and current_time - weapon.last_fire_time >= weapon.fire_rate:
                should_fire = True
                self.keys['fire'] = False
                
        if should_fire:
            shot_info = weapon.fire(current_time)
            if shot_info:
                cam_pitch_kick, cam_yaw_kick = shot_info['cam_kick']
                self.recoil_cam_pitch += cam_pitch_kick
                self.recoil_cam_yaw += cam_yaw_kick
                
                cam_quat = self.camera.get_quat(self.app.render)
                base_forward = cam_quat.get_forward()
                cam_pos = self.camera.get_pos(self.app.render)
                
                for _ in range(shot_info['pellets']):
                    spread = shot_info['spread']
                    ray_dir = Vec3(base_forward)
                    if spread > 0.001:
                        ray_dir += Vec3(
                            random.uniform(-spread, spread),
                            random.uniform(-spread, spread),
                            random.uniform(-spread, spread)
                        )
                    ray_dir.normalize()
                    
                    self.perform_raycast(
                        cam_pos, ray_dir, shot_info['damage'], shot_info['range'],
                        map_manager, enemy_manager, particle_mgr, shot_info['muzzle_pos']
                    )

    def perform_raycast(self, origin, direction, damage, max_range, map_manager, enemy_manager, particle_mgr, muzzle_pos):
        closest_hit_dist = max_range
        hit_enemy = None
        hit_barrel = None
        hit_pos = origin + direction * max_range
        
        # Ray against enemies
        for enemy in enemy_manager.enemies:
            if not enemy.is_alive:
                continue
            e_pos = enemy.get_pos()
            to_enemy = e_pos - origin
            dot = to_enemy.dot(direction)
            if 0.5 < dot < closest_hit_dist:
                proj_pt = origin + direction * dot
                d_horiz = math.sqrt((proj_pt.x - e_pos.x)**2 + (proj_pt.y - e_pos.y)**2)
                d_vert = proj_pt.z - e_pos.z
                if d_horiz <= 0.65 and 0.0 <= d_vert <= 2.2:
                    closest_hit_dist = dot
                    hit_enemy = enemy
                    hit_barrel = None
                    hit_pos = proj_pt
                    
        # Ray against explosive barrels
        for barrel in map_manager.barrels:
            if barrel.is_destroyed:
                continue
            b_pos = barrel.get_pos()
            to_barrel = b_pos - origin
            dot = to_barrel.dot(direction)
            if 0.5 < dot < closest_hit_dist:
                proj_pt = origin + direction * dot
                d_horiz = math.sqrt((proj_pt.x - b_pos.x)**2 + (proj_pt.y - b_pos.y)**2)
                d_vert = proj_pt.z - b_pos.z
                if d_horiz <= 0.75 and 0.0 <= d_vert <= 1.6:
                    closest_hit_dist = dot
                    hit_enemy = None
                    hit_barrel = barrel
                    hit_pos = proj_pt

        # Ray against ground
        if direction.z < -0.01:
            ground_t = (0.0 - origin.z) / direction.z
            if 0.0 < ground_t < closest_hit_dist:
                closest_hit_dist = ground_t
                hit_enemy = None
                hit_barrel = None
                hit_pos = origin + direction * ground_t

        if particle_mgr:
            particle_mgr.spawn_tracer(muzzle_pos, hit_pos)

        if hit_enemy:
            is_dead_before = not hit_enemy.is_alive
            hit_enemy.take_damage(damage)
            is_kill = hit_enemy.health <= 0 and not is_dead_before
            if is_kill:
                enemy_manager.enemies_killed += 1
                
            if hasattr(self.app, 'hud') and self.app.hud:
                self.app.hud.trigger_hitmarker(is_kill=is_kill)
            if self.app.sound_mgr and 'hitmarker' in self.app.sound_mgr:
                self.app.sound_mgr['hitmarker'].play()
                
            if particle_mgr:
                particle_mgr.spawn_impact_sparks(hit_pos, -direction, count=6, color=Vec4(1.0, 0.2, 0.1, 1.0))
                
        elif hit_barrel:
            hit_barrel.take_damage(damage, enemy_manager.enemies, self)
            if particle_mgr:
                particle_mgr.spawn_impact_sparks(hit_pos, -direction, count=8, color=Vec4(1.0, 0.7, 0.1, 1.0))
        else:
            if particle_mgr and closest_hit_dist < max_range:
                particle_mgr.spawn_impact_sparks(hit_pos, Vec3(0, 0, 1), count=5, color=Vec4(0.85, 0.85, 0.8, 1.0))

    def update(self, dt, current_time, map_manager, enemy_manager, particle_mgr):
        self.update_mouse()
        
        # Smooth keyboard 360-degree rotation support (Arrow keys or Q/E)
        turn_rate = 145.0 * dt
        if self.keys.get('turn_left'):
            self.yaw += turn_rate
        if self.keys.get('turn_right'):
            self.yaw -= turn_rate
        
        # Countdown spawn protection shield
        if self.spawn_shield_timer > 0:
            self.spawn_shield_timer -= dt
        
        # Shield recharge
        if self.shield < self.max_shield:
            self.shield_recharge_timer += dt
            if self.shield_recharge_timer >= self.shield_recharge_delay:
                self.shield = min(self.max_shield, self.shield + dt * 18.0)
                
        self.recoil_cam_pitch *= math.exp(-14.0 * dt)
        self.recoil_cam_yaw *= math.exp(-14.0 * dt)
        
        target_height = self.crouch_height if self.keys['crouch'] or self.is_crouching else self.stand_height
        self.current_height += (target_height - self.current_height) * min(1.0, dt * 10.0)
        
        # WASD orientation
        forward_dir = Vec3(-math.sin(math.radians(self.yaw)), math.cos(math.radians(self.yaw)), 0)
        right_dir = Vec3(math.cos(math.radians(self.yaw)), math.sin(math.radians(self.yaw)), 0)
        
        move_vec = Vec3(0, 0, 0)
        if self.keys['forward']: move_vec += forward_dir
        if self.keys['backward']: move_vec -= forward_dir
        if self.keys['right']: move_vec += right_dir
        if self.keys['left']: move_vec -= right_dir
        
        self.is_moving = move_vec.length_squared() > 0.01
        self.is_sprinting = self.keys['sprint'] and self.keys['forward'] and not self.keys['ads'] and not self.is_crouching
        
        if self.is_moving:
            move_vec.normalize()
            speed = self.sprint_speed if self.is_sprinting else (self.crouch_speed if self.is_crouching else self.walk_speed)
            self.vel.x = move_vec.x * speed
            self.vel.y = move_vec.y * speed
            
            if self.is_grounded:
                self.footstep_timer += dt
                cadence = 0.28 if self.is_sprinting else 0.44
                if self.footstep_timer >= cadence:
                    self.footstep_timer = 0.0
                    if self.app.sound_mgr and 'footstep' in self.app.sound_mgr:
                        self.app.sound_mgr['footstep'].play()
        else:
            self.vel.x *= math.exp(-16.0 * dt)
            self.vel.y *= math.exp(-16.0 * dt)
            self.footstep_timer = 0.0

        # Gravity
        self.vel.z += self.gravity * dt
        new_pos = self.pos + self.vel * dt
        
        if new_pos.z <= 0.0:
            new_pos.z = 0.0
            self.vel.z = 0
            self.is_grounded = True
            
        # Smooth sliding collision
        self.pos = map_manager.check_collision(self.pos, new_pos, self.radius, self.current_height)

        # Camera
        eye_pos = self.pos + Vec3(0, 0, self.current_height)
        self.camera.set_pos(eye_pos)
        self.camera.set_hpr(self.yaw + self.recoil_cam_yaw, self.pitch + self.recoil_cam_pitch, 0)

        # Dynamic FOV
        weapon = self.get_current_weapon()
        if self.app.camLens is not None:
            target_fov = weapon.ads_fov if weapon.ads_progress > 0.5 else weapon.hip_fov
            cur_fov = self.app.camLens.get_fov()[0]
            new_fov = cur_fov + (target_fov - cur_fov) * min(1.0, dt * 14.0)
            self.app.camLens.set_fov(new_fov)

        self.update_shooting(current_time, map_manager, enemy_manager, particle_mgr)
        weapon.update(dt, current_time, self.is_moving, self.is_sprinting)
