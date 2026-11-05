"""
texture_generator.py - Procedural high-resolution PBR texture generator.
Generates sci-fi metal floor tiles, corrugated container plating, high-tech wall panels,
weathered sandstone, explosive drum hazard textures, and weapon materials using PIL or pure Python.
"""

import os
import math
import random
from panda3d.core import PNMImage, Texture, Filename

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_textures(target_dir):
    ensure_dir(target_dir)
    print("Generating modern tactical textures...")
    
    # 1. Sci-Fi Metal Grid Floor (512x512)
    img_floor = PNMImage(512, 512, 4)
    for y in range(512):
        for x in range(512):
            # Base dark titanium
            base = 0.14 + (random.random() * 0.03 - 0.015)
            # Steel grid lines every 64px
            is_grid_x = (x % 64 < 3) or (x % 64 > 61)
            is_grid_y = (y % 64 < 3) or (y % 64 > 61)
            
            # Subtle diamond tread pattern inside each tile
            sub_x = x % 32 - 16
            sub_y = y % 32 - 16
            is_diamond = abs(sub_x) + abs(sub_y) < 6
            
            r, g, b = base, base * 1.05, base * 1.15
            if is_grid_x or is_grid_y:
                r, g, b = 0.05, 0.07, 0.09
            elif is_diamond:
                r += 0.05; g += 0.05; b += 0.06
                
            # Subtle cyan glowing conduit in central grooves
            if (x % 256 < 4 or y % 256 < 4) and not (is_grid_x and is_grid_y):
                r, g, b = 0.05, 0.45, 0.65
                
            img_floor.set_xel_val(x, y, int(r * 255), int(g * 255), int(b * 255))
            img_floor.set_alpha_val(x, y, 255)
    img_floor.write(Filename(os.path.join(target_dir, "floor_metal.png")))

    # 2. Corrugated Shipping Container Plate (512x512)
    img_container = PNMImage(512, 512, 4)
    for y in range(512):
        for x in range(512):
            # Corrugated wave along X
            wave = (math.sin(x * 0.12) + 1.0) * 0.5
            shade = 0.25 + wave * 0.35 + (random.random() * 0.04 - 0.02)
            
            # Top/Bottom structural steel beams
            if y < 24 or y > 488:
                r, g, b = shade * 0.5, shade * 0.52, shade * 0.55
            else:
                # Military industrial dark slate blue / charcoal
                r = shade * 0.25
                g = shade * 0.45
                b = shade * 0.65
                
            img_container.set_xel_val(x, y, int(r * 255), int(g * 255), int(b * 255))
            img_container.set_alpha_val(x, y, 255)
    img_container.write(Filename(os.path.join(target_dir, "container.png")))

    # 3. Sci-Fi Cyber Wall Panels (512x512)
    img_wall = PNMImage(512, 512, 4)
    for y in range(512):
        for x in range(512):
            base = 0.20 + (random.random() * 0.02 - 0.01)
            # Panel bevels
            edge_x = min(x % 128, 128 - (x % 128))
            edge_y = min(y % 128, 128 - (y % 128))
            min_edge = min(edge_x, edge_y)
            
            if min_edge < 4:
                shade = 0.08  # Dark groove
            elif min_edge < 8:
                shade = 0.35  # Bevel highlight
            else:
                shade = base
                
            r, g, b = shade, shade * 1.04, shade * 1.12
            
            # Emissive cyber indicator light on corner panels
            if (x % 128 > 108 and y % 128 > 108):
                r, g, b = 0.1, 0.85, 1.0
                
            img_wall.set_xel_val(x, y, int(r * 255), int(g * 255), int(b * 255))
            img_wall.set_alpha_val(x, y, 255)
    img_wall.write(Filename(os.path.join(target_dir, "cyber_wall.png")))

    # 4. Desert Sandstone Fortress (512x512)
    img_sand = PNMImage(512, 512, 4)
    for y in range(512):
        for x in range(512):
            noise = (random.random() * 0.12 - 0.06)
            # Brick block outlines
            is_brick_y = (y % 64 < 3)
            # Alternate horizontal offset per row
            row = y // 64
            offset_x = 32 if (row % 2 == 1) else 0
            is_brick_x = ((x + offset_x) % 128 < 3)
            
            if is_brick_x or is_brick_y:
                r, g, b = 0.38, 0.30, 0.20
            else:
                base_r = 0.72 + noise
                base_g = 0.58 + noise * 0.8
                base_b = 0.40 + noise * 0.6
                r, g, b = base_r, base_g, base_b
                
            img_sand.set_xel_val(x, y, int(r * 255), int(g * 255), int(b * 255))
            img_sand.set_alpha_val(x, y, 255)
    img_sand.write(Filename(os.path.join(target_dir, "sandstone.png")))

    # 5. Explosive Hazard Barrel Texture (512x256)
    img_barrel = PNMImage(512, 256, 4)
    for y in range(256):
        for x in range(512):
            # Heavy red industrial drum
            r = 0.82 + (random.random() * 0.04 - 0.02)
            g = 0.14
            b = 0.12
            
            # Yellow/Black hazard warning stripe in the middle
            if 100 <= y <= 156:
                diag = (x + y * 2) % 64
                if diag < 32:
                    r, g, b = 0.95, 0.85, 0.05  # Bright yellow
                else:
                    r, g, b = 0.10, 0.10, 0.10  # Dark black
            # Steel reinforcing rings
            elif y in (30, 31, 32, 224, 225, 226):
                r, g, b = 0.3, 0.3, 0.35
                
            img_barrel.set_xel_val(x, y, int(r * 255), int(g * 255), int(b * 255))
            img_barrel.set_alpha_val(x, y, 255)
    img_barrel.write(Filename(os.path.join(target_dir, "barrel_tex.png")))

    # 6. Matte Military Weapon Finish (256x256)
    img_gun = PNMImage(256, 256, 4)
    for y in range(256):
        for x in range(256):
            # Carbon-fiber weave pattern
            cx = (x % 8) < 4
            cy = (y % 8) < 4
            weave = 0.04 if (cx ^ cy) else -0.04
            val = 0.18 + weave + (random.random() * 0.02)
            r, g, b = val, val * 1.02, val * 1.05
            img_gun.set_xel_val(x, y, int(r * 255), int(g * 255), int(b * 255))
            img_gun.set_alpha_val(x, y, 255)
    img_gun.write(Filename(os.path.join(target_dir, "gun_metal.png")))

    print("All modern tactical textures generated successfully!")

if __name__ == "__main__":
    generate_textures("textures")
