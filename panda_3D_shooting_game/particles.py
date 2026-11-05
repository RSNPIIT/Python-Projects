"""
particles.py - Visual effects for Modern Shooter:
Tracer lines, muzzle flashes, bullet impact sparks, explosion debris,
and hit smoke.
"""

import random
import math
from panda3d.core import (
    NodePath, Vec3, Vec4, LineSegs, PointLight, BillboardEffect
)
from mesh_builder import make_cube

class ParticleManager:
    def __init__(self, render):
        self.render = render
        self.tracers = []
        self.sparks = []
        self.explosions = []
        self.flashes = []

    def spawn_tracer(self, start_pos, end_pos, color=Vec4(1.0, 0.85, 0.3, 1.0), speed=180.0):
        """Creates a high-velocity visible bullet tracer beam."""
        direction = end_pos - start_pos
        dist = direction.length()
        if dist < 0.1:
            return
        direction.normalize()
        
        # Segment length for tracer
        seg_len = min(4.0, dist * 0.5)
        
        lines = LineSegs()
        lines.set_color(color)
        lines.set_thickness(2.5)
        lines.move_to(0, 0, 0)
        lines.draw_to(0, seg_len, 0)
        
        node = lines.create()
        tracer_np = self.render.attach_new_node(node)
        tracer_np.set_pos(start_pos)
        tracer_np.look_at(start_pos + direction)
        
        self.tracers.append({
            'np': tracer_np,
            'pos': Vec3(start_pos),
            'dir': direction,
            'dist_traveled': 0.0,
            'max_dist': dist,
            'speed': speed
        })

    def spawn_impact_sparks(self, pos, normal=Vec3(0, 0, 1), count=8, color=Vec4(1.0, 0.6, 0.1, 1.0)):
        """Creates sparks scattering off an impact surface."""
        for _ in range(count):
            spark_np = make_cube(0.08, 0.08, 0.08, color)
            spark_np.reparent_to(self.render)
            spark_np.set_pos(pos + normal * 0.05)
            
            # Scatter velocity oriented towards normal
            vel = Vec3(
                normal.x + (random.random() * 2.0 - 1.0) * 0.9,
                normal.y + (random.random() * 2.0 - 1.0) * 0.9,
                normal.z + random.random() * 1.2 + 0.3
            )
            vel.normalize()
            vel *= random.uniform(6.0, 14.0)
            
            self.sparks.append({
                'np': spark_np,
                'vel': vel,
                'life': random.uniform(0.2, 0.5),
                'max_life': 0.5,
                'size': 0.08
            })

    def spawn_explosion_effect(self, pos, radius=6.0):
        """Creates an expanding fireball with shockwave debris and smoke."""
        # Flash light
        plight = PointLight('exp_light')
        plight.set_color(Vec4(1.0, 0.5, 0.1, 1.0))
        plight.set_attenuation(Vec3(0.5, 0.05, 0.01))
        plight_np = self.render.attach_new_node(plight)
        plight_np.set_pos(pos + Vec3(0, 0, 1.5))
        self.render.set_light(plight_np)
        
        # Fireballs & Debris chunks
        chunks = []
        for _ in range(16):
            size = random.uniform(0.4, 1.2)
            c = random.choice([
                Vec4(1.0, 0.9, 0.2, 1.0), # Bright yellow
                Vec4(1.0, 0.4, 0.0, 1.0), # Fiery orange
                Vec4(0.8, 0.1, 0.0, 1.0), # Dark red
                Vec4(0.3, 0.3, 0.3, 0.8), # Smoke grey
            ])
            chunk_np = make_cube(size, size, size, c)
            chunk_np.reparent_to(self.render)
            chunk_np.set_pos(pos + Vec3(
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5),
                random.uniform(0.2, 1.0)
            ))
            vel = Vec3(
                random.uniform(-1.0, 1.0),
                random.uniform(-1.0, 1.0),
                random.uniform(0.5, 1.8)
            )
            vel.normalize()
            vel *= random.uniform(8.0, 20.0)
            chunks.append({
                'np': chunk_np,
                'vel': vel,
                'life': random.uniform(0.4, 0.9),
                'max_life': 0.9,
                'growth': random.uniform(0.5, 2.0)
            })
            
        self.explosions.append({
            'chunks': chunks,
            'light_np': plight_np,
            'light_timer': 0.2
        })

    def update(self, dt):
        # Update tracers
        remaining_tracers = []
        for t in self.tracers:
            move_step = t['speed'] * dt
            t['dist_traveled'] += move_step
            t['pos'] += t['dir'] * move_step
            t['np'].set_pos(t['pos'])
            
            if t['dist_traveled'] < t['max_dist']:
                remaining_tracers.append(t)
            else:
                t['np'].remove_node()
        self.tracers = remaining_tracers
        
        # Update sparks
        remaining_sparks = []
        gravity = Vec3(0, 0, -22.0)
        for s in self.sparks:
            s['life'] -= dt
            if s['life'] > 0:
                s['vel'] += gravity * dt
                pos = s['np'].get_pos() + s['vel'] * dt
                if pos.z < 0: # ground bounce
                    pos.z = 0.02
                    s['vel'].z *= -0.4
                    s['vel'].x *= 0.7
                    s['vel'].y *= 0.7
                s['np'].set_pos(pos)
                scale = max(0.01, (s['life'] / s['max_life']))
                s['np'].set_scale(scale)
                remaining_sparks.append(s)
            else:
                s['np'].remove_node()
        self.sparks = remaining_sparks
        
        # Update explosions
        remaining_explosions = []
        for exp in self.explosions:
            if exp['light_np']:
                exp['light_timer'] -= dt
                if exp['light_timer'] <= 0:
                    self.render.clear_light(exp['light_np'])
                    exp['light_np'].remove_node()
                    exp['light_np'] = None
                    
            alive_chunks = []
            for ch in exp['chunks']:
                ch['life'] -= dt
                if ch['life'] > 0:
                    ch['vel'] += gravity * 0.7 * dt
                    pos = ch['np'].get_pos() + ch['vel'] * dt
                    ch['np'].set_pos(pos)
                    # Expand and fade
                    ratio = ch['life'] / ch['max_life']
                    ch['np'].set_scale(1.0 + (1.0 - ratio) * ch['growth'])
                    alive_chunks.append(ch)
                else:
                    ch['np'].remove_node()
            exp['chunks'] = alive_chunks
            
            if len(alive_chunks) > 0 or exp['light_np'] is not None:
                remaining_explosions.append(exp)
        self.explosions = remaining_explosions

    def cleanup(self):
        for t in self.tracers:
            t['np'].remove_node()
        for s in self.sparks:
            s['np'].remove_node()
        for exp in self.explosions:
            if exp['light_np']:
                self.render.clear_light(exp['light_np'])
                exp['light_np'].remove_node()
            for ch in exp['chunks']:
                ch['np'].remove_node()
        self.tracers.clear()
        self.sparks.clear()
        self.explosions.clear()
